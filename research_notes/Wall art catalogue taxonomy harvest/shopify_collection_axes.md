# Wall-art catalogue taxonomy harvest: Shopify `/collections.json` enumeration

Harvested 2026-10-07 via the public Shopify endpoint `https://<host>/collections.json?limit=250&page=N`,
paginated upward until a page returned an empty `collections` array. No User-Agent was spoofed and no bot
protection was bypassed; three hosts returned HTTP 429 (plain rate limiting) on first pass and were re-read
with exponential backoff until they returned 200.

## Harvest log: pages read and whether exhaustion was reached

| Host | Pages read | Last page size | Reached end? | Unique collections | Notes |
|---|---|---|---|---|---|
| `iamfy.co` (Fy!) | 8 (1-7 data, 8 empty) | 248 | Yes - page 8 returned `collections: []` | **1748** | Clean 200s throughout |
| `abstracthouse.com` | 2 (1 data, 2 empty) | 86 | Yes | **86** | HTTP 429 on first attempt; 200 after backoff |
| `theposterclub.com` | 2 (1 data, 2 empty) | 111 | Yes | **111** | HTTP 429 on first attempt; 200 after backoff |
| `oliveetoriel.com` | 4 (1-3 data, 4 empty) | 154 | Yes | **654** | Clean 200s |
| `society6.com` | 19 (1-18 data, 19 empty) | 69 | Yes | **4319** | 429 at page 5; resumed after backoff. Endpoint works - confirms Shopify migration |

No host was blocked outright: all five returned complete data. Total raw: **6918** collection records,
6918 unique handles (no intra-host handle duplication).

---

## 0. Junk to exclude (Fy! machine-generated noise)

Patterns to filter, with observed counts on `iamfy.co`:

- `^art-lander-ad-[0-9]+-[0-9]+$` - Paid-ad landing pages, two epoch-ms ids
- `^art-lander-grid-[0-9]+$` - Ad grid variants
- `^wall-art-meta-lp-[0-9]+$` - Meta/Facebook landing pages
- `^all-art-meta-lp-[0-9]+$` - Meta landing pages, second series
- `-relevant$` - Shadow twin of every meta-lp / post-it / text-animation page
- `^vibe-[0-9a-f]{8}-[0-9a-f]{4}-` - Single UUID-named vibe collection
- `b2b|test` - B2B partner shops and test shops

Observed counts (de-overlapped, in the order above):

- `art-lander-ad`: **24**
- `art-lander-grid`: **10**
- `art-lander (bare)`: **1**
- `wall-art-meta-lp`: **18**
- `all-art-meta-lp`: **4**
- `-relevant`: **37**
- `vibe-<uuid>`: **1**
- `b2b / test`: **6**

Total Fy! junk handles excluded: **101** of 1748, leaving **1647** real collections.

Also non-taxonomic but *real* (excluded from axis counts, kept as context): B2B/partner white-label shops
(`leucadia-pizzeria`, `prezzo-art-collection`, `prime-47-art-selection`, `letter-four-california-coastal`,
`honeydew-house`, `mozata`, `aces-collection`, `idris`, `b2b_torro_locco`, `b2b_the_family_institute`),
ad-copy landing pages (`wall-art-post-it-*`, `wall-art-text-animation-*`, `wall-art-blank-walls-transformed`,
`wall-art-finally-found-my-style`, `wall-art-living-room-under-500`, `wall-art-looks-like-nobody-elses`,
`wall-art-the-art-effect`, `wall-art-ties-every-room-together`, `wall-art-whatever-your-style`,
`wall-art-whatever-your-vibe`, `wall-art-bathroom-walls-with-joy`, `wall-art-hallways-that-welcome-you-home`,
`wall-art-kitchen-upgrade-no-renovation`, `wall-art-post-it-discovery`), and internal persona test rigs
(`persona-emma`, `persona-ferne`, `persona-julie`, `persona-sabrina`, `persona-stacey`,
`persona-art-for-stacey`, `persona-julie-art-collection`, `art-for-ferne`, `art-for-idris`,
`art-for-julie`, `art-for-sabrina`).

### CRITICAL CAVEAT: `-copy` handles are NOT junk

I initially filtered `-copy` as noise and that is **wrong**. On Fy! the `-copy` handles are live,
correctly-titled collections whose *handle* is a stale leftover from duplication. Handle and content do not
match. The entire `N-print-{room}-gallery-wall-sets` family is only reachable through these handles:

| Handle (misleading) | Actual title | products_count |
|---|---|---|
| `2-print-bathroom-gallery-wall-sets-copy` | 2-Print Children's Room Gallery Wall Sets | 24 |
| `2-print-bedroom-gallery-wall-sets-copy` | 2-Print Bathroom Gallery Wall Sets | 30 |
| `2-print-bedroom-room-gallery-wall-sets-copy` | 2-Print Hallway Gallery Wall Sets | 57 |
| `2-print-childrens-room-gallery-wall-sets-copy` | 2-Print Home Office Gallery Wall Sets | 80 |
| `2-print-gallery-wall-sets-copy` | 2-Print Living Room Gallery Wall Sets | 206 |
| `2-print-hallway-room-gallery-wall-sets-copy` | 2-Print Kitchen Gallery Wall Sets | 32 |
| `2-print-living-room-gallery-wall-sets-copy` | 3-Print Living Room Gallery Wall Sets | 201 |
| `2-print-living-room-gallery-wall-sets-copy-1` | 2-Print Bedroom Gallery Wall Sets | 142 |
| `3-print-bathroom-gallery-wall-sets-copy` | 3-Print Children's Room Gallery Wall Sets | 22 |
| `3-print-bedroom-gallery-wall-sets-copy` | 3-Print Bathroom Gallery Wall Sets | 22 |
| `3-print-bedroom-room-gallery-wall-sets-copy` | 3-Print Hallway Gallery Wall Sets | 39 |
| `3-print-childrens-room-gallery-wall-sets-copy` | 3-Print Home Office Gallery Wall Sets | 78 |
| `3-print-hallway-room-gallery-wall-sets-copy` | 3-Print Kitchen Gallery Wall Sets | 25 |
| `3-print-living-room-gallery-wall-sets-copy` | 3-Print Bedroom Gallery Wall Sets | 117 |
| `dining-room-gallery-wall-sets-copy` | Hallway Gallery Wall Sets | 102 |
| `kitchen-gallery-wall-sets-copy` | Living Room Gallery Wall Sets | 418 |
| `kitchen-gallery-wall-sets-copy-1` | Dining Room Gallery Wall Sets | 169 |

Only `upgrade-your-space-test-copy` / `upgrade-your-space-today-copy` are genuine test junk.
**Implication: any scrape of this taxonomy must key on `title`, not `handle`.**

---

## 1. The Fy! generative grammar

Fy! handles decompose as:

```
{base}-art-prints                      <- 613 observed
{base}-{medium}-art-prints             <- medium in {drawing, illustration, photography, typography, watercolor}
{base}[-{medium}]-canvas-art           <-  88 observed (canvas is a FORMAT suffix applied on top)
art-for-the-{persona}                   <- persona axis, flat, no medium
{N}-print-{room}-gallery-wall-sets      <- set-size x room
{room}-{position}-art-prints            <- room x wall-position
```

Distinct `{base}` tokens: **671**. Medium occurrences: `drawing` 107, `illustration` 158, `photography` 181, `typography` 55, `watercolor` 123, plain (no medium) 613, `canvas-art` 88.

Note `canvas-art` is a *second-order* suffix: handles such as `bold-photography-canvas-art`,
`national-parks-watercolor-canvas-art`, `cottage-core-drawing-canvas-art` apply canvas to an
already-medium-qualified base. So FORMAT x MEDIUM x BASE is a genuine three-way cross, but very sparse.

---

## 2. Axis inventories (every distinct value, deduplicated, alphabetised)

### SUBJECT - Fy! (cardinality **137**)

`album-cover`, `animals`, `animals-photography`, `aperol-spritz`, `architecture`, `art-history`
`astrology`, `astronomy`, `band-posters`, `beach`, `beliefs`, `birds`
`black-cat`, `books`, `botanical`, `butterfly`, `cactus`, `cars`
`cats`, `causes`, `celebrities`, `characters`, `chef`, `cherry-blossom`
`cities`, `cities-drawing`, `cities-illustration`, `cityscapes`, `cloud`, `cocktails`
`comics`, `concepts`, `cooking`, `cultural`, `culture`, `cycling`
`dinosaurs`, `dogs`, `education`, `educational`, `elephant`, `emotions`
`family`, `fantasy`, `fashion`, `fashion-illustration`, `fashion-photography`, `feminine`
`feminism`, `feminist`, `film`, `fish`, `floral`, `flowers`
`flowers-drawing`, `flowers-watercolor`, `food-and-drinks`, `football`, `frog`, `gaming`
`gardens`, `girl-visual`, `golf`, `health-and-wellness`, `hearts`, `herbs`
`historical`, `history`, `hobbies`, `home-decor`, `horror`, `insects`
`interests`, `interior-design`, `interiors`, `landscapes`, `landscapes-photography`, `language`
`lego`, `lemon`, `liberty`, `lifestyle`, `love`, `maps`
`mermaid`, `moon`, `mountains`, `music`, `music-photography`, `mythology`
`national-parks`, `national-parks-watercolor`, `natural`, `nature`, `ocean-and-marine`, `octopus`
`palm-tree`, `pasta`, `patriotic`, `people`, `people-photography`, `pets`
`philosophy`, `philosophy-drawing`, `pizza`, `places`, `plants`, `quotes`
`relationships`, `religion`, `sci-fi`, `science`, `science-fiction`, `shapes`
`ski`, `social`, `socialjustice`, `song-lyrics`, `space`, `spiritual`
`spirituality`, `sport`, `swimming`, `symbols`, `technology`, `tiger`
`transport`, `transportation`, `travel`, `travel-illustration`, `trees-and-forests`, `vehicles`
`war`, `wellness`, `wild-animals`, `wine`, `yoga`

### MOOD / FEELING - Fy! (cardinality **151**)

`abundant`, `adventurous`, `amused`, `amusing`, `appetizing`, `awe`
`awe-inspiring`, `balanced`, `bold`, `bold-photography`, `bold-typography`, `bright`
`calming`, `calming-photography`, `celebratory`, `cheerful`, `clear`, `clever`
`comforting`, `confident`, `contemplative`, `cool`, `cozy`, `creative`
`curious`, `cute`, `dark`, `delicate`, `dignified`, `dramatic`
`dramatic-drawing`, `dramatic-photography`, `dreamlike`, `dreamy`, `dynamic`, `edgy`
`eerie`, `emotional`, `empowering`, `enchanting`, `encouragement`, `endearing`
`energetic`, `energising`, `energising-photography`, `energizing`, `evocative`, `exciting`
`exotic`, `expansive`, `festive`, `focused`, `free-spirited`, `fresh`
`fun`, `funky`, `funny`, `funny-bathroom`, `gentle`, `gentle-drawing`
`graceful`, `harmonious`, `hopeful`, `humor`, `humorous`, `humorous-typography`
`iconic`, `imaginative`, `inspirational`, `inspirational-quotes`, `inspirational-quotes-photography`, `intense`
`intricate`, `intriguing`, `introspective`, `invigorating`, `joyful`, `light`
`lighthearted`, `lively`, `loving`, `lush`, `luxurious`, `luxury`
`magical`, `majestic`, `majestic-drawing`, `meditative`, `melancholy`, `mindfulness`
`moody`, `mysterious`, `mystical`, `neutral-drawing`, `neutral-illustration`, `night`
`nostalgic`, `passionate`, `pastel-watercolor`, `peaceful`, `peaceful-drawing`, `pensive`
`playful`, `positive`, `powerful`, `proud`, `quiet`, `quirky`
`rebellious`, `reflective`, `refreshing`, `relatable`, `relatable-typography`, `relaxed`
`relaxing`, `restful`, `reverent`, `rich`, `romantic`, `romantic-photography`
`sarcastic`, `sensual`, `sentimental`, `serene`, `soft`, `solitary`
`sophisticated`, `spooky`, `striking`, `strong`, `stylish`, `subtle`
`sun`, `sweet`, `thought-provoking`, `thoughtful`, `thoughtful-drawing`, `thoughtful-illustration`
`thoughtful-typography`, `unique`, `uplifting`, `urban`, `vast`, `vibrant`
`vibrant-drawing`, `wanderlust`, `warm`, `warm-illustration`, `welcoming`, `witty`
`wonder`

### STYLE / MOVEMENT / GENRE - Fy! (cardinality **98**)

`80s`, `abstract`, `academic`, `african-art`, `art-deco`, `art-nouveau`
`art-nouveau-illustration`, `art-styles`, `asian`, `asian-inspired`, `baroque`, `bauhaus`
`bohemian`, `boho`, `cartoon`, `chic`, `classic-art`, `classical`
`coastal`, `contemporary`, `cottage-core`, `cottage-core-drawing`, `dark-academia`, `decorative`
`distressed`, `documentary`, `eclectic`, `eclectic-photography`, `elegant`, `expressionism`
`farmhouse`, `farmhouse-drawing`, `figurative`, `figurative-and-nude`, `folk-art`, `french`
`french-country`, `futurism`, `futuristic`, `geometric`, `glam`, `glamorous`
`gothic`, `grandmillennial`, `industrial`, `japandi`, `japanese`, `maximalist`
`maximalist-drawing`, `maximalist-photography`, `mediterranean`, `mediterranean-photography`, `mid-century`, `mid-century-modern`
`minimal`, `minimalist`, `modern`, `modern-art`, `nostalgia`, `opulent`
`orderly`, `organic`, `patterns`, `pop`, `pop-art`, `pop-culture`
`pop-culture-photography`, `portraits`, `raw`, `refined`, `retro`, `retro-culture`
`retro-photography`, `rustic`, `scandinavian`, `scandinavian-illustration`, `scandinavian-watercolor`, `shabby-chic`
`simple`, `southwestern`, `still-life`, `street-art`, `street-art-photography`, `structured`
`surrealism`, `surrealism-photography`, `textural`, `texture`, `traditional`, `tropical`
`victorian`, `vintage`, `vintage-posters`, `western`, `western-photography`, `whimsical`
`whimsical-illustration`, `zen`

### MEDIUM / TECHNIQUE - Fy! (cardinality **16**)

`decor`, `digital-art`, `digital-painting`, `drawing`, `graphic-design`, `illustration`
`illustration-illustration`, `ink`, `line-art`, `linocut`, `mixed-media`, `painting`
`pencil`, `photography`, `typography`, `watercolor`

### ROOM - Fy! (cardinality **15**; of which **11** are crossed with wall position)

`bar-area`, `bar-area-wall-decor`, `bathroom`, `bedroom`, `childrens-room`, `dining-room`
`hallway`, `home-interior`, `home-office`, `kids-room`, `kitchen`, `laundry-room`
`living-room`, `nursery`, `playroom`

### ROOM x WALL POSITION - Fy! (**107** crossed handles; see the matrix in section 2 for the breakdown)

`bathroom-above-bathtub`, `bathroom-above-bed`, `bathroom-above-sofa`, `bathroom-above-toilet`, `bathroom-above-tub`, `bathroom-accent-wall`
`bathroom-corner`, `bathroom-entryway`, `bathroom-feature-wall`, `bathroom-gallery-wall`, `bathroom-play-area`, `bathroom-shelf`
`bathroom-vanity`, `bedroom-above-bed`, `bedroom-above-desk`, `bedroom-above-sofa`, `bedroom-accent-wall`, `bedroom-bedside`
`bedroom-corner`, `bedroom-dresser`, `bedroom-dressing-area`, `bedroom-feature-wall`, `bedroom-gallery-wall`, `bedroom-nightstand`
`bedroom-reading-nook`, `bedroom-side-table`, `bedroom-vanity`, `childrens-room-above-bed`, `childrens-room-above-cot`, `childrens-room-above-crib`
`childrens-room-above-desk`, `childrens-room-above-toilet`, `childrens-room-behind-desk`, `childrens-room-corner`, `childrens-room-feature-wall`, `childrens-room-gallery-wall`
`childrens-room-play-area`, `childrens-room-reading-nook`, `childrens-room-shelf`, `dining-room-above-table`, `dining-room-accent-wall`, `dining-room-bar-cart`
`dining-room-dining-area`, `dining-room-feature-wall`, `dining-room-gallery-wall`, `hallway-accent-wall`, `hallway-entryway`, `hallway-feature-wall`
`hallway-gallery-wall`, `hallway-statement-wall`, `home-office-above-bed`, `home-office-above-desk`, `home-office-above-sofa`, `home-office-accent-wall`
`home-office-behind-desk`, `home-office-corner`, `home-office-feature-wall`, `home-office-gallery-wall`, `home-office-hallway`, `home-office-reading-nook`
`home-office-shelf`, `kids-room-above-bed`, `kids-room-above-desk`, `kids-room-feature-wall`, `kids-room-gallery-wall`, `kids-room-play-area`
`kitchen-above-counter`, `kitchen-above-desk`, `kitchen-above-table`, `kitchen-accent-wall`, `kitchen-bar-area`, `kitchen-bar-cart`
`kitchen-behind-desk`, `kitchen-breakfast-nook`, `kitchen-dining-area`, `kitchen-disco`, `kitchen-entryway`, `kitchen-feature-wall`
`kitchen-gallery-wall`, `kitchen-play-area`, `kitchen-reading-nook`, `kitchen-shelf`, `living-room-above-bed`, `living-room-above-fireplace`
`living-room-above-sofa`, `living-room-accent-wall`, `living-room-bar-area`, `living-room-bar-cart`, `living-room-behind-desk`, `living-room-coffee-table`
`living-room-console-table`, `living-room-corner`, `living-room-dining-area`, `living-room-entryway`, `living-room-feature-wall`, `living-room-gallery-wall`
`living-room-mantel`, `living-room-reading-nook`, `living-room-shelf`, `living-room-side-table`, `living-room-statement-wall`, `nursery-above-cot`
`nursery-above-crib`, `nursery-feature-wall`, `nursery-gallery-wall`, `nursery-play-area`, `playroom-feature-wall`

### ROOM x generic suffix - Fy! (cardinality **13**)

`bathroom-wall-decor`, `bedroom-wall-art`, `bedroom-wall-decor`, `childrens-room-wall-decor`, `dining-room-wall-decor`, `hallway-wall-decor`
`home-office-wall-decor`, `kids-room-wall-decor`, `kitchen-wall-decor`, `living-room-wall-art`, `living-room-wall-decor`, `nursery-wall-decor`
`playroom-wall-decor`

### COLOUR - Fy! (cardinality **35**)

`accent-color`, `black-and-white`, `blue`, `blush-pink`, `colorful`, `colors`
`contrasting`, `earth-toned`, `earthy`, `earthy-illustration`, `gold`, `gradient`
`green`, `grey`, `high-contrast`, `iridescent`, `jewel-tones`, `metallic`
`monochrome`, `multi-colored`, `muted`, `neon`, `neutral`, `orange`
`pastel`, `pink`, `purple`, `rainbow`, `red`, `sage-green`
`teal`, `terracotta`, `vibrant-accent`, `warm-accents`, `yellow`

### OCCASION - Fy! (cardinality **35**)

`anniversary`, `any-celebration`, `any-occasion`, `autumndecor`, `baby-shower`, `birthday`
`birthdays`, `celebrations`, `christmas`, `easter`, `fathers-day`, `get-well-soon`
`graduation`, `halloween`, `holiday-gift`, `housewarming`, `international-womens-day`, `mothers-day`
`new-baby`, `new-home`, `new-job`, `new-parents`, `new-pet`, `office-warming`
`pride-month`, `retirement`, `seasons`, `summer-party`, `sympathy`, `thanksgiving`
`travel-anniversary`, `valentines-day`, `vintage-christmas`, `wedding`, `winter-holidays`

### RECIPIENT / GIFT TARGET - Fy! (cardinality **10**)

`fan-gift`, `for-him`, `for-kids`, `host-gift`, `kids`, `kids-room-decor`
`personalized`, `travel-gift`, `travel-souvenir`, `women`

### FORMAT / SIZE - Fy! (cardinality **11**)

`framed`, `free`, `landscape`, `large`, `medium`, `new-in`
`oversized`, `portrait`, `small`, `square`, `xl`

### ARTIST / NAMED IP - Fy! (cardinality **35**)

`alice-in-wonderland`, `alice-straker`, `andy-westface`, `arsenal`, `audrey-hepburn`, `audubon`
`cezanne`, `claude-monet`, `daft-punk`, `dolly-parton`, `fleetwood-mac`, `frida-kahlo`
`gauguin`, `gustav-klimt`, `hilma-af-klint`, `hiroshi-nagai`, `hokusai`, `kandinsky`
`kusama`, `mirropix`, `mucha`, `paul-klee`, `picasso`, `pissarro`
`pulp-fiction`, `queen`, `redoute`, `renoir`, `sandra-poliakov`, `sargent`
`studio-ghibli`, `toulouse-lautrec`, `vincent-van-gogh`, `wes-anderson`, `william-morris`

### PLACE / GEOGRAPHY - Fy! (cardinality **8**)

`amalfi-coast`, `australia`, `european`, `florence`, `italian`, `new-york`
`new-zealand`, `paris`
### RECIPIENT / PERSONA - Fy! `art-for-the-{persona}` (cardinality **160**)

`academic`, `activist`, `adventurer`, `anglophile`, `animal-activist`
`animal-lover`, `anime-fan`, `architect`, `art-collector`, `athlete`
`baker`, `beach-lover`, `believer`, `biologist`, `bird-watcher`
`bohemian-soul`, `bold-art-lover`, `botanist`, `calming-space-creator`, `calming-space-seeker`
`cat-parent`, `celebration-planner`, `chef`, `child-at-heart`, `clean-eater`
`coastal-decorator`, `coastal-dweller`, `coastal-enthusiast`, `cocktail-connoisseur`, `coffee-snob`
`comics-fan`, `confident-woman`, `connoisseur`, `contemplative-soul`, `contemporary-decorator`
`cottage-core-enthusiast`, `cowboy`, `cowgirlcowboy`, `cozy-home-lover`, `creative`
`culturally-curious`, `cultured`, `curious-mind`, `dark-aesthetic-lover`, `deep-thinker`
`designer`, `dog-lover`, `dog-parent`, `dreamer`, `eclectic-decorator`
`edgy-one`, `elegant-homeowner`, `energetic`, `entertainers`, `enthusiastic-decorator`
`entrepreneur`, `equestrian`, `explorer`, `expressive-individual`, `expressive-soul`
`family-oriented`, `farmer`, `fashionista`, `feminist`, `film-buff`
`foodie`, `foodies`, `free-spirit`, `gardener`, `gentle-soul`
`gifter`, `goth`, `health-enthusiast`, `hip-hop-fan`, `hipster`
`history-buff`, `home-cook`, `home-decorator`, `homebody`, `homemaker`
`hosthostess`, `humorist`, `humorous-friend`, `intellectual`, `interior-designer`
`introvert`, `joker`, `joyful-giver`, `joyful-homeowner`, `kids`
`kids-decorator`, `kids-party-planner`, `landscape-enthusiast`, `londoner`, `marine-biologist`
`meditator`, `mid-century-modern-enthusiast`, `mid-century-modern-lover`, `mindful-giver`, `minimalist`
`modern-enthusiast`, `music-lover`, `music-producer`, `nature-enthusiast`, `nature-lover`
`new-parent`, `optimist`, `patriot`, `personalized-gift-giver`, `philosopher`
`philosophy-enthusiast`, `photographer`, `plant-lover`, `playful-one`, `pop-culture-fan`
`princess`, `pub-enthusiast`, `quirky-art-lover`, `quirky-friend`, `quirky-one`
`rebel`, `relaxed-one`, `retro-fan`, `retro-lover`, `romantic`
`sarcastic-one`, `sci-fi-fan`, `science-enthusiast`, `scientist`, `sentimentalist`
`serene-seeker`, `shopper`, `sleep-lover`, `social-justice-advocate`, `social-justice-warrior`
`spiritual-seeker`, `sports-fan`, `stargazer`, `storyteller`, `student`
`swimmer`, `technophile`, `teenager`, `thoughtful-gift-giver`, `traditionalist`
`trendsetter`, `trendsetters`, `unique-seeker`, `urban-dweller`, `veteran`
`vibrant-soul`, `vintage-lover`, `wellness-seeker`, `whiskey-connoisseur`, `witty-friend`
`world-traveler`, `yogi`, `young-artist`, `young-chef`, `young-musician`

Plus non-`the` recipient collections (8): `art-for-couples`, `art-for-her`, `art-for-her-the-botanist`, `art-for-him`, `art-for-kids`, `art-for-kids-the-explorer`, `art-for-kids-the-nature-lover`, `art-for-kids-the-storyteller`

Note the persona axis carries **no medium cross at all** - there is no `art-for-the-botanist-watercolor`.
It is a flat list. It also contains obvious near-synonym duplicates that inflate the count:
`art-for-the-cowboy`/`art-for-the-cowgirlcowboy`, `art-for-the-dog-lover`/`art-for-the-dog-parent`,
`art-for-the-foodie`/`art-for-the-foodies`, `art-for-the-trendsetter`/`art-for-the-trendsetters`,
`art-for-the-retro-fan`/`art-for-the-retro-lover`, `art-for-the-calming-space-creator`/`-seeker`,
`art-for-the-social-justice-advocate`/`-warrior`, `art-for-the-expressive-individual`/`-soul`,
`art-for-the-mid-century-modern-enthusiast`/`-lover`, `art-for-the-quirky-art-lover`/`-friend`/`-one`,
`art-for-the-connoisseur`/`art-for-the-cultured`/`art-for-the-culturally-curious`.

### WALL POSITION WITHIN ROOM - Fy! (cardinality **36**)

`above-bathtub`, `above-bed`, `above-cot`, `above-counter`, `above-crib`
`above-desk`, `above-fireplace`, `above-sofa`, `above-table`, `above-toilet`
`above-tub`, `accent-wall`, `bar-area`, `bar-cart`, `bedside`
`behind-desk`, `breakfast-nook`, `coffee-table`, `console-table`, `corner`
`dining-area`, `disco`, `dresser`, `dressing-area`, `entryway`
`feature-wall`, `gallery-wall`, `hallway`, `mantel`, `nightstand`
`play-area`, `reading-nook`, `shelf`, `side-table`, `statement-wall`
`vanity`

Contaminants present in the same handle slot but which are NOT positions (medium/generic leakage):
`wall-decor`, `wall-art`, `decor`, and on `kids-room` only: `illustration`, `watercolor`,
`decor-illustration` (i.e. `kids-room-illustration-art-prints` parses as room+medium, not room+position).

#### The ROOM x WALL POSITION matrix, verbatim

| Room | n positions | Positions |
|---|---|---|
| `bathroom` | 13 | `above-bathtub`, `above-bed`, `above-sofa`, `above-toilet`, `above-tub`, `accent-wall`, `corner`, `entryway`, `feature-wall`, `gallery-wall`, `play-area`, `shelf`, `vanity` |
| `bedroom` | 14 | `above-bed`, `above-desk`, `above-sofa`, `accent-wall`, `bedside`, `corner`, `dresser`, `dressing-area`, `feature-wall`, `gallery-wall`, `nightstand`, `reading-nook`, `side-table`, `vanity` |
| `childrens-room` | 12 | `above-bed`, `above-cot`, `above-crib`, `above-desk`, `above-toilet`, `behind-desk`, `corner`, `feature-wall`, `gallery-wall`, `play-area`, `reading-nook`, `shelf` |
| `dining-room` | 6 | `above-table`, `accent-wall`, `bar-cart`, `dining-area`, `feature-wall`, `gallery-wall` |
| `hallway` | 5 | `accent-wall`, `entryway`, `feature-wall`, `gallery-wall`, `statement-wall` |
| `home-office` | 11 | `above-bed`, `above-desk`, `above-sofa`, `accent-wall`, `behind-desk`, `corner`, `feature-wall`, `gallery-wall`, `hallway`, `reading-nook`, `shelf` |
| `kids-room` | 5 | `above-bed`, `above-desk`, `feature-wall`, `gallery-wall`, `play-area` |
| `kitchen` | 16 | `above-counter`, `above-desk`, `above-table`, `accent-wall`, `bar-area`, `bar-cart`, `behind-desk`, `breakfast-nook`, `dining-area`, `disco`, `entryway`, `feature-wall`, `gallery-wall`, `play-area`, `reading-nook`, `shelf` |
| `living-room` | 19 | `above-bed`, `above-fireplace`, `above-sofa`, `accent-wall`, `bar-area`, `bar-cart`, `behind-desk`, `coffee-table`, `console-table`, `corner`, `dining-area`, `entryway`, `feature-wall`, `gallery-wall`, `mantel`, `reading-nook`, `shelf`, `side-table`, `statement-wall` |
| `nursery` | 5 | `above-cot`, `above-crib`, `feature-wall`, `gallery-wall`, `play-area` |
| `playroom` | 1 | `feature-wall` |

**Density: 107 filled cells of 11x36 = 396 possible = 27.0%.** This is the most commercially revealing axis: it is deliberately
sparse and the sparsity is *mostly* sensible (`bathroom-above-toilet` exists, `living-room-above-toilet` does not).

Nonsense cells that DO exist, i.e. generator bleed where the room/position pair is physically absurd:
- `bathroom-above-bed-art-prints`
- `bathroom-above-sofa-art-prints`
- `bathroom-play-area-art-prints`
- `bedroom-above-sofa-art-prints`
- `childrens-room-above-toilet-art-prints`
- `home-office-above-bed-art-prints`
- `home-office-hallway-art-prints`
- `kitchen-above-desk-art-prints`
- `kitchen-play-area-art-prints`
- `kitchen-disco-art-prints`
- `living-room-above-bed-art-prints`
- `home-office-above-sofa-art-prints`
- `kitchen-behind-desk-art-prints`

Near-duplicate position synonyms Fy! generates side by side (direct near-duplication risk):
- `bathroom-above-bathtub` vs `bathroom-above-tub`
- `bedroom-bedside` vs `bedroom-nightstand` vs `bedroom-side-table`
- `childrens-room-above-cot` vs `childrens-room-above-crib`; `nursery-above-cot` vs `nursery-above-crib`
- `accent-wall` vs `feature-wall` vs `statement-wall` (all three on `hallway` and `living-room`)
- whole-room duplication: `childrens-room-*` vs `kids-room-*` vs `nursery-*` vs `playroom-*`

### FORMAT: SET SIZE x ROOM - Fy! gallery wall sets

Set-size values observed: **`2-print`, `3-print`** (cardinality 2). No 4-print or larger exists.
Rooms crossed with set size (by title): `Bathroom`, `Bedroom`, `Children's Room`, `Hallway`,
`Home Office`, `Kitchen`, `Living Room` (7 rooms), plus an uncrossed `2-Print Gallery Wall Sets` /
`3-Print Gallery Wall Sets` parent. **Dining Room is absent from the N-print cross** although
`Dining Room Gallery Wall Sets` (no set size) exists - a real hole. Nursery and Playroom are also absent.
Density: 14 of 2x7 = 14 cells = **100% within the 7 rooms that are crossed at all.**

---
## 3. Which crosses actually exist vs which are absent

### BASE x MEDIUM density (Fy!)

| Mediums per base | n bases | Interpretation |
|---|---|---|
| 0 | 367 | plain only - never qualified by medium |
| 1 | 149 | one medium variant |
| 2 | 38 | two |
| 3 | 31 | three |
| 4 | 44 | four |
| 5 | 34 | five |
| 6 | 8 | all five + canvas |

**Density: 712 filled cells of 671 bases x 6 medium/format values = 4026 = 17.7%.**

#### Densely crossed: the bases that carry ALL SIX (five mediums + canvas)

`abstract`, `beliefs`, `bohemian`, `bold`
`cool`, `culture`, `neutral`, `scandinavian`

#### Bases carrying five mediums

`architecture`, `art-styles`, `awe-inspiring`, `botanical`
`calming`, `christmas`, `contemporary`, `cottage-core`
`earthy`, `empowering`, `energising`, `family`
`farmhouse`, `food-and-drinks`, `hobbies`, `humor`
`humorous`, `inspirational-quotes`, `joyful`, `kids`
`love`, `loving`, `maximalist`, `natural`
`nostalgic`, `pastel`, `peaceful`, `pets`
`portraits`, `thoughtful`, `uplifting`, `vibrant`
`warm`, `whimsical`

#### Per-medium totals - which medium is cheapest to generate

| Medium | n bases crossed | % of 671 bases |
|---|---|---|
| `drawing` | 107 | 15.9% |
| `illustration` | 158 | 23.5% |
| `photography` | 181 | 27.0% |
| `typography` | 55 | 8.2% |
| `watercolor` | 123 | 18.3% |
| `canvas` | 88 | 13.1% |

Ranking: photography (181) > illustration (158) > watercolor (123) > drawing (107) > canvas (88) >
typography (55). **Typography is the sparsest medium by a wide margin** and is applied almost exclusively
to text-bearing or mood bases (`witty`, `relatable`, `sentimental`, `lighthearted`, `language`,
`inspirational-quotes`, `quotes`, `thought-provoking`) and never to subject bases like `birds` or `dogs`.

### Axis-pair cross density summary (Fy!)

| Axis pair | Crossed? | Evidence |
|---|---|---|
| SUBJECT x MEDIUM | Dense | Most high-value subjects carry 4-5 mediums: `animals`, `birds`, `dogs`, `flowers`, `landscapes`, `places`, `people`, `travel`, `insects`, `dinosaurs`, `trees-and-forests`, `ocean-and-marine`, `wild-animals` |
| MOOD x MEDIUM | Dense | The single densest cross. ~120 mood bases carry 3-6 mediums each |
| STYLE x MEDIUM | Medium | `bohemian`, `scandinavian`, `cottage-core`, `farmhouse`, `contemporary`, `maximalist`, `japandi` carry 5-6; `baroque`, `bauhaus`, `victorian`, `expressionism`, `futurism`, `rustic`, `grandmillennial`, `art-nouveau` carry NONE |
| ROOM x MEDIUM | **Absent** | No `bedroom-watercolor-art-prints`. Only `kids-room` leaks (`kids-room-illustration`, `kids-room-watercolor`). Rooms cross with POSITION instead |
| ROOM x POSITION | Sparse by design | 124 of 462 = 26.8% |
| ROOM x SET SIZE | Dense within 7 rooms | 14/14 cells, but Dining Room / Nursery / Playroom excluded entirely |
| PERSONA x anything | **Absent** | 160 personas, zero medium/room/colour crosses. Completely flat |
| COLOUR x MEDIUM | **Near-absent** | Only `green-watercolor`, `rainbow-watercolor`/`-photography`, `monochrome-watercolor`, `muted-watercolor`, `multi-colored-watercolor`, `pastel-*` (6 mediums), `neutral-*` (6), `earthy-*` (6). Plain colours (`blue`, `pink`, `red`, `purple`, `teal`, `yellow`, `orange`, `grey`, `gold`, `terracotta`, `sage-green`, `blush-pink`, `black-and-white`) have NO medium variant |
| OCCASION x MEDIUM | **Watercolor only** | A striking one-medium rule: `anniversary`, `baby-shower`, `birthday`, `birthdays`, `fathers-day`, `graduation`, `housewarming`, `mothers-day`, `new-baby`, `new-home`, `new-parents`, `retirement`, `valentines-day`, `wedding` each have exactly `-watercolor-` and nothing else. `christmas` and `halloween` are the exceptions (4-5 mediums) |
| FORMAT/SIZE x MEDIUM | **Watercolor only** | `large-watercolor`, `medium-watercolor`, `small-watercolor` exist; no `large-photography`. `xl`, `oversized`, `square`, `framed` have none |
| ARTIST/IP x anything | **Absent** | All 35 artist/IP bases are plain only |
| PLACE x anything | **Absent** | `paris`, `florence`, `new-york`, `australia`, `new-zealand`, `amalfi-coast` all plain only |
---
## 4. Other hosts: axis inventories

### `abstracthouse.com` (86 collections, complete)

Flat, hand-built, no generative grammar. Axes used:

- **COLOUR** (14): `black-white`, `blue`, `brown`, `green`, `grey`, `neutral`, `orange`, `purple`, `red`, `taupe`, `teal`, `white`, `yellow`, plus `warm-colours`. Handle form `{colour}-wall-art`.
- **ROOM** (8): `bathroom`, `bedroom`, `dining-room`, `garden-room`, `hallway`, `home-office`, `kitchen`, `living-room`. Handle form `art-for-your-{room}` (room is the ONLY axis with a generative prefix here). `nursery-art-prints` sits outside that form.
  - **`garden-room` is unique to this host** - no other host has it.
- **STYLE/GENRE** (18): `abstract`, `bohemian`, `botanical`, `cityscape`, `contemporary`, `expressionist`, `figurative`, `geometric`, `impressionist`, `japandi`, `line-art`, `maximalist-bold`, `mid-century-modern`, `minimalist`, `modern`, `moody-abstract`, `scandinavian`, `still-life`
- **MEDIUM** (6): `canvas-prints`, `fine-art-photography`, `illustration`, `landscape-photography`, `oil-paintings-on-canvas`, `watercolour-botanical-leaf`
- **FORMAT/SIZE** (7): `canvas-print-sets`, `extra-large`, `large-canvas`, `set-of-three-prints`, `set-of-two-prints`, `square-prints`, `square-wall-art` (the last two are an exact duplicate pair, both 283 products)
- **OCCASION/GIFT** (7): `art-for-spring`, `fathers-day`, `gifts`, `gifts-for-her`, `gifts-for-him`, `mothers-day`, `original-gifts-for-christmas`, `valentines`
- **PRICE BAND - unique to this host** (3): `original-art-under-500`, `original-art-under-1500`, `original-art-under-500` / `Original Art GBP 500-1500`. No other host bands by price except Society6 (`under-50/75/100`).
- **PROVENANCE / EXCLUSIVITY - unique to this host** (6): `limited-edition-prints`, `original-art`, `sold-original-paintings`, `curated-picks`, `hand-picked-collection`, `solace-limited-editions-supporting-mind-charity`
- **ARTIST** (2): `julie-neumann`, `omar-obaid`
- No mood axis, no wall-position axis, no persona axis.

### `theposterclub.com` (111 collections, complete)

- **SUBJECT/GENRE** (14): `abstract`, `animals`, `architecture`, `botanical`, `figurative`, `graphic-design`, `human-figurative`, `illustrations`, `kids`, `landscape`, `line-art`, `minimalistic`, `nature`, `photo`, `scandinavian`, `typography-and-quotes` - all in form `{x}-art-prints`
- **ROOM** (6): `bathroom-art`, `bedroom-art`, `home-office-art`, `kitchen-art`, `living-room-art` - form `{room}-art`. Only 5 rooms + no position axis.
- **COLOUR** (2 only): `black-and-white-art-prints`, `colourful-art-prints`. Remarkably thin.
- **FORMAT** (9): `canvas`, `frames`, `aluminium-frames`, `oak-frames-1`, `coloured-frames-1`, `transparent-frames`, `moebe-frames`, `other-frames`, `passepartout`, `xl-art-prints`, `posters`, `transparent-prints`, `non-print`, `wall-objects`
  - **`wall-objects` / `park-pardon-masks` is a product category unique to this host** (90 products): three-dimensional wall pieces, not prints.
- **COLLABORATION / CAPSULE - the dominant axis here, unique in its density** (~40): `91-92`, `anne-nowak`, `another-art-project`, `atelier-ars-ana`, `boiler-room`, `dominika-kamanova`, `emellie-josefin`, `emilie-holm-atelier`, `laoru-laoru`, `lucrecia-rey-caro`, `nord-projects`, `park-pardon` - all form `{artist}-collection` or `{artist}-x-tpc`; plus named curated capsules: `the-alium-collection`, `the-colour-play-collection`, `the-dazed-collection`, `the-daydreamer-collection`, `the-drawings-collection`, `the-garden-collection`, `the-herbaria-collection`, `the-interstellar-collection`, `the-kinfolk-print-collection`, `the-line-of-power-collection`, `the-magical-mundane-collection`, `the-moments-collection`, `the-paris-metro-collection`, `the-peripheral-collection`, `the-placements-and-forms-collection`, `the-portrait-collection`, `the-soft-wilderness-collection`, `the-sous-la-mer-collection`, `the-symbiont-collection`, `the-zodiac-collection`, `the-art-of-process-collection`, `summer-memories`
- **SEASON/EDIT** (3): `the-art-of-summer`, `the-autumn-edit`, `summer-memories`
- **BACK-END SYSTEM handles exposed publicly** (5): `system-awd-prints`, `system-awd-canvas`, `system-awd-wall-objects`, `system-frame-collection-1`, `system-passepartout-collection` - these are internal product-type registers (AWD = Art Wall Display/Products) and should be filtered as junk.
- **Stale/deprecated handles to filter**: `abstract-art-prints-old`, `line-art-prints-old`, `test-collection`, `design-posters-and-art-prints` (0 products), `medley-collection` (0), `collection` (0), `tpc-collection` (0), `outlet` (0), `framepaint` (0), `how-to-frame-your-art` (0), `feature-collection-the-paris-metro-collection` (0), `the-placements-and-forms-collection-1` (exact dupe of `-collection`).
- **20 of 111 collections have products_count 0** - a third of this taxonomy is dead.
- No mood axis, no wall-position axis, no persona axis, no occasion axis.

### `oliveetoriel.com` (654 collections, complete)

Second-largest and structurally the most different. Generative, but on different axes from Fy!.

- **PRODUCT TYPE - the dominant axis, and far wider than any other host** : `wall-art-prints`, `canvas`, `framed-art`, `posters`, `wallpaper` (removable, peel-and-stick, vinyl, cork, linen, grasscloth, brick, concrete), `wall-murals`, `wall-decals` / `wall-stickers`, `mirrors`, `height-charts`, `calendars`, `iphone-screensavers`, `custom-size-printing`, `print-on-demand`.
  - **Wallpaper, murals, decals, mirrors and height charts are unique to this host.** Nobody else sells a wall *surface*.
- **COLOUR x SUBSTRATE cross - unique**: `blue-wallpaper`, `green-wallpaper`, `brown-wallpaper`, `beige-neutral-wallpaper`, `dark-green-wallpaper`, `black-white-grey-wallpaper`, `monochrome-grey-charcoal-removable-linen-peel-stick-wallpaper-...`, `bright-colourful-wallpaper`, `cool-tones-wallpaper`. Fy! never crosses colour with substrate.
- **COLOUR x GENRE cross - dense and unique in this form** (handle `{colour}-{genre}-wall-art-prints`): colours `aqua`, `black-white`, `blue`, `brown`, `green`, `gold`, `grey`, `monochrome`, `neutral`, `orange`, `pink`, `yellow`, `beige`, `burgundy`, `ivy-green`, `blush`, `teal`-ish; genres `abstract-painting`, `modern-abstract`, `landscape-paintings`, `photography`, `indigenous`, `vintage-poster`. e.g. `brown-indigenous-wall-art-prints`, `green-vintage-poster-wall-art-prints`.
- **PLACE / GEOGRAPHY - by far the widest of any host** (~60+): Australian - `bondi`, `bondi-beach`, `bronte`, `byron-bay-1`, `byron-bay-wategos`, `brisbane`, `sydney`, `queensland`, `tasmania`, `victoria`, `south-australia`, `western-australia`, `new-south-wales`, `far-south-coast`, `gold-coast`, `australiana`, `australia-1`; international - `amalfi-coast-1`, `isle-of-capri`, `positano`, `italy`, `france`, `paris`, `spain`, `greece-greek-islands`, `india`, `mexico`, `hawaii`, `south-america`, `nordic-lands`, `usa`, `nyc`, `los-angeles`, `santa-monica`, `venice-beach`, `venice-usa`, `joshua-tree`, `palm-springs-1`, `french-riviera`, `beverly-hills`, `dallas-texas`, `bradenton-miami-palm-beach-florida`, `atlanta`.
- **GEO-SEO LANDING AXIS - unique and highly notable**: `kids-wallpaper-in-{us-city}` -> `atlanta-ga`, `boston-ma`, `brooklyn-ny`, `chicago-il`, `denver-co`, `houston-tx`, `los-angeles-ca`, `new-jersey`, `san-diego-ca`, `san-francisco-ca`, `seattle-wa`, plus `shop-order-kids-wallpaper-in-austin-tx`. A pure local-SEO doorway grid: 12 cities x 1 product.
- **AGE / GENDER SEGMENT - unique to this host**: `boys-0-10`, `boys-5-10yrs`, `girls-0-10`, `girls-0-5yrs`, `girls-5-10yrs`, `teen-boys-wallpaper`, `teen-girls-wallpaper`, `teenage-boys-wall-art-prints`, `teenage-girls`, `surfer-girls`. Nobody else segments by child age band or gender.
- **ROOM** (12): `bedroom`, `living-room`, `kitchen`, `bathroom`, `dining-room`, `nursery`, `kids`, `boys-bedroom`, `girls-bedroom`, `home-office`, `garden`-adjacent, `playroom`-adjacent. No wall-position axis.
- **ARTIST - very wide** (~35): `alex-mason-art`, `alicia-benetatos`, `amanda-skye`, `amy-hallam`, `anne-korako-camellia-pickle`, `antonia-tzenova`, `arty-guava`, `belinda-stone`, `bigi-nagala`, `bri-chelman`, `britney-turner`, `carson-grzegorczyk`, `cat-gerke-art`, `dan-hobday`, `dani-heyward`, `david-schmitt`, `design-fabrikken`, `domica-hill`, `draw-me-a-song`, `erin-champ-artworks`, `jade-carnell`, `jenny-liz-rome`, `jenny-westenhofer`, `julie-celina`, `julita-elbe`, `katherine-spiller`, `kirsta-benedetti`, `leigh-viner`, `marco-marella-art`, `mario-stefanelli`, `meredith-howse-artworks`, `riccardo-camilli`, `rylee-olsen`, `sella-molenaar`, `shatha-al-dafai-artworks`, `svend-kindt-larsen`, `tim-harris-collection`, `tony-mott-photographic-art-collection`, `warlukurlangu-artist-community`
- **CULTURAL PROVENANCE - unique**: `aboriginal-art`, `indigenous-art`, `{colour}-indigenous-wall-art-prints`, `warlukurlangu-artist-community`, `bigi-nagala`, `dot-decals`.
- **CHANNEL / B2B - unique**: `trade-commercial-interior-designer-...` (22189 products), `commercial-vinyl-wallpaper`, `type-ii-commercial-vinyl-wallcoverings`, `childcare-daycare-vinyl-wallpaper-wallcoverings`, `press-brakes`.
- **MEDIA TIE-IN - unique**: `as-seen-on-three-birds-renovations-house-14`, `three-birds-renovations-x-mick-fanning-rolling-seas`, `shop-the-look-featured-collection`, `the-pantone-color-of-the-year-2026-cloud-dancer-art`, `vogue`.
- **FORMAT/ORIENTATION**: `canvas-art-in-horizontal-landscape`, `canvas-artworks-in-square`, `sq`, `extra-large-wall-art`, `trio-wall-art-3-piece-art-sets`, `kids-3-piece-wall-art-trios`, `wall-art-pair-set-gallery-walls`, `kids-matching-wall-art-print-sets`, `gift-packs`.
  - Set sizes observed: **pair / 2-piece, trio / 3-piece** (same ceiling of 3 as Fy!).
- **Junk / internal to filter**: `boost-all` (25763), `least-popular`, `most-popular`, `sydney-art-test`, `walk-in`, `pt`, `sq`, `press-brakes`, `letter-from-our-founder` (12554 products - a prose page masquerading as a collection), `collection`, `all`, `everything`, plus the duplicate-intent triple `shop-all` / `all-prints-posters-canvas-frames` / `everything` / `wall-decor`.
### `society6.com` (4319 collections, complete - 18 data pages)

The Shopify migration is confirmed: `/collections.json` works and returns 4319 collections, where the old
facet URLs do not. Society6 is **not** a wall-art taxonomy - it is a PRODUCT TYPE x THEME grid across the
whole homeware range, and wall art is one product type among 32.

#### PRODUCT TYPE axis (cardinality **32** observed as handle prefixes)

| Product type prefix | n themes crossed |
|---|---|
| `art-prints` | 582 |
| `shower-curtains` | 228 |
| `iphone-cases` | 179 |
| `curtains` | 160 |
| `posters` | 153 |
| `tapestries` | 124 |
| `pillows` | 114 |
| `rugs` | 87 |
| `bath-mats` | 73 |
| `throw-blankets` | 61 |
| `duvet-covers` | 56 |
| `comforters` | 45 |
| `wood-wall-art` | 37 |
| `mini-art-prints` | 34 |
| `tote-bags` | 34 |
| `mugs` | 32 |
| `wallpaper` | 30 |
| `laptop-sleeves` | 27 |
| `metal-prints` | 26 |
| `serving-trays` | 26 |
| `wrapping-paper` | 24 |
| `cutting-boards` | 23 |
| `desk-mats` | 21 |
| `water-bottles` | 20 |
| `travel-mugs` | 19 |
| `table-runners` | 19 |
| `canvas-prints` | 15 |
| `acrylic-trays` | 15 |
| `placemats` | 14 |
| `stationery-cards` | 12 |
| `notebooks` | 8 |
| `coasters` | 7 |

#### THEME axis (cardinality **1099**)

Too long to reproduce in full here without burying the signal; the full list is derivable from the raw
harvest. The structurally important fact is the shape of its distribution:

| Product types per theme | n themes |
|---|---|
| 1 | 679 |
| 2 | 181 |
| 3 | 91 |
| 4 | 52 |
| 5 | 30 |
| 6 | 19 |
| 7 | 11 |
| 8 | 7 |
| 9 | 5 |
| 10 | 4 |
| 11 | 4 |
| 12 | 3 |
| 13 | 2 |
| 14 | 2 |
| 15 | 3 |
| 18 | 2 |
| 19 | 1 |
| 22 | 2 |
| 23 | 1 |

**679 of 1099 themes (62%) exist on exactly one product type.**
Only 24 themes are crossed onto 10 or more product types - these are the commercially proven ones:

`70s`, `abstract`, `animals`, `anime`, `black-and-white`, `boho`
`botanical`, `cat`, `color`, `colorful`, `digital`, `floral`
`funky`, `funny`, `gothic`, `japanese`, `matisse`, `mid-century-modern`
`modern`, `pattern`, `preppy`, `retro`, `vintage`, `william-morris`

Themes on 7-9 product types (second tier):

`aesthetic`, `art`, `bird`, `chinoiserie`, `christmas`, `cool`
`cute`, `food`, `fuck`, `geometric`, `horror`, `jungle`
`leopard`, `moroccan`, `nature`, `persian`, `pink`, `scandinavian`
`sexy`, `southwestern`, `tiger`, `toile`, `western`

**Grid density: 2305 filled cells of 32 x 1099 = 35168 = 6.6%.** Extremely sparse -
Society6 crosses aggressively only on `art-prints` (582 themes), `shower-curtains` (228) and `iphone-cases` (179),
and barely at all on `coasters` (7) or `notebooks` (8).

#### Society6 axes not keyed to product type (2014 remaining handles)

- **PRICE BAND**: `under-50`, `under-75`, `under-100`
- **OCCASION / SEASONAL CAMPAIGN**: `back-to-school` (+ sub-variants `-feminine`, `-western`, `-naturally-collected`), `fall`, `fall-promotion`, `gothic-halloween`, `4th-of-july`, `labor-day-sale`
- **GIFT GUIDE axis - unique in its persona-crossing form**: `gift-guide`, `gift-guide-art-lover-minimalist`, i.e. `gift-guide-{persona}-{style}`. This is the only host besides Fy! with a persona axis, and Society6 crosses it with style where Fy! does not cross persona with anything.
- **FLAT STYLE/THEME collections** (no product prefix): `abstract`, `modern`, `vintage`, `retro`, `floralphotography`, `wall-art-home-living-minimalism`

---
## 5. Per-host comparison

| | `iamfy.co` | `abstracthouse.com` | `theposterclub.com` | `oliveetoriel.com` | `society6.com` |
|---|---|---|---|---|---|
| Collections (raw) | **1748** | 86 | 111 | 654 | **4319** |
| After junk filter | ~1690 | ~80 | ~75 | ~640 | ~4300 |
| Pages read / end reached | 8 / yes | 2 / yes | 2 / yes | 4 / yes | 19 / yes |
| Generative grammar? | **Yes, heavily** | No (hand-built) | No (hand-built) | Yes, moderately | **Yes, product x theme** |
| SUBJECT | yes (137) | yes (18) | yes (16) | yes (~50) | yes (1099 themes) |
| STYLE / MOVEMENT | yes (98) | yes (18) | partial | yes (~20) | yes |
| MOOD / FEELING | **yes (151)** | no | no | minimal (`moody-hues`, `bold-beautiful`, `subtle`, `warm`, `chic`) | minimal |
| MEDIUM / TECHNIQUE | yes (5 generative + ~10 flat) | yes (6) | yes (~6) | yes (~8) | no (product type instead) |
| ROOM | yes (15 tokens, 11 crossed) | yes (8) | yes (5) | yes (12) | yes (as theme: `bathroom`, `bedroom`) |
| **WALL POSITION IN ROOM** | **yes (36) - UNIQUE** | no | no | no | no |
| COLOUR | yes (~34) | yes (14) | yes (2) | yes (~20, crossed with substrate+genre) | yes (as theme) |
| OCCASION | yes (~34) | yes (8) | seasonal edits only | yes (~8) | yes (campaigns) |
| **PERSONA** | **yes (160) - near-unique** | no | no | no | yes (gift-guide only) |
| FORMAT / SET SIZE | yes (2 and 3-print) | yes (2 and 3-print) | yes (frames, canvas, XL, wall objects) | yes (pair, trio) | yes (32 product types) |
| ARTIST / IP | yes (35) | yes (2) | **yes (~40) - dominant axis** | **yes (~38)** | yes (`matisse`, `william-morris`, `audubon`, `barbie`) |
| PLACE / GEOGRAPHY | yes (7) | minimal | minimal | **yes (~60) - dominant** | yes (as theme: cities) |
| PRICE BAND | no | **yes** | no | `affordable-wall-art` only | **yes** |
| PROVENANCE / ORIGINAL vs PRINT | no | **yes - UNIQUE** | yes (`limited-editions`, `original-art`) | no | no |
| AGE / GENDER SEGMENT | `for-kids`, `kids` only | no | `kids` only | **yes (~10) - UNIQUE** | no |
| GEO-SEO DOORWAY GRID | no | no | no | **yes (12 US cities) - UNIQUE** | no |
| WALL SURFACE (wallpaper/mural/decal) | no | no | no | **yes - UNIQUE** | `wallpaper` (30 themes) |
| 3D WALL OBJECTS | no | no | **yes - UNIQUE** | `mirrors` | no |
| CULTURAL PROVENANCE (Indigenous) | no | no | no | **yes - UNIQUE** | `aboriginal`, `african-american` themes |
| B2B / TRADE CHANNEL | B2B shops only | no | no | **yes - explicit** | no |

### Axes unique to exactly one host

| Axis | Only on | Why it matters |
|---|---|---|
| WALL POSITION WITHIN ROOM (36 values) | `iamfy.co` | The single most distinctive idea in the whole corpus. Nobody else targets "above the toilet". Pure long-tail search capture. |
| PERSONA at scale (160 values) | `iamfy.co` | Society6 has 2 gift-guide personas; Fy! has 160 standalone ones. |
| MOOD/FEELING at scale (151 values) | `iamfy.co` | No other host sells on emotion at all. |
| PRICE BAND on original art | `abstracthouse.com` | Implies real originals inventory, not POD. |
| ORIGINAL vs PRINT provenance | `abstracthouse.com` | `sold-original-paintings` kept live as social proof. |
| 3D WALL OBJECTS | `theposterclub.com` | Escapes the print-commodity race entirely. |
| ARTIST-COLLAB CAPSULES as the primary axis | `theposterclub.com` | ~40 of 111 collections. Scarcity/curation model, the opposite of Fy!. |
| WALL SURFACE (wallpaper, murals, decals, mirrors, height charts) | `oliveetoriel.com` | Highest AOV category in the corpus. |
| GEO-SEO doorway grid (`kids-wallpaper-in-{city}`) | `oliveetoriel.com` | Explicit local-SEO play. |
| AGE/GENDER child segmentation (`girls-0-5yrs`) | `oliveetoriel.com` | Fy! lumps all children together. |
| CULTURAL PROVENANCE (Aboriginal/Indigenous, artist community) | `oliveetoriel.com` | Licensing moat; also a compliance obligation. |
| EXPLICIT B2B/TRADE channel collection | `oliveetoriel.com` | 22189 products exposed to trade clients. |
| PRODUCT TYPE x THEME grid at 32 product types | `society6.com` | Different business: art as surface decoration across homeware. |
---
## 6. Cardinality table and the implied product

### Fy! axis cardinalities (junk excluded)

| Axis | Cardinality |
|---|---|
| SUBJECT | **137** |
| MOOD / FEELING | **151** |
| STYLE / MOVEMENT / GENRE | **98** |
| MEDIUM / TECHNIQUE (generative) | **5** |
| MEDIUM / TECHNIQUE (incl. flat values) | **16** |
| ROOM | **11** |
| WALL POSITION WITHIN ROOM | **36** |
| COLOUR | **35** |
| OCCASION | **35** |
| RECIPIENT / PERSONA (`art-for-the-*`) | **160** |
| RECIPIENT / GIFT TARGET (other) | **10** |
| FORMAT / SIZE | **11** |
| FORMAT / SET SIZE | **2** |
| ARTIST / NAMED IP | **35** |
| PLACE / GEOGRAPHY | **8** |
| *Total distinct `{base}` tokens* | *671* |

### The implied product if all axes were crossed

Taking the content axes that could in principle multiply (SUBJECT x STYLE x MOOD x MEDIUM x ROOM x POSITION
x COLOUR x OCCASION x PERSONA x FORMAT):

```
137 subject x 98 style x 151 mood x 6 medium x 11 room x 36 position
  x 35 colour x 35 occasion x 160 persona x 11 format
  = 1.039e+16  (~1.04e+16) theoretical collections
```

Fy! actually publishes **1690** real collections. That is a fill rate of roughly **1 in 10^12**.
The taxonomy is overwhelmingly *additive*, not multiplicative: axes are laid side by side and only two or
three pairs are ever genuinely crossed.

A more honest accounting of what Fy! actually multiplies:

```
(BASE 671 x MEDIUM/FORMAT 6)               = 4,026 cells, 712 filled (17.7%)
(ROOM 11 x POSITION 36)                     = 396 cells, 124 filled (26.8%)
(SET SIZE 2 x ROOM 7)                       = 14 cells, 14 filled (100%)
(PERSONA 160 x nothing)                      = 160 flat cells
```

---
## 7. Product-level data from the endpoint (`products_count`)

`products_count` is present on every collection on all five hosts. It is a depth/popularity signal, with a
large caveat recorded below.

### Largest collections on `iamfy.co`

| products_count | Title | Handle |
|---|---|---|
| 802,338 | Art Prints | `art-lander` |
| 802,338 | Cooking Art Prints | `cooking-art-prints` |
| 801,303 | Bestselling Canvas Prints | `bestselling-canvas-prints` |
| 740,362 | Art Prints On Sale | `art-prints-on-sale` |
| 625,919 | Canvas Art | `canvas-art` |
| 619,087 | Art by Room | `art-by-room` |
| 607,517 | Art Prints | `art-prints` |
| 567,993 | Wall Art & Wall Decor | `wall-art` |
| 551,504 | Portrait Art Prints | `portrait-art-prints` |
| 305,537 | Medium Art Prints | `medium-art-prints` |
| 275,642 | Large Art Prints | `large-art-prints` |
| 242,260 | Birthday Art Prints | `birthday-art-prints` |
| 233,629 | Find the art you've searching for | `persona-ferne` |
| 227,969 | Find Art That's Really You | `persona-emma` |
| 223,423 | Framed Art Prints | `framed-art-prints` |
| 220,826 | Persona - Idris | `idris` |
| 215,789 | Nature Art Prints | `nature-art-prints` |
| 211,533 | Vibrant Art Prints | `vibrant-art-prints` |
| 177,675 | New Home Art Prints | `new-home-art-prints` |
| 176,725 | Turn Your Space Into A Vibe | `persona-sabrina` |

### Largest collections on `abstracthouse.com`

| products_count | Title | Handle |
|---|---|---|
| 2,168 | New Arrivals | `new-arrivals` |
| 1,973 | Art Prints | `art-prints` |
| 1,973 | Bestsellers | `bestseller` |
| 1,666 | Abstract Art Prints | `abstract-art-prints` |
| 977 | Gifts | `gifts` |
| 699 | Sale | `sale-1` |
| 649 | Bedroom Wall Art | `art-for-your-bedroom` |
| 629 | Blue Wall Art | `blue-wall-art` |
| 568 | Canvas Prints | `canvas-prints` |
| 447 | Art For Your Garden Room | `art-for-your-garden-room` |
| 443 | Large Canvas Wall Art | `large-canvas-prints` |
| 426 | Extra Large Wall Art | `extra-large-wall-art` |
| 410 | Neutral Wall Art Prints | `neutral-art-prints` |
| 361 | Bright And Colourful Wall Art | `bright-and-colourful-wall-art` |
| 345 | Warm Colours Wall Art | `warm-colours-wall-art` |
| 316 | Hand-picked Collection | `hand-picked-collection` |
| 298 | Valentines Gift Ideas | `valentines-gift-ideas` |
| 283 | Square Prints | `square-prints` |
| 283 | Square Wall Art | `square-wall-art` |
| 269 | Father's Day Gifts and Prints | `fathers-day-gifts-and-prints` |

### Largest collections on `theposterclub.com`

| products_count | Title | Handle |
|---|---|---|
| 1,993 | New Arrivals | `new-arrivals` |
| 1,748 | All Artworks | `all-art` |
| 1,484 | Art Prints | `art-prints` |
| 1,473 | SYSTEM - Art Wall Products - Art Prints | `system-awd-prints` |
| 1,471 | Landscape Art Prints | `landscape-art-prints` |
| 788 | Graphic Design Art Prints | `graphic-design-art-prints` |
| 674 | Abstract Art Prints | `abstract-art-prints` |
| 526 | Human & Figurative Art Prints | `human-figurative-art-prints` |
| 514 | Non Print | `non-print` |
| 408 | Figurative Art Prints | `figurative-art-prints` |
| 379 | Colourful Art Prints | `colourful-art-prints` |
| 308 | Influencer Selection | `influencer-selection` |
| 270 | XL Art Prints | `xl-art-prints` |
| 266 | Botanical Art Prints | `botanical-art-prints` |
| 156 | Main Collection | `main-collection` |
| 146 | Canvas Art | `canvas` |
| 146 | Most Popular Canvas Art | `most-popular-canvas` |
| 146 | SYSTEM - AWD - Canvas | `system-awd-canvas` |
| 107 | Illustrations Art Prints | `illustrations-art-prints` |
| 106 | Kids Art Prints | `kids-art-prints` |

### Largest collections on `oliveetoriel.com`

| products_count | Title | Handle |
|---|---|---|
| 25,763 | Boost All | `boost-all` |
| 22,833 | SHOP ALL | `shop-all` |
| 22,623 | Wall Decor | `wall-decor` |
| 22,189 | Trade & Commercial Clients | `trade-commercial-interior-designer-wall-art-prints-wallpaper-online-australia` |
| 20,033 | New Art Arrivals | `modern-new-canvas-wall-art-prints-framed-artwork-australia` |
| 19,972 | Customers' Most Loved Wall Art | `best-sellers` |
| 18,043 | Shop All Artworks | `all-prints-posters-canvas-frames` |
| 17,640 | Extra Large Wall Art | `extra-large-wall-art` |
| 12,554 | Letter from our Founder | `letter-from-our-founder` |
| 10,596 | Shop All Artworks | `everything` |
| 10,592 | least popular | `least-popular` |
| 10,592 | Modern Wall Art | `modern-wall-art` |
| 10,592 | Most Popular | `most-popular` |
| 10,244 | Affordable Wall Art Australia | `affordable-wall-art-australia` |
| 10,244 | Framed Art | `framed-art` |
| 10,241 | Wall Art Australia | Premium Australian Made Wall Art | `wall-art-australian-shop` |
| 10,167 | Posters Australia — Framed & Unframed | `posters-australia` |
| 9,858 | Canvas | `canvas` |
| 9,640 | Art on Canvas | `art-on-canvas` |
| 9,640 | Canvas Prints Australia | `canvas-wall-art-artwork-prints-australia-online` |

### Largest collections on `society6.com`

| products_count | Title | Handle |
|---|---|---|
| 2,066,933 | Moonlit & Moody | `gothic-halloween` |
| 1,656,908 | Soft & Feminine | `back-to-school-feminine` |
| 1,654,459 | Out West | `back-to-school-western` |
| 1,512,534 | Back to School | `back-to-school` |
| 1,458,735 | Gifts Under $75 | `under-75` |
| 1,348,454 | Gift Guide: Shop All | `gift-guide` |
| 1,229,255 | Fall, Finally | `fall-promotion` |
| 986,210 | Gifts Under $50 | `under-50` |
| 963,138 | Red, White, Blue & Artfully Made | `4th-of-july` |
| 948,561 | Gifts Under $100 | `under-100` |
| 811,528 | Gift Guide: The Art Lover for the Minimalist | `gift-guide-art-lover-minimalist` |
| 809,068 | Abstract | `abstract` |
| 774,693 | Naturally Collected | `back-to-school-naturally-collected` |
| 736,856 | Labor Day Sale | `labor-day-sale` |
| 639,176 | Modern | `modern` |
| 617,087 | Floral Photography | `floralphotography` |
| 611,982 | Vintage | `vintage` |
| 601,023 | Minimalist Art & Home Decor | `wall-art-home-living-minimalism` |
| 568,149 | Retro | `retro` |
| 557,052 | Fall | `fall` |

### Largest *taxonomic* (non-catch-all) Fy! collections

Stripping out the catch-alls (`art-prints`, `canvas-art`, `wall-art`, `art-by-*`, `art-prints-on-sale`,
`bestselling-*`, `art-lander`, `upgrade-your-space-*`) gives the real demand signal:

| products_count | Title | Handle |
|---|---|---|
| 802,338 | Cooking Art Prints | `cooking-art-prints` |
| 551,504 | Portrait Art Prints | `portrait-art-prints` |
| 305,537 | Medium Art Prints | `medium-art-prints` |
| 275,642 | Large Art Prints | `large-art-prints` |
| 242,260 | Birthday Art Prints | `birthday-art-prints` |
| 233,629 | Find the art you've searching for | `persona-ferne` |
| 227,969 | Find Art That's Really You | `persona-emma` |
| 223,423 | Framed Art Prints | `framed-art-prints` |
| 220,826 | Persona - Idris | `idris` |
| 215,789 | Nature Art Prints | `nature-art-prints` |
| 211,533 | Vibrant Art Prints | `vibrant-art-prints` |
| 177,675 | New Home Art Prints | `new-home-art-prints` |
| 176,725 | Turn Your Space Into A Vibe | `persona-sabrina` |
| 167,004 | Housewarming Art Prints | `housewarming-art-prints` |
| 162,682 | Warm Art Prints | `warm-art-prints` |
| 159,193 | Cool Art Prints | `cool-art-prints` |
| 159,001 | Cool Canvas Art | `cool-canvas-art` |
| 158,169 | Earthy Art Prints | `earthy-art-prints` |
| 155,109 | Abstract Art Prints | `abstract-art-prints` |
| 154,892 | Abstract Canvas Art | `abstract-canvas-art` |
| 152,336 | Bohemian Art Prints | `bohemian-art-prints` |
| 152,241 | Bohemian Canvas Art | `bohemian-canvas-art` |
| 150,737 | Persona - Stacey | `persona-stacey` |
| 140,883 | Muted Art Prints | `muted-art-prints` |
| 140,343 | Art for The Minimalist | `art-for-the-minimalist` |
| 134,025 | Bold Art Prints | `bold-art-prints` |
| 133,881 | Bold Canvas Art | `bold-canvas-art` |
| 129,389 | Art Style Art Prints | `art-styles-art-prints` |
| 128,313 | Monochrome Art Prints | `monochrome-art-prints` |
| 122,202 | Calming Art Prints | `calming-art-prints` |

### Caveat on `products_count`

These numbers are **not** reliable inventory counts and must not be read as such:

- Fy! reports 802,338 for `cooking-art-prints` and 551,504 for `portrait-art-prints` while the whole
  catalogue catch-all `art-prints` reports 607,517. A sub-collection cannot exceed its parent, so some of
  these are stale cached counts or counts against an unfiltered product universe.
- `upgrade-your-space-test-copy` and `upgrade-your-space-today-copy` both report 48,464 - identical, i.e. the
  same underlying smart-collection rule duplicated.
- Olive et Oriel reports 12,554 products for `letter-from-our-founder`, a prose page. And `most-popular`,
  `least-popular` and `modern-wall-art` all report exactly 10,592 - the same rule under three names.
- Abstract House reports 1,973 for both `art-prints` and `bestseller`, i.e. "bestsellers" is the entire catalogue.
- The Poster Club reports 0 for 30+ live collections.

What the counts ARE good for: **relative ordering within one host**, and detecting duplicate smart-collection
rules (identical counts across differently-named handles). Across the corpus the genuinely deep
*taxonomic* categories, in order, are: Portrait, Cooking, Birthday, Large/Medium size bands, Living Room
Gallery Wall (21,843 on Fy!), Landscape (1,471 on The Poster Club), Abstract (1,666 on Abstract House,
674 on The Poster Club, 809,068 on Society6).
---
## 8. Near-duplication read-across (per the repo-wide rule in CLAUDE.md)

The shared-facts rule is that near-duplicate listings are the main commercial risk, and the wall-art branch
attributes 89% near-duplication to 424k listings not selling. This harvest is direct outside evidence on that
question, so recording it explicitly:

**Fy! is itself a near-duplication machine, and the evidence is in its own handles.** Specific measurable cases:

- **Synonym pairs on the same axis.** `amused`/`amusing`, `humor`/`humorous`, `energising`/`energizing`/`energetic`,
  `relaxed`/`relaxing`/`restful`/`peaceful`/`serene`/`calming`/`quiet`/`zen`, `glam`/`glamorous`,
  `nostalgia`/`nostalgic`, `luxurious`/`luxury`, `birthday`/`birthdays`, `feminism`/`feminist`,
  `transport`/`transportation`, `spiritual`/`spirituality`, `historical`/`history`, `education`/`educational`,
  `minimal`/`minimalist`, `cities`/`cityscapes`/`places`, `flowers`/`floral`, `animals`/`wild-animals`,
  `mid-century`/`mid-century-modern`, `pop`/`pop-art`/`pop-culture`, `figurative`/`figurative-and-nude`,
  `portrait`/`portraits`, `art-styles`/`classic-art`/`modern-art`, `texture`/`textural`,
  `thought-provoking`/`thoughtful`, `concepts`/`beliefs`, `contemplative`/`introspective`/`reflective`/`pensive`.
- **Whole-room duplication.** `childrens-room-*`, `kids-room-*`, `nursery-*` and `playroom-*` are four parallel
  room families for what is substantially one room, each with its own position cross.
- **Position synonyms.** `above-bathtub`/`above-tub`; `above-cot`/`above-crib`; `bedside`/`nightstand`/`side-table`;
  `accent-wall`/`feature-wall`/`statement-wall`.
- **Persona synonyms.** ~15 confirmed near-duplicate persona pairs (listed in section 2), i.e. roughly 9% of the
  persona axis is redundant on its face.
- **Handle/title desynchronisation.** 17 live collections are reachable only via a `-copy` handle whose text
  describes a *different* room from the title. This is what an unmanaged generative taxonomy looks like after
  drift.
- **Duplicate smart-collection rules**, detectable from identical `products_count`: `upgrade-your-space-test-copy`
  and `upgrade-your-space-today-copy` (both 48,464); on Olive et Oriel `most-popular` / `least-popular` /
  `modern-wall-art` (all 10,592) and `canvas-wall-art-artwork-prints-australia-online` / `art-on-canvas` (both 9,640);
  on Abstract House `square-prints` / `square-wall-art` (both 283) and `art-prints` / `bestseller` (both 1,973);
  on The Poster Club `canvas` / `most-popular-canvas` / `system-awd-canvas` (all 146) and `wall-objects` /
  `most-popular-wall-objects` / `system-awd-wall-objects` (all 90).

**The contrast is the actionable finding.** The two hosts with the *smallest* taxonomies - The Poster Club (111)
and Abstract House (86) - are the two that sell curated, artist-collaborated and original work, and they have
near-zero synonym duplication. The two with generative taxonomies (Fy! 1748, Society6 4319) carry heavy
duplication. Olive et Oriel sits in between and differentiates on *substrate* (wallpaper, murals, decals,
mirrors) rather than on more permutations of the same print.

If a catalogue generated on this branch is to be measured against the 89% figure before upload, the axes to
measure on are the ones Fy! actually crosses - BASE x MEDIUM and ROOM x POSITION - because those are where the
combinatorial explosion lives. The axes Fy! deliberately leaves *flat* (persona, artist/IP, place, colour) are
the ones where a new entrant can add breadth without adding near-duplicates.

---
## 9. Method, sources and gaps

### Sources (all primary; public Shopify endpoints, read 2026-10-07)

- `https://iamfy.co/collections.json?limit=250&page=N` - [iamfy.co](https://iamfy.co/collections.json?limit=250&page=1)
- `https://abstracthouse.com/collections.json?limit=250&page=N` - [abstracthouse.com](https://abstracthouse.com/collections.json?limit=250&page=1)
- `https://theposterclub.com/collections.json?limit=250&page=N` - [theposterclub.com](https://theposterclub.com/collections.json?limit=250&page=1)
- `https://oliveetoriel.com/collections.json?limit=250&page=N` - [oliveetoriel.com](https://oliveetoriel.com/collections.json?limit=250&page=1)
- `https://society6.com/collections.json?limit=250&page=N` - [society6.com](https://society6.com/collections.json?limit=250&page=1)

Raw JSON retained at `/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/harvest/`
(`<host>_p<N>.json`, plus the consolidated `all.json` keyed host -> handle -> [title, products_count]).

No User-Agent was spoofed. No bot protection was encountered or bypassed. The only failures were HTTP 429
rate-limiting on `abstracthouse.com` (page 1), `theposterclub.com` (page 1) and `society6.com` (page 5), all of
which returned 200 on retry after a backoff delay. **Every host was fully enumerated; none was blocked.**

### Gaps and limitations

- **Axis assignment of Fy! bases is my interpretation, not the retailer's.** The endpoint returns a flat list of
  handles; it does not label which axis a token belongs to. All 671 base tokens were assigned to exactly one
  axis with no duplicates, but the SUBJECT/STYLE and MOOD/STYLE boundaries are judgement calls (`coastal`,
  `bohemian`, `whimsical`, `natural`, `urban`, `chic`, `elegant` could defensibly sit on either side). Cardinalities
  for those three axes should be treated as +/- ~15.
- **Fy!'s own `art-by-*` collections confirm its intended axis names** - `art-by-artist`, `art-by-colour`,
  `art-by-gift`, `art-by-mood`, `art-by-room`, `art-by-style`, `art-by-subject` - i.e. Fy! itself recognises seven
  axes: ARTIST, COLOUR, GIFT, MOOD, ROOM, STYLE, SUBJECT. It has **no** `art-by-medium` and **no** `art-by-position`
  navigation collection, even though both axes are generated. Those two are SEO-only, not navigational.
- **Society6 theme axis (1099 values) is not reproduced verbatim** in this file. It is in the raw JSON. I report its
  distribution and the 24 themes crossed onto 10+ product types, which is where the signal is.
- **No product-level data beyond `products_count`.** The endpoint gives collection id, title, handle, description,
  published_at, updated_at, image and products_count. It does not give price, SKU or per-product data, so no
  statement about actual sales or revenue per collection is possible from this source.
- **`products_count` is internally inconsistent** on Fy! and Olive et Oriel (sub-collections exceeding parents).
  Treated as a relative-ordering signal only; see section 7.
- **Olive et Oriel collection descriptions were not mined.** Several handles are SEO strings rather than axis
  values (e.g. `trade-commercial-interior-designer-wall-art-prints-wallpaper-online-australia`); their
  descriptions might disambiguate further axes but were out of scope.
- **I did not verify that every Fy! collection is live and reachable in the storefront navigation.** The endpoint
  lists published collections; a published collection can still be orphaned (no nav link), which is almost
  certainly true of the SEO-only medium and position crosses.
- **Not found: a 4-print or larger gallery wall set on any host.** Both Fy! and Olive et Oriel stop at 3. I note
  this as a real absence rather than assuming larger sets exist elsewhere.
- **Not found: a `garden-room` on any host but Abstract House**, and not found on any host: `laundry-room`
  crossed with positions (Fy! has the room, zero positions for it), `playroom` crossed with more than
  `feature-wall`/`wall-decor`, or `dining-room` crossed with set size.
