"""
exclude_listed.py — strip listings already live on eBay.

Streams. An earlier version read each CSV into memory in one go and the
kernel killed it on the second file — 80 MB of CSV becomes several GB once
parsed into dicts. This holds one listing block at a time: a parent row plus
its ten variations, never more.
"""

import argparse, csv, glob, os, sys

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

ap = argparse.ArgumentParser()
ap.add_argument("--listed", default="listed")
ap.add_argument("--csv", nargs="+", required=True)
ap.add_argument("--out", default="clean")
args = ap.parse_args()

# --- labels already on eBay ----------------------------------------------
live = set()
for f in sorted(glob.glob(os.path.join(args.listed, "*.csv"))):
    with open(f, encoding="utf-8", errors="ignore", newline="") as fh:
        rd = csv.reader(fh)
        head = next(rd, None)
        if not head:
            continue
        try:
            ix = head.index("CustomLabel")
        except ValueError:
            print(f"  {os.path.basename(f)}: no CustomLabel column, skipped")
            continue
        for row in rd:
            if len(row) > ix and row[ix].strip():
                live.add(row[ix].strip())
    print(f"  read {os.path.basename(f)}  running total {len(live):,}")

if not live:
    raise SystemExit("no labels found — check the files in listed/")
print(f"\n{len(live):,} labels already listed on eBay\n")

targets = []
for pat in args.csv:
    targets.extend(glob.glob(pat))
targets = sorted(set(targets))

kept_t = drop_t = n = 0

for f in targets:
    with open(f, encoding="utf-8", errors="ignore", newline="") as fh:
        rd = csv.reader(fh)
        head = next(rd, None)
        if not head:
            continue
        try:
            i_lab = head.index("CustomLabel")
            i_ttl = head.index("*Title")
            i_rel = head.index("Relationship")
        except ValueError:
            print(f"  {f}: unexpected columns, skipped")
            continue

        n += 1
        dst = f"{args.out}_{n:02d}.csv"
        kept = drop = 0
        block, blab = [], None

        with open(dst, "w", newline="", encoding="utf-8") as out:
            w = csv.writer(out)
            w.writerow(head)

            def flush():
                nonlocal kept, drop, block, blab
                if not block:
                    return
                if blab and blab in live:
                    drop += 1
                else:
                    w.writerows(block)
                    kept += 1
                block, blab = [], None

            for row in rd:
                is_parent = (len(row) > max(i_ttl, i_rel)
                             and row[i_ttl].strip()
                             and row[i_rel].strip() != "Variation")
                if is_parent:
                    flush()
                    block = [row]
                    blab = row[i_lab].strip() if len(row) > i_lab else None
                else:
                    block.append(row)
            flush()

    if kept == 0:
        os.remove(dst)
        n -= 1
        print(f"  {f}: all {drop:,} already live, nothing written")
    else:
        print(f"  {f} -> {dst}   kept {kept:,}  dropped {drop:,}")
    kept_t += kept
    drop_t += drop

print()
print("=" * 58)
print(f"  {kept_t:,} new listings written to {args.out}_*.csv")
print(f"  {drop_t:,} already live, excluded")
print("=" * 58)
