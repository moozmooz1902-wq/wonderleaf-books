// The sitemap. Every indexable URL, and only indexable URLs.
//
// Variant URLs (?frame=&size=) are deliberately absent. They are what the
// Merchant Center feed links to, not what Search should index - nine URLs
// per design in a sitemap would be asking Google to index nine copies of
// the same page, which is the thin-content signal we are trying not to
// send. The clean product URL is the canonical one and the only one listed.
import type { APIRoute } from 'astro';
import { getDb, allSlugs, nicheCounts } from '../lib/db';
import { TAX, siteUrl } from '../lib/shop';

export const prerender = false;

const STATIC = [
  ['/', '1.0'],
  ['/style', '0.6'],
  ['/rooms', '0.6'],
  ['/about', '0.4'],
  ['/how-its-made', '0.4'],
  ['/delivery', '0.4'],
  ['/returns', '0.4'],
  ['/contact', '0.4'],
  ['/faq', '0.4'],
  ['/terms', '0.2'],
  ['/privacy', '0.2'],
];

export const GET: APIRoute = async ({ locals }) => {
  const db = getDb(locals);
  const base = siteUrl((locals as any)?.runtime?.env);
  const { results: slugs } = await allSlugs(db);
  const { results: counts } = await nicheCounts(db);

  const urls: [string, string][] = [
    ...(STATIC as [string, string][]),
    ...TAX.sections.map((s) => [`/c/${s.slug}`, '0.8'] as [string, string]),
    ...counts.map(
      (c) => [`/c/${c.section}/${c.niche}`, '0.8'] as [string, string]
    ),
    ...TAX.styles.map((s) => [`/style/${s.slug}`, '0.6'] as [string, string]),
    ...TAX.colours.map((c) => [`/colour/${c.slug}`, '0.5'] as [string, string]),
    ...TAX.rooms.map((r) => [`/rooms/${r.slug}`, '0.5'] as [string, string]),
    ...slugs.map((s) => [`/art/${s.slug}`, '0.7'] as [string, string]),
  ];

  const body =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    urls
      .map(
        ([loc, pri]) =>
          `<url><loc>${base}${loc}</loc><priority>${pri}</priority></url>`
      )
      .join('\n') +
    '\n</urlset>\n';

  return new Response(body, {
    headers: {
      'content-type': 'application/xml; charset=utf-8',
      'cache-control': 'public, max-age=3600',
    },
  });
};
