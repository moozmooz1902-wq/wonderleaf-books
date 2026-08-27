# 00 — Diagnosis: why 100,000 listings produced nothing

## The arithmetic

Listing count is a **multiplier**, not a substitute.

```
revenue  =  listings  ×  E[sales per listing]
```

If `E[sales per listing] ≈ 0`, then `100,000 × 0 = 0`. Scaling a process with
zero expected value per unit only scales the cost and the spam signature.

This is the whole problem in one line. Everything below is a decomposition of
*why* `E[sales per listing]` is currently near zero, and what has to change so
that a batch of **500** concepts outperforms a batch of **100,000** rows.

## Why scraped competitor data "works" and our generated data doesn't

When you list from another site's data, you are not borrowing their *art* — you
are borrowing their **demand evidence**. A listing that already exists and ranks
on Etsy/Amazon is a listing that survived a search race: someone typed a phrase,
the listing matched, it converted, the platform kept ranking it. That row carries
information about a real buyer intent.

Our generated rows carry **none of that**. They are invented from the model's
imagination, so the phrase they'd rank for is either (a) nothing anyone types, or
(b) something 400,000 other listings already own.

> **The fix is not better prose. The fix is to put the demand anchor *into* the
> generation step, and refuse to generate anything that doesn't have one.**

## The five failure modes

### 1. No demand anchor
Designs are generated from a theme ("cats", "space", "motivation") instead of
from a **search phrase a buyer actually types**. A poster that no phrase reaches
is invisible regardless of quality. Marketplaces are search engines with a
picture attached.

**Rule:** every concept must be born from a `demand.query` string with an
evidence field. No query, no concept.

### 2. Generic-mean output ("AI slop")
An unconstrained generator returns the *most probable* output — the statistical
mean of its training data. "Cute cat poster" returns the consensus cute cat
poster. Nothing distinctive means no click in a thumbnail grid, and buyers
increasingly read undifferentiated output as low-effort and untrustworthy.

**Rule:** every concept must carry a **visual DNA block** — named style, palette
hexes, composition, typography, texture, and explicit *avoid* list. Constraint is
what pulls output off the mean. See `data/poster_style_dna.json` and
`data/tshirt_layout_archetypes.json`.

### 3. Metadata written as keyword soup
Current output reads like: title stuffed with every keyword, tags that repeat the
title, description that restates the title. Every major platform now scores this
*down*:

- Redbubble rewards **multi-word phrase tags** and a description that does **not**
  repeat the title verbatim.
- Etsy explicitly wants tags to cover terms the title does **not** contain.
- Amazon indexes only the first ~1,000 bytes across all bullets; stuffing past
  that is dead weight, and titles over 75 characters get flagged and rewritten.

**Rule:** one listing = **one buyer intent**. Title owns the primary phrase,
tags cover *adjacent* phrases, description sells the use case.

### 4. Near-duplicate flooding
The same design recoloured 20 times, or one word swapped on the same layout 40
times, is the textbook spam pattern every platform screens for. Displate blocks
near-duplicate resubmission outright. Redbubble bans for tag spamming and
scaled-design spam. Shop-level quality is a ranking input — bad listings drag
down the good ones in the same shop.

**Rule:** hard dedup gate on `(layout_id, palette_id, subject_lemma)` and on
normalised title trigrams. Colourways are a *product option*, not a new listing.

### 5. Production-blind art
An image that looks finished at 512px on a laptop can fail completely as a
24×36 poster or a DTG shirt print: hairlines vanish, gradients band, small
lettering fills in, near-edge text gets trimmed, a white background prints as a
white rectangle on the garment.

**Rule:** production specs are part of the concept record, not an afterthought.
See `data/platform_specs.json`.

## The thumbnail law

Every marketplace surface — Redbubble's feed, Etsy search, Amazon's grid,
Displate's browse — is a wall of roughly 200–300px thumbnails. The buyer's first
decision costs about 400ms.

**If the design does not read at 250px, nothing else in this document matters.**

Practical consequences:
- One focal subject, not a busy scene.
- High figure/ground contrast.
- Text either large enough to read at 250px, or treated as texture.
- Palettes of 3–5 colours, not 30.

## The unit of work must change

| Old unit | New unit |
|---|---|
| A file | A **concept** |
| "generate 10,000 poster ideas" | "generate 40 validated concepts across 6 demand clusters" |
| Metadata written after the art | Metadata and art both derived from the same demand anchor |
| Success = rows produced | Success = rows that pass all 6 gates |

A **concept** is a demand anchor + an audience + a visual DNA block + production
specs + per-platform metadata + an IP clearance record. One concept fans out to
several platform variants and several product types — that is where legitimate
volume comes from, not from inventing more themes.

## Target operating numbers

Replace *"list hundreds of thousands"* with:

- **300–600 validated concepts** in the first pass, ~2,000–4,000 platform/product
  variants derived from them.
- Kill rate at the gates should be **high** (60–80% of raw generations rejected).
  If the validator is passing almost everything, the validator is broken.
- Review at 30–60 days: keep what sells, clone the *winning demand cluster*
  (not the winning image), cull the rest.

## A note on what I could not check

I don't have access to your previous chat sessions, so I could not read the
poster and t-shirt data you generated there. Everything above is diagnosed from
the marketplace side — what the platforms reward and punish — plus the symptom
you described (huge listing counts, no effectiveness), which is itself a very
specific signature. If you paste a sample of ~50 generated rows into this repo
(`pod/samples/`), the validator in `pod/tools/validate_concept.py` will score
them and tell you exactly which gates they fail.
