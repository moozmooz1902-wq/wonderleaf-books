"""
state.py — keep the operation's memory in Cloudflare, not on a pod.

WHY
    Pods are terminated between batches. Everything that says what has already
    been made — the ledger, the queue, the run logs — lives on that pod and
    dies with it. R2 is the only thing that persists.

    pick.py backs the state up automatically, but a backup nobody has tested
    is not a backup. This makes it explicit and checkable:

        python3 state.py backup    r2:tshirt-mockups/art
        python3 state.py check     r2:tshirt-mockups/art
        python3 state.py restore   r2:tshirt-mockups/art

    "check" is the important one. It downloads what is stored, compares it
    against what is local, and says plainly whether a fresh pod could pick the
    work up. Run it before terminating anything.

WHAT IS STORED
    used_designs.txt      every design index ever queued
    generation_queue.csv  the current batch
    Both go to <bucket>/state/.

    Note that R2 holds a SECOND, independent record: the raw filenames
    themselves. rebuild_ledger.py reconstructs the ledger from those, so even
    if this backup were lost the position is recoverable.
"""

import argparse, hashlib, os, shutil, subprocess, sys

FILES = ["used_designs.txt", "generation_queue.csv"]

ap = argparse.ArgumentParser()
ap.add_argument("action", choices=["backup", "restore", "check"])
ap.add_argument("bucket", help="e.g. r2:tshirt-mockups/art")
ap.add_argument("--force", action="store_true",
                help="restore over local files that already exist")
args = ap.parse_args()

REMOTE = args.bucket.rstrip("/") + "/state"


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def digest(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def lines(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8", errors="ignore") as f:
        return sum(1 for _ in f)


# --- rclone must actually be working before anything is trusted -----------
probe = run(f"rclone lsd {args.bucket.split('/')[0]}")
if probe.returncode != 0:
    print("rclone cannot reach the remote:")
    print("  " + (probe.stderr.strip().splitlines() or ["unknown error"])[0][:90])
    sys.exit(1)


if args.action == "backup":
    print(f"backing up to {REMOTE}\n")
    ok = True
    for f in FILES:
        if not os.path.exists(f):
            print(f"  {f:<24} not present locally, skipped")
            continue
        r = run(f"rclone copyto '{f}' '{REMOTE}/{f}'")
        if r.returncode != 0:
            print(f"  {f:<24} FAILED — {r.stderr.strip()[:60]}")
            ok = False
            continue
        # read it straight back and compare, so a silent failure cannot pass
        tmp = f".verify_{f}"
        run(f"rclone copyto '{REMOTE}/{f}' '{tmp}'")
        same = digest(tmp) == digest(f)
        if os.path.exists(tmp):
            os.remove(tmp)
        print(f"  {f:<24} {lines(f):>9,} lines   "
              f"{'verified' if same else 'MISMATCH after upload'}")
        ok = ok and same
    print()
    print("backup verified" if ok else "BACKUP INCOMPLETE — do not terminate the pod")
    sys.exit(0 if ok else 1)


if args.action == "check":
    print(f"checking {REMOTE}\n")
    missing = []
    for f in FILES:
        tmp = f".check_{f}"
        r = run(f"rclone copyto '{REMOTE}/{f}' '{tmp}'")
        if r.returncode != 0 or not os.path.exists(tmp):
            print(f"  {f:<24} NOT IN R2")
            missing.append(f)
            continue
        rl, ll = lines(tmp), lines(f)
        same = digest(tmp) == digest(f) if os.path.exists(f) else None
        note = ("identical to local" if same
                else "differs from local" if same is False
                else "no local copy to compare")
        print(f"  {f:<24} {rl:>9,} lines in R2   {note}")
        if same is False:
            print(f"     local has {ll:,} lines — back up again if local is newer")
        os.remove(tmp)
    print()
    if missing:
        print("NOT SAFE to lose this pod yet. Run:")
        print(f"  python3 state.py backup {args.bucket}")
        sys.exit(1)
    print("Safe to terminate. A fresh pod can restore with:")
    print(f"  python3 state.py restore {args.bucket}")
    print("or rebuild independently from the raw filenames:")
    print(f"  python3 rebuild_ledger.py {args.bucket}/raw")
    sys.exit(0)


if args.action == "restore":
    print(f"restoring from {REMOTE}\n")
    got = 0
    for f in FILES:
        if os.path.exists(f) and not args.force:
            print(f"  {f:<24} already here, left alone (use --force to overwrite)")
            continue
        r = run(f"rclone copyto '{REMOTE}/{f}' '{f}'")
        if r.returncode != 0 or not os.path.exists(f):
            print(f"  {f:<24} not in R2")
            continue
        print(f"  {f:<24} {lines(f):>9,} lines restored")
        got += 1
    print()
    if got:
        print("Restored. Before queuing anything, confirm it matches what is")
        print("actually in the bucket — the ledger records what was QUEUED, and")
        print("a run that died early would have queued more than it generated:")
        print(f"  python3 status.py {args.bucket}")
    else:
        print("Nothing restored. Rebuild from the raw filenames instead:")
        print(f"  python3 rebuild_ledger.py {args.bucket}/raw")
