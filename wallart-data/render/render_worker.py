#!/usr/bin/env python3
"""Make the listing pictures: four colourways x three frame colours, per panel.

Runs ON a pod, because the R2 credentials live on the RunPod template and
nowhere else. Reads the generated panels out of a bucket, writes the framed
mockups back into the same bucket under <prefix>/listing/, and never touches
another store's bucket - one design belongs to one account.

  <prefix>/gen/<SKU>.jpg                     in   (the panel, as generated)
  <prefix>/listing/<SKU>-<ci>-<colour>.jpg   out  (ci = colourway 0..3)

THE BOTTOM 11% OF EVERY PANEL IS CROPPED OFF, and that is not a style
choice. FLUX signs its work: a cursive signature, sometimes a "(C) <name>"
line, sometimes a word of invented lettering, almost always along the
bottom edge. declutter.strip_marks was built to erase them in place and,
measured on real panels on 19 Oct, it does not work well enough to ship:
on four panels with marks it left the signature on three, left the
lettering on all four, and gouged a white hole out of the middle of a
mouse on the fourth. A fixed crop removes the band the marks live in,
cannot damage what it does not touch, and costs about a tenth of the
height - which on these compositions reads as a tighter crop, not a
mutilation. Verified by eye on the same four panels.

RESUME IS BY LISTING, not by a local file. The bucket is the only durable
record: a pod can die at any moment and the next one must not redo its
work. A SKU whose <ci>=0 black mockup is already there is skipped whole.

  usage: render_worker.py --part 3/12 --max-hours 10
"""
import argparse, io, os, sys, time, json
import multiprocessing as mp
import boto3
import numpy as np
from botocore.config import Config
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import compose, choose
from recolour import recolour, RAMPS
from frames import mockup

CROP = 0.11                      # see the docstring: this is the signature fix
COLOURWAYS = ["as-generated"] + list(RAMPS)[:3]
FRAMES = ["black", "white", "oak"]
# Black is the listing's main image and the one a buyer zooms, so it is made
# at eBay's zoom size. White and oak are variation pictures, seen small, and
# at 1000px they cost 40% of the storage for no visible difference.
PX = {"black": 1600, "white": 1000, "oak": 1000}
Q = {"black": 82, "white": 82, "oak": 82}
EDGES = ["WA-" + c for c in "0123456789abcdef"] + ["WA-g"]


def cpu_quota():
    """How many cores this container may actually use.

    cgroup v2 puts "<quota> <period>" in cpu.max; v1 splits it across two
    files; "max" means unlimited, and then there is nothing better than
    os.cpu_count(). Capped at 32 regardless, because the memory per child
    is what bites first.
    """
    try:
        q, per = open("/sys/fs/cgroup/cpu.max").read().split()
        if q != "max":
            return max(1, min(32, int(int(q) / int(per))))
    except Exception:
        pass
    try:
        q = int(open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read())
        per = int(open("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read())
        if q > 0:
            return max(1, min(32, q // per))
    except Exception:
        pass
    return max(1, min(32, os.cpu_count() or 4))


def client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(signature_version="s3v4", max_pool_connections=32,
                      retries={"max_attempts": 10, "mode": "adaptive"}),
        region_name="auto")


def ranges(pre):
    """The same half-open partition r2_count_stores.py uses, for the same
    reason: it is exhaustive whatever the keys are called, instead of
    assuming they are hashes."""
    lo = pre
    for e in EDGES:
        yield lo, pre + e
        lo = pre + e
    yield lo, None


def keys_in(c, bucket, pre, lo, hi, suffix=".jpg"):
    out, tok, after = [], None, lo
    while True:
        kw = {"Bucket": bucket, "Prefix": pre, "MaxKeys": 1000}
        if tok:
            kw["ContinuationToken"] = tok
        else:
            kw["StartAfter"] = after
        r = c.list_objects_v2(**kw)
        stop = False
        for o in r.get("Contents", []):
            k = o["Key"]
            if hi is not None and k > hi:
                stop = True
                break
            if k.endswith(suffix):
                out.append(k)
        if stop or not r.get("IsTruncated"):
            return out
        tok = r["NextContinuationToken"]


def dhash(im, n=16):
    """pipeline.dhash, on the CROPPED artwork - 256-bit gradient hash.

    Computed here because this pass already has every panel decoded in
    memory. Doing it separately would mean downloading the whole catalogue a
    second time, which is the only expensive part of a duplicate audit; the
    last one took 95 minutes at 227k panels and would be about six hours at
    this size. The hashes go back to R2 as JSONL so the audit is a local
    numpy job afterwards, with nothing to fetch.
    """
    g = np.asarray(im.convert("L").resize((n + 1, n), Image.LANCZOS),
                   dtype=np.int16)
    return "".join("1" if v else "0" for v in (g[:, 1:] > g[:, :-1]).ravel())


def render(c, bucket, pre, sku, panel):
    im = Image.open(io.BytesIO(panel))
    w, h = im.size
    art0 = im.crop((0, 0, w, int(h * (1 - CROP))))
    n = 0
    h256 = dhash(art0)
    for ci, cw in enumerate(COLOURWAYS):
        art = art0 if ci == 0 else recolour(art0, cw)
        sheet, _ = compose(art, choose("", f"{sku}-{ci}"))
        for fr in FRAMES:
            buf = io.BytesIO()
            mockup(sheet, fr).resize((PX[fr], PX[fr]), Image.LANCZOS)\
                .save(buf, "JPEG", quality=Q[fr], optimize=True)
            c.put_object(Bucket=bucket, Key=f"{pre}listing/{sku}-{ci}-{fr}.jpg",
                         Body=buf.getvalue(), ContentType="image/jpeg")
            n += 1
    return n, h256


_C = None


def _init():
    """One boto3 client per PROCESS. Clients are not documented thread safe
    and a pool of sixteen sharing one is the kind of saving that corrupts an
    upload rather than speeding it up."""
    global _C
    _C = client()


def _hash_one(args):
    """Download and hash one panel. No pictures are written."""
    bucket, pre, key, sku = args
    try:
        body = _C.get_object(Bucket=bucket, Key=key)["Body"].read()
        im = Image.open(io.BytesIO(body))
        w, h = im.size
        return sku, dhash(im.crop((0, 0, w, int(h * (1 - CROP)))))
    except Exception as e:
        print(f"  FAILED {bucket}/{key}: {e}", flush=True)
        return sku, None


def _one(args):
    """Download, render, upload one panel. Returns (sku, hash, pictures) or
    (sku, None, 0) - a failure must not take the pool down with it, because
    the bucket is the record and the next pod picks the SKU up again."""
    bucket, pre, key, sku = args
    try:
        body = _C.get_object(Bucket=bucket, Key=key)["Body"].read()
        n, h = render(_C, bucket, pre, sku, body)
        return sku, h, n
    except Exception as e:
        print(f"  FAILED {bucket}/{key}: {e}", flush=True)
        return sku, None, 0


def hash_only(c, mine, procs, stop):
    """Fill in the hashes that the render pass lost.

    The authority for 'this panel has pictures' is the bucket, and the
    authority for 'this panel has a hash' is the range's hash file. Where
    they disagree, this closes the gap without re-rendering anything.
    """
    fixed = 0
    for bucket, pre, lo, hi in mine:
        panels = [k for k in keys_in(c, bucket, pre, lo, hi)
                  if "/listing/" not in k]
        tag = f"{bucket}-{lo.replace('/', '_')}"
        key = f"wallart/hashes/{tag}.jsonl"
        have = {}
        try:
            for line in c.get_object(Bucket=bucket, Key=key)["Body"]\
                    .read().decode().splitlines():
                if line.strip():
                    r = json.loads(line)
                    have[r["sku"]] = line
        except Exception:
            pass                       # no file yet is not an error
        # EVERY panel lacking a hash, with no check that it was rendered.
        #
        # The first version listed <pre>listing/ to find out which panels had
        # pictures and hashed only those. That is the right question while a
        # bucket is half rendered - and the wrong amount of work: 360 LIST
        # calls per range just to answer it. Run this AFTER a bucket's render
        # is complete and the question does not arise, because every panel
        # has its pictures. The caller is responsible for that ordering; it
        # is why --bucket exists.
        todo = [(bucket, pre, k, k.rsplit("/", 1)[-1][:-4]) for k in panels
                if k.rsplit("/", 1)[-1][:-4] not in have]
        print(f"  {bucket} {lo}  {len(panels):,} panels, {len(have):,} hashed,"
              f" {len(todo):,} to fix", flush=True)
        if not todo:
            continue
        with mp.Pool(procs, initializer=_init) as pool:
            for sku, h in pool.imap_unordered(_hash_one, todo, chunksize=8):
                if h:
                    have[sku] = f'{{"sku":"{sku}","bucket":"{bucket}","h":"{h}"}}'
                    fixed += 1
                if time.time() > stop:
                    print("UNFINISHED: clock expired", flush=True)
                    break
        c.put_object(Bucket=bucket, Key=key,
                     Body=("\n".join(have[k] for k in sorted(have)) + "\n")
                     .encode(), ContentType="text/plain")
        print(f"  {tag}: {len(have):,} hashes written", flush=True)
    print(f"HASH REPAIR COMPLETE  filled {fixed:,}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True)          # k/N
    ap.add_argument("--stores", default="stores.json")
    ap.add_argument("--max-hours", type=float, default=10.0)
    ap.add_argument("--bucket", help="only this bucket's ranges. Used to run "
                                     "the hash repair on a store whose render "
                                     "has finished while others are still "
                                     "going.")
    ap.add_argument("--hash-only", action="store_true",
                    help="do not render; just compute the hashes that are "
                         "missing. Panels rendered by a pod that was deleted "
                         "mid-range have pictures but no hash, and the hash "
                         "is what the duplicate audit and the CSV builder "
                         "both read. Downloads each missing panel, crops it "
                         "the same 11%, hashes it, merges into the range's "
                         "file. No uploads of pictures, so it is minutes.")
    ap.add_argument("--procs", type=int, default=0,
                    help="default: the pod's cgroup CPU quota. NOT "
                         "os.cpu_count(), which on a 16-vCPU RunPod CPU pod "
                         "reports the HOST's 192 cores - a pool that size "
                         "needs about 19 GB just to import PIL and boto3 in "
                         "every child, and the first attempt sat there "
                         "spawning instead of rendering.")
    a = ap.parse_args()
    procs = a.procs or cpu_quota()
    k, N = (int(x) for x in a.part.split("/"))
    plan = json.load(open(a.stores))
    c = client()
    t0, stop = time.time(), time.time() + a.max_hours * 3600

    work = []
    for s in plan["stores"]:
        pre = s["key_prefix"].strip("/") + "/"
        for lo, hi in ranges(pre):
            work.append((s["bucket"], pre, lo, hi))
    mine = [w for i, w in enumerate(work) if i % N == (k - 1) % N]
    print(f"part {k}/{N}: {len(mine)} of {len(work)} ranges, "
          f"{procs} processes", flush=True)

    if a.bucket:
        mine = [w for w in mine if w[0] == a.bucket]
        print(f"limited to {a.bucket}: {len(mine)} ranges", flush=True)
    if a.hash_only:
        return hash_only(c, mine, procs, stop)

    done_total = made = skipped = 0
    for bucket, pre, lo, hi in mine:
        panels = keys_in(c, bucket, pre, lo, hi)
        have = keys_in(c, bucket, pre + "listing/",
                       (pre + "listing/" + lo.split("/")[-1]) if lo != pre else pre + "listing/",
                       None)
        done = {k2.rsplit("/", 1)[-1][:-len("-0-black.jpg")]
                for k2 in have if k2.endswith("-0-black.jpg")}
        print(f"  {bucket} {lo}..{hi}  {len(panels):,} panels, "
              f"{len(done):,} already rendered", flush=True)
        hashes = []
        todo = []
        for key in panels:
            if "/listing/" in key:
                continue
            sku = key.rsplit("/", 1)[-1][:-4]
            if sku in done:
                skipped += 1
            else:
                todo.append((bucket, pre, key, sku))
        expired = False
        # FLUSH AS WE GO. The first version kept a range's hashes in memory
        # and wrote them when the range finished. Measured at 09:26: luxvia-art
        # was 99.98% rendered but only 92.6% of its hashes existed, because a
        # pod deleted mid-range takes its unwritten hashes with it - and two
        # pods WERE deleted mid-range, deliberately, for being slow. The
        # pictures survive, because they are uploaded one at a time; the
        # record of them did not.
        #
        # Rewriting the same object on each flush keeps the file names
        # enumerable, which is what lets dup_audit fetch them without a
        # credential, and bounds the loss to one flush interval.
        FLUSH = 500
        tag = f"{bucket}-{lo.replace('/', '_')}"

        def put_hashes():
            if hashes:
                c.put_object(Bucket=bucket, Key=f"wallart/hashes/{tag}.jsonl",
                             Body=("\n".join(hashes) + "\n").encode(),
                             ContentType="text/plain")

        with mp.Pool(procs, initializer=_init) as pool:
            for sku, h256, n in pool.imap_unordered(_one, todo, chunksize=4):
                if h256:
                    made += n
                    hashes.append(
                        f'{{"sku":"{sku}","bucket":"{bucket}","h":"{h256}"}}')
                    done_total += 1
                if hashes and len(hashes) % FLUSH == 0:
                    put_hashes()
                if done_total and done_total % 200 == 0:
                    el = time.time() - t0
                    print(f"  {done_total:,} panels, {made:,} pictures, "
                          f"{el/60:.1f} min, "
                          f"{done_total/max(el,1)*3600:,.0f} panels/hr",
                          flush=True)
                if time.time() > stop:
                    print(f"UNFINISHED: clock expired, {made:,} made",
                          flush=True)
                    pool.terminate()
                    expired = True
                    break
        if hashes:
            # one object per range, named so a rerun overwrites rather than
            # duplicates - the bucket stays the record, as everywhere else
            # named by BUCKET AND RANGE ONLY, never by part: a range
            # belongs to exactly one part whatever the fleet size, so the
            # audit can enumerate the file names without being told how many
            # pods there were, and a rerun with a different --parts
            # overwrites the same object instead of leaving two.
            put_hashes()
            print(f"  hashes {len(hashes):,} -> wallart/hashes/{tag}.jsonl",
                  flush=True)
        if expired:
            return
    print(f"RENDER COMPLETE  panels {done_total:,}  pictures {made:,}  "
          f"skipped {skipped:,}  {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
