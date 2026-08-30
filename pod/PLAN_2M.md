# Getting to 2,000,000 listings

Research done 30 Aug 2026. Everything below is measured, not assumed —
sources at the end.

## The short version

Generation is not the constraint. **Selling limit is**, and the honest
ceiling on *distinct* products is about 150,000. 2,000,000 listings is
reachable, but only one of these two ways:

| Route | What it costs |
|---|---|
| **A4 only, £4.99, one size** | Exactly £10.0M of limit — one whole store, and no size dropdown |
| **Five sizes** | £89.9M of limit. You do not have that, and will not get it |
| **13.6 copies of every product** | The failure we just spent a week diagnosing |

So the real question is not "can we make 2 million images". It is
**"what is the largest number of listings that can each still sell?"**

My answer: **~1,030,000** — 147,000 distinct products across 7 stores, with
every store holding a complete catalogue and no duplicates inside any store.
Then grow the subject banks, not the style grid, to go further.

## Why 2M cannot be 2M distinct products

Only three things make two listings genuinely different to a buyer: a
different **subject**, a different **style**, and — for wall art only — a
different **palette**. Everything else is the same product with the words
rearranged, which is what eBay clusters and suppresses.

Counting what exists, generously:

| Bank | Subjects | Styles | Products |
|---|---|---|---|
| UK places | 4,469 | 8 | 35,752 |
| World cities | 1,500 | 8 | 12,000 |
| Countries & maps | 300 | 8 | 2,400 |
| Landmarks | 800 | 6 | 4,800 |
| Wildlife | 1,100 | 10 | 11,000 |
| Dog & cat breeds | 250 | 10 | 2,500 |
| Botanical | 900 | 10 | 9,000 |
| Food & drink | 500 | 8 | 4,000 |
| Sport & hobby | 600 | 8 | 4,800 |
| Music | 250 | 8 | 2,000 |
| Vehicles | 400 | 8 | 3,200 |
| Space | 150 | 8 | 1,200 |
| Myth & folklore | 300 | 8 | 2,400 |
| Abstract & pattern | 300 | 6 | 1,800 |
| **Wall art** | | | **96,852** |
| T-shirts (already built) | | | 50,740 |
| **Total** | | | **147,592** |

2,000,000 ÷ 147,592 = **13.6 copies of every single product**. That is the
424,117-listings-for-43,483-products shape that made the wall art store
worthless. Do not rebuild it.

## The route to ~1,030,000

**147,592 products × 7 stores.** Each store carries the full catalogue.
Inside any one store there is not a single duplicate — which is the only
place duplication is actually punished.

Same product in seven stores is not seven identical listings, because each
store renders its own version:

- its own generation seed, so the picture differs
- its own palette rotation
- its own title frame from a per-store set
- its own price point

The buyer searching "Whitby harbour print" sees seven different pictures
from seven different sellers. That is a normal search result page, not a
flood — and it is the only way a seven-store operation reaches seven
figures without the stores looking like copies of each other.

## Going beyond that: widen the subjects, never the styles

The instinct is to add more styles. Resist it. Style 9 of a lion competes
with styles 1–8 of the same lion, in the same search, from the same seller.

**Subjects are what scale, and UK places are the proof.**

    "wall art print a4"      3,900,000 competing listings
    "hebden bridge print"          201 competing listings

Hebden Bridge has 4,500 residents and supports a market at £6–£35, from
several sellers. That is the whole thesis: a listing nobody else has made
beats a listing competing with 3.9 million others, even when the search
volume is tiny — because the marginal cost of holding it is a slot in a
limit you are not using.

`pod/ebay/data/uk_places.json` is built and committed: **4,469 UK places**,
each with county and country, from GeoNames (population ≥1,000 or an
administrative seat, which catches real towns GeoNames has no population
for). Nearly all carry a county, so titles can disambiguate the seventeen
Newtons.

Where the subject axis goes next, in order of expected return:

1. **UK places → 12,000** by dropping to population ≥250 and adding
   villages in national parks and on the coast, which sell on identity and
   tourism rather than population.
2. **Streets, districts, postcodes** of the 40 largest cities. "Chorlton",
   "Jesmond", "Kelvinside" — people buy the bit of the city they live in.
3. **World cities → 4,000**, weighted to where British people holiday and
   emigrate.
4. **Named walks, peaks, beaches, rivers, castles, lighthouses, piers,
   football grounds by town** (the ground, not the club — see IP note).

That reaches roughly 25,000 place subjects, which at 8 styles is 200,000
products, and takes the total past 250,000 — 1.75M listings across seven
stores, without a single style being reused more than it already is.

## What it costs to build

| | |
|---|---|
| SDXL Lightning, 4 steps, 1024px | ~1.0 s/image on a 4090 |
| 1,030,000 images | ~290 GPU-hours |
| At RunPod 4090 spot (~£0.30/hr) | **~£90** |
| Across 8 pods | about 36 hours |
| Storage: masters + mockups at ~600KB | ~620 GB in R2, ~£8/month |

Print files are **not** stored. `order.py` already builds them on demand
from the 1024px master when an order comes in, which is why 141,000 designs
never became 400 GB of files. Keep that.

Generation is cheap. The expensive resource is selling limit, and the
scarce one is genuinely distinct demand.

## The size decision, which changes everything

Wall art buyers filter by size — A5/A4/A3/A2/A1 is how the whole category
is sold, and every competitor listing found in the research offers a range.
But sizes multiply limit consumption:

| Listings | Sizes | Limit used |
|---|---|---|
| 1,030,000 | 1 (A4, £4.99) | £5.1M |
| 1,030,000 | 3 (£8.99) | £27.8M |
| 1,030,000 | 5 (£8.99) | £46.3M |

Across seven stores £27.8M is affordable if the limits are spread; £46.3M
probably is not. **Three sizes (A4/A3/A2) is the recommendation** — it keeps
the listing inside size-filtered search, which A4-only is excluded from,
at 55% of the cost of five.

This needs your real per-store limits before it can be settled.

## Order of work

1. **Confirm the numbers above against your actual limits** — seven stores,
   what each will carry. Everything else follows from that.
2. **Finish the subject banks** — places are done; wildlife, botanical,
   landmarks, food and drink next. These are data, not code, and they are
   what the whole catalogue is made of.
3. **Style grid** — 8 styles, each a locked prompt fragment and a locked
   palette set, so "art deco" means the same thing in every listing and a
   buyer who liked one can find the others.
4. **Title grammar per bank** — `[subject] [style] [room] wall art print
   A4 A3 A2` filled to 75–80 characters with the words buyers type. The
   t-shirt work already proved this out.
5. **Generate one store, list it, measure.** 147,000 listings in one store
   is a real experiment; 1,030,000 across seven before any of it has sold
   is not.

## Standing rules this must respect

- **DTF for anything printed on garments** — solid ink, see CLAUDE.md.
  Wall art is inkjet on paper and is not bound by the opacity rule, but the
  0.5 mm minimum-detail rule still applies to anything that goes on a tee.
- **Shuffle on upload.** The spread in `build_tee_csv.py` is the reference:
  a plain shuffle left 18.9% of listings next to one from the same theme.
- **No titles claiming Canvas, Framed or Ready to Hang** on unframed A4.
- **IP.** Football grounds yes, club names and badges no. Landmarks yes,
  living architects' recent buildings no. No film, TV, game or music
  franchise subjects — that is what got the earlier banks trimmed.

## Sources

- eBay UK search, "wall art print a4" — 3,900,000 results
- eBay UK search, "hebden bridge print" — 201 results
- eBay UK search, "city skyline wall art print" — style and price sampling
- eBay UK store bigboxart — 118,000 sold; title grammar reference
- GeoNames GB dump, 30 Aug 2026 — 43,712 populated places, 4,469 usable
