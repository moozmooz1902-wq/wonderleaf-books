#!/usr/bin/env python3
"""Score every panel for human figures and for wrong animal eyes.

WHY, measured rather than assumed: thirty random panels read by hand on
19 Oct had FIVE with a human figure in them - about 17%, which on 960,517
panels is roughly 160,000. None was a portrait. They are the small distant
kind a composition puts in for scale: walkers on a dune horizon,
pedestrians in a street, figures crossing a plaza. The CLIP gate rejects
about 40% of generations for PEOPLE during generation and still passes
these, which is not a bug in the gate so much as the truth about the
picture - at that size it reads as a street, not as a person. One panel in
thirty also had an animal face with three eyes.

The seller's rule, set 11 Oct, is no human figures and no wrong eyes. This
pass does not enforce it. It SCORES, writing one line per panel to
`wallart/scores/<bucket>-<range>.jsonl`, so the threshold is the seller's
choice and not a decision taken for them at three in the morning. Dropping
160,000 listings is their call; measuring is mine.

Reuses quality_gate.Gate unchanged - the same caption banks, including the
hard-won note about never adding an "architectural detail with nobody in
it" pass label, which describes exactly the townscapes that DO have
pedestrians and cut true catches from 34 to 19 when it was tried.

  usage: people_sweep.py --part 3/12 --max-hours 6
"""
import argparse, io, json, os, sys, time
import boto3
from botocore.config import Config
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quality_gate

EDGES = ["WA-" + c for c in "0123456789abcdef"] + ["WA-g"]
BATCH = 32


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
    lo = pre
    for e in EDGES:
        yield lo, pre + e
        lo = pre + e
    yield lo, None


def keys_in(c, bucket, pre, lo, hi):
    """Panels only. The render stage writes its pictures to <pre>listing/,
    which sorts after every WA- key and would otherwise be scored twelve
    times over."""
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
            if k.endswith(".jpg") and "/listing/" not in k:
                out.append(k)
        if stop or not r.get("IsTruncated"):
            return out
        tok = r["NextContinuationToken"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True)
    ap.add_argument("--stores", default="stores.json")
    ap.add_argument("--max-hours", type=float, default=6.0)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    k, N = (int(x) for x in a.part.split("/"))
    plan = json.load(open(a.stores))
    c = client()
    t0, stop = time.time(), time.time() + a.max_hours * 3600
    gate = quality_gate.Gate(device=a.device)
    print(f"gate loaded on {a.device} in {time.time()-t0:.0f}s", flush=True)

    work = []
    for s in plan["stores"]:
        pre = s["key_prefix"].strip("/") + "/"
        for lo, hi in ranges(pre):
            work.append((s["bucket"], pre, lo, hi))
    mine = [w for i, w in enumerate(work) if i % N == (k - 1) % N]
    print(f"part {k}/{N}: {len(mine)} of {len(work)} ranges", flush=True)

    total = 0
    for bucket, pre, lo, hi in mine:
        panels = keys_in(c, bucket, pre, lo, hi)
        tag = f"{bucket}-{lo.replace('/', '_')}"
        print(f"  {bucket} {lo}..{hi}  {len(panels):,} panels", flush=True)
        rows, batch, skus = [], [], []

        def flush():
            if not batch:
                return
            s = gate.scores(batch)
            for sk, h, e in zip(skus, s["human"], s["eyes"]):
                rows.append(f'{{"sku":"{sk}","human":{h:.4f},"eyes":{e:.4f}}}')
            batch.clear()
            skus.clear()

        for key in panels:
            if time.time() > stop:
                print(f"UNFINISHED: clock expired, {total:,} scored", flush=True)
                break
            try:
                body = c.get_object(Bucket=bucket, Key=key)["Body"].read()
                batch.append(Image.open(io.BytesIO(body)).convert("RGB"))
                skus.append(key.rsplit("/", 1)[-1][:-4])
            except Exception as e:
                print(f"  FAILED {key}: {e}", flush=True)
                continue
            if len(batch) >= BATCH:
                flush()
                total += BATCH
                if total % (BATCH * 20) == 0:
                    el = time.time() - t0
                    print(f"  {total:,} scored, {el/60:.1f} min, "
                          f"{total/max(el,1)*3600:,.0f}/hr", flush=True)
        flush()
        if rows:
            c.put_object(Bucket=bucket, Key=f"wallart/scores/{tag}.jsonl",
                         Body=("\n".join(rows) + "\n").encode(),
                         ContentType="text/plain")
            print(f"  scores {len(rows):,} -> wallart/scores/{tag}.jsonl",
                  flush=True)
    print(f"SWEEP COMPLETE  scored {total:,}  "
          f"{(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
