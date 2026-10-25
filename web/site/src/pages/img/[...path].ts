// Product images, served from the shop's own domain out of R2.
//
// WHY NOT THE r2.dev URLS THE EBAY FILES USE. They are rate limited. A
// measured run against them got Cloudflare error 1015 on 7,142 of 12,834
// requests at roughly 70 req/s. Google fetches product images in bursts and
// re-fetches them regularly; an image that answers the crawler with 1015 is
// an image Google logs as unavailable, and "image not reachable" disapproves
// the product. One bad afternoon of crawling could disapprove the catalogue.
//
// Reading through a Worker binding has no such ceiling, costs the same, puts
// the images on our own domain for image search, and lets us set a long
// immutable cache. The path is /img/<bucket>/<key>, and <bucket> is matched
// against an allow-list so this cannot be turned into an open proxy for
// anything else in the account.
import type { APIRoute } from 'astro';

const BUCKETS: Record<string, string> = {
  'luxvia-art': 'IMG_LUXVIA',
  'posterleaf-store1': 'IMG_POSTERLEAF',
  'lunar-kms': 'IMG_LUNAR',
  'mercury-usm': 'IMG_MERCURY',
};

// Used only by the dev fallback below, never in production.
const DEV_HOSTS: Record<string, string> = {
  'luxvia-art': 'https://pub-6004b56e7a254092b7bfec9a24cf9484.r2.dev',
  'posterleaf-store1': 'https://pub-0ad8669f94ce487499368f153cdb0c1b.r2.dev',
  'lunar-kms': 'https://pub-1f879b9875164bf59a4806f4026100d0.r2.dev',
  'mercury-usm': 'https://pub-0393733d8d814d7395f37e1eaf666e62.r2.dev',
};

export const prerender = false;

export const GET: APIRoute = async ({ params, locals, request }) => {
  const path = params.path || '';
  const slash = path.indexOf('/');
  if (slash < 1) return new Response('Bad path', { status: 400 });

  const bucket = path.slice(0, slash);
  const key = path.slice(slash + 1);
  const binding = BUCKETS[bucket];
  if (!binding) return new Response('Unknown bucket', { status: 404 });
  // No traversal, no empty keys, images only.
  if (!key || key.includes('..') || !/\.(jpe?g|png|webp)$/i.test(key))
    return new Response('Bad key', { status: 400 });

  const env = (locals as any)?.runtime?.env;
  const r2 = env?.[binding];

  if (!r2 && !import.meta.env.DEV)
    return new Response('No bucket binding', { status: 500 });

  // `caches` exists in the Workers runtime but not in Astro's dev server,
  // where touching it threw "caches is not defined" and turned every image
  // into a 500. Feature-detect rather than assume: the cache is an
  // optimisation, and an optimisation must never be the reason a product
  // photograph fails to load.
  const cache =
    typeof caches !== 'undefined' ? (caches as any).default : undefined;
  const cacheKey = new Request(new URL(request.url).toString(), request);
  if (cache) {
    const hit = await cache.match(cacheKey);
    if (hit) return hit;
  }

  const obj = r2 ? await r2.get(key) : null;

  // DEV-ONLY FALLBACK. Local Astro/miniflare hands you a working R2 binding
  // that is EMPTY, so `r2.get` returns null for every key and the shop has
  // no photographs at all while you are building it. `import.meta.env.DEV`
  // is replaced at build time, so this branch is compiled out of the
  // deployed Worker entirely - production cannot reach the rate-limited
  // r2.dev hosts this route exists to avoid, even by accident.
  if (!obj && import.meta.env.DEV) {
    const host = DEV_HOSTS[bucket];
    if (host) {
      const upstream = await fetch(`${host}/${key}`);
      if (upstream.ok)
        return new Response(upstream.body, {
          headers: {
            'content-type':
              upstream.headers.get('content-type') || 'image/jpeg',
            'cache-control': 'public, max-age=3600',
            'x-img-source': 'dev-fallback',
          },
        });
    }
  }
  if (!obj) return new Response('Not found', { status: 404 });

  const headers = new Headers();
  obj.writeHttpMetadata?.(headers);
  headers.set('etag', obj.httpEtag);
  // The key contains the SKU, the colourway and the frame colour, so a
  // given URL's bytes never change. Immutable is accurate here.
  headers.set('cache-control', 'public, max-age=31536000, immutable');
  if (!headers.has('content-type')) headers.set('content-type', 'image/jpeg');

  const res = new Response(obj.body, { headers });
  if (cache) await cache.put(cacheKey, res.clone());
  return res;
};
