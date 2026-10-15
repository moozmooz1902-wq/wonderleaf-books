#!/usr/bin/env python3
"""Read a RunPod /pods response on stdin, print the wa-v3 shard numbers up.

Prints ERR, and nothing else, when the answer cannot be trusted. That
distinction is the whole point of the file. fill_shards.sh used to inline
this, and an unparseable or incomplete response came out as an EMPTY shard
list - which auto mode reads as "those shards are missing, launch them".

On 15 Oct at 22:05 that launched a second wa-v3-4 and a second wa-v3-6, four
seconds apart, seven minutes after the filler was restarted, while both
originals were running happily from 16:25 and 17:14. Two extra pods at
$0.22/hr generating SKUs that already existed. Same family as the watchdog
bug the same evening: a failed read that looks exactly like a real answer.

Nothing here decides to launch anything. It only reports what it can see,
and says so when it cannot see.
"""
import json
import re
import sys


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        print("ERR")
        return
    try:
        d = json.loads(raw)
    except Exception:
        print("ERR")
        return
    if isinstance(d, dict):
        d = d.get("pods")
    if not isinstance(d, list):
        print("ERR")
        return
    up = sorted({
        re.sub(r"^wa-v3-", "", p["name"])
        for p in d
        if isinstance(p, dict)
        and p.get("desiredStatus") == "RUNNING"
        and str(p.get("name", "")).startswith("wa-v3-")
    }, key=lambda s: int(s) if s.isdigit() else 0)
    print(" ".join(up))


if __name__ == "__main__":
    main()
