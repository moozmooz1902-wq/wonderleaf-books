# Generation plan — 7 stores × 500k, cheapest route

Written after reading your handover pipeline and researching **bigboxart**
(118,000 sold, 99.8%, 5,900 followers) alongside the three stores from round 1.

---

## 1. What bigboxart proves

Their titles are as mechanical as the t-shirt sellers':

```
{Evocative Subject} {Style} Canvas Print Wall Art Home Decor Ready to Hang
 └── Birch Forest Rhythm ── Minimalist ──────────────────────────────────┘
```

Measured against your live titles:

| | bigboxart | Wonderleaf |
|---|---|---|
| Title length | **72.8** chars | 58.3 |
| Unused of 80 | 7.2 | **21.7** |
| Product / commercial words | **38.7 chars (53%)** | 15.0 chars (26%) |
| Price band | £22.95 – £44.95 | £8.99 |

**They spend over half the title on product and buyer language.** You spend a
quarter. Their tail alone — `Canvas Print Wall Art Home Decor Ready to Hang` —
is 45 characters; yours is `A4 Wall Art Print`, 17.

### The distinction that matters most

Both of you put a **style word** in the title. That is correct. The difference is
*which words*:

| bigboxart — heavily searched | Wonderleaf — near-zero search volume |
|---|---|
| Minimalist, Japandi, Scandinavian, Botanical, Mid-Century, Vintage, Modern, Coastal, Retro, Boho, Rustic, Art Deco | Kraft Poster, Muted Pastels, Terracotta, Ochre, Industrial Loft, Colour Field, Tachisme, Watercolour Loose |

**Including a style is right. Your specific vocabulary is what is wrong.** Your 30
DNA names were written to describe a rendering recipe to the generator; they were
never buyer search terms. Swap the *label* without touching the *recipe*.

### Their subject naming is evocative, not literal

`Birch Forest Rhythm` · `Songbird at Rest` · `Canyon Light and Shadow` ·
`Solitary Path in Autumn` · `Misty Valley Reflection`

versus yours: `Rugby Ball` · `Apple On Books` · `Scorpio Constellation`.

Theirs still contain the searchable noun (birch forest, songbird, canyon) but read
like a gallery title. Costs nothing to copy.

### Three grid series running inside their catalogue

- `Postcard from {place}` — Abu Dhabi, Maldives, Provence, Boston, Mallorca, Richmond Park
- `{animal} In A Suit` — Duck, Giraffe, Hedgehog, Stag, Monkey
- `{public-domain artist} {work}` — Audubon, Constable, Turner, Mucha, Waterhouse, Grimshaw, Ohara Koson

And the same design is listed as **Canvas**, **Framed** and **Set of 3** — 2–3
listings per image, exactly the multiplication the t-shirt sellers use on garments.

> ⚠️ They also list **Pablo Picasso** (died 1973 — in copyright until 2043). Do not
> copy that one. Audubon, Constable, Turner, Mucha, Waterhouse, Grimshaw and Ohara
> Koson are all safely public domain.

---

## 2. Why the personalisation-box store made one sale

You set `*C:Size = One Size` with a "type your size" box, to save listing quota.
Here is the problem:

**eBay's left sidebar has a Size filter, and clothing buyers use it constantly.**
A listing whose Size is `One Size` is excluded from every size-filtered search.
You did not just add friction — you removed the listing from the result set for
any shopper who picked a size.

Three further costs stack on top:

1. No `£X to £Y` range, so no price badge in the grid.
2. Typing a size is real friction versus picking from a dropdown.
3. "One Size" on a t-shirt reads as *might not fit me* — a trust problem.

**Fix:** on a quota-limited store, do not flatten sizes. Instead list **fewer
designs with full size variations**. Ten good listings with 10 sizes will beat 100
listings that no size filter can reach. If quota is genuinely binding, that store
should carry your *best* designs, not your most.

---

## 3. The new title formulas

**Wall art — canvas**
```
{Evocative Subject} {Searchable Style} Canvas Print Wall Art Home Decor Ready to Hang
```
**Wall art — unframed A4** (your Store 3 product)
```
{Evocative Subject} {Searchable Style} A4 Wall Art Print Poster Picture Home Decor
```
**Wall art — framed**
```
{Evocative Subject} {Searchable Style} Framed Wall Art Print Picture Home Decor Black Frame
```
**T-shirts**
```
{Subject Phrase} {Theme Keyword} Mens Womens T-Shirt Funny Novelty Gift Tee Top
```

Rules for all four:
- **Fill 70–80 characters.** Under 70 is wasted rank.
- Never repeat what the item specifics already say (`Black`, `100% Cotton`).
- Never claim `Canvas` or `Framed` on unframed paper.
- Fill the **Room** item specific — it is a sidebar filter.
- Add `Womens` where sizing honestly supports it. Your audit: currently 0%.

---

## 4. Cost — the honest numbers

Your own measurement: **440,000 designs in ~17 h on 6× RTX 4090 for ~$36**
= **$0.000082 per image**. That is already near-optimal; SDXL Lightning at 4 steps
is the cheapest credible setup.

Target: 7 stores × 500,000 = **3.5M listings**.

**You do not need 3.5M new images.** Two multipliers cut the requirement:

| Lever | Effect |
|---|---|
| Product multiplication (Canvas / Framed / A4 per design) | ÷3 on wall art |
| Slogan tees rendered as typography | £0 per design, CPU only |
| Retitling what is already live | £0, and it is your biggest win |

Rough build:

| Bucket | New images | Cost |
|---|---|---|
| Wall art delta (you already hold ~424k) | ~240,000 | **$20** |
| T-shirt graphics | ~1,500,000 | **$123** |
| Slogan tees (typography) | 0 | **£0** |
| Retitle entire live catalogue | 0 | **£0** |
| **Total GPU** | ~1.74M | **≈ $143** |

Plus R2 storage: ~1.74M JPEGs ≈ 350 GB ≈ **$5/month** (R2 has no egress fee —
keep using it).

**The whole 3.5M build is under $150 of compute.** Cost was never your problem.

---

## 5. Order of execution

### Phase 0 — Retitle (this week, £0, biggest return)
Download listing exports per store → run the retitle scripts → upload Revise files.
Wall art first: worst titles, 21.7 unused characters each, ~424k listings.
Keeps listing age, watchers and search history. Nothing relists.

*Blocker: `retitle_tees.py` is missing from the handover — send it or I rebuild it.*

### Phase 1 — Fix the generator (1 day, £0)
In `ebay_graphics.py` and the wall-art builder:
- Swap DNA labels → searchable style words (recipes unchanged)
- Delete `Ornithology` / `Herpetology` / `Entomology` from `FAMILY_EXTRA`
- `AUDIENCE = "Mens"` → `"Mens Womens"`
- Drop `Black 100% Cotton` from titles
- Add a **fill-to-70** pass
- Adopt the product-noun tails above
- Fix the `pick.py` ledger bug (a failed run still burns designs — it cost you 900,000)

### Phase 2 — Generate the delta (~$143, 2–3 days of GPU)
Only after Phase 1, so nothing new inherits the old titles.

### Phase 3 — New grids (ongoing, mostly free)
- Slogan tees — 3,119 built, expandable, £0 to render
- `Postcard from {place}` and `{animal} In A Suit` wall-art grids
- Public-domain masters — free subjects with standing search demand
- Symbol × render-treatment for illustrated tees

---

## 6. Store allocation

| Store | Product | Target | Source |
|---|---|---|---|
| 1–4 | Wall art (canvas / framed / A4) | 500k each | ~167k designs each × 3 product types |
| 5–7 | T-shirts | 500k each | SDXL graphics + slogan grid |

**One decision needed from you.** SPEC §8 forbids a design appearing twice *across*
stores. That is stricter than eBay requires and it triples your design bill. Your
competitors run one library across several storefronts. Options:

- **Keep the rule** — safest, needs ~3.5M unique designs
- **Relax across stores, keep it within a store** — a design may appear once per
  store with different title padding; cuts the design requirement by up to 7×

I would relax it and vary the titles, but it is your account risk, so it is your call.

---

## 7. What I still need

| | |
|---|---|
| Listing exports per store | to run Phase 0 |
| `retitle_tees.py` | named in SPEC §11, absent from the zip |
| Wall art frame sizes / colours / pricing | you said black frames — confirm sizes and prices |
| Mockup template PNGs | to composite properly |
| Store category IDs | `StoreCategory` blank in both pipelines |
| Paper gsm | for the description block |
