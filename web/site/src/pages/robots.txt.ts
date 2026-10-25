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

export const GET: APIRoute = ({ locals }) => {
  const base = siteUrl((locals as any)?.runtime?.env);
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
