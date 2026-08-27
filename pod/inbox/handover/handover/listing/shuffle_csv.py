"""
shuffle_csv.py — mix the listing order across CSV files.

WHY
    Design ids are contiguous per subject, so the files arrive as 820 Welsh
    Dragons, then 820 Eastern Dragons, and so on. On eBay's newly-listed page
    that reads as spam, and a sudden wall of one subject is the pattern their
    duplicate checks look for. Interleaving makes a batch look like a normal
    shop adding varied stock.

SAFETY
    A listing is a BLOCK: one parent row followed by its variation rows. The
    block is never split — rows are only ever moved together, and the script
    verifies afterwards that every block still has the same parent, the same
    variation count, the same title and the same image URL. If anything does
    not line up it refuses to write.

    python3 shuffle_csv.py tshirt_ebay_03.csv tshirt_ebay_04.csv ...
"""

import csv, glob, os, random, sys
from collections import Counter

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

files = sys.argv[1:]
if not files:
    raise SystemExit("give the CSV files to shuffle, e.g. tshirt_ebay_0[3-9].csv")

print(f"reading {len(files)} files ...")

header = None
blocks = []          # each block is a list of rows: [parent, var, var, ...]
for f in files:
    with open(f, encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        if header is None:
            header = r.fieldnames
        elif r.fieldnames != header:
            raise SystemExit(f"{f} has different columns — refusing to mix")
        cur = None
        for row in r:
            is_parent = bool(row["*Title"]) and row["Relationship"] != "Variation"
            if is_parent:
                if cur:
                    blocks.append(cur)
                cur = [row]
            else:
                if cur is None:
                    raise SystemExit(f"{f}: variation row before any parent — "
                                     "file is malformed, refusing to touch it")
                cur.append(row)
        if cur:
            blocks.append(cur)

print(f"  {len(blocks):,} listings found")

# --- sanity before touching anything --------------------------------------
sizes = Counter(len(b) for b in blocks)
if len(sizes) != 1:
    print("  block sizes:", dict(sizes))
    raise SystemExit("listings have inconsistent variation counts — "
                     "refusing to shuffle")
per = next(iter(sizes))
print(f"  every listing has {per} rows (1 parent + {per-1} variations)")

# fingerprint each listing so we can prove nothing moved between listings
before = {
    b[0]["CustomLabel"]: (b[0]["*Title"], b[0]["PicURL"], len(b))
    for b in blocks
}
if len(before) != len(blocks):
    raise SystemExit("duplicate CustomLabel across files — refusing to shuffle")

# --- interleave by subject family ------------------------------------------
# Group by the leading word of the title, which is the subject. Round-robin
# across groups so no single subject clusters.
groups = {}
for b in blocks:
    key = b[0]["*Title"].split()[0]
    groups.setdefault(key, []).append(b)

rng = random.Random(42)
for g in groups.values():
    rng.shuffle(g)

order, pos = [], 0
keys = sorted(groups)
rng.shuffle(keys)
while any(pos < len(groups[k]) for k in keys):
    for k in keys:
        if pos < len(groups[k]):
            order.append(groups[k][pos])
    pos += 1

print(f"  interleaved across {len(groups):,} subjects")

# --- verify BEFORE writing -------------------------------------------------
after = {
    b[0]["CustomLabel"]: (b[0]["*Title"], b[0]["PicURL"], len(b))
    for b in order
}
if before != after:
    raise SystemExit("a listing changed during shuffle — refusing to write")
if len(order) != len(blocks):
    raise SystemExit("listing count changed — refusing to write")
print("  verified: every listing intact, title and image still paired")

# --- write back, same rows per file ----------------------------------------
per_file = -(-len(order) // len(files))
for n, f in enumerate(files):
    chunk = order[n * per_file:(n + 1) * per_file]
    tmp = f + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        for b in chunk:
            w.writerows(b)
    os.replace(tmp, f)
    print(f"  {f}: {len(chunk):,} listings")

print(f"\n{len(order):,} listings rewritten in interleaved order")
