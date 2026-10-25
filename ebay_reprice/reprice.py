#!/usr/bin/env python3
"""Reprice an eBay "revise price and quantity" export.

Input is the template eBay gives you from Seller Hub (active listings ->
download -> revise price/quantity). Output is the same template with the
Start price column rewritten, split into N files that are safe to upload.

WHAT MAKES THIS LESS TRIVIAL THAN IT LOOKS, measured on the 25 Oct export
of 502,443 listings / 4,825,276 rows:

* LISTINGS ARE NOT ALL THE SAME SHAPE. 199,319 of them carry 6 variations,
  170,188 carry 9 and 132,934 carry 12, plus two one-off shapes. Anything
  that assumes a fixed 13-row block silently mangles two thirds of the file.
* THERE ARE FOUR FRAME COLOURS, NOT THREE. Besides Black, White and Oak
  there are 147,098 listings using "White - Picture is for illustration".
  A map keyed on the three expected names would leave 441,294 rows at their
  old price, and a listing where two of the white variations cost different
  amounts is worse than one nobody touched.
* SOME ROWS ARE NOT PRICEABLE. One listing uses "A1 SPECIAL SIZE", which is
  not in the price list the seller gave, and 9 rows have an empty variation
  spec. Those are LEFT ALONE and counted, never guessed at. A price I
  invented is a price nobody agreed to.
* A CHILD ROW WITHOUT ITS PARENT IS MEANINGLESS. The item number lives only
  on the parent row, so the split points have to fall on listing
  boundaries. Splitting every N rows would hand eBay orphaned variations.

Nothing is edited in place and nothing is deleted. The input file is only
ever read.
"""
import argparse, csv, collections, os, sys

csv.field_size_limit(10 ** 9)

# The seller's prices, 25 Oct 2026. Keyed on the SIZE token inside the
# variation spec, split by whether the colour is a frame or the print only.
FRAMED = {"A4": 24.99, "A3": 29.99, "A2": 34.99}
PRINT_ONLY = {"A4": 8.99, "A3": 12.99, "A2": 18.99}

# Every colour value that means "framed", including the odd one. The suffix
# on the last is a photography disclaimer, not a different product: it is a
# white frame and it takes the white frame's price.
FRAME_COLOURS = {
    "black", "white", "oak",
    "white - picture is for illustration",
}
PRINT_COLOURS = {"unframed print only"}


def parse_spec(spec):
    """'Color=Black|Size=A4 (21x29.7 cm)' -> ('black', 'A4'). Returns
    (None, None) for anything that is not a colour/size pair we know."""
    colour = size = None
    for part in spec.split("|"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip().lower()
        v = v.strip()
        if k in ("color", "colour"):
            colour = v.lower()
        elif k == "size":
            # "A4 (21x29.7 cm)" -> "A4";  "A1 SPECIAL SIZE" -> "A1 SPECIAL"
            size = v.split("(")[0].strip()
    return colour, size


def price_for(spec):
    """The new price, or None to leave the row untouched."""
    colour, size = parse_spec(spec)
    if not colour or not size:
        return None, "no colour/size in spec"
    table = (FRAMED if colour in FRAME_COLOURS
             else PRINT_ONLY if colour in PRINT_COLOURS else None)
    if table is None:
        return None, f"unknown colour {colour!r}"
    if size not in table:
        return None, f"unknown size {size!r}"
    return table[size], None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out-dir", default="out")
    ap.add_argument("-n", "--files", type=int, default=3)
    ap.add_argument("--max-rows", type=int, default=0,
                    help="also start a new file once it reaches this many "
                         "data rows. The seller's listing files cap at "
                         "500,000, and a 2,000,000-row upload is the kind of "
                         "thing eBay refuses after you have waited for it.")
    ap.add_argument("--prefix", default="EBAY_REPRICE")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    # Pass 1: count listings, so the split lands on listing boundaries and
    # the files come out near enough the same size.
    with open(a.src, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        info = next(r)
        head = next(r)
        idx = {k: i for i, k in enumerate(head)}
        need = ["Start price", "Relationship", "Relationship details",
                "Item number"]
        missing = [k for k in need if k not in idx]
        if missing:
            raise SystemExit(f"template is missing column(s): {missing}")
        listings = sum(1 for row in r
                       if row and not row[idx["Relationship"]].strip()
                       and row[idx["Item number"]].strip())
    per_file = -(-listings // a.files)
    print(f"{listings:,} listings -> {a.files} files, "
          f"~{per_file:,} listings each")

    P = idx["Start price"]
    REL = idx["Relationship"]
    RD = idx["Relationship details"]
    ITEM = idx["Item number"]

    stats = collections.Counter()
    skipped = collections.Counter()
    changed_from = collections.Counter()
    out = None
    w = None
    file_no = 0
    in_file = 0          # listings written to the current file
    written = []
    # A whole listing is buffered so it is never split across two files.
    block = []

    def open_next():
        nonlocal out, w, file_no, in_file
        if out:
            out.close()
            written.append((path_of(file_no), in_file, stats["rows_out_file"]))
            stats["rows_out_file"] = 0
        file_no += 1
        in_file = 0
        p = path_of(file_no)
        out = open(p, "w", newline="", encoding="utf-8-sig")
        w = csv.writer(out, quoting=csv.QUOTE_MINIMAL,
                       lineterminator="\r\n")
        # eBay needs BOTH header lines on every file it is given.
        w.writerow(info)
        w.writerow(head)

    def path_of(n):
        tail = f"_of_{a.files}" if not a.max_rows else ""
        return os.path.join(a.out_dir, f"{a.prefix}_{n}{tail}.csv")

    def flush():
        nonlocal in_file
        if not block:
            return
        if (out is None or in_file >= per_file
                or (a.max_rows
                    and stats["rows_out_file"] + len(block) > a.max_rows)):
            open_next()
        for row in block:
            w.writerow(row)
            stats["rows_out"] += 1
            stats["rows_out_file"] += 1
        in_file += 1
        block.clear()

    with open(a.src, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        next(r)
        for row in r:
            if not row:
                continue
            if len(row) < len(head):
                row = row + [""] * (len(head) - len(row))
            rel = row[REL].strip().lower()
            if rel == "variation":
                new, why = price_for(row[RD].strip())
                if new is None:
                    skipped[why] += 1
                    stats["left_alone"] += 1
                else:
                    old = row[P].strip().strip('"')
                    if old:
                        changed_from[old] += 1
                    row[P] = f"{new:.2f}"
                    stats["repriced"] += 1
                block.append(row)
            else:
                # A parent row starts a new listing: the previous one is
                # complete and can be written.
                flush()
                if row[ITEM].strip():
                    stats["listings"] += 1
                block.append(row)
        flush()
    if out:
        out.close()
        written.append((path_of(file_no), in_file, stats["rows_out_file"]))

    print(f"\nlistings written  {stats['listings']:,}")
    print(f"rows written      {stats['rows_out']:,}")
    print(f"prices rewritten  {stats['repriced']:,}")
    print(f"rows left alone   {stats['left_alone']:,}")
    if skipped:
        print("\nleft alone, by reason (NOT guessed at):")
        for k, v in skipped.most_common():
            print(f"  {v:>8,}  {k}")
    print("\nwhat the old prices were:")
    for k, v in changed_from.most_common(12):
        print(f"  {v:>9,}  was {k}")
    print("\nfiles:")
    for p, n, rows in written:
        print(f"  {os.path.basename(p):<34} {n:>8,} listings  "
              f"{rows:>10,} rows  {os.path.getsize(p)/1e6:>7.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
