# What 1,463,031 competitor listings actually contain

> **Correction, same day.** The first version of this file reported 1,348,089
> titles and a different ranking of subject blocks. My extractor flattened tabs
> but not newlines, so titles containing a line break split into fragments and
> corrupted the source attribution. Re-extracted through a proper CSV writer;
> every figure below is from the corrected data. The subject ranking changed:
> **Animals, not Botanical, is the largest block**, and place art is 3.64% not
> 4.76%.

Analysis of the three MEGA folders the seller supplied, 8 October 2026. These
are eBay File Exchange exports the seller had already prepared from competitor
catalogues, so the listing text is the competitor's subject wording plus the
seller's own eBay suffix.

| folder | what it is | files | titles extracted |
|---|---|---|---|
| `PBF1FRTZ` | Displate, "1.5 million art" | 15 CSV, 1.11 GB | **500,093** |
| `LEdCnJQD` | "800k raw art files" (Fy!-sourced) | 12 CSV, 1.38 GB | **665,026** |
| `jRFREaIB` | Fy! art prints 300k, **one file per collection** | 71 files, 0.49 GB | **297,912** |
| | | **92 files read** | **1,463,031** |

Of those, **1,348,089 carry a usable subject phrase** once the seller's own
`... Wall Art Poster Canvas Print Picture` suffix is stripped; the percentages
below use that denominator. Four of the fifteen Displate files were lost to a
race between two download runs and were re-fetched afterwards, so the Displate
figure is a floor, not a ceiling.

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
| **Animals** | 153,745 | **11.40%** |
| **Botanical** (flowers, leaves, trees, forest) | 142,413 | **10.56%** |
| **Abstract and geometric** | 122,958 | **9.12%** |
| Landscape and nature | 93,024 | 6.90% |
| People, portrait, fashion | 55,064 | 4.08% |
| **Place - map, city, skyline, flag** | 49,058 | **3.64%** |
| Vintage and retro | 41,191 | 3.06% |
| Typography and quotes | 35,946 | 2.67% |
| Celestial | 20,818 | 1.54% |
| Food and drink | 20,584 | 1.53% |
| Nursery and kids | 19,981 | 1.48% |
| Vehicles | 14,952 | 1.11% |
| Sport | 10,926 | 0.81% |
| Music | 6,197 | 0.46% |
| Religion and spiritual | 5,665 | 0.42% |
| Film, TV and gaming | 4,829 | 0.36% |

Place words on their own: **map 22,689 · city 15,872 · skyline 10,287 · street
4,836 · flag 4,481 · island 2,817 · cityscape 2,442 · coast 2,075 · bay 1,635 ·
town 1,552 · state 1,174 · harbour+harbor 869 · county 318 · metro 124 ·
underground 108 · subway 86**.

**Subject phrases are short: mean 28 characters.** The competitor names the
thing and stops. 790,504 of 1,348,089 subject phrases are distinct, so
**41% are duplicates within their own data.**

---

## Their catalogues are template-generated, and the templates are shallow

This is the mechanism worth copying, and the measurements show how little of
each template they have actually used.

| template | listings | distinct slot values | what fills the slot |
|---|---|---|---|
| `{X} Map` | **22,689** | — | places |
| `{X} Definition` / `{X} Meaning` | **17,220 / 15,798** | **9,634** subjects | law student, sneakerhead, tax, coffeeholic, auditor, podiatrist, friendship, boldness, hygge, resilience |
| `{X} Skyline` | **10,287** | — | cities |
| `{X} Life` | 9,359 | — | — |
| `{X} Flag` | 4,481 | — | countries, states, causes |
| `{X} Club` / `{X} Lover` / `I Love {X}` | 1,857 / 1,606 / 1,298 | — | — |
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

**World cities: 56 of 58 present, and deep** — London 5,499 · Paris 4,441 ·
Amsterdam 2,375 · Tokyo 2,103 · Chicago 2,088 · Venice 1,552 · Sydney 1,492 ·
Rome 1,421 · Dubai 1,255 · Barcelona 1,228 · Berlin 1,210 · Rio 1,200 ·
Lisbon 1,099 · Toronto 990 · Singapore 959 · Florence 858 · Istanbul 850.

**UK cities: 71 of 76 present, but only two of them deep** — London 5,499 and
York 5,382, then it falls away sharply: Lincoln 816 · Bath 642 · Edinburgh 579
· Manchester 462 · Liverpool 364 · Birmingham 274 · Bristol 227 · Perth 215 ·
Chester 213 · Brighton 199 · Canterbury 195 · Newcastle 192 · Oxford 188 ·
Glasgow 174 · Leeds 170 · Cambridge 169.

> **Chicago alone (2,088) outnumbers Manchester, Liverpool, Birmingham,
> Bristol, Brighton, Newcastle and Leeds combined (1,888).** A single American
> city carries more of this catalogue than the seven largest English cities
> outside London and York put together. That is the imbalance to exploit.

Absent or thin: St Albans, Newry, Dunfermline, Kirkwall.

**UK ceremonial counties: 8 of 38 effectively missing** — Berkshire,
Buckinghamshire, Hertfordshire, Leicestershire, Northamptonshire,
Nottinghamshire, Warwickshire, Worcestershire. The Midlands and Home Counties,
in other words.

**UK towns, coast and country: 27 of 88 tested are missing** — St Ives, Looe,
Minehead, Lymington, Beaulieu, Seaford, Lewes, Arundel, Bosham, Emsworth,
Cowes, Ventnor, Aberystwyth, Beddgelert, Mallaig, Islay, Ullapool, Applecross,
Pitlochry, Aviemore, Braemar, Ballater, Crathie, Peebles, Portpatrick, Bute,
Northumbria. Those present are mostly thin: Whitby 51 · Bamburgh 51 ·
Alnwick 49 · Scarborough 46 · Exmoor 41.

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
