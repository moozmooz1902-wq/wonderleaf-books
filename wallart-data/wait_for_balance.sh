#!/bin/bash
# Wait for the RunPod balance to come back, then start the shard filler.
#
# When the account ran dry at 14:02 on 16 Oct the filler was left running so
# the fleet would refill by itself. That works, but it is rude: auto mode
# makes a listing call, a confirm call and a create attempt for each of
# twelve missing shards every 45 seconds - roughly two thousand calls an
# hour, every one of them refused for the same reason.
#
# There is no balance endpoint on either API (every REST path checked, and
# the GraphQL myself{} query returns null for this key), so the only honest
# probe is to try to create something and read the refusal. This does that
# ONCE every two minutes - thirty calls an hour instead of two thousand -
# and hands over to fill_shards.sh the moment the refusal changes.
#
# A probe that unexpectedly SUCCEEDS is deleted immediately; it exists to ask
# a question, not to do work.
INTERVAL=120
KEY="${RUNPOD_API_KEY}"
API=https://rest.runpod.io/v1
LOG="${1:-/dev/stdout}"

probe() {
  curl -sS --max-time 45 -X POST -H "Authorization: Bearer $KEY" \
    -H "Content-Type: application/json" \
    -d '{"name":"wa-balance-probe","imageName":"runpod/base:0.7.0-ubuntu2404","containerDiskInGb":10,"volumeInGb":0,"computeType":"CPU","cpuFlavorIds":["cpu3g","cpu3c"],"vcpuCount":2}' \
    "$API/pods" 2>/dev/null
}

while true; do
  OUT="$(probe)"
  case "$OUT" in
    *"balance is too low"*)
      echo "$(date -u +%H:%M:%S)  still no balance" ;;
    *'"id"'*)
      ID=$(printf '%s' "$OUT" | python3 -c "import sys,re;d=sys.stdin.read();m=re.search(r'\"id\": ?\"([a-z0-9]+)\"',d);print(m.group(1) if m else '')")
      [ -n "$ID" ] && curl -sS -X DELETE -H "Authorization: Bearer $KEY" "$API/pods/$ID" >/dev/null 2>&1
      echo "$(date -u +%H:%M:%S)  BALANCE IS BACK - probe pod $ID created and deleted"
      echo "$(date -u +%H:%M:%S)  starting the shard filler"
      exec env CLIP_GATE=1 bash "$(dirname "$0")/fill_shards.sh" 12 110 auto
      ;;
    *"no instances currently available"*)
      # Capacity, not money. Says nothing about the balance either way, so
      # keep waiting rather than concluding anything.
      echo "$(date -u +%H:%M:%S)  probe hit a capacity wall, no verdict" ;;
    *)
      echo "$(date -u +%H:%M:%S)  unexpected: $(printf '%s' "$OUT" | head -c 120)" ;;
  esac
  sleep "$INTERVAL"
done
