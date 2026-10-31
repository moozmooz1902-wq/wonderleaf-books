# End files — second eBay account

Built 31 Oct 2026 from `items.csv.gz`, the shrunk form of a 380 MB
active-listings download. 591,673 listings.

**This is a DIFFERENT ACCOUNT from the files one level up.** Its item
numbers begin `358…`; the other account's begin `137…`, and the two sets
have **zero overlap**. They cannot be mixed up by accident, and they must
not be merged: a File Exchange upload goes to the account you are signed
in as.

| file | rows | size |
|---|---|---|
| `END_TEST_20.csv` | 20 | 1 KB |
| `END_01_of_05.csv` | 118,335 | 3.39 MB |
| `END_02_of_05.csv` | 118,335 | 3.39 MB |
| `END_03_of_05.csv` | 118,335 | 3.39 MB |
| `END_04_of_05.csv` | 118,335 | 3.39 MB |
| `END_05_of_05.csv` | 118,333 | 3.39 MB |

Breakdown: Art Prints (360) 371,274 · T-Shirts (15687) 220,399.

## Two shapes of the same 591,673 listings. Use one set, not both.

| set | files | rows each | size each |
|---|---|---|---|
| `BIG_01..02_of_02.csv` | 2 | 295,837 | 8.46 MB |
| `END_01..05_of_05.csv` | 5 | 118,335 | 3.39 MB |

Both cover all 591,673 with nothing missing and nothing duplicated.
**Uploading both would try to end every listing twice** - harmless, since
the second attempt returns 1047 "already closed", but it doubles the work
and fills the report with errors that are not errors.

The BIG pair is the seller's call, 31 Oct: their account takes **50 MB and
500,000 rows**, which is larger than the published File Exchange limit and
is their own direct experience of their own account. Two files rather than
one because 591,673 is over the 500,000 row cap; the whole catalogue is
only 17 MB, so rows bind long before bytes either way.

The five-file set stays as the fallback. If a BIG file is rejected on
upload, the limit is lower than expected and `END_01_of_05.csv` onwards
will go through - nothing needs rebuilding.

## Why the five-file set is 3.39 MB and not 100 MB

The seller asked for files up to 100 MB. **eBay will not take one.**
File Exchange — and Seller Hub Reports, which replaces it — caps an
upload at about **14.9 MB and 150,000 lines**, and eBay staff say those
are fixed and cannot be raised. A 100 MB file is rejected at upload.

These rows are tiny (`End,358366487916,NotAvailable`, 29 bytes), so the
LINE limit binds long before the byte limit: 150,000 lines is only about
4.3 MB. Hence 118,335 rows each — comfortably inside both.

## Why five balanced files and not four plus a stub

A greedy split at the cap gives four full files and a 31,673-row
remainder. Five equal files upload exactly the same way and read better
in a queue. The 21 Oct wall-art build had the same lesson, where greedy
sharding left a 20-row tail file.

## Checked before hand-off

- header byte-identical on every file to the one eBay accepted on 31 Oct
- every row matches `End,<9-15 digits>,NotAvailable`
- 591,673 rows, 591,673 distinct — zero duplicates within OR across files
- zero item numbers absent from the upload
- zero item numbers from the upload left out
- no stray whitespace, no CRLF, trailing newline on every file
- `END_TEST_20.csv` is a strict subset, sampled evenly across the whole
  set rather than taken from the top — the first test on the other
  account took the first five rows and they turned out to be the only
  three non-variation listings in the account, which told us nothing

**What was NOT checked, and cannot be:** these were built from the
shrunk list, not from the 380 MB download itself. Everything traces back
to `items.csv.gz` exactly; whether that file faithfully represents the
download rests on the extraction, which was proven against the other
account's download — identical output to the full parser, 107,600 for
107,600.

**Ending listings cannot be undone.** A re-list is a new listing with a
new item number and loses the listing's age and watchers. Nothing here
was uploaded; the seller uploads it.
