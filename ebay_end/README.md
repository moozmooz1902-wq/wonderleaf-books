# End-listing files

Built from an eBay **active-listings download** the seller supplies
(`eBay-active-revise-price-quantity-download_GB`).
`build_end_from_download.py` is the builder; re-run it on a fresh download
rather than editing a CSV by hand.

## Current run — 31 Oct 2026

Source: 35.9 MB download, **506,463 rows**.

| file | listings | what it ends |
|---|---|---|
| **`EBAY_END_TEST_5.csv`** | **5** | **upload this one first** |
| **`EBAY_END_ALL.csv`** | **107,600** | everything — art prints AND t-shirts |
| `EBAY_END_ART_ONLY.csv` | 46,377 | Art Prints (360) only |
| `EBAY_END_TEES_ONLY.csv` | 61,223 | T-Shirts (15687) only |

The seller asked for one file, so `EBAY_END_ALL.csv` is the deliverable.
The splits cost nothing to keep and a whole-account end file is not
obviously what someone means by "end my listings".

### The account has shrunk by more than half since 21 Oct

Worth knowing before anyone reaches for the older file:

| | |
|---|---|
| 21 Oct file | 239,449 listings |
| still live today | **107,600** |
| gone since (ended or sold) | **131,849** |
| new since | **0** |

Today's set is a **strict subset** of the 21 Oct one — the seller has been
working through that file. So **the 21 Oct `EBAY_END_ALL.csv` is now stale**:
more than half its item numbers no longer exist, and uploading it would
produce 131,849 errors for listings that are already gone. Git holds the
old version if it is ever needed; the file in this folder is today's.

## The test upload, 31 Oct 19:19 — format proven, and one surprise

eBay accepted the file and processed every row. No format error, no
warning. That is the question the test existed to answer and the answer is
yes.

    137650398239  Success                              Art Prints
    137650449676  Success                              Art Prints
    137650459828  Success                              Art Prints
    137679792460  Failure 1047 already been closed     T-Shirts
    137679795972  Failure 1047 already been closed     T-Shirts

**1047 is not a defect in the file.** It is eBay saying those two listings
were already ended before the upload — the download shows them as active
and they are not. A download is a snapshot; anything that ended after it
was generated still appears in it.

**The sample was worse than it looked, and that is worth recording.** The
test file took the first five rows, and the first three turn out to be the
only three listings in all 107,600 with **no variation rows at all**:

| | listings | variation rows each |
|---|---|---|
| Art Prints | **3** | **0** ← the three that were tested |
| Art Prints | 46,374 | 2 |
| T-Shirts | 61,223 | 5 |

So "three art prints ended cleanly" says nothing about the 46,374 ordinary
art prints — it says the three oddities ended cleanly. Taking the first N
rows of a sorted file is not a sample, and here it picked the only
structurally unusual rows in the account.

`EBAY_END_TEST_20.csv` is the replacement: 15 t-shirts spread evenly across
the tee file plus 5 art prints, **all twenty ordinary multi-variation
listings**, none overlapping the first test. It answers the real question —
whether the 61,223 t-shirts are already closed, which would make the
46,377 art prints the only real work.

## Why 107,600 rows and not 506,463

Only PARENT rows in the download carry an item number; the other 398,863
rows are `Relationship=Variation` children with a blank item number,
belonging to the parent above them. eBay ends a listing by item number and
that ends every variation with it. One row per distinct item number is
correct; a row per source line would be mostly unusable.

## Format

Header is byte-identical to `tshirt/EBAY_END_ALL_TEES.csv`, which uploaded
successfully:

    *Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193),ItemID,EndCode
    End,137650398239,NotAvailable

`NotAvailable` is the end reason, the same one used before.

## Checked before hand-off, on every file including the test one

- header byte-identical to the proven file
- every row matches `End,<9-15 digits>,NotAvailable`
- zero duplicate item numbers
- zero item numbers absent from the source download
- zero source item numbers left out of `EBAY_END_ALL.csv`
- art + tees reconstruct all exactly, with no overlap
- `EBAY_END_TEST_5.csv` is a strict subset of the full file
- no stray whitespace, no CRLF, trailing newline present

The five in the test file, so there is no surprise about what gets ended:

| item | category | SKU |
|---|---|---|
| 137650398239 | Art Prints | M12K-0460253 |
| 137650449676 | Art Prints | M12K-0476938 |
| 137650459828 | Art Prints | M12K-0485860 |
| 137679792460 | T-Shirts | bd_60_Grandson_0 |
| 137679795972 | T-Shirts | hb_classic-car-restoring_Brother_2 |

**Ending listings cannot be undone** — a re-list is a new listing with a new
item number, and it loses the listing's age and watchers. Nothing here was
uploaded to eBay; the seller uploads it.
