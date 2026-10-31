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

## After the upload — 2,218 left, 31 Oct 20:55

The seller uploaded `EBAY_END_ALL.csv` and then pulled a fresh download
to check. 11,379 rows, 9,161 of them variation children:

| | |
|---|---|
| in the end file | 107,600 |
| ended | **105,382 (97.9%)** |
| **still active** | **2,218** — 1,575 t-shirts, 643 art prints |

All 2,218 were in the end file, and every one is a `137…` number, so
this is the first account only; none of the second account's 591,673 is
involved.

**They are NOT a truncated tail.** The survivors sit at rows 4 to 107,171
and are spread through every 10,000-row block of the file:

    rows       1- 10,000:    119
    rows  10,001- 20,000:    155
    rows  20,001- 30,000:     85
    rows  30,001- 40,000:    177
    rows  40,001- 50,000:    206
    rows  50,001- 60,000:    265
    rows  60,001- 70,000:    276
    rows  70,001- 80,000:    331
    rows  80,001- 90,000:    223
    rows  90,001-100,000:    192
    rows 100,001-110,000:    189

That rules out the obvious explanation. A daily action limit or a row cap
would stop part-way and leave a contiguous block at the end; these are
scattered, so eBay read the whole file and 2.1% of the rows individually
did not take.

`EBAY_END_REMAINING_2218.csv` is exactly those 2,218, 65 KB.

### …and the answer was that they were already ended. 21:57

**All 2,218 came back `1047 - The auction has already been closed`.**
Every single one. Not one real failure among them.

So the 20:55 download was STALE. eBay's active-listings download lags
behind the account by an hour or more after a large End run, and the
2,218 were already gone while it was still listing them as live. The
seller watching the Active count fall in the browser was seeing the truth;
the download was not.

The upload report settles it:

| upload | result |
|---|---|
| `EBAY_END_ALL.csv` (107,600) | **107,588 completed, 12 failed** |
| `EBAY_END_REMAINING_2218.csv` | 0 completed, 2,218 already closed |

So the first account is done bar **12 listings**, not 2,218.

**I had this wrong and the wrong answer is worth keeping here.** The
scatter analysis above is sound - the survivors genuinely were spread
through every block of the file rather than sitting in a tail - but I
read "not truncated" as "2.1% individually refused" and guessed at sold,
bid or disputed. The actual explanation was that they had not refused at
all and the evidence I was reading was out of date. **A fresh download is
not a source of truth right after a bulk End; the upload's own result
file is.** It reports per row, at the moment of the attempt, and it is
the only thing that does.

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
