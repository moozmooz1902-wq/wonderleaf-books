# Wall art — start here

Everything learned about the wall-art market, in reading order. Written so a
session that has never seen this conversation can pick it up cold.

**The corpus**: 1,463,031 competitor listings from three MEGA folders the
seller supplied (Displate 500,093 · an "800k raw art" set 665,026 · Fy! 297,912
split one file per collection), plus 168 live images looked at one at a time,
plus 6,918 collection records pulled from five retailers' Shopify endpoints.

Then harvested live and directly: **9,165,241 images** — the complete Fy!
catalogue (6,448,043, with 3,582,363 titles) and the complete Displate
catalogue (2,717,198, no titles in its sitemaps) — plus **34,789 real Displate
search queries**, 105,844 artist collection slugs and Displate's 191 licensed
brands as a compliance negative-list.

**Language**: the corpus is **>99% English**. Latin-accented characters appear
in 0.31% of titles and every non-Latin script together totals under 240
listings. There is no multilingual problem to solve.

---

## Read in this order

1. **`../../reports/Wall art generation plan.md`** — the build plan. Phases,
   arithmetic, costs, what to generate first.
2. **`the_grammar_of_what_sells.md`** — how a selling picture is actually
   built. Eleven composition grammars, three colour strategies, eleven
   techniques named by their physical artefact. From looking at the images.
3. **`subject_technique_pairings.md`** — which technique goes with which
   subject, measured by lift across the whole corpus. The lookup table that
   removes guesswork from prompt building.
4. **`template_catalogue.md`** — the twenty phrasings their catalogues run on,
   with the slot values extracted from the full corpus. Generator input.
5. **`competitor_data_analysis.md`** — subject blocks by volume, the UK
   coverage gap, licensed IP to avoid, generation cost model.
6. **`uk_place_gazetteer.md`** — ~7,000 named UK place atoms from official
   registries, and which place formats a diffusion model can actually carry.
7. **`live_catalogue_6_4m.md`** — the full live Fy! catalogue, 6,448,043
   images, and the 83% repeat rate inside it.
8. **`displate_catalogue_and_demand.md`** — Displate's full 2,717,198 images,
   and 34,789 real search queries. Displate's audience is fandom, not decor.
9. **`seller_data_structure_and_frames.md`** — the seller's own three MEGA
   dumps read column by column: the black/white/oak frame set, the price
   ladder, the exact mockup geometry, and which competitor to copy.
10. **`first_party_demand_watchers.md`** — **read this one.** The seller's own
   eBay export has a Watchers column. It is the only first-party demand signal
   in the project: what gets saved, what never does, and the 7.5x result for
   UK places.

Supporting, read as needed: `live_image_style_analysis.md` (the earlier
156-image pass), `enumerable_subject_lists.md` (species, breeds, plants,
constellations), `art_movement_style_vocabulary.md` (movements with the
copyright cut), `flux_generation_engineering.md` (schnell settings, upscaling,
dedup), `shopify_collection_axes.md` + `collections_raw.json` (6,918 live
collections), `etsy_ebay_taxonomy.md`, `european_uk_retailer_taxonomy.md`,
`pod_marketplace_taxonomy.md`, `browser_harvest_firsthand.md`.

---

## The five things that matter most

1. **Their catalogues are template-generated and the templates are shallow.**
   `Travel Poster For {CITY}` covers 103 cities in 1.46M listings and Liverpool
   is the only UK one. `Painting Of {CITY} With A Cat` runs ~100 variants per
   city across ~20 cities, London the only British one. `Linocut Of {UK beach}`
   exists seven times.
2. **The UK is the gap.** Chicago alone has 2,088 listings — more than
   Manchester, Liverpool, Birmingham, Bristol, Brighton, Newcastle and Leeds
   combined. Edmonton and Winnipeg have more skyline listings than almost any
   British city outside London.
3. **Generate the picture, composite the type.** A third of their images carry
   lettering and FLUX cannot be trusted with it. The repo already has a
   typography renderer that draws type to an asserted size contract.
   Consequence: **near-duplicate checking must run on the picture, not the
   title** — the same panel with different words is still a duplicate.
4. **The hard-edge geometric block should be drawn with code, not generated.**
   Circles, arcs, a horizon split, three flat colours — 9.12% of the corpus,
   122,958 listings. Procedural output is free, instant and pixel-perfect;
   diffusion would be slower, dearer and worse.
5. **Still no sales data — but there is now first-party demand data, and it
   backs the UK plan.** "What sells" in the older notes means listing
   volume: what a competitor chose to make, not what a buyer bought. That
   caveat stands for every supply-derived number here. What changed is that
   Displate publishes 34,789 of its real search queries, and those are demand.
   They say Displate's buyers search for **named entities** — characters,
   actors, bands, game and anime titles (91.2% of queries) — not decor, and
   that UK place names are 0.25% of its queries. But Displate's audience is
   not eBay UK's, and the seller's own eBay export settles it the other way:
   UK-place listings are watched at **7.91% against a 1.05% base (z = +12.6)**
   on just 354 listings out of 168,819. Phase 1 now has first-party evidence
   behind it. Sales data still does not exist anywhere; watchers are the
   closest thing, and a save is not a purchase.

---

## Rules for anything we generate

- No gradients. Flat fill, contour line or hatching. A smooth airbrushed
  gradient is the clearest tell of cheap generated work.
- Detail gradient: the subject is the only sharp thing, the environment flat.
  That is what makes a design read at thumbnail size, which is the size the
  buying decision is made at.
- Line goes over mass, never under.
- Subjects bottom-anchored and cropped by the lower edge.
- Reject any output containing legible text, a signature or a watermark-like
  mark. Three sampled images carried a painted artist signature; the OCR gate
  is a confirmed necessity, not a precaution.
- Never generate: characters and franchises, logos and club crests, celebrity
  likeness, **royal insignia (criminal under s.99 Trade Marks Act 1994)**,
  recognisable branded objects, or any artist dead less than 70 years —
  Warhol, Picasso, Dalí, Miró, Hockney, Pollock, Kusama, Basquiat. Artists
  dead before 1956 are clear: Van Gogh, Monet, Klimt, Hokusai, Mucha, Morris,
  Cézanne, Matisse, Ohara Koson.
- Name a movement or a long-dead artist, never a living one — their own safe
  device is "Inspired By Cézanne", "In The Style Of Ukiyo-e".

## Do not copy from their data

- `aihrgdesign` is a vendor name that appears as a **slot value** 1,628 times
  and opens 6,874 titles. `nissan` appears 169 times inside the skyline
  template. Their slot lists need filtering before use.
- Roughly 90,000 of their titles are truncated mid-word (`art prin`, `art pri`,
  `art pr`) by a builder that trimmed to 80 characters without respecting word
  boundaries.
- 45% of their subject phrases are duplicates of each other.
- Every Displate row carries identical item specifics — Style "Modern", Room
  "Living Room, Bedroom", Colour "Colorful", Pattern "Abstract" on all 500,093
  — so eBay's own filters are useless for every one of those listings.

## State of play

Research complete. **Nothing generated yet.** Phase 1 is scoped to the nine
lettering-free place formats: ~5,900 UK place atoms × 3 treatments = 17,700
designs for about $7 of GPU — and it is no longer a blind bet: the seller's
own watchers put UK places at 7.5x the catalogue's base rate off only 354
listings. See `first_party_demand_watchers.md`.

Blockers before anything can be listed: **no R2 bucket for wall art**
(`plan.json` has `pic_base: ""`, only `tshirt-m12k` has credentials).

Scripts to reproduce any of this are in `../../wallart-data/`.
