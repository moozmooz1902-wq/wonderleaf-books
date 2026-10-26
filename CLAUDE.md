# Where the work lives

**What is waiting on the seller is in `SELLER_TODO.md`.** Read it before
asking them anything: four of the items there have been open for days and
re-asking is how a list gets ignored.

One chat per product line was getting confusing, so this is the map. Read
it first in any new session.

## The decision

**T-shirts are worked on in this branch, `claude/dreamy-hopper-cgp4p4`.**
Everything else about t-shirts - the catalogue, the mockup, the eBay
builder, the RunPod and R2 access - is here. Start with
`tshirt/ACCESS.md`, then `tshirt/RESUME.md`.

**The IMAGE-BASED wall-art pipeline is also on this branch now**, under
`wallart-data/`, built 10-11 Oct 2026. That is the generated-artwork line:
FLUX panels, the code-drawn line families, frames, colourways, the
copyright gate and the RunPod/R2 run. Start with `wallart-data/RESUME.md`
for how to pause and continue, `wallart-samples/PLAN.md` for the costed
plan, and
`research_notes/Wall art catalogue taxonomy harvest/first_real_sample_and_measured_cost.md`
for everything that was measured and everything that failed first.

**The older typography wall-art pipeline stays on
`claude/hopeful-rubin-u14pgu`**, under `wallart/`, with its own stores and
buckets. The two are not duplicated; read that one on that branch. If you
are looking for generated IMAGES, you are in the right place here; if you
are looking for the 2.3M typography catalogue, you are not.

**The OWN-WEBSITE line is `web/`, added 25-26 Oct 2026.** This is the shop
at **walryvo.com**, built to be synced to Google Merchant Center without
the misrepresentation suspension that killed the previous Shopify attempt.
Start with `web/README.md`, then `web/LAUNCH_RUNBOOK.md` (what to do and
why, mapped line by line to Google's actual policy pages) and
`web/SETUP_WALKTHROUGH.md` (the click-by-click for domain, DNS and deploy,
and where the deploy got to).

It is a different product line from eBay and must not be confused with it:

- **240 designs, 12 niches, 2,160 feed items.** Deliberately tiny. A new
  domain carrying millions of near-identical pages is the shape of a feed
  farm; a small coherent shop is the application for permission to submit
  the rest. `web/catalogue/select.py scale_plan()` has the staged ladder.
- **Framed only, one colourway per design.** Both are decisions, not
  oversights, and both have long notes in `select.py` saying why. On eBay
  an unframed variation inherits the framed photo and that is fine; in a
  Merchant Center feed every variant carries its own image, so it would be
  submitting an unframed print with a photograph of a framed one.
- **`web/catalogue/preflight.py` is the gate.** 20 offline checks, 13 more
  against a deployed site, each naming the Google policy or UK law behind
  it. `feed.py` refuses to build while the business identity is incomplete.
  Do not weaken either to make a build pass.
- **One function builds a product** (`product.build_all`) and both the page
  and the feed render from its output. That is the whole anti-mismatch
  design - read the note at the top of `product.py` before changing
  anything there.

**`ebay_reprice/`** is the repricing tool for live eBay listings, used
26 Oct to move 502,443 listings to the go-to prices. Its README records
four things in the export that break a naive find-and-replace.

## Walryvo, the business, in one place

Everything below is also in `web/business.config.json`, which is the single
source the site, the feed and the policy pages all read.

    brand        Walryvo
    domain       walryvo.com   (walryvo.co.uk is held too and must 301 to it)
    legal        NORYMUS LIMITED, company 17020866, England and Wales
    registered   28 Bedford Square, Leigh, WN7 2AA
    VAT          GB513541030
    contact      sales@walryvo.com (Microsoft 365), 07397 937226
    prices       framed A4/A3/A2 24.99/29.99/34.99, free UK delivery, VAT inc
    returns      30 days from delivery
    D1 database  wallart, e1e39887-2c7d-4066-9dc1-15f598af5b6e, already seeded

**Known and NOT fixed, flagged to the seller 25 Oct:** reviewing 48 of the
240 designs by eye found about 4% clear defects - one titled "teasels"
whose picture is a street full of people, one carrying a fake cursive
signature on a page that states the work is not signed, two with possible
small figures. `declutter.py`'s detector is tuned for the bottom 22% of a
panel and does NOT discriminate run full-frame (0.0128 on the known case
against 0.0191 on a clean one), so it is deliberately not shipped as a
check. `web/catalogue/sheet.py` builds numbered contact sheets so the range
can be approved by eye; `--drop` removes what is rejected.

## Why it is split this way

Different product lines, different buckets, different eBay categories
(t-shirts 15687, wall art 360). Merging them would mean one branch where
most of the files are irrelevant to whatever is being worked on.

The cost is that a session on one branch cannot see the other's chat. That
does not matter, because neither can any session: **the repo is the memory,
not the conversation.** Anything worth carrying across gets committed.
`tshirt/ACCESS.md` has a section recording what was carried over from the
wall-art branch, including corrections it forced.

## Shared facts, true for both lines

- eBay business policies on every account are named `1` - shipping, returns
  and payment. Not `default`.
- Quantity 1, location United Kingdom.
- One Cloudflare R2 bucket per eBay account. T-shirts for the M12K account
  go to `tshirt-m12k`. **There is no wall-art bucket yet**: the stored R2
  token can write to `tshirt-m12k` but cannot list or create buckets
  (probed 11 Oct), so generated panels currently live under the prefix
  `tshirt-m12k/wallart/v1/`. A copy within R2 is server side and free, so
  moving them once a bucket exists costs nothing.
- FLUX.1 **schnell** is the image model, for its Apache-2.0 licence.
  FLUX.1-dev is non-commercial and must never be used on goods that are
  sold.
- Near-duplicate listings are treated as the main commercial risk. The
  wall-art branch blames 89% near-duplication for 424k listings not
  selling. Any catalogue generated here gets measured against that before
  it is uploaded - `wallart-data/pipeline.py audit()` is that measurement.
  Measure it on a gradient hash of the ARTWORK, excluding a design's own
  colourways; hashing the framed mockup or using an average hash both give
  answers that are badly wrong, in opposite directions.
- No human figures, and animal eyes must be right. The seller's rule,
  11 Oct. Enforced in `gen/prompts.py`, not left to chance.
- Nothing claims to be hand-painted, original or artist-signed, and the
  fake signatures FLUX scrawls on the artwork are cropped off. Both are
  legal controls, not just quality ones - see `wallart-data/ip_check.py`.

## Access

RunPod and Cloudflare R2 are both connected and verified from the
environment "poster and t shirt data research". No terminal work is needed
from the seller. See `tshirt/ACCESS.md` for how each one is wired, what
does not work and why, so the failed routes are not retried.

**For the website there is NO Cloudflare API token in this environment** -
`tshirt/ACCESS.md` says so explicitly, and the RunPod template carries R2
*storage* keys (R2_ACCESS_KEY_ID etc), which sign S3 requests to buckets
and cannot deploy a Worker, create a D1 database or edit DNS. A deploy
needs `CLOUDFLARE_API_TOKEN` added to the environment's settings panel by
the seller, and a NEW session to pick it up. Checked 26 Oct: that token
authenticates and carries a working Account->D1->Edit, but
`wrangler deploy` is refused by the permission classifier, and adding an
allow-rule for it is refused as self-modification. So the final deploy is
the seller's to run. `web/SETUP_WALKTHROUGH.md` Part 4 has the three
commands.
