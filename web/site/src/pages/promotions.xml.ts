/**
 * The promotions feed, served live so the offer renews itself.
 *
 * Google will not show an open-ended promotion: promotion_effective_dates is
 * required and it wants a real window. A file with a fixed window is a
 * promotion that silently stops one morning, and nobody notices until a
 * quarter's badges have gone.
 *
 * So this is a route rather than a file. Merchant Center fetches it on a
 * schedule, and every fetch returns a window that starts now and ends
 * WINDOW_DAYS out. The offer therefore runs continuously for as long as the
 * shop says it does, and stops the day someone sets PROMO.active to false -
 * which is the only honest way to run a permanent offer: it is permanent
 * because it is genuinely always on, not because the end date is a fiction.
 *
 * Nothing here creates urgency. A countdown on an offer that renews every
 * time it is read would be a lie told by a clock, and "falsely stating that
 * a product will only be available for a very limited time" is a banned
 * practice in its own right, not a grey area.
 */
import type { APIRoute } from 'astro';
import { PROMO } from '../lib/promo';
import { B, siteUrl } from '../lib/shop';
import { edge, TTL_FEED } from '../lib/cache';

export const prerender = false;

const WINDOW_DAYS = 90;

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export const GET: APIRoute = ({ locals }) => {
  const base = siteUrl((locals as any)?.runtime?.env);
  const start = new Date();
  start.setMilliseconds(0);
  const end = new Date(start.getTime() + WINDOW_DAYS * 864e5);
  const iso = (d: Date) => d.toISOString().replace(/\.\d{3}Z$/, '+00:00');

  const items = PROMO.active
    ? `  <item>
    <g:promotion_id>${esc(PROMO.id)}</g:promotion_id>
    <g:product_applicability>all_products</g:product_applicability>
    <g:offer_type>no_code</g:offer_type>
    <g:long_title>${esc(PROMO.title)} on all prints</g:long_title>
    <g:promotion_effective_dates>${iso(start)}/${iso(end)}</g:promotion_effective_dates>
    <g:redemption_channel>online</g:redemption_channel>
  </item>
`
    : '';

  const xml = `<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
<channel>
  <title>${esc(B.brand)} promotions</title>
  <link>${base}/</link>
  <description>Promotions for ${esc(B.brand)}</description>
${items}</channel>
</rss>
`;
  const res = new Response(xml, {
    headers: { 'content-type': 'application/xml; charset=utf-8' },
  });
  edge(res, TTL_FEED);
  return res;
};
