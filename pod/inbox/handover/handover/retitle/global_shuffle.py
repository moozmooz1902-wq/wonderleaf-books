"""
global_shuffle.py — shuffle every listing across every CSV, not within each.

WHY
    shuffle_csv.py reorders rows inside one file. The same listings stay in
    the same file, so file 01 is still the same slice of the catalogue and
    still leans on the same subjects. Uploading that looks like one keyword
    repeated, which is what draws attention.

    This redistributes all 280,000 listings across all the output files, so
    each one is a genuine cross-section of everything.

HOW
    Two passes, so 2.2 GB never has to fit in memory:

      pass 1  stream every listing block and deal it into a random output
              file, like dealing cards
      pass 2  shuffle each output file internally, which is now small enough
              to hold

    A listing block is a parent row plus its variation rows. Blocks move
    whole — a parent without its variations is a broken listing.

USE
    python3 global_shuffle.py tshirt_ebay_*.csv
    python3 global_shuffle.py tshirt_ebay_*.csv --out mixed --seed 7

    Writes mixed_01.csv ... alongside. Originals untouched.
"""

import argparse, csv, glob, os, random, sys

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

ap = argparse.ArgumentParser()
ap.add_argument("csv", nargs="+")
ap.add_argument("--out", default="mixed")
ap.add_argument("--seed", type=int, default=20260813,
                help="change this per store so each gets a different mix")
ap.add_argument("--files", type=int, default=0,
                help="number of output files (default: same as input)")
ap.add_argument("--keep-postcode", action="store_true",
                help="leave the postcode column alone. By default it is "
                     "BLANKED: the same postcode on every listing across "
                     "several stores ties those accounts together, and eBay "
                     "falls back to each account's own postcode anyway")
ap.add_argument("--keep-grey-note", action="store_true",
                help="leave the 'Sports Grey 90%% cotton' line in the "
                     "description. By default it is removed — every listing "
                     "is black, so the exception never applies and it "
                     "contradicts the 100%% Cotton claim above it")
args = ap.parse_args()

rng = random.Random(args.seed)

srcs = []
for pat in args.csv:
    srcs.extend(glob.glob(pat))
srcs = sorted(set(srcs))
if not srcs:
    raise SystemExit("no CSVs matched")

n_out = args.files or len(srcs)
print(f"{len(srcs)} input files -> {n_out} shuffled output files\n")

# --- pass 1: deal every listing into a random output file ----------------
head = None
tmp = [f".shuf_{i:02d}.tmp" for i in range(n_out)]
handles, writers = [], []
for t in tmp:
    fh = open(t, "w", newline="", encoding="utf-8")
    handles.append(fh)
    writers.append(csv.writer(fh))

total = 0
fixed = {"cotton": 0}
for f in srcs:
    with open(f, encoding="utf-8", errors="ignore", newline="") as fh:
        rd = csv.reader(fh)
        h = next(rd, None)
        if h is None:
            continue
        if head is None:
            head = h
        i_ttl = h.index("*Title")
        i_rel = h.index("Relationship")
        i_pc = h.index("*PostalCode") if "*PostalCode" in h else (
               h.index("PostalCode") if "PostalCode" in h else -1)
        i_desc = h.index("*Description") if "*Description" in h else -1

        block = []

        def deal():
            global total
            if not block:
                return
            w = writers[rng.randrange(n_out)]
            w.writerows(block)
            w.writerow(["<<<END>>>"])      # block separator for pass 2
            total += 1

        for row in rd:
            # --- corrections, applied while the row is passing through ----
            if not args.keep_postcode and i_pc >= 0 and len(row) > i_pc:
                row[i_pc] = ""
            if not args.keep_grey_note and i_desc >= 0 and len(row) > i_desc:
                if "Sports Grey" in row[i_desc]:
                    row[i_desc] = row[i_desc].replace(
                        "100% Cotton (Sports Grey 90% cotton, 10% polyester)",
                        "100% Cotton")
                    fixed["cotton"] += 1

            is_parent = (len(row) > max(i_ttl, i_rel)
                         and row[i_ttl].strip()
                         and row[i_rel].strip() != "Variation")
            if is_parent:
                deal()
                block = [row]
            else:
                block.append(row)
        deal()
    print(f"  read {os.path.basename(f)}  {total:,} listings dealt")

for fh in handles:
    fh.close()

print(f"\n{total:,} listings dealt across {n_out} files")
print("shuffling each file internally ...\n")

# --- pass 2: shuffle inside each output file ------------------------------
written = 0
for i, t in enumerate(tmp, 1):
    blocks, block = [], []
    with open(t, encoding="utf-8", newline="") as fh:
        for row in csv.reader(fh):
            if row and row[0] == "<<<END>>>":
                if block:
                    blocks.append(block)
                block = []
            else:
                block.append(row)
    if block:
        blocks.append(block)

    rng.shuffle(blocks)

    dst = f"{args.out}_{i:02d}.csv"
    with open(dst, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(head)
        for b in blocks:
            w.writerows(b)
    os.remove(t)
    written += len(blocks)
    print(f"  {dst}  {len(blocks):,} listings")

print()
print("=" * 56)
print(f"  {written:,} listings across {n_out} files, fully mixed")
print(f"  upload the {args.out}_*.csv files")
if not args.keep_postcode:
    print("  postcode blanked on every row")
if fixed["cotton"]:
    print(f"  'Sports Grey' line removed from {fixed['cotton']:,} descriptions")
print("=" * 56)
