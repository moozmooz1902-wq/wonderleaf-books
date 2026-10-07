#!/usr/bin/env python3
"""Drop the redundant copy of any title that still appears more than once."""
import csv, re, json, os, collections

csv.field_size_limit(20 << 20)
SRC = "/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv"
TMP = SRC + ".new"
def norm(t): return " ".join(re.sub(r"[^a-z0-9 ]", " ", t.lower()).split())

titles = json.load(open("final_titles.json"))
g = collections.defaultdict(list)
for sku, t in titles.items():
    g[norm(t)].append(sku)
DROP = {s for v in g.values() if len(v) > 1 for s in sorted(v)[1:]}
print(f"titles appearing more than once: {sum(1 for v in g.values() if len(v)>1):,}")
print(f"redundant copies to drop       : {len(DROP):,}")

kept = rows = 0
skip = False
with open(SRC, newline="", encoding="utf-8") as f, \
     open(TMP, "w", newline="", encoding="utf-8") as o:
    r = csv.reader(f); w = csv.writer(o, lineterminator="\r\n")
    hdr = next(r); w.writerow(hdr)
    IREL = hdr.index("Relationship")
    for row in r:
        if (row[IREL] or "").strip() == "Variation":
            if skip:
                rows += 1; continue
            w.writerow(row); continue
        if row[1].strip() in DROP:
            skip = True; rows += 1; continue
        skip = False; kept += 1
        w.writerow(row)
os.replace(TMP, SRC)
print(f"kept {kept:,} listings | dropped {len(DROP):,} ({rows:,} rows)")
