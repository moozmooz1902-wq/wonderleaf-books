"""
verify_shuffle.py — prove the shuffle changed only the order.

Run it in the same folder, after global_shuffle.py:

    python3 verify_shuffle.py

Compares every listing in the originals against the mixed files, by custom
label. Checks the title still matches and every variation row is still
attached. 280,000 listings is not something to upload on trust.
"""

import csv, glob, sys

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def read(pat):
    d = {}
    dupes = 0
    for f in sorted(glob.glob(pat)):
        with open(f, encoding="utf-8", errors="ignore", newline="") as fh:
            r = csv.reader(fh)
            h = next(r, None)
            if h is None:
                continue
            il, it, ir = (h.index("CustomLabel"), h.index("*Title"),
                          h.index("Relationship"))
            lab = None
            for row in r:
                if (len(row) > max(il, it, ir) and row[it].strip()
                        and row[ir].strip() != "Variation"):
                    lab = row[il].strip()
                    if lab in d:
                        dupes += 1
                    d[lab] = [row[it].strip(), 0]
                elif lab:
                    d[lab][1] += 1
    return d, dupes


print("reading the originals ...")
a, da = read("tshirt_ebay_*.csv")
print("reading the shuffled files ...")
b, db = read("mixed_*.csv")

lost = set(a) - set(b)
gained = set(b) - set(a)
both = set(a) & set(b)
t_changed = sum(1 for k in both if a[k][0] != b[k][0])
v_changed = sum(1 for k in both if a[k][1] != b[k][1])

print()
print("=" * 52)
print(f"  listings before   : {len(a):,}")
print(f"  listings after    : {len(b):,}")
print(f"  lost              : {len(lost):,}")
print(f"  gained            : {len(gained):,}")
print(f"  titles changed    : {t_changed:,}")
print(f"  variations changed: {v_changed:,}")
print(f"  duplicate labels  : {db:,}")
print("=" * 52)

bad = (len(a) != len(b) or lost or gained or t_changed or v_changed or db)
if bad:
    print("\n  DO NOT UPLOAD — something moved that should not have.")
    for k in list(lost)[:3]:
        print(f"    missing: {k}")
    for k in [x for x in both if a[x][1] != b[x][1]][:3]:
        print(f"    {k}: {a[k][1]} variations before, {b[k][1]} after")
    sys.exit(1)

print("\n  CLEAN — only the order changed. Safe to upload mixed_*.csv")
