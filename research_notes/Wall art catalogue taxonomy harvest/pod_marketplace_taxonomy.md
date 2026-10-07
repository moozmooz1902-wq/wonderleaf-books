# Wall art / art print catalogue taxonomy of the major print-on-demand marketplaces

Harvest date: 2026-10-07. All items below are verbatim labels as the sites render
them unless marked otherwise.

**Access summary — read this before trusting coverage:**

| Site | Access result | What I got |
|---|---|---|
| Society6 | OK (direct HTML, 2.3 MB) | Full nav + collection slugs, style/theme page headings |
| Displate | OK (direct HTML) | Top nav category + fandom + collection menus |
| Fine Art America | Blocked to curl (HTTP 403); **WebFetch succeeded** | Large subject/style/medium/shape/room/collection tree |
| INPRNT | SPA, sitemap `<loc>` elements empty; **server-rendered 404 page leaked the full nav**; `/collections/curated/all/` fetched OK | Product types, 4 top categories, 21 curated collections |
| Redbubble | **BLOCKED** — Cloudflare managed challenge on every path including `/robots.txt` | No direct catalogue data. Only search-engine summaries + third-party seller tooling |
| Saatchi Art | **BLOCKED** — HTTP 403 to curl and WebFetch; support site also behind Cloudflare | Nothing direct |
| TeePublic | **BLOCKED** — HTTP 403 to curl and WebFetch | Nothing |
| Zazzle | **BLOCKED** — HTTP 403 / 404 on candidate wall-art paths | Nothing |
| Wayback Machine | **BLOCKED** — `web.archive.org` connection reset by peer at the agent proxy; WebFetch refuses the host outright | No fallback available for the blocked sites |

Because Wayback was unavailable, I had **no fallback route** for Redbubble, Saatchi
Art, TeePublic or Zazzle. Those four are substantially unharvested and I have not
filled the gaps with guesses.

---

## Q1. Each site's full wall-art category and sub-category tree

### Takeaway
Society6, Displate, Fine Art America and INPRNT trees were walked and are
reproduced verbatim below; Fine Art America has by far the deepest subject tree
(~50 subjects) while Displate's public tree is surprisingly shallow (7 shop
categories) with depth coming from fandoms instead. Redbubble, Saatchi Art,
TeePublic and Zazzle blocked all automated access and their trees are gaps.

### Cited Findings

**Society6 — now a Shopify storefront** (URL pattern changed from the old
`society6.com/art-prints?...` facets to `/collections/<slug>`). Wall-art product
types, verbatim from the mega-menu, with the promotional prefixes as rendered —
[Society6 art prints](https://society6.com/art-prints), [Society6 wall art page](https://society6.com/pages/wall-art):

- 40% Off - Art Prints (`/collections/art-prints`)
- 40% Off - Canvas Prints (`/collections/canvas-prints`)
- 40% Off - Posters (`/collections/posters`)
- 40% Off - Framed Posters (`/collections/framed-posters`)
- 40% Off - Metal Prints (`/collections/metal-prints`)
- 40% Off - Mini Art Prints (`/collections/mini-art-prints`)
- 40% Off - Foil Art Prints (`/collections/foil-art-prints`)
- 40% Off - Collage Sets (`/collections/collage-sets`)
- 40% Off - Tapestries (`/collections/tapestries`)
- 40% Off - Fabric Wall Hangings (`/collections/wall-hangings`)
- 40% Off - Wood Wall Art (`/collections/wood-wall-art`)
- 40% Off - Wall Murals (`/collections/wall-murals`)
- 40% Off - Wallpaper (`/collections/wallpaper`)
- Art & Wall Decor (`/collections/wall-art-decor`)

Society6 art-print sub-categories (two parallel slug schemes exist in the
sitemap/body — hyphen and underscore forms — suggesting a migration in progress) —
[Society6 art prints](https://society6.com/art-prints):

| Label as shown | Slug (hyphen form) | Slug (underscore form also present) |
|---|---|---|
| Abstract Wall Art | `art-prints-abstract` | `art-prints_abstract` |
| Animals | `art-prints-animals` | `art-prints_animal` |
| Black & White | `art-prints-black-and-white` | — |
| Children's Art Prints | `art-prints-childrens` | `art-prints_childrens` |
| Collage | `art-prints-collage` | `art-prints_collage` |
| Floral Art Prints | `art-prints-floral` | `art-prints_floral` |
| Landscapes | `art-prints-landscape` | `art-prints_landscape` |
| Drawing | `art-prints-line-drawing` | — |
| Photography Art Prints | `art-prints-photography` | `art-prints_photography` |
| (no nav label found) | `art-prints-nature` | — |
| (no nav label found) | `art-prints-vintage` | — |
| (no nav label found) | — | `art-prints_portrait` |

Society6 wall-mural sub-categories: `wall-murals-abstract` ("Abstract Wall
Murals"), `wall-murals-landscape` ("Landscape Wall Murals"),
`wall-murals-childrens` ("Wall Murals for Children") — [Society6 wall art page](https://society6.com/pages/wall-art).

**Displate — "Shop by Categories"** (7 only), verbatim from the nav JSON —
[Displate metal posters](https://displate.com/metal-posters):
Anime; Movies & Shows; Cars; Gaming & Fantasy; Space; Sport; Nature & Landscapes;
plus "See All Posters".

Displate additional category labels appearing in the "Popular Now" strip and on
the inspirations page — [Displate posters](https://displate.com/posters), [Displate inspirations](https://displate.com/inspirations):
Gaming; Cars; Travel; Cats; Space; Anime; Movies; Football; Music; Textra;
Animals; Anime & Manga; Comics; Cute; Fantasy; Floral; Inspirational;
Japanese & Asian; Landscapes; Nature; Tv shows.

Displate "Explore" / merchandising axes — [Displate posters](https://displate.com/posters):
Start Browsing; Our Bestsellers; From Verified Creators; Trending Today; New In;
About Our Posters; Get Inspired; Mounting Accessories; Find a Gift; Custom
Displates; Limited Editions; For You; Displate Club; Bestsellers; Novelties;
Displates in Your Homes; Meet the Metal Poster; Browse Top Fandoms; Shop by
Categories; Shop by Fandoms; Shop by Artists; Popular Now; Jump To;
`/browse-brands`; `/browse-verified-creators`; `/shards`; `/limited-edition`.

**Fine Art America** — product types, verbatim —
[Fine Art America /art](https://fineartamerica.com/art):
Canvas Prints; Framed Prints; Art Prints; Posters; Metal Prints; Acrylic Prints;
Wood Prints; Tapestries; Paintings; Photographs; Drawings.

Fine Art America art mediums (separate facet): Paintings; Photographs; Drawings;
Digital Art; Mixed Media — [Fine Art America /art](https://fineartamerica.com/art).
Confirmed independently by their robots.txt, which explicitly allows only these
five profile sub-paths: `digital+art`, `drawings`, `mixed+media`, `paintings`,
`photographs` — [Fine Art America robots.txt](https://fineartamerica.com/robots.txt).

Fine Art America **Subject Categories** (the deepest single tree harvested; 50
items, verbatim) — [Fine Art America /art](https://fineartamerica.com/art):
Abstract; Animals; Architecture; Celebrities; Cities; Classic Artists; Colors;
Decades; Famous Paintings; Fantasy; Flowers; Food And Beverage; Historical
Figures; Holidays; Household Items; Impressionism; Inspirational; Lakes;
Landmarks; Landscapes; Magazine Covers; Maps; Movie Posters; Music; Musical
Posters; Name Signs; National Parks; Nature; Nudes; Patents; Patterns;
Portraits; Professions; Science Fiction; Seasons; Signs; Skylines; Sports; Still
Life; Styles; Sunset; Surrealism; Transportation; Travel Posters; U.S. States;
Universities; Years.

Additional Fine Art America subject/theme labels from the first page section
(some overlap the above, some are distinct): Landscape; Animal; Flower;
Motivational; Mid-Century Modern; Religious; Beach; Lighthouse; Skyline;
Transportation; Sunset; Fantasy; Santa Claus; Rock n' Roll; Concert Photos;
Travel Photos — [Fine Art America /art](https://fineartamerica.com/art).

Fine Art America **Photography Types** facet: Nature Photos; Skyline Photos;
Celebrity Photos; Rock n' Roll Photos; Animal Photos; Travel Photos; Concert
Photos; Sunset Photos — [Fine Art America /art](https://fineartamerica.com/art).

**INPRNT** — top-level categories (only four) —
[INPRNT nav, server-rendered](https://www.inprnt.com/collections/curated/all/):
Fine Art (`/category/fine-art/`); Illustration (`/category/illustration/`);
Graphic Design (`/category/graphic-design/`); Photography (`/category/photography/`).
The same four are reused as the sticker category facet
(`/stickers/?category=fine-art` etc.).

INPRNT wall-art product types, verbatim from the Shop menu —
[INPRNT nav](https://www.inprnt.com/collections/curated/all/):
Art Prints (`/browse/`); Posters (`/posters/`); Canvas Prints (`/canvas/`);
Framed Prints / Framed Art Prints (`/frames/`); Metal Prints (`/metal/`);
Acrylic Prints (`/acrylic/`); Mini Prints (`/mini-prints/`); Photographic Prints
(`/photographic-prints/`); Art Cards (`/art-cards/`); Card Packs (`/cards/`);
Limited Editions (`/browse/editions/`); On Sale (`/sale/`).
Custom/volume services (not consumer catalogue but they name formats): Fine Art
Prints; Photo Prints; Large Format; Custom Framing; Portfolio; Bulk Printing.

### Inferences
- Society6's migration to Shopify collapsed a facet-based taxonomy into flat
  collection slugs. The duplicate `art-prints-x` / `art-prints_x` pairs imply the
  live tree is mid-migration, so slugs harvested today may not be stable.
- Displate's shallow 7-category tree plus 14+ fandom entries indicates licensed IP
  is the primary organising axis there, not style or subject.
- Fine Art America's subject list is the richest prompt seed of the four, and
  several of its entries ("Colors", "Decades", "Seasons", "Styles", "U.S. States",
  "Years") are clearly parent nodes for further enumerable children.

### Gaps
- **Redbubble's wall-art tree was not retrieved.** Cloudflare returned a managed
  challenge ("Enable JavaScript and cookies to continue") on every path, including
  `/robots.txt` and `/sitemap.xml` (403). The task brief's expectation of
  `Wall Art > Posters / Art Prints / Canvas / Framed / Metal / Tapestries` could
  **not** be verified first-hand.
- **Saatchi Art, TeePublic and Zazzle trees entirely unharvested** (403 on all
  attempted paths, both fetch tools).
- Fine Art America's child lists under Colors / Decades / Seasons / Styles /
  U.S. States / Years were not expanded — direct curl to `/art/colors` and
  `/art/paintings` returned 403, and the WebFetch of `/art` truncated.
- Displate category pages below the top 7 (e.g. a `/posters/<category>` pattern)
  could not be found; only `/posters/for-you` and `/posters/trending` exist as
  link targets in the rendered HTML.

---

## Q2. Curated collections, themes and "shop by" axes

### Takeaway
Every site merchandises on a style axis and a seasonal axis; Fine Art America and
Society6 additionally merchandise by **room** and Society6 uniquely by **named
colour**, which is the most directly prompt-actionable axis found.

### Cited Findings

**Society6 — "shop by colour" collections** (a distinct, named-colour axis) —
[Society6 art prints](https://society6.com/art-prints):
Blush Pink (`wall-art-blush-pink`); Cobalt Blue (`cobalt-blue-wall-art`);
Mustard Yellow (`wall-art-mustard-yellow`); Olive Green (`olive-green-wall-art`).

**Society6 — "shop by medium/style" wall-art collections**:
Painting (`wall-art-paintings`); Photography (`wall-art-photography`);
Portraits (`wall-art-portraits`); Watercolor (`wall-art-watercolor`) —
[Society6 art prints](https://society6.com/art-prints).

**Society6 — "Art by Style"** (page section heading), the four named styles —
[Society6 trade program styles](https://society6.com/pages/trade-program-styles):
Abstract Modernist; Synchronic Geometric; Vintage Charm; Photography.

**Society6 — "Art by Theme"** (page section heading), the three named themes —
[Society6 trade program themes](https://society6.com/pages/trade-program-themes):
Coastal Chic; Mountain Lodge; Western Ways.

**Society6 — seasonal / occasion collections** —
[Society6 art prints](https://society6.com/art-prints):
Autumn Arrives (`fall`); Fall Jewel Tones (`fall-jewel-tones`); Harvest Gathering
(`fall-harvest-gathering`); Into the Woods (`fall-nature-outdoors`); Halloween
(`halloween`); Moonlit & Moody (`gothic-halloween`); New & Trending
(`new-arrivals`); Sale (`sale`).

**Society6 — "Shop by Room"** (explicit heading on the Home & Living page) —
[Society6 home & living](https://society6.com/pages/home-living):
Living Room (`living-room`); Bedroom (`bedroom`); Bathroom (`bathroom`);
Kitchen & Dining (`kitchen-dining`); Office (`office`); Furniture (`furniture`);
Lifestyle (`lifestyle`).

**Society6 — price-band axis**: Gifts under $25; Gifts under $50; Gifts under
$100 (slug `under-100`; note the site's own typo "Gifts uner $50") —
[Society6 art prints](https://society6.com/art-prints).

**Society6 — artist-storefront axis** ("Shop by Artist", `/pages/shop-by-artist`),
named shops surfaced in the nav: Alisa Galitsyna (`alisagal`); Ann Marie Coolick
(`annmariecoolick`); Brian Buckley (`bribuckley`); City Art (`cityart7`);
Jeanpaul Ferro (`jeanpaulferro`); Megan Morris (`meganmorrisart`); MoonlightPrint
(`moonlightprint`); MsGonzalez (`msgonzalez`); socoart; the COZY HOME
(`thecozyhome`); The Motivated Type (`themotivatedtype`); Vertigo Artography
(`mohanadshuraideh`) — [Society6 art prints](https://society6.com/art-prints).

**Society6 — SEO landing-page themes** (H2/H3 headings on the wall-art page; these
are editorial micro-niches) — [Society6 wall art page](https://society6.com/pages/wall-art):
"Abstract Portrait Art Prints: Contemporary Figure Art for Modern Interiors";
"Floral Posters: Fresh Ways to Style Botanical Art in Your Home"; "Inspirational
Wall Art: Elevate Your Space with Motivational Typography Prints"; "Romantic
Floral Art: Timeless Inspiration for Modern Spaces"; "Shape Your Space: Bold
Geometric Posters That Define Clean Style"; "Wall Art Inspiration"; "Wall Art
Pieces That Make Your Home"; "There's More Wall Art to Find".

**INPRNT — Curated Collections** (21 named, verbatim; the full
`/collections/curated/all/` list) — [INPRNT curated collections](https://www.inprnt.com/collections/curated/all/):
April Showers; Botanical Bliss; Clownin' Around; Cowboys & Canyons; Dinosaurs;
Film; Fireflies; Floral Fantasy; Froggy Time; Merfolk; Noir; Nostalgia; Pisces
Season; Seasonal Snapshots: Winter; Surrealism; Sweet Treat; Tropical; Winter
Solstice; Winter Wonderland; Year of the Snake.
(Slugs: `april-showers`, `botanical-bliss`, `clownin-around`, `cowboys-canyons`,
`dinosaurs`, `film`, `fireflies`, `floral-fantasy`, `froggy-time`, `merfolk`,
`noir`, `nostalgia`, `pisces-season`, `seasonal-snapshots-winter`, `surrealism`,
`sweet-treat`, `tropical`, `winter-solstice`, `winter-wonderland`,
`year-of-the-snake`.)

**Fine Art America — Room Collections** —
[Fine Art America /art](https://fineartamerica.com/art):
Nursery Room; Boy's Bedroom; Girl's Bedroom; Living Room; Family Room; Kitchen;
Laundry Room; Home Theater.

**Fine Art America — Featured Collections** —
[Fine Art America /art](https://fineartamerica.com/art):
In the News; Slim Aarons; Sports Illustrated Covers; Light & Airy; Rock Royalty;
Norman Rockwell; Famous Paintings; Name Signs.
(Note: Slim Aarons, Sports Illustrated and Norman Rockwell are licensed estates /
brands — see the off-limits list in Q6.)

**Displate — artist-curated named collections** (the "Shop by Artists" axis is
collection-led, not just artist-led) — [Displate metal posters](https://displate.com/metal-posters):
Whimsical Haunts by Snouleaf; Mystic Tarot by Thiago Correa; Retro Monsters by
Pepe Rodriguez; Dark Fantasy by Anato Finnstark; Shadow Knights by Dominik Mayer;
Spooky Puns by Dinomike Design. Seasonal promo: "Scary Good Deals", "See Hottest
Poster Picks".

Displate verified-creator names surfaced on the inspirations page (useful as a
style-reference roster): Adel S; Anato Finnstark; Bruno Kerling Designs; Denis
Orio Ibañez; Ellie MapleFox; Elora Pautrat; EpicArtworks; Gray Isi; Ilustrata;
ImmersiveDimension; Lily Rose; Mason Scott; Pixaverse; PixelGallery; Ruby Art;
Simon Darren; The Deep Studio; Tobias Roetsch; Tomasz Dąbek; Tomi; Vadim
Sadovski — [Displate inspirations](https://displate.com/inspirations).

### Inferences
- The colour axis (Society6's Blush Pink / Cobalt Blue / Mustard Yellow / Olive
  Green) and the room axis (FAA's 8 rooms, Society6's 7) are the two axes most
  directly convertible into prompt modifiers, because both are explicitly
  merchandised and both are orthogonal to subject.
- INPRNT's curated list is heavily seasonal and zeitgeist-driven (Pisces Season,
  Year of the Snake, Winter Solstice), implying their curation refreshes on an
  astrological/zodiac and solstice calendar.

### Gaps
- Society6's "Art by Style" and "Art by Theme" pages each rendered only 3-4 named
  groupings. Whether the trade programme has a longer style/theme list behind the
  `/pages/trade-application` gate is unknown (not attempted — requires signup).
- Redbubble, Saatchi Art, TeePublic and Zazzle collection/"shop by" axes: no data
  (blocked).

---

## Q3. Tag vocabulary

### Takeaway
I could **not** harvest artist-applied tags first-hand from any of the three sites
that expose them (Redbubble blocked by Cloudflare; Society6's Shopify rebuild no
longer exposes a public tag index I could find; INPRNT's tag pages are rendered
client-side and `/search/*` is `Disallow`ed in robots.txt). The only tag material
I have is third-party seller-tool content, which I have labelled as such.

### Cited Findings
- INPRNT's robots.txt explicitly disallows `/search/*` and `/rec_search/*`, which
  is where tag queries resolve — so tag enumeration is blocked by the site's own
  crawl policy — [INPRNT robots.txt](https://www.inprnt.com/robots.txt).
- INPRNT's `sitemap.xml` is served with **empty `<loc>` elements** (29 `<sitemap>`
  entries, all blank), so there is no sitemap route to tag or artwork pages —
  [INPRNT sitemap](https://www.inprnt.com/sitemap.xml).
- Third-party tag list (NOT from Redbubble itself; a seller-tooling blog, "Updated
  April 17, 2026"), wall-art and room-specific tags: living room wall art; bedroom
  decor; nursery art; office decor; earth tones print; navy and gold art; neutral
  wall art — [MetadataReactor, Redbubble Tags That Sell](https://metadatareactor.com/blog/redbubble-tags-that-sell/).
- Same source, aesthetic/style tags: cottagecore; dark academia aesthetic;
  vaporwave design; goblincore; witchcore; whimsigoth; kawaii; vsco; retro; boho
  print; minimalist wall art; vintage poster; botanical print; watercolor;
  minimalist pet art — [MetadataReactor](https://metadatareactor.com/blog/redbubble-tags-that-sell/).
- Same source, subject/identity tag families: profession tags (nurse, teacher,
  engineer, chef, accountant, librarian); hobby tags (hiking, gaming, gardening,
  reading, cycling, knitting, plant mom, bookworm, gamer); pet tags (golden
  retriever, dog mom, cat dad, dog illustration); occasion tags (Christmas gift,
  graduation gift, Mother's Day present, Valentine's Day, birthday gift for her) —
  [MetadataReactor](https://metadatareactor.com/blog/redbubble-tags-that-sell/).
- Same source prescribes a **15-tag** listing budget split as: primary subject
  (2-3), art style (2), colour/aesthetic (1-2), gift intent (3-4), product context
  (1-2) — [MetadataReactor](https://metadatareactor.com/blog/redbubble-tags-that-sell/).
- Redbubble tapestry design-theme vocabulary, from a search-engine summary of
  Redbubble shop pages (**not** a direct fetch — treat as second-hand): boho;
  mandala; hippie; trippy; nature; mountains; forests; waves; sun; moon; space;
  funny; cute; colorful; unusual; maps; vintage; medieval; abstract; educational;
  black-and-white; bright; pastel; patterned — [Redbubble Tapestry shop (via search summary)](https://www.redbubble.com/shop/Tapestry).

### Inferences
- The 15-tag budget structure is a strong signal that Redbubble's own ranking
  rewards a *mix* of subject + style + colour + intent + product-type tags, so a
  generated catalogue should carry all five tag classes per listing rather than
  piling on subject synonyms.
- Society6's move to Shopify collections likely **removed** the artist-tag axis
  from the public site entirely: I found no `/tag/` or `?tag=` route anywhere in
  2.3 MB of rendered HTML across four Society6 pages.

### Gaps
- **No first-hand tag harvest from any site.** This is the largest gap in this
  research. The brief asked for "as many distinct wall-art tags as you can"; I can
  honestly supply only ~60 tags, all second-hand from one seller-tooling blog plus
  one search summary.
- The MetadataReactor list is skewed to apparel and stickers; its wall-art section
  is only 7 tags long. It is also a commercial SEO tool's blog, i.e. an interested
  party, not a primary source.
- I did not verify whether any of these tags actually appear on Redbubble wall-art
  listings, because I could not load Redbubble.

---

## Q4. Visible popularity signals and the specific items carrying them

### Takeaway
Only Displate and Society6 exposed popularity-signal *mechanisms* to me, and
Displate exposed just two badge strings. I captured **no review counts, no star
ratings and no favourite/sold counts** for any individual wall-art item on any
site, so the weighting the brief asked for cannot be built from this harvest.

### Cited Findings
- Displate renders two badge strings in its product markup: **"New"** and
  **"Bestselling"** — [Displate metal posters](https://displate.com/metal-posters).
- Displate exposes sort/merchandising surfaces named "Our Bestsellers",
  "Bestselling posters", "Trending Today", "Popular Now", "See Hottest Poster
  Picks", "Novelties", "New In" and "For You" (`/posters/trending`,
  `/posters/for-you`) — [Displate posters](https://displate.com/posters).
- Displate has a "Verified Creators" tier (`/browse-verified-creators`) and a
  "Limited Editions" tier (`/limited-edition`), plus "Shards" mini-size metal
  collectibles (`/shards`) — [Displate metal posters](https://displate.com/metal-posters).
- Society6 has a "New & Trending" collection (`/collections/new-arrivals`) and a
  public "Customer Reviews" page (`/pages/reviews`) — [Society6 art prints](https://society6.com/art-prints).
- INPRNT has a "Limited Editions" tier (`/browse/editions/`) and an editorial
  "Artist Spotlights" property (spotlights.inprnt.com) — [INPRNT nav](https://www.inprnt.com/collections/curated/all/).
- Fine Art America surfaces an "In the News" featured collection as its editorial
  popularity signal — [Fine Art America /art](https://fineartamerica.com/art).
- A WebFetch of the Displate page returned "No star ratings or review counts are
  visible in the provided content" — [Displate metal posters](https://displate.com/metal-posters).

Specific named items observed with a badge or a merchandising slot (subject/style
noted for weighting; this is a thin sample, not a bestseller list):

| Item title | Site | Signal | Subject / style |
|---|---|---|---|
| Abstract Swirling Colorful Waves | Displate | "New", "Bestselling" badges in markup | abstract / wave / colourful |

Items appearing in Society6's **"Art by Style"** editorial slots (i.e. hand-picked,
a curation signal rather than a sales signal) — [Society6 trade program styles](https://society6.com/pages/trade-program-styles):
Abstract Geometry 2 (geometric abstract); Abstract Geometry 4 (geometric
abstract); Abstract Shapes 59/3 (abstract shapes); Form 14C (abstract form);
In Bloom 27 (floral); Boho Botanica (boho botanical); Blue navy retro
scandinavian Mid century modern (mid-century / Scandinavian); Black Swan White
Swan (animal); Sun Arch Double - Gold (geometric sun arch); Mind (abstract);
"Beach - Summer Love II - Aerial Beach and Ocean photography by Ingrid Beddoes"
(aerial coastal photography); "Look on The Bright Side Marquee Sign Austin Motel
Austin Texas" (typographic/signage photography).

Items appearing in Society6's **"Art by Theme"** editorial slots —
[Society6 trade program themes](https://society6.com/pages/trade-program-themes):
"One Wave At A Time" (coastal/typography); Abstract Mountains II (abstract
landscape); "Aerial Ocean Waves - Coastal Wall Art Photography" (aerial coastal
photography); Autumn Moon (seasonal landscape); Beach Day II (coastal);
Bear In Whimsical Wild (whimsical animal); campfire gathering (mountain lodge);
Cowboy Hat Wall (western); "Don't Call Me Honey Retro Cowgirl On Horseback V.1"
(retro western); "Wild As Heck" A Cowgirl & Her Horse (western); Nautical
Nonsense III (nautical); "These Boots - Yee haw Cherry Red n Blue" (western
boots).

Framed art prints surfaced in Society6's own product grid (subjects, as a crude
proxy for what they choose to show) — [Society6 art prints](https://society6.com/art-prints):
abstract landscape; nursery nature train; Blue Ridge October; bouquet of summer
sunshine; Claude Monet beach; colorful abstract mountains; colorful morning in
the mountain forest; egret on the marsh; floria; midwest birds guide; minimalist
abstract landscape; minimalist sunset III; moon crescent blue; river canyon;
seven leaves plant; Tampa skyline; the big blue bus; the moon balloon; the moon
song; tiger doesn't lose sleep; "These Boots" leopard print; unconditional love;
"Unimpressed" Meika Gafu by Matsumoto Hoji 1814; Villa Bella Azuria; vintage
Parisian green fairy absinthe advertisement; "The Man In The Arena" Theodore
Roosevelt; "Strictly No Elephants" vintage humorous child verses; green misty
mountain pine forest vintage style; invasion on vacation; peachy keen; the first
love.

### Inferences
- Society6's editorial slots cluster heavily on **western/cowgirl**, **coastal/
  aerial ocean**, **abstract geometric** and **mountain-lodge** — four themes
  appearing repeatedly across both style and theme pages. That repetition is the
  closest thing to a weighting signal this harvest produced.
- The absence of any star rating or review count in Displate's and Society6's
  rendered markup suggests both sites keep those behind client-side rendering, so
  weighting by review count would require a JS-capable browser, not HTTP fetches.

### Gaps
- No numeric popularity data of any kind (review counts, star ratings, favourite
  counts, "sold" counts) was obtained for any item on any site.
- Redbubble's "Top Selling" / "Trending" sort orders, Saatchi Art's curated lists
  and TeePublic's/Zazzle's bestseller badges: no data (blocked).

---

## Q5. Styles and media named as browsable facets; formats and orientations

### Takeaway
Fine Art America is the only site that publishes both an explicit **Styles** facet
(14 named styles) and an explicit **Print Shapes** facet (6 orientations); Society6
and INPRNT name media rather than styles, and no site I reached named linocut,
risograph, impasto, art nouveau, bauhaus or japandi as a browsable facet.

### Cited Findings

**Fine Art America — "Styles" facet, 14 named styles, verbatim** —
[Fine Art America /art](https://fineartamerica.com/art):
Abstract; Vintage; Black & White; Minimalist; Boho; Typography; Watercolor;
Surreal; Retro; Light & Airy; Still Life; Whimsical; Vibrant; Muted.

**Fine Art America — additional style/movement labels appearing inside the Subject
tree** (so they are browsable, just filed as subjects): Impressionism;
Surrealism; Mid-Century Modern; Famous Paintings; Classic Artists; Patterns —
[Fine Art America /art](https://fineartamerica.com/art).

**Fine Art America — "Print Shapes" facet** (the orientation axis) —
[Fine Art America /art](https://fineartamerica.com/art):
Horizontal; Vertical; Square; Panoramic; Horizontal Panoramic; Vertical Panoramic.

**Society6 — media/style facets**: Painting; Photography; Watercolor; Portraits;
Drawing (slug `art-prints-line-drawing`, i.e. line drawing); Collage; Abstract;
Black & White; Floral; Landscapes; Animals; Children's; Vintage (slug
`art-prints-vintage`); Nature (slug `art-prints-nature`) —
[Society6 art prints](https://society6.com/art-prints).

**Society6 — style names from the "Art by Style" section**: Abstract Modernist;
Synchronic Geometric; Vintage Charm; Photography —
[Society6 trade program styles](https://society6.com/pages/trade-program-styles).

**INPRNT — the medium axis is the category axis**: Fine Art; Illustration;
Graphic Design; Photography — [INPRNT nav](https://www.inprnt.com/collections/curated/all/).
Styles appear only as curated-collection names (Noir, Surrealism, Nostalgia) —
[INPRNT curated collections](https://www.inprnt.com/collections/curated/all/).

**Displate — finishes** (a material facet unique to metal): Matte; Gloss; Textra
— [Displate metal posters](https://displate.com/metal-posters).
Displate formats: Limited Editions; Shards (mini-size metal collectibles); Custom
Displates — [Displate metal posters](https://displate.com/metal-posters).

**Formats / sets**: Society6 sells **Collage Sets** (`/collections/collage-sets`),
which is the multi-panel / gallery-wall format, plus Mini Art Prints and Foil Art
Prints as distinct formats — [Society6 art prints](https://society6.com/art-prints).
INPRNT sells Mini Prints and Art Cards as small formats —
[INPRNT nav](https://www.inprnt.com/collections/curated/all/).

**Framed vs unframed** is a product-type split, not a facet, on all four sites
reached: Society6 separates "Art Prints" from "Framed Posters"; INPRNT separates
"Art Prints" (`/browse/`) from "Framed Prints" (`/frames/`); Fine Art America
separates "Art Prints" from "Framed Prints" —
[Society6](https://society6.com/art-prints), [INPRNT](https://www.inprnt.com/collections/curated/all/), [Fine Art America](https://fineartamerica.com/art).

### Inferences
- The six Fine Art America print shapes are the only explicit aspect-ratio
  taxonomy found, and they map cleanly onto generation targets: 3:2 landscape,
  2:3 portrait, 1:1, and two panoramic extremes.
- Several styles the brief asked about — linocut, risograph, impasto, art nouveau,
  bauhaus, japandi, digital, photography (as a *style* rather than a medium),
  collage (on FAA) — are **absent** from every browsable facet I reached. They may
  exist as artist tags, which I could not harvest (Q3).

### Gaps
- **No size or dimension data captured for any site.** The brief asked for sizes
  and aspect ratios; I obtained only Fine Art America's six shape names and no
  inch/cm dimensions, because product pages were not reachable (Redbubble, Saatchi,
  TeePublic, Zazzle blocked) or render sizes client-side (Society6, Displate,
  INPRNT).
- No diptych/triptych facet was found on any site. Society6's "Collage Sets" is
  the nearest equivalent; whether it is 2-, 3- or n-panel is unconfirmed.
- Redbubble's, Saatchi Art's, TeePublic's and Zazzle's style facets: no data.

---

## Q6. Absent or restricted subjects, AI-generated-content policies, and licensed IP

### Takeaway
Saatchi Art and INPRNT have published AI restrictions; Society6 has moved to a
gated, curated submission model explicitly aimed at cutting AI and low-quality
content; and **Redbubble's published Community and Content Guidelines appear to
contain no AI provision at all** — a claim I could not verify first-hand because
the site was blocked. Licensed IP is pervasive on Displate and present on Fine
Art America, and is listed separately below as off-limits.

### Cited Findings — AI policies
- **INPRNT** "explicitly prohibits artworks generated completely via an automated
  AI or machine-learning process in its content guidelines" — reported by a
  secondary source; I could **not** reach INPRNT's own guidelines page
  (`/help/content-guidelines/` returned 404) —
  [Synthedia, The Banning of AI-Generated Images Has Begun](https://synthedia.substack.com/p/the-banning-of-ai-generated-images);
  [AlternativeTo, Anti-AI Art Communities](https://www.alternativeto.net/list/41259/anti-ai-art-communities/).
  Note the wording "completely via an automated process" — this implies
  AI-assisted work may be permitted, but I could not confirm the exact text.
- **Saatchi Art** publishes a dedicated "AI Generated Art Policy" support article
  — [Saatchi Art support, AI Generated Art Policy](https://support.saatchiart.com/hc/en-us/articles/27671947605915-AI-Generated-Art-Policy).
  **I could not read it**: the support site returned HTTP 403 to curl and WebFetch
  and serves a Cloudflare "Just a moment..." challenge. Its existence is
  confirmed; its contents are a gap.
- **Society6** is shutting down many artist accounts and moving "to a more curated
  marketplace", with the stated aim of reducing "low-quality and AI-generated
  content"; affected artists lost accounts by **18 March**, and **new members must
  submit artwork for approval before joining** — reported by a seller-facing
  secondary source dated around Feb 2025, which also notes Society6 historically
  permitted AI-generated designs —
  [Wildlife Art Store, How to Sell Art on Society6](https://www.wildlifeartstore.com/sell-art-on-society6/).
  Treat the March date as **dated (2025)** and unverified against Society6's own
  policy pages.
- **Redbubble**: one source asserts Redbubble's Community and Content Guidelines
  "contain no reference to artificial intelligence, generative AI or AI-generated
  content anywhere in the page", and explicitly contradicts the widely repeated
  claims that Redbubble requires AI disclosure in the description field and caps
  AI uploads per day for new accounts —
  [search summary citing Redbubble guidelines analysis](https://felloai.com/can-you-sell-ai-art/).
  **Conflicting claims exist in the wild**; I could not adjudicate because
  redbubble.com and help.redbubble.com both returned 403 / Cloudflare challenge.
- Society6 publishes a "Copyright & Trademark Policy" page at
  `/pages/copyright` — [Society6 art prints](https://society6.com/art-prints). Not read.
- INPRNT publishes an "Artist Agreement" (`/info/artist_terms/`) and "Terms of
  Use" (`/info/terms/`) — [INPRNT nav](https://www.inprnt.com/collections/curated/all/). Not read.
- Displate publishes `/about-copyright` — [Displate metal posters](https://displate.com/metal-posters). Not read.

### Cited Findings — LICENSED IP, OFF-LIMITS (do not generate)

**Displate licensed fandoms** — these resolve under a dedicated `/licensed/`
URL namespace, which is an unambiguous marker of licensed-only content —
[Displate metal posters](https://displate.com/metal-posters):

| Franchise | Displate path |
|---|---|
| Marvel | `/licensed/marvel` |
| Star Wars | `/licensed/star-wars` |
| Warhammer | `/licensed/warhammer` |
| Lord of the Rings / Middle-Earth | `/licensed/middleearth` |
| Clair Obscur: Expedition 33 | `/licensed/clair-obscur-expedition-33` |
| NBA | `/licensed/nba` |
| Cyberpunk 2077 | `/licensed/cyberpunk-2077` |
| DC Comics | `/licensed/dc-comics` |
| Destiny | `/licensed/destiny` |
| Stranger Things | `/licensed/stranger-things-series` |
| Elden Ring | `/licensed/elden-ring` |
| Wizarding World (Harry Potter) | `/licensed/wizarding-world` |
| Call of Duty | `/licensed/call-of-duty` |
| League of Legends | `/licensed/league-of-legends` |

Further franchises named on Displate's inspirations page (also off-limits) —
[Displate inspirations](https://displate.com/inspirations):
Arcane; Assassin's Creed; Avatar: The Last Airbender; Dark Souls; Dune; Fallout;
Friends; Ghost of Yōtei; God Of War; Horizon; K-Pop Demon Hunters; Monster Hunter;
Portal; Resident Evil; SpongeBob SquarePants; TEKKEN; World Of Warcraft.

**Fine Art America licensed estates / brands** (surfaced as Featured Collections
and featured artists) — [Fine Art America /art](https://fineartamerica.com/art):
Slim Aarons (photographic estate); Sports Illustrated Covers (brand); Norman
Rockwell (estate); Rock Royalty (music photography licensing); Celebrities;
Celebrity Photos; Magazine Covers; Movie Posters; Musical Posters; Rock n' Roll
Photos; Concert Photos; Universities (collegiate trademarks); Sports (club and
league marks); Patents (reproductions — public-domain status varies by date).

**Displate sports/club marks**: NBA (licensed), plus a "Football" category and a
"Sport" category which in practice carry club badges —
[Displate posters](https://displate.com/posters).

**Public-domain-adjacent but check carefully**: Fine Art America's "Classic
Artists" and "Famous Paintings" collections name Vincent Van Gogh, Claude Monet,
Leonardo da Vinci, Gustav Klimt, Edward Hopper, Briton Riviere, Winslow Homer and
Michelangelo — [Fine Art America /art](https://fineartamerica.com/art).
Society6 likewise carries a "Claude Monet beach" framed art print and an
"Unimpressed Meika Gafu by Matsumoto Hoji 1814" print —
[Society6 art prints](https://society6.com/art-prints).
These artists are long out of copyright, but Norman Rockwell (d. 1978) and Edward
Hopper (d. 1967) are **not** — those two sit in the licensed list above, not here.

### Cited Findings — conspicuously absent / restricted subjects
- **Nudes** is a browsable Fine Art America subject category, i.e. permitted there
  — [Fine Art America /art](https://fineartamerica.com/art). No equivalent facet
  appears anywhere in Society6's, Displate's or INPRNT's navigation, which is a
  notable asymmetry.
- Fine Art America's robots.txt blocks `/displayartwork.html`,
  `/previewhighresolutionimage.php` and `/pdfartworkmenu.php`, and disallows most
  `/profiles/*/art/*` paths — an anti-scraping posture rather than a content
  restriction — [Fine Art America robots.txt](https://fineartamerica.com/robots.txt).

### Inferences
- The AI-policy gradient across the four reachable sites runs: INPRNT (strictest,
  fully-automated work banned) → Society6 (gated approval, explicitly
  anti-AI-flood since 2025) → Fine Art America / Displate (no AI policy found
  either way) → Redbubble (reportedly silent in its guidelines). A catalogue
  intended for multiple sites should therefore be built to INPRNT's standard or
  simply not submitted to INPRNT.
- Displate's `/licensed/` URL namespace is a clean machine-readable boundary: any
  subject reachable under `/licensed/` is a franchise and must not be generated.
  The ~31 franchises listed above are a usable denylist seed.
- The near-total absence of a Nudes facet outside Fine Art America suggests figure
  work is a low-return category for a multi-site catalogue.

### Gaps
- **Saatchi Art's AI policy text is unread** despite the article being located
  (403/Cloudflare). This is a confirmed-to-exist but unread primary source.
- **INPRNT's own content-guidelines page was not found** (`/help/content-guidelines/`
  → 404). The AI prohibition rests on two secondary sources only, and the exact
  wording and the AI-assisted/AI-generated boundary are unverified.
- **Redbubble's AI position is genuinely unresolved.** Sources conflict and I could
  not read the primary document. Do not treat "Redbubble has no AI policy" as
  established.
- Society6's current (2026) policy pages (`/pages/copyright`) and INPRNT's Artist
  Agreement were located but not read; prohibited-subject lists for both are gaps.
- No site's prohibited-subject list (hate symbols, weapons, drugs, etc.) was
  retrieved for any of the eight sites.
- Zazzle's and TeePublic's licensed-IP programmes (both are known to run large
  official fan-art licensing schemes) are unharvested, so the off-limits franchise
  list above is Displate-and-FAA-only and is certainly incomplete.
