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

## Phrase quality: what was wrong and what was done

### Nonsense a buyer would spot

Two template faults were producing wrong prints at scale, and both were
found by drawing forty phrases at random from the finished catalogue and
reading them rather than by any test:

**Nursery prints with a 1950s birth year.** `{name} / born {year}` used the
general year pool, which runs back to 1950. "Ronan born 1987" on a nursery
print is nobody's purchase. Nursery templates now use `{byear}`, the last
fourteen years.

**Anniversaries that contradicted themselves.** The anniversary name IS a
number of years - Paper is the 1st, Silver the 25th - but the name and the
year were filled from separate pools, so the catalogue contained "Mr & Mrs
Wong Paper anniversary 1986" (a 40th) and "Paper anniversary 1952" (a 74th).
`{annivy}` now carries the year the name implies, derived from the current
year at generation time so it does not go stale.

Also: "Vintage 2024" and "Legend since 2025" are not a thing, so anything
claiming age uses `{vyear}`, which starts eighteen years back.

Those three fixes removed about 78,000 listings. Every one of them was wrong.

### The phrases written for the thin niches

2,311 phrases were written for the thirteen thin niches in one sitting, and
**49% of them began with a word from the end of the line before**:

    "Wash your hands"        -> "Hands washed properly"
    "Hands washed properly"  -> "Properly twenty seconds"
    "Take the long way"      -> "Long way round"

That is chaining, which produces volume quickly and is not how you write
something somebody wants on their wall. All 1,118 chain links were removed,
the originals left untouched, and the gaps filled with phrases written to
stand on their own. Duplicates were removed and American spelling corrected
- this catalogue sells in the UK, so "Mom's laundry service" was wrong.

Two earlier attempts to automate this judgement are recorded in
`sellable.py`, both wrong in ways worth not repeating: counting search words
in the phrase (they belong in the title), and a growing pile of regexes that
ended up cutting "WC", "Loo" and "Please flush", which are among the best
selling bathroom prints there are.

## No duplicates: what is guaranteed and what is not

Checked on the generated catalogue, not asserted:

    2,293,671 listings
            0 duplicate SKUs
            0 duplicate titles inside any one store
          253 repeated designs (0.011%)
      157,000 titles shared across DIFFERENT stores

The last line is the honest caveat. The four stores are four eBay accounts,
so a repeated title is not two listings competing inside one shop - but they
do meet each other in eBay search. Removing it entirely would mean one
global title index across all four, which costs about 150,000 more listings.

### Why titles were repeating, and what gave way

A title is 80 characters and has to carry the phrase, the niche keyword, the
seller's tail (Framed, Poster, Gift) and ideally a differentiator. `fit()`
trimmed the PHRASE first to make room, which is exactly backwards: the
phrase is the only part that makes one listing different from the next.

    "The {surname} family together since {year}"

is 77 distinct phrases. The year fell off the end and all 77 became "The
Poole Family Together Since Sign Art Print Wall Decor Framed Poster Gift" -
74 of them in one store. "Proud to be from {town}" lost the town the same
way, and 144 listings came out as "Proud to Be from Town Typography Wall
Art Print".

The budget now goes: the phrase first and never cut below 62 characters,
then the seller's tail, then the niche keyword (in a shorter form if the
full one will not fit, because that is how the listing is FOUND), then
colour and room, then the paper sizes. That took repeated titles from 16.5%
to 12.6%.

The rest cannot be fixed inside 80 characters - 48 colourways of "Everything
Stops for Tea" have nowhere to put the colour - so a title that is already
used in that store is not listed at all. 153,943 rows were dropped that way,
which is where 2.5M became 2.29M. Every one of them was a listing that would
have competed with one of its own siblings.

## How 3,989 typed lines become 2.29 million listings

Worth setting out plainly, because the ratio looks impossible.

    1. A person types 3,989 lines into banks/niches/.
       3,699 are plain phrases. 290 contain a {slot}.

    2. A slot draws from a list: 368 surnames, 2,317 UK towns, 516 first
       names, 77 years, 67 counties, 60 dog breeds, 40 professions.

    3. One template is therefore many phrases:
         "The {surname} family est. {year}"  =  368 x 77  =  28,336

    4. 290 templates expand to 878,232 distinct phrases.

    5. Each phrase is drawn an average of 2.6 ways - a different colourway,
       font, layout or ornament, aimed at a different room.

       878,232 x 2.6  =  2,293,671 listings

The important number in that chain is **878,232**, not 2.29M. That is how
many listings carry genuinely different WORDS. The 2.6 multiplier is the
same words drawn differently, which is a real choice a buyer makes - people
search "sage green kitchen print" - but it is not new content.

### What that means commercially

This is a long tail, not a broad one. "The Okafor Family Est. 1998" sells to
the Okafors and nobody else, so 878,232 phrases are 878,232 very
low-frequency searches. Each listing sells rarely; the volume is the
business model, and it is the same one the collaborator's live catalogue
runs on.

Two things follow that the seller should decide on, not me:

- **eBay insertion fees.** 2.29M listings across four accounts is about
  573,000 each, far beyond any free allowance. That is a real monthly cost
  and it should be checked against each account's allowance before the
  first upload.
- **A smaller, denser catalogue is a legitimate alternative.** Listing the
  best 100,000 rather than all 2.29M would cost a fraction and lose only the
  rarest tail.
