/**
 * EDGE CACHING POLICY.
 *
 * Every HTML page on this site is rendered on demand from D1. Without a
 * cache that is one database round trip per page view, and at a large
 * catalogue it is the dominant cost and the dominant latency. With one, a
 * page that has been asked for recently is served from the Cloudflare
 * location nearest the visitor and never reaches the database at all.
 *
 * THE RISK, AND WHY THE NUMBERS LOOK THE WAY THEY DO.
 *
 * A cached page showing yesterday's price while the Merchant Center feed
 * carries today's is a price mismatch, and repeated price mismatches is
 * precisely how a feed earns a misrepresentation finding rather than a
 * simple disapproval. That is the failure this whole project exists to
 * avoid, so the cache is deliberately not generous:
 *
 *  - `max-age=0` so a VISITOR'S OWN BROWSER never holds a stale price. We
 *    can purge Cloudflare. We cannot purge somebody's laptop.
 *  - `s-maxage=300` so the shared edge cache holds it for five minutes. A
 *    deliberate price change is live everywhere inside five minutes with
 *    no action, and immediately if the cache is purged.
 *  - `stale-while-revalidate` so a cache miss after expiry serves the old
 *    copy and refreshes behind it, instead of making one unlucky visitor
 *    wait for the database.
 *
 * AFTER ANY PRICE CHANGE OR RESEED, PURGE: Cloudflare dashboard ->
 * walryvo.com -> Caching -> Configuration -> Purge Everything. Takes a few
 * seconds and removes the five-minute window entirely.
 *
 * Policy pages hold longer because nothing in them is priced; checkout,
 * cart and order pages are never cached at all.
 */
export const TTL_CATALOGUE = 300; // 5 minutes
export const TTL_STATIC = 3600; // 1 hour - policy and information pages
export const TTL_FEED = 900; // 15 minutes - feed.xml, sitemap

type HasHeaders = { headers: Headers };

/** Cache at the edge, never in the visitor's browser. */
export function edge(res: HasHeaders, seconds: number = TTL_CATALOGUE) {
  res.headers.set(
    'cache-control',
    `public, max-age=0, s-maxage=${seconds}, stale-while-revalidate=86400`
  );
}

/** Nothing about this response may be stored anywhere. */
export function noStore(res: HasHeaders) {
  res.headers.set('cache-control', 'no-store');
}
