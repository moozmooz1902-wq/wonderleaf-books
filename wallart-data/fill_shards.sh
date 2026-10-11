#!/bin/bash
# Keep trying until every shard is running.
#
# Community capacity for these cards is not absent, it is MOMENTARY. Probed
# 11 Oct: the same request that answered "no instances currently available"
# five times in a row succeeded on the sixth, seconds later, and an 80 GB
# container disk succeeded while 50, 40 and 30 GB all failed in the same
# minute. So a single attempt per shard is the wrong shape; retrying is.
#
# Costs nothing while it fails, and relaunch.sh carries the $0.32/hr ceiling.
#   usage: fill_shards.sh <nshards> <deadline-minutes> <shard> [shard...]
N=$1; MINS=$2; shift 2
TODO=("$@")
END=$(( $(date +%s) + MINS * 60 ))
declare -A SKIP
while [ ${#TODO[@]} -gt 0 ] && [ "$(date +%s)" -lt "$END" ]; do
  LEFT=()
  for K in "${TODO[@]}"; do
    if [ -n "${SKIP[$K]}" ] && [ "$(date +%s)" -lt "${SKIP[$K]}" ]; then
      LEFT+=("$K"); continue
    fi
    OUT=$(bash relaunch.sh "$N" "$K")
    echo "$(date -u +%H:%M:%S)  $OUT"
    case "$OUT" in
      # A shard that keeps being offered a card over the ceiling will create
      # and terminate a pod every pass, which is churn for nothing. Back that
      # one off for a few minutes instead; plain no-capacity retries fast.
      *"OVER CEILING"*) LEFT+=("$K"); SKIP[$K]=$(( $(date +%s) + 300 )) ;;
      *"NO CAPACITY"*)  LEFT+=("$K") ;;
    esac
  done
  TODO=("${LEFT[@]}")
  [ ${#TODO[@]} -gt 0 ] && sleep 45
done
if [ ${#TODO[@]} -gt 0 ]; then
  echo "still unfilled after ${MINS}m: ${TODO[*]}"
else
  echo "all shards filled"
fi
