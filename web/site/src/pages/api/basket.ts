/**
 * Price a basket, authoritatively.
 *
 * The basket page used to add up its own localStorage and print a total.
 * With a promotion that becomes two implementations of one price, and the
 * one the shopper reads is the one that is not binding. So the page sends
 * its item ids here and renders whatever comes back: the prices are read
 * from D1 and the discount from lib/promo.ts, which is the same function
 * /api/checkout uses to build the Stripe session. One price, worked out
 * once, in the only place that cannot be edited from a browser console.
 */
import type { APIRoute } from 'astro';
import { getDb, variantById } from '../../lib/db';
import { priceBasket, PROMO } from '../../lib/promo';
import { B } from '../../lib/shop';

export const prerender = false;

interface Line { id: string; qty: number }

export const POST: APIRoute = async ({ request, locals }) => {
  let body: { items?: Line[] };
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Bad request' }, 400);
  }
  const items = (body.items || []).filter(
    (l) => typeof l.id === 'string' && Number.isInteger(l.qty) && l.qty > 0
  );
  if (items.length > 40) return json({ error: 'Too many items' }, 400);

  const db = getDb(locals);
  const lines = [];
  const gone: string[] = [];
  for (const l of items) {
    const v = await variantById(db, l.id);
    if (!v) { gone.push(l.id); continue; }
    lines.push({
      id: v.id,
      title: v.title,
      qty: Math.min(l.qty, 10),
      price: v.price,
      slug: v.slug,
      size_label: v.size_label,
      size_cm: v.size_cm,
      frame: v.frame,
      frame_label: v.frame_label,
      image_path: v.image_path,
    });
  }

  const priced = priceBasket(lines);
  const merged = priced.lines.map((p) => ({
    ...p,
    ...(lines.find((l) => l.id === p.id) as any),
    free: p.free,
  }));

  const d = B.fulfilment.delivery[0];
  return json({
    ...priced,
    lines: merged,
    gone,
    delivery: d.price,
    grand: Math.round((priced.total + d.price) * 100) / 100,
    promo: PROMO.active
      ? { title: PROMO.title, blurb: PROMO.blurb, group: PROMO.groupSize }
      : null,
  });
};

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
  });
