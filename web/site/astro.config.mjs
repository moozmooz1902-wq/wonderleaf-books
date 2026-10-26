// @ts-check
import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

// SERVER RENDERED, ON PURPOSE.
//
// A static build would be faster and cheaper, and it is the wrong choice
// here for one specific reason: every row in the Merchant Center feed links
// to a URL carrying ?frame= and ?size=, and the page has to answer with THAT
// variant's price and title - in the HTML, before any JavaScript runs,
// because Google's crawler is what reads it.
//
// A static page cannot vary by query string server-side. It would serve the
// default variant's price to all nine variant URLs, so eight of every nine
// feed rows would disagree with their own landing page. That is the "price
// mismatch" disapproval, and at scale it reads as misrepresentation - which
// is the exact failure this shop is being rebuilt to avoid.
//
// Category and policy pages are prerendered individually (see `prerender`
// in each page), so only the pages that genuinely need a request are
// rendered on one.
// EVERY BUILD GETS ITS OWN CACHE NAMESPACE.
//
// The edge cache in src/middleware.ts stores rendered HTML, and that HTML
// names a hashed stylesheet - /_astro/about.<hash>.css. A deploy changes the
// hash and deletes the old file. So a cached page served after a deploy asks
// for a stylesheet that no longer exists, and the shop renders as unstyled
// HTML: black Times on white, every link blue and underlined. That happened
// on the first theme change, on the live domain.
//
// Purging after each deploy is the usual answer and it is not good enough -
// it is a manual step, and the API token here cannot purge anyway. Instead
// the cache key carries this value, so a new build simply cannot read the
// previous build's entries. Date.now() is evaluated when the config is
// loaded, which is once per build.
const BUILD_ID = Date.now().toString(36);

export default defineConfig({
  vite: { define: { __BUILD_ID__: JSON.stringify(BUILD_ID) } },
  output: 'server',
  adapter: cloudflare({
    platformProxy: { enabled: true },
    imageService: 'passthrough',
  }),
  site: process.env.SITE_URL || 'http://localhost:4321',
  trailingSlash: 'never',
  build: { format: 'file' },
  compressHTML: true,
});
