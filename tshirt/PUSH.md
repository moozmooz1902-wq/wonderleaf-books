# What to upload, and in what order

Everything below is finished and verified. Nothing here needs a terminal.

## Order of operations

The account is at its selling limit, so listings have to come off before the
new ones go on. End first, then test small, then upload.

1. **`EBAY_END_TEST_50.csv`** - fifty ends, to confirm the End template.
2. **`EBAY_END_TSHIRTS.csv`** - 125,966 ends, one file. T-shirts only; no
   wall art. *(Uploaded 2026-10-07.)*
3. **`EBAY_TEST_3.csv`** - three listings. Cheapest possible check that the
   variation set is accepted.
4. **`EBAY_TEST_50.csv`** - fifty listings. Check in Seller Hub that all five
   sizes came through, the photo shows, the price is £11.99 and each size
   shows 1 available.
5. **`EBAY_ONE_FILE.zip`** - the whole catalogue as one file.

### Error 21919053, and the fix

The first test upload failed on all fifty rows with:

    VariationSpecificsSet container (Item.Variations.VariationSpecificsSet)
    is required to list a Multi-SKU item.

The seller then supplied a file that **had uploaded successfully**, and
comparing the two field by field found six differences. The first attempt at a
fix put the variation set in the wrong place - pipe-separated in `C:Size` -
when the working file declares it on the **parent's `RelationshipDetails`**,
semicolon-separated. All six are now matched:

| | working file | ours before | ours now |
|---|---|---|---|
| parent `RelationshipDetails` | `Size=S;M;L;XL;2XL` | blank | `Size=S;M;L;XL;2XL` |
| parent `C:Size` | blank | the pipe list | blank |
| size labels | `S M L XL 2XL` | `Small ... XX-Large` | `S M L XL 2XL` |
| variation `*Category` / `*ConditionID` / `*Title` | repeated | blank | repeated |
| variation `CustomLabel` | blank | `WLT-nnnnnn-S` | blank |
| `*Location` | `Manchester` | `United Kingdom` | `Manchester` |

Dropping the per-variation SKU is right rather than merely matching: an order
then reports the **parent** custom label, which is exactly what the fulfilment
tool resolves `art/raw/<label>.png` and `art/mock/<label>.jpg` from.

**One deliberate difference remains.** The working file uses postage policy
`1`; ours uses `2`, because the seller said the postage policy on this account
is 2. If a test comes back with a business-policy error, that is the field to
flip, and nothing else about the structure is in doubt.

Also worth noting for later: the working file's own titles read
`... Mens Womens T-Shirt Funny Novelty Gift Tee Top`, so eBay accepts that
shape. Ours follow the hot sellers' shape instead, on the seller's
instruction - see above.

## The end file

`EBAY_END_TSHIRTS.csv` - **one file**, 125,966 rows, `End` / `NotAvailable`.
`EBAY_END_TEST_50.csv` is the same thing cut to 50 rows to test the template.

    125,966 t-shirt listings ended   (upload 115,966 + 10,000 spare)
    118,872 t-shirts left live
          0 wall art touched - Art Prints (360) is untouched

Chosen worst-first, in two passes, and the file is **written in that order**:

    86,770  duplicate titles already live against each other. The 244,816
            live GR- t-shirts carry only 158,046 distinct titles, so a third
            of that catalogue is competing with itself. One copy of each
            title is kept; the older copies are ended.
    39,196  longest-listed of the remainder (lowest item number first), as
            the only available proxy for "has been up longest and still has
            not converted". The downloaded file carries no sales data.

Because the order is worst-first, the file can simply be **truncated** to end
fewer. Keep the header and the first N rows and the ends stay the worst N.
Everything down to row 86,770 is removing a duplicate of a listing that stays
live, so nothing unique comes off until past that point.

Held back and never ended: the 22 t-shirts whose SKU is not `GR-#######`
(the `hb_`, `oc_`, `br_` batch, the 40 that carry variations, and the 7 at
quantity 10). They look like a separate, more deliberate set.

`EBAY_END_MANIFEST.csv` lists every ended item with its SKU, title and the
reason, for the record.

## The upload file

**`EBAY_ONE_FILE.zip`** - one eBay File Exchange CSV, zipped.

    105,573 listings
    527,865 size variations, exactly 5 per listing, no orphans
    633,438 data rows, 30 columns
    £11.99, quantity 1 per size, category 15687, United Kingdom
    business policies: shipping 2, returns 1, payment 1
    every listing has a PicURL and a print master in the bucket

Built by joining the eight `EBAY_part0*.csv` files, whose headers are
byte-identical and which were split on listing boundaries. The joined file
was re-parsed after every change and checked, not assumed: every listing has
exactly five variations, no orphan variations, nothing missing `C:Size`,
nothing missing `PicURL`, no title over 80 characters, and every description
heading matching its title.

### Titles are the text printed on the shirt, and nothing describing it

**A real defect, found by the seller.** One listing was titled "Music Raising
My Husband Is Exhausting Light Band T-Shirt Mens Music Tee Top" while the shirt
reads "THIS IS WHAT AN AWESOME HUSBAND LOOKS LIKE".

The cause: this catalogue replicates a competitor's hot sellers, and each row
kept their `original_title` - here *"Raising My Husband Is Exhausting Mens
Light Cotton T-Shirt"* - from which `subject` was derived as
`RAISING HUSBAND LIGHT`. The printed design comes from a **separate** template
bank, `THIS IS WHAT AN AWESOME {N} LOOKS LIKE`, landing in `slogan`.
`render_illus.py` line 108 draws `row["slogan"]`, so **the slogan is the
product**, and the title was being built from the competitor's words instead.
The two were never tied together.

The rule now:

    {slogan, in full} T-Shirt Mens [Funny|theme] [Tee] [Top]

and **nothing that merely describes the design**. 80 characters is the scarce
resource and a buyer reads the wording off the title, so subject,
illustration and palette words are out. They moved into the description, which
now opens its **This design** block with `Printed wording: "<slogan>"` and
carries the style, layout, colourway, illustration and a `Theme:` keyword list.

    shirt: THIS IS WHAT AN AWESOME HUSBAND LOOKS LIKE
    title: This Is What An Awesome Husband Looks Like T-Shirt Mens Music Tee Top

    shirt: TRUST ME I'M A GRANDPA
    title: Trust Me I'm A Grandpa T-Shirt Mens Family Tee Top

    shirt: WEEKEND FORECAST FEELING WITH A CHANCE OF DRINKING
    title: Weekend Forecast Feeling With A Chance Of Drinking T-Shirt Mens Beer Tee Top

**105,536 of 105,573 titles (100.0%) open with the COMPLETE printed slogan.**
Mean length 50.7 against the hot sellers' 61.2. Three earlier attempts are
recorded here so they are not repeated:

- Building the head from the competitor's title - the original bug.
- Trimming a long slogan from the end, which produced *"This Is What An
  Awesome T-Shirt Mens..."*. The full slogan is now tried before anything is
  shortened, and when it truly cannot fit the niche noun is kept.
- Adding describing words to every title, which is what the seller caught
  second: *"...Husband Looks Like T-Shirt Mens Raising Light Woman Tee"*.

### Theme words are only used when the design corroborates them

The source `theme` field is a loose bucket, not a reliable label, and trusting
it put wrong keywords in titles - the one the seller spotted was
*"I Work Hard So I Can Keep Skydiving T-Shirt Mens **Fishing** Tee Top"*.

`fishing2` turns out to hold scuba, camping, skydiving, caravan, sailing and
kayaking, so it is now **Outdoors**, not Fishing. But the wider problem is that
every bucket carries stragglers: `music` holds HUSBAND, `gym` holds UNION,
`patriotic` holds VIKING, `Birthday` was applied to *"PEACE LOVE DAUGHTER"*,
`Football` to *"I LOVE UNION"*, `Christmas` to *"PEACE LOVE SLICE"* (a pizza).

So a theme word is now emitted **only when the design corroborates it**: the
word, or one of a hand-written synonym set, must appear in the slogan, niche,
subject or illustration. `Funny` is exempt, being a tone rather than a claim
about the subject. **35,253 theme words were suppressed on that test**, led by
Birthday (7,318), Football (6,561), Christmas (5,448) and Geek (4,337). A
shorter honest title beats a keyword that misdescribes the shirt.

### The cost of slogan-led titles, and what was done about it

Slogans repeat: 26,468 distinct across the catalogue, one of them 96 times. A
title that is only the slogan plus garment keywords therefore collides a lot -
**78,543 of 115,966 would have been duplicates**. Rather than lose two thirds
of the catalogue, a distinguishing noun is appended **only where a title would
otherwise clash**, so the clutter lands on the duplicates and never on a title
that did not need it. Suppressing uncorroborated theme words removes a
differentiator too, so the residue grew from 9,128 to 10,393; those redundant
copies were dropped on the seller's standing instruction.

    115,966  listings built
    -10,393  redundant copies of a title that still collided
    =105,573 listings, zero duplicate titles

### 545 old near-duplicate pairs dropped

Before the rebuild, 545 pairs differed only by `T-Shirt` versus `T Shirt`.
Only 2 of the 545 shared both slogan and illustration - the rest were
genuinely different designs that collided on title text - but one of each pair
was dropped on the seller's instruction, safe over sorry. 115,966 down to
**115,421**.

### Every description now says what makes the design different

Two listings can share a theme - two different Happy Birthday shirts - and the
photo and print file already differ. Each description now carries a
**This design** block naming the drawing style, the layout, the colourway and
the illustration subject, taken from the catalogue's own design record, so
there is something concrete to tell them apart by:

    This design
    Line art, wording above the illustration in a mono bone colourway.
    Illustration: anime girl sitting next to a car. Printed for this listing
    only - each of our designs is drawn separately, so the artwork, wording
    and colours differ from listing to listing.

`EBAY_PARTS_CLEAN.zip` (the eight parts) is still here and is the same data
if File Exchange rejects the single file for size.

## Headroom arithmetic

On a **listing** count the upload lands below where the account sits now,
with the 10,000 spare slots asked for:

    live now          668,956 listings   (424,118 wall art + 244,838 tees)
    after the ends    542,990 listings
    after the upload  648,563 listings   - 20,393 fewer than today

On an **item** count it also fits, and that is what the quantity choice is
for. The file carries **quantity 1 on each of the five sizes**, matching
everything else on the account, so a listing is five items rather than
twenty-five:

    live now          about   669,281 items
    after the ends    about   543,315 items
    new upload                527,865 items
    account after           1,071,180 items

At quantity 5 the same upload would have asked for **2,899,150 items**, about
five times what the account holds today, while 125,966 ends free only about
125,966 items. Quantity 1 is what keeps the item count in range.

If it turns out fewer listings can go up than the file holds, split the
upload rather than ending more - 118,872 live t-shirts are still selling and
are worth more than empty headroom.

## What is in the bucket

    art/mock/WLT-######.jpg   listing photo, 2000 x 2000
    art/raw/WLT-######.png    print master, transparent, 300 dpi, 2600px wide

Both are the paths the fulfilment tool resolves a custom label to, so an
order looks up its own artwork with no extra step.

**Verified against the live bucket on 2026-10-07**, not from memory:
all 105,573 custom labels in the upload file resolve to both
`art/mock/<label>.jpg` and `art/raw/<label>.png` in `tshirt-m12k`. Zero
missing on either side. `art/mock/` holds 116,355 WLT objects - the 389
extra are the trademark and likeness listings that were pulled, correctly
absent from the file. Six photos drawn across the catalogue were 2000 x 2000
and six masters were transparent at 2600px wide.

The print masters are flat spot colour with hard edges - 5 to 7 inks, no
semi-transparent pixels anywhere - because the transfers are DTF and DTF
cannot hold a gradient or a soft edge.

The bucket also holds about 1.45 million objects under the same two prefixes
with numeric names. Those are not from this catalogue and nothing here has
touched them.

## What changed in the artwork

13,313 listings (11%) carry a real illustration above the slogan, recoloured
into each listing's own palette. The other 103,000 are type-only, which is
the format their own data rates highest. The SKUs did not change, so the
eBay file is unaffected either way.

---

## Why the upload stopped at ~20,000 (10 October 2026)

**It is the monthly VALUE limit, not the quantity limit.** From the seller's
Seller Hub screen:

| limit | used | state |
|---|---|---|
| Quantity of items | 731,773 / 10,000,000 | **9.3M spare — only 7.3% used** |
| Money value | **£10.2M / £10M** | **exceeded** |

So the account has essentially unlimited item headroom and no value headroom.
Ending listings to free *item* space was solving the wrong constraint.

### The arithmetic

Listed value is price x quantity x sizes, and every listing in this catalogue
carries five sizes at quantity 1:

    per listing      5 x 1 x £11.99        = £59.95
    20,000 uploaded                        = £1.20M
    85,573 remaining                       = £5.13M
    getting back under the cap             = £0.20M
    headroom needed to finish              = £5.33M  = 53% of the whole £10M limit

Finishing this upload by ending alone means clearing **more than half the
account's total allowance by value**. The first 125,966 ends bought 20,000
listings; finishing needs roughly four times that again.

### The three levers, in order

1. **Request a value-limit increase.** There is a "Request to list more" link
   on the same Seller Hub screen. At £10.2M listed across 731,773 items this
   is the normal remedy and the only one that destroys nothing.
2. **Reduce value per listing.** Five sizes to three (M/L/XL) takes a listing
   from £59.95 to £35.97, so the remaining 85,573 would need £3.08M instead of
   £5.13M — **£2.05M of allowance saved without ending anything**. Changes the
   product, so it is the seller's call.
3. **End for value, not for count.** If ending, select to maximise £ freed per
   listing removed — a different ordering from `EBAY_END_TSHIRTS.csv`, which
   was worst-first by duplication.

   **CORRECTION (same day).** An earlier version of this line said the old
   t-shirts carry ten sizes each and so free about 2.7x a wall-art listing.
   That is wrong, and it inverted the advice. Only **40** of the old t-shirts
   carry variations (`build_end.py` holds them back by name); the other
   ~244,776 GR- listings are **single-item listings worth one unit each**.
   The ten-size example came from a 20-row sample of the unsold export that
   happened to fall among those 40. This file's own earlier arithmetic already
   said so — *"125,966 ends free only about 125,966 items"*.

### What ending can actually free

    all 118,872 remaining old t-shirts, at £11.99   ->  £1.43M
    headroom actually needed                            £5.33M
                                                        ------
    ending EVERY remaining old t-shirt covers           27%

**Ending t-shirts cannot solve this**, even if every one of them went. A
single-item t-shirt frees £11.99; an old wall-art listing (£29.95 framed +
£14.99 unframed) frees **£44.94 — 3.7x as much**. £5.33M is 118,603 wall-art
listings, 28% of the 424,118 live.

### The size lever, with all old tees ended

Even after freeing the full £1.43M, at five sizes only a fifth of the
catalogue fits:

    5 sizes  £59.95/listing   ->   20,438 of 105,573
    4 sizes  £47.96           ->   25,548
    3 sizes  £35.97           ->   34,064
    2 sizes  £23.98           ->   51,096
    1 size   £11.99           ->  102,191

### Caution before ending anything else

The counter reads "listed **and sold**", which may be cumulative for the
month. If it is, ending will **not** give the value back and listings would be
destroyed for nothing until the cycle resets. End a small batch first and
check whether the £10.2M figure actually falls.

### Tooling

`build_end2.py` builds the next tranche from a **fresh Active listings export**
(Seller Hub → Reports → Downloads). A fresh export is required: the container
no longer holds the one the first end file came from, and the account has
changed twice since. It skips every ItemID already in `EBAY_END_TSHIRTS.csv`
and anything with a `WLT-` SKU or an ItemID newer than the newest already-ended
one, so it cannot end the 20,000 new listings. It needs extending to sort by
value freed before it is used for lever 3.


---

## Corrected wall-art value, and how much to end (10 October 2026)

**The seller corrected the structure: the live wall art is A3 only, framed
plus unframed print only.** An earlier estimate of £339.95 per listing came
from the September `roops active listings REPRICED.csv` export, which still
carried A4/A3/A2 across Black/White/Oak/Unframed — 6 to 12 variations and
£170.8M of listed value across 502,477 listings. That export is stale and
must not be used for value arithmetic.

Current structure:

    A3 framed          £29.95
    A3 unframed only   £14.99
                       ------
    per listing        £44.94

### Wall art to end, assuming the end-all-old-t-shirts file goes up first

Ending all 118,872 remaining old t-shirts frees **£1.43M** (single-item
listings at £11.99).

| finish the 85,573 at | £ still needed | wall art to end | % of 424,118 live |
|---|---|---|---|
| **5 sizes** | £3.90M | **86,890** | **20.5%** |
| 4 sizes | £2.88M | 64,059 | 15.1% |
| 3 sizes | £1.85M | 41,228 | 9.7% |
| 2 sizes | £0.83M | 18,397 | 4.3% |

The size choice is worth far more than it looks: dropping from five sizes to
three removes **45,662 wall-art listings** from what has to be destroyed.

### The safety guarantee on the t-shirt end file

The old catalogue uses `GR-#######` SKUs and the new one uses `WLT-######`
(verified against `EBAY_PART1of3.csv`). Ending is restricted to `GR-` SKUs,
so the ~20,000 new listings cannot be touched by SKU alone — the ItemID check
is a second, independent guard rather than the only one.

### Still outstanding

The active t-shirt export the first end file was built from is gone from the
container, so `build_end2.py` needs a **fresh Active listings export** to
recover the 118,872 ItemIDs. One export covering the whole account serves both
jobs — the t-shirt end-all file and the wall-art selection.
