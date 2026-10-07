#!/usr/bin/env python3
"""Write the slogan-led titles in, and drop what could not be made unique.

Variation rows now repeat *Title (that is what the seller's working file does),
so both the parent and its five children get the new title, and the <h2> in the
description is re-synced too.
"""
import csv, re, html, json, os

csv.field_size_limit(20 << 20)
SRC = "/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv"
TMP = SRC + ".new"
d = json.load(open("slogan_titles.json"))
titles, DROP = d["titles"], set(d["failed"])
H2 = re.compile(r"(<h2[^>]*>)(.*?)(</h2>)", re.S)

kept = droppedrows = 0
cur_dropped = False
cur_title = None
with open(SRC, newline="", encoding="utf-8") as f, \
     open(TMP, "w", newline="", encoding="utf-8") as o:
    r = csv.reader(f); w = csv.writer(o, lineterminator="\r\n")
    hdr = next(r); w.writerow(hdr)
    IREL = hdr.index("Relationship"); ITITLE = hdr.index("*Title")
    IDESC = hdr.index("*Description")
    for row in r:
        if (row[IREL] or "").strip() == "Variation":
            if cur_dropped:
                droppedrows += 1; continue
            row[ITITLE] = cur_title
            w.writerow(row); continue
        sku = row[1].strip()
        if sku in DROP:
            cur_dropped = True; droppedrows += 1; continue
        cur_dropped = False
        cur_title = titles[sku]
        row[ITITLE] = cur_title
        row[IDESC] = H2.sub(lambda m: m.group(1) + html.escape(cur_title, quote=True)
                            + m.group(3), row[IDESC], count=1)
        kept += 1
        w.writerow(row)
os.replace(TMP, SRC)
print(f"kept {kept:,} listings | dropped {len(DROP):,} ({droppedrows:,} rows)")
