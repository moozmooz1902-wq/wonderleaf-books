#!/usr/bin/env python3
"""Delete diagnostic pods that nothing is watching any more.

Every diagnostic pod here is reaped by its LAUNCHER, in a finally. That works
until the launcher dies, and on 16 Oct the container restarted three times in
two hours - once in the middle of r2_count_stores.py, which left
ce2u3ba1ho09iw billing with nobody waiting on it. A finally does not run when
the process is SIGKILLed.

So this is the backstop: it does not know or care what launched anything, it
just looks at what is RUNNING and applies a deadline per job type. Shards are
never touched.

Deadlines are the job's own shape, not one number. The counter and the age
histogram are listing passes measured in minutes; the sweep and the audit
download the whole catalogue and legitimately run over an hour. A pod still
inside its deadline is reported and left alone, so a running audit is never
killed by the thing meant to catch a dead one.

    python3 reap_orphans.py            # report only, deletes nothing
    python3 reap_orphans.py --delete   # actually reap
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

API = "https://rest.runpod.io/v1"

# minutes a job of this name may run before it counts as orphaned
DEADLINES = {
    "wallart-count": 20,
    "wallart-ages": 20,
    "wallart-sweep": 180,
    "wallart-sweep-after": 180,
    "wallart-audit": 240,
}
DEFAULT_DEADLINE = 60


def pods():
    tok = os.environ.get("RUNPOD_API_KEY", "")
    out = subprocess.run(
        ["curl", "-sS", "--max-time", "60", "-H", f"Authorization: Bearer {tok}",
         f"{API}/pods"], capture_output=True, text=True).stdout
    try:
        d = json.loads(out)
    except Exception:
        return None                      # unreadable is NOT "nothing running"
    if isinstance(d, dict):
        d = d.get("pods")
    return d if isinstance(d, list) else None


def age_minutes(p):
    t = p.get("lastStartedAt") or p.get("createdAt") or ""
    t = t.replace(" UTC", "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f %z", "%Y-%m-%d %H:%M:%S %z"):
        try:
            return (datetime.now(timezone.utc)
                    - datetime.strptime(t, fmt)).total_seconds() / 60
        except Exception:
            pass
    return None                          # unknown age is never reaped


def main():
    do_delete = "--delete" in sys.argv
    d = pods()
    if d is None:
        print("pod list unreadable - doing nothing, which is the safe answer")
        return 1
    running = [p for p in d if p.get("desiredStatus") == "RUNNING"]
    others = [p for p in running
              if not str(p.get("name", "")).startswith("wa-v3-")]
    print(f"{len(running)} running, "
          f"{len(running) - len(others)} shards, {len(others)} diagnostic")
    reaped = 0
    for p in others:
        name, pid = p.get("name", "?"), p["id"]
        mins, limit = age_minutes(p), DEADLINES.get(p.get("name"), DEFAULT_DEADLINE)
        if mins is None:
            print(f"  {pid} {name}: age unknown, left alone")
            continue
        if mins <= limit:
            print(f"  {pid} {name}: {mins:.0f}m of {limit}m, still within "
                  f"its deadline - left alone")
            continue
        if not do_delete:
            print(f"  {pid} {name}: {mins:.0f}m, OVER its {limit}m deadline "
                  f"- would delete (pass --delete)")
            continue
        tok = os.environ.get("RUNPOD_API_KEY", "")
        subprocess.run(["curl", "-sS", "-X", "DELETE", "-H",
                        f"Authorization: Bearer {tok}", f"{API}/pods/{pid}"],
                       capture_output=True, text=True)
        print(f"  {pid} {name}: {mins:.0f}m, over its {limit}m deadline "
              f"- DELETED")
        reaped += 1
    if not others:
        print("  no diagnostic pods")
    elif do_delete:
        print(f"reaped {reaped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
