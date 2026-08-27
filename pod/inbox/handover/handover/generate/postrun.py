"""
postrun.py — raw artwork -> print files -> mockups, in parallel chunks.

RUNS ALONGSIDE GENERATION.
    Generation is GPU-bound; the CPUs sit near idle. This uses those cores so
    the two stages overlap instead of running back to back.

WHY BOTH STEPS ARE PARALLEL
    The first version ran dtf.py single-threaded: ~3 seconds per image, so a
    4,000-file chunk took 3.3 hours and the whole job would have needed over
    100. Both the DTF conversion and the mockup build now run across every
    spare core, and each worker does convert-then-mockup on its own slice so
    the print file never has to be written and re-read.

    nice -n 10 ./venv/bin/python postrun.py

Resumable: anything already in R2 under mock/ is skipped.
"""

import argparse, csv, os, re, shutil, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("--chunk", type=int, default=4000)
ap.add_argument("--transfers", type=int, default=48,
                help="parallel R2 transfers. 16 was conservative and left the "
                     "job waiting on the network rather than the CPU; 48-64 "
                     "suits a pod with real bandwidth")
# Reads R2_REMOTE, which every other tool in the pipeline already uses.
#
# This used to default to r2:tshirt-mockups/art and ignore the environment.
# On the m12k run that meant a whole night spent reprocessing STORE 1's
# designs while the 360,000 new ones were never touched — and it cost a
# second pod to put right. With seven buckets and one hardcoded default,
# that was going to happen again.
ap.add_argument("--bucket",
                default=os.environ.get("R2_REMOTE", "r2:tshirt-mockups/art"))
ap.add_argument("--workers", type=int, default=0)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--watch", type=int, default=0, metavar="SECS",
                help="after clearing the queue, wait SECS and look for more "
                     "instead of exiting. Use --watch 300 when generation is "
                     "still running, so mockups keep pace instead of piling "
                     "up into a separate job at the end")
args = ap.parse_args()

WORK = "_proc"
os.makedirs(WORK, exist_ok=True)
if not args.workers:
    # leave a few cores for the generation processes feeding the GPUs
    args.workers = max(2, (os.cpu_count() or 8) - 6)


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def listing(path):
    r = sh(f"rclone lsf {args.bucket}/{path}")
    return {l.strip() for l in r.stdout.splitlines() if l.strip()}


# Say which bucket, every time. The failure above was silent: the only
# clue was an "already done" figure that looked plausible.
print(f"bucket: {args.bucket}", flush=True)
if not os.environ.get("R2_REMOTE"):
    print("  (R2_REMOTE not set — using the default. Check this is right.)",
          flush=True)
print("indexing R2 ...", flush=True)
raw = listing("raw")
# Compare by STEM, not by rewriting the extension.
#
# This line used to be listing("mock") with .jpg swapped for .png, which
# assumed raw designs are always PNG. With --jpeg they are .jpg, so nothing
# ever matched, "already done" read 0, and postrun rebuilt every mockup that
# already existed — twice, once for 360,588 and again for 799,998.
done = {os.path.splitext(f)[0] for f in listing("mock")}
# Sort by design id, but never crash on a filename that does not parse.
# A doubled extension in R2 ("409439.png.png") got past a single splitext
# and killed the whole run after generation had already paid for the work.
def _id(f):
    m = re.search(r"(\d+)", os.path.basename(f))
    return int(m.group(1)) if m else 0

# raw holds FILENAMES, done holds STEMS — match on the stem of each
_todo_files = [f for f in raw if os.path.splitext(f)[0] not in done]
_bad = [f for f in _todo_files if not re.search(r"\d", os.path.basename(f))]
if _bad:
    print(f"  skipping {len(_bad)} unparseable filenames, e.g. {_bad[:2]}")
todo = sorted(set(_todo_files) - set(_bad), key=_id)
if args.limit:
    todo = todo[:args.limit]

print(f"  raw available : {len(raw):,}")
print(f"  already done  : {len(done):,}")
print(f"  to process    : {len(todo):,}")
print(f"  workers       : {args.workers}")
if not todo:
    raise SystemExit("nothing to do")

# One worker script does the whole chain for its slice: convert to a
# transparent print file, QC it, then build the mockup. Keeping it in one
# process avoids writing 3600x4800 PNGs to disk only to read them straight
# back.
WORKER = f'''
import csv, os, sys
sys.path.insert(0, ".")
from dtf import to_dtf, qc
import photo_mockup as PM

me, n = int(sys.argv[1]), int(sys.argv[2])
files = [l.strip() for l in open("{WORK}/files.txt") if l.strip()]
rows = []
for i, fn in enumerate(files):
    if i % n != me:
        continue
    src = "{WORK}/raw/" + fn
    if not os.path.exists(src):
        continue
    # Print file is ALWAYS a PNG — it carries transparency, which JPEG
    # cannot hold. With --jpeg the source is 1000000.jpg, and reusing
    # that name made to_dtf write a JPEG: it threw, the except branch
    # marked every design flagged, and postrun reported "kept 0"
    # while dtf.py itself worked perfectly.
    stem = os.path.splitext(fn)[0]
    pr = "{WORK}/print/" + stem + ".png"
    try:
        st = to_dtf(src, pr)
        issues = qc(st)
        if not issues:
            PM.build(pr, "{WORK}/mock/" + stem + ".jpg")
        rows.append((fn, "NO" if issues else "YES", "; ".join(issues)))
    except Exception as e:
        rows.append((fn, "NO", "failed: " + str(e)[:60]))
    finally:
        # the print file is regenerated per order, so it is not kept
        if os.path.exists(pr):
            os.remove(pr)

with open("{WORK}/qc_%d.csv" % me, "w", newline="") as f:
    csv.writer(f).writerows(rows)
'''
with open(f"{WORK}/worker.py", "w") as f:
    f.write(WORKER)

t0, processed, flagged = time.time(), 0, 0

for start in range(0, len(todo), args.chunk):
    batch = todo[start:start + args.chunk]
    for d in ("raw", "print", "mock"):
        shutil.rmtree(f"{WORK}/{d}", ignore_errors=True)
        os.makedirs(f"{WORK}/{d}", exist_ok=True)

    with open(f"{WORK}/files.txt", "w") as f:
        f.write("\n".join(batch))
    sh(f"rclone copy {args.bucket}/raw {WORK}/raw --files-from {WORK}/files.txt "
       f"--transfers {args.transfers} --checkers {args.transfers//2} --quiet")
    got = len(os.listdir(f"{WORK}/raw"))
    if not got:
        print(f"  chunk at {start}: nothing downloaded", flush=True)
        continue

    procs = [subprocess.Popen([sys.executable, f"{WORK}/worker.py",
                               str(i), str(args.workers)])
             for i in range(args.workers)]
    for p in procs:
        p.wait()

    bad = 0
    for i in range(args.workers):
        p = f"{WORK}/qc_{i}.csv"
        if os.path.exists(p):
            for row in csv.reader(open(p)):
                if len(row) > 1 and row[1] == "NO":
                    bad += 1
            os.remove(p)
    flagged += bad

    made = len(os.listdir(f"{WORK}/mock"))
    sh(f"rclone copy {WORK}/mock {args.bucket}/mock "
       f"--transfers {args.transfers} --checkers {args.transfers//2} "
       f"--s3-upload-concurrency 2 --buffer-size 0 --quiet")

    for d in ("raw", "print", "mock"):
        shutil.rmtree(f"{WORK}/{d}", ignore_errors=True)

    processed += got
    el = time.time() - t0
    rate = processed / max(el, 1)
    left = (len(todo) - processed) / max(rate, 0.001) / 3600
    print(f"  {processed:,}/{len(todo):,}  kept {made:,}  flagged {bad:,}  "
          f"{rate:.1f}/s  ~{left:.1f}h left", flush=True)

el = time.time() - t0
print(f"\ndone: {processed:,} in {el/3600:.1f}h, {flagged:,} flagged")

# --- keep pace with generation ----------------------------------------
# Without this, postrun exits the moment it clears its queue. Generation
# then runs on for hours producing designs nobody is processing, and the
# whole backlog has to be done afterwards on an idle GPU pod — which is
# both slow and expensive. With --watch it sleeps and looks again.
if args.watch:
    import time as _t
    idle = 0
    while True:
        _t.sleep(args.watch)
        # stems again, for the same reason as above
        _raw = {os.path.splitext(f)[0] for f in listing("raw")}
        _mock = {os.path.splitext(f)[0] for f in listing("mock")}
        fresh = _raw - _mock
        if not fresh:
            idle += 1
            print(f"  nothing new ({idle} checks idle)", flush=True)
            # generation finished a while ago and nothing is arriving
            if idle >= 6:
                print("  nothing new for a long time — exiting", flush=True)
                break
            continue
        idle = 0
        print(f"\n  {len(fresh):,} new designs — processing", flush=True)
        os.execv(sys.executable, [sys.executable] + sys.argv)
