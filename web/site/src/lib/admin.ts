/**
 * The dashboard's authentication and its queries, kept out of the page so
 * the page is only layout.
 *
 * AUTHENTICATION IS A SHARED SECRET, AND THE SECRET MUST EXIST. There is no
 * default key and no "if unset, allow": a missing ADMIN_KEY makes /admin
 * answer 503, because the failure mode of the alternative is publishing the
 * shop's order history and every visitor's movements to anyone who guesses
 * a URL. Set it once, from web/site:
 *
 *     npx wrangler secret put ADMIN_KEY
 *
 * The key is compared in constant time, which matters more than it looks:
 * a plain === on a secret leaks its length and then its contents to anyone
 * willing to time a few thousand requests.
 */

export const COOKIE = 'wa_admin';

export function adminKey(env: any): string | null {
  const k = env?.ADMIN_KEY;
  return typeof k === 'string' && k.length >= 8 ? k : null;
}

function same(a: string, b: string) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

export function presented(request: Request, url: URL): string | null {
  const q = url.searchParams.get('key');
  if (q) return q;
  const raw = request.headers.get('cookie') || '';
  for (const part of raw.split(';')) {
    const [n, ...v] = part.trim().split('=');
    if (n === COOKIE) return decodeURIComponent(v.join('='));
  }
  return null;
}

export function authed(request: Request, url: URL, env: any): boolean {
  const want = adminKey(env);
  if (!want) return false;
  const got = presented(request, url);
  return !!got && same(got, want);
}

export function cookieHeader(key: string, secure: boolean) {
  // HttpOnly so no script on the page can read it, SameSite=Lax so it is not
  // sent on cross-site requests, 30 days so the shop owner is not typing a
  // key into their phone every morning.
  return (
    `${COOKIE}=${encodeURIComponent(key)}; Path=/; HttpOnly; SameSite=Lax; ` +
    `Max-Age=${30 * 86400}${secure ? '; Secure' : ''}`
  );
}

// ---------------------------------------------------------------------------

const DAY = 86400;

export interface Dash {
  now: number;
  live: number;
  liveList: { path: string; src: string; country: string | null; ago: number }[];
  views: { today: number; d7: number; d30: number };
  visitors: { today: number; d7: number; d30: number };
  series: { day: string; views: number; visitors: number }[];
  pages: { path: string; n: number }[];
  sources: { src: string; n: number; visitors: number }[];
  countries: { country: string; n: number }[];
  google: { shopping7: number; search7: number; shoppingAll: number; searchAll: number };
  crawls: { bot: string; pages: number; images: number; feeds: number; other: number }[];
  crawlDays: { day: string; n: number }[];
  orders: {
    count: { today: number; d7: number; d30: number; all: number };
    revenue: { today: number; d7: number; d30: number; all: number };
    recent: { id: string; created: string; total: number; currency: string; status: string; email: string | null }[];
  };
  checkouts: { d7: number; d30: number; all: number };
  catalogue: { products: number; variants: number };
}

/** Fill in the days nothing happened, so the chart is a fortnight wide. */
function padDays(rows: any[], days: number, now: number) {
  const have = new Map(rows.map((r) => [r.day, r]));
  const out = [];
  for (let i = days - 1; i >= 0; i--) {
    const day = new Date((now - i * DAY) * 1000).toISOString().slice(0, 10);
    const r = have.get(day);
    out.push({
      day,
      views: Number(r?.v || 0),
      visitors: Number(r?.u || 0),
    });
  }
  return out;
}

/** One round of every number the dashboard shows. */
export async function dash(db: D1Database): Promise<Dash> {
  const now = Math.floor(Date.now() / 1000);
  const t0 = now - 300; // "live" is the last five minutes
  const dToday = new Date().toISOString().slice(0, 10);
  const d7 = now - 7 * DAY;
  const d30 = now - 30 * DAY;
  const day7 = new Date((now - 7 * DAY) * 1000).toISOString().slice(0, 10);
  const day14 = new Date((now - 13 * DAY) * 1000).toISOString().slice(0, 10);

  const q = (sql: string, ...b: any[]) => db.prepare(sql).bind(...b);
  const rs = await db.batch<any>([
    q('SELECT COUNT(DISTINCT visitor) c FROM hits WHERE ts > ?', t0),
    q('SELECT path, src, country, ts FROM hits WHERE ts > ? ORDER BY ts DESC LIMIT 20', t0),
    q('SELECT COUNT(*) v, COUNT(DISTINCT visitor) u FROM hits WHERE day = ?', dToday),
    q('SELECT COUNT(*) v, COUNT(DISTINCT visitor) u FROM hits WHERE ts > ?', d7),
    q('SELECT COUNT(*) v, COUNT(DISTINCT visitor) u FROM hits WHERE ts > ?', d30),
    q('SELECT day, COUNT(*) v, COUNT(DISTINCT visitor) u FROM hits WHERE day >= ? GROUP BY day ORDER BY day', day14),
    q('SELECT path, COUNT(*) n FROM hits WHERE ts > ? GROUP BY path ORDER BY n DESC LIMIT 10', d7),
    q('SELECT src, COUNT(*) n, COUNT(DISTINCT visitor) u FROM hits WHERE ts > ? GROUP BY src ORDER BY n DESC LIMIT 10', d7),
    q('SELECT country, COUNT(*) n FROM hits WHERE ts > ? AND country IS NOT NULL GROUP BY country ORDER BY n DESC LIMIT 8', d7),
    q("SELECT SUM(src='google-shopping') s7, SUM(src='google-search') g7 FROM hits WHERE ts > ?", d7),
    q("SELECT SUM(src='google-shopping') sa, SUM(src='google-search') ga FROM hits"),
    q("SELECT bot, SUM(CASE WHEN kind='page' THEN n ELSE 0 END) p, SUM(CASE WHEN kind='image' THEN n ELSE 0 END) i, SUM(CASE WHEN kind='feed' THEN n ELSE 0 END) f, SUM(CASE WHEN kind NOT IN ('page','image','feed') THEN n ELSE 0 END) o FROM crawls WHERE day >= ? GROUP BY bot ORDER BY p+i+f+o DESC LIMIT 12", day7),
    q('SELECT day, SUM(n) n FROM crawls WHERE day >= ? GROUP BY day ORDER BY day', day14),
    q("SELECT COUNT(*) c, COALESCE(SUM(total),0) t FROM orders WHERE substr(created,1,10) = ?", dToday),
    q("SELECT COUNT(*) c, COALESCE(SUM(total),0) t FROM orders WHERE created >= ?", new Date((now - 7 * DAY) * 1000).toISOString()),
    q("SELECT COUNT(*) c, COALESCE(SUM(total),0) t FROM orders WHERE created >= ?", new Date((now - 30 * DAY) * 1000).toISOString()),
    q('SELECT COUNT(*) c, COALESCE(SUM(total),0) t FROM orders'),
    q('SELECT id, created, total, currency, status, email FROM orders ORDER BY created DESC LIMIT 10'),
    q('SELECT COUNT(*) c FROM checkouts WHERE ts > ?', d7),
    q('SELECT COUNT(*) c FROM checkouts WHERE ts > ?', d30),
    q('SELECT COUNT(*) c FROM checkouts'),
    q('SELECT (SELECT COUNT(*) FROM products) p, (SELECT COUNT(*) FROM variants) v'),
  ]);

  const one = (i: number) => (rs[i].results?.[0] as any) || {};
  const all = (i: number) => (rs[i].results as any[]) || [];
  const n = (x: any) => Number(x || 0);

  return {
    now,
    live: n(one(0).c),
    liveList: all(1).map((r) => ({
      path: r.path, src: r.src, country: r.country, ago: now - n(r.ts),
    })),
    views: { today: n(one(2).v), d7: n(one(3).v), d30: n(one(4).v) },
    visitors: { today: n(one(2).u), d7: n(one(3).u), d30: n(one(4).u) },
    // FOURTEEN BARS, ALWAYS. A day with no visitors is a fact about the
    // shop and belongs on the chart; leaving it out makes one quiet day
    // look like a full fortnight of traffic, which on day one of recording
    // is the most misleading possible picture.
    series: padDays(all(5), 14, now),
    pages: all(6).map((r) => ({ path: r.path, n: n(r.n) })),
    sources: all(7).map((r) => ({ src: r.src || 'direct', n: n(r.n), visitors: n(r.u) })),
    countries: all(8).map((r) => ({ country: r.country, n: n(r.n) })),
    google: {
      shopping7: n(one(9).s7), search7: n(one(9).g7),
      shoppingAll: n(one(10).sa), searchAll: n(one(10).ga),
    },
    crawls: all(11).map((r) => ({
      bot: r.bot, pages: n(r.p), images: n(r.i), feeds: n(r.f), other: n(r.o),
    })),
    crawlDays: all(12).map((r) => ({ day: r.day, n: n(r.n) })),
    orders: {
      count: { today: n(one(13).c), d7: n(one(14).c), d30: n(one(15).c), all: n(one(16).c) },
      revenue: { today: n(one(13).t), d7: n(one(14).t), d30: n(one(15).t), all: n(one(16).t) },
      recent: all(17).map((r) => ({
        id: r.id, created: r.created, total: n(r.total),
        currency: r.currency, status: r.status, email: r.email,
      })),
    },
    checkouts: { d7: n(one(18).c), d30: n(one(19).c), all: n(one(20).c) },
    catalogue: { products: n(one(21).p), variants: n(one(21).v) },
  };
}
