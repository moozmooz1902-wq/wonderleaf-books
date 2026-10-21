# End-listing files, built 21 Oct 2026

Built from an eBay **active-listings download** the seller supplied
(`eBay-active-revise-price-quantity-download_GB`, 67 MB, 905,971 rows).
`build_end_from_download.py` is the builder; re-run it on a fresh download
rather than editing a CSV by hand.

## The one thing to know

The download was a WHOLE ACCOUNT, not one product line. It holds both:

| file | listings | what it ends |
|---|---|---|
| `EBAY_END_ALL.csv` | 239,449 | **everything - art prints AND t-shirts** |
| `EBAY_END_ART_ONLY.csv` | 127,493 | Art Prints (360) only |
| `EBAY_END_TEES_ONLY.csv` | 111,956 | T-Shirts (15687) only |

The seller asked for "one file", so `EBAY_END_ALL.csv` is the deliverable.
The two split files exist because a whole-account end file is not obviously
what someone means when they say "end my listings", and the split costs
nothing to keep.

## Why 239,449 rows and not 905,971

Only PARENT rows in the download carry an item number; the other 666,522
rows are `Relationship=Variation` children with a blank item number,
belonging to the parent above them. eBay ends a listing by item number and
that ends every variation with it. One row per distinct item number is
correct; a row per source line would be mostly unusable.

## Format

Header is byte-identical to `tshirt/EBAY_END_ALL_TEES.csv`, which uploaded
successfully:

    *Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193),ItemID,EndCode
    End,137650344631,NotAvailable

`NotAvailable` is the end reason, the same one used before.

## Checked before hand-off

- header byte-identical to the proven file
- all 239,449 rows match `End,<9-15 digits>,NotAvailable`
- zero duplicate item numbers
- zero item numbers absent from the source download
- zero source item numbers left out
- zero malformed item numbers, zero unexpected categories

**Ending listings cannot be undone** - a re-list is a new listing with a new
item number, and it loses the listing's age and watchers. Nothing here was
uploaded to eBay; the seller uploads it.
