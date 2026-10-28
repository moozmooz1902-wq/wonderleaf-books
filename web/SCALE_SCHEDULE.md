# The scale-up schedule — dates, gates and what to watch

Written 28 Oct 2026, the day the feed first synced. `select.py scale_plan()`
holds the sizes; this holds the **timing**, the **conditions** and the
**evidence** that each stage is safe to take.

**Every date here is "not before", never "on".** A date that arrives while
a condition is unmet means wait, not go. The conditions are the plan; the
dates only stop us waiting forever out of caution.

---

## Why slow is the strategy, not the caution

The previous Shopify shop was suspended for misrepresentation. A brand-new
domain that suddenly carries hundreds of thousands of near-identical pages
is the shape Google's reviewers are trained to find, and the account has
**no history to weigh against it**. Every clean week is an asset: a new
Merchant Center account is capped at 150,000 products and Google raises
that cap on its own, for accounts that approach it while performing
cleanly. There is no form to fill in. Clean time is the only currency.

So the catalogue is not the bottleneck and never will be — 3.77M designs
exist already. **Account standing is the bottleneck**, and it is bought
with weeks.

---

## Stage 0 — now. 209 designs, 2,508 items. Live.

Not a waiting room. Three things have to finish here and none of them is
about products.

| | Who | Why it blocks everything |
|---|---|---|
| **Identity verification** in Merchant Center | seller | An unverified identity blocks the review of everything else. Nothing below starts until this clears. |
| **SIC code 96090 → 47910** at Companies House | seller | Google compares the public register against the site. |
| **Stripe account verification** | seller | A shop that cannot complete a sale is its own policy problem. |

And one that is about products:

- **The eye pass on the 209.** `python3 catalogue/sheet.py`, then
  `--drop` what is rejected. About 4% carry a visible defect. At 209 this
  is a morning. It never gets cheaper than this.

**Leave the 192 "Image not processed" alone.** The cause was found and
fixed on 28 Oct (`GMC_IMAGES_28OCT.md`); Google re-crawls failed images by
itself over several days. Re-check on **31 Oct**. Do not force a refetch by
changing image URLs — a product's image URL is part of its identity.

---

## Stage 1 — 1,000 designs. Not before ~18 Nov 2026.

That is three weeks out, and only because every condition below needs real
elapsed time.

**All of these must be true:**

- Identity verification **passed**, not pending.
- **Free listings are serving** — not "approved", actually appearing. The
  evidence is impressions in Merchant Center → Performance. Approved and
  serving are different states and only the second one proves the account
  works.
- **Zero policy issues for 14 consecutive days.** Not "none today".
- The 192 image disapprovals are at zero.
- The eye pass is done and rejects are dropped.

**How to take it:**

```bash
cd web
python3 catalogue/select.py -n 1000 --niches all
python3 catalogue/build_db.py
python3 catalogue/feed.py
python3 catalogue/preflight.py          # must be 0 failures
# deploy, then:
python3 catalogue/preflight.py --live   # must be 0 failures
```

Then do nothing else for two weeks. Changing the shop and growing it in
the same week makes a disapproval impossible to attribute.

---

## Stage 2 — 5,000 designs. Not before ~16 Dec 2026.

**Conditions:** another **14 clean days** after stage 1 is fully crawled,
Search Console showing category pages indexed, and no new disapproval
category appearing after the jump.

**The thing that changes here:** 1,000 designs can be reviewed by eye.
5,000 cannot. So the quality gate changes shape:

- Review a **random 200** on contact sheets, not all of them.
- If **2% or more** show a defect, do not ship — fix the selection first.
  At 5,000 designs a 4% rate is 200 bad products, and they will be live
  and indexed before anyone notices.
- Run `wallart-data/pipeline.py audit()` on the selection and keep
  near-duplication **under 1%**. The eBay line blames 89% near-duplication
  for 424k listings not selling; that number is the whole reason this
  catalogue is selected rather than dumped.

---

## Stage 3 — 25,000 designs. Not before ~20 Jan 2027.

**Conditions:** **30 clean days** after stage 2, Search is indexing
category pages (Search Console → Pages → Indexed, trending up), and free
listings are producing clicks rather than only impressions.

This is the first stage where the shop stops being reviewable by a person
at all. From here the gates are statistical: sample 200, defect rate under
2%, near-duplication under 1%, every preflight check green.

Watch the **sitemap** here. `allSlugs()` is unpaged and the standard caps a
file at 50,000 URLs — 25,000 designs is about 25,000 product URLs plus
category pages, so this is the stage where it needs splitting. See
`SCALE.md`.

---

## Stage 4 — 100,000 designs. Not before ~March 2027.

**Conditions:** 30 clean days after stage 3, and the account has never had
a policy issue it did not clear within a week.

**Colourways arrive here, as a Colourway variant inside existing products
— never as new products.** Four colourways as separate products is the
exact near-duplicate shape that does not sell and does attract review.

This lands close to the **150,000 product cap**. Do not ask for a raise;
Google lifts it on its own for accounts performing cleanly near the cap.
Asking is not a route and drawing attention is a cost.

---

## Stage 5 — 500,000+. No date, and one precondition.

Only with **unframed photographs actually rendered**. Today the unframed
tier is served from `/unframed/` stills; at this scale every variant
carrying a correct image stops being a detail. Until then 100,000-150,000
is the ceiling and it is a fine ceiling — it is 60% of the entire
Merchant Center allowance for a new account.

---

## What to look at, and how often

**Weekly, five minutes** — Merchant Center → Products:

| Number | Healthy | Act if |
|---|---|---|
| Not approved | 0 | anything appears that is not an image crawl in progress |
| Under review | falling | stuck above zero for more than a week |
| Free listings impressions | rising | flat for two weeks after verification passes |

**Monthly** — Search Console: are category pages indexed, and growing?

**Before every stage** — `preflight.py --live` must be **0 failures**. It
is 46 checks and each one names the Google policy or UK law behind it. Do
not weaken a check to make a stage pass; the check is the cheap version of
the suspension.

---

## The rule that matters more than the dates

**One change at a time, and a clean fortnight between changes.**

Growing the catalogue, changing prices, changing the theme and turning on
ads are four separate experiments. Done in the same week, a disapproval
cannot be attributed to any of them, and the only remaining move is to
undo everything — which costs more weeks than doing them one at a time
ever would have.

If a stage goes wrong: **stop, do not resubmit in circles.** Review
attempts are limited and exhausting them is how accounts get permanently
blocked.

---

## One thing worth doing early: automate the deploy

Every stage above ends in "deploy", which today means the seller at a
terminal. Connecting the GitHub repo to **Cloudflare Workers Builds**
(Workers & Pages → wallart-shop → Settings → Builds, root directory
`web/site`) makes every push deploy itself. That turns each stage from a
scheduled chore into a push, and removes the most likely reason a stage
slips: nobody was free to run it.
