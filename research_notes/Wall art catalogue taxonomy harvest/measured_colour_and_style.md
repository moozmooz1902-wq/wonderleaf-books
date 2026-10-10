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
