# Generation spec for the first build

10 October 2026. Written from measurement, not taste. Every number here traces
to one of: the seller's own watcher data (`first_party_demand_watchers.md`),
the measured pixel statistics (`measured_colour_and_style.md`,
`wallart-data/technique_profiles.py`), or the size contract on the wall-art
branch. Nothing has been generated yet — this is the brief to run when the
seller says go.

## Product A — vintage travel poster, UK place

**Why:** `vintage` z = +6.6, UK places 7.91% vs 1.05% base at z = +12.6, the
format is grammar G6 which `wallart/render.py` already builds, and 24 random
live images titled "vintage" came back as exactly this.

**Composition (G6):** an art panel inset inside a cream margin; the place name
set in the margin in letterspaced caps; optional small second line for the
county or country.

**Measured targets** — from the `illustration` profile (n = 596), which is what
these are:

    mean lightness        0.62
    mean saturation       0.30
    edge density          0.060      (flat shapes, few fine lines)
    border minus centre   +0.05      (a margin, but not a wide white one)
    colour strategy       full spectrum 36% / duotone-analogous
    hue mass              red ~28%, orange ~25%, cyan ~16%

**Prompt skeleton** (FLUX.1 schnell, 4 steps, guidance 0.0, 256-token window,
848x1200 for the A-ratio):

> `vintage travel poster illustration of {PLACE}, {LANDMARK}, flat screen-printed
> colour in {PALETTE}, simplified geometric shapes, bold shapes with no outline,
> high horizon, no text, no lettering, no words`

`{PALETTE}` is drawn from the three measured strategies, weighted as measured:
duotone-analogous ~33%, full spectrum ~30%, complementary ~14%, and warm
neutral + accent only ~3% — **not** the "house trick" the earlier grammar note
claimed.

**The negative prompt does not work** — FLUX schnell at `guidance_scale=0`
ignores it. "no text, no lettering" goes in the positive prompt, and the OCR
gate is what actually enforces it.

## Product B — charcoal breed portrait

**Why:** `charcoal` 5.96% and `sketch` 5.26% are the only techniques beating
the base rate; nine of 24 random live charcoal images are breed portraits;
221 Kennel Club breeds are already enumerated; grammar G8 describes the layout.

**Composition (G8):** one head-and-shoulders subject, centred, cropped by the
lower edge, vast light ground, breed name in small letterspaced caps beneath.

**Measured targets** — from the `drawing` profile (n = 113):

    mean lightness        0.71      (light, airy)
    mean saturation       0.18      (very low - nearly colourless)
    edge density          0.052
    border minus centre   +0.13     (a real paper margin)
    colour strategy       duotone-analogous 44%, heavily monochrome-leaning

**Prompt skeleton:**

> `charcoal and graphite drawing of a {BREED}, head and shoulders, direct gaze,
> visible paper grain, loose open hatching, vast white paper around the subject,
> no colour, no text`

## Rules that apply to both

From `the_grammar_of_what_sells.md`, still standing because they were about
craft rather than frequency:

- **No gradients.** Flat fill, contour line or hatching. A smooth airbrushed
  gradient is the clearest tell of cheap generated work.
- **Detail gradient:** the subject is the only sharp thing. That is what makes
  a design read at thumbnail size, which is the size the buying decision is
  made at.
- **Line over mass, never under.**
- **Reject any output with legible text, a signature or a watermark.** Three
  sampled competitor images carried a painted artist signature, so the OCR
  gate is confirmed necessary.
- **Never generate** characters, franchises, logos, club crests, celebrity
  likeness, royal insignia (criminal under s.99 Trade Marks Act 1994),
  branded objects, or any artist dead less than 70 years.

And from tonight:

- **Never "funny" or "cute".** 0.39% and 0.24% against a 1.05% base.
- **Do not use colour as a SKU axis.** Colour words in titles clear nothing
  either way; `orange` is slightly below base. Colour belongs in the picture.
- **Warm palettes in the picture.** Red and orange are 50–70% of the colourful
  pixels in *every* measured technique group. That is a property of the art,
  not of the title.

## Output contract — unchanged, and asserted

    art/raw/<SKU>.png     the print file, A4 2480x3507 / A3 3508x4961 / A2 4961x7015 at 300dpi
    art/mock/<SKU>.jpg    the listing photo, 2000x2000 on wall #EDE9E3
    moulding              outer edge (406,160)-(1593,1840), art area 1106x1598

Three frame colours on identical geometry (`wallart-data/frames.py`): **black
is the main image** because the team's crop tool finds the dark moulding;
white and oak are gallery variants. Listing shape follows the Fy! dump:
`Color=Black;White;Oak | Size=A4;A3;A2`, price £19.99 / £24.99 / £29.99
framed, category 360, quantity 1, policies 1/1/1.

## Titling

Keyword stack, not a sentence — 70.3% of competitor titles are bare noun
phrases. Shorten the 43-character boilerplate tail and give those characters
to subject, place, technique and register. The current catalogue spends 56%
of every title on a tail identical across all 168,819 listings and truncates
the distinguishing part at 35 characters.

## Duplicate guard

Near-duplicate checking runs on the **picture**, not the title — confirmed:
the live catalogue's titles are only 2.1% duplicated while the pictures are
the problem. pHash first, then CLIP/DINOv2 embeddings with FAISS, reject at
≥0.93 cosine. No two designs may share subject + technique + palette.

## First run size

~20,600 designs (18,465 place posters + 2,136 breed portraits), about **$8 of
GPU**, becoming 185,400 eBay variations across three frames and three sizes.
Measure that against real watchers before scaling the multiplier.
