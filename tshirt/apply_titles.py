#!/usr/bin/env python3
"""Write the rebuilt titles into the eBay file and drop what the seller asked.

Dropped:
  - one of each of the 545 old near-duplicate title pairs (the seller's call:
    only 2 of the 545 were truly the same design, the rest were different
    designs that collided on title text, but safe beats sorry)
  - the 110 listings no unique title could be built for inside 80 characters

The listing description carries the title in its <h2>, so that is updated too,
and a dropped listing takes its five variation rows with it.
"""
import csv, re, json, html, collections, os

csv.field_size_limit(20 << 20)
SRC = "/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv"
TMP = SRC + ".new"

d = json.load(open("new_titles.json"))
titles, unplaceable = d["titles"], set(d["dropped"])

def norm(t): return " ".join(re.sub(r"[^a-z0-9 ]", " ", t.lower()).split())

# rebuild the old-duplicate groups to pick which copy goes
old = []
with open(SRC, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if not (row.get("Relationship") or "").strip():
            old.append((row["CustomLabel"].strip(), row["*Title"].strip()))
g = collections.defaultdict(list)
for s, t in old: g[norm(t)].append(s)
dupe_drop = {s for v in g.values() if len(v) > 1 for s in sorted(v)[1:]}

DROP = unplaceable | dupe_drop
print(f"drop: {len(unplaceable):,} unplaceable + {len(dupe_drop):,} duplicate copies"
      f" = {len(DROP):,} listings", flush=True)

kept = dropped_rows = retitled = desc_fixed = 0
cur_dropped = False
with open(SRC, newline="", encoding="utf-8") as f, \
     open(TMP, "w", newline="", encoding="utf-8") as out:
    r = csv.reader(f); w = csv.writer(out, lineterminator="\r\n")
    hdr = next(r); w.writerow(hdr)
    I_SKU, I_TITLE, I_DESC = 1, 3, 4
    I_REL = hdr.index("Relationship")
    for row in r:
        if (row[I_REL] or "").strip() == "Variation":
            if cur_dropped:
                dropped_rows += 1
            else:
                w.writerow(row)
            continue
        sku = row[I_SKU].strip()
        if sku in DROP:
            cur_dropped = True; dropped_rows += 1; continue
        cur_dropped = False
        new = titles.get(sku)
        if new:
            oldt = row[I_TITLE]
            row[I_TITLE] = new
            retitled += 1
            # the description repeats the title in its <h2>
            esc_old, esc_new = html.escape(oldt, quote=False), html.escape(new, quote=False)
            if esc_old and esc_old in row[I_DESC]:
                row[I_DESC] = row[I_DESC].replace(esc_old, esc_new)
                desc_fixed += 1
            elif oldt in row[I_DESC]:
                row[I_DESC] = row[I_DESC].replace(oldt, new)
                desc_fixed += 1
        kept += 1
        w.writerow(row)

os.replace(TMP, SRC)
print(f"listings kept      {kept:,}")
print(f"titles replaced    {retitled:,}")
print(f"descriptions fixed {desc_fixed:,}")
print(f"rows dropped       {dropped_rows:,}")
