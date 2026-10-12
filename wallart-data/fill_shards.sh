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
#
# With the word "auto" in place of a shard list, it works out which of
# 1..N are not running on each pass. That is what you want while pods are
# expiring on a stagger: the six oldest hit --max-hours ten hours after
# they started, which is ten different minutes, and a fixed list written
# in advance is wrong by the second expiry.
N=$1; MINS=$2; shift 2
AUTO=0
[ "$1" = "auto" ] && AUTO=1
running_shards() {
  curl -sS --max-time 60 https://rest.runpod.io/v1/pods | python3 -c "
import sys, json, re
d = json.load(sys.stdin); d = d if isinstance(d, list) else d.get('pods', [])
print(' '.join(sorted(
    re.sub(r'^wa-v3-', '', p['name'])
    for p in d
    if p.get('desiredStatus') == 'RUNNING'
    and str(p.get('name', '')).startswith('wa-v3-'))))"
}
if [ "$AUTO" = "1" ]; then
  TODO=()
else
  TODO=("$@")
fi
END=$(( $(date +%s) + MINS * 60 ))
declare -A SKIP
while [ "$(date +%s)" -lt "$END" ]; do
  if [ "$AUTO" = "1" ]; then
    UP=" $(running_shards) "
    TODO=()
    for K in $(seq 1 "$N"); do
      case "$UP" in *" $K "*) ;; *) TODO+=("$K") ;; esac
    done
    if [ ${#TODO[@]} -eq 0 ]; then
      sleep 60; continue
    fi
  elif [ ${#TODO[@]} -eq 0 ]; then
    break
  fi
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
  [ "$AUTO" = "1" ] || TODO=("${LEFT[@]}")
  sleep 45
done
if [ "$AUTO" = "1" ]; then
  echo "window over; running now: $(running_shards)"
elif [ ${#TODO[@]} -gt 0 ]; then
  echo "still unfilled after ${MINS}m: ${TODO[*]}"
else
  echo "all shards filled"
fi
