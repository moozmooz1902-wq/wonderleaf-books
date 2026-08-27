# Store 1 export — what 669,137 real listings actually show

Source: the store's own eBay revise export, 97 MB, 669,137 rows.
Template `eBay-active-revise-price-quantity-download_GB`.

| | |
|---|---|
| Wall art (cat 360) | **424,117** |
| T-shirts (cat 15687) | **244,818** |
| Variations | **none** — 668,935 of 669,137 are single listings |
| Quantity | qty 1 on 669,114 |
| Mean price | £10.09 |
| Approx catalogue value | ~£6.75M against a £10M ceiling |

---

## Correction: the t-shirt titles were already fixed

I recommended retitling as phase 0. **On the t-shirts that has already been done**,
and it did not produce sales.

| Term | SPEC §11 (before) | This export (now) |
|---|---|---|
| Womens | 0% | **100%** |
| Mens | 100% | 100% |
| Unisex | 4% | **98%** |
| Novelty | 5% | **89%** |
| Gift | 0% | **82%** |
| Funny | 0% | **36%** |
| Mean title length | — | **77.7 / 80** |
| Under 70 chars | — | **0%** |

By my own criteria those titles are now textbook. Nothing left to win there.

**So the title theory is not the whole answer, and I was wrong to lead with it for
the tees.** It still applies to wall art (below), but the tees need something else.

---

## What is actually wrong: the catalogue has no demand behind it

Measured against the themes that demonstrably sell on UK eBay (from the 1,080-title
competitor corpus in `pod/research/ebay_corpus/`):

| Theme | Competitors | Wonderleaf tees | Wonderleaf wall art |
|---|---|---|---|
| Biker / motorcycle | **15%** | 0.2% | 0.3% |
| Music scene | **14%** | 0.3% | 0.1% |
| Skull / gothic | **12%** | 4.8% | 0.0% |
| Flags / nationality | **10%** | 0.1% | 0.4% |
| Viking / Norse | **6%** | 1.6% | 0.0% |
| Birthday / age | **4%** | **0.0% — 2 listings** | 0.0% |
| Fishing / outdoors | 4% | 0.3% | 0.6% |
| Family / gifting | 3% | **0.0%** | 0.4% |
| Gym / martial arts | 4% | 0.0% | 0.1% |

What the catalogue *is* about instead:

> **tees:** nature, wildlife, bird, neon, fantasy, botanical, reptile, mushrooms,
> anime, charcoal, glowing, sunbeams
>
> **wall art:** vintage, green, botanical, blue, travel, sage, burgundy, navy,
> dusty pink, mustard, farmhouse, rustic

This is a **nature-and-wildlife illustration catalogue**. It is well made and
correctly titled. It is simply not what UK eBay buyers shop for on a t-shirt.

**Two listings out of 244,818 mention a birthday.** Birthday tees are the most
mechanical, most reliable gifting grid on the platform — competitors run thousands.

The 35.6% "funny slogan" figure is an artefact: it counts the word *funny* in the
keyword tail added by the retitle, not actual joke designs.

### Why this happened

`graphics.py` builds 1,512 subjects × 35 scenes × 16 styles = 3,894,993
combinations. The subjects were chosen to fill a grid, not because anyone searches
for them. "Ostrich Bird", "Beetle Neon Glow", "Grave Stone Greyscale" are all
valid points in that space and all commercially empty.

That is gate G0 from the original data pool — **no demand anchor** — at 244,818×
scale.

---

## Wall art: the retitle is only half done

Unlike the tees, wall art still has real title headroom:

- mean **67.4** chars, **59% under 70**, **5,343,432 wasted characters**
- gift 25%, room word 27%, home decor 8%, poster 18%
- but **canvas 0%, framed 0%, picture 0%, ready to hang 0%**

bigboxart's tail — `Canvas Print Wall Art Home Decor Ready to Hang` — is 45
characters of product nouns. Wonderleaf ends on `A4 ART PRINT`, 12.

Finishing this retitle is still cheap and still worth doing.

---

## Revised priorities

| Was | Now |
|---|---|
| 1. Retitle everything | 1. **Finish the wall-art retitle only** (tees are done) |
| 2. Fix the generator | 2. **Build catalogue in the themes that sell** — biker, skull, Viking, birthday, flags, trades, family, music |
| 3. Generate more | 3. **Add size variations to the tees** — all 244,818 are single qty-1 listings, so none appear in a size-filtered search |

The slogan grid already built (`pod/ebay/data/slogan_designs.json`, 3,119 designs)
sits exactly in the themes reading 0–5% here, and costs £0 to render on black.

**More of the current catalogue will not sell. Different catalogue will.**
