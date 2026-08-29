#!/usr/bin/env python3
"""
Render the t-shirt catalogue: two files per design.

    <design_id>.png   4500x5400 transparent  -> print/  (goes to the printer)
    <design_id>.jpg   2000x2000              -> mock/   (the eBay image)

CPU ONLY. These are typography on black - no GPU, no model, no image API.
Resumable: anything already on disk is skipped, so it is safe to re-run.

    python3 run.py --workers 32
    python3 run.py --workers 32 --limit 200      # smoke test first
"""
import argparse, json, multiprocessing as mp, os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("BLANK_TEE", os.path.join(HERE, "blank.png"))

import render_designs as rd
import photo_mockup as pm

ART = os.path.join(HERE, "print")
MOCK = os.path.join(HERE, "mock")
FONTS = os.path.join(HERE, "fonts")

# Set by --upload. When on, each design is pushed to R2 and deleted locally the
# moment it is finished, so peak disk stays near zero and a 5GB pod is enough.
UPLOAD = None


def _push(local, remote_dir):
    name = os.path.basename(local)
    r = subprocess.run(
        ["rclone", "copyto", "--s3-no-check-bucket", "-q", local,
         f"{UPLOAD}/{remote_dir}/{name}"],
        capture_output=True, text=True)
    if r.returncode == 0:
        os.remove(local)
        return True
    return False


def one(d):
    png = os.path.join(ART, d["design_id"] + ".png")
    jpg = os.path.join(MOCK, d["design_id"] + ".jpg")
    if os.path.exists(png) and os.path.exists(jpg):
        return "skip"
    try:
        art = None
        if not os.path.exists(png):
            art = rd.render(d, FONTS)
            art.save(png, compress_level=6)
        if not os.path.exists(jpg):
            pm.build(art if art is not None else png, jpg)
        if UPLOAD:
            if not (_push(png, "raw") and _push(jpg, "mock")):
                return f"UPLOAD FAILED {d['design_id']}"
        return "ok"
    except Exception as e:
        return f"FAIL {d['design_id']}: {type(e).__name__} {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", default=os.path.join(HERE, "catalogue.json"))
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int)
    ap.add_argument("--shard", metavar="I/N",
                    help="split the catalogue across several pods. Pod 1 runs "
                         "--shard 1/2, pod 2 runs --shard 2/2. Each takes every "
                         "Nth design, so no pod repeats another's work.")
    ap.add_argument("--upload", metavar="R2DEST",
                    help="e.g. r2:tshirt-xxx/art  - upload each file and delete "
                         "it locally as soon as it is done. Keeps peak disk near "
                         "zero, so a 5GB pod is enough. Requires rclone set up.")
    ap.add_argument("--no-resume", action="store_true",
                    help="re-render every design even if it is already in R2, "
                         "overwriting each file in place. Use this when the "
                         "RENDERER has changed - resume only knows whether a "
                         "file exists, not whether it is the current version, "
                         "so without this a re-render skips the whole "
                         "catalogue and does nothing. Overwriting in place is "
                         "safer than emptying the bucket first: the listings "
                         "keep working throughout.")
    a = ap.parse_args()

    global UPLOAD
    UPLOAD = a.upload
    already = set()
    if UPLOAD and a.no_resume:
        print("  --no-resume: re-rendering everything, overwriting in place")
    if UPLOAD and not a.no_resume:
        if not shutil.which("rclone"):
            sys.exit("rclone not found - install it, or drop --upload and use a bigger disk")
        print(f"  uploading to {UPLOAD} and deleting locally as we go")
        # A terminated pod loses the container disk, so "does the file exist
        # locally" is useless for resume - everything would re-render from zero.
        # Ask R2 what is already there instead. Same idea as rebuild_ledger.py:
        # the bucket is the source of truth, not any local file.
        print("  checking what is already in R2 ...", flush=True)
        try:
            r = subprocess.run(["rclone", "lsf", f"{UPLOAD}/mock",
                                "--retries", "1", "--low-level-retries", "2",
                                "--contimeout", "15s", "--timeout", "60s"],
                               capture_output=True, text=True, timeout=600)
            if r.returncode == 0:
                already = {ln[:-4] for ln in r.stdout.split() if ln.endswith(".jpg")}
                print(f"  {len(already):,} designs already done - skipping those")
            else:
                print(f"  (could not list R2, starting fresh: {r.stderr.strip()[:120]})")
        except subprocess.TimeoutExpired:
            # Resume is an optimisation. Never let it block the render.
            print("  (listing R2 timed out, starting fresh - nothing is lost,")
            print("   finished designs will simply be re-uploaded over themselves)")

    os.makedirs(ART, exist_ok=True)
    os.makedirs(MOCK, exist_ok=True)
    designs = json.load(open(a.catalogue))
    if a.limit:
        designs = designs[:a.limit]
    if a.shard:
        i, n = (int(x) for x in a.shard.split("/"))
        if not 1 <= i <= n:
            sys.exit("--shard must be like 1/2, 2/2 - index within range")
        designs = designs[i - 1::n]
        print(f"  shard {i} of {n}: {len(designs):,} designs")
    if already:
        designs = [d for d in designs if d["design_id"] not in already]
    print(f"  {len(designs):,} designs to do, {a.workers} workers")
    t0, ok, skip, fail = time.time(), 0, 0, []
    def _init(dest):
        global UPLOAD
        UPLOAD = dest

    with mp.Pool(a.workers, initializer=_init, initargs=(UPLOAD,)) as pool:
        for i, r in enumerate(pool.imap_unordered(one, designs, chunksize=16), 1):
            if r == "ok":
                ok += 1
            elif r == "skip":
                skip += 1
            else:
                fail.append(r)
            if i % 1000 == 0:
                el = time.time() - t0
                print(f"  {i:,}/{len(designs):,}  {el/60:.1f} min  "
                      f"eta {(len(designs)-i)*el/i/60:.0f} min", flush=True)

    print(f"\n  rendered {ok:,}  skipped {skip:,}  failed {len(fail)}")
    for f in fail[:10]:
        print("   ", f)
    print(f"  total {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
