// Stripe webhook. Records the order so the shop can honour what it sold.
//
// This exists for a compliance reason as much as an operational one. The
// returns page promises a refund within a window from delivery; "denying
// return and refund for a product despite having a clear refund or return
// policy" is listed among the egregious misrepresentation violations, with
// suspension and no prior warning. A shop that cannot look up what it sold,
// to whom, and when, cannot keep that promise. So the order is written down.
//
// The signature is verified before anything is trusted. An unverified
// webhook body is just a POST from the internet.
import type { APIRoute } from 'astro';
import Stripe from 'stripe';
import { getDb } from '../../lib/db';
import { vapid, pushAll } from '../../lib/push';
import { B } from '../../lib/shop';

export const prerender = false;

export const POST: APIRoute = async ({ request, locals }) => {
  const env = (locals as any)?.runtime?.env;
  const key = env?.STRIPE_SECRET_KEY;
  const secret = env?.STRIPE_WEBHOOK_SECRET;
  if (!key || !secret) return new Response('Not configured', { status: 503 });

  const sig = request.headers.get('stripe-signature');
  if (!sig) return new Response('No signature', { status: 400 });
  const raw = await request.text();

  const stripe = new Stripe(key, { apiVersion: '2025-02-24.acacia' as any });
  let event: Stripe.Event;
  try {
    // constructEventAsync, not constructEvent: Workers have no synchronous
    // crypto, and the sync version throws at runtime here.
    event = await stripe.webhooks.constructEventAsync(raw, sig, secret);
  } catch (e: any) {
    return new Response(`Bad signature: ${e?.message}`, { status: 400 });
  }

  if (event.type === 'checkout.session.completed') {
    const s = event.data.object as Stripe.Checkout.Session;
    const db = getDb(locals);
    try {
      await db
        .prepare(
          'INSERT OR REPLACE INTO orders (id,created,email,total,currency,' +
            'status,items,shipping) VALUES (?,?,?,?,?,?,?,?)'
        )
        .bind(
          s.id,
          new Date().toISOString(),
          s.customer_details?.email ?? null,
          (s.amount_total ?? 0) / 100,
          (s.currency ?? 'gbp').toUpperCase(),
          s.payment_status ?? 'unknown',
          s.metadata?.items ?? '[]',
          JSON.stringify(
            (s as any).shipping_details ?? s.customer_details?.address ?? null
          )
        )
        .run();
    } catch (e) {
      // Returning 500 makes Stripe retry, which is what we want: a paid
      // order that was not written down is the one failure here that
      // actually costs a customer their print.
      return new Response('Could not record order', { status: 500 });
    }

    // THEN TELL THE PHONE. After the row is written, never before: a
    // notification about an order that failed to save would send somebody
    // to a dashboard that does not show it.
    //
    // Deliberately outside the try above. A push that fails must NOT make
    // this handler return 500, because Stripe would then retry the whole
    // webhook and the shop would record the order again to fix a
    // notification - exactly the wrong trade.
    try {
      const v = vapid(env, B.email);
      if (v) {
        const p = pushAll(db, v);
        const wait = (locals as any)?.runtime?.ctx?.waitUntil;
        wait ? wait.call((locals as any).runtime.ctx, p) : await p;
      }
    } catch { /* an order is worth more than a notification */ }
  }

  return new Response('ok', { status: 200 });
};
