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
# Prints the shard numbers that are up, or the single word ERR when the
# answer cannot be trusted. See shards_up.py for why those must not be the
# same thing: an unreadable response used to come out as an empty list, which
# auto mode reads as "every shard is missing".
running_shards() {
  curl -sS --max-time 60 https://rest.runpod.io/v1/pods \
    | python3 "$(dirname "$0")/shards_up.py"
}
if [ "$AUTO" = "1" ]; then
  TODO=()
else
  TODO=("$@")
fi
END=$(( $(date +%s) + MINS * 60 ))
declare -A SKIP
# A pod that has just been created is not RUNNING yet, so the next pass 45
# seconds later sees that shard missing and launches ANOTHER one. The
# confirm-read does not help here, because both reads are telling the truth -
# the pod genuinely is not running yet. So remember what was just launched
# and leave it alone long enough to come up. Measured on 15 Oct: a shard
# takes about two minutes to reach RUNNING, so four is a safe floor.
declare -A JUST
LAUNCH_COOLDOWN=240
while [ "$(date +%s)" -lt "$END" ]; do
  if [ "$AUTO" = "1" ]; then
    UP_RAW="$(running_shards)"
    if [ "$UP_RAW" = "ERR" ]; then
      echo "$(date -u +%H:%M:%S)  pod list unreadable, skipping this pass"
      sleep 60; continue
    fi
    UP=" $UP_RAW "
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
    if [ -n "${JUST[$K]}" ] && \
       [ $(( $(date +%s) - ${JUST[$K]} )) -lt $LAUNCH_COOLDOWN ]; then
      echo "$(date -u +%H:%M:%S)  shard $K launched $(( $(date +%s) - ${JUST[$K]} ))s ago, still coming up"
      LEFT+=("$K"); continue
    fi
    # CONFIRM IT IS STILL MISSING, from a second independent read, before
    # spending money on it. The 22:05 duplicates on 15 Oct came from acting
    # on one reading; a shard that is actually up appears in both, and a
    # reading that cannot be trusted is skipped rather than acted on.
    CONFIRM="$(running_shards)"
    if [ "$CONFIRM" = "ERR" ]; then
      echo "$(date -u +%H:%M:%S)  shard $K: second read failed, not launching"
      LEFT+=("$K"); continue
    fi
    case " $CONFIRM " in
      *" $K "*)
        echo "$(date -u +%H:%M:%S)  shard $K is up after all, not launching"
        continue ;;
    esac
    OUT=$(bash relaunch.sh "$N" "$K")
    case "$OUT" in
      *NO\ CAPACITY*|*OVER\ CEILING*) ;;      # nothing was created
      *) JUST[$K]=$(date +%s) ;;
    esac
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
