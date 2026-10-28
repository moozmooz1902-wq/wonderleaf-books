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
import { priceBasket, PROMO } from '../../lib/promo';
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

  // Prices come from D1, never from the request. The browser sends ids and
  // quantities and nothing else; anything it claims about money is ignored.
  const found = [];
  for (const l of items) {
    const v = await variantById(db, l.id);
    if (!v) return json({ error: `We no longer sell ${l.id}` }, 409);
    found.push({ v, qty: Math.min(l.qty, 10) });
  }

  // The SAME function the basket page was priced with. If this ever stopped
  // being the same function, the shop would advertise one total and charge
  // another, which is the failure Google names outright.
  const priced = priceBasket(
    found.map(({ v, qty }) => ({ id: v.id, title: v.title, qty, price: v.price }))
  );

  const line_items = [];
  const record: any[] = [];
  for (const { v, qty } of found) {
    const free = priced.lines.find((p) => p.id === v.id)?.free ?? 0;
    const paid = qty - free;
    const desc = v.frame === 'none'
      ? `${v.size_label} (${v.size_cm}), unframed print`
      : `${v.size_label} (${v.size_cm}), ${v.frame_label} frame`;
    const money = (n: number) => ({
      currency: B.currency.toLowerCase(),
      // Pence. The catalogue stores pounds, so round rather than truncate:
      // Math.trunc(29.99 * 100) is 2998 in floating point.
      unit_amount: Math.round(n * 100),
      tax_behavior: 'inclusive' as const,
    });
    if (paid > 0)
      line_items.push({
        quantity: paid,
        price_data: {
          ...money(v.price),
          product_data: {
            name: v.title,
            description: desc,
            metadata: { variant_id: v.id, slug: v.slug },
          },
        },
      });
    // The free ones are their own zero-priced line rather than a coupon, so
    // the Stripe page and the receipt both say which print was free and why.
    if (free > 0)
      line_items.push({
        quantity: free,
        price_data: {
          ...money(0),
          product_data: {
            name: `${v.title} — free`,
            description: `${desc} · ${PROMO.title}`,
            metadata: { variant_id: v.id, slug: v.slug, promo: PROMO.code },
          },
        },
      });
    record.push({ id: v.id, title: v.title, qty, price: v.price, free });
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
            // HANDLING + TRANSIT AT BOTH ENDS. The maximum always added
            // dispatch to transit; the minimum did not, so Stripe told
            // buyers "2-7 business days" when nothing can arrive before
            // 1 day to print plus 2 in the post. The feed had it right all
            // along - it declares handling and transit separately and lets
            // Google add them - so checkout was the odd one out, and it is
            // the number shown at the moment someone pays.
            delivery_estimate: {
              minimum: {
                unit: 'business_day',
                value: B.fulfilment.min_handling_days + d.min_days,
              },
              maximum: {
                unit: 'business_day',
                value: B.fulfilment.dispatch_working_days + d.max_days,
              },
            },
          },
        },
      ],
      phone_number_collection: { enabled: false },

      // THE POLICIES MUST BE REACHABLE DURING CHECKOUT, NOT JUST BEFORE IT.
      //
      // Google's checkout requirements are explicit: "Customers must be
      // able to find refund and return policies, terms and conditions, and
      // a way to contact you throughout checkout", and omitting them is
      // "treated as misrepresentation, which can lead to ad or free listing
      // disapproval or account suspension".
      //
      // Our checkout is Stripe's hosted page, so our own footer is not on
      // it. These two settings put the terms acceptance and the policy
      // links on Stripe's page itself. Without them the shop would satisfy
      // the rule everywhere except the one page where Google states it.
      consent_collection: { terms_of_service: 'required' },
      custom_text: {
        terms_of_service_acceptance: {
          message:
            `I agree to the [terms and conditions](${base}/terms), the ` +
            `[returns policy](${base}/returns) ` +
            `(${B.returns.window_days} days from delivery, any reason) and ` +
            `the [privacy policy](${base}/privacy).`,
        },
        submit: {
          message:
            `Printed and framed in ${B.fulfilment.made_in} and dispatched ` +
            `within ${B.fulfilment.dispatch_working_days} working days. ` +
            `Questions: ${B.email}`,
        },
      },

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

// no-store, belt and braces. The middleware already refuses to cache
// anything under /api, but this response carries a Stripe Checkout URL
// bound to one basket and one customer: serving a stored copy to the next
// visitor would put them into somebody else's payment session.
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json',
      'cache-control': 'no-store',
    },
  });
