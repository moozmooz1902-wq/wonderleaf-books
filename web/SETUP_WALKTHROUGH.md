# Getting walryvo.com live — step by step

Written 26 Oct. Follow it in order. **Part 1 is the only part that can
break something that currently works** (your email), so it is the slowest
and most careful.

Split by who does what:

| Part | Who |
|---|---|
| 1. Add domain to Cloudflare, fix DNS | **You** — needs your Cloudflare login |
| 2. Switch nameservers | **You** — needs your GoDaddy login |
| 3. Test email still works | **You** — one minute |
| 4. Deploy the shop | **Me**, if you add two tokens — or you, with 5 commands |
| 5. Stripe webhook | **You** — needs the dashboard |
| 6. Live checks + feed | **Me** |

---

## PART 1 — Add the domain to Cloudflare

Nothing changes on the live domain during this part. Cloudflare only starts
answering for walryvo.com after Part 2.

**Use the same Cloudflare account that holds your R2 buckets** (luxvia-art,
posterleaf-store1, lunar-kms, mercury-usm). The shop reads images straight
out of those buckets, and that only works if the Worker and the buckets are
in one account.

1. Sign in at **dash.cloudflare.com**.
2. Top of the page: **Add a domain** (older accounts say *Add site*).
3. Type `walryvo.com`. Choose **Free**. Continue.
4. Cloudflare scans your existing DNS and shows what it found. **Do not
   press Continue yet.**

### 1a. Check the scan against this — the important bit

Cloudflare will answer for your domain using *only* the records in this
list. Anything its scan missed stops existing the moment Part 2 finishes.
The records that matter most are the mail ones: miss them and
`sales@walryvo.com` dies silently, which is the contact address on every
page of the shop and in Merchant Center.

Captured live from your DNS on 26 Oct. Every one of these must be present:

| Type | Name | Value | Proxy |
|---|---|---|---|
| MX | `walryvo.com` | `walryvo-com.mail.protection.outlook.com` (priority 0) | DNS only |
| TXT | `walryvo.com` | `v=spf1 include:secureserver.net -all` | n/a |
| TXT | `walryvo.com` | `NETORGFT21256617.onmicrosoft.com` | n/a |
| CNAME | `autodiscover` | `autodiscover.outlook.com` | **DNS only** |
| CNAME | `selector1._domainkey` | `selector1-walryvo-com._domainkey.netorgft21256617.r-v1.dkim.mail.microsoft` | **DNS only** |
| CNAME | `selector2._domainkey` | `selector2-walryvo-com._domainkey.netorgft21256617.r-v1.dkim.mail.microsoft` | **DNS only** |
| TXT | `_dmarc` | `v=DMARC1; p=quarantine; adkim=r; aspf=r; rua=mailto:dmarc_rua@onsecureserver.net;` | n/a |
| SRV | `_sip._tls` | `100 1 443 sipdir.online.lync.com` | n/a |

**"DNS only" means the cloud icon must be GREY, not orange.** An orange
cloud on a mail record breaks mail delivery. Click the cloud to toggle it.

Add by hand anything the scan missed.

### 1b. Delete these three

They are the registrar's parking page. The Worker replaces them in Part 4.

- `A` → `15.197.148.33`
- `A` → `3.33.130.190`
- `CNAME` `www` → `walryvo.com`

### 1c. Do not "fix" the SPF record

`v=spf1 include:secureserver.net -all` looks wrong for a Microsoft mailbox.
It is right. I traced the chain on 26 Oct: `secureserver.net` →
`spf-0.secureserver.net` → includes `spf.protection.outlook.com`. Changing
it to something that looks more sensible will break your outgoing mail.

Now press Continue. Cloudflare shows you two nameservers like
`xxx.ns.cloudflare.com`. Copy both.

---

## PART 2 — Point the nameservers at Cloudflare (GoDaddy)

1. Sign in at **godaddy.com** → **My Products** → **Domains**.
2. Click `walryvo.com`.
3. Find **Nameservers** → **Change**.
4. Choose **I'll use my own nameservers** (sometimes *Enter my own
   nameservers (advanced)*).
5. Replace both entries with the two Cloudflare gave you. Save.
6. GoDaddy may warn that services will be affected. That is expected —
   you copied the records in Part 1.

Takes anywhere from 10 minutes to a few hours. Cloudflare emails you when
the domain is active.

---

## PART 3 — Prove your email still works

**Do not skip this.** From a different address (phone, Gmail, anything not
on walryvo.com), send a message to `sales@walryvo.com`. Confirm it arrives.
Then reply from it and confirm the reply lands.

If mail has stopped: go back to Part 1a and compare the records again. The
old records are still at GoDaddy and can be read from the DNS zone there.

---

## PART 4 — Deploy the shop

### Option A — I do it (easier)

Add two credentials in the environment settings panel — the cloud
environment menu in this session's title bar, then **Edit**, under
**Network secrets** (or *API credentials*):

| Name | What |
|---|---|
| `CLOUDFLARE_API_TOKEN` | dash.cloudflare.com → My Profile → API Tokens → Create Token → Custom token |
| `STRIPE_SECRET_KEY` | Stripe → Developers → API keys → secret key |

The Cloudflare token needs these permissions:

- Account → **Workers Scripts** → Edit
- Account → **D1** → Edit
- Account → **Workers R2 Storage** → Edit
- Zone → **DNS** → Edit (zone: walryvo.com)
- Zone → **Workers Routes** → Edit (zone: walryvo.com)

**A new session picks these up** — they will not appear in the session
that is already running. Start a fresh one and say "deploy it".

This is why the keys go in the panel rather than the chat: the panel is
built for credentials, a chat transcript is a stored record, and a live
secret key in a stored record is a leaked key no matter who reads it.

### Option B — you do it (5 commands)

In a terminal with Node installed, in the `web/site` folder:

```bash
npm install
npx wrangler login                    # opens a browser
npx wrangler d1 create wallart        # paste the printed id into wrangler.toml
npm run db:seed:remote                # loads 240 products / 2,160 variants
npm run deploy
npx wrangler secret put STRIPE_SECRET_KEY   # paste at the prompt
```

Then in the Cloudflare dashboard: **Workers & Pages → wallart-shop →
Settings → Domains & Routes → Add → Custom domain → `walryvo.com`**.

Add a second Redirect Rule so `walryvo.co.uk` 301s to `walryvo.com`
(Rules → Redirect Rules → hostname equals `walryvo.co.uk` → dynamic →
`concat("https://walryvo.com", http.request.uri.path)` → 301).

---

## PART 5 — Stripe webhook

Only possible once the site answers on https://walryvo.com.

1. Stripe → **Developers → Webhooks → Add endpoint**
2. URL: `https://walryvo.com/api/stripe-webhook`
3. Event: `checkout.session.completed`
4. Stripe shows a signing secret starting `whsec_` →
   `npx wrangler secret put STRIPE_WEBHOOK_SECRET` (or add it to the panel
   and I will set it)
5. Stripe → **Settings → Customer emails → Successful payments: ON**
6. Tell me, and I set `order_confirmation_email: true` — the last failing
   preflight check

---

## PART 6 — Then I run the checks

```bash
python3 catalogue/preflight.py --live -n 60
```

That fetches the real site and proves, among 13 other things, that every
sampled variant URL quotes the same price the feed does — the mismatch
that got the Shopify shop suspended.

**Only after that is green does anything go to Merchant Center.**

---

## Order of operations, one line

DNS copied → nameservers switched → email retested → deployed → Stripe
secrets → live preflight green → **then** Search Console, then Merchant
Center, then the feed.
