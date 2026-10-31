/**
 * FIRST-PARTY ANALYTICS, BECAUSE THERE WAS NO WAY TO SEE ANYTHING.
 *
 * Asked on 31 Oct: "has Google sent us anything yet?" There was no way to
 * answer. Cloudflare's own analytics need a zone-analytics permission this
 * environment's API token does not carry, Merchant Center has no read API
 * for engagement, and the site itself recorded nothing at all. So the shop
 * could have been getting traffic for a week and nobody would know.
 *
 * This file is the fix, and it is deliberately NOT Google Analytics:
 *
 *  - No third-party script, so the privacy policy's "this page loads from
 *    one server, ours" stays true.
 *  - No cookie and no device storage, so PECR's consent rules do not bite
 *    and nobody needs a banner.
 *  - No IP address is stored. A visitor is a SHA-256 of their IP, their
 *    user agent and a salt that changes at midnight UTC, truncated to 16
 *    hex characters. That is enough to tell two people apart today and
 *    useless for telling who anybody is, or for joining yesterday to today.
 *
 * WHAT IS COUNTED AND WHY IT IS SPLIT IN TWO.
 *
 * Humans get one row each per page view, in `hits`. At this traffic that is
 * a handful of writes a day and the detail is worth it - live visitors, the
 * exact page, where they came from.
 *
 * Crawlers get a daily COUNTER in `crawls`, never a row each. Googlebot
 * fetching 2,508 products and their photographs is tens of thousands of
 * requests, and a row apiece would spend the whole D1 write allowance on
 * recording a robot. Counters are also batched in the isolate and flushed
 * every few seconds, so a crawl of a thousand images is a handful of
 * writes rather than a thousand. An isolate that dies with a part-full
 * buffer loses those few counts, which is why the dashboard calls the
 * crawl numbers a lower bound rather than a total.
 *
 * THE COLUMN THAT ANSWERS THE ORIGINAL QUESTION is `src`. A click from a
 * Google free listing arrives carrying `srsltid` in the query string -
 * that parameter is Google Shopping's own click marker and nothing else
 * sets it. So "did the Merchant Center feed actually do anything" is one
 * SELECT, and it does not depend on anyone's dashboard but ours.
 */

const BOTS: [RegExp, string][] = [
  [/googlebot-image/i, 'Googlebot-Image'],
  [/googlebot/i, 'Googlebot'],
  [/google-inspectiontool/i, 'Google-InspectionTool'],
  [/storebot-google/i, 'Storebot-Google'],
  [/google-shopping|googleproducer|google-read-aloud/i, 'Google-Shopping'],
  [/adsbot-google/i, 'AdsBot-Google'],
  [/apis-google|feedfetcher/i, 'Google-Other'],
  [/bingbot|adidxbot/i, 'Bingbot'],
  [/duckduckbot/i, 'DuckDuckBot'],
  [/yandexbot/i, 'YandexBot'],
  [/baiduspider/i, 'Baiduspider'],
  [/applebot/i, 'Applebot'],
  [/petalbot/i, 'PetalBot'],
  [/facebookexternalhit|meta-externalagent/i, 'Facebook'],
  [/twitterbot/i, 'Twitterbot'],
  [/ahrefsbot/i, 'AhrefsBot'],
  [/semrushbot/i, 'SemrushBot'],
  [/mj12bot|dotbot|blexbot/i, 'SEO crawler'],
  [/gptbot|claudebot|ccbot|perplexitybot|bytespider/i, 'AI crawler'],
  [/headlesschrome|puppeteer|playwright/i, 'Headless browser'],
  [/\bbot\b|crawler|spider|crawl|slurp|scrapy|curl\/|wget|python-requests|http-client|monitor|uptime/i,
   'Other bot'],
];

export function botName(ua: string): string | null {
  for (const [re, name] of BOTS) if (re.test(ua)) return name;
  return null;
}

/** page | image | feed | api | asset — what was asked for, not who asked. */
export function kindOf(path: string): string {
  if (path.startsWith('/img/') || path.startsWith('/unframed/')) return 'image';
  if (path === '/feed.xml' || path === '/promotions.xml') return 'feed';
  if (path === '/sitemap.xml' || path === '/robots.txt') return 'feed';
  if (path.startsWith('/api/')) return 'api';
  if (path.startsWith('/_astro/') || path.startsWith('/favicon')) return 'asset';
  return 'page';
}

/**
 * Where a visitor came from, in one word.
 *
 * `srsltid` is the one that matters: Google appends it to clicks from free
 * product listings and Shopping, so its presence is direct proof the feed
 * is earning traffic. gclid/gad_source mean a paid click. Everything else
 * falls back to the referrer's host, and no referrer at all is "direct" -
 * which on a brand-new shop usually means someone typed it or followed a
 * link from a message, not that they are a regular.
 */
export function sourceOf(url: URL, referer: string): string {
  const q = url.searchParams;
  if (q.has('srsltid')) return 'google-shopping';
  if (q.has('gclid') || q.has('gad_source') || q.has('gbraid')) return 'google-ads';
  const utm = q.get('utm_source');
  if (utm) return utm.slice(0, 40).toLowerCase();
  if (!referer) return 'direct';
  let host = '';
  try {
    host = new URL(referer).hostname.replace(/^www\./, '');
  } catch {
    return 'direct';
  }
  if (/(^|\.)google\./.test(host)) return 'google-search';
  if (/(^|\.)bing\.com$/.test(host)) return 'bing';
  if (/(^|\.)duckduckgo\.com$/.test(host)) return 'duckduckgo';
  if (/(^|\.)ebay\./.test(host)) return 'ebay';
  if (/(^|\.)onbuy\.com$/.test(host)) return 'onbuy';
  return host.slice(0, 60) || 'direct';
}

async function visitorId(ip: string, ua: string, day: string) {
  const data = new TextEncoder().encode(`${day}|${ip}|${ua}`);
  const buf = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(buf)]
    .slice(0, 8)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

// ---------------------------------------------------------------------------
// Crawler counters, batched inside the isolate.
// ---------------------------------------------------------------------------
const pending = new Map<string, number>();
let pendingTotal = 0;
let lastFlush = 0;

async function flush(db: D1Database) {
  if (!pending.size) return;
  const rows = [...pending.entries()];
  pending.clear();
  pendingTotal = 0;
  lastFlush = Date.now();
  const stmt = db.prepare(
    'INSERT INTO crawls (day,bot,kind,n) VALUES (?,?,?,?) ' +
      'ON CONFLICT(day,bot,kind) DO UPDATE SET n = n + excluded.n'
  );
  await db.batch(
    rows.map(([k, n]) => {
      const [day, bot, kind] = k.split('\u0000');
      return stmt.bind(day, bot, kind, n);
    })
  );
}

/**
 * Record one request. Never throws, never blocks the response.
 *
 * Everything here runs inside waitUntil, so a database that is slow or
 * missing costs the visitor nothing. An analytics table is not worth one
 * millisecond of a product page, and it is certainly not worth a 500.
 */
export function record(ctx: any, request: Request, url: URL) {
  try {
    const env = ctx?.locals?.runtime?.env;
    const db: D1Database | undefined = env?.DB;
    const waitUntil = ctx?.locals?.runtime?.ctx?.waitUntil?.bind(
      ctx.locals.runtime.ctx
    );
    if (!db || request.method !== 'GET') return;

    const path = url.pathname;
    // The dashboard must not appear in its own numbers. /api/admin counts
    // too: it polls every ten seconds, so without this line an open tab
    // would show up for ever as a busy "Headless browser" crawling the
    // shop, which is both wrong and the sort of wrong that gets believed.
    if (path.startsWith('/admin') || path.startsWith('/api/admin')) return;

    const kind = kindOf(path);
    if (kind === 'asset') return;

    const ua = request.headers.get('user-agent') || '';
    const bot = botName(ua);
    const now = new Date();
    const day = now.toISOString().slice(0, 10);

    if (bot) {
      const key = `${day}\u0000${bot}\u0000${kind}`;
      pending.set(key, (pending.get(key) || 0) + 1);
      pendingTotal++;
      // Flush on COUNT, on buckets, or on age - whichever comes first.
      //
      // Counting buckets alone would not do it: a crawler hammering product
      // photographs is one bucket with a large number in it, so the map
      // never grows and the only thing forcing a write is the clock. An
      // isolate evicted mid-crawl would then take fifteen seconds of
      // Googlebot with it, which is exactly the traffic this table exists
      // to measure. 200 bounds the loss at 200 requests.
      if (pendingTotal >= 200 || pending.size >= 20 ||
          Date.now() - lastFlush > 15_000) {
        const p = flush(db).catch(() => {});
        waitUntil ? waitUntil(p) : void p;
      }
      return;
    }

    // Humans: only real pages. An image or a feed fetched by a browser is
    // part of a page view that was already counted.
    if (kind !== 'page') return;

    const ip =
      request.headers.get('cf-connecting-ip') ||
      request.headers.get('x-forwarded-for') ||
      '';
    const referer = request.headers.get('referer') || '';
    const country = (request as any).cf?.country || null;
    const src = sourceOf(url, referer);
    let refHost: string | null = null;
    try {
      const h = new URL(referer).hostname;
      refHost = h === url.hostname ? null : h.slice(0, 80);
    } catch {
      refHost = null;
    }

    const p = (async () => {
      const vid = await visitorId(ip, ua, day);
      await db
        .prepare(
          'INSERT INTO hits (ts,day,visitor,path,ref,src,country) ' +
            'VALUES (?,?,?,?,?,?,?)'
        )
        .bind(
          Math.floor(now.getTime() / 1000),
          day,
          vid,
          path.slice(0, 200),
          refHost,
          src,
          country
        )
        .run();
      // Keep the table from growing for ever, cheaply: roughly one request
      // in 200 pays for the tidy-up. 90 days is longer than any question
      // anyone asks of it.
      if (Math.random() < 0.005) {
        const cutoff = Math.floor(now.getTime() / 1000) - 90 * 86400;
        await db.prepare('DELETE FROM hits WHERE ts < ?').bind(cutoff).run();
      }
    })().catch(() => {});
    waitUntil ? waitUntil(p) : void p;
  } catch {
    /* analytics must never break a page */
  }
}
