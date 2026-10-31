// The support inbox, behind the admin key.
//
// GET  /api/mail             -> the 25 newest messages
// GET  /api/mail?id=...      -> one message in full, and marks it read
// POST /api/mail {id, text}  -> reply in the thread, as sales@walryvo.com
//
// Everything is live from Microsoft 365. Nothing is copied into D1 - see
// the note at the top of lib/mail.ts for why that is deliberate.
import type { APIRoute } from 'astro';
import { adminKey, authed } from '../../lib/admin';
import { mailCfg, listMail, readMail, replyMail } from '../../lib/mail';
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

function gate(request: Request, url: URL, env: any) {
  if (!adminKey(env)) return json({ error: 'ADMIN_KEY is missing.' }, 503);
  if (!authed(request, url, env)) return json({ error: 'Unauthorised' }, 401);
  return null;
}

export const GET: APIRoute = async ({ request, locals }) => {
  const env = (locals as any)?.runtime?.env;
  const url = new URL(request.url);
  const stop = gate(request, url, env);
  if (stop) return stop;

  const cfg = mailCfg(env, B.email);
  // NOT an error. The inbox is an optional extra and the rest of the back
  // office works without it, so say plainly that it is switched off rather
  // than making the whole dashboard look broken.
  if (!cfg) return json({ configured: false, messages: [] });

  try {
    const id = url.searchParams.get('id');
    if (id) return json({ configured: true, message: await readMail(cfg, id) });
    return json({ configured: true, messages: await listMail(cfg, 25) });
  } catch (e: any) {
    return json({ configured: true, error: String(e?.message || e) }, 502);
  }
};

export const POST: APIRoute = async ({ request, locals }) => {
  const env = (locals as any)?.runtime?.env;
  const url = new URL(request.url);
  const stop = gate(request, url, env);
  if (stop) return stop;

  const cfg = mailCfg(env, B.email);
  if (!cfg) return json({ error: 'The inbox is not configured.' }, 503);

  let body: any;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Bad request' }, 400);
  }
  const id = String(body?.id || '');
  const text = String(body?.text || '').trim();
  if (!id) return json({ error: 'Which message?' }, 400);
  if (!text) return json({ error: 'The reply is empty.' }, 400);
  // A reply is sent to a real customer and cannot be unsent. The limit is
  // not about storage; it is a guard against a stuck key repeating itself
  // into somebody's inbox.
  if (text.length > 20000) return json({ error: 'That reply is too long.' }, 400);

  try {
    await replyMail(cfg, id, text);
    return json({ ok: true });
  } catch (e: any) {
    return json({ error: String(e?.message || e) }, 502);
  }
};
