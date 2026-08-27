# Rescuing the dead store — first priority

The store with the ~10M item / £10M value allowance that makes no sales.

---

## 1. You were forced into a false choice

Value ceiling £10,000,000, tee at £11.99:

| Config | Items/listing | £/listing | Max listings | Size filter |
|---|---|---|---|---|
| 10 sizes (3-4yrs…2XL) | 10 | £119.90 | 83,402 | works |
| **5 sizes (S,M,L,XL,2XL)** | **5** | **£59.95** | **166,805** | **works** |
| 4 sizes (M,L,XL,2XL) | 4 | £47.96 | 208,507 | works |
| Flat "One Size" | 1 | £11.99 | 834,028 | **dead** |

You went flat to buy listing headroom. But **five real sizes already gives you
166,805 listings** — far more than you need to prove the store works — and keeps
the size filter alive.

Going to One Size bought 5× more listings you did not need, and cost you every
size-filtered search. Clothing buyers filter by size constantly. That is the
whole trade, and it explains the single sale.

**Action: revert to 5 adult sizes.** S, M, L, XL, 2XL covers the overwhelming
majority of menswear demand. Drop kids sizes on this store.

---

## 2. But the ceiling was never the problem

```
10,000,000 listings  ×  0 conversion  =  0
```

Same arithmetic as day one. A store that converts at zero does not get better by
being given more listings. **Do not put 500,000 items on this store yet.** That
is the right target *after* it sells, not before.

---

## 3. The actual problem: cold start

eBay ranks on demonstrated performance. A listing with no sales has no signal, so
it sits at the bottom, so it gets no impressions, so it never gets a sale. That
loop does not break on its own.

Worse: a listing that gets **clicks but no sales settles into a low position that
is hard to escape without relisting**. Bad signal is stickier than no signal.

And here is the trap you are actually in — **spreading makes it permanent.** eBay
gives each listing a small exploration allocation of impressions. Split across
500,000 listings, every listing gets approximately nothing, so none of them ever
generates the data Cassini needs to rank them. **The catalogue size is what is
keeping the store invisible.**

> A big catalogue is a *reward* for a store that converts. It is a *handicap* for
> one that doesn't.

---

## 4. The plan — concentrate, then buy the first sales

### Phase A — Fix the structure (free, this week)

1. **5 real size variations**, not One Size.
2. **New titles** — the formula from `PLAN_GENERATION.md`, filled to 70–80 chars:
   ```
   {Subject Phrase} {Theme Keyword} Mens Womens T-Shirt Funny Novelty Gift Tee Top
   ```
3. **Fill every item specific.** They are the sidebar filters. A blank field means
   invisible to any buyer who filters on it. Size, Colour, Brand, Material,
   Department, Type, Sleeve Length, Neckline, Fit, Style, Occasion, Theme — all of
   them, every listing.

### Phase B — Cut the catalogue right down

Take this store to a **curated core of 3,000–5,000 listings.** Not 500,000.

Choose them by *demand*, not by what happens to exist:
- The slogan grid — 3,119 designs, built from joke frames measured across live
  competitor catalogues, so each one has an actual audience
- Black tees, so they cost **£0** to render
- Spread across the measured UK themes: biker, skull, Viking, funny, fishing,
  trades, music

End or archive the rest on this store. They are not earning; they are diluting.

### Phase C — Buy the first sales

**Promoted Listings at a 2–3% ad rate on the core, for a 2–4 week window.**

This is the standard tool for exactly this problem. You pay only when an item
sells, so a store with no sales risks nothing. The paid impressions feed clicks
and purchases back into Cassini's organic model — you are not renting rank, you
are manufacturing the signal the listing needs to earn rank.

Target: **a sale in the first week per listing cohort.** Listings that convert
early hold a stable position afterwards.

### Phase D — Only then scale

Measure at 30 days: which themes converted, at what sell-through. Clone the
*winning demand cluster*, not the winning image. Expand toward 166,805 — the real
ceiling at 5 sizes — one validated cohort at a time.

---

## 5. What this changes about the 500k-per-store target

Nothing, eventually. But the order matters:

| | Wrong order | Right order |
|---|---|---|
| 1 | Upload 500k | Fix structure + titles |
| 2 | Wait for sales | Cut to a 3–5k core |
| 3 | — | Promote, get first sales |
| 4 | — | Scale the winners to 166k |

Store 3's wall art is the cautionary tale: 424,134 listings, no sales. That was
not a volume shortfall.

---

## 6. Working method — CSV, no API

Confirmed: everything stays on File Exchange CSV. No API connection, no software
authorisation, nothing automated against the account.

The loop is:

```
you download the listing export  ->  I rewrite it  ->  you upload the Revise file
```

Revise keeps item age, watchers and search history. Warning rows still apply;
only `Failure` does not.

The out-of-stock restock problem we will handle separately later, also by CSV.

---

## 7. To start, send me

1. **The listing export for this store** — I will rewrite titles and rebuild the
   size variations in the same file format.
2. Confirmation of the **exact selling limit wording** from Seller Hub. Whether it
   is "items and value per month" or an active-listing cap changes how aggressive
   Phase B can be.
