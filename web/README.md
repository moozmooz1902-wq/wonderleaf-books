# web/ — the wall-art shop

A storefront for the generated wall art, built to be synced to Google
Merchant Center **without** a misrepresentation suspension. That constraint
shaped nearly every decision here; where a choice looks odd, the comment at
the top of the file says what it is defending against.

**Start with [`LAUNCH_RUNBOOK.md`](LAUNCH_RUNBOOK.md).** It is ordered and
it is the only document you need to follow.

## What is where

```
web/
  business.config.json   WHO THE BUSINESS IS. One source of truth for the
                         footer, the policy pages, the feed and Stripe.
                         Fields still empty here BLOCK the build, by design.
  LAUNCH_RUNBOOK.md      Step by step, in order. Read this.
  catalogue/
    taxonomy.py          The 53 browsable niches, built from the subject
                         modules' own groupings. `python3 taxonomy.py` to see
                         the tree; it proves all 5,204 subjects map.
    select.py            Picks the best N designs. Demand-weighted,
                         duplicate-distanced, quota'd. `-n 5000` to grow.
    product.py           ONE function builds a product. Page and feed are
                         both rendered from its output - read the note at the
                         top, it is the core of the whole design.
    build_db.py          selection -> catalogue.json + seed.sql + site data.
    feed.py              The Merchant Center feed. Refuses to build while the
                         business identity is incomplete.
    preflight.py         THE GATE. Run before every submission.
  site/                  Astro on Cloudflare Workers + D1.
  feed/                  Generated feed output.
```

## The pipeline

```bash
cd catalogue
python3 select.py -n 1000     # choose the range
python3 build_db.py           # build catalogue + db + site data
python3 preflight.py          # must be all green
python3 feed.py --tsv         # only builds if identity is complete
```

Then `cd site && npm run deploy`, then `python3 preflight.py --live`.

## Current state, 25 Oct 2026

Built and verified:

- **1,000 products, 9,000 feed variants.** 53 niches, every one holding
  12–28 designs so no category page is a dead end.
- Technique mix 22% charcoal / 15% pencil sketch — the two measured winners
  on the seller's own eBay watchers (z=+5.9 and +4.4 against a 1.05% base
  rate), at 2.7x their share of the grid — with the other twelve techniques
  present in testable volume rather than crowded out.
- Closest pair in the range **48 of 256 hash bits apart**; the eBay
  duplicate audit calls 24 or fewer "near".
- Astro build clean. Every route returns 200. Variant URLs verified to
  serve their own price server-side in both the visible HTML and the
  JSON-LD (framed `?size=a4` → £14.99, `a3` → £19.99, `a2` → £24.99;
  unframed £6.99 / £8.99 / £9.99).
- Feed passes 20 of Google's own spec rules locally, 0 problems on 9,000
  items.

Blocked on the seller for: brand name, domain, VAT number, support email
on the domain, phone number. `preflight.py` lists them and refuses to
produce a submittable feed until they are set — see Step 2 of the runbook.

## Two things that are decisions, not oversights

**Framed only.** The eBay listings sell an unframed option whose variation
carries no picture, so eBay falls back to the framed main photo. That is
fine on eBay and cannot carry over: in a Merchant Center feed every variant
is its own product with its own image, so an unframed print would be
submitted with a photograph of a framed one — an image/offer mismatch, and
the first line of the misrepresentation policy. There is no unframed
photograph in the buckets to use instead, and making one needs the R2 write
key, which lives on the RunPod template and not here. Add unframed the day
real unframed photographs exist, not before.

**One colourway per design.** Each design exists in four recolours. Showing
all four adjacent is the near-duplicate problem in its purest form, so the
opening range takes colourway 0 only — the generated panel, not a recolour.
Colourways come back at the 100,000 stage as an option inside the existing
product, which is honest and useful rather than four near-identical
listings.

## What this does not do yet

### The range has not been approved by eye, and it needs to be

I reviewed 48 of the 1,000 as contact sheets (`sheet.py --sample 96`). In
those 48:

| Found | Example | Why it matters |
|---|---|---|
| **Wrong subject entirely, with people in it** | `#22` is titled *teasels* — a plant — and the picture is a wet street full of walking figures | The product photograph does not show the product. That is the misrepresentation policy's first line, and it also breaks the no-human-figures rule |
| **A fake signature** | `#43`, a mill above a town, carries a cursive scrawl on the ground line | Every product page states the work is "not signed or numbered". A signature in the image contradicts the page |
| **Two possible small figures** | `#11` Bardsey Island, `#71` Coniston Water | The for-scale kind. Needs a closer look |

So roughly **4% clear defects and another ~4% borderline**, which on 1,000
designs is perhaps 40 to 80 to pull. That is a morning's work with the
contact sheets and it must happen before the feed is submitted:

```bash
python3 sheet.py                    # sheets of the whole range
python3 sheet.py --drop 22,43,...   # remove what you rejected
python3 build_db.py && python3 preflight.py
```

**Why the existing tooling did not catch these.** `render_worker.py` crops
a fixed bottom 11% of each panel, which removes signatures FLUX puts at the
very bottom edge. The one in `#43` sits on the drawn ground line about
two-thirds down — far above that band. `declutter.py` has a proper
morphological detector but is tuned for the bottom 22%; I tried running it
full-frame and it does **not** discriminate (the known-signature panel
scored 0.0128 against 0.0191 for a clean one, i.e. worse than chance). I
have not shipped it as a check, because a check that does not work is worse
than none. Retuning it is a real piece of work and a separate job from this
one.

### Other gaps

- **The human-figure sweep proper has not been run.** About 17% of all
  panels carry a small distant figure. `select.py` holds back the
  compositions where one is likeliest, but that is a proxy, not a detector.
  `render/people_sweep.py` is the real thing and needs a GPU pod (~$1–2).
- **No unframed photographs**, so the shop is framed only. See above.
- **`preflight.py --live` has never run against a deployed site**, because
  there is no domain yet. Everything verified so far is local.
