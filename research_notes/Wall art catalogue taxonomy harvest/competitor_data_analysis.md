# What 1,348,089 competitor listings actually contain

Analysis of the three MEGA folders the seller supplied, 8 October 2026. These
are eBay File Exchange exports the seller had already prepared from competitor
catalogues, so the listing text is the competitor's subject wording plus the
seller's own eBay suffix.

| folder | what it is | files | titles extracted |
|---|---|---|---|
| `PBF1FRTZ` | Displate, "1.5 million art" | 15 CSV, 1.11 GB | **500,093** |
| `LEdCnJQD` | "800k raw art files" (Fy!-sourced) | 12 CSV, 1.38 GB | **374,723** |
| `jRFREaIB` | Fy! art prints 300k, **one file per collection** | 71 files, 0.49 GB | **473,273** |
| | | | **1,348,089** |

---

## The images in these dumps cannot be retrieved

Every image URL in all three exports is dead:

- Displate: `s3.g.s4.mega.io/.../displate/<id>/black.png` → **HTTP 500**
- Fy!: `fydn.imgix.net/m%2Fgen%2Fart-print-std-portrait-framed-black%2F...` → **HTTP 410 Gone**

So no visual analysis is possible from the dumps themselves. Both retailers'
live sites are reachable, so a sample of real images was taken from those
instead - see `live_image_style_analysis.md`. Everything in *this* file comes
from text, and is labelled as such.

There is also no GPU, no CUDA and no local vision model in this container
(`nvidia-smi` absent, `torch` not installed), and RunPod credit is about $3, so
a bulk machine-vision pass over images was not an option either way.

---

## Subject blocks, measured

Share of all 1.35M listings whose subject phrase matches each block. A listing
can match more than one, so these do not sum to 100%.

| block | listings | share |
|---|---|---|
| Botanical (flowers, leaves, trees, forest) | 69,371 | **7.93%** |
| Animals | 62,417 | **7.13%** |
| Landscape and nature | 61,081 | **6.98%** |
| Abstract and geometric | 49,462 | **5.65%** |
| **Place - map, city, skyline, flag** | 41,677 | **4.76%** |
| People, portrait, fashion | 40,940 | 4.68% |
| Typography and quotes | 34,447 | 3.94% |
| Celestial | 15,124 | 1.73% |
| Vintage and retro | 12,212 | 1.40% |
| Vehicles | 11,863 | 1.36% |
| Food and drink | 10,702 | 1.22% |
| Sport | 8,106 | 0.93% |
| Music | 5,328 | 0.61% |
| Nursery and kids | 5,278 | 0.60% |
| Religion and spiritual | 5,068 | 0.58% |
| Film, TV and gaming | 3,923 | 0.45% |

Place words on their own: **map 20,180 · city 12,410 · skyline 9,139 · flag
4,350 · street 2,529 · cityscape 1,706 · island 1,185 · town 1,020 · coast 882
· bay 768 · harbour+harbor 537 · county 261 · metro 107 · underground 72**.

**Subject phrases are short: mean 23 characters.** The competitor names the
thing and stops. 479,280 of 874,816 Displate+800k subjects are distinct, so
**45% are duplicates within their own data.**

---

## Their catalogues are template-generated, and the templates are shallow

This is the mechanism worth copying, and the measurements show how little of
each template they have actually used.

| template | listings | distinct slot values | what fills the slot |
|---|---|---|---|
| `{X} Map` | **20,180** | — | places |
| `{X} Definition` / `{X} Meaning` | **17,113 / 15,707** | **9,579** subjects | law student, sneakerhead, tax, coffeeholic, auditor, podiatrist, friendship, boldness |
| `{X} Skyline` | **9,139** | — | cities |
| `{X} Flag` | 4,350 | — | countries, states, causes |
| `... in the style of {MOVEMENT}` | 3,232 | **135** | Pop Art 685, Matisse 606, Ukiyo-e 181, Expressionism 142, Impressionism 141, William Morris 99, Fauvism 89, Cubism 78 |
| `Still Life ...` | 1,572 | — | — |
| `... Line Drawing` | 1,334 | — | — |
| `{X} Travel Poster` | 1,328 | — | destinations |
| `Inspired By {ARTIST}` | 704 | **110** | Cezanne 138, Matisse 90+22, Van Gogh 16, Warhol 16, Klimt 12 |
| `{PLACE} Black And White Analogue Photograph` | 682 | — | places |
| `Flower Market {X}` | 546 | — | — |
| `Bird With A Flower Crown {SPECIES}` | **296** | **96 species** | Falcon, Magpie, Pheasant, Kiwi, Sparrow, **Great Blue Heron, American Goldfinch, Cowbird, Hermit Thrush** |
| `A Window View Of {CITY} In The Style Of {MOVEMENT}` | **148** | **20 cities x 3 movements** | Marrakech, San Francisco, Prague, Istanbul, Havana, Vienna, Berlin, London, New York, Venice, Tokyo, Amsterdam, Paris, Rio, Florence, Sydney, Barcelona, Cape Town, Rome, Buenos Aires |
| `{X} Illustration Zodiac Star Sign` | 51 | 12 signs | — |
| `Linocut Of {UK BEACH}` | **7** | **5 places** | Cemaes Bay Anglesey, Barafundle Bay Pembrokeshire, Broadstairs Kent, Chesil Beach Dorset, Bamburgh Northumberland |

**The last two rows are the finding.** `A Window View Of {city} In The Style Of
{movement}` is a clean, proven, fully pictorial template and they have filled
exactly **20 cities x 3 movements = 148 cells**. `Linocut Of {UK beach}` exists
in **five** instances. These are not saturated markets; they are templates
nobody has run to depth.

---

## Where the place coverage actually is, and is not

Tested against official lists.

**World cities: 56 of 58 present, and deep** — Paris 2,389 · London 2,234 ·
Chicago 1,537 · Dubai 996 · Tokyo 978 · Venice 893 · Sydney 810 · Amsterdam 762
· Toronto 738 · Singapore 722 · Rio 705.

**UK cities: 69 of 76 present but shallow** — York 3,256 and London 2,234 are
strong, then it collapses: Lincoln 772 · Manchester 335 · Liverpool 307 ·
Edinburgh 220 · Chester 213 · Bath 188 · Birmingham 187 · Bristol 161 ·
Newcastle 141 · Leeds 137 · Oxford 122 · Brighton 114 · Plymouth 111 ·
Sheffield 106 · Cambridge 101.

> **Chicago alone has more listings (1,537) than Manchester, Liverpool,
> Birmingham, Bristol, Newcastle, Leeds, Sheffield and Brighton combined
> (1,688 across eight cities).** That is the imbalance to exploit.

Absent or thin: St Albans, Lisburn, Armagh, Newry, Dunfermline, Kirkwall.

**UK ceremonial counties: 14 of 38 effectively missing** — Bedfordshire,
Berkshire, Buckinghamshire, Derbyshire, Gloucestershire, Hertfordshire,
Leicestershire, Lincolnshire, Merseyside, Northamptonshire, Nottinghamshire,
Shropshire, Warwickshire, Worcestershire.

**UK towns, coast and country: 44 of 88 tested are missing** — Windermere,
Alnwick, Lulworth, St Ives, Fowey, Polperro, Mousehole, Looe, Tintagel,
Clovelly, Lynmouth, Minehead, Swanage, Lymington, Beaulieu, Seaford, Lewes,
Arundel, Bosham, Emsworth, Cowes, Shanklin, Ventnor, Aberystwyth, Conwy,
Caernarfon, Betws-y-Coed, Beddgelert, Mallaig, Mull, Islay, Ullapool, Plockton,
Applecross, Pitlochry, Aviemore, Braemar, Ballater, Peebles, Moffat,
Portpatrick, Bute, Northumbria.

Every one of those is a place a UK buyer would plausibly buy a print of, and
most are exactly the sort of coastal and country subject the `Linocut Of {UK
beach}` template was built for and then abandoned after five.

---

## Style and medium vocabulary, measured

| style word | listings | share |
|---|---|---|
| gold / metallic | 8,434 | 0.96% |
| watercolour | 8,170 | 0.93% |
| black & white / monochrome | 4,519 | 0.52% |
| gothic / dark / skull | 3,882 | 0.44% |
| neon | 3,573 | 0.41% |
| boho | 3,074 | 0.35% |
| graffiti / street art | 2,378 | 0.27% |
| pop art | 2,336 | 0.27% |
| line art | 2,190 | 0.25% |
| photographic | 1,974 | 0.23% |
| ink / sumi-e | 1,448 | 0.17% |
| psychedelic | 1,284 | 0.15% |
| pencil / charcoal | 1,140 | 0.13% |
| oil / impasto | 1,103 | 0.13% |
| vector / flat | 1,078 | 0.12% |
| cyanotype / blueprint | 1,015 | 0.12% |
| surreal | 947 | 0.11% |
| collage | 942 | 0.11% |
| y2k / vaporwave | 651 | 0.07% |
| japandi / scandi | 641 | 0.07% |
| linocut / woodblock | 537 | 0.06% |
| art deco | 266 | 0.03% |
| art nouveau | 85 | 0.01% |
| cottagecore | 82 | 0.01% |
| risograph | 59 | 0.01% |
| halftone | 28 | 0.00% |

Two readings. The top of the list is where supply already is, so matching it
competes head-on. The bottom - **linocut 537, art deco 266, art nouveau 85,
cottagecore 82, risograph 59, halftone 28** - is nearly empty, and the earlier
style research found those are exactly the textured, handmade treatments the
2026 trend sources call for. They are also the treatments that hide the
machine-made look, because the physical artefact reads as craft.

---

## The licensed IP in their data, which is what to avoid

2.32% of the 1.35M listings (20,320, overlapping) carry something that should
never be generated. Present in the dumps, verbatim: *Millenium Falcon*, *Vader
Helmet Schematic*, *ARC-170*, *Hammer and Sickle*.

| category | listings | share |
|---|---|---|
| Named modern artists (Banksy, Warhol, Picasso, Dali, Basquiat, Haring, Hockney, Kusama) | 4,708 | 0.54% |
| Brands (Nike, Gucci, Chanel, Coca-Cola, BMW, Porsche, PlayStation) | 4,279 | 0.49% |
| Sports clubs and figures | 3,886 | 0.44% |
| Music artists | 3,033 | 0.35% |
| Film and TV series | 948 | 0.11% |
| Disney | 791 | 0.09% |
| Marvel / DC | 650 | 0.07% |
| Anime franchises | 548 | 0.06% |
| Video games | 525 | 0.06% |
| Star Wars | 439 | 0.05% |
| Royal | 263 | 0.03% |
| Harry Potter | 141 | 0.02% |
| LOTR / Hobbit | 109 | 0.01% |

Fy!'s own titles name artists openly: **pre-1956 artists in 4.15%** of their
titles (Matisse 2,479 · William Morris 1,566 · Redouté 589 · Hokusai 541 ·
Monet 485 · Klimt 482 · Van Gogh 423 · Cézanne 390) and **post-1955 artists in
0.78%** (Warhol 401 · Picasso 296 · Dalí 203 · Miró 195 · Hockney 93 · Pollock
80 · Kusama 70 · Basquiat 31). The second group is still in copyright and is
the clearest avoidable risk in the whole corpus.

Their safe-naming device is worth copying: **"Inspired By Cézanne"**, **"Blue
Leaf Inspired By Matisse"**, **"In The Style Of Ukiyo-e"**. Naming a movement
or a long-dead artist captures the search demand; naming a living or
recently-dead one invites a takedown.

---

## Data-quality faults in their files, worth not repeating

- **Titles truncated mid-word.** The template skeletons show
  `{} definition meaning art print` (6,712) degrading through `art prin`
  (2,132), `art pri` (1,880), `art pr` (1,696), `art p` (1,238) - their title
  builder cut to 80 characters without respecting word boundaries.
- **8,008 Fy! titles exceed 80 characters**, with one at 899. eBay will reject
  those.
- **45% duplicate subject phrases** in the Displate and 800k sets.
- Every Displate row carries identical item specifics - `*C:Style` = Modern,
  `*C:Room` = "Living Room, Bedroom", `*C:Colour` = Colorful, `*C:Pattern` =
  Abstract on all 500,093 - so those columns carry no information at all and
  cannot be used as a taxonomy signal. eBay's own filters will be useless for
  every one of those listings.

---

## Generation cost, computed

FLUX.1 schnell at 4 steps, roughly 1 megapixel, on RunPod's published rates.
Throughput is the weak figure - community reports say ~2 s/image on a 4090,
JarvisLabs says 6-10 s - so three cases are shown.

| designs | optimistic 2 s | middle 4 s | pessimistic 8 s |
|---|---|---|---|
| 100,000 | **$19** | **$38** | **$76** |
| 500,000 | $94 | $189 | $378 |
| 1,000,000 | $189 | $378 | $756 |
| 2,500,000 | $472 | $944 | $1,889 |

All on an RTX 4090 at $0.34/GPU-hour (community cloud). A secure-cloud 4090 is
2x, an L40S 2.5x, an A100 80GB 4.8x - there is no reason to pay for those here.

Wall-clock on the cheap option at the middle speed: 1M designs is 46 days on
one GPU, **9.3 days on five**, 2.3 days on twenty - for the same $378, because
the bill is GPU-hours not GPU-count.

**Storage**: listing images at ~400 KB each cost **$6/month per million** on R2.
Pre-rendering A2/300dpi print masters would cost **$659/month per million** -
about 100x more for files with a sub-0.1% hit rate. Store the recipe and a
compressed master; render the print file on order.

**Upscaling** to A2 at 300 dpi costs about as much again as generating
($567/million). Only upscale a design **after it sells**.

So the honest headline: **a million designs is a few hundred dollars of GPU
time and $6/month to host.** The constraint is not money.
