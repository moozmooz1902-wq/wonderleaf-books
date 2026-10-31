#!/usr/bin/env node
/**
 * Generate a VAPID key pair for the back office's phone notifications.
 *
 *     node web/tools/vapid-keys.mjs
 *
 * Node only, no packages to install — you already have Node because the
 * shop is built with it. (The first version of this was Python and needed
 * the `cryptography` package, which is one more thing to go wrong on
 * somebody else's machine for no benefit.)
 *
 * RUN IT ON YOUR OWN MACHINE, not in a chat and not in a shared session.
 * The private key it prints is what lets anyone wake your phone, and a
 * secret that has been pasted into a conversation is a secret written down
 * somewhere you do not control. Nothing is saved to disk here: lose the
 * key and you generate another pair, and the phones re-subscribe the next
 * time they open /admin.
 *
 * WHAT A VAPID KEY IS. A plain P-256 key pair. The public half identifies
 * the shop to Apple's and Google's push services; the private half signs a
 * short token proving a push came from us. It is not an account and there
 * is nothing to sign up for — which is how the shop sends its own
 * notifications with no app store and no third-party service.
 */
import { generateKeyPairSync, createPublicKey } from 'node:crypto';

const b64 = (b) => Buffer.from(b).toString('base64url');

const { privateKey } = generateKeyPairSync('ec', { namedCurve: 'prime256v1' });
const jwk = createPublicKey(privateKey).export({ format: 'jwk' });
const priv = privateKey.export({ format: 'jwk' });

// Uncompressed point: 0x04 || X || Y. That is the form the browser's
// applicationServerKey wants and the form lib/push.ts checks for.
const pub = Buffer.concat([
  Buffer.from([4]),
  Buffer.from(jwk.x, 'base64url'),
  Buffer.from(jwk.y, 'base64url'),
]);

console.log(`
Two secrets. Run these from web/site and paste the value when wrangler asks:

  npx wrangler secret put VAPID_PUBLIC_KEY
     ${b64(pub)}

  npx wrangler secret put VAPID_PRIVATE_KEY
     ${priv.d}

Then: npm run deploy

On the iPhone, open walryvo.com/admin, Share -> Add to Home Screen, open it
from the new icon, and tap "Turn on notifications". iOS only allows web
notifications from an installed app, which is why the Home Screen step is
not optional.
`);
