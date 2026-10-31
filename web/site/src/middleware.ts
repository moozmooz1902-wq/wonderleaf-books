/**
 * THE EDGE CACHE ITSELF.
 *
 * Setting Cache-Control on a Worker's response does NOT cache it. A Worker
 * is the origin, and its response goes straight past Cloudflare's cache to
 * the client. The header alone would buy nothing, which is the trap: the
 * site would look cached, the database would still be read on every view,
 * and the only evidence would be the bill.
 *
 * So the storing is done explicitly through the Cache API, the same way
 * /img/[...path].ts already does it for photographs. Writes go into the
 * zone's cache, so a "Purge Everything" in the dashboard clears these too.
 *
 * What is NOT cached, and why each one would be a bug:
 *  - anything but GET            - a POST is an action, not a document
 *  - any response that is not 200 - never cache a 404 or a 500
 *  - anything setting a cookie   - it would be served to the next visitor
 *  - anything marked no-store    - checkout, cart, order confirmation
 *  - /api/*                      - prices are computed there, per request
 *
 * The cache key is the full URL including the query string, so
 * ?frame=oak&size=a2 is a different entry from ?frame=black&size=a4. Those
 * two must never share a cached copy: they are different prices.
 */
import { defineMiddleware } from 'astro:middleware';
import { record } from './lib/analytics';

declare const __BUILD_ID__: string;

const NEVER = /^\/(api|cart|order-confirmed|admin)(\/|$)/;

export const onRequest = defineMiddleware(async (ctx, next) => {
  const req = ctx.request;
  const url = new URL(req.url);

  // COUNT IT BEFORE THE CACHE, or the numbers are wrong in the one
  // direction nobody would notice. A page served from the edge cache never
  // reaches the route that rendered it, so anything counted further down
  // would miss every repeat visitor and every crawl of a popular page -
  // and would quietly under-report exactly the traffic we are hoping for.
  // This middleware runs on every request, hit or miss, so it is the only
  // honest place to do it.
  record(ctx, req, url);

  // `caches` exists in the Workers runtime but not in Astro's dev server.
  // Feature-detect: the cache is an optimisation and must never be the
  // reason a page fails to render.
  const store = typeof caches !== 'undefined' ? (caches as any).default : null;
  const usable = store && req.method === 'GET' && !NEVER.test(url.pathname);
  if (!usable) return next();

  // The build id namespaces the cache. See astro.config.mjs: without it a
  // page cached before a deploy keeps naming the previous build's hashed
  // stylesheet, which the deploy has already deleted, and the shop renders
  // with no styling at all.
  const keyUrl = new URL(url.toString());
  keyUrl.searchParams.set('__b', __BUILD_ID__);
  const key = new Request(keyUrl.toString(), { method: 'GET' });
  const hit = await store.match(key);
  if (hit) {
    const res = new Response(hit.body, hit);
    res.headers.set('x-cache', 'HIT');
    return res;
  }

  const res = await next();
  const cc = res.headers.get('cache-control') || '';
  // A PAGE THAT THREW HALFWAY THROUGH IS STILL A 200.
  //
  // Astro streams the response, so an error raised while rendering the body
  // ends the stream after whatever had already been written - header, then
  // nothing - and the status line went out as 200 long before. Caching that
  // serves the broken page to everyone for the rest of the TTL. It happened
  // on the live shop: a deploy shipped a bundle whose config was one build
  // behind, the product page threw on a missing value, and the truncated
  // render was cached and served until it expired.
  //
  // So a response is only storable if it finished. Checking for the closing
  // tag costs one read of a body that was about to be cloned anyway.
  const html = (res.headers.get('content-type') || '').includes('text/html');
  let body: string | null = null;
  let complete = true;
  if (html) {
    body = await res.clone().text();
    complete = body.trimEnd().endsWith('</html>');
  }

  const storable =
    res.status === 200 &&
    complete &&
    !res.headers.has('set-cookie') &&
    cc.includes('s-maxage') &&
    !cc.includes('no-store');

  if (html && body !== null) {
    res.headers.set('x-cache', storable ? 'MISS'
                                        : complete ? 'BYPASS' : 'INCOMPLETE');
    // The body has been read, so re-serve it rather than the consumed
    // stream, and give the cache its own copy.
    const out = new Response(body, { status: res.status, headers: res.headers });
    if (storable) ctx.locals.runtime?.ctx?.waitUntil?.(store.put(key, out.clone()));
    return out;
  }
  if (storable) {
    res.headers.set('x-cache', 'MISS');
    ctx.locals.runtime?.ctx?.waitUntil?.(store.put(key, res.clone()));
  }
  return res;
});
