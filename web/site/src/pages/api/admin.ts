// The dashboard's data, as JSON. Polled every few seconds by /admin.
//
// Separate from the page so the page can refresh its numbers without
// re-rendering, and so the numbers can be read from anywhere - a phone
// shortcut, a script, a second screen - with the same key.
import type { APIRoute } from 'astro';
import { getDb } from '../../lib/db';
import { adminKey, authed, dash } from '../../lib/admin';

export const prerender = false;

export const GET: APIRoute = async ({ request, locals }) => {
  const env = (locals as any)?.runtime?.env;
  const url = new URL(request.url);

  if (!adminKey(env))
    return json({ error: 'ADMIN_KEY is missing on this Worker.' }, 503);
  if (!authed(request, url, env)) return json({ error: 'Unauthorised' }, 401);

  try {
    const data = await dash(getDb(locals));
    return json(data, 200);
  } catch (e: any) {
    // The most likely cause by far is that migrate_analytics.sql has not
    // been applied yet, so say so rather than leaving a blank dashboard.
    const msg = String(e?.message || e);
    if (/no such table/i.test(msg))
      return json(
        {
          error:
            'The analytics tables do not exist yet. From web/site run: ' +
            'npx wrangler d1 execute wallart --remote ' +
            '--file=../catalogue/migrate_analytics.sql',
        },
        503
      );
    return json({ error: msg }, 500);
  }
};

function json(body: unknown, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'x-robots-tag': 'noindex, nofollow',
    },
  });
}
