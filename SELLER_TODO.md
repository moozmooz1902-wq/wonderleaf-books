# What is waiting on the seller

Updated 26 Oct 2026, late evening. Everything here needs a login, a payment, a judgement
call or a document that Claude does not and should not have. Nothing on
this list is blocked on code.

Ordered by what unblocks the most.

---

## A. walryvo.com is LIVE — done 26 Oct

Nothing in this section is outstanding. Kept as a record of what was done
and by whom, because several of these were the seller's logins and will be
again if anything needs redoing.

| | |
|---|---|
| Nameservers moved to Cloudflare | seller, 17:05 |
| Zone active, all 12 records intact, mail verified | 17:20 |
| Deployed from the seller's Mac | seller, 18:06 |
| walryvo.com + www attached to the Worker | over the API, 18:26 |
| `STRIPE_SECRET_KEY` set, checkout proven live | 18:26 |
| `STRIPE_WEBHOOK_SECRET` set, endpoint enabled | 18:36 |
| Bright black-and-white theme deployed | 18:31 |

Checkout was tested end to end rather than assumed: a real Stripe Checkout
session (`cs_live_...`) was created from a real variant id, HTTP 200. The
key is a RESTRICTED key (`rk_live_`), which is the safer choice and does
carry the scope.

**Three bugs only a real deploy could have found**, all fixed:

1. `site/src/data/*.json` were gitignored, so a fresh checkout would not
   build at all.
2. `cart.astro` used Astro's `define:vars`, the one critical CVE of the
   eleven npm reports that was actually in the shipped site. Replaced with
   data attributes; the other ten are build tooling and do not ship.
3. `wrangler.toml` points `[assets]` at `./dist`, and the adapter does not
   emit a `.assetsignore`, so the compiled server — including the Stripe
   route — would have been published as downloadable files. The build now
   writes that file itself.

And one found by looking at the live site rather than the deploy output:
the first theme deploy rendered walryvo.com as **unstyled HTML**, because
the edge cache held the previous build's page, which names a hashed
stylesheet the deploy had just deleted. The cache key now carries a build
id, so it cannot recur.

## Changing the shop's colours

One word. `web/business.config.json`, the `"theme"` field:

| Name | What it is |
|---|---|
| `ink-black` | black page, white type |
| `paper-white` | white page, black type |
| `gallery-cream` | the exact cream the mockups are photographed on, so prints have no visible edge — **current** |
| `plaster-pink` | warm gallery pink, claret accent |

Change it, then `python3 web/catalogue/build_db.py` and deploy. Nothing else
needs touching: `themes.json` holds the palettes, build_db.py writes
`theme.css`, and every rule in the stylesheet takes its colour from those
tokens. There is no hex value anywhere else.

To add a shade, copy a block in `web/themes.json` and give it a name. Every
preset must define every token — there is no fallback, and a missing one is
an invisible colour rather than an error.

The one token that is not a taste decision is `plate-wall`, the background
behind the big images. Every mockup is a framed print on flat cream,
rgb(237,234,227), baked into the photograph. On a light theme set it to that
exact value and the picture has no edge; on a dark one set it near the page
colour and the print reads as a lit panel on a dark wall.

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

## B1. The back office — three commands, then you can see everything

Added 31 Oct. `walryvo.com/admin` shows live visitors, orders, revenue,
conversion, where traffic came from and which search engines have crawled
the shop. Until this is deployed **there is no way to know whether anyone
is visiting at all** — Cloudflare's analytics need a permission our token
does not have and Merchant Center has no engagement API.

From `web/site`, after `git pull`:

```bash
npx wrangler d1 execute wallart --remote --file=../catalogue/migrate_analytics.sql
npx wrangler secret put ADMIN_KEY     # type a long password when prompted
npm run deploy
```

Then open <https://walryvo.com/admin>. `web/DASHBOARD.md` explains every
number — the one to watch is **Google Shopping**, which counts clicks
arriving with Google's own `srsltid` marker and is therefore direct proof
the Merchant Center feed earned a visit.

**As of 31 Oct the shop has had 0 orders.** Nine Stripe checkout sessions
exist and all nine are ours, created by preflight's own tests. There is no
customer data to read yet, from anywhere.

---

## B2. Merchant Center — what you do, and the one thing I need

The feed is already live and already automatic. Nothing gets uploaded by
hand, now or ever:

| | |
|---|---|
| Products | <https://walryvo.com/feed.xml> — 2,508 items |
| Promotions | <https://walryvo.com/promotions.xml> — buy 2 get 1 free |

Both are served by the same Worker that serves the shop, out of the same
deploy. Google re-reads them daily on its own, so they cannot drift behind
the site, and `preflight.py --live` compares the served feed byte for byte
against the catalogue so a deploy can never quietly ship a stale one.

### NO BARCODES. Not one. This is the whole point of this channel.

Asked twice on 28 Oct, so it is written down here rather than only in
`web/catalogue/feed.py`. **Google does not require a GTIN for goods that
have never had one** — made-to-order, custom and own-brand products are
exactly the case it provides for. You supply **brand + MPN** instead, and
the feed has done that from the day it was built. Measured on the live
feed just now:

| | |
|---|---|
| `g:gtin` tags | **0** |
| `g:brand` | 2,508 |
| `g:mpn` | 2,508 |
| `identifier_exists` | 0 — deliberately absent |

That last row is the subtle one. With brand and MPN present you must **not**
set `identifier_exists` to `no`; omitting it lets Google's default apply.
Setting it to `no` on a product that does have a GTIN is a policy violation,
so the safe construction is the one already in place.

**This is the asymmetry that decides the whole strategy.** OnBuy demands a
GS1-registered EAN per variant and refuses all exemptions, so volume there
costs real money. Google accepts brand + MPN, so **walryvo.com can carry
the entire catalogue at zero barcode cost.** If the plan is "list
everything", this is the channel it belongs on — see
`wallart-data/onbuy/BARCODE_COSTING.md` §4.

### Your five steps

1. **Sign up** at <https://merchants.google.com> — **use
   sales@walryvo.com, not the Gmail.** A Google Account does not need a
   @gmail.com address; create one on the Microsoft 365 mailbox at
   <https://accounts.google.com/signup> → "Use my current email address
   instead". Decided 28 Oct, and it is free to decide now because nothing
   is tied to the Gmail yet: Search Console is not set up and there is no
   verification tag on the site.

   **Why the professional one.** It matches the domain being claimed, it
   is a business asset rather than a personal one if anyone else ever runs
   the shop, and the site, the feed and every policy page already publish
   sales@walryvo.com as the contact — an identity review is exactly the
   place where those lining up matters.

   **The one real risk, and its fix.** Password recovery runs through that
   mailbox, so losing the M365 account loses the Google one. So: set
   moozmooz1902@gmail.com as the **recovery address** on the new Google
   Account, and once Merchant Center exists, add the Gmail as a second
   **admin** user. Two ways back in, neither of them a single mailbox.

   **Order matters.** Create the Google Account first, then Search Console,
   then Merchant Center — all three on the same account. Doing Search
   Console on one account and Merchant Center on another means verifying
   the domain twice.
2. **Legal name: NORYMUS LIMITED. Display name: Walryvo.** These are two
   different fields and the distinction decides whether identity
   verification passes - the payments-profile legal name must match the
   company document exactly, while the shop name shoppers see is Walryvo.
   `web/IDENTITY_VERIFICATION.md` has the whole thing.
   Address 28 Bedford Square, Leigh, WN7 2AA. Customer service
   sales@walryvo.com and 07397 937226 — the same pair that is on the site.
3. **Claim walryvo.com.** Google will show you a verification token. Copy
   the whole line and send it to me — either the
   `<meta name="google-site-verification" content="...">` tag or the DNS
   TXT value. I have Cloudflare DNS edit, so I will add whichever you send
   and tell you when it has propagated; you then press Verify.
4. **Add the two data sources.** Data sources → Add product source →
   **Scheduled fetch** → paste the feed URL → daily. Then the same again
   for the promotions URL under Promotions. Do not pick "upload a file".
5. **Identity verification.** **Read `web/IDENTITY_VERIFICATION.md`
   before starting it** - attempts are limited and the end of them is full
   suspension, the person who starts must finish, and the payments-profile
   name has to be corrected BEFORE submitting rather than after. An
   unverified identity blocks the review of everything else, so do it
   early rather than last.

### Do NOT bother with the Merchant Center API

Offered 28 Oct and declined, for a reason worth keeping: the API exists to
**submit products**, and that is the one part already solved better. The
scheduled fetch pulls the feed daily with no credentials to hold, nothing
to expire and nothing to re-run. Everything still outstanding — creating
the account, verifying identity, claiming the domain — needs a human in a
browser and no API can do it. So there is nothing to hand over.

### A note on preflight's failures, 28 Oct

Three consecutive `--live` runs failed 4, then 2, then 6 checks, a
different set each time, and **every failure was a network error** —
`TimeoutError`, `IncompleteRead`, `RemoteDisconnected`. Each one was then
spot-checked by hand and the site answered correctly: `/`, `/terms` and
`/c/landscapes/british-coast` all HTTP 200, and both "failing" images came
back as real JPEGs of 141 KB and 188 KB. **The site is fine; this
environment's proxy is flaky.** If a future run shows the same shape —
network exceptions rather than content mismatches, and a different set
each run — re-run before believing it, and check a couple by hand.

### Two choices only you can make

**1. Free listings only at launch, or paid Shopping ads as well?**

My recommendation: **free listings only**, and add ads once the account has
been clean for a few weeks. Free listings are the traffic you said you were
after and they cost nothing. Ads put the account under the advertising
policies as well as the Shopping ones, which means a second review surface
on a brand-new domain, and money spent while approval is still pending. The
switch to ads later costs nothing and loses nothing.

**2. Submit the opening 209, or wait for your eye-approval pass?**

My recommendation: **do your pass on the contact sheets first**, then
submit. About 4% of the range has a visible defect (see section B) and the
detector cannot find them. A disapproval for "image quality" on a new
account is cheap to avoid now and expensive to argue later, and the pass is
a morning's work. If you would rather go now, say so and I will submit the
209 as they stand — nothing is broken, it is a question of how good a first
impression the account makes.

Either way **I will not submit anything to Google without you saying so.**

### After submission — the schedule is written down

**`web/SCALE_SCHEDULE.md`** has the dated ladder from 209 designs to
500,000: what must be true before each stage, the earliest date for each,
the commands, and what to watch weekly. Written 28 Oct. In short: 1,000
not before ~18 Nov, 5,000 not before ~16 Dec, 25,000 not before ~20 Jan,
100,000 around March — and every one of those is "not before", never "on".
The gate is **14 clean days, then 30**, not the calendar.

Do not resubmit, do not edit in circles, and do not request reviews you do
not need. Review attempts are limited and running out of them is how
accounts get permanently blocked. New accounts are capped at **150,000
products**; Google raises it on its own for accounts that approach the cap
while performing cleanly. `web/SCALE.md` has the ladder from 209 to
millions, and the order the steps have to happen in.

---

## B3. OnBuy — files are built, TWO THINGS BLOCK THEM

Added 27 Oct. 10,000 listings from `luxvia-art`, built and checked.
`wallart-data/README_ONBUY.md` is the full briefing; this is the short list.

OnBuy is a **catalogue** marketplace, not a listing one. That makes it
structurally different from eBay and produces one blocker that may decide
whether OnBuy is viable at all:

0. **The ticket is written** — `wallart-data/onbuy/EXEMPTION_TICKET.md`.
   Paste and send. It does NOT claim a trademark you do not hold; it says
   so plainly and asks whether a pending application would do, which is the
   question that decides the route. It also asks OnBuy to enable live
   product creation, which a new account needs anyway.
1. **Barcode exemption — raise this ticket first.** A new OnBuy product
   normally needs a real GS1 EAN. 10,000 designs is 10,000 products;
   buying that many GTINs is a four-figure annual licence and the full
   3.77M is not purchasable at all. Inventing them loses the account.
   OnBuy grants an exemption to sellers holding a **UK or EU trademark for
   their brand**, which is why these files carry brand **Walryvo** and not
   `Unbranded` — "Unbranded" can be neither trademarked nor exempted.
   NORYMUS LIMITED does not appear to hold that trademark yet (£170 at the
   IPO, ~4 months). **Ask OnBuy whether an application satisfies them
   before paying for one** — the ticket asks exactly that.
   **The template makes this worse than first thought:** EAN is Required
   and every worked example gives each VARIANT its own barcode, so it is
   90,000 for the opening 10,000 designs, not 10,000. The fallback ladder
   if they refuse is at the end of the ticket file.
2. ~~The category ID.~~ **RESOLVED 27 Oct** from the template the seller
   sent: **9376**, "Home & Garden > Furniture, Furnishings & Decor >
   Artwork > Artwork Prints".

The barcode is now the ONLY thing blocking the file. Every variant row
reads `NEEDS-BARCODE-EXEMPTION` until it is settled and the checker refuses
the upload. Deliberate: rejected loudly beats filed wrongly.

**What to send me — the API keys are the valuable one.** OnBuy's own sell
page lists "Access to API & integrations" on the **Standard £25 plan**, not
just the higher tiers. With the consumer key and secret key I can pull the
real category tree myself, have the create call tell me the real required
fields instead of guessing them, and push listings programmatically instead
of through a spreadsheet a person reviews over about five days. For 10,000
that is an afternoon rather than weeks; for 3.77M it is the difference
between possible and not. They are account credentials — put them in the
environment's settings panel rather than a chat message if you can, and a
new session picks them up.

Failing that: the Product Create Template spreadsheet (Listing → Add
Listing → "Click Here to Find Out More") and the category ID.

Either way, **three weights** — one framed print of each size, A4/A3/A2,
in its packaging. The weights in the file are estimates and they are the
only number in it that was never measured; OnBuy prices delivery off them,
so one that is too low is paid for on every order.

**The fees are a good shape for this catalogue** (checked 27 Oct, and your
seller panel is the authority): **no per-listing fee and no SKU cap on any
plan**, so the £25/month subscription costs the same whether you list
10,000 or all 3.77M. Commission is by category and wall art lands at
**15%**, charged on the delivered total **including postage** — so adding a
delivery charge does not dodge it, and free delivery with an inclusive
price stays the right call. On the reduced OnBuy prices set
27 Oct — **£5 under eBay on every framed size, so £19.99 / £24.99 /
£29.99** — that is £16.99 net on an A4, and breakeven on the subscription is
roughly 1.8 A4 sales a month. **Whether £16.99 still clears your print and
frame cost is the one number only you have**; the files are built either
way and changing the price is one line in `onbuy_plan.json`. The £2-off
unframed prices (£6.99 / £10.99 / £16.99) are recorded in the same file but
unused, because the OnBuy file is framed only.

**Upload the 5-listing test file first.** OnBuy's bulk route is a support
ticket reviewed by a person, reportedly around five days, so a format
mistake in a 10,000-row file costs five days and a rejection on a new
account. Same two-step that caught the variation-picture problem on eBay.

Measured in the 10,000: themes within a point of the whole catalogue
(animals 34% / flowers 28% / landscapes 25%), 4,410 distinct subjects, 14
techniques, all four colourways evenly used, **11 near-duplicates in
10,000 — 0.11%**, against the 89% the wall-art branch blames for 424k eBay
listings not selling. 79 listings were dropped as restricted subjects
(alcohol/tobacco in the title) and all 150 sampled picture URLs came back
as live JPEGs.

**Framed only, nine variants, no unframed option** — the one deliberate
difference from the eBay files. On eBay the unframed row carries no
picture and eBay shows the black frame instead, which you approved. On a
marketplace that shows a picture per variant that becomes a framed
photograph on an unframed product. No unframed photo exists in
`luxvia-art` and none can be made: the stored R2 token cannot write to
that bucket. It costs the £8.99 entry price, and README_ONBUY.md says
exactly what would unlock it.

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

The website, 209 products and 12 categories, the logo and banner, every
policy page, the unframed tier from £8.99, the buy-2-get-1-free offer
priced end to end through Stripe, the Merchant Center feed (2,508 items,
auto-fetched at <https://walryvo.com/feed.xml>), the promotions feed, the
preflight gate at **42 live checks, 0 failing**, the eBay repricing files,
and the D1 database created and seeded. See `CLAUDE.md` for the map.
