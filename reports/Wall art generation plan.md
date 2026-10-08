# How to make millions of wall-art designs of our own

Written 8 October 2026, from the three MEGA folders you sent (1,463,031
competitor listings), 156 of the retailers' live images viewed one by one, a UK
place gazetteer built from official registries, and the earlier taxonomy and
legal research in this repo.

The short version: **the competitors' catalogues are template-generated and
their templates are barely filled in.** We do not need a new idea. We need to
take proven templates and run them to depth on slot values they have skipped —
and the biggest skipped block is the UK itself.

---

## 1. What the data actually says

**Their catalogues are machine-made from a few dozen phrasings.** The template
counts are the whole story:

| their template | listings they made | slot values they used |
|---|---|---|
| `{X} Definition` / `{X} Meaning` | 17,220 / 15,798 | **9,634 subjects** |
| `{X} Map` | 22,689 | places |
| `{X} Skyline` | 10,287 | cities |
| `... In The Style Of {MOVEMENT}` | 3,232 | 135 movements |
| `Inspired By {ARTIST}` | 704 | 110 artists |
| `Bird With A Flower Crown {SPECIES}` | 296 | **96 species, skewed American** |
| `A Window View Of {CITY} In The Style Of {MOVEMENT}` | **148** | **20 cities × 3 movements** |
| `Linocut Of {UK BEACH}` | **7** | **5 beaches** |

Look at the last two rows. `A Window View Of {city} In The Style Of {movement}`
is a clean, fully pictorial template with no lettering, and they have filled
**148 cells**. `Linocut Of {UK beach}` — a template aimed squarely at the UK
market — exists in **five instances**. These are not saturated markets. They
are good ideas nobody has run.

**The UK is the hole.** Place art is 3.64% of their corpus (map 22,689, city
15,872, skyline 10,287), and the coverage is lopsided:

> **Chicago alone (2,088 listings) outnumbers Manchester, Liverpool,
> Birmingham, Bristol, Brighton, Newcastle and Leeds combined (1,888).**

Only London (5,499) and York (5,382) are deep. Bath 642, Edinburgh 579,
Manchester 462, Liverpool 364, Birmingham 274. Eight of the 38 ceremonial
counties are missing outright — Berkshire, Buckinghamshire, Hertfordshire,
Leicestershire, Northamptonshire, Nottinghamshire, Warwickshire,
Worcestershire, i.e. the Midlands and Home Counties. Of 88 well-known UK towns
and coastal places tested, 27 are absent and most of the rest are thin: Whitby
51, Bamburgh 51, Alnwick 49, Scarborough 46.

**Their styles cluster where supply already is.** Gold/metallic 8,434,
watercolour 8,170, black & white 4,519, neon 3,573. Meanwhile **linocut 537,
art deco 266, art nouveau 85, cottagecore 82, risograph 59, halftone 28** —
and those are precisely the textured, handmade treatments the 2026 trend
research calls for, and the ones that disguise machine-made output because the
physical artefact reads as craft.

**What the images told us that the titles could not.** Fy! is 79% portrait 3:4;
Displate is uniformly 5:7 — one master cannot serve both without a crop.
Displate uses **no margin at all** (0 of 48 sampled), and one sampled quote
print is cropped mid-letter as a result. Fy!'s catalogue looks coherent not
because of one style but because of three constants: a flat artwork file with
no frame or room mockup, portrait 3:4, and a restricted warm-neutral palette.
And **Displate's 2024-26 work is converging on AI-photoreal hyper-saturation**
— the exact register our near-duplication problem lives in. That is the one
thing in this corpus to deliberately not copy.

---

## 2. The generation model

One design = **one slot value × one treatment × one composition**. Nothing
clever. The scale comes from the slot lists being long and official.

### The UK place axis — about 7,000 named atoms, all from official registries

| block | count |
|---|---|
| Named settlements (454 English built-up areas 20k+, 235 Scottish towns, 161 Welsh towns, 558 London districts) | **1,408** |
| Hills and water (214 Wainwrights, 282 Munros, 186 Welsh Nuttalls, 244 Scottish islands, 1,013 lochs, 1,205 named rivers, 31 Lakeland lakes) | **3,175** |
| Built landmarks (212 cathedrals, 446 English Heritage, 302 Historic Scotland, 260 Welsh castles, 85 lighthouses, 59 piers, 441 stone circles, 74 Oxbridge colleges) | **1,879** |
| Protected areas (15 National Parks, 46 National Landscapes) | **61** |
| Transport (269 Underground stations, 195 canals) | **464** |
| **total** | **≈6,987** |

And the ONS built-up-area dataset extends settlements from 1,408 to **7,018**
if we drop the population floor to 5,000 — villages included.

### The other subject axes, also from official lists

636 British bird species (BOU) · 107 British mammals · 59 butterflies · 221
Kennel Club dog breeds · 45 cat breeds · ~130 native livestock breeds · 1,692
native plants (BSBI) · ~3,000 visible fungi · 35 native trees · 88 IAU
constellations · 102 IBA cocktails · **9,634 Definition subjects already
extracted from their own data**.

### The treatment axis — 15 that FLUX renders well and the market under-supplies

linocut · woodblock · vintage travel poster · letterpress · risograph ·
cyanotype · botanical plate · antique lithograph · watercolour (wet-edge,
granulating) · ink wash · impasto / palette knife · single-weight line art ·
mid-century flat · art nouveau ornament · halftone

Each gets prompt fragments naming the **physical artefact** — gouge marks,
roller mottle, paper tooth, dry-brush skip, riso mis-registration, plate
wear — not the style noun. That was the single clearest lesson from looking at
their images.

### The arithmetic, at three depths

| depth | designs | GPU cost at 4 s/image on a community RTX 4090 | SKUs at 15 listing variations |
|---|---|---|---|
| **Phase 1 — prove it** | 7,000 UK places × 3 treatments = **21,000** | **$8** | 315,000 |
| **Phase 2 — the UK catalogue** | 7,000 places × 15 treatments = **105,000**, plus 1,200 species × 10, 4,700 botanical × 8, 9,634 definitions × 3 = **134,000 more** | **$90** | 3.6M |
| **Phase 3 — millions of designs** | 7,018 settlements + all other axes × 139 copyright-free treatments ≈ **1.0-1.4M designs** | **$380-530** | 15M+ |

**Sizes and frame colours are variations inside one listing, never separate
listings.** eBay allows 250 variations free, and three independent retailers in
this market (Saatchi, Wallfillers, Fy!) all put the size/material matrix inside
one product. That is how a few hundred thousand designs becomes millions of
SKUs without a duplicate problem.

---

## 3. What to generate — the ranked build order

1. **`{UK place} in {treatment}`, pictorial, no lettering.** The direct answer
   to the gap. Whitby in linocut, Alnwick in vintage travel poster, Islay in
   cyanotype, Aviemore in woodblock. 7,000 × 15 = 105,000 designs that barely
   exist anywhere.
2. **`A Window View Of {UK place} In The Style Of {movement}`** — their own
   template, which they ran to 20 world cities and three movements. We run it
   to 1,408 UK settlements and 20 public-domain movements. Fully pictorial, no
   text, so no lettering risk.
3. **British wildlife at species depth.** Their `Bird With A Flower Crown`
   covers 96 species and leans American (Great Blue Heron, American Goldfinch,
   Cowbird). The BOU British List has **636**. Same for 107 mammals, 59
   butterflies, native livestock breeds.
4. **Botanical plates of British flora** — 1,692 native plants in the antique
   plate idiom, with the Latin binomial composited as type afterwards, never
   generated.
5. **`{X} Definition`** — 9,634 subjects already proven in their data, as a
   typography product our existing text renderer can draw perfectly.
6. **Textured abstract in the warm-neutral palette** — the safest
   high-volume filler, no subject to get wrong, and the palette Fy! uses to
   make a mixed catalogue look like one shop.

---

## 4. What must never be generated

2.32% of their 1.46M listings carry something that would get a listing pulled,
and it sits **inside ordinary subject collections**, not in a separate fandom
aisle — the image sampling found a licensed children's character, a
Winnie-the-Pooh quote, a named video game and song lyrics inside normal
collections. Present verbatim in the dumps: *Millenium Falcon*, *Vader Helmet
Schematic*, *ARC-170*.

| exclude | why |
|---|---|
| Characters, franchises, film and game art | copyright + the top VeRO trigger |
| Logos, brands, football crests | trade mark |
| Celebrity likeness | passing off (*Fenty v Arcadia*) |
| **Royal insignia, Royal Arms, crowns** | **criminal offence, s.99 Trade Marks Act 1994** |
| Artists dead less than 70 years — Warhol, Picasso, Dalí, Miró, Hockney, Pollock, Kusama, Basquiat | copyright in specific works. Their data names these in 0.78% of Fy! titles — the clearest avoidable risk in the corpus |
| Any output containing legible text, a signature or a watermark-like mark | the one control with direct judicial support, from *Getty v Stability* |
| Football stadiums (135 in the gazetteer) | listed for completeness, flagged trademark-risky, recommend not building |

**Copy their safe-naming device.** Fy! writes *"Inspired By Cézanne"*, *"In The
Style Of Ukiyo-e"*, *"William Morris Style"*. Naming a movement or a long-dead
artist captures the search demand; naming a living one invites a takedown.
Artists dead before 1956 are clear: Van Gogh, Monet, Klimt, Hokusai, Mucha,
Morris, Cézanne, Matisse (d. 1954).

---

## 5. The pipeline

**Generate the picture, composite the type.** This is the most important
architectural decision and it falls out of the image sampling: 17 of 48
Displate images and about 32 of 108 Fy! images contain text, including a map
built from hundreds of place names. FLUX cannot be trusted with lettering, and
we already have a typography renderer that draws type to an asserted size
contract. So schnell draws the panel; place names, captions and Latin binomials
are composited as vector type at build time.

Settings, from the engineering research:
- **schnell's T5 window is 256 tokens, not 512** (that is the dev figure, and
  nearly every guide online conflates them). Enforce it at prompt assembly.
- **Negative prompts do nothing** at `guidance_scale=0`. Unwanted frames,
  borders and signatures are handled by positive description, deliberate
  overscan-and-crop, and a rejection gate — not by asking.
- Generate at **848×1200** for the A-series ratio, **864×1152** for 3:4,
  **880×1232** for 5:7. The A-ratio with 2% overscan can serve 5:7 by
  differential crop; 3:4 needs its own render.
- **Design with a margin.** Displate's zero-margin convention is why one of
  their quote prints is cropped mid-letter. We keep a safe area.

Quality gates, cheapest first: palette conformance in CIELAB · OCR for
unwanted lettering and watermarks · aesthetic predictor calibrated per
treatment · then the near-duplicate index.

**The near-duplicate gate must run on the picture, not the title.** Same panel
plus different type is still a duplicate. pHash as tier one, then CLIP or
DINOv2 embeddings in a FAISS HNSW index (M=32, efConstruction=200,
efSearch=128 — about 15 GB for 5M vectors, one ordinary machine). Reject at
≥0.93 cosine; the 0.85-0.93 band needs calibrating by hand on a few hundred
labelled pairs, because that band is where the business lives and the
literature is silent.

**Render print files on order.** Pre-rendering A2/300dpi masters for a million
designs would cost **$659/month** of storage against **$6/month** for the
listing images — about 100× more for files with a sub-0.1% hit rate. Store the
prompt, model and seed, plus a compressed master. **Upscale only after a design
sells**; upscaling the whole catalogue costs about as much again as generating
it ($567 per million).

---

## 6. What it costs

FLUX.1 schnell, 4 steps, ~1 megapixel, RunPod's published rates. Throughput is
the weak number — community reports say ~2 s/image on a 4090, JarvisLabs says
6-10 — so three cases:

| designs | optimistic 2 s | middle 4 s | pessimistic 8 s |
|---|---|---|---|
| 100,000 | $19 | **$38** | $76 |
| 500,000 | $94 | **$189** | $378 |
| 1,000,000 | $189 | **$378** | $756 |
| 2,500,000 | $472 | **$944** | $1,889 |

All on an RTX 4090 at **$0.34/GPU-hour** on community cloud. Secure cloud is
2×, an L40S 2.5×, an A100 80GB 4.8× — no reason to pay for any of those here.

Wall-clock at the middle speed: a million designs is 46 days on one GPU,
**9.3 days on five**, 2.3 days on twenty — for the same $378, because the bill
is GPU-hours, not GPU-count.

Hosting: **$6/month per million** listing images on R2, which charges no egress.

So your memory is right: **this is cheap.** A million designs is a few hundred
dollars of GPU time. The constraint has never been money.

**With the ~$3 currently in RunPod** we can generate roughly **7,000 designs**
at the middle speed — which is almost exactly Phase 1's 7,000 UK places at one
treatment each. That is a real, completable first batch, not a toy: it would
put one print of every named UK place, hill, island, castle, lighthouse and
cathedral into the catalogue. Top up to **$50** and Phase 2's full 239,000-design
UK catalogue is covered with change left over.

---

## 7. Honest limits

- **The images in your dumps cannot be retrieved.** Displate's S3 host returns
  500, Fy!'s imgix host 410. Style was learned from 156 images sampled off the
  live sites instead. Everything drawn from the dumps is text-only, and labelled
  as such.
- **No sales data anywhere.** Not in the dumps, not on either site. "What sells"
  rests on listing volume, which is what a competitor chose to make, not what a
  buyer chose to buy. Volume is a supply signal that we are reading as a demand
  signal, and that is an assumption, not a measurement.
- **The per-subject style findings are n=10 each**, and the Displate sample
  (48 images) was not subject-balanced because its browse pages are
  Cloudflare-blocked, so no per-subject claim about Displate is supportable.
- **I corrected my own error partway through.** The first extraction flattened
  tabs but not newlines, which corrupted the source attribution and the subject
  ranking. The figures here are from the re-extraction; the ranking changed
  (Animals, not Botanical, is the largest block).
- **Four of fifteen Displate files** were lost to a race between two download
  runs and re-fetched, so the Displate count is a floor.
- **Munros read 282 official against 266 named rows** in the source table; that
  discrepancy is unresolved and flagged in the gazetteer.
