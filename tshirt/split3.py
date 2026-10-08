#!/usr/bin/env python3
"""Split the upload file into three, cutting only between listings.

A listing is a parent row plus its five variation rows, so a cut in the wrong
place would orphan variations and eBay would reject the part. Each part gets
its own copy of the header.
"""
import csv, os, sys

csv.field_size_limit(20 << 20)
SRC = "EBAY_ONE_FILE.csv"
N = 3

hdr = open(SRC, newline="", encoding="utf-8").readline().rstrip("\r\n").split(",")
IREL = hdr.index("Relationship")

# first pass: how many listings are there
total = 0
with open(SRC, newline="", encoding="utf-8") as f:
    r = csv.reader(f); next(r)
    for row in r:
        if (row[IREL] or "").strip() != "Variation":
            total += 1
per = -(-total // N)                      # ceiling, so the last part is the small one
print(f"listings {total:,} -> {N} parts of up to {per:,}")

# second pass: write them out
part = 0
out = w = None
count_in_part = 0
counts = []
with open(SRC, newline="", encoding="utf-8") as f:
    r = csv.reader(f); next(r)
    for row in r:
        is_parent = (row[IREL] or "").strip() != "Variation"
        if is_parent and (out is None or count_in_part >= per):
            if out:
                out.close(); counts.append(count_in_part)
            part += 1
            out = open(f"EBAY_PART{part}of{N}.csv", "w", newline="", encoding="utf-8")
            w = csv.writer(out, lineterminator="\r\n")
            w.writerow(hdr)
            count_in_part = 0
        if is_parent:
            count_in_part += 1
        w.writerow(row)
out.close(); counts.append(count_in_part)
print("listings per part:", counts, "total", sum(counts))
assert sum(counts) == total, "listing count changed"
