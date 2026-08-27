# eBay UK grid engine

The competitor teardown is in [`FINDINGS.md`](FINDINGS.md). This is what it builds.

## The one thing that changes everything

They are not generating a million ideas. They are generating a **grid**:

```
LISTINGS  =  DESIGNS  ×  PRODUCTS  ×  STORES
             ↳ size and colour are VARIATIONS INSIDE a listing, never separate rows
```

74% of their tee titles end in one of exactly **17 fixed garment suffixes**. Their
poster titles end in one of **~15 fixed format phrases**. The title is
`{design stem} + {keyword padding} + {product suffix}`, assembled to land in
eBay's 70–80 character band — and in 600 sampled titles, **not one exceeded 80**.

If our pipeline emits one row per creative concept, we need a million concepts to
reach a million listings. They need 20,000. Our unit cost per listing is ~50×
theirs. That is the whole gap.

## Proof it works

```
$ python3 tools/generate_listings.py designs --library lib20k.json --stores 3 --out million.jsonl

1,020,000 listings -> million.jsonl
  titles in the 70-80 band: 1,020,000 (100%)
  titles over 80 chars:     0
  duplicates:               0
  elapsed:                  21 seconds
```

20,000 designs → **1.02 million listings → 20.6 million SKUs** once size and
colour variations are counted.

## Two grids need almost no artwork at all

```bash
python3 tools/generate_listings.py flags     --stores 3   #  24,888 listings
python3 tools/generate_listings.py birthdays --stores 3   #  27,096 listings
```

- **Flags** — 4 treatments × ~125 countries × 17 garments. One flag treatment,
  correct demonym per country ("Torn Morocco Flag **Moroccan** Day Football", which
  is exactly their live format). 24,888 listings from *one* piece of art.
- **Birthdays** — 8 phrasings × ages 3–98, birth year computed from `--year`, with
  correct ordinals (21**st**, 43**rd**, 71**st**, and the 11/12/13 exception).
  Re-run every January or the whole grid goes stale.

These are the two purest grid themes in their catalogue, and they're sitting in
plain sight.

## Compatibility gating

A naive cartesian product emits `73rd Birthday … Kids Sweatshirt Jumper` and puts
rude slogans on childrenswear. That noise is what makes a large catalogue read as
spam. `compatible()` gates the grid instead:

- Birthday ages 3–15 → kids garments only; 16+ → adult garments only
- `uk_funny_slogan` and anything flagged `adult_only` → never on childrenswear
- `mens_only` copy → never on a womens cut
- per-design `exclude_products` opt-outs

Verified: kids garments carry ages 3–15, adult garments 16–98, nothing crosses.

## Policy guardrails (built in, not optional)

| Rule | Why |
|---|---|
| Size/colour are **variations inside one listing** | Splitting them into separate listings is the classic eBay duplicate-listing breach |
| Different **garment** or **print format** = separate listing | Genuinely different items — this is permitted and is where the multiplication is legitimate |
| Never the same `design+product` twice **within one store** | Enforced by the dedup key; verified 0 duplicates across 1.02M rows |
| Same `design+product` across **different stores** gets different keyword padding | Byte-identical cross-store listings look like what they are |
| Hard 80-character title ceiling | Over-length titles truncate and the tail never indexes |

## Files

```
FINDINGS.md                     The teardown - 6 findings, every number reproducible
data/product_matrix.json        17 garment slots + 5 art formats, price ladders, variation axes
data/uk_theme_bank.json         15 UK themes with measured shares + keyword banks
tools/generate_listings.py      The grid engine (stdlib only, streams to JSONL/CSV)
../research/ebay_corpus/        600 raw competitor titles + analyse.py
```

## Commands

```bash
# how big is the grid?
python3 tools/generate_listings.py estimate --designs 20000 --stores 3

# built-in near-zero-artwork grids
python3 tools/generate_listings.py flags     --stores 3 --out flags.jsonl
python3 tools/generate_listings.py birthdays --stores 3 --year 2026 --out bdays.jsonl

# your own library
python3 tools/generate_listings.py designs --library designs.json --stores 3 --out all.jsonl
python3 tools/generate_listings.py art     --library artworks.json --stores 2 --format csv --out art.csv
```

Design library format:

```json
[{"design_id": "blk_cafe_racer_01",
  "stem": "Cafe Racer Biker Motorbike Motorcycle",
  "theme": "uk_biker",
  "ip_tier": "R0",
  "extra_keywords": ["Custom Bike", "Enthusiast"],
  "adult_only": false,
  "exclude_products": []}]
```

## Where the designs come from

The grid multiplies designs — it doesn't invent them. Two sources, in priority order:

1. **Public domain.** 52% of Canvas Art Shop's catalogue is out-of-copyright art
   (Hokusai, Van Gogh, Goya, Klimt, Waterhouse, Morris, Blake, Munch…). A named
   masterwork carries standing search demand at zero origination cost, which is the
   one thing generated art cannot buy. Tens of thousands of catalogued works are
   available through Rijksmuseum, Met Open Access, NYPL, Smithsonian and Library of
   Congress. See [`../strategy/05_IP_SAFETY.md`](../strategy/05_IP_SAFETY.md).
2. **Original art on the measured UK themes** — biker, skull, Viking, flags, music
   scene, retro, military. `data/uk_theme_bank.json` carries the shares and the
   keyword banks; the visual DNA libraries in [`../data/`](../data/) constrain the
   image model so output doesn't regress to the generative mean.

**What not to copy:** 26% of their poster catalogue is protected IP (Banksy alone
is 14%) and 8% is celebrity likeness. Their retro-British-TV tee theme is
wholesale rights infringement. Copy the format engine and the public-domain
strategy; leave the exposure with them.

## How this fits the earlier work

`pod/strategy/` and `pod/data/` were aimed at Redbubble / Etsy / Amazon / Displate
— the right research for those channels, which you've said you're opening. The
six-gate model there governs **whether a design is worth making**. This engine
governs **how one design becomes thousands of listings**. They compose:

```
demand-gated design library  →  grid engine  →  per-channel metadata
     (pod/strategy)              (pod/ebay)      (04_METADATA_PLAYBOOK.md)
```

eBay is the one channel where the grid is the dominant mechanic, because eBay
ranks listings and the others rank designs.
