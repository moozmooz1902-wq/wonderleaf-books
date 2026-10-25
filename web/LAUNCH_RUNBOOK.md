# Launching the shop without a misrepresentation suspension

Written 25 October 2026. Everything here is ordered. Do it in this order,
because several steps only work if an earlier one is already true.

The emphasis throughout is the thing that has gone wrong before:
**misrepresentation**. Google tells you the policy and not the sentence you
broke, so the only defence is to satisfy every condition the policy covers
and to be able to prove it. That is what `catalogue/preflight.py` is for.

---

## Step 0 — The one thing to check before anything else

**Do NOT create a new Merchant Center account.** Find out what state your
existing one is in first, at <https://merchants.google.com>.

This matters more than any other decision here. Google classes "creating a
new account to get around a suspension" as *circumventing systems*, under
Abuse of the Network, and treats it as egregious — the enforcement is
link-based, so a new account tied to the same company, bank account, phone
number or device can be actioned along with the old one. Starting fresh to
escape a suspension is the one move that can turn a recoverable problem
into an unrecoverable one.

So:

| What you find | What to do |
|---|---|
| The old account is **suspended** | Keep it. Fix the cause (this whole runbook), change its website to the new domain, then request a review. That is remediation, not evasion. |
| The old account is **fine / you closed it yourself** | You may open a fresh account cleanly. |
| You can't get in at all | Recover access before anything else. Do not route around it. |

**A new domain is a different matter, and yes — get one.** Enforcement
attaches to the website as well as the account, so the Shopify domain
carries the history of the site that was actioned. A new domain under the
same honest identity is a genuinely new shop, not a disguise. What must
*not* change is who you say you are: NORYMUS LIMITED, company 17020866,
everywhere, on both the site and the account. Hiding the connection is
what gets accounts banned; the connection itself is fine.

---

## Step 1 — Fix your SIC code (free, and nobody tells you about it)

Your Companies House record says SIC **96090 — "Other service activities
not elsewhere classified"**. You are selling framed art prints online.
Those do not match, and a reviewer checking the company behind the shop can
see it.

Change it to one of:

- **47910** — Retail sale via mail order houses or via the Internet ← the right one
- 47789 — Other retail sale of new goods in specialised stores
- 18129 — Printing (other), if you want to reflect the printing side too

You update SIC codes when filing a confirmation statement, and you can file
one early for a small fee. Yours is not due until February 2027, so file
early. It is the cheapest credibility you will ever buy.

While you are there: the company was incorporated 9 February 2026, so it is
about eight months old. That is young but entirely legitimate. It is a
reason to get everything else exactly right, not a problem in itself.

---

## Step 2 — Send me five things

The build is finished and **blocked** on these. `preflight.py` refuses to
produce a feed until they are filled in, deliberately: a feed with blanks in
the business identity misrepresents who is selling.

1. **Brand / trading name** — the name on the site and in Merchant Center.
   Must match across the domain, the site, the account and Stripe.

   > *"We make it ourselves so there's no brand"* — that is true about the
   > world and wrong about the feed. Google requires `brand` on new
   > products and **explicitly permits your own name when you manufacture
   > the goods**, which you do. What gets you disapproved is putting
   > `Generic`, `Unbranded` or `N/A` in that field. So your trading name
   > *is* the brand. Preflight rejects all three of those words, and also
   > checks the brand resembles the domain, because verification
   > cross-checks the business name against the site.
2. **The new domain** — see Step 3 for how to choose.
3. **VAT number** — `GB` plus 9 digits. You said you are registered.
4. **A support email on that domain** — `hello@yourdomain.co.uk`. Not
   Gmail. A registered company selling from a free mailbox is a named
   trust-signal failure in Merchant Center reviews, and preflight rejects
   it.
5. **A working UK phone number** — answered, or with voicemail. A dead
   number counts as false contact information.

Already done and verified for you: legal name, company number (checked
against the public register), registered office, delivery terms, returns
window, and the whole catalogue.

**Decision I made for you, change it if you disagree:** UK delivery is set
to **free**. On a £24.99–£34.99 framed print it converts better than a
£4.95 line, it makes the feed's shipping attribute trivially correct, and
it removes the undisclosed-delivery-cost risk completely. One number in
`business.config.json` changes it everywhere.

---

## Step 2b — The product category (already set, here is the proof)

Every item is submitted as:

```
google_product_category = 500044
  Home & Garden > Decor > Artwork > Posters, Prints & Visual Artwork
```

Taken from Google's own published taxonomy file, not from memory — I
downloaded `taxonomy-with-ids.en-GB.txt` and grepped it. Worth stating
because the neighbouring id is a trap: **500045 is Decorative Tapestries**,
and 597 is Picture Frames. A framed print is not a picture frame; you are
selling the artwork, and the frame is how it is supplied. Getting this
wrong puts your products in the wrong comparison set and can look like
miscategorisation.

Alongside it each product carries a `product_type` of your own, e.g.
`Wall Art > Landscapes & Places > British Coast > Charcoal Drawings`,
which is what Google uses for reporting and bidding.

---

## Step 3 — Domain

Buy it anywhere (Cloudflare Registrar sells at cost, about £8–11/yr, and
keeps everything in one account).

- `.co.uk` reads correctly for a UK company. `.com` is fine too.
- Short, pronounceable, not a hyphen salad. Not a near-copy of a known
  brand — that is a different policy violation.
- **Never** a free subdomain, and never the old Shopify domain.
- Buy it and point DNS at Cloudflare **before** you touch Merchant Center.
  A domain registered yesterday with no site on it is a weak signal; the
  same domain with a working shop on it is not.

Then set it in two places: `brand`/`domain` in
`web/business.config.json`, and `SITE_URL` in `web/site/wrangler.toml`
(it still says `REPLACE_WITH_YOUR_DOMAIN`, and preflight will keep failing
until it does not).

---

## Step 4 — Put the site up

In `web/site`:

```bash
npm install

# 1. The catalogue database
npx wrangler d1 create wallart
#    -> paste the database_id it prints into wrangler.toml

# 2. Load the 1,000 products / 9,000 variants
npm run db:seed:remote

# 3. Deploy
npm run deploy
```

Then in the Cloudflare dashboard: **Workers & Pages → wallart-shop →
Settings → Domains** and add your domain.

Notes:

- The four R2 buckets are already bound in `wrangler.toml`. Images are
  served from `/img/<bucket>/<key>` on your own domain — **not** from the
  `pub-*.r2.dev` URLs the eBay files use. Those are rate limited (a
  measured run got Cloudflare error 1015 on 7,142 of 12,834 requests), and
  an image that returns 1015 to Google's crawler is logged as unavailable,
  which disapproves the product. This was not optional.
- If deploy complains `Invalid binding SESSION`, run
  `npx wrangler kv namespace create SESSION` and add the printed binding to
  `wrangler.toml`. The shop does not use sessions; the adapter just expects
  the binding to exist.

---

## Step 5 — Stripe

**Use Stripe.** Reasons, in order of how much they matter here:

1. Stripe Checkout is hosted, so card details never touch your server. You
   stay in PCI scope SAQ-A, the lightest there is.
2. Apple Pay, Google Pay and Link come free with it. More ways to pay is
   more conversion on a £25 impulse purchase.
3. Its own business verification uses the same Companies House and bank
   details as Merchant Center, so getting one right gets the other right.
4. UK pricing is roughly 1.5% + 20p on UK cards, 2.5% + 20p on
   international, no monthly fee. Check the current rate when you sign up.

Set up:

```bash
npx wrangler secret put STRIPE_SECRET_KEY
npx wrangler secret put STRIPE_WEBHOOK_SECRET
```

In the Stripe dashboard:

1. Add a webhook to `https://yourdomain/api/stripe-webhook` for the event
   `checkout.session.completed`.
2. **Settings → Customer emails → turn on "Successful payments".** The
   order-confirmed page tells the buyer an email is coming. If Stripe is not
   sending one, the site is stating something untrue. Once it is on, set
   `order_confirmation_email: true` in `business.config.json` — preflight
   fails until you do.
3. **Settings → Public details**: business name, support email, phone and
   address, all matching Companies House and Merchant Center.
4. **Statement descriptor** = your brand. A card statement showing a name
   the customer does not recognise produces chargebacks, and chargebacks
   feed back into Google's view of you.

The checkout page itself already shows the terms, returns and privacy
links and requires acceptance — Google's checkout rules say customers must
be able to reach those "throughout checkout", and omitting them is
"treated as misrepresentation". That is set in `api/checkout.ts`; do not
remove it.

**The business name, address and company number in Stripe must match
Companies House and Merchant Center exactly.** Verification cross-checks
them and a mismatched director name or address country is the commonest
failure. Also set the Stripe statement descriptor to your brand — a card
statement showing an unrecognised name generates chargebacks, and
chargebacks feed back into Google's view of you.

Consider adding PayPal later. A lot of UK buyers over 45 will not use a
card on an unfamiliar shop. It is not needed for launch.

---

## Step 5b — Approve the pictures by eye (do not skip this)

I reviewed 48 of the 1,000 designs and found, in those 48 alone: one
titled *teasels* whose picture is a street full of walking people, one
carrying a fake cursive signature on a product page that says "not signed",
and two with possible small figures. That is about 4% clear defects, so
expect **40 to 80 across the full 1,000**.

None of it is catchable by code today — see the README for why the existing
signature detector does not discriminate when run full-frame. It is,
however, about twenty minutes with contact sheets:

```bash
cd web/catalogue
python3 sheet.py                      # numbered sheets of the whole range
python3 sheet.py --drop 22,43,71      # whatever you rejected
python3 build_db.py                   # rebuild without them
```

Look for: people of any size, animal eyes that are wrong, anything that
looks like a signature, and any picture that is not what its label says.
The last one matters most — a product photograph that does not show the
product is the misrepresentation policy's first line.

---

## Step 6 — Run the gate

```bash
cd web/catalogue
python3 preflight.py          # offline checks
```

Fix everything until it says all pass. Then deploy, then:

```bash
python3 preflight.py --live -n 60
```

The `--live` run is the one that matters. It fetches your real site and
checks, among other things, that **every sampled variant URL quotes the
same price the feed does**, in the visible HTML *and* in the JSON-LD. That
single check is the most likely cause of what happened to you before, and
it is the reason the product pages are server-rendered rather than static.

Only once it is all green:

```bash
python3 feed.py --tsv
```

It refuses to build otherwise.

---

## Step 7 — Google, in this order

Order matters. Submitting a feed before the site is verified and complete
spends a review you cannot get back.

1. **Search Console** — add the domain, verify by DNS TXT record. Submit
   `https://yourdomain/sitemap.xml`. Do this first: it proves ownership and
   starts indexing while you do the rest.
2. **Let it sit for a few days.** A shop that has existed for an hour
   reviews worse than one that has existed for a week. Use the time to
   place a real test order through the live checkout and actually fulfil
   it — see Step 8.
3. **Merchant Center** — the existing account per Step 0, or a new one if
   Step 0 said that is clean. Set:
   - Business name = your brand, exactly as on the site
   - Business address = 28 Bedford Square, Leigh, WN7 2AA
   - Customer service email + phone = the same ones on the site
   - Website = the new domain, claimed and verified (it will use the
     Search Console verification already in place)
4. **Business identity verification.** Expect to upload photo ID, proof of
   address and company documents. Have them ready and make sure every name
   and address matches. Reports suggest this is now standard for UK
   merchants and that an unverified identity blocks the substantive review
   of anything else, so do not skip or delay it.
5. **Shipping and returns settings in Merchant Center** must say the same
   thing as `/delivery` and `/returns`. Free UK delivery, dispatch within
   3 working days, 30-day returns from delivery. A difference between the
   account settings and the site is a misrepresentation finding by itself.
6. **Submit the feed.** `web/feed/feed.xml`, as a scheduled fetch from a
   URL you host or a manual upload. Opt in to **free listings** (that is
   the free traffic you are after) before paid Shopping ads.
7. **Wait.** New accounts are reviewed, typically a few days. Do not
   resubmit, do not edit in circles, do not request reviews you do not
   need — review attempts are limited and running out of them is how
   accounts become permanently blocked.

---

## Step 8 — Place a real order yourself, before Google does

Buy one print from the live site with a real card. Then fulfil it properly:
print it, frame it, post it, and keep the proof.

Do this because Google may test the checkout, and because every promise on
the site is now a promise you have personally verified you can keep.
"Denying return and refund for a product despite having a clear refund or
return policy" is an egregious violation with no warning stage. The first
time you find out whether your 3-day dispatch is real should not be when a
customer is waiting.

Then return it to yourself, through your own returns process, and confirm
the refund lands. Now the returns policy is true too.

---

## Step 9 — Scaling up, and not before

The catalogue tool can produce any number of products. The staged plan is
in `catalogue/select.py`:

| Stage | Designs | Niches | When |
|---|---|---|---|
| **240** | now | 12 | Launch. 2,160 feed items. Change nothing else until the account is healthy. |
| 600 | | 20 | Only after free listings are serving and there have been **zero** policy issues for 14 straight days. Adds Still Life and Architecture. |
| 2,500 | | 40 | After another 30 clean days, and once Search is actually indexing category pages. |
| 10,000 | | 53 | The whole taxonomy. |
| 40,000 | | 53 | Add the other three colourways here — as a Colourway option inside existing products, not as new products. |
| 100,000+ | | 53 | Only on a boringly healthy account, and only with real unframed photographs if you want unframed. |

Growing is one command, and the menus grow with it — they are built from
whatever is in stock, so a stage that adds Still Life adds its nav link too:

```bash
cd web/catalogue
python3 select.py -n 600 --niches all --per-min 14 --per-max 40
python3 build_db.py
python3 preflight.py && python3 feed.py --tsv
cd ../site && npm run db:seed:remote && npm run deploy
```

**Every stage needs the eye-check in Step 5b again** on the designs that are
new. The defect rate does not fall just because the account is healthy.

**Why not go straight to millions,** given that is the whole point of the
data: a brand-new domain carrying millions of near-identical pages is the
exact shape of a feed farm, and Google will neither index nor trust it. The
1,000 are not a limitation, they are the application for permission to
submit the rest. Get the account healthy and the ceiling comes off.

---

## The misrepresentation checklist, mapped to the policy

Every line is something Google's policy names, and where in this build it
is handled.

| Policy line | How it is handled |
|---|---|
| "Present a false identity, business name, or contact information" | Legal name, company number, VAT number and registered office in the footer of **every** page, plus a dedicated contact page. Verified against Companies House. |
| "Using a false or virtual address as headquarters" | Real registered office. Preflight rejects an address with fewer than two lines. |
| "Hiding where products ship from" | `/delivery` states printed, framed and posted in the United Kingdom. |
| "Hiding processing delays behind a stated delivery time" | Dispatch time and transit time are shown **separately**, and both go in the feed as handling/transit times. |
| "Not showing the total price, including taxes, fees" | All prices VAT-inclusive, free delivery, total shown before payment. The server looks up prices; the browser cannot propose one. |
| Price mismatch between feed and landing page | Pages are server-rendered from the same build as the feed; `preflight --live` samples variant URLs and compares HTML and JSON-LD against the feed. |
| "Denying return and refund despite having a clear policy" | 30 days from delivery, no reason needed; orders recorded by the Stripe webhook so they can be honoured. |
| "Offers that represent your products in a way that isn't accurate" | Framed only, because the only photographs that exist are of framed prints. Every page states the artwork is digitally created and not a painting, original or signed work. |
| "Promising products or promotions users can't actually get" | Nothing is out of stock because everything is made to order. UK-only shipping is stated and enforced in checkout. |
| Unreliable claims / invented social proof | No reviews, no ratings, no bestseller badges, no countdown timers. Preflight fails the build if any appear. Fake reviews are also a criminal matter in the UK under the DMCC Act 2024. |
| Policy pages missing or needing JavaScript | Delivery, returns, terms, privacy, contact and about are server-rendered plain HTML, linked from every page, and `--live` asserts their content. |
| Images unavailable to the crawler | Served from your own domain out of R2 with a long cache, not from the rate-limited r2.dev hosts. `robots.txt` explicitly allows Googlebot-Image. |
| Placeholder / template copy | Preflight scans the site source, `wrangler.toml` and the config for 15 placeholder patterns and fails on any hit. |
| Copyright | No named IP in the subject lists; the generator's copyright gate already blocks it; nothing claims to be hand-made or signed. |
| "Customers must be able to find refund and return policies, terms and conditions, and a way to contact you **throughout checkout**" | Stripe Checkout is configured with required terms acceptance linking to `/terms`, `/returns` and `/privacy`, plus a line carrying the dispatch time and support email. |
| Return policy consistent "in the footer, returns page and web banner" | All three, generated from one config: the banner at the top of every page, the returns page, and the footer states the terms in full rather than only linking them. |
| "Repair or redirect broken URLs, such as those returning 404 or 500" | A missing page renders the shop's own 404 with full navigation, verified returning status 404. |
| "Ensure all links across the website are working and point to relevant content" | Menus are generated from the products, so a category the range does not cover is not linked at all. `preflight --live` crawls every internal link; 70 checked locally, 0 broken. |
| Site must be "fully-functional", no pages that look unfinished | Preflight fails if any niche in the navigation holds fewer than 6 designs. |
| Restricted products (alcohol, tobacco) | A print of a negroni is not a negroni, but the screening is automated and reads the title. 6,401 panels excluded by rule in `select.py`, and preflight re-checks the built feed. |
| Contact details must match Merchant Center | Organization markup with the legal name, company number, VAT number, address, email and phone is on **every** page, generated from the same config the footer uses. |
| Guest checkout; business fields optional | Stripe Checkout, guest by default. We collect no company name. |
| Price must not increase between listing and checkout | The browser sends only variant ids and quantities; the server looks up every price. A posted price is impossible. |
| "Show the local currency ... consistently from product page through checkout" | GBP throughout, VAT inclusive, set once in config. |

---

## If it gets suspended anyway

1. **Read the notice.** It names a policy. Find the matching row above.
2. **Do not request a review until the cause is fixed.** Attempts are
   limited; wasting them is how accounts get permanently blocked.
3. **Do not delete the account and start again.** That is the
   circumvention trap from Step 0.
4. Run `python3 preflight.py --live -n 200` — a bigger sample finds
   mismatches a 30-product sample missed.
5. Check the obvious human things the code cannot: is the phone answered,
   is the mailbox monitored, does the Stripe name match, has anything on
   the site started claiming something it should not.
6. Fix, verify green, then appeal once, explaining specifically what was
   wrong and what you changed.
