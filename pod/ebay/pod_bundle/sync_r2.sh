#!/usr/bin/env bash
# Upload finished files to R2 and delete the local copy, so a 142GB render
# fits on a 100GB volume. Run this in a SECOND terminal, alongside run.py.
#
#   export R2_BUCKET=tshirt-xxx
#   bash sync_r2.sh
set -uo pipefail
: "${R2_BUCKET:?set R2_BUCKET first}"
HERE="$(cd "$(dirname "$0")" && pwd)"

while true; do
  for kind in print mock; do
    dir="$HERE/$kind"
    [ -d "$dir" ] || continue
    # art/raw and art/mock are the paths the existing fulfilment tools expect
    remote=$([ "$kind" = print ] && echo raw || echo mock)
    find "$dir" -type f \( -name '*.png' -o -name '*.jpg' \) -mmin +1 -print0 \
      | xargs -0 -P 16 -I{} sh -c '
          f="$1"
          if rclone copyto --s3-no-check-bucket "$f" \
             "r2:'"$R2_BUCKET"'/art/'"$remote"'/$(basename "$f")" -q; then
            rm -f "$f"
          fi' _ {}
  done
  p=$(find "$HERE/print" -type f 2>/dev/null | wc -l)
  m=$(find "$HERE/mock" -type f 2>/dev/null | wc -l)
  echo "$(date +%H:%M:%S)  awaiting upload: print=$p mock=$m"
  sleep 30
done
