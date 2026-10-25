# Repricing live eBay listings

`reprice.py` rewrites the Start price column of an eBay
"revise price and quantity" export and splits the result into files that
are safe to upload.

```bash
# the 3 files the seller asked for, 25 Oct
python3 reprice.py ebay_price.csv -o out -n 3

# the same data capped at 500,000 rows per file
python3 reprice.py ebay_price.csv -o out500k -n 1 --max-rows 500000
```

## The prices it writes (seller, 25 Oct 2026)

| Size | Framed (Black / White / Oak) | Unframed Print Only |
|---|---|---|
| A4 | £24.99 | £8.99 |
| A3 | £29.99 | £12.99 |
| A2 | £34.99 | £18.99 |

## What the 25 Oct export actually contained

502,443 listings, 4,825,276 rows. Four things in it would break a naive
find-and-replace, and each one is handled explicitly:

- **Listings are not all the same shape.** 199,319 carry 6 variations,
  170,188 carry 9, 132,934 carry 12, plus a 16-row and a 3-row one. Any
  code assuming a fixed block size mangles two thirds of the file.
- **There are four frame colour values, not three.** 147,098 listings use
  `White - Picture is for illustration`. It is a white frame with a
  photography disclaimer attached, so it takes the white frame price. A map
  keyed on the three obvious names would have left 441,294 rows at the old
  price, giving listings where two white options cost different amounts.
- **Some rows cannot be priced.** One listing uses `A1 SPECIAL SIZE`, which
  is not in the price list, and 12 rows have an empty variation spec. All 16
  are left exactly as they were and reported. A price nobody agreed to is
  worse than a price left alone.
- **A child row without its parent is meaningless** — the item number lives
  only on the parent row. Splits therefore fall on listing boundaries, never
  every N rows.

## Verified on the output, not assumed

- 4,825,276 rows out = 4,825,276 rows in
- 502,443 listings, 0 duplicate item numbers
- 0 orphans: no listing split across two files
- 0 price mismatches against the table above
- both header lines (`#INFO` and the column row) on every file
