# What to upload, and in what order

Everything below is finished and verified. Nothing here needs a terminal.

## Order of operations

The account is at its selling limit, so listings have to come off before the
new ones go on. End first, then test, then upload.

1. **`EBAY_END_TEST_50.csv`** - fifty ends. Confirms the End template and the
   column names are right on fifty rows instead of 130,000.
2. **`EBAY_END_TSHIRTS.csv`** - 129,881 ends. T-shirts only; no wall art.
3. **`EBAY_TEST_50.csv`** - fifty new listings, same header as the main file.
   Check in Seller Hub that all five sizes came through, the photo shows, and
   the price is £12.99.
4. **`EBAY_ONE_FILE.zip`** - the whole catalogue as one file.

## The end file

`EBAY_END_TSHIRTS.csv` - 129,881 rows, `End` / `NotAvailable`.

    129,881 t-shirt listings ended
    114,957 t-shirts left live
          0 wall art touched - Art Prints (360) is untouched

Chosen worst-first, in two passes:

    86,770  duplicate titles already live against each other. The 244,816
            live GR- t-shirts carry only 158,046 distinct titles, so a third
            of that catalogue is competing with itself. One copy of each
            title is kept; the older copies are ended.
    43,111  longest-listed of the remainder (lowest item number first), as
            the only available proxy for "has been up longest and still has
            not converted". The downloaded file carries no sales data.

Held back and never ended: the 22 t-shirts whose SKU is not `GR-#######`
(the `hb_`, `oc_`, `br_` batch, the 40 that carry variations, and the 7 at
quantity 10). They look like a separate, more deliberate set.

`EBAY_END_MANIFEST.csv` lists every ended item with its SKU, title and the
reason, for the record.

## The upload file

**`EBAY_ONE_FILE.zip`** - one eBay File Exchange CSV, zipped.

    115,966 listings
    579,830 size variations, exactly 5 per listing, no orphans
    695,796 data rows, 30 columns
    £12.99, quantity 5, category 15687, United Kingdom
    business policies named 1 for shipping, returns and payment
    every listing has a PicURL and a print master in the bucket

Built by joining the eight `EBAY_part0*.csv` files, whose headers are
byte-identical and which were split on listing boundaries. The joined file
was re-parsed afterwards and checked, not assumed: every listing has exactly
five variations, there are no orphan variations, no variation is missing
`C:Size`, and no parent is missing `PicURL`.

`EBAY_PARTS_CLEAN.zip` (the eight parts) is still here and is the same data
if File Exchange rejects the single file for size.

## Headroom arithmetic

    live now          668,956 listings   (424,118 wall art + 244,838 tees)
    after the ends    539,075 listings
    after the upload  655,041 listings   - 13,915 fewer than today

So on a **listing** count the upload lands below where the account sits now,
with about 14,000 spare.

**On an item count it does not, and this is the one thing to check before
uploading.** Everything live is quantity 1, so 668,956 listings is about
669,281 items. The new file is quantity 5 on each of five sizes, which is
25 items per listing:

    new upload        2,899,150 items
    account after     3,438,550 items   - about 5x today

If the limit on this account is expressed in items rather than listings,
ending 129,881 listings does not create room for that, because it frees
about 129,881 items and the upload asks for 2.9 million. Dropping quantity
from 5 to 1 takes the upload to 579,830 items and the account to 1,119,230.
That is a one-value change to the file and does not affect the SKUs, the
artwork or the bucket. Worth reading the actual limit off Seller Hub first.

## What is in the bucket

    art/mock/WLT-######.jpg   listing photo, 2000 x 2000
    art/raw/WLT-######.png    print master, transparent, 300 dpi, 2600px wide

Both are the paths the fulfilment tool resolves a custom label to, so an
order looks up its own artwork with no extra step.

**Verified against the live bucket on 2026-10-07**, not from memory:
all 115,966 custom labels in the upload file resolve to both
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
