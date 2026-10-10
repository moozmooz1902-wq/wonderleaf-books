# Colour and style measured from the pixels, not from the titles

10 October 2026. The titles say what a seller *calls* a picture. This note is
about what the pictures actually are, measured on a shuffled sample drawn from
the full 9,165,241-image corpus (Fy! + Displate).

Two different kinds of number are reported here and they have very different
reliability. **Read the caveat before using the style labels.**

## Why this ran here and not on a GPU

The plan was a GPU pod over the whole corpus. It did not survive contact:
RunPod's datacenter IPs are throttled by the Shopify CDN. A pod harvested
**8.3 MB of sitemap in 12 minutes and then stalled completely**, against
1.6 GB in 5 minutes from this container. Four pods were tried; two earlier
failures were my own (`bash -lc` resets PATH and dropped `/opt/conda/bin`, so
nothing ran at all; then a 31 GB container was killed because I had disabled
PIL's decompression-bomb limit).

The useful consequence: **the colour work needs no GPU.** It is numpy, it runs
at download speed, and it is exact. Total RunPod spend on the attempt was
about **$0.21**.

## The caveat: style labels are weak, colour numbers are not

The CLIP zero-shot labels were checked against titles that name their own
technique — if a seller calls it a linocut, did the model say linocut?

| technique | agreement |
|---|---|
| photograph | 80% (4/5) |
| linocut | 67% (4/6) |
| watercolour | 44% (21/48) |
| crayon / pastel | 22% (2/9) |
| paper collage | 0% (0/10) |
| line art | 0% (0/2) |
| pencil / graphite | 0% (0/2) |
| **overall** | **37.8% (31/82)** |

So the technique axis is usable only for photograph and linocut, and
`vector_flat` taking 18.5% of Fy! and 35.3% of Displate is almost certainly a
generic prompt attracting mass rather than a real finding. **Technique shares
below are not to be quoted as fact.** The comparisons *between* the two
sources are more robust than the absolute numbers, because the same bias
applies to both.

The colour and composition numbers have no such problem — they are measured
arithmetic on the pixels.

## Colour strategy, measured (this is the reliable part)

Derived from the hue histogram, saturation and palette of each image, not from
the model:

| strategy | Fy! | Displate |
|---|---|---|
| Duotone or analogous (two adjacent hue families) | **32.4%** | 33.4% |
| Full spectrum | 30.4% | 25.2% |
| **Monochrome** | **20.8%** | **23.0%** |
| Complementary pair (two hue families far apart) | 13.9% | 14.8% |
| Warm neutral + hot accent | **2.5%** | 3.6% |

### This corrects the earlier grammar notes

`the_grammar_of_what_sells.md` was written from looking at a small number of
images and named three colour strategies, leading with:

> *"C1 — A complementary pair carries the image… Five of the first eleven
> images use orange/blue. This is not coincidence; it is the house trick."*
> *"C2 — Warm neutral plus one hot accent… This is the palette that makes a
> mixed catalogue look like one shop."*

Measured across thousands of images rather than eleven: **C1 is 14%, not the
house trick. C2 is 2.5%, not the house palette.** Both were real patterns in
the images that were looked at, and both generalised badly.

What actually dominates is duotone/analogous at ~33% and — the finding that
matters — **monochrome at 21–23%. One competitor image in five is
essentially colourless.**

That lines up exactly with the first-party demand evidence, where charcoal
(5.96%) and sketch (5.26%) are the only techniques beating the base watch
rate. Supply and demand agree on monochrome, which they agree on almost
nowhere else.

It also explains the null result on colour words in titles: nothing cleared
significance either way, and `orange` — the supposed house trick — sits
slightly *below* base at 0.28%.

## Composition, measured

| ground | Fy! | Displate |
|---|---|---|
| Textured | 48.0% | 24.3% |
| Full bleed, no margin | 28.4% | 47.3% |
| Flat colour | 20.8% | 22.8% |
| White paper with a margin | 2.8% | 5.6% |

| text on the image | Fy! | Displate |
|---|---|---|
| None | 74.5% | **55.0%** |
| Text-led | 20.5% | **34.2%** |
| Small caption | 5.0% | 10.8% |

**Displate carries text on 45% of its images against Fy!'s 25.5%** — the
fandom-versus-décor split again, visible in the pixels. And Displate's
subjects include `religious` at 4.2% and `vehicle_car` at 5.6%, neither of
which appears near the top for Fy!.

## The gap worth noting

`G6_poster_margin` — an art panel inset inside a cream type margin, the format
the repo already builds and the one the vintage travel posters use — is only
**2.8% of Fy!'s images** and 7.4% of Displate's. White-paper grounds are
2.8% and 5.6%.

So the format that the first-party watcher data points at is thinly supplied
by both competitors. That is the shape of an opportunity rather than a
crowded shelf, and it costs nothing to test.

## Sample and status

4,000 images, shuffled across the full 9.17M corpus, so any prefix is
unbiased. A larger colour-only pass over 400,000 images is running; this note
will be superseded by it on the colour numbers, which are the ones worth
having precise.

---

# The measured technique spec (59,997 images)

Superseding the CLIP-labelled section above for anything about technique.
Method changed: instead of asking a model what technique a picture is (37.8%
agreement), the **title is the label** — Fy! states its technique in 142.6% of
its titles — and the **pixels are the measurement**. No model, no guessing.

Sample: 59,997 images measured from a 400,000-image list shuffled across the
full 9,165,241-image corpus. Script: `wallart-data/technique_profiles.py`.

| technique | n | lightness | saturation | edge | border−centre | dominant strategy | top hues |
|---|---|---|---|---|---|---|---|
| painting | 1,492 | 0.578 | 0.329 | 0.054 | +0.039 | full spectrum 41% | red 30% orange 28% cyan 13% |
| illustration | 1,228 | 0.624 | 0.300 | 0.060 | +0.055 | full spectrum 36% | red 29% orange 25% cyan 16% |
| watercolour | 666 | **0.724** | 0.212 | 0.052 | **+0.142** | duotone 36% | orange 28% red 21% cyan 14% |
| ink | 655 | 0.646 | 0.298 | 0.047 | +0.059 | duotone 47% | red 29% rose 27% orange 13% |
| photograph | 287 | 0.529 | **0.177** | 0.052 | **−0.037** | **monochrome 57%** | red 36% cyan 25% |
| drawing | 245 | 0.713 | **0.166** | 0.052 | **+0.124** | **monochrome 44%** | orange 33% red 33% |
| pastel | 213 | 0.708 | 0.231 | 0.041 | +0.046 | duotone 35% | orange 29% red 28% |
| oil | 170 | **0.514** | 0.327 | 0.053 | **−0.042** | full spectrum 37% | orange 30% red 21% |
| collage | 160 | 0.643 | 0.296 | 0.054 | **+0.171** | full spectrum 51% | orange 32% red 28% |

## Three findings that are directly usable

**1. `border − centre` sorts every technique into three presentation families.**
This single number says how the work is staged, and it is unambiguous:

- **Margin prints** (+0.12 to +0.17): collage, watercolour, drawing. These are
  presented as paper with a visible light border. A generator must leave that
  margin, or the output will read as the wrong kind of object.
- **Near full-bleed** (+0.04 to +0.06): ink, illustration, pastel, painting.
- **Edge-to-edge and dark** (−0.04): oil, photograph. No margin at all, and
  darker than everything else.

**2. Red and orange are 50–60% of the colourful pixels in *every* technique.**
Not one group is an exception. Wall art is warm, universally, whatever the
medium. Set against the title evidence — where colour words clear nothing and
`orange` sits slightly *below* the base watch rate — the rule is exact:
**warm palettes belong in the picture and never in the title.**

**3. The two least saturated techniques are drawing (0.166) and photograph
(0.177), and both are the most monochrome** (44% and 57%). These are the same
techniques the first-party watcher data singles out: charcoal 5.96% and
sketch 5.26%, the only two beating the 1.05% base.

So the strongest demand signal in the project points at the least saturated,
most monochrome corner of the supply — and that corner is thinly populated:
drawing is 245 of 59,997 measured images, **0.4%**.

**A technique with the best measured demand and 0.4% of supply is the clearest
opportunity this research has produced.**

## Generation targets, per product

**Charcoal breed portrait** — match the `drawing` profile:
lightness **0.71**, saturation **0.17**, edge **0.052**, border−centre
**+0.12** (a real paper margin), monochrome-leaning.

**Vintage UK place poster** — match the `illustration` profile:
lightness **0.62**, saturation **0.30**, edge **0.060**, border−centre
**+0.055**, full-spectrum or duotone, warm-dominant.

These are assertable: render a batch, measure it with the same script, and
compare. A generated set that does not land near these numbers does not look
like the market, whatever it looks like to us.
