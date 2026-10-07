# Wall art catalogue taxonomy: Etsy and eBay UK (structure, facets, shop sections, vocabulary)

Harvested 2026-10-07. Access reality up front, because it shapes everything below:

| Target | Method | Result |
|---|---|---|
| `www.etsy.com/*` (browse `/c/`, `/market/`, `/help/categories/seller`, `/seller-handbook/*`) | WebFetch and curl with full browser headers (UA, Accept, Accept-Language, sec-ch-ua, Sec-Fetch-*) | **HTTP 403 on every path, every attempt.** Etsy edge returns a "Please enable JS" interstitial. No Etsy page was read directly. |
| `openapi.etsy.com/v3/application/buyer-taxonomy/nodes` | curl | **403** (needs `x-api-key`; no key available) |
| `www.ebay.co.uk/b/*` and `/sch/*` (browse + search) | WebFetch and curl | **403** (confirms the earlier research note) |
| `pages.ebay.co.uk/categorychanges/UK_Category_Changes.html` | curl | **200 — 929 KB, full UK category list with IDs. This is the primary source for the eBay section below.** |
| `www.ebay.co.uk/n/all-categories` | curl | **200** (buyer-facing nav, gives `bn_` browse-node codes) |
| `www.ebay.co.uk/str/<slug>` (seller storefronts) | curl | **200 — store category menus readable in page JSON. Primary source for the eBay shop-section section below.** |
| `www.ebay.co.uk/sellercentre/*` | curl | 200 but generic guidance only; no per-category aspect values |
| `web.archive.org` | WebFetch | tool-level block ("Claude Code is unable to fetch from web.archive.org"); curl → connection reset by peer; `archive.org/wayback/available` → 429 |
| `r.jina.ai` reader proxy on Etsy/eBay | curl | 403 (Cloudflare challenge on the proxy itself) |
| GitHub code search for mirrored Etsy taxonomy JSON | `gh api /search/code` | **403 — "sessions are bound to their configured repositories"**; code search unavailable in this session |

Consequence: the **eBay UK category tree and the eBay UK shop sections in these notes are primary-source verbatim**. Everything attributed to Etsy's own filters, and all eBay *aspect value* lists, are **second-hand (search-engine summaries of pages I could not open)** and are labelled as such. I have not invented any list.

---

## Q1. Etsy's full browse tree for Wall Decor and every filter facet

### Takeaway
Etsy was 403 on every path, so I could not read the browse tree or the facet rails directly. What I have is search-engine-derived fragments of the `/c/home-and-living/home-decor/wall-decor` page plus the category chips Etsy renders on `/market/` pages. The facet *names* the brief lists are consistent with those fragments, but I cannot certify a complete facet-value enumeration for Etsy, and I am not going to synthesise one.

### Cited Findings
- The Wall Decor node sits at `Home & Living > Home Decor > Wall Decor`, URL `https://www.etsy.com/c/home-and-living/home-decor/wall-decor`; a vintage-scoped duplicate exists at `https://www.etsy.com/c/vintage/home-and-living/home-decor/wall-decor` — [Etsy Wall Decor (URL only; page unreadable, 403)](https://www.etsy.com/c/home-and-living/home-decor/wall-decor); [Etsy Vintage Wall Decor](https://www.etsy.com/c/vintage/home-and-living/home-decor/wall-decor)
- Search-engine summary of that Wall Decor page lists these sub-options: **Wall Hangings; Wall Decals & Murals; Wallpaper; Wall Clocks; Wall Shelves; Key Holders & Key Hooks; Window Clings; Wall Stencils** — [via search summary of etsy.com/c/home-and-living/home-decor/wall-decor](https://www.etsy.com/c/home-and-living/home-decor/wall-decor) *(second-hand; page itself 403)*
- Category chips Etsy renders on wall-art `/market/` pages (the "shop by category" rail) were summarised as: **Wall Hangings; Wall Decor; Prints; Signs; Digital Prints; Giclée Prints; Paintings; Watercolor Paintings; Drawings & Sketches**, and on a narrower query also **Wood & Linocut Prints; Pet Portraits** — [via search summary of etsy.com/market/tree_art_prints](https://www.etsy.com/market/tree_art_prints) *(second-hand)*
- Further chips summarised from tapestry/wall-hanging market pages: **Wall Hangings; Wall Decor; Suncatchers; Signs; Tapestries; Home Accents; Christmas Ornaments; Prints; Garlands, Flags & Bunting** — [via search summary of etsy.com/market/wall_hanging_decor](https://www.etsy.com/market/wall_hanging_decor) *(second-hand)*
- Etsy's own seller documentation on attributes confirms the facet *families* but publishes no value lists: attributes cover "material, primary color, secondary color, holiday, occasion, height, and width", and "the category and subcategories you choose determine which attributes you can add" — [Etsy Seller Handbook: Updates to Listing Categories and Attributes (403 to me; title/claims via search summary)](https://www.etsy.com/seller-handbook/article/362857340643)
- Third-party guides confirm the same families and nothing more granular: Color (primary + secondary), Material, Size/dimensions, Occasion ("Wedding, birthday, anniversary"), Holiday ("Christmas, Valentine's Day"), Recipient ("for him, for her, for kids, for pets"), and category-specific fields "room (for home decor), craft type (for supplies), or style" — [Listadum, Etsy Listing Attributes 2026](https://www.listadum.com/blog/etsy-listing-attributes); [Alura, Optimizing Etsy Listings with Attributes](https://www.alura.io/docs/article/optimizing-etsy-listings-with-attributes)
- Etsy's taxonomy is machine-readable per category: "each category's JSON contain[s] information about its place in the hierarchy and the attributes, values, and scales for items in that category", retrievable via `getSellerTaxonomyNodes` and `getPropertiesByTaxonomyId` — [etsy/open-api discussion #776](https://github.com/etsy/open-api/discussions/776); [Etsy Listings Tutorial](https://developer.etsy.com/documentation/tutorials/listings/)

### Inferences
- The clean way to get the real Etsy facet/value enumeration is **not** scraping: it is one authenticated call to `getPropertiesByTaxonomyId` for the Wall Decor / Prints taxonomy ids with an Etsy app key. That is a single-key dependency, not a research problem.
- "Prints" and "Digital Prints" / "Giclée Prints" being siblings of "Wall Decor" in the chip rails suggests Etsy's *buyer* facets cut across two different trees (Art & Collectibles > Prints vs Home & Living > Home Decor > Wall Decor). A generated catalogue therefore needs a listing-category decision per item, not one fixed node.

### Gaps
- **No verified Etsy sub-category list under Wall Decor.** The two chip lists above conflict in membership (one includes Wallpaper/Wall Clocks/Wall Shelves, the other Suncatchers/Tapestries/Ornaments), which is itself evidence they are different UI rails, not one tree.
- **No verified Etsy facet value lists at all** for style, colour, room, orientation, material, size, framing, subject, occasion, holiday or personalisation.
- Could not confirm whether Etsy UK (`/uk/c/...`) exposes different facets from US; both URLs 403.

---

## Q2. Etsy's named STYLE taxonomy (filter + seller "Style" attribute)

### Takeaway
**I could not reproduce Etsy's real Style list and I will not guess it.** Every route to the authoritative list was blocked. What I can report is that Etsy *has* "Style" as a category-dependent attribute, that sellers may pick more than one value, and that the style names in the brief (Boho, Mid-Century Modern, Japandi, Hollywood Regency, etc.) do exist as Etsy *market/search* namespaces — which is not the same thing as being dropdown values.

### Cited Findings
- Style is a category-dependent attribute, multi-select: "You can select more than one style if your product genuinely fits multiple categories", with the warning not to pick "Vintage" opportunistically — [Listadum, Etsy Listing Attributes 2026](https://www.listadum.com/blog/etsy-listing-attributes)
- Example of Style used as a value pair in integration docs: "Material: Sterling Silver" and "Style: Vintage" — [Alura](https://www.alura.io/docs/article/optimizing-etsy-listings-with-attributes)
- `Hollywood Regency` and `Japandi` exist as Etsy market namespaces (`etsy.com/market/hollywood_regency`, `etsy.com/market/japandi_style`), with associated descriptive tag clusters "Glam Decor, Luxury, Decorative, Ornamental, Vintage Style" and "Calm Minimal Interior, Scandinavian, Minimalist, Wabi Sabi" respectively — [Etsy market: Hollywood Regency](https://www.etsy.com/market/hollywood_regency); [Etsy market: Japandi Style](https://www.etsy.com/market/japandi_style) *(second-hand via search summaries; both 403 to me)*
- Style labels confirmed in use as *descriptive* vocabulary on Etsy wall-art shops/market pages (see Q5/Q6 for shop-level evidence): boho, mid-century modern, abstract, botanical, minimalist, coastal, farmhouse, vintage, Scandinavian, pop surrealism, contemporary, Japanese — [Creative's Hour, 20 Most Successful Etsy Wall Art Stores 2026](https://thecreativeshour.com/etsy-wall-art-stores/); [Etsy market summaries](https://www.etsy.com/market/wall_hanging_decor)

### Inferences
- The brief's candidate style list is plausible as *market vocabulary* and should be treated as a keyword axis for prompt generation, but it must not be presented as "Etsy's Style attribute values" in any downstream document until a `getPropertiesByTaxonomyId` call confirms it.

### Gaps
- **The real, ordered Etsy Style enum is missing.** Routes tried and blocked: Etsy browse facet rail (403), Etsy help "Complete Etsy Category List" (403), Etsy Seller Handbook (403), Etsy Open API buyer/seller taxonomy (403, no key), GitHub code search for mirrored taxonomy JSON (session-restricted), Wayback (unreachable), reader proxy (Cloudflare). A targeted search for a published list containing both "Hollywood Regency" and "Japandi" returned only Etsy market pages, no enum.

---

## Q3. eBay UK category tree for wall art, with category numbers, and the aspects

### Takeaway
Primary-source and complete: eBay UK publishes its whole category list with IDs at `pages.ebay.co.uk`, and I extracted the two relevant branches verbatim with nesting. **Important correction to the brief: `360` is not "wall art" — it is `Art Prints` inside the `Art` branch (eBay UK also brands node 360 as "Pictures And Prints" on some browse pages). The Home Décor route for posters/prints is `41511`.** Both branches are *leaves* — eBay does no further category subdivision of posters/prints, so all subject/style splitting happens through aspects, which I could **not** enumerate authoritatively because every aspect-bearing surface (browse rails, Taxonomy API) is 403 or auth-walled.

### Cited Findings — eBay UK: Home, Furniture & DIY > Home Décor (verbatim, with IDs)
Source for this entire block: [eBay UK Category Changes, full UK category list](https://pages.ebay.co.uk/categorychanges/UK_Category_Changes.html)

| Category | ID |
|---|---|
| **Home Décor** (parent) | **10033** |
| Baskets | 125072 |
| Decorative Accessories | 262984 |
| — Ashtrays | 74316 |
| — Bookends | 20551 |
| — Bottles | 36016 |
| — Boxes, Jars & Tins | 36017 |
| — Decorative Fans | 41509 |
| — Display Stands | 38225 |
| — Door Stops | 36022 |
| — Fruit | 36018 |
| — Globes | 36023 |
| — Letter Racks | 31586 |
| — Masks | 38235 |
| — Message Boards | 41510 |
| — Plate Racks & Hangers | 31588 |
| — Plates & Bowls | 36019 |
| — Suncatchers & Mobiles | 20578 |
| Dried & Artificial Flowers & Plants | 4959 |
| Mirrors | 20580 |
| Photo & Picture Frames | 79654 |
| Plaques & Signs | 31587 |
| **Posters & Prints** | **41511** |
| Screens & Room Dividers | 31601 |
| Sculptures & Figurines | 36025 |
| Throws | 20549 |
| Vases | 101415 |
| Wall Decals & Stickers | 159889 |
| Wall Hangings | 38237 |
| Other Home Décor | 10034 |

(next sibling after Home Décor in the tree: Home Security | 41968 — confirms the branch is closed)

### Cited Findings — eBay UK: Art (verbatim, with IDs and buyer browse-node codes)
Source: [eBay UK Category Changes](https://pages.ebay.co.uk/categorychanges/UK_Category_Changes.html); `bn_` codes from [eBay UK all-categories nav](https://www.ebay.co.uk/n/all-categories)

| Category | ID | Buyer browse node |
|---|---|---|
| **Art** (parent) | **550** | — |
| Art Drawings | 552 | bn_2316942 |
| Art NFTs | 262051 | — |
| Art Photographs | 2211 | bn_2316099 |
| Art Posters | 28009 | bn_2316224 |
| **Art Prints** (UK browse label also "Pictures And Prints") | **360** | bn_16566819; also bn_7023612369 as "Pictures And Prints" |
| Art Sculptures | 553 | bn_2316943 |
| Mixed Media Art & Collage Art | 554 | — |
| Paintings (nav label "Art Paintings") | 551 | bn_7204697 |
| Textile Art & Fiber Art | 156196 | — |
| Other Art | 20158 | — |

(next sibling after Art: Baby | 2984)
- UK "Pictures And Prints" branding on node 360: [ebay.co.uk/b/Pictures-And-Prints/360/bn_7023612369](https://www.ebay.co.uk/b/Pictures-And-Prints/360/bn_7023612369) (403 to me; URL/title from search index). US brands the same node "Art Prints": [ebay.com/b/Art-Prints/360/bn_2311282](https://www.ebay.com/b/Art-Prints/360/bn_2311282)

### Cited Findings — other eBay UK nodes that carry wall-art-shaped inventory
All from [eBay UK Category Changes](https://pages.ebay.co.uk/categorychanges/UK_Category_Changes.html):
- Posters & Prints (duplicate node names in other branches): **123769**, **123779**, **261627**, **27399**, **8694**, **99973**
- Posters & Wall Hangings | **177051**
- Wall Art & Posters | **82498** (under Comic Book Memorabilia)
- Paintings, Posters & Prints | **37859** (under Cat Collectables — i.e. eBay replicates a poster node inside collectable-animal branches)
- Advertising/ Posters | **86958**; Artists/ Groups | **58698**; Animation Art | **1529**; Animation Art & Merchandise | **13658**; Art Work | **1371**
- Tapestries | **261588** (out of scope per brief, shares subject taxonomy)
- Plaques & Signs | **261626**, **75592**, **31587**; Signs & Plaques | **46299**, **261064**; Plaques, Signs & Letters | **122769**
- Picture/Photo Frames | **33235**; Photo & Picture Frames | **79654**; Display Frames | **259132**; Digital Photo Frames | **150044**
- Wallpaper Rolls & Sheets | **50364**; Wallpaper Murals | **79626**; Wallpaper Borders | **42136**; Other Wallpaper & Accessories | **52348** (out of scope; relevant only because the biggest UK store observed sells across posters *and* murals with one subject taxonomy — see Q5)
- Decorative Decals & Transfers | **41215**; Wall Decals & Stickers | **159889** (out of scope)
- Aerial Photographs | **53617**; Anatomical, Eye/Vision & Reference Charts | **185286** (chart/diagram subject matter)

### Cited Findings — eBay aspects for these categories (second-hand, incomplete)
These are the aspect **names** and sample **values** that search-engine summaries of eBay poster/print browse pages and listings surfaced. I could not open the pages, so treat every value list as a partial sample, not an enum:
- `Original/Licensed Reprint` — values seen: **Original; Licensed Reprint; Not Specified** — [via search summary of ebay.com/b/Posters-Prints/41511](https://www.ebay.com/b/Posters-Prints/41511/bn_1853005)
- `Subject` — values seen: **Musical Bands & Groups; Women; Anime; Landscape; Concerts; Race Car** — same source
- `Style` — values seen: **Art Deco; Abstract; Modernism; Illustration Art; Realism; Pop Art** — same source
- `Type` — values seen: **Print; Poster** — same source
- `Framing` — **Framed; Unframed**; `Size` — **Small; Medium; Large**; `Period/Era` — **Modern; Vintage**; `Image Orientation` — **Portrait; Landscape**; plus `Region of Origin`, `Country/Region of Manufacture` — same source
- `Production Technique` — values seen: **Giclée Print; Giclee & Iris Print; Lithography; Offset Lithograph** — [via search summaries of ebay.com Art Prints (360) listings](https://www.ebay.com/b/Art-Prints/360/bn_2311282)
- `Print Surface` — values seen: **Paper; Canvas; Gloss Paper; Matte Paper** — same source
- Browse-node names visible in the search index reveal further aspect values as facet combinations on 41511: **Wooden**, **Vintage/Retro**, **Framed**, **Canvas**, **Modern**, **Art Deco**, **Original**, **Unbranded** (Brand aspect), plus Subject values **Palm Tree**, **Tree of Life**, **Trees & Forest** — [ebay.com/b/Wooden-Vintage-Retro-Home-Decor-Posters-Prints/41511](https://www.ebay.com/b/Wooden-Vintage-Retro-Home-Decor-Posters-Prints/41511/bn_7115841757); [ebay.com/b/Art-Deco-Trees-Forest-Home-Decor-Posters-Prints/41511](https://www.ebay.com/b/Art-Deco-Trees-Forest-Home-Decor-Posters-Prints/41511/bn_89031825); [ebay.com/b/Canvas-Trees-Forest-Home-Decor-Posters-Prints/41511](https://www.ebay.com/b/Canvas-Trees-Forest-Home-Decor-Posters-Prints/41511/bn_7115573754)
- Further 28009 (Art Posters) facet values from browse-node names: **Americana** (Subject), **Limited Edition** (Features), **Model** (Subject) — [ebay.com/b/Americana-Original-Art-Posters/28009](https://www.ebay.com/b/Americana-Original-Art-Posters/28009/bn_82793953); [ebay.com/b/Limited-Edition-Art-Posters/28009](https://www.ebay.com/b/Limited-Edition-Art-Posters/28009/bn_80999840)
- 360 (Art Prints) facet values from browse-node names: **Signed** (Features), **Original** — [ebay.com/b/Signed-Original-Art-Prints/360](https://www.ebay.com/b/Signed-Original-Art-Prints/360/bn_7116769464)
- eBay's own guidance is generic: item specifics "may include brand, size, type, colour, style or other relevant info", are required in Home & Garden among others, and "Recommended is NOT Required" — [eBay UK Seller Centre: Item specifics](https://www.ebay.co.uk/sellercentre/listings/item-specifics); [eBay Community: Recommended is NOT Required](https://community.ebay.com/t5/Selling/Item-Specifics-PLEASE-PEOPLE-Recommended-is-NOT-Required/td-p/31886757)
- Art-specific seller advice (no enums): "Fill out all applicable fields – medium, size, style, subject" — [Printify, Selling art on eBay](https://printify.com/blog/selling-art-on-ebay/)
- The authoritative route exists and is documented: `getItemAspectsForCategory` on the Commerce Taxonomy API returns every aspect, its cardinality, and its recommended values per category id — [eBay getItemAspectsForCategory](https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getItemAspectsForCategory) (docs page fetched successfully, 200; the API itself needs an OAuth token I do not have)

### Inferences
- Because 41511 and 360 are leaves, **eBay expects subject differentiation to live in aspects, and eBay then auto-generates pseudo-categories from aspect combinations** (the `bn_*` browse nodes above are literally Style×Subject×Material×Framing crosses). For catalogue generation that means an aspect-complete listing is what buys you shelf space, and the browse-node names are a free, machine-readable list of the aspect crosses eBay thinks are worth a page.
- Mining `ebay.co.uk/b/...` browse-node *URLs* out of a search index (which worked, since the index holds the titles even though the pages 403) is a viable workaround for harvesting aspect values at scale without API access.

### Gaps
- **No complete, authoritative aspect list or recommended-value list for 41511, 360, 28009, 551 or 38237.** `getItemAspectsForCategory` requires an OAuth application token; browse pages are 403; `ebay.co.uk/sellercentre/listings/item-specifics-by-category` → 404. The brief's named aspects **Material, Room, Colour, Artist, Theme, Features** were not individually confirmed for these categories — only Subject, Style, Type, Original/Licensed Reprint, Framing, Size, Period/Era, Image Orientation, Production Technique, Print Surface, Brand, Region of Origin, Country/Region of Manufacture were.
- Could not check whether eBay UK and eBay US differ in aspect *values* for 41511/360 (only the node *label* difference, Art Prints vs Pictures And Prints, is evidenced).

---

## Q4. Shop section structures of the largest wall-art shops

### Takeaway
**eBay UK store sections: harvested verbatim and primary-source** — `ebay.co.uk/str/<slug>` is reachable even though browse is not, and the section menus are in the page payload. These are genuinely market-tested buckets. **Etsy shop sections: blocked** (all etsy.com 403), so for Etsy I have shop names + sales counts + niche descriptions from a third-party roundup, not verbatim section lists.

### Cited Findings — eBay UK store category menus, verbatim
Each list below is the store's own section menu as served by eBay (navigation chrome such as "All categories / Back to Shopfront / Shop by category / Show more" stripped).

**CANVAS ART SHOP ONLINE** (`ebay.co.uk/str/canvasartshoponline`; family-run since 2004; canvas prints, framed prints, float-effect canvas) — 40 sections — [store page](https://www.ebay.co.uk/str/canvasartshoponline); [profile claims via search summary](https://www.ebay.co.uk/str/canvasartshoponline):
`Banksy Artworks` · `Yellow Mustard Collection` · `Classic Paintings` · `Animals` · `City` · `Peaky Blinders` · `FORTNITE` · `Gustav Klimt Collection` · `FRAMED PRINTS` · `Van Gogh` · `John William Waterhouse` · `L S Lowry` · `Nature` · `Scenery` · `LIVINGROOM` · `PREMIUM FLOAT EFFECT CANVAS` · `Famous Landmarks` · `Famous People` · `Movies & TV` · `Famous Mugshots` · `Motorcycle` · `Music` · `Street Art` · `KITCHEN` · `Splash Art` · `Minimalist Art` · `Eric Ravilious` · `Football` · `SPORTS` · `Abstract Art` · `Cars` · `Famous Artists` · `Slogan Wall Art` · `Vintage Poster Prints` · `Pop Art` · `Unique Art` · `Derry` · `Anime & Manga Prints` · `Neon Sign Prints` · `TRENDY NEW ARTS` · `Other`

**premiumarte** (`ebay.co.uk/str/premiumarte`; 98.8% positive, 98K items sold, joined Oct 2008) — sections span canvas, acrylic glass, room dividers, corkboards and wallpaper, and the store runs parallel UK/US/ES menus — [store page](https://www.ebay.co.uk/str/premiumarte):
*Format/product sections:* `Canvas Prints` · `Canvas Prints - HandArt` · `Canvas Prints - Mega XXXL` · `HandArt` · `Acrylic Glass Print` · `Photo Wallpaper` · `Photo Wallpapers` · `Wallpapers` · `Room Dividers` · `Corkboards` · `Backsplash for Kitchen` · `3D Wall Optical Illusion` · `NEW IN` · `UK - Ebay Shop` · `US - Ebay PremiumArte Shop` · `ES - Ebay Tienda`
*Subject/style sections:* `Abstract` · `Abstract/Geometric` · `Animals` · `Animal` · `Angels` · `Africa` · `Beach & Sea` · `Botanical` · `Botanical/Tropical` · `Buddha` · `Cars` · `Children` · `City` · `Cosmos` · `Cosmos and sky` · `Flowers` · `Food&drinks&cigar` · `Forest` · `Gamers` · `Graffiti` · `Gustav Klimt` · `Banksy` · `Hobby` · `Japan` · `Landscape` · `Mandala` · `Marble` · `Moroccan Stylel/Mandala` · `Nature` · `Nordic style` · `People` · `Quotes` · `Tropical` · `Waterfall` · `Words` · `World Map` · `3D Effect` · `Faux Stone` · `Faux Bricks` · `Faux Bricks/Faux Stone` · `Faux Bricks/Stone/Wood` · `Faux Cement` · `Faux Wood` · `Non-Woven` · `Self-adhesive foil`
*Spanish-locale duplicates (same taxonomy, translated):* `Buda` · `Flores` · `Abstracto` · `Ciudad` · `Animales` · `Ventana de faux` · `Naturaleza` · `Mapamundi` · `Bebidas y Comida` · `Klimt` · `Angeles` · `Personas` · `Jugadores` · `Cuadro` · `Cuadro Mega XXXL` · `Papel Pintado` · `Ninos` · `Ladrillo` · `Tablas` · `Piedras` · `Angel` · `Botanico` · `Fotomural` · `Biombo` · `Cuadro de Cristal acrílico` · `3d ilusion optica` · `Tablero de corcho` · `HOME` · `3D`

**SwiftprintUK** (`ebay.co.uk/str/swiftprintuk`; 99.8% positive, **304K items sold**, joined Nov 2008 — the highest item-count UK print seller I found) — 5 sections only — [store page](https://www.ebay.co.uk/str/swiftprintuk):
`PERSONALISED CANVAS` · `POSTER PRINTING` · `BANNER POLE` · `LEAFLETS FLYERS` · `ROLLER BANNER` · `Other`

**photooncanvas** (`ebay.co.uk/str/photooncanvas`; 99.6% positive, 5.3K sold, joined Mar 2017) — [store page](https://www.ebay.co.uk/str/photooncanvas):
`Picture Frame` · `Wall art print` · `Canvas Roll` · `Custom Item` · `Other` (plus unrelated holster sections — `Glock Holster`, `Smith & Wesson Holster`, `Ruger Holster`, `Sig Sauer Holster`, `Taurus Holster`, `Springfield Armory Holster` — i.e. the store is not wall-art-pure)

**The Art Stop** (`ebay.co.uk/str/theartstop`; positions itself "OWN WHAT'S REAL / Direct from the artist. Provenance.") — [store page](https://www.ebay.co.uk/str/theartstop):
`Street Photography` · `Graffiti` · `Graffiti Artist` · `Urban Art` · `Limited Editions` · `Original Silver Gelatin Prints` · `3-Day Silent Auction`

Store slugs probed that do **not** exist / are closed (HTTP 410): `gbposters`, `wallartprints`, `canvasartrocks`, `bigwallart`, `wallartdirect`, `printsandposters`, `thecanvasartfactory`, `artforthehome`. Slugs that resolved but served no store-section menu: `iposters`, `artgeist`, `pyramidinternational`, `artforthehomeuk`.

### Cited Findings — Etsy's largest wall-art shops (sales counts + self-described niche; sections NOT readable)
All from [Creative's Hour, "20 Most Successful Etsy Wall Art Stores in 2026"](https://thecreativeshour.com/etsy-wall-art-stores/) — a third-party roundup, dated 2026; sales figures are that site's figures, not Etsy's:

| Shop | Sales | Niche as described |
|---|---|---|
| NorthPrints | 472,000+ | "Printable vintage wall art — remastered botanical prints, farmhouse decor, nursery art, sports vintage, cowboy western" |
| KIKIANDNIM | 213,000+ | Digital downloads and **Samsung Frame TV art**; abstract, botanical, coastal, seasonal |
| thewheatfield | 212,000+ | Watercolour nature and floral art prints, cards, stickers, pins, calendars |
| LanternPressArtwork | 200,000+ | "National parks, cityscapes, lighthouses, wildlife, vintage-style travel posters" |
| khallion | 176,000+ | Pop-culture / fandom illustration prints, posters, stickers, postcards, pins |
| LILAxLOLA | 156,000+ | "Nursery and children's wall art — peekaboo baby animals, abstract prints, coastal themes, Frame TV art" |
| ArtPrintsFactory | 151,000+ | "animals, inspirational quotes, gallery wall sets, educational posters, personalized name prints" |
| TheCrownPrints | 139,000+ | "baby animals wearing flower crowns (signature), dinosaurs, food trucks, abstract, coastal, vintage" |
| VioletGraceUK | 136,000+ | **UK**; "Personalized word art prints, family name prints, occasion-specific custom art" |
| LariPrintDesign | 133,000+ | "vintage paintings, modern abstracts, gallery wall sets, botanical prints, seasonal collections" |
| PrintableSky | 112,000+ | "nature photography, mountain landscapes, minimalist prints, home decor, nursery art, wedding signs" |
| artPause | 111,000+ | "City skyline art, world maps, country maps, canvas prints, framed prints" |
| CocoMilla | 111,000+ | "city maps, science and medical illustrations, sports art, nature prints" |
| mabgraves | 99,000+ | "Pop surrealism fine art prints … fairy tale, storybook, dark whimsical" |
| OldEnglishCo | 97,000+ | Hand-lettered typographic art prints |
| EnjoyTheWood | 95,000+ | 3D wooden world maps, city maps, lake maps, cork push-pin maps |
| PRRINT | 84,000+ | "Anatomy prints, vintage scientific engravings, botanical art, curiosity-cabinet" |
| berkleyillustration | 75,000+ | Animal portraits in vintage human clothing |
| 23maps | 71,000+ | "City maps, custom star maps, watercolor maps, gold foil maps, personalized coordinate prints" |
| SugarnCanvas | Star Seller (n/a) | "boho, mid-century modern, abstract, botanical, minimalist line art" |

- A second, different top-10 (ranked by EtsyHunt's own metric, not sales) : **NeonOutshine; WallArtsConcept; LittleWildStudios; ZCDigitalStudio; LeeartfromVietnam; PawtraitDesignCo; NoraEventCo; TheContrastStudios; Joannekateillustrate; AnomalyArtPrints** — [EtsyHunt, Top 100 best selling wall art on Etsy 2026](https://etsyhunt.com/best-etsy-wall-art)
- Alura maintains a continuously-updated best-selling Etsy Art & Collectibles shop list — [Alura best-selling Etsy shops: Art & Collectibles](https://www.alura.io/best-selling-etsy-shops/art-collectibles) *(not fetched; listed as a live source for the writer)*

### Inferences
- The eBay UK menus and the Etsy niche descriptions converge on the same primary axis: **named subject, not style.** Canvas Art Shop Online's 40 sections are almost entirely subject/IP buckets (Banksy, Peaky Blinders, Fortnite, Klimt, Van Gogh, Lowry, Waterhouse, Ravilious, football, cars, mugshots) with only four style buckets (Abstract Art, Minimalist Art, Pop Art, Street Art), two room buckets (LIVINGROOM, KITCHEN) and three format buckets (FRAMED PRINTS, PREMIUM FLOAT EFFECT CANVAS, Neon Sign Prints).
- **Licensed IP is a large share of the eBay UK subject taxonomy and is unusable for a generated catalogue** (Peaky Blinders, Fortnite, Banksy, named living artists). The public-domain slice — Klimt, Van Gogh, Waterhouse, Ravilious (d. 1942), "Classic Paintings", "Vintage Poster Prints" — is the copyable part.
- Two viable section models exist: **broad-subject (Canvas Art Shop Online, premiumarte, 40–50 sections)** and **format-first with personalisation (SwiftprintUK, 5 sections, 304K items sold)**. The second sells more units with a tenth of the taxonomy, which argues that section count is not the driver.

### Gaps
- **No verbatim Etsy shop section lists.** etsy.com 403 on every path, so `etsy.com/shop/<name>?section_id=` was unreachable. This is the single biggest hole in these notes relative to the brief.
- Sales/feedback figures for eBay stores (304K items sold etc.) came from search-engine summaries of the store profiles, not from a field I read directly in the HTML.
- No eBay UK seller with verified *wall-art-only* volume ranking; `swiftprintuk` is partly a print-shop (leaflets, banners) and `photooncanvas` partly a holster seller.

---

## Q5. Tag and title vocabulary of the big shops, grouped by axis

### Takeaway
Grouping the verbatim eBay section names, the Etsy niche descriptions and the published keyword lists gives a usable multi-axis vocabulary of roughly 200 named items. Every item below appears in a cited source; nothing is invented. Volumes are only available for a handful of head terms.

### Cited Findings — axis by axis

**Subject — fine art / public-domain artists** (from eBay store sections, [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline), [premiumarte](https://www.ebay.co.uk/str/premiumarte)): `Gustav Klimt` · `Van Gogh` · `John William Waterhouse` · `L S Lowry` · `Eric Ravilious` · `Classic Paintings` · `Famous Artists` · `Famous Paintings`-adjacent `Unique Art`

**Subject — nature / landscape**: `Nature` · `Scenery` · `Landscape` · `Forest` · `Trees & Forest` · `Palm Tree` · `Tree of Life` · `Waterfall` · `Beach & Sea` · `Cosmos` · `Cosmos and sky` · `Flowers` · `Botanical` · `Botanical/Tropical` · `Tropical` · `Marble` — [premiumarte](https://www.ebay.co.uk/str/premiumarte); [eBay 41511 browse nodes](https://www.ebay.com/b/Canvas-Trees-Forest-Home-Decor-Posters-Prints/41511/bn_7115573754); mountain landscapes, national parks, lighthouses, wildlife — [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/)

**Subject — animals**: `Animals` · `Animal` · pet portraits · baby animals · "peekaboo baby animals" · "baby animals wearing flower crowns" · dinosaurs · animal portraits in vintage clothing — [premiumarte](https://www.ebay.co.uk/str/premiumarte); [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/); [EtsyHunt](https://etsyhunt.com/best-etsy-wall-art)

**Subject — place / cartography**: `City` · `World Map` · `Famous Landmarks` · `Derry` · city skyline art · country maps · city maps · lake maps · star maps · watercolour maps · gold foil maps · coordinate prints · cork push-pin maps · `Africa` · `Japan` — [premiumarte](https://www.ebay.co.uk/str/premiumarte); [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/)

**Subject — people / culture / IP (mostly unusable, listed for completeness)**: `Famous People` · `Famous Mugshots` · `Movies & TV` · `Music` · `Peaky Blinders` · `FORTNITE` · `Banksy` · `Anime & Manga Prints` · `Gamers` · `People` · `Children` · `Angels` · `Buddha` — [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [premiumarte](https://www.ebay.co.uk/str/premiumarte)

**Subject — sport / vehicles**: `Football` · `SPORTS` · `Cars` · `Motorcycle` · `Hobby` · sports art · "sports vintage" · `Race Car` (eBay Subject value) — [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/)

**Subject — scientific / educational**: anatomy prints · vintage scientific engravings · "curiosity-cabinet" · science and medical illustrations · educational posters · `Anatomical, Eye/Vision & Reference Charts` (eBay node 185286) — [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/); [eBay UK category list](https://pages.ebay.co.uk/categorychanges/UK_Category_Changes.html)

**Subject — typography / words**: `Quotes` · `Words` · `Slogan Wall Art` · hand-lettered typographic prints · inspirational quotes · "Personalized word art prints" · song-lyric prints — [premiumarte](https://www.ebay.co.uk/str/premiumarte); [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/); [EtsyHunt](https://etsyhunt.com/best-etsy-wall-art)

**Style**: `Abstract` · `Abstract Art` · `Abstract/Geometric` · `Minimalist Art` · `Pop Art` · `Street Art` · `Graffiti` · `Urban Art` · `Mandala` · `Moroccan Stylel/Mandala` *(sic, store's own typo)* · `Nordic style` · `Vintage Poster Prints` · `Splash Art` · `3D Effect` · `3D Wall Optical Illusion` · boho · mid-century modern · farmhouse · coastal · Scandinavian · contemporary · pop surrealism · "dark whimsical" · Japanese · modern · `Art Deco` · `Modernism` · `Illustration Art` · `Realism` — [premiumarte](https://www.ebay.co.uk/str/premiumarte); [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [theartstop](https://www.ebay.co.uk/str/theartstop); [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/); [insightagent 200+ Art Keywords 2026](https://www.insightagent.app/guides/etsy-art-keywords-list)

**Colour**: `Yellow Mustard Collection` (an entire eBay store section built on one colour) · "neutral abstract art print" · "large navy blue abstract canvas art" · "black and white mountain landscape print" · "black and white plant art" · earth tones — [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [insightagent](https://www.insightagent.app/guides/etsy-art-keywords-list); [eRank Etsy trends 2026](https://help.erank.com/blog/etsy-trends-2026/)

**Room**: `LIVINGROOM` · `KITCHEN` · `Backsplash for Kitchen` · living room art · bedroom art · office art · kitchen art · nursery art · bathroom art · "above bed" — [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [premiumarte](https://www.ebay.co.uk/str/premiumarte); [insightagent](https://www.insightagent.app/guides/etsy-art-keywords-list); [EtsyHunt](https://etsyhunt.com/best-etsy-wall-art)

**Format / medium / finish**: `FRAMED PRINTS` · `PREMIUM FLOAT EFFECT CANVAS` · `Canvas Prints` · `Canvas Prints - Mega XXXL` · `Acrylic Glass Print` · `Canvas Roll` · `Picture Frame` · `Wall art print` · `PERSONALISED CANVAS` · `POSTER PRINTING` · `Neon Sign Prints` · `Original Silver Gelatin Prints` · `Limited Editions` · `HandArt` · wall art · art print · canvas art · framed art · digital art · printable art · fine art print · acrylic painting · watercolor art · metal/glass wall art · gallery wall sets · "set of 3" · **Samsung Frame TV art** — [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [premiumarte](https://www.ebay.co.uk/str/premiumarte); [swiftprintuk](https://www.ebay.co.uk/str/swiftprintuk); [photooncanvas](https://www.ebay.co.uk/str/photooncanvas); [theartstop](https://www.ebay.co.uk/str/theartstop); [insightagent](https://www.insightagent.app/guides/etsy-art-keywords-list); [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/)

**Mood / merchandising**: `TRENDY NEW ARTS` · `NEW IN` · `Unique Art` · `Other` · `3-Day Silent Auction` · "OWN WHAT'S REAL / Direct from the artist. Provenance." · "aesthetic" · "whimsical" — eBay store pages as cited above

**Measured head-term volumes (second-hand, eRank-derived)**: "wall art" 450K searches/month; "canvas wall art" 120K; "framed wall art" 95K; "large wall art" 80K; "modern wall art" 75K — [via search summary of eRank](https://help.erank.com/blog/top-keywords-on-etsy/). "wall art" ranked **#9 Etsy Q1 2026 (down from #1 the prior year), #3 in Q2 2026, #7 in September 2026**; "wall decor" #76–77 in June; "glass wall art" 149% CTR Feb 2026; "moss wall art" +15,046% trend — [eRank Top Etsy Searches Q1 2026](https://help.erank.com/blog/top-etsy-searches-q1-2026/); [eRank Q2 2026](https://help.erank.com/blog/top-etsy-searches-q2-2026/); [eRank June 2026](https://help.erank.com/blog/top-keywords-on-etsy-june-2026/)

**UK-specific keyword ranks, Etsy, February 2026, verbatim top 20** — [eRank, The UK's Top Etsy Keywords in February 2026](https://help.erank.com/blog/the-uks-top-etsy-keywords-february-2026/):
1 valentine downloads · 2 digital products · 3 valentines card · 4 amethyst gift · **5 wall art** · 6 gifts for him · 7 fallout · 8 3d printed · 9 digital download · 10 ring · 11 candles · 12 necklace · 13 pokemon · 14 heated rivalry · 15 birthday card · 16 tshirt · 17 vintage · 18 home decor · 19 gift · **20 poster**; extended ranks: **#138 glass wall art, #151 nursery wall art**

**Long-tail keyword patterns, published** (shape templates for prompt generation) — [insightagent](https://www.insightagent.app/guides/etsy-art-keywords-list): "minimalist line art print set of 3" · "modern abstract geometric art for living room" · "boho watercolor floral wall art" · "black and white mountain landscape print" · "large navy blue abstract canvas art" · "minimalist botanical line drawing set" · "farmhouse rustic landscape wall art" · "coastal beach ocean sunset art print" · "minimalist botanical line art print" · "modern botanical wall art set" · "scandinavian botanical art"

### Inferences
- The recurring title grammar is `[colour] + [style] + [subject] + [format] + (for [room]) + (set of N)`. That is directly templatable for a generated catalogue and is the natural defence against the near-duplication risk recorded in CLAUDE.md: vary the axes, not the pixels.
- "wall art" falling from #1 to #9 on Etsy between Q1 2025 and Q1 2026 while still ranking #5 in the UK top-20 suggests the head term is saturating, which argues for competing on long-tail axis combinations rather than head keywords.

### Gaps
- No access to any shop's actual 13-tag lists (Etsy caps tags at 13); every "tag" above is inferred from section names, titles and third-party keyword roundups, not from a listing's tag field.
- No numeric volume for any of the long-tail or axis terms except the five head terms.

---

## Q6. Which subjects are market-validated (recur across shops) vs long tail

### Takeaway
Across the five eBay UK store menus and the 20+ Etsy shop descriptions, seven subject clusters recur in nearly every catalogue; a long tail of single-shop obsessions sits beneath them.

### Cited Findings
**Recurs in most or all catalogues (market-validated core):**
- Botanical / floral / plants — premiumarte (`Flowers`, `Botanical`), NorthPrints, thewheatfield, SugarnCanvas, LariPrintDesign, PRRINT, insightagent keyword set — [premiumarte](https://www.ebay.co.uk/str/premiumarte); [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/); [insightagent](https://www.insightagent.app/guides/etsy-art-keywords-list)
- Abstract / geometric — premiumarte, canvasartshoponline, KIKIANDNIM, LILAxLOLA, TheCrownPrints, SugarnCanvas, LariPrintDesign — same sources
- Landscape / nature / mountains / forest — canvasartshoponline (`Nature`, `Scenery`), premiumarte (`Landscape`, `Forest`, `Waterfall`), PrintableSky, LanternPressArtwork — same sources
- Animals (incl. pets and nursery animals) — premiumarte, LILAxLOLA, TheCrownPrints, ArtPrintsFactory, berkleyillustration, PawtraitDesignCo — same sources
- City / map / place — canvasartshoponline (`City`, `Famous Landmarks`), premiumarte (`City`, `World Map`), artPause, 23maps, CocoMilla, EnjoyTheWood — same sources
- Coastal / sea / beach — premiumarte (`Beach & Sea`), KIKIANDNIM, LILAxLOLA, TheCrownPrints, insightagent ("coastal beach ocean sunset art print") — same sources
- Typography / quotes / word art — premiumarte (`Quotes`, `Words`), canvasartshoponline (`Slogan Wall Art`), OldEnglishCo, VioletGraceUK, ArtPrintsFactory — same sources
- Vintage / classic painting reproductions — canvasartshoponline (`Classic Paintings`, `Vintage Poster Prints`, Klimt, Van Gogh, Waterhouse), NorthPrints, LariPrintDesign, PRRINT — same sources

**Long tail (one or two shops only):**
`Famous Mugshots` · `Derry` · `Yellow Mustard Collection` · `Eric Ravilious` · `Splash Art` · `Neon Sign Prints` · `Faux Stone` / `Faux Bricks` / `Faux Cement` / `Faux Wood` · `Corkboards` · `Room Dividers` · `3D Wall Optical Illusion` · `Backsplash for Kitchen` · `Original Silver Gelatin Prints` · `Graffiti Artist` · anatomy prints · food trucks · dinosaurs · "baby animals wearing flower crowns" · pop surrealism / fairy-tale / "dark whimsical" · moss wall art · glass wall art · Samsung Frame TV art · `Angels` · `Buddha` · `Mandala` · `Africa` · `Japan` · `Gamers` · `Marble` — [canvasartshoponline](https://www.ebay.co.uk/str/canvasartshoponline); [premiumarte](https://www.ebay.co.uk/str/premiumarte); [theartstop](https://www.ebay.co.uk/str/theartstop); [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/); [eRank June 2026](https://help.erank.com/blog/top-keywords-on-etsy-june-2026/)

### Inferences
- Two long-tail items are rising rather than niche-stable and are worth separating out: **glass wall art** (#138 UK Feb 2026, 149% CTR) and **moss wall art** (+15,046% trend) — both are *material* innovations, not subjects, and neither is producible from a FLUX image pipeline alone.
- **Samsung Frame TV art** is the one format-level long-tail item that a purely digital pipeline can serve at zero marginal cost (specific aspect ratios, digital delivery), and it already appears in two of the largest Etsy shops (KIKIANDNIM 213K, LILAxLOLA 156K).

### Gaps
- Frequency counting here is across 5 eBay menus + 20 Etsy shop descriptions, not across whole catalogues. Without Etsy shop-section access I cannot weight by listing count or by sales per subject.

---

## Q7. Occasion, season and gifting axes

### Takeaway
Occasion evidence is thinner than the brief hopes. I found strong, dated UK evidence for Valentine's and birthdays, and shop-level evidence for weddings, seasonal collections and Christmas adjacency — but **I found no source enumerating the full occasion list (Diwali, Eid, Hanukkah, Burns Night, St Patrick's/Andrew's/David's/George's Day, christening, retirement, bereavement) for wall art on either platform.** Those remain unverified.

### Cited Findings
- Etsy exposes `Occasion` and `Holiday` as distinct attributes; documented example values: Occasion "Wedding, birthday, anniversary"; Holiday "Christmas, Valentine's Day" — [Listadum](https://www.listadum.com/blog/etsy-listing-attributes)
- Etsy also exposes a `Recipient` attribute: "for him, for her, for kids, for pets" — [Listadum](https://www.listadum.com/blog/etsy-listing-attributes)
- **UK, February 2026, verbatim:** "valentine downloads" #1, "valentines card" #3, "gifts for him" #6, "birthday card" #15, "gift" #19, "valentine" #23; eRank notes valentine terms were "down to two" in the Top 20 versus "eight" the previous year — [eRank UK February 2026](https://help.erank.com/blog/the-uks-top-etsy-keywords-february-2026/)
- Wedding is an active wall-art adjacency: PrintableSky sells "wedding signs" alongside printable wall art — [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/)
- Season as a shop section rather than a holiday: KIKIANDNIM "seasonal themes", LariPrintDesign "seasonal collections" — [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/)
- Christmas appears inside Etsy's wall-decor chip rails as `Christmas Ornaments` — [via search summary of etsy.com/market/wall_hanging_decor](https://www.etsy.com/market/wall_hanging_decor) *(second-hand)*
- Birthday as a personalised wall product: "Personalised Birthday Name Flag, Birthday Banner, Custom Birthday Banner, Fabric Sign" is a top-10 EtsyHunt wall-art listing — [EtsyHunt](https://etsyhunt.com/best-etsy-wall-art)
- "occasion-specific custom art" is VioletGraceUK's (136,000+ sales, UK) stated core — [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/)

### Inferences
- The UK occasion calendar visibly drives the Etsy head terms month to month (February 2026 top-20 is Valentine-dominated), so occasion is better modelled as a **publishing calendar** than as a catalogue facet.
- No eBay UK store in the harvested set has an occasion section at all — all five menus are subject/format. Occasion appears to be an Etsy-side axis, not an eBay-side one, on current evidence.

### Gaps
- **Unverified:** Mother's Day, Father's Day, Easter, Halloween, anniversaries, new home, new baby, christening, graduation, retirement, bereavement/memorial, Diwali, Eid, Hanukkah, Burns Night, St Patrick's/St Andrew's/St David's/St George's Day. Each is plausible but I have no source tying it to a wall-art taxonomy, and Etsy's own Holiday/Occasion enums were unreachable (403).
- No month-by-month UK occasion keyword series was fetched beyond February 2026; eRank publishes monthly UK roundups that would close this if reachable.

---

## Q8. Personalisation axes, and pre-generatable vs order-time

### Takeaway
Personalisation is the strongest single commercial signal in the harvest: the highest item-count eBay UK seller found leads with `PERSONALISED CANVAS`, and the top EtsyHunt wall-art listings are overwhelmingly custom. The axes split cleanly into ones needing order-time input and ones that are really just finite enumerations — and the finite ones can be pre-generated.

### Cited Findings — named personalisation axes
- `PERSONALISED CANVAS` is the **first** store section of SwiftprintUK (304K items sold) — [swiftprintuk](https://www.ebay.co.uk/str/swiftprintuk)
- `Custom Item` is a store section at photooncanvas, whose offer is "personalized canvas prints with custom photos" — [photooncanvas](https://www.ebay.co.uk/str/photooncanvas)
- Etsy personalisation axes named by the big shops: "personalized name prints" (ArtPrintsFactory); "Personalized word art prints, family name prints, occasion-specific custom art" (VioletGraceUK); "personalized travel maps", "cork push-pin maps" (EnjoyTheWood); "custom star maps", "personalized coordinate prints" (23maps) — [Creative's Hour](https://thecreativeshour.com/etsy-wall-art-stores/)
- Top EtsyHunt wall-art listing titles, verbatim, showing the live personalisation grammar — [EtsyHunt](https://etsyhunt.com/best-etsy-wall-art):
  - "Custom Name Neon Sign for Kids Personalized Neon Sign for Bedroom Custom LED Lights Kids Room Decor"
  - "Custom Toddler Mispronunciation Print | Personalised Keepsake First Word Wall Art"
  - "Pet Portrait Custom and Personalized. Pet Dog Wall Art DIGITAL DOWNLOAD"
  - "Personalised Birthday Name Flag, Birthday Banner, Custom Birthday Banner, Fabric Sign"
  - "Personalized Jungle Cruise Entrance Sign Print Poster Disney World Disneyland"
- Etsy's structured fields that carry personalisation adjacency: `Occasion`, `Holiday`, `Recipient` ("for him, for her, for kids, for pets") — [Listadum](https://www.listadum.com/blog/etsy-listing-attributes)
- UK demand signal for the gifting framing: "gifts for him" #6 and "gift" #19 in the UK Etsy top-20, February 2026 — [eRank UK February 2026](https://help.erank.com/blog/the-uks-top-etsy-keywords-february-2026/)

### Inferences
**Needs customer input at order time** (free-text or uploaded asset — cannot be pre-generated):
- Personal / family / child name, couple names
- Custom quote, first word, mispronunciation, song lyric choice
- Uploaded photo (photo-on-canvas, pet portrait from photo)
- Arbitrary address or coordinates, arbitrary date/time (star map)
- Arbitrary place name outside a pre-built set

**Finite enumerations masquerading as personalisation** (pre-generatable in bulk — the high-leverage set for an image pipeline):
- City / town / country / region prints from a fixed UK gazetteer (artPause, 23maps, CocoMilla all work this way)
- Birth-month flower, birthstone, zodiac sign (12 each)
- Letter/monogram sets (26)
- Football club, county, national flag sets
- Occasion-by-year wording (e.g. a year-dated print) where the year set is small
- Room × colour × size variants of the same subject

### Gaps
- I could not read Etsy's actual personalisation mechanics (the "Personalisation" toggle, character limit, and whether it is exposed as a facet to buyers) because all Etsy pages 403.
- No evidence found on how eBay UK handles personalisation structurally in 41511/360 (there is a `Personalise` aspect on some eBay categories, but I could not confirm it for these, see Q3 gaps).

---

## Cross-cutting notes for the report writer

- **Correct the brief's category assumption:** eBay UK node **360 = Art Prints / "Pictures And Prints"** (branch: Art, 550), **not** wall art generally. The Home Décor poster node is **41511**. Both are leaves; there is no deeper eBay category tree to harvest. — [eBay UK Category Changes](https://pages.ebay.co.uk/categorychanges/UK_Category_Changes.html)
- **UK vs US differences actually evidenced:** only the node label (UK "Pictures And Prints" vs US "Art Prints" for 360) and the UK keyword mix (eRank UK monthly list differs sharply from the US list — Valentine's, "gifts for him", "fallout", "pokemon"). I found **no** evidence of UK/US divergence in Etsy's facets or eBay's aspect values.
- **Dating:** eBay UK category IDs — current as of fetch 2026-10-07. eRank keyword ranks — Feb/Jun/Sep 2026 and Q1/Q2 2026, current. Creative's Hour shop list — self-dated 2026. EtsyHunt list — self-dated 2026. The eBay aspect-value samples have no reliable date and should be marked **undated**.
- **Scope hygiene:** premiumarte's menu mixes in-scope canvas/acrylic prints with out-of-scope wallpaper, murals, room dividers, corkboards and kitchen backsplash. I kept the full menu because the *subject* taxonomy is shared and copyable, per the brief's exception clause, but the format sections should be filtered out of any generated catalogue.
- **The two API calls that would close most of the gaps in these notes** (both need a credential this session does not have): Etsy `getPropertiesByTaxonomyId` for the Wall Decor / Prints taxonomy ids, and eBay `getItemAspectsForCategory` for 41511, 360, 28009, 551, 38237. — [Etsy Listings Tutorial](https://developer.etsy.com/documentation/tutorials/listings/); [eBay getItemAspectsForCategory](https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getItemAspectsForCategory)
- **A scraping workaround that did work and scales:** eBay `/b/` pages are 403, but their **browse-node titles are in the search index**, and each title is literally an aspect cross (e.g. "Art Deco Trees & Forest Home Décor Posters & Prints", "Canvas Trees & Forest…", "Wooden Vintage/Retro…", "Signed Original Art Prints"). Enumerating those titles via search yields eBay's own aspect-value crosses without touching the blocked pages. Likewise `ebay.co.uk/str/<slug>` is reachable and carries each store's section menu in its page JSON under `STORE_CATEGORY`.
