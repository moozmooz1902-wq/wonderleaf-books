# UK wall-art market, eBay UK, and the UK-focused retailers (Fy!, Abstract House, Olive et Oriel, Desenio UK, King & McGaw)

**Scope note on method and source quality (read first).** Direct access to the
highest-value primary sources was blocked during this research:

- `ebay.co.uk` category pages, search pages and sold/completed-listing pages returned **HTTP 403** to both WebFetch and curl with a browser user-agent. No first-hand eBay UK sold-price or sold-volume data could be captured. Everything below about eBay UK is from search-engine snippets of eBay UK pages, or from a seller's own site — treated as weaker evidence and labelled as such.
- `desenio.co.uk` returned **HTTP 429** (rate-limited) on every attempt; no Desenio UK price ladder was captured first-hand.
- `kingandmcgaw.com` returned **HTTP 403**; King & McGaw pricing below is from search snippets only, and one snippet quoted **USD** prices, implying the snippet came from their US storefront. Flagged inline.
- Fy!'s bestseller collection URL 404'd; the general art-prints listing page was captured successfully and is the stronger Fy! evidence.

Market-size figures come from commercial market-research vendors (Grand View,
IMARC, Technavio). These are **modelled estimates, not measured sales**, and
different vendors disagree materially. They are useful for order of magnitude
only. Several wall-art "trend" pages that rank well in search
(aboutwallart.com, musaartgallery.com, hdlondonart.com, trowbridgegallery.com,
accio.com) are **retailer/SEO content marketing**, not independent research —
flagged wherever cited.

---

## What sells on eBay UK in wall art / posters / prints: category structure, price points, highest-volume sellers, listing titles

### Takeaway

eBay UK's wall-art demand is concentrated in **mass-market canvas prints** —
abstract swirls, florals, skylines and world maps, sold heavily as **sets of
three**, keyed to a **colour-plus-room** formula (teal, mustard, blush pink,
navy, grey × living room/bedroom) rather than to artists or art movements.
Listing titles on the highest-volume UK sellers are keyword-stuffed strings in
a repeatable order: *colour → room → subject → "Canvas Wall Art" → format/size
→ internal SKU*. No first-hand sold-price or sold-volume data could be obtained
because eBay UK blocked automated access.

### Cited Findings

**Category structure**

- eBay's numeric category **360 is "Art Prints"**, sitting under *Art* (category 550), in the "Art from Dealers & Resellers" area. — [eBay UK Art Prints category](https://www.ebay.co.uk/t/Art-Prints/360/bn_16566819); category-ID context from [eBay category-change notice](https://pages.ebay.com/as/en-us/categorychanges/art.html)
- Distinct eBay UK browse nodes exist for, at minimum: **Pictures And Prints** (`bn_7023612369`), **Art Prints** (`bn_16566819`), **Framed Wall Pictures** within Art Prints (`bn_7022893553`), **Set Of Prints** (`bn_7023600434`), **Canvas Art Prints** (`bn_86050393`), **Art Wall Hangings** (`bn_12090053`), **Art Paintings** (`bn_7204697`), plus keyword-derived nodes "wall art painting" (`bn_7024835363`) and "large wall painting" (`bn_7024747434`). — [eBay UK browse nodes as returned in search results](https://www.ebay.co.uk/b/bn_7023612369)
- The existence of a dedicated **"Set Of Prints"** browse node on eBay UK is itself evidence that multi-panel sets are a first-class demand pattern there, not a niche. — [eBay UK Set Of Prints](https://www.ebay.co.uk/b/bn_7023600434)
- **Important caveat on category 360:** the CLAUDE.md in this repo records wall art as eBay category **360**. That matches "Art Prints" above. But eBay UK also routes large volumes of this product through **Home, Furniture & DIY → Home Décor → Wall Décor** style nodes (the `bn_7024835363` / `bn_7024747434` keyword nodes and "Art Wall Hangings" point that way). I could not confirm the exact leaf-category IDs used by the high-volume UK sellers because listing pages were 403-blocked. **This needs verifying from a real listing before upload.**

**What is featured / described as best-selling**

- In eBay UK's **Pictures and Prints** category, floral wall art appears among the featured/best-selling items, with titles such as *"Le Reve Floral Rose Wall Art"* and *"LR Floral Rose Wall Art Canvas Flowers Picture"*. — [eBay UK Pictures And Prints](https://www.ebay.co.uk/b/bn_7023612369)
- In eBay UK's **Canvas Art Prints** category, abstract wall art leads, e.g. *"Wallfillers 1357 Abstract Wall Art Painting Print Canvas"*. — [eBay UK Canvas Art Prints](https://www.ebay.co.uk/b/bn_86050393)
- A commercial sourcing blog claims top-selling art on eBay in 2025 includes DIY craft kits, abstract wall art and "iconic reprints", with growing demand for 3D textures and "luxury looks at mid-range prices", plus ready-to-hang as a purchase driver. — [Accio](https://www.accio.com/business/top-selling-art-on-ebay) — **weak source: vendor-sourcing SEO content, no methodology, not UK-specific.**

**Highest-volume UK seller observed: Wallfillers**

- Wallfillers' eBay UK store is reported at **98.6% positive feedback and 51,000 items sold**. — [Wallfillers eBay UK store](https://www.ebay.co.uk/str/wallfillers-canvas) (figures via search snippet; store page not directly fetchable)
- Verbatim Wallfillers eBay UK listing titles captured:
  - *Set of 3 Teal Canvas Wall Art Prints UK Living Bed Room Pictures 3033*
  - *Set of 3 Piece Red Canvas Wall Art Pictures UK Sunset Living Room 3001*
  - *Blush Pink Grey Black Canvas Wall Art - Trees Leaves Blossom - Set of 2 Pictures*
  - *Large Orange Grey Map of World Atlas Canvas Wall Art Print - Multi 3 Set - 3304*
  - *London Skyline Canvas Wall Art Print - 17 Colours Available - 94cm wide*
  - *Navy Blue and Grey Swirl Living Room Canvas Wall Art - Abstract Print*
  - *Mustard Yellow and Grey Swirl Bedroom Canvas Wall Art - Abstract Print*
  — [Wallfillers eBay UK store](https://www.ebay.co.uk/str/wallfillers-canvas)
- Wallfillers' own site positions on **"Extra Large - Wall Art - Prints - Framed Canvas - XXL Pictures"** and organises navigation by: New, Best Sellers, **XXL Oversized**, **Sets of 3**, artist collections (Van Gogh, Monet, Kandinsky), style filters (Abstract, Floral, Geometric) and colour filters (Blue, Green, Pink). — [Wallfillers](https://wallfillers.co.uk/) and [Wallfillers best sellers](https://wallfillers.co.uk/collections/best-sellers) (product tiles/prices were truncated and could not be read)
- A second high-volume eBay UK wall-art store observed in results: **"CANVAS ART SHOP ONLINE"**. — [eBay UK store](https://www.ebay.co.uk/str/canvasartshoponline)

### Inferences

- **The title formula is the main transferable finding.** Wallfillers' titles follow a consistent, learnable grammar: `[Set of N] + [colour 1] [colour 2] + [room] + [subject] + "Canvas Wall Art" + [Print/Pictures] + [size or colour-count] + [numeric SKU]`. The word "UK" is inserted into titles (e.g. "Prints UK Living Bed Room") — almost certainly for eBay search matching against UK-qualified queries, not for description. Any catalogue generated here should mimic this grammar for eBay UK rather than using gallery-style titles.
- **Colour is the primary buying axis on eBay UK, subject is secondary.** Titles lead with colour pairs (teal; red; blush pink/grey/black; orange/grey; navy/grey; mustard/grey) and the same base artwork is sold in "17 Colours Available". This implies eBay UK buyers shop to match an existing room scheme. Generating one strong composition in many colourways is the structurally correct play for eBay UK — but this collides directly with the **89% near-duplication risk recorded in CLAUDE.md**. The distinction that matters: *deliberate colourway variants of one design on one listing* (Wallfillers' approach — one listing, 17 colours) is not the same as *many near-identical separate listings*. Recommend variant-on-one-listing, not variant-as-new-listing.
- **Sets of 2 and 3 are disproportionately important on eBay UK** relative to the single-print model used by Fy!/Desenio. eBay has a dedicated browse node for it and the top seller's navigation has "Sets of 3" as a top-level item.
- Since the single UK example with a named subject is *London Skyline*, and world/atlas maps appear twice, geographic subjects appear to work on eBay UK — see the UK-subject section below.

### Gaps

- **No sold-listing data at all.** eBay UK 403'd WebFetch and curl, so typical realised price, sell-through rate, and sold-volume-by-subcategory are entirely unevidenced. This is the single biggest hole in these notes. Getting it will require a real browser session, the eBay Browse/Marketplace Insights API, or a third-party tool (Terapeak via an eBay seller account — Terapeak is the native source for UK sold data and the account already exists per `tshirt/ACCESS.md`).
- **No eBay UK price points captured.** I could not retrieve a single GBP price from eBay UK. Do not assume the retailer prices below transfer to eBay; eBay UK canvas is a visibly lower-price channel than Abstract House or King & McGaw.
- Could not confirm the exact leaf category ID(s) the volume sellers list in, nor whether 360 or a Home Décor node converts better.
- No data on eBay UK listing-level conversion rates, impressions or click-through.

---

## Fy! (iamfy.co): bestselling prints, subjects and styles

### Takeaway

Fy! is a London-founded (2014) independent-artist marketplace carrying
**~25,000 art prints**, priced at roughly **£19.95–£46.95** for prints, and it
merchandises almost entirely on **style / room / subject** taxonomies rather
than artist names. Its front-of-house product skews **illustrative, witty,
music- and book-themed** — i.e. gift-driven rather than interior-matching.

### Cited Findings

- Fy! lists **25,001 art prints** and offers canvas prints, framed prints and posters. — [Fy! art prints](https://iamfy.co/collections/art-prints)
- Price points observed on the art-prints listing (GBP, ranges reflect size tiers):
  - *What's The Best That Could Happen* — The 13 Prints — £19.95–£35.95
  - *Fairytale Of New York, The Pogues* — Indieprints — £19.95–£35.95
  - *Nothing Is Under Control* — Cosmo Illustrator — £27.95–£46.95
  - *Dream of Flowers. Gustav Klimt Style* — alenaganzhela — £19.95–£35.95
  - *Bookworm* — Flow Line — £19.95–£35.95
  — [Fy! art prints](https://iamfy.co/collections/art-prints)
- Fy!'s **style taxonomy**: Maximalist, Cottage Core, Modern, Scandinavian, Art Deco, Bohemian, Abstract, Industrial, Coastal. — [Fy!](https://iamfy.co/collections/art-prints)
- Fy!'s **room taxonomy**: Living Room, Bedroom, Home Office, Kitchen, Hallway, Bathroom, Kids' Room. — [Fy!](https://iamfy.co/collections/art-prints)
- Fy!'s **subject taxonomy**: Music, Vintage, Film, Flowers, Animals, Travel, Food & Drink, Botanical. — [Fy!](https://iamfy.co/collections/art-prints)
- Fy! offers a native **"Best selling"** sort, alongside featured, most relevant, A–Z and price sorts. — [Fy!](https://iamfy.co/collections/art-prints)
- Fy! was running **40% off all art**, free shipping over £59, free returns, at time of capture (Oct 2026). — [Fy!](https://iamfy.co/collections/art-prints)
- Fy! is UK-based, founded 2014 in London, focused on independent artists; rated **4.4 from 1,886 reviews**, >87% on-time delivery, >93% accurate-and-undamaged orders, ~5-day average delivery. — [Reviews.io Fy! store reviews](https://www.reviews.io/company-reviews/store/fy/EJ); company background also at [CB Insights](https://www.cbinsights.com/compare/digiposter-vs-fy)
- Fy! Trustpilot presence confirms UK/IE trading. — [Trustpilot iamfy.co](https://www.trustpilot.com/review/iamfy.co?page=7)

### Inferences

- **Fy!'s £19.95 entry / £35.95–£46.95 top is the realistic UK online price corridor for an unframed-to-framed independent-artist print.** It is roughly 3–5× an eBay UK poster and roughly 1/5 of Abstract House. That three-tier structure (eBay mass-market canvas < Fy!-style marketplace < Abstract House / King & McGaw premium) is the clearest pricing map I could establish for the UK.
- The products surfaced first — a Pogues *Fairytale Of New York* lyric print, two humorous typographic prints, a *Bookworm* print, and a "Klimt Style" pastiche — suggest Fy!'s merchandising engine favours **music, humour and literary identity** over pure decor. These are **gift** purchases keyed to a recipient's taste, not room purchases.
- The "Klimt Style" title is notable: it signals Fy! tolerates and surfaces **style-of-a-famous-artist** generated work. That is a directly relevant precedent for a generated catalogue, though *Fairytale Of New York* also shows Fy! carries work trading on named copyrighted songs — a licensing risk this project should not copy.
- Fy!'s nine-way style taxonomy and seven-way room taxonomy are effectively a **ready-made prompt matrix** (9 styles × 7 rooms × 8 subjects) validated by a real UK marketplace's own merchandising.

### Gaps

- `iamfy.co/collections/bestsellers` and `/best-sellers` both 404'd. The five products listed above are from the **default sort** of the general art-prints collection, **not** a confirmed bestseller ranking. Do not report them as "Fy!'s bestsellers" — report them as "products Fy! surfaces first".
- No Fy! revenue, order-volume or category-mix data found.
- No evidence on which of Fy!'s nine styles actually sells best.

---

## Abstract House: positioning and pricing

### Takeaway

Abstract House is the **premium end** of the UK online wall-art market —
London studio, handcrafted framing, **£115–£774** observed, 50×50cm to
100×100cm — and it merchandises by **colour** as a first-class axis alongside
subject, with "Set of Three", "Gallery Walls & Sets" and "Large Canvas" as
named collections.

### Cited Findings

- Observed bestseller prices (GBP): *Swan In Flight Art Print* 50×50cm **£115**; *Monopoly Canvas Art* 100×100cm **£325**; *Chronological Abstraction Gallery Wall Art* **£774**; *Abstract Paradigm III Canvas Art* 50×70cm **from £175**; *The Morning After Canvas Art* 50×70cm **from £175**; *Contemporary Study I Canvas Art* 70×100cm **from £245**. — [Abstract House](https://www.abstracthouse.com/)
- Style/subject collections: Abstract, Botanical, Geometric, Cityscape, Fine Art Photography, Landscape, Figurative. — [Abstract House](https://www.abstracthouse.com/)
- **Colour collections** are a primary navigation axis: Blue, Brown, Green, Black & White, **Neutral Palette**, Red, Vibrant Colours, Yellow. — [Abstract House](https://www.abstracthouse.com/)
- Format collections: Set of Three Prints, Gallery Walls & Sets, Large Canvas Prints, Canvas Prints, Limited Edition Prints, Bestsellers. — [Abstract House](https://www.abstracthouse.com/)
- Size ladder: **50×50, 50×70, 70×70, 70×100, 100×100 cm**. Frames in **black and oak** finishes. Product types: art prints, canvas art, original paintings, ready-to-hang framed. — [Abstract House](https://www.abstracthouse.com/)
- Positioning line: **"The room starts with art."** Claims: handcrafted in their London studio, award-winning craftsmanship, free and fast delivery in 2–4 days, **70,000+ satisfied art collectors**, Rated Excellent on Trustpilot, sustainable materials and ethical production. — [Abstract House](https://www.abstracthouse.com/)

### Inferences

- Abstract House and Wallfillers independently converge on **colour-led navigation** (Abstract House has eight colour collections; Wallfillers has colour filters and sells one design in 17 colourways). Two UK sellers at opposite ends of the price range both treating colour as the primary axis is the strongest cross-source signal in these notes about how UK buyers shop prints.
- The **50×70cm** size appears at Abstract House, and is also the standard European/Desenio poster size. Combined with Abstract House's 50×50 / 70×70 / 70×100 / 100×100, the UK premium ladder is metric and square-friendly — not the US 8×10/11×14/16×20 inch ladder. A generated catalogue for the UK should be authored at metric aspect ratios (**1:1, 5:7, 7:10**) rather than US inch ratios.
- "Set of Three" and "Gallery Walls & Sets" being named collections at the premium end as well as on eBay confirms **multi-print sets are a UK-wide pattern across price tiers**, not an eBay quirk. Sets also raise average order value and are a natural fit for generated work (coherent series from one prompt family).

### Gaps

- `abstracthouse.com/collections/bestsellers` 404'd; the six products above come from the homepage's featured/bestseller module, which I cannot confirm is rank-ordered by sales.
- No unit volumes, revenue or category mix.

---

## Olive et Oriel: positioning — and why it is **not** a UK comparator

### Takeaway

**Olive et Oriel is Australian, not UK.** It prices in **AUD**, produces in
NSW, and positions as *"Australia's most trusted"*. It ships to the UK among
40+ countries but has **no UK site and no GBP pricing**. Its taxonomy is still
useful as a reference, but its prices and subject mix (including Indigenous
Australian artists) should not be read as UK market evidence.

### Cited Findings

- Positioned as "Australia's most trusted" premium wall art provider since 2015; all production in-house on the **Central Coast, NSW**. — [Olive et Oriel](https://www.oliveetoriel.com/)
- Pricing is in **AUD**: prints from **AUD $69.95**, wallpaper from **AUD $279.95**. Site displays AUD; **no UK site or GBP pricing**. Ships to 40+ countries with duties/taxes prepaid. — [Olive et Oriel](https://www.oliveetoriel.com/)
- Four product categories: Wall Art (fine art prints, framed, canvas, posters); Wallpaper (paste-the-wall, peel & stick, grasscloth, cork, commercial vinyl); Kids & Nursery (child-safe inks); **Sets & Pairs** (pre-curated gallery wall combinations). — [Olive et Oriel](https://www.oliveetoriel.com/)
- Popular styles/subjects listed: **coastal, botanical/floral, abstract, family photos, bohemian, Scandinavian minimalism, vintage-inspired**. Named artists include Teigan Geercke, Julie Celina, and Indigenous Australian artists. — [Olive et Oriel](https://www.oliveetoriel.com/)
- Size range **A4 up to 120×150cm**, framed or unframed; gallery-wrapped canvas up to 180cm. Archival pigment inks on matte fine art paper. — [Olive et Oriel](https://www.oliveetoriel.com/)

### Inferences

- At AUD $69.95 entry (roughly £35–£37 at typical 2026 rates — **my conversion, not a quoted GBP price**) Olive et Oriel sits at Fy!'s *top* tier for its *entry* product, before UK shipping. It is unlikely to be a significant competitive presence in the UK.
- Its "Sets & Pairs" category is the third independent confirmation of the sets pattern.
- The brief named Olive et Oriel as a "UK-focused retailer". **That premise is wrong and the report should say so** — it is an Australian retailer that happens to ship internationally.

### Gaps

- No UK-specific sales, traffic share or GBP pricing exists to find, because the UK operation does not appear to exist as a separate storefront.

---

## Desenio UK and King & McGaw: positioning and pricing

### Takeaway

These two bracket the UK market's two other recognisable models — Desenio as
the **Scandinavian-minimal, low-price, size-laddered poster** operation, King &
McGaw as the **licensed museum/gallery reproduction** operation at **£75–£230**
for standard framed prints and **£260–£600** for special and limited editions.
Both resisted direct capture, so detail here is thinner than I would like.

### Cited Findings

**Desenio UK**

- Desenio operates a UK storefront at `desenio.co.uk` with a **"Maps and cities"** posters category. — [Desenio UK maps and cities](https://desenio.co.uk/posters-prints/maps-and-cities/)
- Desenio's UK city map prints are described as graphical and hand-sketched, in **Scandinavian design, black and white with a hint of colour for sea areas**, covering **London, Leeds, Edinburgh, Manchester, Liverpool, Glasgow and Newcastle**. — [Desenio UK maps and cities](https://desenio.co.uk/posters-prints/maps-and-cities/) (via search snippet; page itself 429'd)

**King & McGaw**

- Framed prints span roughly **£75 to £230** depending on artwork and format: Basquiat *Pez Dispenser 1984* **£75**; Rothko *Blue Green & Brown* **£200**; Hokusai *The Great Wave At Kanagawa* and *Red Fuji* both **£110**. — [King & McGaw prints](https://www.kingandmcgaw.com/prints)
- Popular artists cited: Gustav Klimt, Jean-Michel Basquiat, Louise Body, Frank Bowling; special and limited editions **£175–£600**. — [King & McGaw special editions](https://www.kingandmcgaw.com/prints/special-editions)
- Special editions are **hand-framed in their Sussex studios**, ranging **£260–£350 and above**. — [King & McGaw special editions](https://www.kingandmcgaw.com/prints/special-editions)
- King & McGaw works with major museums and galleries to source artwork; it also runs an **"In Demand Art Prints"** collection. — [King & McGaw in-demand](https://www.kingandmcgaw.com/collections/in-demand); company background [Wikipedia: King and McGaw](https://en.wikipedia.org/wiki/King_and_McGaw)
- King & McGaw supplies print-on-demand and branded ranges to third-party cultural retailers, including the **Courtauld Gallery shop**, **Heal's**, the **Wallace Collection shop**, and a licensed **James Bond / 007** framed-print range. — [Courtauld shop](https://shop.courtauld.ac.uk/collections/king-and-mcgaw); [Heal's](https://www.heals.com/collections/king-and-mcgaw); [Wallace Collection shop](https://wallacecollectionshop.org/collections/king-and-mcgaw); [007Store](https://007store.com/collections/king-mcgaw-framed-prints)

### Inferences

- King & McGaw's model is **licensing-dependent and therefore not replicable by generated imagery** — its value is the rights to Rothko, Basquiat, Hokusai and museum collections, plus Sussex hand-framing. It is a competitor for wall space and budget, not a template.
- Desenio's UK-city-maps range (seven named cities, Scandi black-and-white treatment) is a **directly replicable format**: geometric, text-labelled, monochrome-plus-one-accent, and it scales across dozens of UK towns without near-duplication penalties because each city's street geometry genuinely differs. This is the most promising UK-specific generated-catalogue idea surfaced by this research.
- The **absence** of Desenio price data means the low end of the UK poster ladder is unevidenced here. From Fy!'s £19.95 entry and Desenio's known positioning as a discount poster operation, Desenio's small sizes almost certainly sit **below** £19.95 — but I have no source and am not asserting a number.

### Gaps

- **No Desenio UK prices by size.** `desenio.co.uk` returned 429 on every attempt. The standard Desenio size ladder (21×30, 30×40, 50×70, 70×100 cm) is from my prior knowledge, **not sourced in this research** — treat as unverified.
- No Desenio or King & McGaw bestseller rankings captured. King & McGaw's `/bestsellers` 403'd; one search snippet quoted **USD $19 / $32** mounted-print prices, which indicates a **US storefront** and should not be cited as UK pricing.
- No UK market-share or revenue split between these players.

---

## UK interiors colour and style trends, 2025–2026

### Takeaway

The consistent cross-source signal is a **decisive move from cool grey to warm
earth**: terracotta, clay pink, warm beige, sage, olive, warm taupe, mustard,
with **green overtaking blue as the accent colour** and jewel tones (forest
green, deep burgundy) for drama. On format, the signal is **bigger**:
large-scale single statement pieces, triptychs and coordinated multi-panel
sets. **Caveat: most of these sources are retailer SEO content, not independent
research.**

### Cited Findings

- Warm, earthy neutrals — **terracotta, clay pink, warm beige** — plus rich jewel tones — **forest green, deep burgundy** — lead 2026 wall colour. **Sage, terracotta, clay and warm taupe** have displaced cool greys; the move is explicitly away from cool toward warm undertones. — [Rust-Oleum colour trends 2026](https://rustoleumcolours.co.uk/paint-colour-trends-for-2026/) (paint manufacturer — commercial, but a manufacturer's own forecast is reasonable evidence of what will be on UK walls); corroborated by [Kent Plasterers wall colour trends 2026](https://kentplasterers.co.uk/wall-colour-trends-2026/) — **weak source, trade SEO blog**
- Blue is a standout 2026 favourite, spanning **muted duck egg to bold shades**; however **green has overtaken blue as the accent colour of choice**, with **forest, teal and olive** rising. — [DFS 2026 design trends](https://www.dfs.co.uk/inspiration/2026-design-trends) — retailer content, but DFS is a major UK furniture retailer forecasting its own buying
- 2026 UK wall art is driven by **large-scale expressive pieces, sustainable and textured materials, bold-but-earthy palettes**, and a preference for **local artists and makers**. Oversized canvases and coordinated multi-panel sets create focal points in living rooms and open-plan spaces; single large pieces or triptychs unify colour and line. — [Trowbridge Gallery, UK wall art trends 2026](https://www.trowbridgegallery.com/trade-art-insights/current-uk-wall-art-trends-for-2026-influencing-designers-4733) — **trade-gallery content marketing aimed at interior designers; directional only**
- Trowbridge's specific designer palette for 2026: **"warm neutrals with pops of terracotta, sage, deep green and mustard"**. Named style trends: **statement canvases, abstract expressionism, textured mixed-media, curated gallery walls**, plus "digital art and limited editions" offering exclusivity without commission costs. Size guidance: specify **at least one piece 120×80cm or larger** for primary spaces. Framing: **neutral frames and float mounts** favoured, anti-reflective glazing for high-gloss prints. — [Trowbridge Gallery](https://www.trowbridgegallery.com/trade-art-insights/current-uk-wall-art-trends-for-2026-influencing-designers-4733)
- A "quieter interiors" approach pairs with a **single large-format print in a warm, muted palette** anchoring a room; pieces should feel personal and considered. — [About Wall Art, 2026 decorating trends](https://aboutwallart.com/blogs/news-articles-home-decor-inspiration/my-guide-to-the-top-interior-decorating-trends-2026) — **weak source: retailer blog**
- **Houzz UK 2025 search data** (the one source here with actual measured UK search behaviour): **"oak kitchen" +214%**, **"wood kitchen" +116%**, **"glass wall partition" +202%**, **"double vanity" ~+750%**, **"double shower" +172%**, **"skylight" +115%**, **"coffee station" +77%**, **"freestanding bath" +53%**, **"marble bathroom" +51%**; **"pink kitchen" and "pink bathroom" both over +100%**. Wooden slat walls and wood panels trending. — [Interior Daily reporting Houzz UK 2025 trends](https://www.interiordaily.com/article/9742034/houzz-reveals-key-uk-interior-design-trends-for-2025/)
- Sustainable wall art from recycled and natural materials (reclaimed wood, bamboo, cork, jute) is gaining prominence. — [Interior Daily / Houzz UK](https://www.interiordaily.com/article/9742034/houzz-reveals-key-uk-interior-design-trends-for-2025/)
- Further UK-trend coverage exists at [Yorkshire Post interiors 2025](https://www.yorkshirepost.co.uk/lifestyle/homes-and-gardens/interior-design-trends-set-to-define-home-style-in-2025-4916362) (regional press, broader trend framing).

### Inferences

- **Pink is the strongest measured UK colour signal**, not an inferred one: Houzz UK recorded >100% growth in both "pink kitchen" and "pink bathroom" searches. That is behavioural data, unlike the paint-brand forecasts. Combined with Wallfillers' "Blush Pink Grey Black" bestseller title, **blush/dusty pink is defensible as a priority colourway for a UK generated catalogue.**
- **Green + warm earth is the safest palette bet**, appearing independently in DFS's retail forecast, Rust-Oleum's paint forecast and Trowbridge's designer guidance. "Mustard yellow and grey" appears in Wallfillers' eBay titles too — mustard bridges the forecast palette and proven eBay demand.
- **Grey is the trend to avoid going long on** — three sources describe the move away from cool grey. But note the tension: Wallfillers' actual eBay bestseller titles are *full* of grey ("Blush Pink Grey Black", "Orange Grey", "Navy Blue and Grey", "Mustard Yellow and Grey"). Interpretation: **grey persists as the pairing/neutral in eBay's mass market even as the trend press declares it over.** Design for grey-as-secondary, warm-as-primary.
- The Houzz oak/wood signal (+214% "oak kitchen") matters for **framing** choices, not just imagery — and Abstract House already offers oak as one of only two frame finishes. Oak frame mockups will likely outperform black for UK 2026.
- Trowbridge's "120×80cm or larger" guidance and Wallfillers' XXL-Oversized top-level navigation both point the same way: **UK demand is drifting to larger formats**, which has a direct implication for generation resolution. FLUX.1-schnell output will need upscaling to print at 120×80cm at acceptable DPI; this should be checked before committing a catalogue to large sizes.

### Gaps

- No independent, non-commercial UK colour-trend research (e.g. a retailer sales-mix disclosure or a market-research panel) was found. Every palette source is a party with something to sell.
- Houzz data is **2025**, reported by a trade outlet rather than from the Houzz report itself; I could not reach the original Houzz UK report.
- Houzz's measured terms are about **rooms and fittings**, not prints. The leap from "pink bathroom +100%" to "pink prints sell" is my inference, not evidenced.

---

## UK-specific subjects: towns and cities, coastal, countryside, football, pubs, British humour, royal, seasonal

### Takeaway

**UK city/place subjects are strongly evidenced** — Desenio runs a seven-city
UK map range, Wallfillers' only named UK subject is *London Skyline*, and
specialist UK map-print businesses exist at scale. **Coastal is evidenced** as a
style category across multiple retailers. **Football, pubs, British humour,
royal and seasonal are weakly evidenced or unevidenced** in what I could reach
— I found existence proof (businesses selling them) but no demand or sales
data.

### Cited Findings

**Towns, cities and maps — the best-evidenced UK subject**

- Decorating with a map of one's hometown or favourite destination is described as "extremely popular"; holiday-location maps are called the most popular map type. — [Mapiful UK](https://www.mapiful.com/inspiration/united-kingdom/); [Beach House Art custom maps](https://www.beachhouseart.co.uk/pages/custom-maps) — **both retailer copy, so "popular" is a sales claim, not a measurement**
- Desenio UK's city map range covers **London, Leeds, Edinburgh, Manchester, Liverpool, Glasgow, Newcastle**. — [Desenio UK](https://desenio.co.uk/posters-prints/maps-and-cities/)
- A dedicated UK city-map print business operates at [Art By Arjo](https://artbyarjo.com/shop/ukcitymaps-prints), and a British Isles map-art collection at [Maps As Art](https://www.mapsasart.com/collections/uk).
- Wallfillers' eBay UK range includes *London Skyline Canvas Wall Art Print - 17 Colours Available - 94cm wide* and *Large Orange Grey Map of World Atlas Canvas Wall Art Print - Multi 3 Set*. — [Wallfillers eBay UK](https://www.ebay.co.uk/str/wallfillers-canvas)
- Abstract House runs a **Cityscape Art** collection. — [Abstract House](https://www.abstracthouse.com/)
- Fy! has **Travel** as a subject category. — [Fy!](https://iamfy.co/collections/art-prints)

**Pubs**

- **Pubstops** maps the pubs and bars of UK towns and cities in London-Underground-map style, sold as prints, frames and mugs, covering **over 100 towns and cities**. — [Pubstops](https://pubstops.co.uk/)
- Pub-map prints are also a Redbubble category. — [Redbubble pub maps](https://www.redbubble.com/shop/pub+maps+framed-prints)

**Football**

- Football-and-pub crossover has historical precedent: for the 1930–31 season the East End brewery Charrington circulated a map of London football grounds and their local pubs. — [Londonist](https://londonist.com/london/maps/antique-football-ground-pub-map)

**Coastal and countryside**

- **Coastal** is a named style category at Fy!. — [Fy!](https://iamfy.co/collections/art-prints)
- **Coastal** and **Landscape** are named collections at Abstract House. — [Abstract House](https://www.abstracthouse.com/)
- Coastal imagery is a leading bestselling style at Olive et Oriel (**Australian — see caveat above**). — [Olive et Oriel](https://www.oliveetoriel.com/)
- Coastal wall art and beach art prints are a standing retail category in the UK. — [Beach House Art](https://www.beachhouseart.co.uk/pages/custom-maps)

**British humour**

- Fy!'s first-surfaced products include humorous typographic prints — *What's The Best That Could Happen*, *Nothing Is Under Control*. — [Fy!](https://iamfy.co/collections/art-prints)

### Inferences

- **UK place-based prints are the strongest UK-specific opportunity identified**, on three grounds: multiple independent businesses exist purely on this subject (Pubstops with 100+ towns, Art By Arjo, Maps As Art, Mapiful, Desenio's seven cities); place names carry natural long-tail search demand on eBay UK and Etsy UK; and each town genuinely differs, so a large catalogue can be built **without** triggering the 89% near-duplication problem CLAUDE.md flags. Pubstops' 100+ towns is an existence proof that the long tail below London/Manchester is commercially worth serving.
- **Pubstops' format is the model to study**: a stylised transit-map treatment applied to a town's pubs. It is text-and-geometry heavy — which is precisely where **FLUX.1-schnell will struggle**, since diffusion models render legible place-name text and accurate geography poorly. This subject probably needs a **data-plus-vector pipeline, not image generation**. Flagging this because it is the gap between the best commercial opportunity found and the technology this project is built on.
- **Football is a licensing trap.** Club names, crests, kits and stadium imagery are aggressively protected in the UK. The only football evidence I found is a 1930s historical artefact. Generated football prints sold on eBay UK would be an IP-takedown risk, and eBay UK's VeRO programme is actively used by Premier League clubs. Recommend avoiding.
- **Royal and seasonal subjects: I found nothing.** No source in this research supports or refutes them. Given the repo's commercial-risk framing, these should be treated as **untested**, not as opportunities.
- British humour / typographic prints are evidenced as present on Fy! but there is no UK sales data. They are also the cheapest thing to generate (text-led) and therefore the most crowded — likely a low-margin, high-duplication segment.

### Gaps

- **No sales or search-volume data for any UK-specific subject.** Everything above is existence-of-supply evidence, which is weaker: a category can be well-supplied and still not sell.
- **Nothing found on royal subjects** (coronation, jubilee, royal portraits) in the UK print market.
- **Nothing found on seasonal subject demand** (Christmas prints, autumn, bonfire night) specifically for wall art.
- **Nothing found on countryside subjects specifically** — Lake District, Cotswolds, Peak District, Highlands — beyond generic "Landscape" categories.
- No evidence on which UK cities beyond Desenio's seven have viable demand, nor on relative volumes between them.

---

## Gifting occasions driving UK print sales, and when

### Takeaway

The two anchors are **Christmas** (with a November search peak and decoration
items at 10% of most-desired UK Christmas gifts) and **UK Mother's Day /
Mothering Sunday** (≈**£1.57–1.6bn** UK retail spend, **£60+** average per
person). Critically, **UK Mothering Sunday is a moveable Lent date in March,
not the US May date** — a scheduling trap for any US-derived calendar.

### Cited Findings

- **UK Mother's Day retail spend was projected at £1.57 billion for 2025**. — [Statista, Mother's Day spending UK](https://statista.com/statistics/1287462/mothers-day-spending-united-kingdom)
- UK consumers spend **over £1.6 billion annually** on Mother's Day across gifts, flowers, cards and experiences, with **average spend typically exceeding £60 per person**. — [Jondo UK, Mother's Day gift-giving trends 2026](https://www.jondo.co.uk/post/mother-s-day-gift-giving-trends-in-the-uk-key-insights-for-e-commerce-brands-in-2026) — **print-supplier content marketing; the £1.6bn is consistent with the Statista figure so treat the magnitude as sound**
- For UK e-commerce sellers, demand for gifts, **personalised products and keepsakes peaks at UK Mother's Day**, dated **15 March** in the year referenced. — [MerchOne, custom Mother's Day gifts UK](https://merchone.com/blog/custom-mothers-day-gifts-uk/) — **POD-supplier blog, weak source**; UK date mechanics confirmed independently at [Time and Date, Mothering Sunday UK](https://timeanddate.com/holidays/uk/mothering-sunday)
- **Decoration articles accounted for 10% of Christmas gifts most desired by UK consumers in 2025.** — [Statista, Christmas gifts desired by UK consumers 2025](https://www.statista.com/statistics/1084794/christmas-gifts-desired-by-uk-consumers/)
- Christmas is the most popular spending holiday by far, with Black Friday among the most popular shopping days. — [Statista](https://www.statista.com/statistics/1084794/christmas-gifts-desired-by-uk-consumers/)
- Personalised framed canvas wall art is characterised as feeling "permanent and emotionally anchored", making it a favoured gift. — [Jondo UK](https://www.jondo.co.uk/post/mother-s-day-gift-giving-trends-in-the-uk-key-insights-for-e-commerce-brands-in-2026) — **supplier opinion, not data**
- **Search-volume seasonality:** peak interest for "wall art posters" occurred in **November 2025**; trough in **May 2025**. — [RankHero, wall-art-poster keyword](https://www.rankhero.com/keywords/wall-art-poster) — **weak source: third-party keyword aggregator, methodology undisclosed**
- A Mintel report on the UK Mother's Day market exists but is paywalled. — [Mintel, UK Mother's Day Market Report 2026](https://store.mintel.com/report/uk-mothers-day-market-report)
- US contrast, cited explicitly as **US data**: US Mother's Day spending rose by nearly $4 billion in one year. — [Axios](https://www.axios.com/2023/05/13/mothers-day-gifts-2023-spending). **Not transferable: the US date is the second Sunday in May, the UK date is the fourth Sunday in Lent (March), so campaign calendars cannot be shared.**

### Inferences

- **The UK gifting calendar for prints is: Mother's Day (March, moveable) → Father's Day (June) → Christmas peak with November search ramp and Black Friday.** Only the first and third are evidenced here.
- The **November search peak against a May trough** implies print listings should be live and ranked by **early October at the latest** — ranking on eBay UK takes weeks of sales history to build, so a catalogue uploaded in November has largely missed the window. Given today's date (**7 October 2026**), a Christmas 2026 push is already tight.
- **Personalisation and gifting are the same demand.** Both the Mother's Day sources tie the peak specifically to *personalised* products and keepsakes, not generic decor. This suggests the gifting opportunity is in personalised formats rather than in generated art per se — a structural limitation for a generated catalogue.
- "Decoration" at 10% of desired Christmas gifts is a **real but modest** share; it is not a top-three gift category. Print gifting is a solid secondary market, not a primary one.

### Gaps

- **No UK Father's Day spending figure found**, and no evidence it drives print sales.
- No evidence on other plausible UK print-gifting occasions: weddings, new home/housewarming, new baby, anniversaries, Valentine's Day, graduations.
- The Mintel UK Mother's Day report is paywalled, so no category-level breakdown of what is actually bought.
- No eBay UK or Etsy UK seasonal sales-curve data — only a third-party keyword tool's seasonality, which I rate low confidence.

---

## Room-by-room demand in the UK

### Takeaway

Retailer taxonomies give a consistent UK room hierarchy —
**Living Room → Bedroom → Home Office → Kitchen → Hallway → Bathroom → Kids'
Room** — and eBay UK's top seller puts the room name **in the listing title**,
which is the actionable finding. Beyond taxonomy, UK room-specific *demand*
data for prints is thin; most "room trend" content I found concerns fittings
and paint, not art.

### Cited Findings

- Fy!'s room taxonomy, in the order presented: **Living Room, Bedroom, Home Office, Kitchen, Hallway, Bathroom, Kids' Room**. — [Fy!](https://iamfy.co/collections/art-prints)
- Wallfillers puts the room in eBay UK titles: *"…UK Living Bed Room Pictures"*, *"…Sunset Living Room"*, *"Navy Blue and Grey Swirl **Living Room** Canvas Wall Art"*, *"Mustard Yellow and Grey Swirl **Bedroom** Canvas Wall Art"*. — [Wallfillers eBay UK](https://www.ebay.co.uk/str/wallfillers-canvas)
- Room-specific guidance for 2026: **bedrooms** take calming, smaller works; **living rooms** suit statement pieces or gallery walls; **kitchens and bathrooms** require sealed prints or metal substrates for moisture resistance. — [Trowbridge Gallery](https://www.trowbridgegallery.com/trade-art-insights/current-uk-wall-art-trends-for-2026-influencing-designers-4733) — **trade content marketing**
- **Oversized canvases and coordinated multi-panel sets** are used in living rooms and open-plan spaces. — [Trowbridge Gallery](https://www.trowbridgegallery.com/trade-art-insights/current-uk-wall-art-trends-for-2026-influencing-designers-4733)
- For **kitchens**, small-scale wall art such as botanical prints or simple abstract designs personalises without crowding. — [About Wall Art, UK 2026 trends by room](https://aboutwallart.com/blogs/news-articles-home-decor-inspiration/home-decor-trends-for-2026-key-looks-for-every-room) — **retailer blog, weak**
- **Nursery:** the accent-wall trend is extending to all four walls, closets and ceilings; **"elevated nostalgia"** is emerging (line art of childhood characters); **custom name art is "a staple accent"** in 2025 nursery design, from wooden lettering to canvas calligraphy; celestial motifs and bold vibrant patterns feature. — [Home Network nursery trends 2025](https://www.homenetwork.ca/nursery-trends-2025/) and [Automate Life nursery trends 2025](https://automatelife.net/top-nursery-trends-designers-recommend-for-2025/) — **both North American sources; flagged as non-UK, see inference below**
- UK nursery wall decor is a live retail category covered by UK parenting press. — [Mother & Baby, nursery wall decor](https://www.motherandbaby.com/first-year/products/nursery/nursery-wall-decor/)
- Olive et Oriel maintains a dedicated **Kids & Nursery** range using child-safe inks (**Australian retailer**). — [Olive et Oriel](https://www.oliveetoriel.com/)
- UK **bathroom and kitchen** search growth 2025 (Houzz UK, measured): double vanity ~+750%, double shower +172%, freestanding bath +53%, marble bathroom +51%, oak kitchen +214%, wood kitchen +116%, coffee station +77%, pink kitchen and pink bathroom both >+100%. — [Interior Daily / Houzz UK](https://www.interiordaily.com/article/9742034/houzz-reveals-key-uk-interior-design-trends-for-2025/)
- Abstract House's own navigation offers no room axis at all — it sorts by style, colour and format only. — [Abstract House](https://www.abstracthouse.com/)

### Inferences

- **Living room and bedroom dominate**, on two independent signals: Fy! lists them first, and they are the only two rooms Wallfillers names in eBay titles. Home office appearing third in Fy!'s list is a plausible post-2020 UK artefact but is unevidenced as a sales rank.
- **The actionable finding is titling, not taxonomy.** Putting "Living Room" or "Bedroom" into an eBay UK title is what the 51k-items-sold seller does, and it is free to replicate.
- **Room axis correlates with price tier.** The mass-market seller (Wallfillers) and the mid-market marketplace (Fy!) both merchandise by room; the premium seller (Abstract House) does not. Interpretation: room-matching is how *value* buyers shop, style/colour is how *design-led* buyers shop. A generated catalogue aimed at eBay UK should lead on room; one aimed at a design marketplace should lead on style.
- **Kitchen and bathroom are structurally weak for paper prints** — moisture means sealed or metal substrates per Trowbridge, and the demand Houzz measured there is for fittings (vanities, baths, oak units), not art. Low priority.
- **Nursery is the clearest room-level opportunity but is dominated by personalisation.** Every nursery source points to custom name art as the staple. Generated art cannot supply a name; a name overlay on a generated background can. Note that the nursery trend evidence is **North American**, so the specific motifs (celestial, "elevated nostalgia") should be treated as unconfirmed for the UK even though the personalisation pattern is corroborated by the UK Etsy evidence below.

### Gaps

- **No UK sales-by-room data from any retailer or marketplace.** The hierarchy above is inferred from navigation order, which is a merchandising choice, not a sales ranking.
- No UK-specific nursery print trend research; had to fall back on North American sources, flagged.
- No data on hallway or home-office print demand in the UK beyond their presence in Fy!'s menu.

---

## Personalised prints on eBay UK and Etsy UK: scale, formats, prices

### Takeaway

The UK personalised-gifts market is sized at roughly **USD 1.89bn (2024)**
growing **8–11% CAGR**, and Etsy UK personalised prints transact across a very
wide band — observed **£8.99 to £56**, with heavy discounting and free UK
delivery as the norm. Formats cluster into **pet portraits, custom maps, song
lyrics/foil, nursery name art and photo canvas**. **No eBay UK personalised
print data could be obtained.**

### Cited Findings

- UK personalised gifts market: **estimated to grow by USD 1.26 billion 2025–2029 at ~11% CAGR**. — [Technavio via PR Newswire](https://www.prnewswire.com/news-releases/personalized-gifts-market-in-the-uk-to-grow-by-usd-1-26-billion-from-2025-2029--driven-by-gift-giving-culture-and-seasonal-decor-demand-with-ai-impact---technavio-302370802.html); also [Technavio report page](https://www.technavio.com/report/uk-personalized-gifts-market-analysis)
- **Conflicting vendor estimate:** UK personalised gifts valued at **USD 1.89 billion in 2024**, reaching **USD 3.27 billion by 2032** at **8.16% CAGR**. — [Data Bridge Market Research](https://www.databridgemarketresearch.com/reports/uk-personalized-gifts-market) — **note the two vendors disagree on both growth rate (11% vs 8.16%) and framing (increment vs total); neither discloses method. Use the order of magnitude only.**
- An earlier Technavio vintage put the 2024–2028 increment at **USD 1.13 billion**, and another at **USD 1.25bn for 2025–2029** — the same house publishing three different numbers across editions. — [Technavio 2024–2028](https://finance.yahoo.com/news/personalized-gifts-market-uk-grow-041800231.html); [Technavio 2025–2029 alt figure](https://www.prnewswire.com/news-releases/personalized-gifts-market-in-uk-to-grow-by-usd-1-25-billion-2025-2029-with-the-advent-of-gift-giving-culture-and-increasing-demand-for-seasonal-decorations-driving-market-growth-ai-transforming-market---technavio-302365349.html)
- Growth drivers named: UK gift-giving culture, **rising demand for seasonal decorations**, smartphone usage and digitisation, eco-friendly personalised gifts. Named challenge: competition from homemade/DIY gifts. — [Technavio](https://www.prnewswire.com/news-releases/personalized-gifts-market-in-the-uk-to-grow-by-usd-1-26-billion-from-2025-2029--driven-by-gift-giving-culture-and-seasonal-decor-demand-with-ai-impact---technavio-302370802.html)
- **Etsy is named as a key market player**; Etsy has launched **"Gift Mode"**, an AI-driven gift-recommendation feature based on recipient profiles. — [Technavio](https://www.prnewswire.com/news-releases/personalized-gifts-market-in-the-uk-to-grow-by-usd-1-26-billion-from-2025-2029--driven-by-gift-giving-culture-and-seasonal-decor-demand-with-ai-impact---technavio-302370802.html); [Etsy UK personalisation hub](https://www.etsy.com/uk/featured/hub/personalization-shop)
- **Observed Etsy UK personalised-print prices (GBP, as displayed with discounts):**
  - Custom Pet Portraits — **£25.51** (20% off £31.88)
  - Add-On Print & Framed Option — **£21.78** (50% off £43.57), free UK delivery
  - A4 Custom Foil Metallic Song Lyrics Art — **£13.50** (55% off £30.00), free UK delivery
  - Personalised Photo Canvas Print, custom family & pet wall art — **£8.99** (40% off £14.98), free UK delivery
  - Personalised Travel Adventures Map Print — **£56.00** (20% off £70.00), free UK delivery
  — [Etsy UK personalised print market page](https://www.etsy.com/uk/market/personalised_print)
- Etsy UK bestseller example title: *"Personalised Girls Name Frames - Pink Woodland Animals Nursery Wall Art - Baby Girl Gift"*. — [Etsy UK framed personalised prints](https://www.etsy.com/uk/market/framed_personalised_prints)
- Etsy UK maintains dedicated market pages for **personalised_print**, **personalisable_prints**, **best_selling_prints**, **most_sold_prints**, **print_on_demand_best_sellers** and **framed_personalised_prints**. — [Etsy UK best selling prints](https://www.etsy.com/uk/market/best_selling_prints); [Etsy UK print-on-demand bestsellers](https://www.etsy.com/uk/market/print_on_demand_best_sellers)
- UK illustrated-map printables are a live Etsy category. — [Etsy UK illustrated map printable](https://www.etsy.com/market/uk_illustrated_map_printable)

### Inferences

- **Etsy UK's personalised-print price band is £9–£56, with a centre of gravity around £14–£26.** That overlaps Fy!'s £19.95–£35.95 almost exactly — but Etsy's prints are *personalised*, meaning personalisation does not command a premium over good non-personalised design in the UK. It wins on **relevance and gifting fit**, not price.
- **Near-universal heavy discounting on Etsy UK** (20%, 40%, 50%, 55% off observed on five of five items) implies anchor-and-discount is the expected pricing presentation. A catalogue listing at flat prices will look expensive next to these.
- **Three personalised formats recur and are the practical shortlist**: (1) **custom maps** — highest price achieved, £56, and connects to the UK place-subject finding; (2) **nursery name art**, corroborated by both the Etsy bestseller title and the nursery trend sources; (3) **pet portraits** at ~£25. Song-lyric prints are cheap (£13.50) and carry music-licensing exposure.
- **Custom maps are the convergence point of this entire research**: they are the best-evidenced UK subject, the highest-priced Etsy personalised format, a standalone business model (Pubstops, Mapiful, Art By Arjo), and inherently non-duplicative. The blocker remains that they are **data/vector work, not diffusion-model work**.
- **Personalisation is a structural mismatch with a generated static catalogue.** Personalised items need per-order variable data; generated catalogues are pre-rendered. Capturing this demand means a render-on-order step, which is a different pipeline from bulk pre-generation.

### Gaps

- **No eBay UK personalised-print data whatsoever** — no sold volumes, no price points, no listing counts. eBay UK was 403-blocked throughout. The key question "how big is this on eBay UK" is **unanswered**.
- No Etsy UK category sales volumes, listing counts or sell-through rates. Etsy market pages were reachable only via search snippets; no shop-level sold counts captured.
- The market-size figures are **modelled vendor estimates covering all personalised gifts**, not prints. No print-specific UK figure exists in these sources.
- Etsy prices above are **displayed sale prices from one snapshot**, not realised averages.

---

## Conversion, search volume and sales-rank data for UK wall art

### Takeaway

**This is the weakest-evidenced question in the assignment.** I found no
conversion-rate data for UK wall art from any credible source, and no sales-rank
data. The only search-volume figures available come from a third-party keyword
aggregator with undisclosed methodology — notable only for one finding, that
**"wall print" is disproportionately a UK query (37% of global volume vs 20%
US)**. Market-size estimates exist but conflict sharply between vendors.

### Cited Findings

**Search volume (low confidence — single weak source)**

- **"wall print"**: 33,100 average monthly searches globally; **UK 12,100 = 37% of volume**, versus **USA 20%** — i.e. UK over-indexes heavily on this term. — [RankHero, "wall print"](https://www.rankhero.com/keywords/wall-print)
- **"wall poster"**: 60,500 average monthly searches globally; **UK 3,600 = 6%**. — [RankHero, "wall poster"](https://www.rankhero.com/keywords/wall-poster)
- **"wall art poster"**: 4,400 monthly searches, high competition; **UK 720 = 16%**. — [RankHero, "wall art poster"](https://www.rankhero.com/keywords/wall-art-poster)
- Seasonality for "wall art posters": **peak November 2025, trough May 2025**. — [RankHero](https://www.rankhero.com/keywords/wall-art-poster)
- Related keyword pages exist for "uk wall art", "art poster", "wall art gift" and "gold wall art". — [RankHero uk-wall-art](https://www.rankhero.com/keywords/uk-wall-art); [art-poster](https://www.rankhero.com/keywords/art-poster); [wall-art-gift](https://www.rankhero.com/keywords/wall-art-gift); [gold-wall-art](https://www.rankhero.com/keywords/gold-wall-art)
- **Source warning:** RankHero is an SEO keyword aggregator reselling third-party clickstream estimates. It discloses no methodology and its page timestamps (e.g. "Updated Jun 27, 2026") do not identify the data period. Treat all figures above as indicative only.

**Market size (vendor estimates, conflicting)**

- **UK wall art market: USD 4,140.2 million revenue in 2025**, reaching **USD 6,741.2 million by 2033**, CAGR **6.4% from 2026 to 2033**. Largest segment in 2025 was **wallpapers/stickers/wall coverings at 38.14% revenue share**. — [Grand View Research, UK wall art outlook](https://www.grandviewresearch.com/horizon/outlook/wall-art-market/uk)
- **UK home decor market: USD 25,717.58 million in 2024**, reaching **USD 36,509.22 million by 2033**, CAGR **3.97% (2025–2033)**. — [IMARC, UK home decor market](https://www.imarcgroup.com/uk-home-decor-market)
- Growth attributed to consumer interest in contemporary interior aesthetics and to **online platforms featuring curated and customised wall art collections**. — [Grand View Research](https://www.grandviewresearch.com/horizon/outlook/wall-art-market/uk)
- Other vendors covering the same ground, with differing numbers and no shared method: [Market Research Future](https://www.marketresearchfuture.com/reports/wall-art-market-12499), [Future Market Insights](https://www.futuremarketinsights.com/reports/wall-art-market), [Verified Market Research UK home decor](https://www.verifiedmarketresearch.com/product/uk-home-decor-market/), [Mordor Intelligence UK home decor](https://www.mordorintelligence.com/industry-reports/uk-home-decor-market), [IndexBox UK framed wall art decor](https://www.indexbox.io/store/united-kingdom-kw-framed-wall-art-decor-840-market-analysis-forecast-size-trends-and-insights/), [Markwide UK home decor](https://markwideresearch.com/united-kingdom-home-decor-market). A retailer blog aggregating such figures sits at [Musa Art Gallery](https://musaartgallery.com/en-fr/blogs/news/home-decor-statistics-2026-market-size-trends-and-wall-art) — **retailer content, do not cite as research.**

### Inferences

- **The one finding worth carrying forward is terminology.** If "wall print" really is 37% UK versus 20% US, then UK buyers use **"print"** where US buyers use **"poster"**. eBay UK titles should favour **"Print" / "Wall Art Print" / "Pictures"** over "Poster" — and Wallfillers' titles independently confirm this: they say "Canvas Wall Art Print" and "Pictures", never "Poster". Two weakly-related signals agreeing on terminology is more useful than either alone.
- **The UK wall-art market being 16% of UK home decor** (4.14 of 25.7 USD bn) is plausible but rests on two different vendors' incompatible models; do not quote the ratio.
- **Grand View's segmentation undercuts the headline.** If wallpaper/stickers/wall coverings are 38% of "wall art", then the USD 4.14bn figure is **not** a prints-and-posters market size. The addressable prints segment is substantially smaller and unquantified here.
- The November search peak agrees with the Christmas gifting evidence, giving two independent-ish signals for an autumn listing deadline.

### Gaps

- **No conversion-rate data for UK wall art on any channel** — not eBay UK, not Etsy UK, not D2C. Nothing credible found. This question is effectively unanswered.
- **No sales-rank data.** eBay UK has no public bestseller rank equivalent to Amazon BSR, and its pages were 403-blocked.
- **No Google Trends data captured.** I did not reach trends.google.com; the search-volume figures above are from a reseller, not Google.
- No eBay UK listing counts, impression or click-through data; no Terapeak access attempted.
- No UK-specific average order value or returns-rate data for prints.

---

## Cross-cutting notes for the report writer

### Takeaway

Four findings recur across independent sources and should carry the most weight;
three structural problems also recur and should be stated plainly.

### Cited Findings

- **Colour as the primary axis** — Abstract House runs eight colour collections ([Abstract House](https://www.abstracthouse.com/)); Wallfillers filters by colour and sells one design in **17 colourways** ([Wallfillers eBay UK](https://www.ebay.co.uk/str/wallfillers-canvas)); Wallfillers' site has colour filters ([Wallfillers](https://wallfillers.co.uk/)).
- **Sets of 2–3 across every price tier** — eBay UK has a dedicated *Set Of Prints* node ([eBay UK](https://www.ebay.co.uk/b/bn_7023600434)); Abstract House has *Set of Three Prints* and *Gallery Walls & Sets* ([Abstract House](https://www.abstracthouse.com/)); Wallfillers has *Sets of 3* in top-level navigation ([Wallfillers](https://wallfillers.co.uk/)); Olive et Oriel has *Sets & Pairs* ([Olive et Oriel](https://www.oliveetoriel.com/)).
- **Warm earth palette with green ascendant** — [DFS](https://www.dfs.co.uk/inspiration/2026-design-trends), [Rust-Oleum](https://rustoleumcolours.co.uk/paint-colour-trends-for-2026/), [Trowbridge](https://www.trowbridgegallery.com/trade-art-insights/current-uk-wall-art-trends-for-2026-influencing-designers-4733) agree independently.
- **A three-tier UK price ladder** — eBay UK mass-market canvas (price unevidenced, visibly lowest) < Fy! **£19.95–£46.95** ([Fy!](https://iamfy.co/collections/art-prints)) and Etsy UK personalised **£9–£56** ([Etsy UK](https://www.etsy.com/uk/market/personalised_print)) < King & McGaw **£75–£230** standard, **£260–£600** editions ([King & McGaw](https://www.kingandmcgaw.com/prints)) and Abstract House **£115–£774** ([Abstract House](https://www.abstracthouse.com/)).
- **Metric size ladder** — Abstract House: 50×50, 50×70, 70×70, 70×100, 100×100 cm ([Abstract House](https://www.abstracthouse.com/)); Olive et Oriel A4–120×150cm ([Olive et Oriel](https://www.oliveetoriel.com/)); Trowbridge recommends ≥120×80cm for primary spaces ([Trowbridge](https://www.trowbridgegallery.com/trade-art-insights/current-uk-wall-art-trends-for-2026-influencing-designers-4733)).

### Inferences

- **On the repo's 89% near-duplication risk:** the UK evidence says colourway variation is *how the market works*, which looks like a direct conflict. The resolution is that proven UK sellers put many colourways **inside one listing** (Wallfillers: "17 Colours Available"), not across many listings. Measure duplication at the **listing** level, and treat colourways as variations rather than SKUs. This is a concrete, evidenced answer to a risk CLAUDE.md flags as the main commercial one.
- **On FLUX.1-schnell's fit:** the two best-evidenced UK opportunities — **place/map prints** and **personalised name art** — are both **text-and-data-led**, where diffusion models are weakest. The opportunities that suit schnell best (abstract, botanical, florals, coastal, geometric) are also the most crowded and most duplication-prone. The report should state this tension rather than only listing opportunities.
- **On large formats:** UK demand is drifting to 100×100cm and 120×80cm+. Native schnell resolution will not print at those sizes at acceptable DPI without an upscaling stage. This should be treated as a pipeline requirement, not a detail.
- **On eBay category:** CLAUDE.md records wall art as category **360**, which matches eBay's "Art Prints". That is consistent. But the high-volume UK canvas sellers may be listing in Home Décor nodes instead, and I could not verify which. Worth checking against a live listing before the first upload.

### Gaps

- **The eBay UK half of this assignment is substantially unevidenced** because eBay UK returned 403 to every automated request (WebFetch and curl with browser headers alike). Category structure came through via search snippets; **sold prices, sold volumes, sell-through and conversion did not**. Recommend: use Terapeak through the existing eBay seller account, or the eBay Marketplace Insights API, before making pricing decisions. Do not let the retailer prices in these notes stand in for eBay UK prices.
- Fy!, Abstract House, King & McGaw and Wallfillers **bestseller pages all failed** (404/403/truncated). Products attributed to those brands here come from default-sorted listings or homepage modules and are **not confirmed sales rankings**.
- Royal subjects, seasonal subjects, UK countryside subjects, Father's Day, weddings, housewarming and new-baby occasions, and all conversion metrics are **entirely unevidenced** in this research.
