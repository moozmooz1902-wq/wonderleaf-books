#!/bin/bash
# Keep the render fleet full until every part reports COMPLETE.
#
# Same shape as fill_shards.sh and for the same reasons: community capacity
# is momentary rather than absent, a pod takes a couple of minutes to reach
# RUNNING so a just-launched part must not be launched again, and a part
# that has finished its ranges is dropped rather than replaced.
#   usage: fill_render.sh <parts> <minutes>
N=${1:-12}; MINS=${2:-600}
HERE="$(cd "$(dirname "$0")" && pwd)"
DONEFILE="$HERE/done_parts.txt"
END=$(( $(date +%s) + MINS * 60 ))
declare -A JUST
while [ "$(date +%s)" -lt "$END" ]; do
  RAW=$(curl -sS --max-time 60 https://rest.runpod.io/v1/pods)
  UP=$(echo "$RAW" | python3 -c "
import json,sys
try: d=json.load(sys.stdin)
except Exception: print('ERR'); raise SystemExit
if not isinstance(d,list): print('ERR'); raise SystemExit
for p in d:
    if p.get('desiredStatus')=='RUNNING' and str(p.get('name','')).startswith('wa-render-'):
        print(p['name'].rsplit('-',1)[-1])
" 2>/dev/null)
  # An unreadable list must not read as "every part is missing" - that is
  # the pods()-returns-None lesson, and here it would launch twelve pods.
  if [ "$UP" = "ERR" ]; then sleep 60; continue; fi
  for k in $(seq 1 "$N"); do
    grep -qx "$k" "$DONEFILE" 2>/dev/null && continue
    echo "$UP" | grep -qx "$k" && continue
    now=$(date +%s)
    [ -n "${JUST[$k]}" ] && [ $(( now - ${JUST[$k]} )) -lt 300 ] && continue
    echo "$(date -u +%H:%M:%S) launching part $k"
    python3 "$HERE/../launch_render.py" --parts "$N" --only "$k" \
        --name wa-render --max-hours 10 --oversub 2
    JUST[$k]=$now
  done
  sleep 120
done
echo "fill_render window over"
