# First-hand browser harvest (coordinator)

Captured directly in this session with a real Chromium browser (Playwright,
`/opt/pw-browsers/chromium-1194`) on 7 October 2026, after installing the agent
proxy's CA into the Chromium NSS trust store so TLS would verify. This closes
some of the gaps the HTTP-fetch researchers reported, and confirms others as
genuinely closed.

Everything below was read off the live page, not from a search summary.

---

## Access results: what a real browser changes and what it does not

| Site | Plain HTTP fetch (researchers) | Real browser (this harvest) |
|---|---|---|
| Juniqe | 200 with an **empty body** (client-rendered SPA) | **Readable** — full nav and filter facets |
| Fy! / iamfy.co | reachable | **Readable** + `collections.json` enumerable |
| Abstract House | reachable | **Readable** |
| Saatchi Art | 403 | **Readable** — full filter facets |
| Rijksmuseum | 404 on the art-movements path | Collection page readable (thin) |
| Redbubble | Cloudflare 403 everywhere | **Still blocked** — "Just a moment..." interstitial does not clear |
| Etsy | 403 everywhere | **Still blocked** — 403, empty body |
| Desenio / Poster Store | Vercel checkpoint 429 | **Still blocked** — checkpoint does not clear |
| Posterlounge | 429 | **Still blocked** — 429 Too Many Requests |
| King & McGaw | 403 | **Still blocked** — Cloudflare |
| Surface View | 403 | **Still blocked** — Cloudflare |
| Art Institute of Chicago | 403 | **Still blocked** — Cloudflare |
| MoMA Design Store | not reached | **Blocked** — Cloudflare |
| The Poster Club `/collections/all-posters` | — | 404 (wrong slug; store itself is reachable) |
| Royal Academy `/shop/prints` | — | 404 (wrong slug) |

**Conclusion on access.** The sites that were failing for *technical* reasons
(SPA rendering, TLS) are now readable. The sites that were failing because they
actively refuse automated clients — Redbubble, Etsy, Desenio, Poster Store,
Posterlounge, King & McGaw, Surface View, AIC, MoMA — refuse a real browser too.
Going further would mean defeating their anti-bot protection, which was not
attempted. **Treat Redbubble, Etsy and Desenio as unavailable in this
environment**, not as "not found yet". The Wayback Machine is also unreachable
from here, so it is not a fallback.

---

## Juniqe (juniqe.com/uk) — verbatim

**Catalogue size, stated on the wall-art listing page: `318 775 designs`.**
This is the only hard catalogue-size figure recovered from any curated retailer
in this research, and it is a useful benchmark: a well-regarded European retailer
operates at ~319k designs, not millions.

### Wall-art nav (verbatim)
Wall Art Bestsellers · Abstract Wall Art · Nature Wall Art · Flower Wall Art ·
Animal Wall Art · Travel Wall Art · Classic Artists · Posters · Canvas Prints ·
Framed Prints · All Art Styles · Print Techniques · Van Gogh Prints ·
Kandinsky Prints · Klimt Prints · Hokusai Prints · Frida Kahlo Prints ·
Personalise Wall Art · Colin Campbell Cooper · Trending Wall Art

Note the named-artist landing pages are **all public-domain artists**
(Van Gogh d.1890, Kandinsky d.1944, Klimt d.1918, Hokusai d.1849,
Kahlo d.1954) plus one obscure one (Colin Campbell Cooper d.1937). That is the
same prompt-vs-metadata line the legal research drew, and a major retailer is
sitting exactly on the safe side of it.

### Filter facets (verbatim, after expanding every "Show all")

**Topic — 17 values, the complete list:**
Typography & Quotes · Animals · Architecture & Cities · Nature & plants ·
People & Portraits · Fiction & Fantasy · Spirituality · Space · Music & Film ·
Food & Drink · Technology & Future · sport · Vehicles · Travel & Maps ·
Children & Babies · Family · Love

**Orientation — 3:** Portrait · Landscape · Square

**Wall art size — 5 bands (note: bands, not fixed sizes):**
S (< 30 cm) · M (30–49.9 cm) · L (50–69.9 cm) · XL (70–99.9 cm) ·
XXL (from 100 cm)

**Personalisable:** No · Yes — personalisation is a first-class filter.

**Product types (16):** Wall Art · Wall Art Framed · Calendars · Apparel ·
Kids Apparel · Baby Apparel · Phone Cases · Stickers · Stationery ·
Home & Kitchen · Home Textiles · Towels · Backlit Films · PVC Banners ·
Wallpapers

**Not harvested:** the "Design color" and "Style" facets render their values
lazily and stayed empty after expansion. Those two Juniqe axes remain unknown.

### Licensed IP present
Juniqe carries **Disney, Star Wars™, Marvel, Disney Princess, Mickey** as
top-level nav items. Confirms the pattern from Displate: licensed fandom is a
large part of what sells on these sites and is exactly what cannot be generated.

### Price points observed on the listing grid
Posters from £3.95 / £4.95 / £5.95 / £6.95 / £7.95 — i.e. **the entry price for
a poster from a curated European retailer is under £8**.

---

## Fy! (iamfy.co) — verbatim nav, plus the generated-taxonomy finding

### Nav (verbatim)
- **BROWSE:** All Art Prints · Bestsellers · New In · XL Art Prints ·
  Canvas Prints · Framed Prints · On Sale
- **CURATED PICKS:** Trending Now · Editors' Picks · **William Morris Style** ·
  Japanese Art · **Art Nouveau / Klimt**
- **BY COLOUR (9):** All Colours · Green · Pink · Blue · Yellow · B&W · Warm ·
  Pastels · Red
- **STYLE TILES (11):** Maximalist · Cottage Core · Modern · Scandinavian ·
  Art Deco · Bohemian · Eclectic · Traditional · Abstract · Industrial · Coastal
- **ROOM TILES (10):** Living Room · Bedroom · Home Office · Kitchen · Hallway ·
  Bathroom · Kids' Room · Laundry Room · **Coffee Nook** · **Cloakroom**
- **TREND TILES (11):** Music · Vintage · Film · Flowers · Animals · Travel ·
  Food & Drink · Disco · Cities · Sport · Illustration · Botanical
- **GALLERY WALLS:** AI Designer · Two Print Sets · Three Print Sets
- Also: Art for Business · Art for Hotels · Style Quiz · By Mood

"William Morris Style" and "Art Nouveau / Klimt" are the naming convention worth
copying: they capture famous-name search demand without claiming to reproduce a
specific work.

### The important structural finding: Fy!'s catalogue is axis-generated

Fy!'s public `collections.json` shows their collection handles are produced by
**crossing axes**, which is the same thing this project wants to do. Observed
patterns:

| Pattern | Example handles |
|---|---|
| `{subject}-art-prints` | `abstract-`, `animals-`, `birds-`, `botanical-`, `architecture-`, `books-`, `butterfly-`, `cactus-`, `cars-`, `cats-`, `cherry-blossom-`, `beach-` |
| `{subject}-{medium}-art-prints` | `abstract-watercolor-`, `abstract-drawing-`, `abstract-illustration-`, `abstract-photography-`, `abstract-typography-`, `birds-photography-`, `botanical-drawing-` |
| `{mood}-art-prints` and `{mood}-{medium}-art-prints` | `abundant-`, `adventurous-`, `amused-`, `amusing-`, `appetizing-`, `awe-inspiring-`, `balanced-`, `bold-`, `bright-`, `calming-`, `celebratory-`, `cheerful-`, `chic-` |
| `{style}-art-prints` | `art-nouveau-`, `art-deco-`, `baroque-`, `bauhaus-`, `bohemian-`, `boho-`, `academic-`, `african-art-`, `asian-`, `80s-` |
| **`{room}-{wall position}-art-prints`** | `bathroom-above-toilet-`, `bathroom-above-bathtub-`, `bathroom-vanity-`, `bathroom-shelf-`, `bathroom-corner-`, `bathroom-entryway-`, `bathroom-feature-wall-`, `bedroom-above-bed-`, `bedroom-nightstand-`, `bedroom-dresser-`, `bedroom-reading-nook-`, `bedroom-vanity-`, `childrens-room-above-cot-`, `childrens-room-above-crib-`, `childrens-room-play-area-`, `childrens-room-reading-nook-` |
| `art-for-the-{persona}` (~200 values) | `-botanist`, `-bird-watcher`, `-cocktail-connoisseur`, `-anglophile`, `-equestrian`, `-yogi`, `-goth`, `-londoner`, `-pub-enthusiast`, `-whiskey-connoisseur`, `-marine-biologist`, `-stargazer`, `-hip-hop-fan`, `-film-buff`, `-feminist`, `-veteran` |
| `{occasion}-art-prints` | `anniversary-`, `baby-shower-`, `birthday-`, `christmas-`, `celebrations-`, `fathers-day` |
| `{colour}-art-prints` | `blue-`, `blush-pink-`, `black-and-white-`, `green-` |
| `{N}-print-{room}-gallery-wall-sets` | 2-print and 3-print × bathroom / bedroom / children's room / hallway / home office / kitchen / living room |

**The medium axis is explicit and small: drawing · illustration · photography ·
typography · watercolor · canvas-art (+ the bare form).** That is a retailer
treating medium as a primary multiplier, which is directly reusable.

**The ROOM × WALL POSITION axis is the find of this harvest.** "Bathroom above
toilet art", "bedroom nightstand art", "above cot art" are real search
behaviours with real spatial constraints (size, orientation, subject
appropriateness) — and they multiply against every subject. No other retailer in
this research exposes it.

**Junk to filter** if anyone re-enumerates: `art-lander-ad-1202517...`,
`art-lander-grid-17878...`, `b2b-test-shop`, `b2b_torro_locco`, `-copy` and
`-relevant` suffixed duplicates, and handle/title mismatches (several
`2-print-bedroom-...-copy` handles carry a *Bathroom* title — their generator has
drifted).

---

## Saatchi Art (saatchiart.com/prints) — verbatim filter facets

- **MATERIAL (5):** Fine Art Paper · Canvas · Acrylic · Metal · Photo Paper
- **SIZE (4):** Small (<20 in) · Medium (20–40 in) · Large (40–45 in) ·
  Oversized (>45 in) — **imperial, US-facing**
- **ORIENTATION (3):** Vertical · Horizontal · Square
- **STYLE (6 shown, more behind "SHOW MORE"):** Abstract · Modernism ·
  Contemporary · Minimalism · Expressionism · Impressionism
- **SUBJECT (6 shown, more behind "SHOW MORE"):** Floral · Fashion · Landscape ·
  Abstract · Travel · Food & Drink
- Also faceted on: ORIGINAL MEDIUM · COLOR · ARTIST COUNTRY · FEATURED IN

Pricing starts "From $40", and listings advertise **"Available in 5 sizes, 4
materials"** — i.e. Saatchi also puts the size/material matrix *inside one
listing*, not across listings. Third independent retailer doing this.

---

## Abstract House (abstracthouse.com) — collection list

`abstract-art-prints` · `art-prints` · `bestseller` · `black-white-art-prints` ·
`blue-wall-art` · `botanical-art-prints` · `bright-and-colourful-wall-art` ·
`brown-wall-art` · `canvas-prints` · `cityscape` · `curated-picks` ·
`figurative-art` · `fine-art-photography` · `gallery-wall-art` ·
`geometric-wall-art` · `green-wall-art` · `landscape-photography` ·
`large-canvas-prints` · `limited-edition-prints` · `neutral-art-prints` ·
`new-arrivals` · `original-art` · `red-wall-art` · `set-of-three-prints` ·
`yellow-wall-art`

Colour axis (6): blue · brown · green · red · yellow · black & white, plus
"neutral" and "bright and colourful" as moods. Named pages for `art-by-colour`
and `art-by-room`. Prices are **USD and high** ($193–$292 for a print, $400+ for
canvas, originals $627–$5,185) — this is a gallery, not a commodity seller, and
is **not** a pricing comparable.

---

## Gaps this harvest leaves open

- **Redbubble, Etsy, Desenio, Poster Store, Posterlounge, King & McGaw, Surface
  View, AIC, MoMA Design Store: unavailable.** Not "unsearched" — they refuse
  automated clients, and the Wayback Machine is unreachable from here.
- **Juniqe's Design color and Style facet values** — lazily rendered, not captured.
- **No numeric popularity signals** on any site read here: no review counts, no
  star ratings, no sold counts. Juniqe and Fy! render those client-side or not at
  all. The weighting-by-sales part of the brief cannot be satisfied from these
  sources; the usable proxies are nav prominence, the existence of a dedicated
  collection, and repetition across retailers.
