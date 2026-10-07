# What to upload, and in what order

Everything below is finished and verified. Nothing here needs a terminal.

## Order of operations

The account is at its selling limit, so listings have to come off before the
new ones go on. End first, then test, then upload.

1. **`EBAY_END_TEST_50.csv`** - fifty ends. Confirms the End template and the
   column names are right on fifty rows instead of 126,000.
2. **`EBAY_END_TSHIRTS.csv`** - 125,966 ends, one file. T-shirts only; no
   wall art.
3. **`EBAY_TEST_50.csv`** - fifty new listings, same header as the main file.
   Check in Seller Hub that all five sizes came through, the photo shows, the
   price is £12.99 and each size shows 1 available.
4. **`EBAY_ONE_FILE.zip`** - the whole catalogue as one file.

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

    115,966 listings
    579,830 size variations, exactly 5 per listing, no orphans
    695,796 data rows, 30 columns
    £12.99, quantity 1 per size, category 15687, United Kingdom
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
    after the ends    542,990 listings
    after the upload  658,956 listings   - 10,000 fewer than today

So on a **listing** count the upload lands below where the account sits now,
with the 10,000 spare slots asked for.

**On an item count it does not, and this is the one thing to check before
uploading.** Everything live is quantity 1, so 668,956 listings is about
669,281 items. The new file is quantity 5 on each of five sizes, which is
25 items per listing:

    new upload        2,899,150 items
    account after     3,442,465 items   - about 5x today

If the limit on this account is expressed in items rather than listings,
ending 129,881 listings does not create room for that, because it frees
about 129,881 items and the upload asks for 2.9 million. Dropping quantity
from 5 to 1 takes the upload to 579,830 items and the account to 1,119,230.
If it turns out fewer listings can go up than the file holds, the upload is
better split than the ends made bigger - 118,872 live t-shirts are still
selling and are worth more than empty headroom. Worth reading the actual limit off Seller Hub first.

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
