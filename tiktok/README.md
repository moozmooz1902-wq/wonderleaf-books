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
```

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
- `video.text_bias` — where captions sit in the safe area. `0.18` keeps them
  clear of both TikTok's top bar and the product on the wall.

## Requirements

Python 3.11+, and ffmpeg. If `ffmpeg` isn't on your PATH the pipeline falls back
to the static build from `imageio-ffmpeg`; install it with
`pip install imageio-ffmpeg`. (Note: Playwright's bundled ffmpeg is compiled
with `--disable-everything` and will not work.)
