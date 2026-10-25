// Create a Stripe Checkout Session.
//
// STRIPE CHECKOUT RATHER THAN A CARD FORM ON OUR PAGE. The card details
// never touch this Worker, which keeps the shop in PCI scope SAQ-A - the
// lightest there is - and gets Apple Pay, Google Pay and Link without any
// extra work. It also gives Google a checkout that demonstrably completes,
// which matters if Merchant Center runs a test order.
//
// THE PRICES ARE LOOKED UP HERE, NEVER ACCEPTED FROM THE BROWSER. The
// request carries variant ids and quantities and nothing else. Trusting a
// posted price would let anyone buy an A2 for a penny, and - the reason it
// belongs in this file's comments rather than only a security note - it
// would mean the amount charged could differ from the amount published in
// the feed and on the page. "Not showing the total price" and bait-and-
// switch pricing are both named under dishonest pricing in the
// misrepresentation policy. One source of truth for a price, all the way
// to the card.
import type { APIRoute } from 'astro';
import Stripe from 'stripe';
import { getDb, variantById } from '../../lib/db';
import { B, siteUrl } from '../../lib/shop';

export const prerender = false;

interface Line {
  id: string;
  qty: number;
}

export const POST: APIRoute = async ({ request, locals }) => {
  const env = (locals as any)?.runtime?.env;
  const key = env?.STRIPE_SECRET_KEY;
  if (!key)
    return json({ error: 'Payments are not configured yet.' }, 503);

  let body: { items?: Line[] };
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Bad request' }, 400);
  }
  const items = (body.items || []).filter(
    (l) => typeof l.id === 'string' && Number.isInteger(l.qty) && l.qty > 0
  );
  if (!items.length) return json({ error: 'Your basket is empty' }, 400);
  if (items.length > 40) return json({ error: 'Too many items' }, 400);

  const db = getDb(locals);
  const line_items = [];
  const record: any[] = [];
  for (const l of items) {
    const v = await variantById(db, l.id);
    if (!v) return json({ error: `We no longer sell ${l.id}` }, 409);
    const qty = Math.min(l.qty, 10);
    line_items.push({
      quantity: qty,
      price_data: {
        currency: B.currency.toLowerCase(),
        // Pence. The catalogue stores pounds, so round rather than
        // truncate: Math.trunc(29.99 * 100) is 2998 in floating point.
        unit_amount: Math.round(v.price * 100),
        tax_behavior: 'inclusive' as const,
        product_data: {
          name: v.title,
          description: `${v.size_label} (${v.size_cm}), ${v.frame_label} frame`,
          metadata: { variant_id: v.id, slug: v.slug },
        },
      },
    });
    record.push({ id: v.id, title: v.title, qty, price: v.price });
  }

  const base = siteUrl(env);
  const d = B.fulfilment.delivery[0];
  const stripe = new Stripe(key, { apiVersion: '2025-02-24.acacia' as any });

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items,
      // UK only, stated here and on every page that mentions delivery.
      // Offering a country we do not actually ship to is "promising
      // products or promotions that users can't actually get".
      shipping_address_collection: { allowed_countries: B.fulfilment.ships_to as any },
      shipping_options: [
        {
          shipping_rate_data: {
            type: 'fixed_amount',
            display_name: d.name,
            fixed_amount: {
              amount: Math.round(d.price * 100),
              currency: B.currency.toLowerCase(),
            },
            tax_behavior: 'inclusive',
            delivery_estimate: {
              minimum: { unit: 'business_day', value: d.min_days },
              maximum: {
                unit: 'business_day',
                value: d.max_days + B.fulfilment.dispatch_working_days,
              },
            },
          },
        },
      ],
      phone_number_collection: { enabled: false },
      success_url: `${base}/order-confirmed?session={CHECKOUT_SESSION_ID}`,
      cancel_url: `${base}/cart`,
      metadata: { items: JSON.stringify(record).slice(0, 480) },
      // Prices already include UK VAT, and tax_behavior above tells Stripe
      // so, which is what makes the receipt show the right VAT split.
      // Turn Stripe Tax on here only if you start selling outside the UK -
      // at that point the VAT treatment genuinely changes and the delivery
      // and returns copy has to change with it.
      automatic_tax: { enabled: false },
    });
    return json({ url: session.url });
  } catch (e: any) {
    return json({ error: e?.message || 'Payment provider error' }, 502);
  }
};

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  });
