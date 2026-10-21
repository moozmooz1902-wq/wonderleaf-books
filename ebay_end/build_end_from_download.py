#!/usr/bin/env python3
"""Build an eBay File Exchange End file from an active-listings download.

Only the PARENT rows carry an item number; variation children have a blank
one and belong to the parent above them. eBay ends a listing by its item
number, so one row per distinct item number ends the whole listing including
every variation. Writing a row per source line would be 905,971 rows for
239,449 listings - wrong, and most of them unusable.
"""
import csv, re, sys, collections

src, out_all, out_art, out_tee = sys.argv[1:5]
HDR = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193),ItemID,EndCode"
ENDCODE = "NotAvailable"
ITEM_RE = re.compile(r"^\d{9,15}$")

f = open(src, encoding="utf-8-sig", newline="")
f.readline()                                   # the #INFO template line
rdr = csv.DictReader(f)

seen = set()
rows = []            # (item, category)
bad = []
for r in rdr:
    it = (r.get("Item number") or "").strip().strip('"')
    if not it:
        continue                               # variation child: parent covers it
    if not ITEM_RE.match(it):
        bad.append(it); continue
    if it in seen:
        continue
    seen.add(it)
    rows.append((it, (r.get("Category name") or "").strip()))

art = [i for i, c in rows if c.startswith("Art Prints")]
tee = [i for i, c in rows if c.startswith("T-Shirts")]
other = [(i, c) for i, c in rows if not (c.startswith("Art Prints")
                                         or c.startswith("T-Shirts"))]

def write(path, items):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(HDR + "\n")
        for i in items:
            fh.write(f"End,{i},{ENDCODE}\n")
    return len(items)

n_all = write(out_all, [i for i, _ in rows])
n_art = write(out_art, art)
n_tee = write(out_tee, tee)

print(f"listings found          {len(rows):,}")
print(f"  Art Prints (360)      {n_art:,}")
print(f"  T-Shirts (15687)      {n_tee:,}")
print(f"  other categories      {len(other):,}", other[:3] if other else "")
print(f"malformed item numbers  {len(bad):,}", bad[:3] if bad else "")
print(f"\nwrote {n_all:,} rows -> everything")
print(f"wrote {n_art:,} rows -> art only")
print(f"wrote {n_tee:,} rows -> tees only")
