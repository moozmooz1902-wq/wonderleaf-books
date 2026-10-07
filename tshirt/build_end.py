#!/usr/bin/env python3
"""Build an eBay File Exchange End file for t-shirts only.

Selection order, worst-first:
  1. Near-duplicate titles already live against each other - keep one copy of
     each title, end the rest. These are the listings eBay's duplicate-listing
     policy actually objects to, so they are the safest thing to remove.
  2. Then the longest-listed remaining tees (lowest eBay item number first),
     as the only available proxy for "has been up longest and still has not
     converted", until the target is met.

Never touched: anything in Art Prints (360), and any t-shirt whose SKU is not
GR-####### (a small separate batch of 22, plus the 40 that carry variations).
"""
import csv, json, os, re, collections

UPLOAD_LISTINGS = 115_966        # listings in EBAY_ONE_FILE.csv, counted not assumed
EXTRA_ROOM      = 10_000         # spare slots the seller asked for on top
TARGET = UPLOAD_LISTINGS + EXTRA_ROOM

def norm(t):
    t = t.lower(); t = re.sub(r"[^a-z0-9 ]", " ", t)
    return " ".join(t.split())

SCRATCH = ("/tmp/claude-0/-home-user-wonderleaf-books/"
           "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/")
tees = json.load(open(os.environ.get("TEES", SCRATCH + "tees.json")))

# only the GR- commodity catalogue is eligible
elig, held = [], []
for item, sku, title, sp, bin_, q in tees:
    (elig if re.fullmatch(r"GR-\d+", sku or "") else held).append((item, sku, title))
print(f"live t-shirts            {len(tees):,}")
print(f"  eligible (GR- SKUs)    {len(elig):,}")
print(f"  held back (other SKUs) {len(held):,}  -> {[h[1] for h in held][:6]}")

bytitle = collections.defaultdict(list)
for item, sku, title in elig:
    bytitle[norm(title)].append((item, sku, title))
# keep the newest copy of each title (highest item number), end the older ones
dupes = []
for t, group in bytitle.items():
    if len(group) > 1:
        group.sort(key=lambda g: int(g[0]))
        dupes.extend(group[:-1])
print(f"\ndistinct titles          {len(bytitle):,}")
print(f"duplicate copies to end  {len(dupes):,}")

dupe_items = {d[0] for d in dupes}
rest = sorted((e for e in elig if e[0] not in dupe_items), key=lambda g: int(g[0]))

need_more = max(0, TARGET - len(dupes))
chosen = dupes + rest[:need_more]
print(f"\ntarget to end            {TARGET:,}  (upload {UPLOAD_LISTINGS:,} + {EXTRA_ROOM:,} spare)")
print(f"  from duplicates        {len(dupes):,}")
print(f"  plus longest-listed    {need_more:,}")
print(f"  TOTAL to end           {len(chosen):,}")
print(f"t-shirts left live after {len(tees) - len(chosen):,}")

assert len({c[0] for c in chosen}) == len(chosen), "duplicate item numbers in end list"

HDR = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193),ItemID,EndCode\n"
def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(HDR)
        w = csv.writer(f, lineterminator="\n")
        for item, sku, title in rows:
            w.writerow(["End", item, "NotAvailable"])
    print(f"  wrote {path}  ({len(rows):,} rows)")

OUT = "/home/user/wonderleaf-books/tshirt/"
print()
write(OUT + "EBAY_END_TEST_50.csv", chosen[:50])
write(OUT + "EBAY_END_TSHIRTS.csv", chosen)

# a plain record of what is being ended, for the seller's own reference
with open(OUT + "EBAY_END_MANIFEST.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["ItemID", "SKU", "Title", "Reason"])
    for item, sku, title in dupes:
        w.writerow([item, sku, title, "duplicate title already live"])
    for item, sku, title in rest[:need_more]:
        w.writerow([item, sku, title, "longest-listed, not converting"])
print(f"  wrote {OUT}EBAY_END_MANIFEST.csv")
