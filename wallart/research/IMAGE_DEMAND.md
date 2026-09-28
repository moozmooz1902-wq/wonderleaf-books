# Image wall art on eBay UK: what actually sells

Research date: **28 Sep 2026**. This is the image-print companion to `DEMAND.md`, which covers typography.
Machine-readable table: `image_themes.json` (83 theme x style rows, 22 top sellers, 3 contrast sellers).
Raw pages and scripts are in `raw/image/` (gitignored).

## How the numbers were collected

- **What was fetched:** eBay UK active-listing search pages, Best Match order, 240 per page, with curl. That covered
  435 search terms, 1,200 result pages and 55 seller pages, for **133,279 unique print-like listings**.
- **What "sold" means:** eBay's lifetime "X sold" counter. It only appears on multi-quantity listings. It is not a
  90-day figure, and "275+" style values are floors. The sold filter needs a sign-in, so no sell-through rates.
- **How rare sales are:** only **1,868 image listings (1.4%)** show any sold counter; 838 show 50 or more.
- **Exclusions:** personalised and word-art listings (covered in `DEMAND.md`), and print services such as "your
  photo on canvas".
- All numbers are measured. Image style labels are a visual read of 96 thumbnails.

## Executive summary

1. **The biggest image market is educational wall charts.**
   - Multiplication square 6,002 sold; girls' times tables 5,081; times tables 4,130; alphabet 2,970;
     number square 2,645. All at **£3.69**.
   - A3 laminated times tables 3,224; periodic table 1,686 / 747 / 719; GB & Ireland A1 map 2,080; world maps
     1,782 / 1,650 / 1,028 / 1,003.
   - All of these can be **generated from data or layout**, with no AI and no copyright problem.
2. **The décor formula that works: a plain photographic subject on white, A4 unframed, one price of £3.99.**
   The seller is `grabbanicepair_ltd`, with 1,100 listings:
   - palm leaf 1,002 / 617 / 503
   - giraffe with flower garland 873; elephant with garland 445
   - highland cow on the toilet 369; monkey on the toilet 313
   - tiger 253, zebra pair 244
3. **Public-domain vintage art sells when it has a hook.**
   - Dictionary-page prints (`in-the-frame-shop`): stag 489, Alice 463, peacock 392, fox in clothes 342, all at £5.99.
   - Vintage racing, travel and propaganda posters: 100–430 each at £3.60–£6.44.
   - Plain museum reproductions sell little: Monet 46, Last Supper 62.
4. **These styles showed zero page-1 sales:** "vogue" animals, animal and botanical line art, "vintage botanical
   print", mid-century, Bauhaus, japandi, "geometric print" (830,000 results) and "pop art animal".
5. **Winners are small catalogues of multi-quantity listings**: 64, 714, 1,100 and 1,500 listings.
   - `bigboxart`: 89,000 AI-look framed listings, **0 of its top 240 show a sold counter**.
   - `canvasartshop`: 11,000 listings, 16 of 240 selling.
   - `artscape_galleries`: 9,000 listings, 178 of 240 selling, but every item is a known vintage design.
6. **Cheap sells.** Listings with 50+ sold have a median price of **£5.97**; listings with no sales, **£11.99**.
   Store 1's mean is £10.09.

## Why store 1 doesn't sell

| | Store 1 | Sellers that sell |
|---|---|---|
| Quantity | **Qty 1 on 669,114 of 669,137 listings** | Multi-quantity, good-til-cancelled; one item number builds up hundreds to thousands of sales and its search rank. A qty-1 listing can never show a sold counter. |
| Catalogue | 424k listings; 45k distinct titles; 3,122 subjects | 17–5,800 listings with high sell-through |
| Why the subject exists | A subject x style x palette grid | Each answers a job or search: a chart, a map, a joke, a known vintage poster |
| Price | Mean £10.09 | Median £5.97; £3.69–£5.99 for the volume leaders |
| Title | Leads with style and palette words | Subject first, then plain product words: PRINT, PICTURE, POSTER, A4, UNFRAMED |

**Category, measured:** for the same terms, **Art Prints (360)** has far more competing listings than
**Decorative Posters & Prints (41511)**: 60.1M against 4.7M results over 329 terms. The share of listings with sales
is the same in both (1.41% against 1.42%). The one winner checked (highland cow bathroom set) is in 41511.

## What the winners do

| Feature | 50+ sold listings | No sold counter |
|---|---|---|
| Median price | **£5.97** | £11.99 |
| Price range (variations) | 36% | 57% |
| "A4" / "A3" in title | **38% / 22%** | 15% / 7% |
| "Unframed" | **17%** | 4% |
| "Picture" | **33%** | 17% |
| "Canvas" | 12% | **27%** |
| "Framed" | 4% | **19%** |
| Free delivery | **76%** | 52% |

- **Variations are not the winning ingredient.** Where they work, it's a size ladder with a very low entry price
  shown in search (`blackheartprints` A5–A1 from £2.99). The top image sellers sell one size at one price.
- **Room mockups** are standard on the non-selling big catalogues too, so they don't create demand.
- **Sets** help only in nursery and bathroom niches.
- **Title formulas that sell:**
  - `giraffe print PICTURE flower garland WALL ART A4 unframed 22 pink` (873)
  - `Funny bathroom highland cow on toilet Print Picture Poster Unframe A4` (369)
  - `SUMBOX EDUCATIONAL NUMBER SQUARE MATHS POSTER WALL CHART COUNT 1 - 100 TEACHING` (2,645)

## The 15 best bets

| # | Theme x style | Evidence (sold) | Price | Production |
|---|---|---|---|---|
| 1 | Educational charts: times tables, number squares, alphabet, phonics, time, shapes | 6002, 5081, 4130, 3224, 2970, 2645 | £3.69–£5.99 | procedural |
| 2 | World maps: political with flags, kids' animal map | 1782, 1650, 1028, 1003, 578, 323 | £7.99–£22.64 | procedural |
| 3 | Photo animals on the toilet or in the bath | 369, 313, 282, 178, 152 | £3.99 | AI |
| 4 | Tropical leaf photos | 1002, 617, 503 | £3.99 | AI or stock photo |
| 5 | Photo animals with a flower garland or crown | 873, 445, 343, 253, 237 | £3.99 | AI |
| 6 | Science charts: periodic table, skeleton, solar system | 1686, 860, 747, 719 | £3.69–£15.99 | procedural / public domain |
| 7 | Dictionary-page prints (dressed animals, Alice, birds) | 489, 463, 392, 342 | £5.99 | public domain |
| 8 | UK, Ireland and country maps; UK counties | 2080, 497, 180, 171 | £5.76–£7.89 | procedural |
| 9 | Nursery safari animals, single and set of 3 | 241, 232, 188, 175 | £3.99 / £9.99 | AI |
| 10 | Vintage-style world travel posters | 344, 288, 220, 219 | £3.93–£12.64 | public domain + new |
| 11 | Vintage motor racing and cycling (no brands) | 427, 208, 184, 135 | £3.60–£6.44 | public domain + new |
| 12 | UK railway-style town posters | 123, 91, 84, 74 | £4.23–£6.29 | new designs |
| 13 | Public-domain masters (Van Gogh, Klimt, Hokusai, Mucha) | 377, 176, 130, 126 | £3.85–£14.99 | public domain |
| 14 | Black-and-white animal photo pairs | 309, 244, 169, 161 | £3.99 | AI or stock |
| 15 | Vintage advertising and propaganda (no live brands) | 162, 142, 109, 100 | £4.92–£6.44 | public domain |

**Do not mass-produce:**
- "vogue" animals, line art, boho, mid-century, Bauhaus, japandi and plain landscapes (zero or near-zero sales)
- species-only "{animal} print" without a format hook
- anything that depends on film, club, band, brand or living-artist IP (Banksy, Vettriano, Lowry, Wrendale,
  Disney, Marvel)

## Seasonality

Image prints are mainly evergreen.
- **Christmas:** image prints (hot chocolate station, gonks, festive robin and highland cow) need to be live by
  mid-October.
- **Mother's Day:** "mummy and baby" animal pairs before Mothering Sunday.
- **Back to school:** educational charts should be stocked by August–September.

## Risks

- **UK copyright** lasts 70 years from the artist's death.
  - Public domain in 2026: Van Gogh, Monet, Klimt, Hokusai, Hiroshige, Mucha, Morris, Tenniel, Kandinsky, Mondrian,
    Matisse.
  - Not public domain: Picasso, Dalí, Hopper, Lowry, Vettriano, Banksy, and many 1930s–50s railway poster artists.
- **Trade marks:** Peter Rabbit, Frida Kahlo, car makers, and brand names in vintage adverts.
- **Map data:** Natural Earth is public domain; OS OpenData and OpenStreetMap need attribution.
- **Duplicates:** eBay's duplicate rule also covers identical items sold under different user IDs.
