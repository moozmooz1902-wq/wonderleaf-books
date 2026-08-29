#!/usr/bin/env python3
"""
Build a File Exchange End file from a Seller Hub active-listings export.

    # see what would be ended, WITHOUT writing anything
    python3 end_listings.py --listings active.csv --match-category "Posters"

    # write the End files once the counts look right
    python3 end_listings.py --listings active.csv \
        --match-category "Posters" --out end_wallart

Ending listings cannot be undone - a relist is a new listing with a new item
number and no history. So the default is a DRY RUN: it prints what it would
end and writes nothing until --out is given.

The export is the one from Seller Hub -> Reports -> Downloads -> Listings.
Column names are matched loosely, because eBay has changed them over the
years: "Item number" / "Item ID" / "ItemID" all work.
"""

import argparse, collections, csv, os, re, sys

csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))

ACTION = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=745|CC=UTF-8)"
HEADER = [ACTION, "ItemID", "EndCode"]

# Every spelling of the columns we need that eBay has used.
WANT = {
    "item": ("item number", "item id", "itemid", "item#"),
    "title": ("title", "item title"),
    "label": ("custom label (sku)", "custom label", "customlabel", "sku"),
    "category": ("category name", "category", "ebay category"),
    "qty": ("available quantity", "quantity", "quantity available"),
    "price": ("start price", "current price", "price"),
}


def find_columns(fieldnames):
    got = {}
    lower = {(f or "").strip().lower(): f for f in fieldnames}
    for key, names in WANT.items():
        for n in names:
            if n in lower:
                got[key] = lower[n]
                break
    return got


def read_listings(path):
    # Seller Hub exports sometimes carry a preamble line before the header.
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        head = fh.readline()
        fh.seek(0)
        if "," not in head or len(head.split(",")) < 3:
            fh.readline()
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit(f"{path}: no rows found")
    return rows, find_columns(rows[0].keys())


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listings", required=True,
                    help="the Seller Hub active-listings export")
    ap.add_argument("--out",
                    help="output prefix. WITHOUT this it is a dry run and "
                         "nothing is written")
    ap.add_argument("--match-category", action="append", default=[],
                    help="end listings whose category contains this. Repeat "
                         "for several")
    ap.add_argument("--match-title", action="append", default=[],
                    help="end listings whose title matches this regex")
    ap.add_argument("--match-label", action="append", default=[],
                    help="end listings whose custom label starts with this")
    ap.add_argument("--keep-category", action="append", default=[],
                    help="never end anything in a category containing this. "
                         "Applied after the matches, so it always wins")
    ap.add_argument("--end-code", default="NotAvailable",
                    choices=("NotAvailable", "Incorrect", "LostOrBroken",
                             "OtherListingError", "SellToHighBidder"))
    ap.add_argument("--rows", type=int, default=100000,
                    help="max rows per output file")
    ap.add_argument("--limit", type=int,
                    help="end at most this many, for a first cautious batch")
    a = ap.parse_args()

    rows, col = read_listings(a.listings)
    if "item" not in col:
        raise SystemExit(
            "no item-number column found. Columns in this file:\n  "
            + "\n  ".join(sorted(rows[0].keys())))

    print(f"  {len(rows):,} rows in {a.listings}")
    print(f"  using columns: "
          + ", ".join(f"{k}={v!r}" for k, v in sorted(col.items())))

    if not (a.match_category or a.match_title or a.match_label):
        # Ending everything in the file is almost never what is meant, and it
        # is not recoverable. Make it impossible to do by accident.
        raise SystemExit(
            "\n  refusing to end EVERY listing in the file.\n"
            "  Give at least one --match-category / --match-title / "
            "--match-label.\n"
            "  Run with only --listings to see the categories present.")

    title_res = [re.compile(p, re.I) for p in a.match_title]
    seen_items = set()
    picked, kept_back = [], 0
    by_cat = collections.Counter()
    samples = []

    for r in rows:
        item = (r.get(col["item"]) or "").strip()
        # Variation rows repeat the parent's item number; ending it once ends
        # the whole listing.
        if not item.isdigit() or item in seen_items:
            continue
        seen_items.add(item)

        cat = (r.get(col.get("category", ""), "") or "")
        title = (r.get(col.get("title", ""), "") or "")
        label = (r.get(col.get("label", ""), "") or "")

        hit = (any(m.lower() in cat.lower() for m in a.match_category)
               or any(rx.search(title) for rx in title_res)
               or any(label.startswith(m) for m in a.match_label))
        if not hit:
            continue
        if any(k.lower() in cat.lower() for k in a.keep_category):
            kept_back += 1
            continue

        picked.append(item)
        by_cat[cat or "(no category)"] += 1
        if len(samples) < 10:
            samples.append(f"{item}  {cat[:26]:<26} {title[:60]}")

    print(f"\n  {len(seen_items):,} distinct listings in the file")
    print(f"  {len(picked):,} match and would be ended")
    if kept_back:
        print(f"  {kept_back:,} matched but were held back by --keep-category")
    print(f"  {len(seen_items) - len(picked) - kept_back:,} untouched")

    if by_cat:
        print("\n  by category:")
        for c, n in by_cat.most_common(15):
            print(f"    {n:>8,}  {c}")

    if samples:
        print("\n  a sample of what would be ended:")
        for s in samples:
            print(f"    {s}")

    if a.limit:
        picked = picked[:a.limit]
        print(f"\n  --limit: writing only the first {len(picked):,}")

    if not a.out:
        print("\n  DRY RUN - nothing written. Add --out <prefix> to write the "
              "End files.")
        return

    files, n = [], 1
    for i in range(0, len(picked), a.rows):
        fn = f"{a.out}_{n:02d}.csv"
        with open(fn, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(HEADER)
            for item in picked[i:i + a.rows]:
                w.writerow(["End", item, a.end_code])
        print(f"  {fn}  {min(a.rows, len(picked) - i):,} rows  "
              f"{os.path.getsize(fn) / 1e6:.1f} MB")
        files.append(fn)
        n += 1
    print(f"\n  {len(picked):,} listings to end across {len(files)} file(s)")
    print("  This cannot be undone. A relist gets a new item number and "
          "loses the listing's history.")


if __name__ == "__main__":
    main()
