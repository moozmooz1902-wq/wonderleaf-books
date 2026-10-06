#!/usr/bin/env python3
"""Render every design in FINAL_V7.csv and upload it to R2.

Runs on the pod, on all cores. Resumable: anything already in the bucket is
skipped, so a stopped run costs only what it was mid-way through.

Each row carries its own look (A-D) and colourway index, so the rendering
is deterministic - the same listing always produces the same shirt.
"""
import csv, io, os, sys, time
from multiprocessing import Pool, cpu_count
from PIL import Image, ImageDraw

import styles2, mockup
from linebreak import break_lines

SIZE    = int(os.environ.get("SIZE", "1200"))
QUALITY = int(os.environ.get("QUALITY", "86"))
WORKERS = int(os.environ.get("WORKERS", str(cpu_count())))
PREFIX  = os.environ.get("PREFIX", "v2/")
BUCKET  = os.environ["R2_BUCKET"]



_blank = None
_s3 = None


def s3():
    global _s3
    if _s3 is None:
        import boto3
        from botocore.config import Config
        _s3 = boto3.client(
            "s3",
            endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            config=Config(retries={"max_attempts": 5, "mode": "standard"},
                          max_pool_connections=WORKERS + 8),
            region_name="auto")
    return _s3


def init():
    global _blank
    _blank = Image.open(mockup.BLANK).convert("RGBA")


def one(row):
    sku = f"WLT-{int(row['source_idx']):06d}"
    key = f"{PREFIX}{sku}.jpg"
    try:
        li = int(row.get("look") or 0)
        pi = int(row.get("palette_idx") or 0)
        art = styles2.render(break_lines(row["slogan"]), li, pi,
                             seed=int(row["source_idx"]))
        im = mockup.place(art, _blank).resize((SIZE, SIZE), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=QUALITY, optimize=True)
        buf.seek(0)
        s3().upload_fileobj(buf, BUCKET, key,
                            ExtraArgs={"ContentType": "image/jpeg",
                                       "CacheControl": "public, max-age=31536000"})
        return 1
    except Exception as e:
        print(f"  FAILED {sku}: {type(e).__name__}: {str(e)[:120]}", flush=True)
        return -1


def already_uploaded():
    have, tok = set(), None
    c = s3()
    while True:
        kw = {"Bucket": BUCKET, "Prefix": PREFIX, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = c.list_objects_v2(**kw)
        have.update(o["Key"] for o in r.get("Contents", []))
        if not r.get("IsTruncated"): return have
        tok = r["NextContinuationToken"]


def main():
    rows = [r for r in csv.DictReader(open("FINAL_V7.csv")) if r.get("slogan")]
    print(f"{len(rows):,} designs; checking what is already in the bucket...", flush=True)
    have = already_uploaded()
    todo = [r for r in rows
            if f"{PREFIX}WLT-{int(r['source_idx']):06d}.jpg" not in have]
    print(f"{len(have):,} already up, {len(todo):,} to do, {WORKERS} workers", flush=True)
    if not todo:
        print("nothing to do"); return
    t0 = time.time(); ok = bad = 0
    with Pool(WORKERS, initializer=init) as p:
        for i, r in enumerate(p.imap_unordered(one, todo, chunksize=32), 1):
            ok += (r == 1); bad += (r == -1)
            if i % 2000 == 0:
                rate = i / (time.time() - t0)
                print(f"  {i:,}/{len(todo):,}  {rate:.0f}/s  "
                      f"eta {(len(todo)-i)/rate/60:.0f} min  ({bad} failed)", flush=True)
    print(f"\nDONE  uploaded {ok:,}  failed {bad:,}  in {(time.time()-t0)/60:.1f} min", flush=True)
    s3().put_object(Bucket=BUCKET, Key=f"{PREFIX}_DONE.txt",
                    Body=f"uploaded={ok} failed={bad}".encode(), ContentType="text/plain")


if __name__ == "__main__":
    main()
