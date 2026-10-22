#!/bin/bash
# Audit each bucket separately, writing one drop list per bucket.
#
# The global run over all 960,517 panels was killed twice - once by a
# 40-minute wrapper, once by a container restart - after about an hour of
# compare at 55% memory, leaving nothing. Per bucket it is a quarter of the
# panels and a quarter of the memory, each run finishes in minutes, and a
# restart costs one bucket instead of everything.
#
# Sound because allocate.store_for puts a design in exactly ONE store, so a
# near-duplicate pair of the same design cannot span buckets. Two DIFFERENT
# designs that happen to be near neighbours could land in different stores,
# and this will not catch that - but they would sit on different eBay
# accounts rather than competing inside one shop, which is the harm the
# audit exists to prevent. The within-store guarantee is unchanged.
#
# luxvia-art is not here: it was audited and dropped before its delivered
# build, and that file is not being rebuilt.
cd "$(dirname "$0")"
for b in posterleaf-store1 lunar-kms mercury-usm; do
  echo "=== $b  $(date -u +%H:%M:%S) ==="
  python3 -u dup_audit.py --src "hashes_$b" --drop "drop_$b.txt" || echo "FAILED: $b"
  echo "--- $b done $(date -u +%H:%M:%S), drop list: $(wc -l < "drop_$b.txt" 2>/dev/null || echo 0) lines"
done
cat drop_posterleaf-store1.txt drop_lunar-kms.txt drop_mercury-usm.txt > drop_skus.txt 2>/dev/null
echo "COMBINED drop_skus.txt: $(wc -l < drop_skus.txt) lines"
