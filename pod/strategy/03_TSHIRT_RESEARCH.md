# 03 — T-shirt research: Amazon Merch, Redbubble, Etsy, TeePublic

## The t-shirt market is the inverse of the poster market

A poster is bought for a **wall**. A t-shirt is bought for a **person** — either
to declare something about yourself, or to give to someone whose identity you are
naming. That difference drives every rule below.

Two purchase modes, and they need different metadata:

| | **Self-expression** | **Gifting** |
|---|---|---|
| Trigger | Browsing, identity, humour | A date, a role, a relationship |
| Search | Vague / browse-led (Redbubble) | Precise and high-intent (Amazon, Etsy) |
| Phrase shape | "burnout shirt", "shoegaze aesthetic tee" | "gift for dachshund mom", "nurse graduation gift" |
| Timing | Flat | **Spikes — load 8–10 weeks early** |
| Platform fit | Redbubble, TeePublic | Amazon Merch, Etsy |

Gifting is where the money is on Amazon, and gifting searches contain the
relationship word — `mom`, `dad`, `nana`, `wife`, `coworker`, `bonus mom`. Our
generated titles have been describing the *design*; gift buyers search for the
*recipient*.

---

## Finding A: the specificity law

> "A design that speaks to French bulldog owners will always outsell a design
> that speaks to dog lovers in general."

Breed-specific, discipline-specific, and job-specific designs are reported to
outsell generic equivalents by an order of magnitude. Roughly 95% of POD designs
fail, and the named causes are: **zero keyword demand**, **oversaturation in a
generic niche**, or **wrong platform**. All three are demand-side failures, not
art failures.

The corollary is uncomfortable but useful:

> **A mediocre design in a hungry niche beats a beautiful design targeting
> nobody.**

Which is exactly why volume-without-demand fails: we were producing the second
kind at industrial scale.

## Finding B: the niche stack that actually converts

Ranked, with the specificity move for each:

| # | Niche | Generic (dead) | Specific (works) |
|---|---|---|---|
| 1 | **Occupation** — nurses lead, then teachers, firefighters, electricians, trades | "nurse life" | "ICU night shift nurse", "third year apprentice electrician" |
| 2 | **Pet breed** — golden retriever, dachshund, French bulldog | "dog mom" | "dachshund mom", "reactive dog owner" |
| 3 | **Humour / sarcasm** — self-buy *and* giftable | "funny shirt" | "I'm not arguing, I'm just explaining why I'm right" |
| 4 | **Family identity** — dad, mom, nana, bonus mom, step-dad | "best dad" | "bonus dad", "girl dad of three" |
| 5 | **Retro / vintage aesthetic** — distressed, faded, 70s–80s type | "vintage shirt" | "1978 bass tournament", "retro sunset national park" |
| 6 | **Hobby** — hiking, fishing, yoga, bouldering, keyboards, tabletop | "hiking" | "trad climbing", "fly tying", "mechanical keyboard enthusiast" |
| 7 | **State / regional pride** — TX, TN, CO, the South | "USA" | "Appalachian Trail section hiker" |
| 8 | **Motivational / mindset** — fitness-adjacent | "be positive" | "do hard things", "zone 2 only" |
| 9 | **Social statement** — keep it non-divisive | political slogans | "support your local farmer" |
| 10 | **Seasonal / holiday** | generic Christmas | "first Christmas as a nana" |

Redbubble adds four of its own, driven by its younger audience: **mental health &
neurodivergence** (sincere, specific, original wording — not the slogan everyone
has done), **music-scene aesthetics without band names**, **meme/insider
humour**, and **activism/identity**.

**Style direction for 2026:** retro sports and varsity graphics with distressed
typography are growing month-over-month (football, basketball, baseball, with
soccer surging). The broader aesthetic sweet spot sits between Y2K and 90s
references — pixel art, loading-screen iconography, chunky serif type, early
internet visual language. Ironic "fake brand" apparel and anti-design are working
specifically *because* they read as the opposite of generic AI output.

## Finding C: text still dominates, but flat text is dying

Text-based shirts continue to dominate Amazon Merch — fast to make, easy to niche
down, broad demographic reach. **But flat generic quote shirts are losing ground
to designs with strong typographic personality.** The differentiator is no longer
*having* a phrase; it is the **lockup** — how the phrase is set, stacked, arched,
distressed, and paired with a mark.

This is precisely where our generated data has been weakest: we generate
*phrases* and leave the layout to chance. A phrase without a specified lockup
returns the mean, which is centred Impact-adjacent text on a blank tee.

**Fix:** every t-shirt concept must name a **layout archetype** from
[`../data/tshirt_layout_archetypes.json`](../data/tshirt_layout_archetypes.json)
— 14 named lockups with slot structure, type rules, and colour rules.

## Finding D: vintage is the durable baseline

Vintage-styled tees hold a steady sales floor that other aesthetics don't reach,
because they're insulated from the trend cycle that dates a modern design within
a year. The mechanics that make it read as vintage:

- **Muted, faded palette** — never pure black on pure white; use off-blacks
  (`#2B2B28`), creams (`#EFE7D5`), rusts, mustards, sage.
- **Distress texture** breaking up solid ink areas — the look of a garment washed
  a hundred times. Applied *on top of* the art, not as a filter over everything.
- **Era-committed typography** — a 70s slab, an 80s outline script, a 90s bold
  condensed. Not "vintage in general".
- **Limited ink count** — 2–4 colours, like a real screen print.
- **The winning formula is a hybrid**: a period layout carrying a modern message.

## Finding E: production reality of DTG

- **4500 × 5400 px, 300 DPI, transparent PNG, sRGB, ≤25 MB.** This covers Amazon
  Merch, Printify, Printful, and most others.
- A white background exports as a **printed white rectangle** on the garment.
  Transparency is not optional.
- **Design for both light and dark garments.** Either export two versions, or
  build a palette that survives both. A design that only works on white halves
  your garment options and your colour-variant sales.
- **No hairlines, no thin outlines, no subtle gradients.** DTG fills in fine
  detail and bands soft gradients.
- **Maximum 2–3 complementary type families**, and everything must read at
  thumbnail size — see the thumbnail law in `00_DIAGNOSIS.md`.
- Test the composition against a **250px thumbnail** and against **both** a white
  and a black garment mock before shipping.

## Finding F: text is the highest trademark risk in the catalogue

Text-based designs carry trademark risk that sellers routinely overlook. A short
phrase can be registered as a mark, and putting it on a shirt is *use in
commerce*. Character names, franchise names, band names, logos, album art and
lyrics are all protected.

The doctrine that keeps you selling: **design the vibe, never the name.**
"Retro JRPG energy", "soulslike difficulty humour", "90s shoegaze",
"underground techno", "cozy farming-sim aesthetic" — all capture the audience
without a protected string. Full rules in `05_IP_SAFETY.md`.

## Portfolio math, honestly stated

The commonly cited target is roughly **200+ designs each earning about $20/month**.
That is a real model, but note what it assumes: 200 designs that each *have a
demand anchor*. It is not 200,000 designs that don't. The multiplier only ever
applies to a per-listing expectation greater than zero.

---

**Generator-ready data:**
[`../data/tshirt_layout_archetypes.json`](../data/tshirt_layout_archetypes.json) ·
[`../data/tshirt_niches.json`](../data/tshirt_niches.json) ·
[`../data/palettes.json`](../data/palettes.json)
