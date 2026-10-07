#!/usr/bin/env python3
"""What is actually live on this account, by category, parents vs variations."""
import csv, collections, re, sys
csv.field_size_limit(20 << 20)
SRC = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/drive/live.bin"

f = open(SRC, newline="", encoding="utf-8-sig")
first = f.readline()                      # the #INFO line
assert first.startswith("#INFO"), first[:60]
r = csv.DictReader(f)
print("columns:", r.fieldnames, flush=True)

cat = collections.Counter()           # parents per category
catvar = collections.Counter()        # variations per category
qty = collections.Counter()           # total available quantity per category
rows = parents = variations = 0
cur_cat = None
for row in r:
    rows += 1
    rel = (row.get("Relationship") or "").strip()
    c = (row.get("Category name") or "").strip()
    q = (row.get("Available quantity") or "").strip()
    if rel == "":
        parents += 1
        cur_cat = c
        cat[c] += 1
    else:
        variations += 1
        catvar[cur_cat] += 1
    try:
        qty[cur_cat] += int(q or 0)
    except ValueError:
        pass

print(f"\nrows {rows:,} | listings {parents:,} | variations {variations:,}")
print(f"\n{'listings':>9} {'variations':>11} {'total qty':>11}  category")
for c, n in cat.most_common(40):
    print(f"{n:>9,} {catvar[c]:>11,} {qty[c]:>11,}  {c}")
print(f"\ndistinct categories: {len(cat)}")

# which ones are t-shirts?
print("\n--- categories whose ID or name looks like a t-shirt ---")
for c, n in cat.most_common():
    cid = re.search(r"\((\d+)\)\s*$", c)
    cid = cid.group(1) if cid else "?"
    if cid == "15687" or re.search(r"t-?shirt|tee\b", c, re.I):
        print(f"  {n:>9,}  id={cid:>7}  {c}")
