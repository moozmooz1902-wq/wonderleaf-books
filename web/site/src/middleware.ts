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

declare const __BUILD_ID__: string;

const NEVER = /^\/(api|cart|order-confirmed)(\/|$)/;

export const onRequest = defineMiddleware(async (ctx, next) => {
  const req = ctx.request;
  const url = new URL(req.url);

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
  const storable =
    res.status === 200 &&
    !res.headers.has('set-cookie') &&
    cc.includes('s-maxage') &&
    !cc.includes('no-store');

  if (storable) {
    res.headers.set('x-cache', 'MISS');
    ctx.locals.runtime?.ctx?.waitUntil?.(store.put(key, res.clone()));
  }
  return res;
});
