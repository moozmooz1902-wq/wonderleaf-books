#!/usr/bin/env python3
"""Declare the variation set on each parent row.

eBay rejected the test file with 21919053: "VariationSpecificsSet container
(Item.Variations.VariationSpecificsSet) is required to list a Multi-SKU item."

In File Exchange a multi-variation listing declares its variation axis on the
PARENT row, with every value the children use, pipe-separated. Our parents had
C:Size empty and only the children carried a size, so eBay had no set to build
the variation matrix from.
"""
import csv, os, sys, collections

csv.field_size_limit(20 << 20)
SET = "Small|Medium|Large|X-Large|XX-Large"

for path in sys.argv[1:]:
    tmp = path + ".new"
    parents = fixed = 0
    kids = collections.defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f, \
         open(tmp, "w", newline="", encoding="utf-8") as o:
        r = csv.reader(f); w = csv.writer(o, lineterminator="\r\n")
        hdr = next(r); w.writerow(hdr)
        IREL = hdr.index("Relationship"); ISIZE = hdr.index("C:Size")
        for row in r:
            if (row[IREL] or "").strip() == "Variation":
                kids[row[1].rsplit("-", 1)[0]].append(row[ISIZE])
            else:
                parents += 1
                if not row[ISIZE].strip():
                    row[ISIZE] = SET; fixed += 1
            w.writerow(row)
    os.replace(tmp, path)
    # every child's size must appear in the declared set
    allowed = set(SET.split("|"))
    bad = {k: v for k, v in kids.items() if set(v) - allowed or len(set(v)) != 5}
    print(f"{path}: {parents:,} parents, {fixed:,} given the variation set"
          f" | listings whose child sizes do not match the set: {len(bad)}")
