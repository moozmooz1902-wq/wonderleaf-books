"""
status.py — where are we, and where do we start from?

THE PROBLEM THIS SOLVES
    Pods get terminated. Weeks pass. The queue file, the ledger and the logs
    all lived on a machine that no longer exists, and the only question that
    matters is: what has already been made, and what is safe to make next?

    R2 is the answer, because every generated design is stored as <index>.png.
    The bucket IS the record. This reads it and reports the position, so
    picking the work back up months later needs no notes and no memory.

    python3 status.py r2:tshirt-mockups/art
    python3 status.py r2:store1 r2:store2 r2:store3

WHAT IT TELLS YOU
    how many designs exist, how many have mockups, how many are still
    unprocessed, whether the local ledger matches, and exactly what to run
    next.
"""

import argparse, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("buckets", nargs="+",
                help="bucket roots, e.g. r2:tshirt-mockups/art")
ap.add_argument("--ledger", default="used_designs.txt")
ap.add_argument("--space", type=int, default=0,
                help="total design space; read from graphics.py if omitted")
args = ap.parse_args()


def lsf(path):
    r = subprocess.run(f"rclone lsf {path}", shell=True,
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    out = set()
    for line in r.stdout.splitlines():
        m = re.match(r"^(\d+)\.(png|jpg|jpeg|tif)$", line.strip(), re.I)
        if m:
            out.add(int(m.group(1)))
    return out


space = args.space
if not space:
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from graphics import TOTAL_SPACE
        space = TOTAL_SPACE
    except Exception:
        space = 0

# --- heartbeat: is a run alive right now? --------------------------------
# watchdog.py writes this to R2 every few minutes during a run, so this
# question is answerable from any machine without touching the pod. A pod
# terminated overnight shows up here instead of being discovered days later.
def _heartbeat(bucket):
    import json, tempfile
    from datetime import datetime, timezone
    tmp = os.path.join(tempfile.gettempdir(), "_hb.json")
    r = subprocess.run(
        f"rclone copyto '{bucket.rstrip('/')}/state/heartbeat.json' '{tmp}'",
        shell=True, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    try:
        with open(tmp) as f:
            b = json.load(f)
        os.remove(tmp)
    except Exception:
        return None
    try:
        age = (datetime.now(timezone.utc)
               - datetime.fromisoformat(b["updated"])).total_seconds()
    except Exception:
        age = None
    b["age"] = age
    return b


print("=" * 62)
print(" WHERE WE ARE")
print("=" * 62)

hb = _heartbeat(args.buckets[0])
if hb:
    age = hb.get("age")
    if age is None:
        when = "unknown"
    elif age < 120:
        when = f"{int(age)} seconds ago"
    elif age < 7200:
        when = f"{int(age/60)} minutes ago"
    else:
        when = f"{age/3600:.1f} hours ago"

    done, total = hb.get("done", 0), hb.get("total", 0)
    pct = f" ({done/total*100:.1f}%)" if total else ""

    if hb.get("generating") and age is not None and age < 900:
        print(f"\n  RUNNING — last seen {when}")
        print(f"    {done:,} of {total:,} generated{pct}")
        if total and done:
            left = (total - done) / max(done, 1)
            print(f"    on this pace, roughly {left * age / 3600:.1f}h of work left"
                  if age else "")
    else:
        print(f"\n  NOT RUNNING — last heartbeat {when}")
        print(f"    reached {done:,} of {total:,}{pct} before it stopped")
        print("    The pod was terminated or the run finished. Nothing is lost:")
        print("    the designs are in R2 and the ledger can be rebuilt from them.")
    if hb.get("backup_failed"):
        print(f"    WARNING: backup was failing for {', '.join(hb['backup_failed'])}")
else:
    print("\n  no heartbeat in R2 — either no run has used watchdog.py yet,")
    print("  or the state folder is empty. Start one alongside generation with:")
    print(f"    nohup python3 watchdog.py {args.buckets[0]} > watchdog.log 2>&1 &")

all_raw, all_mock = set(), set()
for b in args.buckets:
    raw = lsf(f"{b}/raw")
    mock = lsf(f"{b}/mock")
    if raw is None:
        print(f"\n  {b}  — cannot read, check the path and rclone config")
        continue
    mock = mock or set()
    all_raw |= raw
    all_mock |= mock
    print(f"\n  {b}")
    print(f"    generated : {len(raw):,}")
    print(f"    mockups   : {len(mock):,}")
    pending = raw - mock
    if pending:
        print(f"    unprocessed: {len(pending):,}  <- postrun.py has work to do")

print("\n" + "-" * 62)
print(f"  TOTAL generated across all buckets : {len(all_raw):,}")
print(f"  TOTAL with mockups                 : {len(all_mock):,}")
if space:
    print(f"  design space                       : {space:,}")
    print(f"  used                               : {len(all_raw)/space*100:.2f}%")
    print(f"  remaining                          : {space - len(all_raw):,}")

# --- does the local ledger agree? ----------------------------------------
print("\n" + "-" * 62)
print("  LEDGER")
if os.path.exists(args.ledger):
    led = set()
    with open(args.ledger, encoding="utf-8") as f:
        for line in f:
            if line.strip().isdigit():
                led.add(int(line.strip()))
    print(f"    local file : {len(led):,} entries")
    missing = all_raw - led
    extra = led - all_raw

    if missing:
        print(f"    !! {len(missing):,} generated designs are NOT in the ledger")
        print("       The next batch could reuse them. Rebuild before running:")
        print(f"       python3 rebuild_ledger.py " +
              " ".join(f"{b}/raw" for b in args.buckets))
    if extra:
        # queued but never generated, usually because a pod died mid-run
        print(f"    {len(extra):,} ledger entries have no file — queued but not")
        print("       generated, or rejected. Rebuilding from R2 frees them.")
    if not missing and not extra:
        print("    matches R2 exactly")
else:
    print(f"    no local ledger ({args.ledger})")
    print("    This is expected on a fresh pod. Rebuild it from R2 first:")
    print(f"      python3 rebuild_ledger.py " +
          " ".join(f"{b}/raw" for b in args.buckets))

# --- what to do next -----------------------------------------------------
print("\n" + "=" * 62)
print(" WHAT TO RUN NEXT")
print("=" * 62)
step = 1
if not os.path.exists(args.ledger) or (all_raw - led if os.path.exists(args.ledger) else True):
    print(f"\n  {step}. Rebuild the ledger from R2 — this is the step that stops")
    print("     duplicates, and it works even though the old pod is gone.")
    print(f"       python3 rebuild_ledger.py " +
          " ".join(f"{b}/raw" for b in args.buckets))
    step += 1

pending_all = all_raw - all_mock
if pending_all:
    print(f"\n  {step}. Finish processing {len(pending_all):,} designs that have no")
    print("     mockup yet — they are generated and paid for already.")
    print("       nice -n 10 python3 postrun.py")
    step += 1

print(f"\n  {step}. Queue the next batch. It excludes everything above by itself.")
print("       python3 pick.py --count 282000        # 200,000 kept")
print("       python3 audit.py generation_queue.csv")
step += 1

print(f"\n  {step}. Generate, then verify before uploading.")
print("       python3 no_duplicates.py " +
      " ".join(f"{b}/raw" for b in args.buckets) + " --csv tshirt_ebay_*.csv")
print()
