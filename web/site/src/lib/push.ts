/**
 * PUSH NOTIFICATIONS TO A PHONE, with no app store and no third party.
 *
 * Asked for on 31 Oct: "notifications on my iPhone when an order comes in".
 *
 * iOS 16.4 and later support the Web Push standard, but only for a site
 * that has been added to the Home Screen. So /admin ships a manifest and a
 * service worker, "Add to Home Screen" turns it into an app icon, and from
 * then on it can be woken by a push like any other app. No App Store
 * account, no Pushover, no Firebase, nothing to pay for.
 *
 * THE TRICK THAT MAKES THIS SHORT: THE PUSH CARRIES NO PAYLOAD.
 *
 * A normal web push encrypts its body to the subscription's keys - ECDH on
 * P-256, HKDF, AES-128-GCM, a specific record layout. That is a few hundred
 * lines of cryptography which is wrong until it is exactly right, and wrong
 * here means a notification that silently never arrives.
 *
 * It is also unnecessary. The standard allows a push with no body at all.
 * The phone wakes the service worker, and the service worker - which is on
 * our own origin and carries the admin cookie - simply asks the shop what
 * happened. So the only cryptography left is signing a VAPID token, which
 * is one ES256 signature that WebCrypto does natively.
 *
 * The side effect is a better guarantee than the usual one: nothing about
 * an order ever passes through Apple's or Google's push servers. They are
 * told only that this endpoint should wake up. The order details travel
 * from our Worker to the phone over our own TLS connection.
 *
 * KEYS. A VAPID key pair is a P-256 key pair. Generate it with
 * `python3 web/tools/vapid_keys.py` and set both halves as secrets; the
 * script prints the commands. The private key never passes through a chat,
 * a file in the repo, or anyone's clipboard history if you follow it.
 */

const b64url = (b: ArrayBuffer | Uint8Array) => {
  const u = b instanceof Uint8Array ? b : new Uint8Array(b);
  let s = '';
  for (const x of u) s += String.fromCharCode(x);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
};

const fromB64url = (s: string) => {
  const pad = s.replace(/-/g, '+').replace(/_/g, '/');
  const bin = atob(pad + '='.repeat((4 - (pad.length % 4)) % 4));
  const u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return u;
};

export interface Vapid {
  publicKey: string;   // base64url, uncompressed P-256 point (65 bytes)
  privateKey: string;  // base64url, 32-byte scalar
  subject: string;     // mailto: for the push service to complain to
}

export function vapid(env: any, email: string): Vapid | null {
  const publicKey = env?.VAPID_PUBLIC_KEY;
  const privateKey = env?.VAPID_PRIVATE_KEY;
  if (!publicKey || !privateKey) return null;
  return { publicKey, privateKey, subject: `mailto:${email}` };
}

/**
 * Import the raw 32-byte private scalar as an ECDSA key.
 *
 * WebCrypto will not take a bare scalar, so it is wrapped in a JWK next to
 * the public point it belongs to - which is why both halves are needed to
 * sign, not just the private one.
 */
async function signingKey(v: Vapid) {
  const pub = fromB64url(v.publicKey);
  if (pub.length !== 65 || pub[0] !== 4)
    throw new Error(
      'VAPID_PUBLIC_KEY is not a 65-byte uncompressed P-256 point. ' +
        'Regenerate with web/tools/vapid_keys.py.'
    );
  const jwk: JsonWebKey = {
    kty: 'EC',
    crv: 'P-256',
    x: b64url(pub.slice(1, 33)),
    y: b64url(pub.slice(33, 65)),
    d: v.privateKey,
    ext: true,
  };
  return crypto.subtle.importKey('jwk', jwk, { name: 'ECDSA', namedCurve: 'P-256' },
                                 false, ['sign']);
}

async function vapidHeader(v: Vapid, endpoint: string) {
  const aud = new URL(endpoint).origin;
  const header = b64url(new TextEncoder().encode(JSON.stringify({ typ: 'JWT', alg: 'ES256' })));
  const claims = b64url(
    new TextEncoder().encode(
      JSON.stringify({
        aud,
        // 12 hours. The spec allows 24; staying well under it avoids the
        // "token expired" rejections that a clock a few minutes out would
        // otherwise cause.
        exp: Math.floor(Date.now() / 1000) + 12 * 3600,
        sub: v.subject,
      })
    )
  );
  const body = `${header}.${claims}`;
  const sig = await crypto.subtle.sign(
    { name: 'ECDSA', hash: 'SHA-256' },
    await signingKey(v),
    new TextEncoder().encode(body)
  );
  // WebCrypto returns r||s, which is exactly what JWS ES256 wants.
  return `vapid t=${body}.${b64url(sig)}, k=${v.publicKey}`;
}

export interface PushResult {
  sent: number;
  gone: string[];     // endpoints the push service says no longer exist
  errors: string[];
}

/**
 * Wake every subscribed phone. Bodyless, urgent, four hours to live.
 *
 * A 404 or 410 from the push service means that subscription is dead - the
 * app was deleted or the browser cleared it - and the row is removed. Any
 * other failure is reported but kept, because a push service having a bad
 * ten minutes is not a reason to forget somebody's phone.
 */
export async function pushAll(db: D1Database, v: Vapid, ttl = 4 * 3600): Promise<PushResult> {
  const subs = await db.prepare('SELECT endpoint FROM push_subs').all<any>();
  const out: PushResult = { sent: 0, gone: [], errors: [] };
  for (const row of subs.results || []) {
    const endpoint: string = row.endpoint;
    try {
      const r = await fetch(endpoint, {
        method: 'POST',
        headers: {
          authorization: await vapidHeader(v, endpoint),
          ttl: String(ttl),
          urgency: 'high',
          // No body, so no Content-Encoding and no Content-Length.
        },
      });
      if (r.status === 404 || r.status === 410) {
        out.gone.push(endpoint);
      } else if (!r.ok) {
        out.errors.push(`${r.status} ${(await r.text().catch(() => '')).slice(0, 120)}`);
      } else {
        out.sent++;
      }
    } catch (e: any) {
      out.errors.push(String(e?.message || e).slice(0, 120));
    }
  }
  if (out.gone.length) {
    const del = db.prepare('DELETE FROM push_subs WHERE endpoint = ?');
    await db.batch(out.gone.map((e) => del.bind(e))).catch(() => {});
  }
  if (out.sent) {
    await db
      .prepare('UPDATE push_subs SET last_ok = ?, fails = 0')
      .bind(new Date().toISOString())
      .run()
      .catch(() => {});
  }
  return out;
}
