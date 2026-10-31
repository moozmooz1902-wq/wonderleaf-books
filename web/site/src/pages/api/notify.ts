// What a woken phone should say.
//
// The push itself carries no payload (see lib/push.ts), so the service
// worker asks this endpoint what happened and builds the notification from
// the answer. That keeps every detail of an order on our own connection
// rather than passing it through Apple's or Google's push servers.
import type { APIRoute } from 'astro';
import { adminKey, authed } from '../../lib/admin';
import { getDb } from '../../lib/db';
import { mailCfg, listMail } from '../../lib/mail';
import { B } from '../../lib/shop';

export const prerender = false;

export const GET: APIRoute = async ({ request, locals }) => {
  const env = (locals as any)?.runtime?.env;
  const url = new URL(request.url);
  const out = (b: unknown, s = 200) =>
    new Response(JSON.stringify(b), {
      status: s,
      headers: {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'no-store',
        'x-robots-tag': 'noindex, nofollow',
      },
    });

  if (!adminKey(env)) return out({ error: 'ADMIN_KEY is missing.' }, 503);
  if (!authed(request, url, env)) return out({ error: 'Unauthorised' }, 401);

  const db = getDb(locals);
  let order: any = null;
  let todayCount = 0;
  let todayTotal = 0;
  try {
    const today = new Date().toISOString().slice(0, 10);
    const rs = await db.batch<any>([
      db.prepare('SELECT id,created,total,currency,email FROM orders ORDER BY created DESC LIMIT 1'),
      db.prepare("SELECT COUNT(*) c, COALESCE(SUM(total),0) t FROM orders WHERE substr(created,1,10)=?").bind(today),
    ]);
    order = rs[0].results?.[0] || null;
    todayCount = Number(rs[1].results?.[0]?.c || 0);
    todayTotal = Number(rs[1].results?.[0]?.t || 0);
  } catch { /* the dashboard reports a missing table; a notification should not */ }

  let unread = 0;
  const cfg = mailCfg(env, B.email);
  if (cfg) {
    try {
      unread = (await listMail(cfg, 25)).filter((m) => !m.read).length;
    } catch { /* the inbox being down is not worth a silent notification */ }
  }

  const money = (n: number) =>
    '£' + Number(n || 0).toLocaleString('en-GB', { minimumFractionDigits: 2 });

  // Orders come first: that is what the phone is for. An unread customer
  // email is the fallback so a push is never shown with nothing in it.
  let title = 'Walryvo';
  let body = 'Open the back office';
  let tag = 'walryvo';
  if (order) {
    title = `New order — ${money(order.total)}`;
    body =
      (order.email ? `${order.email} · ` : '') +
      `${todayCount} order${todayCount === 1 ? '' : 's'} today, ${money(todayTotal)}`;
    tag = `order-${order.id}`;
  } else if (unread) {
    title = `${unread} unread customer email${unread === 1 ? '' : 's'}`;
    body = 'Open the inbox';
    tag = 'mail';
  }

  return out({ title, body, tag, url: '/admin', unread, todayCount, todayTotal });
};
