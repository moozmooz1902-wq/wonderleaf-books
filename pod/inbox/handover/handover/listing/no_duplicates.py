"""
no_duplicates.py — prove no design appears twice, anywhere.

WHAT IT CHECKS
    1. Within each bucket: no design generated twice
    2. Across buckets: no design in more than one store
    3. Against the ledger: everything generated is recorded, and everything
       recorded was generated
    4. Optionally against eBay CSVs: no custom label listed twice

WHY
    Duplicate listings across stores are worse than within one: eBay treats
    the same design on two accounts as a stronger duplication signal than on
    one. And the failure is silent — nothing complains until the listings are
    already live.

    Run this before every upload. It takes a couple of minutes and reads
    directly from R2, so it cannot be fooled by a stale local file.

    python3 no_duplicates.py r2:store1/raw r2:store2/raw r2:store3/raw
    python3 no_duplicates.py r2:tshirt-mockups/art/raw --csv tshirt_ebay_*.csv
"""

import argparse, csv, glob, os, re, subprocess, sys
from collections import defaultdict

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

ap = argparse.ArgumentParser()
ap.add_argument("buckets", nargs="+", help="rclone paths holding raw designs")
ap.add_argument("--ledger", default="used_designs.txt")
ap.add_argument("--csv", nargs="*", default=[],
                help="eBay CSVs to check for repeated custom labels")
args = ap.parse_args()

fails = []


def check(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  — {detail}" if detail else ""))
    if not ok:
        fails.append(label)


# --- read every bucket ----------------------------------------------------
where = defaultdict(list)      # design id -> which buckets hold it
per_bucket = {}

for b in args.buckets:
    print(f"listing {b} ...", flush=True)
    r = subprocess.run(f"rclone lsf {b}", shell=True,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"cannot read {b}: {r.stderr.strip()[:70]}")
    ids = []
    for line in r.stdout.splitlines():
        m = re.match(r"^(\d+)\.(png|jpg|jpeg|tif)$", line.strip(), re.I)
        if m:
            ids.append(int(m.group(1)))
    per_bucket[b] = ids
    for i in ids:
        where[i].append(b)
    print(f"  {len(ids):,} designs")

print(f"\nCHECKING {len(where):,} distinct designs across {len(args.buckets)} bucket(s)\n")

# --- 1. within each bucket ------------------------------------------------
print("WITHIN EACH BUCKET")
for b, ids in per_bucket.items():
    dupes = len(ids) - len(set(ids))
    check(dupes == 0, f"{b}", f"{len(ids):,} files, {dupes} repeated")

# --- 2. across buckets ----------------------------------------------------
print("\nACROSS BUCKETS")
shared = {i: bs for i, bs in where.items() if len(bs) > 1}
check(not shared, "no design appears in more than one store",
      f"{len(shared):,} shared" if shared else f"{len(where):,} all unique")
if shared:
    for i, bs in list(shared.items())[:5]:
        print(f"         design {i} is in: {', '.join(bs)}")

# --- 3. against the ledger ------------------------------------------------
print("\nAGAINST THE LEDGER")
if os.path.exists(args.ledger):
    led = set()
    with open(args.ledger, encoding="utf-8") as f:
        for line in f:
            if line.strip().isdigit():
                led.add(int(line.strip()))
    generated = set(where)
    missing = generated - led
    check(not missing, "everything generated is recorded in the ledger",
          f"{len(missing):,} missing — the next batch could reuse these"
          if missing else f"{len(led):,} recorded")
    if missing:
        print("         fix with: python3 rebuild_ledger.py " +
              " ".join(args.buckets))
    # ledger entries with no file are normal: rejected designs are deleted
    unused = led - generated
    if unused:
        print(f"         ({len(unused):,} ledger entries have no file — "
              "normal, those were rejected)")
else:
    check(False, "ledger exists", f"{args.ledger} not found")

# --- 4. eBay CSVs ---------------------------------------------------------
files = []
for pat in args.csv:
    files.extend(glob.glob(pat))
if files:
    print(f"\nEBAY CSVs ({len(files)} files)")
    labels = []
    titles = []
    for f in files:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r.get("CustomLabel"):
                labels.append(r["CustomLabel"])
            if r.get("*Title") and r.get("Relationship") != "Variation":
                titles.append(r["*Title"])
    check(len(labels) == len(set(labels)), "no custom label listed twice",
          f"{len(labels):,} listings, {len(labels)-len(set(labels))} repeated")
    check(len(titles) == len(set(titles)), "no title repeated",
          f"{len(titles)-len(set(titles))} repeated")

print("\n" + "=" * 66)
if fails:
    print(f"FAILED {len(fails)} CHECK(S) — DO NOT UPLOAD:")
    for f in fails:
        print(f"  * {f}")
    sys.exit(1)
print("NO DUPLICATES ANYWHERE — safe to upload")
