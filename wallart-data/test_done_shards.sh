#!/bin/bash
# Does DONE_SHARDS drop exactly the finished stripes and nothing else?
# Runs the REAL stripe_done + TODO loop text lifted from fill_shards.sh,
# with the pod list faked, so no pods are created.
SRC=/home/user/wonderleaf-books/wallart-data/fill_shards.sh
eval "$(sed -n '/^DONE_SHARDS=/,/^}/p' "$SRC")"

build_todo() {   # $1 = N, $2 = space-separated running shards
  local N="$1" UP=" $2 " K; TODO=()
  for K in $(seq 1 "$N"); do
    stripe_done "$K" && continue
    case "$UP" in *" $K "*) ;; *) TODO+=("$K") ;; esac
  done
  echo "${TODO[*]}"
}

fail=0
check() {  # desc, expected, got
  if [ "$2" = "$3" ]; then printf '  ok    %-46s -> [%s]\n' "$1" "$3"
  else printf '  WRONG %-46s -> [%s], expected [%s]\n' "$1" "$3" "$2"; fail=1; fi
}

DONE_SHARDS=""
check "no skips, all 12 up"            ""            "$(build_todo 12 '1 2 3 4 5 6 7 8 9 10 11 12')"
check "no skips, 1 missing"            "1"           "$(build_todo 12 '2 3 4 5 6 7 8 9 10 11 12')"

DONE_SHARDS="1"
check "skip 1, 1 missing"              ""            "$(build_todo 12 '2 3 4 5 6 7 8 9 10 11 12')"
check "skip 1, 1 and 5 missing"        "5"           "$(build_todo 12 '2 3 4 6 7 8 9 10 11 12')"
check "skip 1, all up"                 ""            "$(build_todo 12 '1 2 3 4 5 6 7 8 9 10 11 12')"
check "skip 1, nothing up"             "2 3 4 5 6 7 8 9 10 11 12" "$(build_todo 12 '')"

DONE_SHARDS="1 11 12"
check "skip 1 11 12, none up"          "2 3 4 5 6 7 8 9 10" "$(build_todo 12 '')"
check "skip 1 11 12, 10 missing only"  "10"          "$(build_todo 12 '1 2 3 4 5 6 7 8 9 11 12')"

# Substring traps: "1" must not match 11 or 12, and "2" must not match 12.
DONE_SHARDS="1"
check "skip 1 does not skip 11 or 12"  "11 12"       "$(build_todo 12 '1 2 3 4 5 6 7 8 9 10')"
DONE_SHARDS="2"
check "skip 2 does not skip 12"        "12"          "$(build_todo 12 '1 2 3 4 5 6 7 8 9 10 11')"

[ "$fail" = "0" ] && echo "PASS" || { echo "FAIL"; exit 1; }
