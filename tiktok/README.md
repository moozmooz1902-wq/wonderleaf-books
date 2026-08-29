# Wonderfeed

Builds ready-to-post TikTok videos for wall-art print sets: Claude writes the
script, fal.ai generates the visuals from your real product photo, ffmpeg
assembles a 1080×1920 MP4 with burned-in captions.

Read [`STRATEGY.md`](STRATEGY.md) first — it explains *what* to post and why.
This file covers *how to run it*.

---

## Why this doesn't auto-post to TikTok

You asked for fully hands-off daily uploads with the product link attached.
That is not currently possible, for three independent reasons:

1. **Unaudited API clients can only post `SELF_ONLY`** (private), capped at
   5 users per 24h, and the account must be private at the time of posting.
   Public posting requires passing TikTok's app audit — 2–4 weeks, multiple
   rounds of feedback.
2. **Even once audited, the Content Posting API cannot attach a TikTok Shop
   product tag.** There is no endpoint for it. You'd be auto-posting videos
   with no link — the one thing that makes them worth posting.
3. **TikTok Shop Affiliate APIs are not available in the UK/EU.**

So the pipeline automates everything up to the post, and you spend ~15 minutes
once a week scheduling a batch in TikTok Studio (which *does* let you tag
products and schedule 10 days ahead). Monday–Saturday you touch nothing.

If you later pass the audit and decide link-free posting is worth it,
`wonderfeed/publish.py` has the token-refresh and upload plumbing; only the
`video.publish` call would need adding.

## Setup

```bash
cd tiktok
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp config/settings.example.yaml config/settings.yaml
cp config/products.example.yaml config/products.yaml
```

Then edit `config/products.yaml`:

- `link` — your TikTok Shop product URL
- `images` — a real photo of the prints, saved under `tiktok/assets/`.
  Every generated visual is anchored to this, so the art in the video is the
  art you sell.
- `angles` — **your variety engine.** 15+ per product. The pipeline will not
  reuse a (product, angle) pair within 21 days.

Secrets go in the environment, never in the YAML:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export FAL_KEY="..."
```

## Running it

```bash
# Prove the pipeline works — no API calls, no spend, placeholder visuals
python -m wonderfeed.run --dry-run --count 3

# Build a real week
python -m wonderfeed.run --count 7

# One product only
python -m wonderfeed.run --product botanical-3set --count 2

# Everything in one niche, N videos for each product in it
python -m wonderfeed.run --niche cars --per-product 3

# Cap the total regardless
python -m wonderfeed.run --niche family --per-product 3 --count 20
```

`--per-product` is the "more videos for them" switch: it takes N *distinct*
angles from every product in scope, so ten products at 3 each gives thirty
videos with no repeated premise.

### Angles — the variety engine

One product against thirty angles gives thirty genuinely different videos. The
same product with three angles gives near-duplicates, which TikTok's duplicate
detection notices. Don't hand-write them:

```bash
python -m wonderfeed.angles --product botanical-3set --count 30          # preview
python -m wonderfeed.angles --product botanical-3set --count 30 --write  # append
```

It is told what you already have and won't repeat it, so run it again whenever
a product runs dry.

### Filling the shop — catalogue generation

The 100-slot cap is the real constraint, so fill every slot with a *different
bet*. This generates listing concepts across twelve niches, all as trios:

```bash
python -m wonderfeed.catalogue --list-niches
python -m wonderfeed.catalogue --count 100                    # preview
python -m wonderfeed.catalogue --count 100 --write            # merge into products.yaml
python -m wonderfeed.catalogue --niche cars --count 12 --write
python -m wonderfeed.catalogue --count 20 --dry-run --write   # offline placeholders
```

Write-back merges by `id` and never overwrites an existing product, so re-running
is safe — it adds what's new and leaves what's there alone.

Each concept arrives with a name, description, three room settings and five
angles, but with **empty `link` and `images`**. Fill those in once the listing
exists in Seller Center: the pipeline refuses to generate visuals without a real
product photo, because that photo is what keeps the art in the video identical
to the art you sell.

### Listing rotation — working the 100 cap

```bash
python -m wonderfeed.listings add --sku WL-001 --product botanical-3set --title "Botanical Trio"
python -m wonderfeed.listings import --csv seller-center-export.csv
python -m wonderfeed.listings review
python -m wonderfeed.listings cull --sku WL-002 --reason "1900 views, 0 units"
```

`review` sorts every live listing into `KEEP` / `CULL` / `WATCH` / `TOO EARLY`
and tells you how many slots culling would free. The important distinction:

- **`CULL`** — real traffic, zero units. The listing converts nothing. Free the slot.
- **`WATCH`** — barely any traffic, zero units. **Not** dead, just untested.
  Point more videos at it before judging.

Both look like "zero sales" on a Seller Center report and they need opposite
responses. Thresholds are under `listings:` in `settings.yaml`.

The CSV importer matches Seller Center's headers loosely (`Seller SKU`,
`Product Views`, `SKU Orders`, `GMV`…) and strips `£` and thousands separators.
Unknown SKUs are reported rather than silently dropped. Culling here only
records the decision — you still delist it in Seller Center.

Each video produces three files in `out/`:

| File | What it is |
|---|---|
| `<stem>.mp4` | The 9-second 1080×1920 video |
| `<stem>.txt` | Caption, hashtags, the product to tag, and a pre-post checklist |
| `<stem>.json` | The full brief, for debugging a bad video |

## Weekly automation

`.github/workflows/wonderfeed.yml` runs every Sunday 06:00 UTC, builds 7 videos
and uploads them as a downloadable artifact. Add `ANTHROPIC_API_KEY` and
`FAL_KEY` under **Settings → Secrets and variables → Actions**.

Trigger it by hand from the Actions tab (`Run workflow`) to test — tick
**dry run** for a free run.

State (`out/state.json`) is cached between runs so angle rotation persists.

## Cost per video

| Stage | Cost |
|---|---|
| Script (Claude Sonnet) | ~£0.01 |
| 3 stills (Flux Kontext) | ~£0.09 |
| Motion clips (optional, Kling) | ~£0.60 |
| Render (ffmpeg, local) | £0 |

**~£0.10/video with `use_motion: false`** (Ken Burns pans over stills — this is
the default and it looks fine at 9 seconds). ~£0.70 with real motion.

At 3/day that's roughly **£9/month** on stills, or £63/month with motion. Start
with motion off; turn it on only for products already proven to convert.

## Configuration notes

- `models.still_endpoint` / `motion_endpoint` — fal changes model slugs
  regularly. If a run fails with a 404, check <https://fal.ai/models> and update
  these. Nothing else needs touching.
- `video.beat_seconds` — `[2.5, 3.0, 3.5]`. Shorter is generally better; don't
  exceed ~12s total for this format.
- `voiceover.mode` — `none` by default. Add a trending sound in-app instead;
  it outperforms TTS narration for this category.
- **Looking un-AI.** `wonderfeed/realism.py` gives each video a fixed camera,
  lens, lighting and grade — held constant across its three beats so they read
  as one shoot — plus rotating framing and two domestic imperfections (a plug
  socket, a scuffed skirting board, a mug on the side table). It also steers
  *away* from "hyperrealistic / 8k / ultra-detailed", which push the glossy
  render look rather than reduce it. Add your own entries to the lists in that
  file; more variety there means less sameness across a hundred videos.
- `video.text_bias` — where captions sit in the safe area. `0.18` keeps them
  clear of both TikTok's top bar and the product on the wall.

## Requirements

Python 3.11+, and ffmpeg. If `ffmpeg` isn't on your PATH the pipeline falls back
to the static build from `imageio-ffmpeg`; install it with
`pip install imageio-ffmpeg`. (Note: Playwright's bundled ffmpeg is compiled
with `--disable-everything` and will not work.)
