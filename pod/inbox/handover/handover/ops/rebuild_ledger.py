"""
rebuild_ledger.py — reconstruct the used-designs record from R2.

WHY THIS EXISTS
    pick.py keeps a ledger (used_designs.txt) so a batch generated months
    after the last one still cannot reuse a design. That file is the only
    thing standing between incremental batches and duplicate listings — the
    failure that once had to be undone with eBay End files.

    But the ledger is just a text file on a pod, and pods get terminated.

    The real record is R2 itself: every generated design is stored as
    <index>.png, so the bucket IS the list of what has been used. This
    reconstructs the ledger from those filenames, across as many buckets as
    the operation has grown to.

    python3 rebuild_ledger.py r2:tshirt-mockups/art/raw
    python3 rebuild_ledger.py r2:store1/raw r2:store2/raw r2:store3/raw
"""

import argparse, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("buckets", nargs="+",
                help="rclone paths holding the raw generations")
ap.add_argument("--out", default="used_designs.txt")
ap.add_argument("--merge", action="store_true",
                help="add to the existing ledger instead of replacing it")
args = ap.parse_args()

found = set()

if args.merge and os.path.exists(args.out):
    with open(args.out, encoding="utf-8") as f:
        for line in f:
            if line.strip().isdigit():
                found.add(int(line.strip()))
    print(f"existing ledger: {len(found):,}")

for b in args.buckets:
    print(f"listing {b} ...", flush=True)
    r = subprocess.run(f"rclone lsf {b}", shell=True,
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  failed: {r.stderr.strip()[:80]}")
        continue
    n = 0
    for line in r.stdout.splitlines():
        m = re.match(r"^(\d+)\.(png|jpg|jpeg|tif)$", line.strip(), re.I)
        if m:
            found.add(int(m.group(1)))
            n += 1
    print(f"  {n:,} designs")

if not found:
    raise SystemExit("nothing found — check the bucket paths")

with open(args.out, "w", encoding="utf-8") as f:
    for i in sorted(found):
        f.write(f"{i}\n")

print(f"\n{len(found):,} design indices written to {args.out}")
print("pick.py reads this automatically, so the next batch cannot reuse any "
      "of them.")
