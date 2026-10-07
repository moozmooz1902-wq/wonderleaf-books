#!/usr/bin/env python3
"""Join the eight eBay File Exchange parts into one file and verify the result.

The parts share a byte-identical header and were split on listing boundaries,
so a straight concatenation that drops the repeated headers is lossless. This
re-reads the joined file with the csv module afterwards rather than trusting
the join, and checks the things eBay will reject on.
"""
import csv, glob, io, os, sys, collections

SRC = sorted(glob.glob("/tmp/claude-0/-home-user-wonderleaf-books/"
                       "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/ebay/EBAY_part0*.csv"))
OUT = "/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv"
csv.field_size_limit(10 << 20)

assert len(SRC) == 8, SRC
header = open(SRC[0], newline="", encoding="utf-8").readline()

written = 0
with open(OUT, "w", newline="", encoding="utf-8") as out:
    out.write(header)
    for i, p in enumerate(SRC, 1):
        with open(p, newline="", encoding="utf-8") as f:
            first = f.readline()
            assert first == header, f"header differs in {p}"
            # Copy the rest verbatim; quoting and embedded newlines pass through.
            while True:
                chunk = f.read(1 << 22)
                if not chunk:
                    break
                out.write(chunk)
        print(f"  joined part{i:02d}", flush=True)

# --- verify by re-parsing the joined file -----------------------------------
rows = parents = variations = 0
kids = collections.Counter()
parent_skus, orphan, badsize = set(), [], []
sizes_seen = collections.Counter()
prices, qtys, cats, locs = set(), set(), set(), set()
pic_missing = 0

with open(OUT, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    cols = r.fieldnames
    action = cols[0]
    for row in r:
        rows += 1
        rel = (row.get("Relationship") or "").strip()
        label = (row.get("CustomLabel") or "").strip()
        if rel == "":                      # parent
            parents += 1
            parent_skus.add(label)
            cats.add(row["*Category"]); locs.add(row["*Location"])
            if not (row.get("PicURL") or "").strip():
                pic_missing += 1
        elif rel == "Variation":
            variations += 1
            base = label.rsplit("-", 1)[0]
            kids[base] += 1
            sizes_seen[(row.get("RelationshipDetails") or "").strip()] += 1
            prices.add(row["*StartPrice"]); qtys.add(row["*Quantity"])
            if not row.get("C:Size", "").strip():
                badsize.append(label)

for base in kids:
    if base not in parent_skus:
        orphan.append(base)

bad_count = {b: n for b, n in kids.items() if n != 5}

print(f"\nfile            {OUT}")
print(f"size            {os.path.getsize(OUT)/1e6:.1f} MB")
print(f"columns         {len(cols)}")
print(f"data rows       {rows:,}")
print(f"listings        {parents:,}")
print(f"variations      {variations:,}")
print(f"variations/listing  {sorted(set(kids.values()))}")
print(f"listings not having exactly 5   {len(bad_count)}")
print(f"orphan variations (no parent)   {len(orphan)}")
print(f"variations missing C:Size       {len(badsize)}")
print(f"parents missing PicURL          {pic_missing}")
print(f"distinct CustomLabel parents    {len(parent_skus):,}")
print(f"price values    {sorted(prices)}")
print(f"quantity values {sorted(qtys)}")
print(f"category values {sorted(cats)}")
print(f"location values {sorted(locs)}")
print(f"size details    {dict(sizes_seen)}")

# hand the parent SKU list on for the bucket contract check
with open("/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/"
          "scratchpad/parent_skus.txt", "w") as f:
    f.write("\n".join(sorted(parent_skus)))

ok = (not bad_count and not orphan and not badsize and pic_missing == 0
      and parents == len(parent_skus))
print("\nVERDICT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
