"""
watchdog.py — auto-backup and a heartbeat, so a dead pod announces itself.

THE PROBLEM
    A pod was terminated and it went unnoticed. Checking manually only works
    if you remember to check, and the moment you need the state most is the
    moment the machine holding it has gone.

    Two things fix that, and neither needs anyone to remember anything:

    1. The state is backed up on a timer, not at the end. Termination loses
       minutes, not a batch.
    2. A heartbeat file is written to R2 every cycle, carrying the progress
       counts and a timestamp. Anything, anywhere, can read that file and say
       whether the run is alive — no access to the pod required.

    Start it once, right after launching generation:

        nohup ./venv/bin/python watchdog.py r2:tshirt-mockups/art \\
            > watchdog.log 2>&1 &

    Then from ANY machine, at any time:

        python3 status.py r2:tshirt-mockups/art

    which reports "running, last seen 2 minutes ago" or "STOPPED 6 hours ago".
"""

import argparse, json, os, re, subprocess, time
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("bucket", help="e.g. r2:tshirt-mockups/art")
ap.add_argument("--every", type=int, default=300, help="seconds between cycles")
ap.add_argument("--files", nargs="*",
                default=["used_designs.txt", "generation_queue.csv"])
args = ap.parse_args()

REMOTE = args.bucket.rstrip("/") + "/state"


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def progress():
    """Read the worker logs for where each one has got to."""
    out = {}
    for f in sorted(os.listdir(".")):
        m = re.match(r"^(w\d+)\.log$", f)
        if not m:
            continue
        done = total = 0
        try:
            with open(f, errors="ignore") as fh:
                for line in fh:
                    g = re.search(r"\[(w\d+)\]\s+([\d,]+)/([\d,]+)", line)
                    if g:
                        done = int(g.group(2).replace(",", ""))
                        total = int(g.group(3).replace(",", ""))
        except OSError:
            continue
        out[m.group(1)] = {"done": done, "total": total}
    return out


def alive():
    return sh("pgrep -f pod_sdxl.py").returncode == 0


print(f"watchdog started, every {args.every}s -> {REMOTE}", flush=True)
cycle = 0

while True:
    cycle += 1
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    prog = progress()
    running = alive()

    # --- back the state up ------------------------------------------------
    backed, failed = [], []
    for f in args.files:
        if not os.path.exists(f):
            continue
        r = sh(f"rclone copyto '{f}' '{REMOTE}/{f}'")
        (backed if r.returncode == 0 else failed).append(f)

    # --- write the heartbeat ---------------------------------------------
    beat = {
        "updated": stamp,
        "generating": running,
        "workers": prog,
        "done": sum(w["done"] for w in prog.values()),
        "total": sum(w["total"] for w in prog.values()),
        "backed_up": backed,
        "backup_failed": failed,
        "host": os.uname().nodename,
    }
    with open(".heartbeat.json", "w") as f:
        json.dump(beat, f, indent=1)
    hb = sh(f"rclone copyto '.heartbeat.json' '{REMOTE}/heartbeat.json'")

    done, total = beat["done"], beat["total"]
    pct = f"{done/total*100:.1f}%" if total else "?"
    note = "" if hb.returncode == 0 else "   HEARTBEAT UPLOAD FAILED"
    if failed:
        note += f"   BACKUP FAILED: {', '.join(failed)}"
    print(f"[{stamp}] {'running' if running else 'NOT RUNNING'}  "
          f"{done:,}/{total:,} {pct}{note}", flush=True)

    # Once generation has stopped, do one final backup and exit rather than
    # looping forever on a pod that is only being paid for out of habit.
    if not running and cycle > 1:
        print("generation has stopped — final backup, then exiting", flush=True)
        for f in args.files:
            if os.path.exists(f):
                sh(f"rclone copyto '{f}' '{REMOTE}/{f}'")
        break

    time.sleep(args.every)
