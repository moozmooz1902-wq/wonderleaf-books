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

Each store puts 65% of its rows into its own market and spreads 35% across
everything else. That way no store depends on one niche, and every store tests
demand across all niches.

1. Faith & Blessings: Christian, scripture, Irish blessings, Islamic, Hindu/Sikh, memorial
2. Business & Motivation: offices, car showrooms, gyms, salons, barbers, clinics, motivation
3. Food, Drink & Hospitality: kitchen, café, pub/bar, restaurants, hotels, shops
4. Family, Wedding & Home: family name signs, weddings, new home, bathroom, laundry
5. Kids, Nursery & School: nursery names, classrooms, schools, libraries
6. Humour, Hobbies & Pets: man cave, garage, hobbies, dog breeds, garden, dialect
7. Gifts, Places & Seasons: birthdays, anniversaries, UK towns, Christmas, coastal

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
