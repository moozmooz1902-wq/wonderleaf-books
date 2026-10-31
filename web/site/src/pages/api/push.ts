// Phone notifications: subscribe, unsubscribe, and a test push.
//
// GET  /api/push             -> { configured, publicKey, count }
// POST /api/push {subscription}        -> remember this phone
// POST /api/push {unsubscribe:endpoint}-> forget it
// POST /api/push {test:true}           -> wake every subscribed phone now
import type { APIRoute } from 'astro';
import { adminKey, authed } from '../../lib/admin';
import { getDb } from '../../lib/db';
import { vapid, pushAll } from '../../lib/push';
import { B } from '../../lib/shop';

export const prerender = false;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'x-robots-tag': 'noindex, nofollow',
    },
  });

export const GET: APIRoute = async ({ request, locals }) => {
  const env = (locals as any)?.runtime?.env;
  const url = new URL(request.url);
  if (!adminKey(env)) return json({ error: 'ADMIN_KEY is missing.' }, 503);
  if (!authed(request, url, env)) return json({ error: 'Unauthorised' }, 401);

  const v = vapid(env, B.email);
  if (!v) return json({ configured: false, publicKey: null, count: 0 });
  let count = 0;
  try {
    const r = await getDb(locals).prepare('SELECT COUNT(*) c FROM push_subs').first<any>();
    count = Number(r?.c || 0);
  } catch { /* table may not exist yet */ }
  return json({ configured: true, publicKey: v.publicKey, count });
};

export const POST: APIRoute = async ({ request, locals }) => {
  const env = (locals as any)?.runtime?.env;
  const url = new URL(request.url);
  if (!adminKey(env)) return json({ error: 'ADMIN_KEY is missing.' }, 503);
  if (!authed(request, url, env)) return json({ error: 'Unauthorised' }, 401);

  const v = vapid(env, B.email);
  if (!v) return json({ error: 'Notifications are not configured.' }, 503);
  const db = getDb(locals);

  let body: any;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Bad request' }, 400);
  }

  try {
    if (body?.test) {
      const r = await pushAll(db, v);
      return json({
        ok: true,
        ...r,
        // Said out loud because "it worked" and "there was nobody to tell"
        // look identical from a phone that is not the one subscribed.
        note: r.sent
          ? `Woke ${r.sent} device(s).`
          : 'No subscribed devices — turn notifications on from the phone first.',
      });
    }

    if (body?.unsubscribe) {
      await db.prepare('DELETE FROM push_subs WHERE endpoint = ?')
        .bind(String(body.unsubscribe)).run();
      return json({ ok: true });
    }

    const s = body?.subscription;
    const endpoint = String(s?.endpoint || '');
    if (!/^https:\/\//.test(endpoint))
      return json({ error: 'That is not a push subscription.' }, 400);
    await db
      .prepare(
        'INSERT INTO push_subs (endpoint,p256dh,auth,created) VALUES (?,?,?,?) ' +
          'ON CONFLICT(endpoint) DO UPDATE SET p256dh=excluded.p256dh, ' +
          'auth=excluded.auth, fails=0'
      )
      .bind(
        endpoint,
        s?.keys?.p256dh ?? null,
        s?.keys?.auth ?? null,
        new Date().toISOString()
      )
      .run();
    return json({ ok: true });
  } catch (e: any) {
    const msg = String(e?.message || e);
    if (/no such table/i.test(msg))
      return json(
        { error: 'Run migrate_analytics.sql first — push_subs is missing.' },
        503
      );
    return json({ error: msg }, 500);
  }
};
