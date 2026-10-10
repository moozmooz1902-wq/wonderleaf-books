# What to generate, from what the seller's own buyers saved

10 October 2026. Everything here is scored against the Watchers column of the
seller's own eBay export — 168,819 listings, 2,142 watchers, a **1.05% base
rate**. Each word is scored in Poisson standard deviations above or below its
expected count, so the small counts cannot invent a winner. Only |z| ≥ 2 is
shown. Script: `wallart-data/mine_unsold.py`.

This is not competitor supply. It is what this seller's own audience saved.

## The winners

### Technique — the hand-drawn monochrome family, and only that family

| z | watched / listings | rate | technique |
|---|---|---|---|
| **+5.9** | 9 / 151 | **5.96%** | charcoal |
| **+4.4** | 6 / 114 | **5.26%** | sketch |
| +2.4 | 7 / 279 | 2.51% | drawing |

Nothing else in a 27-word technique vocabulary clears significance.
**Watercolour, linocut, oil, gouache, pastel, collage, engraving, risograph —
none of them.** That is a surprise worth stating, because watercolour and
linocut are exactly what Fy! leans on (watercolour 5.6% of its titles) and what
the earlier grammar notes recommended.

The three that do clear are one coherent thing: a hand-made monochrome mark.
Charcoal at 5.7× the base rate is the single strongest technique signal in the
project.

### Register — vintage, noir, gothic, gold

| z | watched / listings | rate | word |
|---|---|---|---|
| **+6.6** | 68 / 2,959 | 2.30% | vintage |
| **+4.8** | 9 / 197 | **4.57%** | noir |
| **+3.8** | 5 / 103 | **4.85%** | gothic |
| +2.3 | 30 / 1,871 | 1.60% | retro |
| +2.1 | 10 / 491 | 2.04% | gold |

### Place and culture

| z | watched / listings | rate | word |
|---|---|---|---|
| **+4.3** | 14 / 443 | 3.16% | japanese |
| **+3.9** | 5 / 99 | **5.05%** | london |
| **+3.6** | 7 / 185 | 3.78% | greek |
| **+3.1** | 5 / 133 | 3.76% | japan |
| +2.9 | 5 / 143 | 3.50% | york |

Plus the aggregate UK-place result: **354 listings, 7.91%, z = +12.6**.

### Subject

| z | watched / listings | rate | subject |
|---|---|---|---|
| **+7.2** | 13 / 213 | **6.10%** | chopper (motorcycles) |
| **+4.1** | 19 / 728 | 2.61% | moon |
| +2.8 | 4 / 102 | 3.92% | ship |

## The losers, which matter just as much

| z | watched / listings | rate | word |
|---|---|---|---|
| **−4.9** | 22 / 5,690 | **0.39%** | funny |
| **−3.9** | 6 / 2,479 | **0.24%** | cute |
| −2.4 | 1 / 750 | **0.13%** | dark |
| −2.2 | 19 / 3,004 | 0.63% | love |
| −3.1 | 13 / 2,886 | 0.45% | shirt |

**The t-shirt register does not transfer.** `funny` and `cute` carry 8,169
listings between them and 28 watchers — a quarter to a third of the base rate.
The humour and cuteness that sell t-shirts actively repel wall-art buyers.
`shirt` at 0.45% says the same thing from another angle.

Note the split between `dark` (0.13%, a dud) and `gothic`/`noir` (4.85% and
4.57%, strong). The *aesthetic* sells; the flat adjective does not. That is a
lesson about naming as much as about pictures.

## The brief this adds up to

A coherent house style falls out of the numbers, and none of it is encumbered:

> **Hand-drawn monochrome marks — charcoal and graphite sketch — in a vintage,
> noir or gothic register, of named places (UK first, then Japan and Greece)
> and of specific heavy objects (motorcycles, ships, the moon), with gold as
> the one accent.**

Every element of that is measured, not guessed. It is also almost the opposite
of the catalogue the seller currently has, which is mostly licensed fandom,
plus a long tail of "funny" and "cute" that earns nothing.

### How this sits against the earlier research

The grammar notes recommended eleven techniques, led by the painterly ones, and
three colour strategies built on complementary pairs. Those came from reading
competitor *supply*. This comes from first-party *demand*, and it disagrees:
the painterly techniques do not clear significance, while charcoal — which the
grammar notes list but do not emphasise — is the top performer.

Where supply and demand disagree, demand wins. The painterly techniques are
not ruled out; they are simply unproven on this audience, and should be
treated as hypotheses to test rather than the backbone of the first run.

The one place they agree: `vintage` and `retro` both score, and the grammar
notes' photochrom technique ("hand-tinted monochrome photograph, faded palette,
grain, aged cream border") sits squarely inside the vintage/noir winner.

## Limits

- Watchers are not sales. No sales data exists anywhere in this project.
- This ranks only what the catalogue already contains. Charcoal wins among the
  151 charcoal listings that exist; it cannot tell us how a charcoal listing
  would do at 50,000 of them, and saturation is a real risk.
- Several winners rest on single-digit watched counts. The σ test guards
  against the worst of it, but these are leads to test at modest volume first,
  not licences to generate a million of anything.
- The catalogue is dominated by licensed fandom, which may itself have drawn a
  fandom-leaning audience. A cleaner catalogue might attract different buyers.
