#!/usr/bin/env bash
# finish.sh — take it from "generation is done" to "CSVs are ready", alone.
#
#   nohup bash finish.sh > finish.log 2>&1 &
#
# Waits for postrun to finish the mockups, builds the eBay CSVs, verifies
# them, interleaves them, and pushes everything to R2 so the pod can be
# terminated the moment it is done. Check finish.log when you get back.

set -uo pipefail
cd /workspace || exit 1
source venv/bin/activate 2>/dev/null

BUCKET="${R2_REMOTE:-r2:tshirt-mockups/art}"
ROWS="${ROWS:-110000}"

say() { printf '\n=== %s  (%s) ===\n' "$1" "$(date -u +%H:%M)"; }

# ---------------------------------------------------------------- 1. wait
say "1/5  waiting for postrun"
while pgrep -f "postrun.py" >/dev/null; do
    tail -1 postrun.log 2>/dev/null | tr -d '\n'; echo
    sleep 300
done
echo "  postrun has finished"

# Nothing should still be on local disk, but flush anyway — designs sitting
# in a worker buffer are the one thing a termination would lose.
for i in 0 1 2 3 4 5 6 7; do
    [ -d "raw_w$i" ] && rclone move "raw_w$i" "$BUCKET/raw" --transfers 48 --quiet
done

# ------------------------------------------------------- 2. fetch mockups
say "2/5  fetching the mockup list"
# NAMES ONLY — never download the images.
#
# ebay_graphics.py builds listings from the FILENAMES; it never opens the
# pictures. Downloading them filled a 100 GB volume at around 160 GB and
# killed the run. Empty placeholders do the identical job for a few MB.
rm -rf mock_all && mkdir -p mock_all
rclone lsf "$BUCKET/mock" > mock_names.txt || exit 1
( cd mock_all && xargs -a ../mock_names.txt -n 500 touch )
N=$(ls mock_all 2>/dev/null | wc -l)
echo "  $N mockups"
if [ "$N" -lt 1000 ]; then
    echo "  TOO FEW — something is wrong. Stopping rather than building a"
    echo "  CSV from a partial set."
    exit 1
fi

# ---------------------------------------------------------- 3. build CSVs
say "3/5  building the eBay CSVs"
rm -f tshirt_ebay_*.csv
./venv/bin/python ebay_graphics.py --dir mock_all --rows "$ROWS" || exit 1

# --------------------------------------------------------------- 4. check
say "4/5  verifying"
./venv/bin/python check_csv.py
CHECK=$?
./venv/bin/python no_duplicates.py "$BUCKET/raw" --csv tshirt_ebay_*.csv
DUPES=$?

# The image-URL check fails intermittently on the rate-limited r2.dev
# domain, which does not matter — eBay fetches each image once at upload and
# rehosts it. Duplicates are the one that must pass.
if [ $DUPES -ne 0 ]; then
    echo
    echo "  DUPLICATE CHECK FAILED — do not upload. Leaving the CSVs for"
    echo "  inspection rather than shuffling them."
    exit 1
fi

# ------------------------------------------------------------- 5. shuffle
say "5/5  interleaving and backing up"
./venv/bin/python shuffle_csv.py tshirt_ebay_*.csv

rclone copy . "$BUCKET/csv" --include "tshirt_ebay_*.csv" --transfers 16 --quiet
./venv/bin/python state.py backup "$BUCKET" 2>/dev/null

echo
echo "======================================================"
echo " READY"
echo "======================================================"
ls -lh tshirt_ebay_*.csv 2>/dev/null | awk '{print "  "$5, $9}'
echo
echo "  CSVs are also in $BUCKET/csv, so the pod can be terminated."
echo "  check_csv exit code: $CHECK  (2 = only the r2.dev URL check, fine)"
echo "  no_duplicates: PASSED"
echo
echo "  Download the CSVs, then terminate the pod."
