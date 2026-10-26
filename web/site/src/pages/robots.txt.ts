// robots.txt
//
// Googlebot and Googlebot-Image are both allowed everything that matters.
// Blocking either is a quiet way to break Shopping: Merchant Center must be
// able to fetch the landing page AND the image, and a disallowed image is
// recorded as unavailable, which disapproves the product.
//
// /cart and /api are disallowed because they are not content. /img is NOT
// disallowed - that would hide every product photograph.
import type { APIRoute } from 'astro';
import { siteUrl } from '../lib/shop';

export const prerender = false;

export const GET: APIRoute = ({ locals, request }) => {
  const base = siteUrl((locals as any)?.runtime?.env);

  // NON-CANONICAL HOSTS GET A BLANKET DISALLOW.
  //
  // The Worker answers on its *.workers.dev address as well as on the shop's
  // own domain, and a deploy can be tested there days before DNS moves. If
  // that address were crawlable, Google could index a second complete copy
  // of the shop on a hostname we do not own the brand of - a new domain
  // whose entire catalogue already exists elsewhere, which is the worst
  // possible way to introduce walryvo.com to Search. Merchant Center
  // verification is tied to the canonical domain too.
  //
  // So: everything but the real domain is closed to crawlers. This is about
  // indexing only - the site works normally on either host.
  const host = new URL(request.url).hostname;
  const canonical = new URL(base).hostname;
  if (host !== canonical && host !== `www.${canonical}`)
    return new Response('User-agent: *\nDisallow: /\n', {
      headers: { 'content-type': 'text/plain; charset=utf-8' },
    });

  return new Response(
    `User-agent: *
Allow: /
Disallow: /api/
Disallow: /cart
Disallow: /checkout

User-agent: Googlebot
Allow: /

User-agent: Googlebot-Image
Allow: /img/

Sitemap: ${base}/sitemap.xml
`,
    { headers: { 'content-type': 'text/plain; charset=utf-8' } }
  );
};
