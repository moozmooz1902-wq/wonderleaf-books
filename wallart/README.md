# Wall art catalogue generator: typography prints for 7 stores

Typography wall art (quotes, signs, scripture, personalised names), drawn as
flat vector-style artwork with no AI images and no image storage. One command builds
the listing catalogue for all seven stores, and one small server draws any
listing picture on request.

## What is here

| File | What it does |
|---|---|
| `banks/niches/*.txt` | 42 hand-written phrase banks, one per niche (kitchen, café, car showroom, faith, nursery, ...). Plain text, edit freely. |
| `banks/slots/*.txt` | Values that fill `{slot}` templates: 516 first names, 369 surnames, 2,326 UK towns, 60 dog breeds, 60 hobbies, 40 jobs... |
| `banks/audiences.txt` | 329 micro-niche audiences and venues for the AI phrase expansion |
| `phrases.py` | Expands banks and templates into unique phrases; adds ~690 public-domain Bible verses (World English Bible, British Edition) |
| `styles.py` | 26 named colourways, 28 font pairings, 10 layouts, ornament choices per niche |
| `render.py` | Draws a design at any size: ~6 ms at listing size, 0.45 s for an A3 print at 300 dpi |
| `generate.py` + `plan.json` | Builds `out/store{1..7}.csv.gz`: one row per listing with SKU, phrase, style, venue, 80-char title and image path |
| `serve.py` | On-demand image server: listing photo, wall mockup and print file, all from the URL |
| `expand_phrases.py` | Has Claude write ~95k new phrases for 1,183 micro-niches via the Batch API |
| `fetch_assets.py` | Downloads the free fonts (OFL/Apache) and the scripture text |

## The stores (plan.json)

One Cloudflare R2 bucket per eBay account. 65% of each store's listings come
from its own markets and 35% are spread across everything else. No design
(phrase, venue and colour) appears in two stores.

| Bucket | Listings | Markets |
|---|---|---|
| `luxvia-art` | 1,000,000 | family and surname signs, home, wedding, new home, birthdays and anniversaries, UK towns, Christmas |
| `mercury-usm` | 500,000 | kitchen, café, bar and pub, restaurants and shops, bathroom, laundry, garden, man cave, hobbies, pets, humour, dialect |
| `lunar-kms` | 500,000 | nursery and kids, classroom and school, faith and scripture, memorial, thank-you gifts |
| `posterleaf-store1` | 500,000 | motivation, office and business venues (car showrooms, gyms, salons, clinics), words, classic quotes, coastal |

Every design prints as black or one dark colour on a **white background**, to
keep ink costs down. Every listing offers **A4, A3 and A2**, each **Unframed or
in a Black Frame** (six variations, prices in `plan.json`).

## From catalogue to eBay

```bash
python3 generate.py                  # out/<bucket>.csv.gz, 2.5M designs (~5 min)
python3 build_ebay.py                # out/ebay/<bucket>/*.csv + one zip per store
python3 build_ebay.py --check        # structure check of every file
python3 publish.py --store 1 --bucket luxvia-art        # render + upload images to R2
```

Before uploading to eBay, fill these in `plan.json`:
- `stores[].pic_base`: the bucket's public URL (Cloudflare -> R2 -> bucket -> Settings -> Public access)
- `ebay.profiles`: shipping, returns and payment policy names, exactly as they appear in each eBay account
- `ebay.prices` and `ebay.quantity`

Images go to `art/mock/<SKU>.jpg` (unframed), `art/mock/<SKU>_framed.jpg` (black frame)
and `art/raw/<SKU>.png` (A3 print file, 300 dpi). That is the layout the existing
`order.py` / `print_tool.py` already read, so fulfilment works unchanged. Add the
four buckets' public URLs to `sources.json`.

See `COMPLIANCE.md` for the IP / VeRO rules every phrase and title passes.

## Rules that keep it from becoming duplicate spam

Store 1's 424k wall-art listings are 89% near-duplicates, which is the likeliest
reason they don't sell. So:

- No two rows anywhere share the same phrase, venue and colourway.
- Every unique phrase is used before any phrase gets a second version.
- A hand-written phrase can appear in up to 4 colourways per venue. "Dream big"
  becomes separate office, gym, classroom and car showroom listings, each a different
  buyer search.
- A personalised phrase ("The Smith Family Est. 1998") appears at most 3 times.
- No single template produces more than 40,000 phrases, and couple-name prints
  are capped at 400k listings.
- Overflow stays on-theme. If a store's own niches are full, the store is smaller
  rather than padded with other stores' stock.

## Where it stands now

With the hand-written banks, those rules allow **2.7M listings**, not 7M. The
generic niches (motivation, business venues, café) have 40–140 phrases each and
fill up first. Most of the gap is closed by the AI expansion below.

## How to run

```bash
pip install pillow anthropic
python3 fetch_assets.py                  # fonts + scripture, once
python3 generate.py --plan-only          # see the allocation
python3 generate.py                      # write out/store1..7.csv.gz (~2.5 min)
python3 render.py "But first, / *coffee*" --palette sage --orn cup --out test.png
python3 serve.py --port 8080             # image server
```

### Growing to 7M: AI phrase expansion (needs an API key)

1. Add `ANTHROPIC_API_KEY` as an environment variable in the Claude Code
   environment settings. Then start a new session so it takes effect.
2. `python3 expand_phrases.py plan` shows every micro-niche and the cost estimate
   (Haiku 4.5 ≈ $5, Sonnet 5 ≈ $11, Opus 5 ≈ $26 at batch prices).
3. `python3 expand_phrases.py submit --limit 20`: try 20 first and read the output.
4. `python3 expand_phrases.py submit`, then an hour later `collect`.
5. `python3 generate.py` picks up `banks/niches_ai/` automatically.

## Images: no storage

`img_path` encodes the design, e.g. `/m/sage/classic_serif/stack/cup/<phrase>.jpg`.
Run `serve.py` on a small VPS behind a free Cloudflare cache, and set each
listing's picture URL to `https://<your-domain>` + `img_path`. eBay copies each
picture once when the listing goes live, so each image is drawn about once.
Print files come from `/p/A4/...` when an order arrives.

## Still to build

- The eBay File Exchange upload file (size variations A5/A4/A3, prices, item
  specifics, shipping profiles), built from these CSVs.
- The order-to-print step (fetch `/p/<size>/...` for each sold SKU).

## Image sizes are an interface, not a detail

The seller's team runs a tool over the listing photos that finds the black
frame and crops away the rest. The canvas size and the frame's position
inside it are therefore depended on by other people's software.

Everything already in the seller's buckets is 2000 x 2000 - checked on 14
photos drawn at random from a real listing of a bucket, not from memory of
what was built - so that is what `LISTING_PX` is set to, and `publish.py`
and `serve.py` both take it from there rather than each passing a number.

    listing photo  2000 x 2000 JPEG on #EDE9E3
    frame box      (406, 160, 1593, 1840)   = 1187 x 1680
    print area     1105 x 1598 inside the moulding
    A4 print file  2480 x 3507 PNG at 300 dpi
    A3 print file  3508 x 4961
    A2 print file  4961 x 7015

`python3 size_contract.py` asserts all of it and fails loudly if any of it
moves. Run it after touching `render.py`, `publish.py` or `serve.py`.

## Titles: the search words go at the end and are never trimmed

The seller puts the same words at the end of every title. `fit()` filled
left to right and ran out of characters before reaching them, so "Framed"
was landing on 7% of titles and "Poster" on 11%. It now reserves that tail
before the optional middle - venue, colour, paper sizes - so:

    Poster   11.5% -> 100%
    Framed    7.1% -> 100%
    Gift     52.3% -> 100%

still with nothing over 80 characters, median 77. The cost is the paper
sizes, which fall from 50% to 17% of titles; they are a listing variation
anyway, and "poster" appears 912 times in the eBay search-box research
against 75 for "a4".

"Bold" is in the list at the seller's request but is **off by default**
(`BOLD = False` in `generate.py`). It appears zero times across the 303
researched search terms, so it would spend five characters of every title on
a word nobody types. Set it True to put it back.

## Ink: about half black, the rest colour

`palette_order()` draws each slot black with probability `BLACK_SHARE`
(0.5). Measured on the generated catalogue: 51% of listings on the black
cartridge alone, 50% at every variant position, with the rest spread across
navy, gold, blush, burnt orange, sage, mustard, brown and rainbow.

The white ground is what saves the ink. A dark colour on it costs barely
more than black, and the palette name goes in the title because decor buyers
search it.
