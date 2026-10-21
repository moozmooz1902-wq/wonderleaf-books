# Test files, one per bucket - 21 Oct 2026

Ten listings each, so the seller can prove the format on whichever account
they choose rather than on luxvia, which is their main one.

    lunar-kms_TEST_10.csv          10 listings, 40 rows
    luxvia-art_TEST_10.csv         10 listings, 40 rows
    mercury-usm_TEST_10.csv        10 listings, 40 rows
    posterleaf-store1_TEST_10.csv  10 listings, 40 rows

Each listing is one parent plus three Variation rows, one per frame colour,
black first in the parent's `PicURL` so black is the main image.
GBP 19.99, quantity 1, A3, category 360, policies 1/1/1.

## Built without a pod, and why that is sound

The FULL per-store build needs a pod: it diffs the catalogue against a
LISTING of the bucket, and the R2 keys live only on template `vbsgwyibn1`.
At ten listings that is unnecessary. `make_test_files.py` instead fetches
**every picture of every candidate panel over the public r2.dev URL** and
drops any panel that is not complete on all twelve - three frames by four
colourways. Two luxvia panels were skipped for exactly that reason, 1 and 3
pictures short.

Verifying the pictures individually is stronger evidence than a bucket
listing, not weaker: the public URL is the thing eBay itself will fetch.

## Checked, by verify_test_files.py

- 30/30 distinct pictures live in each of the four files, re-fetched after
  the files were written
- every parent followed by exactly three Variation rows
- every picture on its OWN store's host AND under its own key prefix, so no
  file can point at another bucket's images
- every SKU matches `WA-<16 hex>-<0-3>` and hashes back to the bucket whose
  file it is in, via allocate.store_for
- price 19.99 and quantity 1 on every variation row
- **zero problems across all four files**

## The format risk these files exist to settle

Our Variation children do NOT repeat `*Category`, `*ConditionID` and
`*Title`. `tshirt/PUSH.md` records that the tee file eBay actually accepted
DOES repeat them, found by diffing a working file after error 21919053
rejected all fifty rows of a first attempt. The parent's variation set is
present here, so this may be fine - but it is unproven for wall art, and
that is the whole point of testing ten listings instead of 3.8 million.

If a test returns 21919053, the fix is to repeat those three fields on
every child row, and the per-store builds have to be re-run.
