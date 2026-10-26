# What is waiting on the seller

Updated 26 Oct 2026. Everything here needs a login, a payment, a judgement
call or a document that Claude does not and should not have. Nothing on
this list is blocked on code.

Ordered by what unblocks the most.

---

## A. To get walryvo.com live — three steps, about 40 minutes

### A1. Move the nameservers to Cloudflare

**This is the only step in the whole project that can break something that
already works.** The mailbox is Microsoft 365 via GoDaddy, and Cloudflare
will answer for the domain using only the records its scan imported. A
missed MX record kills `sales@walryvo.com` silently — the contact address
on every page of the shop and in Merchant Center.

`web/SETUP_WALKTHROUGH.md` Part 1 has the full live record set — all 12
records, read off your DNS at 15:14 on 26 Oct and stored in
`web/dns_snapshot.json`. Compare Cloudflare's import against that table
**before** switching anything at GoDaddy. Mail records must be grey-cloud
(DNS only); the SPF record looks wrong and is right, and the DKIM records
really do end in `.microsoft` — do not tidy either.

Afterwards, tell me and I run `python3 web/dns_check.py`, which compares
what the world now sees against that snapshot and fails loudly if any mail
record went missing. Then re-test the mailbox from an outside address.

### A2. Deploy — three commands

The database is already created. **Do not run `wrangler d1 create` again** -
that would make a second, empty one.

**The seed DOES need running once more.** It did not on 25 Oct, but the
schema gained a `facet_counts` table on 26 Oct and the site reads it on
every page. Deploy without reseeding and every page returns 500.

```bash
cd web/site
npm install
npx wrangler login
npm run db:seed:remote        # required - the schema changed on 26 Oct
npm run deploy
echo "sk_live_YOURKEY" | npx wrangler secret put STRIPE_SECRET_KEY
```

Or allow `npm run deploy`, `npx wrangler deploy`, `npx wrangler secret put`
and `npx wrangler d1 execute` for Bash in Claude Code settings, and a new
session can finish it. The overnight attempt was refused at exactly that
point, and self-granting the permission was refused too — correctly.

Then attach the custom domain: Workers & Pages → wallart-shop → Settings →
Domains & Routes → Add → `walryvo.com`. And a Redirect Rule so
`walryvo.co.uk` 301s to it.

### A3. Stripe, two things

- **Webhook**: Developers → Webhooks → `https://walryvo.com/api/stripe-webhook`,
  event `checkout.session.completed`. Needs the site live first. Then
  `npx wrangler secret put STRIPE_WEBHOOK_SECRET`.
- **Settings → Customer emails → Successful payments: ON.** Until this is
  on, the order-confirmed page promises an email that never arrives. It is
  the last failing preflight check — say the word and it gets flipped.

---

## B. Quick, and worth doing before Merchant Center sees you

- **Change the SIC code.** Companies House has NORYMUS LIMITED as 96090
  "other service activities", which does not describe selling art prints.
  **47910** (retail via mail order or internet) is the right one. Changed
  on a confirmation statement, which can be filed early for a small fee.
- **Check the VAT name.** Confirm GB513541030 is registered to NORYMUS
  LIMITED at <https://www.gov.uk/check-uk-vat-number>. Google compares the
  VAT record against the site. Thirty seconds.
- **Statement descriptor — seller says it is already set to `WALRYVO`**
  ("i think"), so this is a confirmation rather than a task. Settings →
  Business → Public details. Confirmed 26 Oct that the checkout code sets no
  descriptor, so Checkout falls back to the account default — likely
  NORYMUS. A buyer who sees an unrecognised name on their card statement
  three days later disputes the charge with their bank rather than emailing
  you, and Google's misrepresentation policy expects the shop, the payment
  and the business to line up. Check the public business name and support
  email on the same page read Walryvo and sales@walryvo.com.
- **Finish Stripe account verification.** The dashboard was still prompting.
  Nothing technical is blocked, but payouts are, and Merchant Center wants
  the same documents.
- **Approve the opening 240 designs by eye.** About 4% have clear defects —
  see `web/README.md`. `python3 web/catalogue/sheet.py` builds numbered
  contact sheets, `--drop 22,43,...` removes what is rejected. A morning's
  work and it cannot be automated: the detector does not discriminate.

---

## C. Decisions asked for and never answered

These have been open a while. None is urgent; all of them block something.

1. **Which R2 bucket goes to which eBay account?** Not recorded anywhere.
   Needed before anything else is matched up across the four stores.
2. **The people sweep** (`render/people_sweep.py`, about $1-2 of GPU). 17%
   of panels carry a small distant human figure — roughly 160,000 designs
   and 640,000 listings — which breaks the no-human-figures rule. Not
   portraits; the for-scale kind.
3. **Which end-listing file to use**: `ebay_end/EBAY_END_ALL.csv` (239,449,
   art and tees), `EBAY_END_ART_ONLY.csv` (127,493) or
   `EBAY_END_TEES_ONLY.csv` (111,956).
4. **The t-shirts.** `tshirt/EBAY_ONE_FILE.zip`, 105,573 listings, finished
   since 7 Oct and never uploaded. There is an unsettled shipping-policy
   conflict — the file says profile 2, CLAUDE.md says 1 — that
   `tshirt/EBAY_TEST_3.csv` settles in a single upload.

---

## D. Open from the 26 Oct repricing

- **Did the three files upload cleanly?** 502,443 listings repriced.
- **Was that export the lunar-kms account?** Flat prices were applied as
  instructed. lunar-kms is supposed to run +£10 framed / +£5 unframed. If
  it was lunar, it needs regenerating.
- **A1 SPECIAL SIZE** — 4 rows on one listing, left at £54.99 framed /
  £41.90 unframed because the price list does not cover A1. Give a price
  and it gets set.

---

## Not on this list, because it is done

The website, all 240 products and 12 categories, the logo and banner, every
policy page, the Merchant Center feed (2,160 items, 0 spec problems), the
preflight gate at 19 of 20, the eBay repricing files, and the D1 database
created and seeded. See `CLAUDE.md` for the map.
