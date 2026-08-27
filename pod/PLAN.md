# The plan — after reading the handover

Written 2026-08-28 from `pod/inbox/handover/` (SPEC.md, 7,302 lines of working
code, 6 real live listing rows) plus the wall-art project notes.

---

## The diagnosis is now confirmed from three independent directions

I found the same fault three separate ways. That is as close to certainty as
this gets.

**1. My competitor teardown** (600 live titles, harvested overnight)
Winners pack the title to eBay's limit and spend it on buyer language.
Canvas Art Shop: mean **73.6 chars, 82% inside the 70-80 band, none over 80**.

**2. Your own audit** (`SPEC.md` §11, measured across **669,138 live listings**)

| Term | T-shirts | Wall art |
|---|---|---|
| gift | **0%** | **0%** |
| funny | **0%** | — |
| novelty | 5% | — |
| unisex | 4% | — |
| "Womens" on unisex garments | **0%** | — |
| home decor / picture / framed | — | **0%** |
| room words (bedroom, kitchen…) | — | **~0%** |
| poster | — | 14% |

**3. Your live CSV** (the 6 real rows in the handover)

```
[52] Rugby Ball Kraft Poster Terracotta A4 Wall Art Print              ← 28 chars unused
[63] Virgo Constellation Retro 70s Black And White A4 Wall Art Print   ← 17 chars unused
[75] Ostrich in Moonlight Bird Mens T-Shirt Black 100% Cotton Ornithology Unisex
[80] Monarch Butterfly Under the Stars Nature Mens T-Shirt Black 100% Cotton Wildlife
```

Wall art averages **65 characters against an 80 limit**. That is roughly a fifth
of your single most valuable ranking asset left blank, ~424,000 times.

And the words that *are* there come from the generator's own taxonomy, not from
anything a buyer types:

- `FAMILY_EXTRA` in `ebay_graphics.py` ships **"Ornithology"**, **"Herpetology"**,
  **"Entomology"**. Nobody buying a t-shirt searches those.
- Wall art ships **"Kraft Poster"**, **"Terracotta"**, **"Muted Pastels"**,
  **"Industrial Loft"**. Those describe the picture to somebody already looking
  at it.
- **"Black 100% Cotton"** costs 17 characters in every tee title to say something
  the item specifics already say and nobody searches.

`AUDIENCE = "Mens"` is hardcoded at line 124. Your own audit says Womens appears
in 0% of unisex-garment titles. That is half the gift market unable to find you.

> **The catalogue is not too small. It is invisible.** 424,118 wall art listings
> with no sales is not a volume problem — the volume is already there.

---

## Phase 0 — Retitle the live catalogue. Do this first, before anything else.

This is by a wide margin the highest-value work available, and it is cheap.

**Why it beats generating anything new:**

| | Retitle | New listings |
|---|---|---|
| Listing age, watchers, search history | **kept** | starts at zero |
| Image cost | **£0** | GPU time |
| Listing slots | **0 used** | consumes allowance |
| Turnaround | hours | days |
| Reach | ~424k wall art + the tee catalogue | whatever you add |

An eBay **Revise** file changes the title in place. Nothing ends, nothing
relists, images are untouched. Warning rows still apply — only `Failure` does not
(SPEC §6).

**What already exists:** `retitle/retitle_art.py` — and its docstring reaches the
same conclusion I did, independently. Good.

**What is missing:** `retitle_tees.py` is named in SPEC §11 but **is not in the
handover zip**. Either send it or I rebuild it.

**The rewrite rule, both sides:**
1. Keep the subject — it is the word people type.
2. Delete generator vocabulary — palette names, style names, taxonomy words.
3. Delete anything the item specifics already carry (`Black`, `100% Cotton`).
4. Spend the freed characters on **buyer language**: Gift, Funny, Novelty, For
   Him, For Her, Christmas, Birthday, Dad, Mum, Unisex, **Womens**.
5. For wall art, stack the product nouns the way competitors do — *Wall Art Print
   Poster Picture Decor* — and add a **room word**. Room is a sidebar filter.
   Never claim Canvas or Framed on unframed paper.
6. **Fill 70-80 characters.** Every one under 70 is wasted rank.

**Order of attack:** wall art first — it has the worst titles, the most unused
characters, and 424k listings with nothing to lose.

---

## Phase 1 — Stop the generator producing the same fault

Retitling fixes the past; this stops it recurring.

In `listing/ebay_graphics.py`:

- Replace the taxonomy words in `FAMILY_EXTRA` with commercial ones. `Ornithology`
  → `Bird Lover Gift`. `Entomology` → `Nature Lover Gift`.
- `AUDIENCE = "Mens"` → `"Mens Womens"` where sizing honestly supports it, so the
  garment is findable by both. (Your note about returns is fair — the fix is
  honest unisex sizing language, not silence.)
- Drop `Black 100% Cotton` from the title. It is already in the item specifics.
- Add a **fill-to-70 pass**: after the title is built, if it is under 70
  characters, append unused buyer keywords until it is not.

Same three changes on the wall-art builder, plus a room word.

---

## Phase 2 — Then, and only then, add new catalogue

The engine I built overnight plugs straight into the existing pipeline:

- **Slogan grid** — 50 joke frames × 93 subjects = 3,119 slogans, and on black
  tees they are pure typography, so they cost **£0 to render**. That is a
  genuinely different product from the SDXL graphics: text tees serve searches
  the picture tees cannot.
- **Symbol × render-treatment grid** — the axis I found in a competitor's Viking
  range (Valknut / Detailed / Charcoal / Frozen / with Runes). Maps directly onto
  your SDXL pipeline: same subject, different style prompt.
- **Design-as-variation** — one competitor listing carried 14 designs in a single
  listing, concentrating sales and rank instead of spreading it. Worth an A/B.

Your design space is already 3,894,993 combinations against a ledger of ~924k.
**Supply of designs was never the constraint.**

---

## What I still need from you

| Gap | Why it matters |
|---|---|
| **`retitle_tees.py`** | Named in SPEC §11, absent from the zip |
| **Wall art frame sizes, colours, pricing** | You said black frames — I have Store 1/2 as A4/A3/A2 and Black/White/Oak at £24.99/£29.99/£34.99 framed. Confirm what is current |
| **Mockup templates** (the actual PNGs) | To composite properly instead of my placeholder |
| **Store category IDs** | `StoreCategory` blank in both pipelines |
| **Paper gsm** | For the wall-art description block |

## Two things worth fixing while we are in there

- **`pick.py` ledger bug** (SPEC §8): a *failed* run still appends its draw to
  `used_designs.txt`. Three failures inflated the ledger 924,199 → 1,824,199,
  burning 900,000 designs that were never generated. It should only write on
  success.
- **7 stores, one design library.** Your competitors `t-shirt-junky` and
  `love_tshirts` share 12% of design stems across storefronts. You have 7 buckets
  and a strict no-duplicates rule across all of them — that is the *stronger*
  position, but it means each store needs its own title padding so the same
  design does not read as a duplicate across accounts.
