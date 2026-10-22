#!/bin/bash
# Rebuild every store with the 12-variation pricing. Retries because
# 16-vCPU community capacity is intermittent - and "NO CAPACITY" from the
# launcher means only that no tier returned an id, never that the balance
# is gone. Check the balance with a raw create before assuming.
cd "$(dirname "$0")"
for b in luxvia-art posterleaf-store1 lunar-kms mercury-usm; do
  for try in 1 2 3 4 5 6 7 8 9 10 11 12; do
    out=$(timeout 180 python3 launch_build.py --store "$b" 2>&1)
    echo "$out" | tail -1
    if echo "$out" | grep -q "/hr"; then break; fi
    echo "  $(date -u +%H:%M:%S) $b: no capacity, retry $try in 90s"
    sleep 90
  done
done
echo "ALL FOUR BUILD PODS LAUNCHED $(date -u +%H:%M:%S)"
