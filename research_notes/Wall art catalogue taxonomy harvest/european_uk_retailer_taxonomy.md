# Wall Art Catalogue Taxonomy — European & UK Poster/Print Retailers

Harvest date: 2026-10-07. Scope: posters, art prints, framed prints, canvases only.

## Access status per retailer (read this first)

| Retailer | UK storefront | Harvest result |
|---|---|---|
| The Poster Club | theposterclub.com, ships UK | **FULL nav harvested verbatim** |
| Abstract House | abstracthouse.com, UK (London) | **FULL nav harvested verbatim** |
| Fy! (iamfy.co) | iamfy.co, UK | **FULL nav harvested verbatim** — richest tree of all |
| Photowall | photowall.co.uk, GBP | **FULL axes harvested with item counts** |
| Bimago | bimago.co.uk | **FULL nav harvested verbatim** |
| Olive et Oriel | oliveetoriel.com, **AUD only** | **FULL nav harvested verbatim** |
| Paper Collective | papercollective.com | **Nav harvested** (shallow tree) |
| Wallfillers | ebay.co.uk/str/wallfillerscanvas | **Categories + 48 item titles & GBP prices harvested** |
| Desenio | desenio.co.uk | **BLOCKED** — HTTP 429 / "Vercel Security Checkpoint" on every path and every TLD (.co.uk, .com, .eu). Partial taxonomy recovered from search-result URLs only |
| Poster Store | posterstore.co.uk | **BLOCKED** — HTTP 429 on .co.uk, .com, .eu, all paths. Partial taxonomy from search-result URLs only |
| Posterlounge | posterlounge.co.uk | **BLOCKED** — HTTP 429 on .co.uk and .de. Partial taxonomy from search-result URLs only |
| Juniqe | juniqe.co.uk 301s to juniqe.com/uk | **PARTIALLY BLOCKED** — returns HTTP 200 but an empty body (client-side-rendered SPA). Lists recovered via search only |
| King & McGaw | kingandmcgaw.com, GBP | **BLOCKED** — HTTP 403 on all paths. Category + collection lists recovered via search |
| Surface View | surfaceview.co.uk | **BLOCKED** — HTTP 403. Partner list recovered via search |
| Art Republic | — | **DEFUNCT / REDIRECTED**, see below |
| Pictowall | pictowall.co.uk | **BLOCKED** — HTTP 522 (origin down at time of harvest) |
| Scandinavian Design Center | — | **REBRANDED**, see below |

Two further access notes:
- `web.archive.org` page content is **not fetchable** from this environment ("Claude Code is unable to fetch from web.archive.org"), though the `archive.org/wayback/available` JSON API *is*. A current Desenio snapshot exists (`web.archive.org/web/20261004211227/https://desenio.co.uk/`, 2026-10-04) and a Poster Store one (`web.archive.org/web/20260614013818/https://posterstore.co.uk/`, 2026-06-14) — **both are reachable from an unblocked machine and are the single highest-value follow-up action.** — [Wayback availability API](http://archive.org/wayback/available?url=desenio.co.uk)
- Raw `curl` is reset by the agent proxy, and the `r.jina.ai` text-extraction proxy returns the same Vercel checkpoint for Desenio, so the 429 is origin-side bot protection, not a proxy artefact.

**Two retailers on the brief no longer exist as specified:**
- **Art Republic**: `artrepublic.com` now 301-redirects to `artfinder.com`. The related Brighton gallery lineage (Ink-d → artrepublic Soho → Lawrence Alkin Gallery → Enter Gallery) closed permanently after 30 years, founder Lawrence Alkin citing "the challenges of recent years have left us with no other choice." — [Scene Magazine](https://www.scenemag.co.uk/enter-gallery-brightons-oldest-independent-art-gallery-to-close-its-doors/)
- **Scandinavian Design Center**: `scandinaviandesigncenter.com/products/art-prints-posters/` 301-redirects to `nordicnest.com/products/art-prints-posters` (which itself 404s at that exact path). The brand has been absorbed into Nordic Nest.

---

## Q1. Full navigation trees, verbatim

### Takeaway
Six retailers' trees were harvested verbatim and are reproduced in full below; they confirm the four-axis (motif / style / colour / room) merchandising model, with Fy! and Photowall exposing the most completely enumerated axes. The two retailers the brief singled out as the four-axis exemplars — Desenio and Poster Store — both block automated access and could only be partially reconstructed.

### Cited Findings

#### Fy! (iamfy.co) — FULL TREE, VERBATIM
All of the following from [iamfy.co](https://iamfy.co/):

- **Shop**: All Art Prints · Bestsellers · New In · XL Art Prints · Canvas Prints · Framed Prints · On Sale
  - *Curated Picks*: Trending Now · Editors' Picks · William Morris Style · Japanese Art · Art Nouveau / Klimt
  - *By Colour*: All Colours · Green · Pink · Blue · Yellow · B&W · Warm · Pastels · Red
- **Style**: Trending Now · New Arrivals · Best Sellers · Curator's Notebook
  - *Style tiles*: Maximalist · Cottage Core · Modern · Scandinavian · Art Deco · Bohemian · Eclectic · Traditional · Abstract · Industrial · Coastal · Style Quiz
- **Room**: Trending Now · New Arrivals · Best Sellers · Art for Business · Art for Hotels
  - *Room tiles*: Living Room · Bedroom · Home Office · Kitchen · Hallway · Bathroom · Kids' Room · Laundry Room · Coffee Nook · Cloakroom
- **Trends**: New this week · Father's Day · Editors' Picks · Japanese Art · Disco · William Morris · By Mood
  - *Trend tiles*: Music · Vintage · Film · Flowers · Animals · Travel · Food & Drink · Disco · Cities · Sport · Illustration · Botanical
- **Gallery Walls**: AI Designer · How to Create a Gallery Wall · Two Print Sets · Three Print Sets
- **Frames**: All Frames · Frame size guide · Frames for Business
  - *Frame Colour*: Black · White · Natural · Brown · Gold · Silver
  - *Frame Style*: Essentials · Linear · Gallery · Heritage · Coastal · Statement
  - *Trending Frame Styles* (named frame models): Standard · Beat · Open · Vitrine · Grain · Lift · Tally · Lull · Step · Codex · Drift · Echo

#### The Poster Club — FULL TREE, VERBATIM
All of the following from [theposterclub.com](https://www.theposterclub.com/):

- **SHOP**
  - *Art Prints*: All Art Prints · New Arrivals · Most Popular · Curator's Picks · X-Large Art Prints · Limited Editions · Shop By Artist
  - *Canvas Art*: All Canvas Art · Most Popular Canvas Art
  - *Wall Objects*: All Wall Objects · Most Popular Wall Objects · Wall Object Collections
  - *Frames*: All Frames · Oak Frames · Coloured Frames
  - *Passepartouts*: All Passepartouts
  - *Gift Card*
- **INSPIRATION**
  - *Collections*: Shop by Collection · Artist Collaborations · The Zodiac Collection by Sofia Lind · The Peripheral Collection by Liv Lee · The Symbiont Collection by Suzanne Lustig · The Interstellar Collection by Anne Novak
  - *By Room*: Kitchen · Living Room · Bedroom · Home Office · Bathroom · Kids Room
  - *By Style*: Abstract · Animals · Botanical · Human & Figurative · Illustrations · Line Art · Minimalistic · Photo Art
  - *Art Walls*: Art Wall Gallery · How To Create An Art Wall · Art Wall Designer
  - *Stories*: Curated By · Home Stories · Journal
  - *Guides*: How to Hang & Frame Your Art · How To Create An Art Wall
  - *Also surfaced*: Perfect Match · Curator's Picks

Note: The Poster Club collapses motif and style into **one** axis called "By Style" (Abstract, Animals, Botanical, Human & Figurative, Illustrations, Line Art, Minimalistic, Photo Art) and exposes **no colour axis at all**.

#### Abstract House — FULL TREE, VERBATIM
All of the following from [abstracthouse.com](https://abstracthouse.com/):

- **PRINTS**
  - *Shop By Style & Subject*: Abstract Art · Botanical Art Prints · Geometric Wall Art · Cityscape Art · Fine Art Photography · Landscape Art Prints · Figurative Art Prints · Shop All Prints
  - *Popular*: Set Of Three Prints · Gallery Walls & Sets · Large Artwork · Canvas Art · Bestsellers · Limited Edition Prints · Art By Room
  - *Art By Colour*: Blue Art · Brown Art · Green Art · Black & White · Neutral Palette · Red Art · Vibrant Colours · Yellow Wall Art · View All Colours
  - *Featured*: New Arrivals · Bestselling Art
- **PAINTINGS**: Original Art
- **GALLERY WALLS**: Gallery Wall Art
- **GUIDES**
  - *Editorial*: Art Buying Guides · How-To Guides · Sustainability · Art Care Guides · Upcoming Events
  - *Art Advisory*: Art Advisory Service · Commission An Artist · Art For The Office · Art Personality Quiz
  - *Help*: About Us · Contact Us · Delivery & Returns · Quality Craftsmanship

#### Bimago — FULL TREE, VERBATIM (framed-print/canvas/poster branches only; wallpaper branches included for completeness since the motif vocabulary is shared)
All of the following from [bimago.co.uk](https://www.bimago.co.uk/):

Top level: Canvas Prints · Wall Murals · Wallpapers · Room Dividers · Posters · Painting Kits · Textiles · Wall Panels · Trends · Inspirations · New arrivals

- **Canvas Prints**
  - *Themes*: 3D · Abstract · African · Street Art · Black And White · Flowers · People · World Maps · Still Life · Cities · Landscapes · Sacred Art · Zen · Text · Animals
  - *Reproductions* (see Q7 — this is the public-domain range): Canaletto · Caravaggio · Caspar David Friedrich · Claude Monet · Edgar Degas · El Greco · Gustav Klimt · Hieronymus Bosch · Jan van Eyck · Jan Vermeer · Leonardo da Vinci · Michelangelo · Rafael Sanzio · Rembrandt · Sandro Botticelli · Pierre-Auguste Renoir · Titian · Vincent van Gogh · Wassily Kandinsky · William Blake · William Turner · See all
  - *Style*: Art Nouveau · Boho · Glamour · Industrial · Marines · Minimalist · Modern · Pop Art · Photographs · Scandinavian · Vintage · Watercolor
  - *Interiors*: Office · Dining Room · Kitchen · For Children · Hallway · Living Room · Bedroom
  - *Types*: Canvas gallery · Framed canvas · Decorative acoustic panels · XXL Large Canvas Prints · Round Canvas Prints · Premium Canvas Print · Multi Part Canvas Prints
- **Posters**
  - *Themes*: Abstract and Geometric · Animals · Automotive · Banksy and Street Art · Black and White · Botanical · Colorful · Flowers · Gifts · Graphics · Love and Heart · Maps and Cities · Nature · Photographs · Seasons · Typography · Woman · World Map
  - *Trendy Styles*: Vintage · Boho · Glamour · Industrial · Modern · Scandinavian · Minimalist · Pop Art
  - *Interiors*: Living Room · Bedroom · Kitchen · Bathroom · Office · Gym and fitness · Garage · Dining Room · Hallway
  - *Sizes*: 21x30 cm · 30x40 cm · 40x60 cm · 50x70 cm · 60x90 cm · 70x100 cm
- **Room Dividers** (motif vocabulary, reusable): 3D · Abstract · Animals · Backgrounds and patterns · Botanical · Brick · Cities · Flowers · Geometric · Landscapes · Mandala · Marble · Stone · Trees · Wood · World Maps · Zen
- **Wallpapers** (motif vocabulary, reusable): 3D · Abstract · Animals · Automotive · Black and white · Botanical · Effects and Backgrounds · Fantasy · Flowers · For Children · Hobby · Landscapes · Love · Ornament · Patterns · Seasons · Text
- **Trends** (named seasonal collections — 28 of them): Frida Kahlo · Sage Green · Decometry · A burst Of Colour · Japandi · A Space Odyssey · A Spark Of Magic · Gentle Stories · Children's World · Art Déco · In Bloom · Back To Classics · Dopamine House · Japanese Touch · Go Green · Self Love · Office At Home · Scandi Boho · Fresh Flower Delivery · Nordic Power · PasteLOVE · Flowers In Her Hair · Colours Of Nature · Who Run The World? Girls! · Banksy · Full Of Love · House Dressed In Autumn · Back to school
- **Inspirations**
  - *Styles*: Boho · Scandinavian · Glamour · Loft · Classic · Hampton · Art Déco · New York · Modern · Provencal · Rustic · Vintage · Shabby Chic · Nautical · Eclectic · Minimalist · See all
  - *Interiors*: Living Room · Bedroom · Kitchen · Dining Room · Bathroom · Office · Hallway · Children's Room · Teen Room · Gaming Room · Guest Room · Living Room with Kitchenette · Wardrobe · Home Office · Garage · Corridor · See all
  - *Wall Colours*: Green Walls · Orange Walls · Blue Walls · Purple Walls · Red Walls · Grey Walls · Yellow Walls · Pink Walls · Black Walls · Brown Walls

#### Photowall — FULL AXES WITH ITEM COUNTS, VERBATIM
All of the following from [photowall.co.uk/posters](https://www.photowall.co.uk/posters). **Total 20,366 motifs; posters priced from £18–£21 GBP.** Counts are the single most useful weighting signal harvested anywhere in this job.

- *Discover*: Top Sellers · New · Nature · Art & Design · Kids · Animals · Surface & Textures · Astronomy · Entertainment & Movies · Maps, Flags & Places · Patterns & Shapes · Spirituality & Religion · Sports
- *By Motif (with counts)*: Nature (9,864) · Art & Design (8,379) · Maps, Flags & Places (3,589) · Animals (3,281) · Kids (1,707) · Surface & Textures (675) · Entertainment & Movies (632) · Astronomy (332) · Sports (174) · Spirituality & Religion (125)
- *By Colour (with counts)*: Black & white (1,773) · Blue (2,049) · Green (1,774) · Grey (1,009) · Multi coloured (929) · White (919) · Brown (852) · Pink (777) · Beige (710) · Black (583) · Orange (346) · Red (340) · Yellow (335) · Turquoise (334) · Purple (309) · Light green (106) · Dark (59) · Light blue (26) · Dark green (16) · Light pink (14)
- *By Room (with counts)*: Living room (2,587) · Kids Room (1,542) · Bedroom (1,142) · Hallway (758) · Diningroom (729) · Teenroom (406) · Office (383) · Kitchen (304) · Bathroom (171) · Nursery (138) · Ceiling
- *By Style (with counts)*: Vintage (1,399) · Minimalist (390) · Japandi (169) · Industrial (159) · Glam & Luxury (99) · Mid-Century Modern (79) · Rustic & Country (76) · Bohemian (60) · Scandinavian (28) · Chinoiserie (28)
- *Wall Format (with counts)*: Landscape (12,074) · Portrait (6,555) · Square (1,490) · Extra wide (247)
- *Image Type*: Illustrated (13,713) · Photographic (6,560)

#### Olive et Oriel — FULL TREE, VERBATIM (Australian, **AUD $ only**)
All of the following from [oliveetoriel.com](https://www.oliveetoriel.com/). Wall-art branches only reproduced here:

- **Wall Art**
  - *Art Prints & Posters*: Prints—New & Trending · Upload Your Photos · Abstract · Botanical & Floral · Coastal & Beach · Pairs & Sets · Animals & Wildlife · Typography & Quotes · Landscapes & Nature · Kids & Nursery · Travel & Destinations · Vintage-Inspired · Zodiac & Star Signs
  - *Framed Art Prints*: Shop New Wall Art · Matching Pairs & Sets · 3 Piece Sets · Panoramic Wall Art · Family Photo Printing · Coastal Art · Modern & Minimalist · Fine Art Photography · Abstract · Floral & Botanical · Aboriginal · Figurative & Portraits · Travel Photography
  - *Canvas*: New Arrivals · Upload Your Photo · Abstract Art · Aboriginal · Coastal & Beach · Modern Neutral Abstracts · Vintage Designs · Family Photos on Canvas · Botanical & Floral · Landscape Paintings
  - *Shop by Colour*: Blue · Green · Grey · Pink · Brown · Orange · Yellow · Purple · Red · Beige & Neutrals · Vibrant & Colourful · Black & White
  - *Customisable*: Family Photos · Personalized Wall Art
- **Sets**: Paired Art · Set of 3
- **Room**: Bedroom · Living Room · Kitchen · Dining · Kids Rooms
- **Kids** — *Themed Bedrooms*: Outer Space Theme · Coastal & Beach Theme · Dinosaurs · Into the Jungle · Magical Garden · Mermaids · Australiana; *Kids Wall Decor*: Art Prints · Wall Decals · Canvas · Matching Print Sets · Print Trios for Kids
- **Artists**: Indigenous · Photographers · Illustrators & Mixed-Media Artists · Abstract Painting

#### Paper Collective — NAV HARVESTED (shallow tree)
From [papercollective.com](https://www.papercollective.com/). Top level: News · Art Prints · Crafted Forms · Acoustic Panels · Frames & Shelves · Professional · Inspiration.
- *Art Prints categories*: Paintings · Photography · Graphic Design · Limited Editions & Originals · Bestsellers · Square Art · MADO Family Art
- *Named collections*: FW26 Collection · Fiberium (Limited Edition) · Studio Life (Limited Edition) · Woven Check/Dome/Rings/Oval (Limited Edition) · Ceramic Weave (Limited Edition) · Mental Pictures (Limited Edition) · Zodiac Collectibles
- *Inspiration tags*: Large Art · Art Walls · Room Inspiration
- Paper Collective merchandises by **medium** (Paintings / Photography / Graphic Design), not by motif, colour or room — the clearest outlier in the set.

#### Desenio — PARTIAL (site blocked; structure inferred from live search-result URLs only)
Confirmed-live URL paths, each of which is a real category node:
- `desenio.co.uk/posters-prints/` (root) — [source](https://desenio.co.uk/posters-prints/)
- `/posters-prints/art-prints/` with children: `abstract-line-and-shapes`, `watercolor-paintings`, `minimalist-art`, `line-art-2`, `abstract-art`, `graphical` — [Desenio art prints](https://desenio.ca/posters-prints/art-prints/), [line art](https://desenio.com/posters-prints/art-prints/line-art-2/), [minimalist](https://desenio.com/posters-prints/art-prints/minimalist-art/), [graphical](https://desenio.com/posters-prints/art-prints/graphical/), [watercolour](https://desenio.com/posters-prints/art-prints/watercolor-paintings/)
- `/posters-prints/top-list/` — the bestseller page, titled "Bestsellers scandinavian art" — [source](https://desenio.com/posters-prints/top-list/)
- `/posters-prints/sizes/posters-30x40cm/` and `/posters-prints/sizes/50x70cm/` — a dedicated **size** axis — [source](https://desenio.co.uk/posters-prints/sizes/posters-30x40cm/)
- `/frames/sizes-frames/30x40-frames/` and `/frames/sizes-frames/50x70-frames/` — a frames tree mirrored by size — [source](https://desenio.co.uk/frames/sizes-frames/50x70-frames/)
- `/canvas-prints/vintage-motifs/` — a canvas tree with its own motif children — [source](https://desenio.com/canvas-prints/vintage-motifs/)
- `/g/gallery-walls/` — gallery-wall sets — [source](https://desenio.eu/g/gallery-walls/)
- Desenio's own copy: prints are sold as "art photography, black & white prints, Scandinavian wall art, retro art, modern prints, abstract art, illustrations and children's wall art"; most popular categories are "photo art, typographical posters, hand-illustrated posters, graphical prints, line art". Shop-by-room values: Kitchen, Kids Room, Bathroom, Living Room, Bedroom, Office, Hallway. Named style values: Scandinavian, Romantic, Playful, Contemporary, Timeless Classic, Bold & Eclectic, Modern & Urban. — [Desenio](https://desenio.com/)

#### Poster Store — PARTIAL (site blocked; structure inferred from live search-result URLs only)
Confirmed-live URL paths: `/posters-prints/` (root), `/posters-prints/bestseller-art-prints/`, `/posters-prints/living-room-wall-art/`, `/posters-prints/kitchen/`, `/posters-prints/citrus-posters/` — [Poster Store posters](https://posterstore.com/posters-prints/), [bestsellers](https://posterstore.com/posters-prints/bestseller-art-prints/), [living room](https://posterstore.com/posters-prints/living-room-wall-art/), [citrus](https://posterstore.com/posters-prints/citrus-posters/)
- Catalogue size: "40,000+ unique wall posters and canvases online"; "Influenced by Scandinavian art". — [posterstore.co.uk](https://posterstore.co.uk/)
- Named popular categories: Fashion · Famous Artist Posters · Autumn · Funny Posters · Kitchen · Bauhaus Prints · Poster Packs · Photo art. Named motifs: black & white · vintage · landscapes · nature. Room values: Kitchen · Kids Room · Living Room · Bedroom · Home Office · Bathroom · Laundry Room. Living-room styles named: "modern minimalist, retro vintage, and botanical". — [posterstore.co.uk](https://posterstore.co.uk/), [living room](https://posterstore.com/posters-prints/living-room-wall-art/)

#### Posterlounge — PARTIAL (site blocked; structure inferred from live search-result URLs only)
Confirmed-live URL paths: `/wall-art/`, `/wall-art/posters/`, `/wall-art/art-prints/`, `/wall-art/gallery-prints/`, `/wall-art/posters/living-room/`, `/wall-art/posters/graphic-design/` — [wall art](https://www.posterlounge.co.uk/wall-art/), [posters](https://www.posterlounge.co.uk/wall-art/posters/), [art prints](https://www.posterlounge.co.uk/wall-art/art-prints/), [gallery prints](https://www.posterlounge.co.uk/wall-art/gallery-prints/), [graphic design](https://www.posterlounge.co.uk/wall-art/posters/graphic-design/)
- *Product/medium ladder*: posters · canvas prints · acrylic prints · wood prints · art prints · aluminium prints · gallery prints · wall stickers · foam board prints — [Posterlounge](https://www.posterlounge.co.uk/wall-art/posters/)
- *Interior styles*: Japandi · Boho · Contemporary · Mid-century modern · Nautical · Vintage
- *Subjects/themes*: children's rooms · kitchens · living rooms · bedrooms · black and white · photography · contemporary · sayings & quotes · nature · abstract art · vintage · cities · flowers · landscapes · animals · pop art · world maps · stars & celebrities · Buddhism · lighthouses · country style

#### Juniqe — PARTIAL (SPA returns empty body; lists recovered via search)
Confirmed-live category-hub URLs: `/uk/wall-art/wall-art/categories`, `/uk/wall-art/wall-art/styles`, `/uk/wall-art/wall-art/rooms`, `/uk/trends`, `/uk/eye-catcher` (large format), `/uk/wall-art/pink`, `/uk/wall-art/living-room` — [Juniqe categories](https://www.juniqe.com/uk/wall-art/wall-art/categories), [styles](https://www.juniqe.com/uk/wall-art/wall-art/styles), [rooms](https://www.juniqe.com/uk/wall-art/wall-art/rooms), [trends](https://www.juniqe.com/uk/trends), [Eye-Catcher](https://www.juniqe.com/uk/eye-catcher)
- Juniqe exposes a **colour axis** as flat URLs (`/uk/wall-art/pink` pattern). Only `pink` was directly confirmed.

#### King & McGaw — PARTIAL (403; lists recovered via search)
Confirmed-live URLs: `/collections`, `/museums-and-archives`, `/collections/in-demand`, `/new`, `/stories/museum-quality-prints`, plus a separate trade site `trade.kingandmcgaw.com` — [Collections](https://www.kingandmcgaw.com/collections), [Museums and Archives](https://www.kingandmcgaw.com/museums-and-archives), [In Demand](https://www.kingandmcgaw.com/collections/in-demand)

### Inferences
- Four distinct merchandising architectures are visible: (a) **full four-axis** (Desenio, Poster Store, Photowall, Bimago, Fy!, Olive et Oriel, Abstract House); (b) **three-axis, no colour** (The Poster Club); (c) **medium-first** (Paper Collective, Posterlounge); (d) **licence-first** (King & McGaw, Surface View, where the collection *is* the museum partner).
- Colour is the axis most often omitted by curated/artist-led retailers and most often present at commodity retailers — Wallfillers' eBay store is organised by colour and *nothing else*, which is the purest expression of the commodity end.

### Gaps
- Desenio's and Poster Store's complete motif/style/colour/room menus — the single most important deliverable in the brief — could not be harvested. Both block this environment with HTTP 429. Current Wayback snapshots exist and are named above; they need a machine that can reach web.archive.org.
- Pictowall returned HTTP 522 (origin unreachable) and was not harvested at all.
- Surface View's own collection list was not harvested (403); only its partner institutions are evidenced.

---

## Q2. Named MOTIF / SUBJECT lists

### Takeaway
A stable core motif vocabulary of roughly 18 terms recurs across every retailer harvested — Abstract, Botanical/Floral, Animals, Landscape, Cities/Maps, Black & White, Typography/Quotes, Vintage, Kids, Line Art, Photography, Food & Drink, Travel, Celestial/Astronomy, Figurative/Portrait, Coastal/Nautical, Sport, Music — and the per-retailer variation is mostly in how finely that core is subdivided.

### Cited Findings
Consolidated motif vocabulary, by retailer (all from the verbatim trees cited in Q1):

| Motif term | Retailers using it |
|---|---|
| Abstract | The Poster Club, Abstract House, Bimago, Fy!, Olive et Oriel, Juniqe, Posterlounge, Desenio |
| Botanical / Floral / Flowers | The Poster Club, Abstract House, Bimago, Fy!, Olive et Oriel, Juniqe, Posterlounge, Desenio |
| Animals / Wildlife | The Poster Club, Bimago, Fy!, Olive et Oriel, Photowall, Juniqe, Posterlounge, King & McGaw |
| Landscape / Nature | Abstract House, Bimago, Olive et Oriel, Photowall, Juniqe, Posterlounge, King & McGaw, Poster Store |
| Cities / Cityscape / Maps / World Maps | Abstract House, Bimago, Fy!, Photowall, Posterlounge, King & McGaw (Landmarks) |
| Black & White | Abstract House, Bimago, Fy! (B&W), Photowall, Juniqe, Posterlounge, Desenio, Poster Store |
| Typography / Quotes / Text | Bimago, Olive et Oriel, Juniqe, Posterlounge (sayings & quotes), King & McGaw, Desenio |
| Vintage | Fy!, Olive et Oriel (Vintage-Inspired), Photowall, Bimago, Juniqe, Posterlounge, King & McGaw, Desenio, Poster Store |
| Kids / Nursery | The Poster Club, Olive et Oriel, Photowall, Bimago (For Children), Juniqe, Posterlounge, Desenio |
| Line Art | The Poster Club, Juniqe, Desenio |
| Photography / Photo Art | The Poster Club, Abstract House (Fine Art Photography), Bimago, Paper Collective, Juniqe, Posterlounge, King & McGaw, Desenio, Poster Store |
| Food & Drink / Drinks | Fy!, Juniqe (Food, Drinks) |
| Travel | Fy!, Olive et Oriel (Travel & Destinations), Juniqe |
| Celestial / Astronomy / Zodiac | Photowall (Astronomy), Olive et Oriel (Zodiac & Star Signs), The Poster Club (The Zodiac Collection), Paper Collective (Zodiac Collectibles) |
| Figurative / Portraits / People | The Poster Club (Human & Figurative), Abstract House, Bimago (People), Olive et Oriel, Juniqe, King & McGaw (Figures) |
| Coastal / Nautical / Marines | Fy!, Olive et Oriel, Bimago (Marines), Posterlounge (Nautical), King & McGaw (Coastal) |
| Sport | Fy!, Photowall, King & McGaw |
| Music | Fy!, Juniqe, King & McGaw (Art Inspired By Music) |
| Film / Movies / Entertainment | Fy!, Photowall (Entertainment & Movies), Juniqe, King & McGaw (Film) |
| Geometric | Abstract House, Bimago |
| Still Life | Bimago |
| Street Art / Banksy | Bimago (two separate nodes: "Street Art", "Banksy and Street Art") |
| Fashion | Poster Store |
| Architecture | (Not found as a top-level motif at any harvested retailer; closest are King & McGaw "Landmarks" and Bimago "Cities") |
| Surface & Textures | Photowall (675 items) |
| Spirituality & Religion / Sacred Art / Zen / Buddhism | Photowall, Bimago (Sacred Art, Zen), Posterlounge (Buddhism) |
| Automotive | Bimago |
| African / Aboriginal / Indigenous | Bimago (African), Olive et Oriel (Aboriginal, Indigenous) |
| Love & Heart | Bimago, Juniqe |
| Seasons | Bimago, Fy! (Father's Day, Autumn at Poster Store) |
| Monsters & Fantasy | Juniqe, Bimago (Fantasy) |
| Celebrities / Stars | Juniqe, Posterlounge (stars & celebrities) |
| Motivational | Juniqe |
| Whimsical | King & McGaw |
| Lighthouses | Posterlounge (unusually specific) |
| Kitchen & Bath | King & McGaw (merchandises a room as a subject) |
| Disco | Fy! (trend-led motif) |
| Mandala / Marble / Stone / Wood / Brick / Trees | Bimago |

King & McGaw's full named category list, verbatim: Abstract · Coastal · Figures · Film · Floral · Graphic & Illustration · Kitchen & Bath · Landmarks · Landscapes · Museum · Nature · Photography · Sport · Typography · Vintage · Warhol · Whimsical · Wildlife — [King & McGaw collections](https://www.kingandmcgaw.com/collections)

Juniqe's full named themed-category list: Photography · Kids · Typography · Motivational · Vintage · Animals · Botanical · Travel · Nature · Food · Portraits · Japanese Inspired · Celebrities · Music · Drinks · Love · Monsters & Fantasy · Movies · Abstract — [Juniqe categories](https://www.juniqe.com/uk/wall-art/wall-art/categories)

### Inferences
- Every motif in the brief's example list is confirmed at two or more retailers **except "Architecture"**, which no harvested retailer merchandises under that name — it is split between "Cities/Cityscape" and "Landmarks".
- Photowall's counts give a usable weighting: Nature and Art & Design together are 18,243 of 20,366 motifs (~90%), so a generation programme matching this market by volume is overwhelmingly a nature-and-graphic-design programme.

### Gaps
- Desenio's and Poster Store's complete motif lists remain unharvested (see Q1 gaps). The terms recorded for them are from marketing copy, not from their menus, and should be treated as indicative only.

---

## Q3. Named STYLE lists

### Takeaway
The style axis is more volatile than the motif axis and splits into two sub-types that retailers mix freely: **art-historical movements** (Bauhaus, Art Deco, Art Nouveau, Pop Art, Cubism, Expressionism, Surrealism) and **interior-décor styles** (Scandinavian, Japandi, Boho, Mid-Century Modern, Industrial, Coastal, Maximalist, Cottage Core).

### Cited Findings
- **Fy!**: Maximalist · Cottage Core · Modern · Scandinavian · Art Deco · Bohemian · Eclectic · Traditional · Abstract · Industrial · Coastal (+ a "Style Quiz" tool) — [iamfy.co](https://iamfy.co/)
- **Photowall** (with counts): Vintage (1,399) · Minimalist (390) · Japandi (169) · Industrial (159) · Glam & Luxury (99) · Mid-Century Modern (79) · Rustic & Country (76) · Bohemian (60) · Scandinavian (28) · Chinoiserie (28) — [photowall.co.uk](https://www.photowall.co.uk/posters)
- **Bimago, canvas styles**: Art Nouveau · Boho · Glamour · Industrial · Marines · Minimalist · Modern · Pop Art · Photographs · Scandinavian · Vintage · Watercolor — [bimago.co.uk](https://www.bimago.co.uk/)
- **Bimago, poster "Trendy Styles"**: Vintage · Boho · Glamour · Industrial · Modern · Scandinavian · Minimalist · Pop Art — [bimago.co.uk](https://www.bimago.co.uk/)
- **Bimago, Inspirations styles** (the widest list harvested anywhere): Boho · Scandinavian · Glamour · Loft · Classic · Hampton · Art Déco · New York · Modern · Provencal · Rustic · Vintage · Shabby Chic · Nautical · Eclectic · Minimalist — [bimago.co.uk](https://www.bimago.co.uk/)
- **Bimago, wallpaper styles** (reusable vocabulary): Art déco · Boho · Exotic · Eclectic · Futuristic · Glamour · Japan · Classic · Colonial · Industrial · Seascape · Minimal · Modern · Oriental · Retro · Rustic · Scandi boho · Shabby Chic · Scandi · Vintage — [bimago.co.uk](https://www.bimago.co.uk/)
- **Juniqe**: Vintage · Black & White · Calligraphy & Lettering · Bauhaus · Line Art · Japanese Inspired · Boho · Country style · Pop Art · Street Art Style · Minimalism · Cubism · Expressionism · Paper marbling · Memphis design · Surrealism — [Juniqe styles](https://www.juniqe.com/uk/wall-art/wall-art/styles)
- **Posterlounge**: Japandi · Boho · Contemporary · Mid-century modern · Nautical · Vintage; plus "vintage or Scandinavian, boho or industrial" — [Posterlounge](https://www.posterlounge.co.uk/wall-art/posters/)
- **Desenio**: Scandinavian · Romantic · Playful · Contemporary · Timeless Classic · Bold & Eclectic · Modern & Urban — [Desenio](https://desenio.com/)
- **Paper Collective** (medium-as-style): Paintings · Photography · Graphic Design — [papercollective.com](https://www.papercollective.com/)
- **Abstract House** merges style and subject into one axis named "Shop By Style & Subject" (Abstract Art, Botanical, Geometric, Cityscape, Fine Art Photography, Landscape, Figurative) — [abstracthouse.com](https://abstracthouse.com/)
- **Poster Store**: "Bauhaus Prints" is a named top category — [posterstore.co.uk](https://posterstore.co.uk/)
- **Fy! named style-as-collection**: William Morris Style · Japanese Art · Art Nouveau / Klimt — [iamfy.co](https://iamfy.co/)

### Inferences
- Of the brief's candidate style list, confirmed at two or more retailers: Scandinavian, Japandi, Mid-Century, Bauhaus, Art Deco, Art Nouveau, Boho, Minimalist, Vintage, Retro, Illustration, Photography, Painting, Graphic, Watercolour, Line Drawing. **Collage and Risograph were not found at any harvested retailer** — they appear to be absent from this market's merchandised style vocabulary.
- Terms found that the brief did not anticipate, and which are therefore the live 2025-26 additions: Maximalist, Cottage Core, Glam & Luxury, Chinoiserie, Dopamine House, Memphis design, Paper marbling, Hampton, Provencal, Shabby Chic, Loft, Scandi Boho.

### Gaps
- Desenio's and Poster Store's style menus (as opposed to their marketing adjectives) are unharvested.

---

## Q4. COLOUR axis and exact colour vocabulary

### Takeaway
Six retailers expose a colour axis and their vocabularies agree on a core of about ten values (Blue, Green, Pink, Yellow, Red, Brown, Grey, Black & White, Beige/Neutral, Multi/Vibrant); Photowall's is the most granular at 20 values with counts, and Wallfillers' eBay store is organised by colour to the exclusion of every other axis.

### Cited Findings
- **Photowall (20 values, with counts)**: Beige (710) · Black (583) · Black & white (1,773) · Blue (2,049) · Brown (852) · Dark (59) · Dark green (16) · Green (1,774) · Grey (1,009) · Light blue (26) · Light green (106) · Light pink (14) · Multi coloured (929) · Orange (346) · Pink (777) · Purple (309) · Red (340) · Turquoise (334) · White (919) · Yellow (335) — [photowall.co.uk](https://www.photowall.co.uk/posters)
- **Olive et Oriel (12 values)**: Blue · Green · Grey · Pink · Brown · Orange · Yellow · Purple · Red · Beige & Neutrals · Vibrant & Colourful · Black & White — [oliveetoriel.com](https://www.oliveetoriel.com/)
- **Abstract House (9 values)**: Blue Art · Brown Art · Green Art · Black & White · Neutral Palette · Red Art · Vibrant Colours · Yellow Wall Art · View All Colours — [abstracthouse.com](https://abstracthouse.com/)
- **Fy! (9 values)**: All Colours · Green · Pink · Blue · Yellow · B&W · Warm · Pastels · Red — note Fy! includes two *temperature/tonal* values (Warm, Pastels) rather than hues — [iamfy.co](https://iamfy.co/)
- **Wallfillers (13 values, the entire store taxonomy)**: Red Canvas · Purple Canvas · Black and White Canvas · Plum Canvas · Teal Canvas · Brown Canvas · Pink Canvas · Green Canvas · Blue Canvas · Yellow Canvas · Orange Canvas · Cream Canvas · Other — [wallfillers canvas](https://www.ebay.co.uk/str/wallfillerscanvas)
- **Bimago** exposes colour only as *wall* colour for styling, not print colour (10 values): Green Walls · Orange Walls · Blue Walls · Purple Walls · Red Walls · Grey Walls · Yellow Walls · Pink Walls · Black Walls · Brown Walls — [bimago.co.uk](https://www.bimago.co.uk/)
- **Juniqe** exposes colour as flat URLs; `/uk/wall-art/pink` confirmed live — [Juniqe pink](https://www.juniqe.com/uk/wall-art/pink)
- **Desenio**: colour range described only as "soft pastels and neutral tones to bold and vibrant hues" — no enumerated values recovered — [Desenio](https://desenio.com/)
- **The Poster Club** and **Paper Collective**: **no colour axis exposed** — [theposterclub.com](https://www.theposterclub.com/), [papercollective.com](https://www.papercollective.com/)

### Inferences
- Wallfillers' two non-standard values, **Plum** and **Teal**, are absent from every curated retailer's vocabulary and present at the highest-volume eBay canvas seller. Combined with its item titles (Q6), Plum and Teal look like a UK eBay-specific commodity demand that the Scandinavian retailers do not serve.
- "Cream" (Wallfillers) / "Beige & Neutrals" (Olive et Oriel) / "Neutral Palette" (Abstract House) / "Beige" (Photowall, 710 items) are the same bucket under four names, and it is large everywhere.

### Gaps
- Juniqe's and Poster Store's full colour value lists; Desenio's colour values (if any discrete axis exists).

---

## Q5. ROOM axis

### Takeaway
Ten room values are near-universal; the competitive variation is in the long tail, where Fy! (Laundry Room, Coffee Nook, Cloakroom) and Bimago (Gaming Room, Garage, Wardrobe, Living Room with Kitchenette) have pushed furthest.

### Cited Findings

| Room | Fy! | The Poster Club | Photowall (count) | Bimago | Olive et Oriel | Abstract House | Desenio | Poster Store | Juniqe | Posterlounge |
|---|---|---|---|---|---|---|---|---|---|---|
| Living Room | Yes | Yes | 2,587 | Yes | Yes | via "Art By Room" | Yes | Yes | Yes | Yes |
| Bedroom | Yes | Yes | 1,142 | Yes | Yes | " | Yes | Yes | Yes | Yes |
| Kitchen | Yes | Yes | 304 | Yes | Yes | " | Yes | Yes | Yes | Yes |
| Dining Room | — | — | 729 (Diningroom) | Yes | Yes (Dining) | " | — | — | Yes (Kitchen-Dining) | — |
| Hallway | Yes | — | 758 | Yes | — | " | Yes | — | Yes | — |
| Bathroom | Yes | Yes | 171 | Yes | — | " | Yes | Yes | Yes | — |
| Home Office / Office | Yes | Yes | 383 | Yes | — | " | Yes | Yes | Yes | — |
| Nursery | — | — | 138 | — | Yes (Kids & Nursery) | " | — | — | — | — |
| Kids' Room | Yes | Yes | 1,542 | Yes | Yes | " | Yes | Yes | Yes | Yes |
| Teen Room | — | — | 406 (Teenroom) | Yes | — | " | — | — | Yes (Teenager's) | — |
| Laundry / Utility | Yes (Laundry Room) | — | — | — | — | " | — | Yes (Laundry Room) | — | — |
| Stairway | — | — | — | — | — | — | — | — | — | — |
| Other | Coffee Nook, Cloakroom | — | Ceiling | Gaming Room, Guest Room, Garage, Wardrobe, Corridor, Living Room with Kitchenette, Beauty studio, Restaurant | — | Art For The Office | — | — | Architectural Offices | — |

Sources as in Q1: [iamfy.co](https://iamfy.co/), [theposterclub.com](https://www.theposterclub.com/), [photowall.co.uk](https://www.photowall.co.uk/posters), [bimago.co.uk](https://www.bimago.co.uk/), [oliveetoriel.com](https://www.oliveetoriel.com/), [abstracthouse.com](https://abstracthouse.com/), [Desenio](https://desenio.com/), [posterstore.co.uk](https://posterstore.co.uk/), [Juniqe rooms](https://www.juniqe.com/uk/wall-art/wall-art/rooms), [Posterlounge](https://www.posterlounge.co.uk/wall-art/posters/)

Beyond-domestic room axes: Fy! "Art for Business" and "Art for Hotels"; Abstract House "Art For The Office"; Bimago "Beauty studio" and "Restaurant"; Olive et Oriel "Hotel & Hospitality" and "Childcare" (wallcoverings); King & McGaw operates a separate trade site at trade.kingandmcgaw.com. — [iamfy.co](https://iamfy.co/), [abstracthouse.com](https://abstracthouse.com/), [bimago.co.uk](https://www.bimago.co.uk/), [King & McGaw trade](https://trade.kingandmcgaw.com/)

### Inferences
- **"Stairway" from the brief's list was found at no retailer.** The closest is Bimago's "Corridor" and the universal "Hallway".
- Photowall's counts show the room axis is extremely top-heavy: Living Room + Kids Room + Bedroom = 5,271 of roughly 8,160 room-tagged items.

### Gaps
- Abstract House has an "Art By Room" node but its individual room values were not enumerated on the pages harvested.

---

## Q6. FORMAT and SIZE ladders, sets, frames

### Takeaway
The European metric poster ladder is standardised at 21x30 / 30x40 / 40x50 / 50x70 / 60x90 / 70x100 cm, confirmed outright at Bimago and Desenio; the set/multiple vocabulary is consistently pairs, sets of three, sets of five and gallery walls; and Wallfillers shows the UK eBay canvas market runs on a completely different ladder measured in total width (120cm, 130cm, 160cm).

### Cited Findings
- **Bimago poster size ladder, verbatim**: 21x30 cm · 30x40 cm · 40x60 cm · 50x70 cm · 60x90 cm · 70x100 cm — [bimago.co.uk](https://www.bimago.co.uk/)
- **Desenio** has a dedicated size axis under `/posters-prints/sizes/`, with confirmed nodes `posters-30x40cm` and `50x70cm`, and gives imperial equivalents in-page: 30x40 cm = 11¾ x 15¾ in; 50x70 cm = 19¾ x 27½ in. Desenio's frames tree mirrors the same ladder at `/frames/sizes-frames/30x40-frames/` and `/50x70-frames/`. Desenio's EU site uses a dual-label format: "30x40 cm (11 x 15 in)" — [Desenio 30x40](https://desenio.co.uk/posters-prints/sizes/posters-30x40cm/), [Desenio 50x70](https://desenio.co.uk/posters-prints/sizes/50x70cm/), [Desenio frames 50x70](https://desenio.co.uk/frames/sizes-frames/50x70-frames/), [Desenio EU](https://desenio.eu/prints/sizes/30x40-cm-11-x-15-in/)
- **Photowall wall-format axis (orientation rather than size)**: Landscape (12,074) · Portrait (6,555) · Square (1,490) · Extra wide (247) — [photowall.co.uk](https://www.photowall.co.uk/posters)
- **Bimago canvas format types**: Canvas gallery · Framed canvas · Decorative acoustic panels · XXL Large Canvas Prints · Round Canvas Prints · Premium Canvas Print · Multi Part Canvas Prints. Room-divider panel counts: 3 panels · 5 panels. Wall panel shapes: Hexagon · Square · Oval · Rectangular — [bimago.co.uk](https://www.bimago.co.uk/)
- **Sets and multiples**: Fy! — Two Print Sets, Three Print Sets, Gallery Walls (with an "AI Designer"); Abstract House — Set Of Three Prints, Gallery Walls & Sets, Large Artwork; Olive et Oriel — Paired Art, Set of 3, Matching Pairs & Sets, 3 Piece Sets, Panoramic Wall Art, Print Trios for Kids; The Poster Club — Art Wall Gallery + Art Wall Designer; Desenio — `/g/gallery-walls/`; Paper Collective — Art Walls, Large Art, Square Art — [iamfy.co](https://iamfy.co/), [abstracthouse.com](https://abstracthouse.com/), [oliveetoriel.com](https://www.oliveetoriel.com/), [theposterclub.com](https://www.theposterclub.com/), [Desenio gallery walls](https://desenio.eu/g/gallery-walls/), [papercollective.com](https://www.papercollective.com/)
- **Large-format nodes**: Fy! "XL Art Prints"; The Poster Club "X-Large Art Prints"; Juniqe "Eye-Catcher" (large-format); Bimago "XXL Large Canvas Prints"; Abstract House "Large Artwork"; Paper Collective "Large Art" — [iamfy.co](https://iamfy.co/), [theposterclub.com](https://www.theposterclub.com/), [Juniqe Eye-Catcher](https://www.juniqe.com/uk/eye-catcher), [bimago.co.uk](https://www.bimago.co.uk/)
- **Frame taxonomies**:
  - Fy! — *Colour*: Black, White, Natural, Brown, Gold, Silver. *Style*: Essentials, Linear, Gallery, Heritage, Coastal, Statement. *Named frame models*: Standard, Beat, Open, Vitrine, Grain, Lift, Tally, Lull, Step, Codex, Drift, Echo — [iamfy.co](https://iamfy.co/)
  - The Poster Club — All Frames, Oak Frames, Coloured Frames, plus a separate **Passepartouts** (mount) category — [theposterclub.com](https://www.theposterclub.com/)
  - Paper Collective — Frames & Shelves, including Floating Gallery Shelves and the Artefakt Shelf — [papercollective.com](https://www.papercollective.com/)
  - Desenio — frames organised by size — [Desenio frames](https://desenio.co.uk/frames/sizes-frames/50x70-frames/)
- **Posterlounge medium ladder** (format-as-substrate): posters · canvas prints · acrylic prints · wood prints · art prints · aluminium prints · gallery prints · wall stickers · foam board prints — [Posterlounge](https://www.posterlounge.co.uk/wall-art/posters/)
- **Wallfillers UK eBay canvas ladder** — sized by overall set width, not by sheet: "130cm", "160cm", "120cm x 50cm", "125cm Wide", "79cm Square"; panel counts of 3, 4 and 5 ("Split 3 Panel", "Set of 4", "Set of 5", "5 Part", "Four Panel") — [wallfillers canvas](https://www.ebay.co.uk/str/wallfillerscanvas)

### Inferences
- **40x50 cm and the A-size ladder (A4/A3/A2/A1) appear at none of the harvested retailers.** The brief anticipated both; the European trade ladder recovered here is 21x30 / 30x40 / 40x60 / 50x70 / 60x90 / 70x100. Note Bimago uses **40x60**, not 40x50.
- Fy!'s twelve named frame models and six frame styles are a far deeper frame taxonomy than anyone else's, and are the only retailer treating the frame as a design object with its own product names.

### Gaps
- No retailer's complete size-to-price matrix was harvested; Abstract House, Fy! and The Poster Club collection URLs guessed for this purpose all 404'd, and the three Scandinavian majors block access.
- Square and panoramic ladders exist (Paper Collective "Square Art", Olive et Oriel "Panoramic Wall Art", Photowall "Square"/"Extra wide") but their actual dimensions were not recovered.

---

## Q7. Artist-free / in-house ranges vs licensed-artist ranges, and public-domain ranges

### Takeaway
The catalogue splits cleanly into three commercial tiers, and only the first is matchable by generation: **anonymous in-house commodity** (Desenio, Poster Store, Photowall, Bimago, Wallfillers — no artist attribution anywhere in the taxonomy), **named-artist licensed** (The Poster Club, Paper Collective, Fy!, Juniqe, Olive et Oriel — the artist *is* a navigation axis), and **institution-licensed museum reproduction** (King & McGaw, Surface View — the museum partner *is* the collection).

### Cited Findings

**Tier 1 — artist-free / in-house (generation-matchable):**
- **Photowall**: 20,366 motifs merchandised purely by motif/colour/room/style with no artist axis in the navigation at all — [photowall.co.uk](https://www.photowall.co.uk/posters)
- **Bimago**: no artist axis for its own ranges; the only named individuals are dead painters in the "Reproductions" node — [bimago.co.uk](https://www.bimago.co.uk/)
- **Wallfillers**: 13 colour categories, no artist axis, product titles are pure keyword strings ending in a stock number ("...Prints Set 4042") — [wallfillers canvas](https://www.ebay.co.uk/str/wallfillerscanvas)
- **Desenio** and **Poster Store**: neither exposes an artist axis in any recovered URL path; Poster Store does have a "Famous Artist Posters" node, which by its name is reproduction rather than in-house — [Desenio](https://desenio.com/), [posterstore.co.uk](https://posterstore.co.uk/)

**Tier 2 — named-artist licensed:**
- **The Poster Club**: "Shop By Artist" is a top-level node; named artist collections are The Zodiac Collection by Sofia Lind, The Peripheral Collection by Liv Lee, The Symbiont Collection by Suzanne Lustig, The Interstellar Collection by Anne Novak; plus "Artist Collaborations" and "Limited Editions" — [theposterclub.com](https://www.theposterclub.com/)
- **Paper Collective**: "Artists" and "Join as an Artist" nodes; Limited Editions & Originals range with named editions Fiberium, Studio Life, Woven Check/Dome/Rings/Oval, Ceramic Weave, Mental Pictures — [papercollective.com](https://www.papercollective.com/)
- **Olive et Oriel**: Artists axis split Indigenous / Photographers / Illustrators & Mixed-Media Artists / Abstract Painting; "Commission An Artist"-style trade offer via The Designer Edit → Signature Art Collection — [oliveetoriel.com](https://www.oliveetoriel.com/)
- **Abstract House**: "Limited Edition Prints", "Original Art", "Commission An Artist", "Art Advisory Service" — [abstracthouse.com](https://abstracthouse.com/)

**Tier 3 — public domain / museum / vintage reproduction:**
- **Bimago "Reproductions"** — a 21-painter public-domain range, every one of whom is out of copyright: Canaletto, Caravaggio, Caspar David Friedrich, Claude Monet, Edgar Degas, El Greco, Gustav Klimt, Hieronymus Bosch, Jan van Eyck, Jan Vermeer, Leonardo da Vinci, Michelangelo, Rafael Sanzio, Rembrandt, Sandro Botticelli, Pierre-Auguste Renoir, Titian, Vincent van Gogh, Wassily Kandinsky, William Blake, William Turner. Bimago also sells Klimt, Van Gogh and Banksy as Painting Kits — [bimago.co.uk](https://www.bimago.co.uk/)
- **King & McGaw** — the deepest institution-licensed range in the UK. Named collections: Andy Warhol · Art Inspired By Music · Bluebellgray · Chatsworth House · Courtauld Gallery · Flower Fairies · Hollywood Photo Archive · Illustrated London News · Imperial War Museums · Sir John Soane's Museum · Ladybird Books · London Metropolitan Archives · London Transport Museum · The Lowry · National Archives · National Portrait Gallery · National Gallery · Pablo Picasso · P&O Heritage · Penguin Books · Royal Academy of Arts · Royal Horticultural Society · The Snowman · Stilltime Collection · Tate. It "works directly with major museums including the V&A, Tate, MoMA and the National Gallery, plus individual artists and estates, to produce licensed fine-art prints", and describes its offer as "uniquely combin[ing] rarely available or exclusive museum images with contemporary work from new artists". There is also a dedicated `/museums-and-archives` hub and a "Museum" category — [King & McGaw collections](https://www.kingandmcgaw.com/collections), [Museums and Archives](https://www.kingandmcgaw.com/museums-and-archives), [Wikipedia](https://en.wikipedia.org/wiki/King_and_McGaw)
- **Surface View** — collections are "a carefully selected choice of images from museums, galleries and archives that range from Old Masters and vintage maps through black and white photography, vintage, kitsch and retro style, iconic textile designs, collaborations with contemporary designers". Named partners: The National Gallery, Victoria & Albert Museum, Royal Horticultural Society, Museum of London, National Galleries of Scotland, New York Botanical Garden. Its V&A range covers "hand-painted chinoiseries, botanical studies, fashion photography, and William Morris wallpapers", and "a percentage of each print purchased... directly supports the institution" — [Colourful Beautiful Things](https://www.colourfulbeautifulthings.co.uk/surface-view-create-your-own-bespoke-wall-coverings/), [Seen PR](http://www.seenpr.com/blog-content/2020/12/4/surface-view-collaborates-with-the-vampa-to-offer-fine-art-for-the-modern-home)
- **Fy!** sells public-domain style as a *collection* rather than as attributed reproduction: "William Morris Style", "Japanese Art", "Art Nouveau / Klimt" — note "Style" and the slash construction, which is styling-after rather than reproducing — [iamfy.co](https://iamfy.co/)
- **Desenio** sells `/canvas-prints/vintage-motifs/` described as "various versions of popular school classroom motifs, photographs, hand-drawn sketches" — classic public-domain-adjacent vintage material — [Desenio vintage motifs](https://desenio.com/canvas-prints/vintage-motifs/)

### Inferences
- The generation-matchable share of this market is Tier 1 plus the "styled-after" part of Tier 3 (Fy!'s construction). Tier 2 and institution-licensed Tier 3 are not matchable, because the licence or the named artist is the product.
- Fy!'s "William Morris Style" / "Art Nouveau / Klimt" naming is the template to copy for generated public-domain-adjacent work: it captures the search demand for a famous name without claiming to reproduce a specific work.
- Bimago's 21-painter list is effectively a ready-made public-domain prompt brief, since every name on it is out of copyright.

### Gaps
- Pricing of the public-domain ranges specifically (King & McGaw, Surface View, Bimago Reproductions) was not recovered — all three sites block or 403. The brief asked how they "describe and price" these ranges; the description is evidenced above, the pricing is not.

---

## Q8. Bestsellers / most-popular pages and what is on them

### Takeaway
Nine of the harvested retailers publish a bestseller or most-popular page, and I was able to capture actual item titles with prices for only one of them — Wallfillers, where 48 titles and prices were harvested. The curated retailers' bestseller collection URLs could not be reached.

### Cited Findings

**Bestseller pages that exist (node name, verbatim):**
| Retailer | Named node |
|---|---|
| Desenio | "Top list" at `/posters-prints/top-list/`, page titled "Bestsellers scandinavian art" — [source](https://desenio.com/posters-prints/top-list/) |
| Poster Store | "Bestseller Posters - Buy our Top selling Art Prints" at `/posters-prints/bestseller-art-prints/` — [source](https://posterstore.com/posters-prints/bestseller-art-prints/) |
| The Poster Club | "Most Popular" (art prints), "Most Popular Canvas Art", "Most Popular Wall Objects", "Curator's Picks" — [source](https://www.theposterclub.com/) |
| Fy! | "Bestsellers", "Best Sellers" (repeated under Style/Room/Trends), "Trending Now", "Editors' Picks", "New this week" — [source](https://iamfy.co/) |
| Abstract House | "Bestsellers", "Bestselling Art" — [source](https://abstracthouse.com/) |
| Photowall | "Top Sellers" — [source](https://www.photowall.co.uk/posters) |
| Paper Collective | "Bestsellers" — [source](https://www.papercollective.com/) |
| King & McGaw | "In Demand Art Prints" at `/collections/in-demand` — [source](https://www.kingandmcgaw.com/collections/in-demand) |
| Wallfillers | "Best Sellers" section in the eBay store — [source](https://www.ebay.co.uk/str/wallfillerscanvas) |
| Bimago | No bestseller node; uses "Trends" and "New arrivals" instead — [source](https://www.bimago.co.uk/) |

**Wallfillers — 48 live item titles with GBP prices, verbatim, in store order** — [wallfillers canvas](https://www.ebay.co.uk/str/wallfillerscanvas). Seller stats on the page: 98.2% positive feedback, 51K items sold, 812 followers.

At £54.39: Extra Large Green Trees Canvas Wall Art Pictures 130cm Prints Set 4042 · Large Brown Living Room Landscape Canvas Wall Art 130cm Pictures 4088 · Large Plum White Floral Orchids Canvas Wall Art Prints Pictures 4116 · Large Purple Canvas Wall Art Pictures Set 130cm Wide XL Prints 4002 · Large Black White Canvas Wall Art Pictures 130cm Wide Prints XL 4003 · Paris Eiffel Tower Brown Canvas Pictures Set 130cm Wide Sepia XL 4013 · Large Black White Grey Canvas Art Pictures 130cm Wide Prints XL 4019 · Lime Green Flower Floral Canvas Wall Art Pictures 130cm Prints XL 4070 · Large Plum Living Room Landscape Canvas Wall Art 130cm Pictures 4087 · Large Purple Black Grey Abstract Canvas Pictures 160cm Wall Art 4092 · Large Blue Canvas Wall Art Pictures Yachts Boats Sea XL 130cm Set 4105 · Large Teal Turquoise Floral Canvas Wall Art Pictures XL Prints 4109 · Large Teal White Gerbera Daisy Canvas Wall Art Pictures Prints XL 4114 · Large Floral Black White Orchids Canvas Wall Pictures Prints Art 4128 · Large Abstract Lime Green Canvas Wall Art Pictures Set Prints XL 4143 · Large Sunset Beach Living Room Canvas Wall Art Pictures Prints XL 4152 · 3 Part Brown Sepia Canvas Pictures Wall Art Living Room Prints 3076 · Three Purple Canvas Pictures Landscapes Wall Art Prints Bedroom 3086 · Brown Extra large Canvas Picture of Sunset Beach Landscape 1131 · Brown Cheap Canvas Picture of Floral Lillies - 120cm x 50cm - 1055 · Extra Large Black White Lily Floral Canvas 130cm Wide Prints Art 4051 · Sikh Canvas Art of Golden Temple Amritsar for Living Room - 4 Panel - Blue · Beach Canvas Prints of Sunset for your Bedroom - Set of 4 - Purple Landscape · Wide Canvas Wall Art of a Lake Sunset for your Living Room · Plum Cheap Canvas Wall Art of Seascape Sunset - 120cm x 50cm - 1004 · Canvas Prints of Banksy Balloon Girl in Orange for your Bedroom · Large Blue Beach Sea Sunset Canvas Wall Art Pictures XL Set Boats 4107 · Set of 3 Plum Purple Wall Art Canvas Pictures Paris France Prints 3015 · Canvas Art of Abstract in Teal for your Living Room · Black and White New York Skyline - Modern Canvas 120cm Wide - 1269 · Black and White Venice Grand Canal Italy - Canvas Split 3 Panel 125cm Wide · Brown Ocean Sunrise - Modern Seascape Canvas Wall Art - 120cm Wide Prints · Large Black White Map of World Atlas Canvas Wall Art Print - Split 3 Set - 3315 · Large Map of the World Canvas Art Print - Colourful Cream - 120cm Wide - 1314

At £69.00 (five-panel sets): Set of 5 Pictures Black Red Canvas Wall Art Prints Koi Carp Fish 5094 · 5 Part Red Canvas Pictures Wall Art Dining Bed Room Flowers Lily 5052 · Set of 5 Panel Black White Canvas Wall Art Pictures Large Prints 5003 · Set of 5 Sepia Brown Canvas Wall Art Pictures Living Room Prints 5061 · Set Five Cheap Large Lime Green Canvas Art Wall Pictures Prints 5138 · 5 Piece Orange Canvas Art Pictures Africa Elephants Wall Prints 5102 · Set of Five Purple Plum Canvases Art Prints Large Wall Pictures 5021 · London Eye Canvas Prints UK Night for your Living Room - Set of Five · Extra Large Pink Forest Trees Canvas Art Five Piece in Black and White · Summertime Floral Canvas Pictures for your Living Room - 5 Piece · Extra Large Orange and White Swirl - Abstract Canvas Multi 5 Part · Set of Five Piece Abstract Purple Canvas Wall Art Picture Prints 5058

At £49.00: Brown Cheap Canvas of Jetty Landscape - 120cm x 50cm - 1045
At £42.99: Extra Large Red Swirl - Abstract Canvas Modern - 79cm Square - 1s265l

**Poster Store** individual bestseller items confirmed by URL: "Lemon Tree Poster" sits under `/posters-prints/bestseller-art-prints/lemon-tree-poster/`, and the citrus family includes Abstract Lemon Tree Poster · Lemon Tree Poster · Amalfi Coast Lemons Poster · Lemon Delivery Poster · Lemons on Table Poster · Stripes and Lemons Poster · Lemon Tea Poster. Poster Store also runs a whole `/posters-prints/citrus-posters/` category — [Lemon Tree Poster](https://posterstore.co.uk/p/posters-prints/bestseller-art-prints/lemon-tree-poster/), [Citrus posters](https://posterstore.com/posters-prints/citrus-posters/)

### Inferences
- The Wallfillers title corpus is the clearest signal in this harvest of how the UK eBay canvas buyer searches: a title is `[size/panel-count] + [colour] + [motif] + [room] + "Canvas Wall Art Pictures Prints"` + stock number. Colour and room are in the title, not just the category. Every one of the 48 items is an anonymous commodity image — this is the part of the market matchable by generation.
- Wallfillers' price ladder is flat by panel count, not by motif: 1-4 panel/130cm = £54.39, 5-panel = £69.00, with £49.00 and £42.99 outliers on smaller single pieces.
- The recurrence of Plum, Teal, Purple and Lime Green across the Wallfillers list, against their near-total absence from the Scandinavian retailers' palettes, is the sharpest taxonomy divergence found.

### Gaps
- Actual item titles from the Desenio, Poster Store, The Poster Club, Fy!, Abstract House, Photowall, Paper Collective and King & McGaw bestseller pages. Desenio/Poster Store/King & McGaw are blocked; for The Poster Club, Fy! and Abstract House (all fetchable) I guessed the collection slugs and got 404s on six attempts, so the correct slugs need to be read off the live nav first.

---

## Q9. Price ladders in GBP

### Takeaway
Only three GBP price points were recovered with sources, and no retailer's full size-to-price matrix was harvested; this is the weakest-evidenced part of the harvest.

### Cited Findings
- **Desenio (GBP)**: 30x40 cm and 50x70 cm prints both "starting from £6.95", with observed price points of £6.95, £12.95, £14.45, £18.95 and £21.45 across designs. Frames: 30x40 cm at £22, 50x70 cm at £39. Note that Desenio prices by *design*, not by size — the same ladder of price points appears at both sizes. — [Desenio 30x40](https://desenio.co.uk/posters-prints/sizes/posters-30x40cm/), [Desenio 50x70](https://desenio.co.uk/posters-prints/sizes/50x70cm/), [Desenio frames](https://desenio.co.uk/frames/sizes-frames/50x70-frames/) — *recovered from search-result metadata, not from the live pages, because the site blocks access; treat as indicative.*
- **Photowall (GBP)**: posters "From £18–£21 GBP" — [photowall.co.uk](https://www.photowall.co.uk/posters)
- **Wallfillers (GBP)**: £42.99 / £49.00 / £54.39 / £69.00, keyed to panel count and overall width as set out in Q8 — [wallfillers canvas](https://www.ebay.co.uk/str/wallfillerscanvas)
- **Olive et Oriel**: prices in **AUD $ only**; no GBP storefront — [oliveetoriel.com](https://www.oliveetoriel.com/)

### Inferences
- The UK ladder spans an order of magnitude on the same wall: Desenio from £6.95, Photowall £18-21, Wallfillers £42.99-69.00 for multi-panel canvas sets. Canvas and multi-panel formats carry roughly 5-8x the unit price of an unframed poster, which is where the margin is.

### Gaps
- No GBP prices recovered for Poster Store, Posterlounge, Juniqe, The Poster Club, Paper Collective, Fy!, Abstract House, King & McGaw, Surface View, Bimago or Pictowall. Three of those (Fy!, Abstract House, The Poster Club) are fetchable and a product-page fetch would yield their ladders immediately; the rest are blocked.
- Per-format and per-frame price ladders were not recovered for any retailer.

---

## Q10. UK market presence and shipping

### Takeaway
Thirteen of the seventeen retailers have a UK storefront or GBP pricing; Olive et Oriel is AUD-only, and two of the named retailers no longer exist in the form the brief assumes.

### Cited Findings
- **Dedicated .co.uk storefront**: desenio.co.uk, posterstore.co.uk, posterlounge.co.uk, photowall.co.uk, bimago.co.uk, surfaceview.co.uk, pictowall.co.uk — all confirmed as live hostnames during this harvest (several returned bot-protection codes rather than 404s, which confirms the host exists).
- **UK-based, .com domain**: iamfy.co (Fy!), abstracthouse.com, kingandmcgaw.com (GBP) — [iamfy.co](https://iamfy.co/), [abstracthouse.com](https://abstracthouse.com/), [King & McGaw](https://www.kingandmcgaw.com/collections)
- **UK path on an international domain**: juniqe.co.uk 301-redirects to juniqe.com/uk — [Juniqe UK](https://www.juniqe.com/uk/wall-art?page=1)
- **Danish, ships UK, English-language storefront**: theposterclub.com, papercollective.com — [theposterclub.com](https://www.theposterclub.com/), [papercollective.com](https://www.papercollective.com/)
- **UK eBay**: ebay.co.uk/str/wallfillerscanvas — note the older `ebay.co.uk/str/wallfillers` URL now returns HTTP 410 Gone, so `wallfillerscanvas` is the current store — [wallfillers canvas](https://www.ebay.co.uk/str/wallfillerscanvas)
- **Australian, AUD only, no GBP storefront**: oliveetoriel.com — [oliveetoriel.com](https://www.oliveetoriel.com/)
- **No longer a UK wall-art retailer**: artrepublic.com (redirects to artfinder.com); scandinaviandesigncenter.com (redirects to nordicnest.com)
- **King & McGaw** also has a UK trade/wholesale arm at trade.kingandmcgaw.com describing itself as "Art Print Publisher, Printer, Framer and Wholesaler", and is stocked by Heal's — [King & McGaw trade](https://trade.kingandmcgaw.com/), [Heal's](https://www.heals.com/collections/king-and-mcgaw)

### Inferences
- Desenio and Poster Store both run multi-TLD estates (.co.uk / .com / .eu / .ca / .com.au) with the *same* category path structure across them, which means a taxonomy harvested from any one TLD transfers to the UK one.

### Gaps
- Pictowall's UK status could not be verified beyond the hostname resolving; the origin returned HTTP 522 throughout.
- Trustpilot and review-aggregator evidence on which ranges draw praise or complaints was not gathered — I spent the available budget on taxonomy coverage, which the brief ranked higher.

---

## Cross-cutting note for the report writer

Two things in this harvest bear directly on the near-duplication risk recorded in the project's CLAUDE.md:

- **Photowall's item counts are the only hard distribution data recovered** (20,366 motifs across named buckets). They show the market is heavily concentrated: Nature + Art & Design = ~90% of motifs; Landscape orientation = 59% of items; Illustrated outnumbers Photographic roughly 2:1. A generated catalogue mirroring this distribution would itself be concentrated, which is exactly the condition that produces near-duplication.
- **The matchable commodity segment is well-bounded**: Photowall, Bimago (non-reproduction ranges), Desenio, Poster Store and Wallfillers carry no artist attribution and merchandise purely on motif/colour/room/style. Those five define the generation target. The Poster Club, Paper Collective, Fy! (partly), Olive et Oriel, Abstract House, King & McGaw and Surface View all sell attribution or licence as the product and are not matchable.

A methodological caveat the writer should carry forward: **the three largest and most directly relevant retailers (Desenio, Poster Store, Posterlounge) all blocked this harvest.** Everything attributed to them in these notes comes from live URL paths and marketing copy surfaced in search results, not from their menus. Their complete four-axis trees — the brief's headline request — remain unharvested, and the named Wayback snapshots are the route to them.
