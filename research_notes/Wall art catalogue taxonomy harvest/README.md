# Wall art — start here

Everything learned about the wall-art market, in reading order. Written so a
session that has never seen this conversation can pick it up cold.

**The corpus**: 1,463,031 competitor listings from three MEGA folders the
seller supplied (Displate 500,093 · an "800k raw art" set 665,026 · Fy! 297,912
split one file per collection), plus 168 live images looked at one at a time,
plus 6,918 collection records pulled from five retailers' Shopify endpoints.

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
3. **`template_catalogue.md`** — the twenty phrasings their catalogues run on,
   with the slot values extracted from the full corpus. Generator input.
4. **`competitor_data_analysis.md`** — subject blocks by volume, the UK
   coverage gap, licensed IP to avoid, generation cost model.
5. **`uk_place_gazetteer.md`** — ~7,000 named UK place atoms from official
   registries, and which place formats a diffusion model can actually carry.

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
5. **No sales data exists anywhere in this corpus.** "What sells" throughout
   these notes means listing volume — what a competitor chose to make, not what
   a buyer bought. Supply is being read as demand. The seller's own eBay
   figures would settle it and nothing here replaces them.

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
designs for about $7 of GPU.

Blockers before anything can be listed: **no R2 bucket for wall art**
(`plan.json` has `pic_base: ""`, only `tshirt-m12k` has credentials).

Scripts to reproduce any of this are in `../../wallart-data/`.
