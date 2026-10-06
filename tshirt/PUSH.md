# What to upload, and in what order

Everything below is finished and verified. Nothing here needs a terminal.

## The file

**`EBAY_PARTS_CLEAN.zip`** - eight eBay File Exchange CSVs.

    115,966 listings
    579,830 size variations, exactly 5 per listing, no orphans
    £12.99, quantity 5, category 15687, UK
    business policies named 1 for shipping, returns and payment
    every listing has a photo and a print master in the bucket

This supersedes `EBAY_PARTS.zip`, which still contains the 389 listings
that were pulled for trademark and likeness. Do not upload that one.

## Order

1. **`EBAY_TEST_50.csv` first.** Fifty listings, same format. It costs
   nothing to find out that a column name or a policy name is wrong on
   fifty rows instead of 116,000.
2. Check in Seller Hub that the fifty came through with all five sizes, the
   photo showing, and the right price.
3. Then the eight parts in order, `EBAY_part01` through `08`. They are split
   on listing boundaries, so a part never cuts a listing in half.

## What is in the bucket

    art/mock/WLT-######.jpg   listing photo, 1200px
    art/raw/WLT-######.png    print master, transparent, 300dpi

Both are the paths the fulfilment tool resolves a custom label to, so an
order looks up its own artwork with no extra step.

The print masters are flat spot colour with hard edges - 5 to 7 inks, no
semi-transparent pixels anywhere - because the transfers are DTF and DTF
cannot hold a gradient or a soft edge.

Note the bucket also holds about 1.45 million objects under the same two
prefixes with numeric names. Those are not from this catalogue and nothing
here has touched them.

## What changed in the artwork

13,313 listings (11%) now carry a real illustration above the slogan,
recoloured into each listing's own palette. The other 103,000 are type-only,
which is the format their own data rates highest. The SKUs did not change,
so the eBay file is unaffected by it either way.
