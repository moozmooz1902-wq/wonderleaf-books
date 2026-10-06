#!/usr/bin/env python3
"""Print-ready artwork for every listing: transparent PNG at 300 dpi.

The mockups in v2/ are product photos for the eBay listing. A printer needs
the artwork on its own - no shirt, no background - at print resolution.

  art/mock/<SKU>.jpg  listing photo, 1200px        (copied from v2/)
  art/raw/<SKU>.png   artwork, transparent, 300dpi (this script)

Those exact paths are what the fulfilment tool looks for.

22cm wide at 300 dpi is 2598px, so the canvas is 2600 wide. Same design,
same seed, so the print file always matches the photo the buyer saw.
"""
import csv, io, os, time
from multiprocessing import Pool, cpu_count
from PIL import Image

import styles2
from linebreak import break_lines

PRINT_W = int(os.environ.get("PRINT_W", "2600"))     # 22cm @ 300dpi
WORKERS = int(os.environ.get("WORKERS", str(cpu_count())))
# The seller's fulfilment tool (pod/ebay/fulfilment/wl_lookup.py) resolves a
# custom label to {bucket}/art/raw/{label}.png for the print master and
# {bucket}/art/mock/{label}.jpg for the listing photo, and tshirt-m12k is
# already registered in its sources.json as store 2. Writing anywhere else
# means the tool finds nothing when an order comes in.
PREFIX  = "art/raw/"
BUCKET  = os.environ["R2_BUCKET"]
_s3 = None


def s3():
    global _s3
    if _s3 is None:
        import boto3
        from botocore.config import Config
        _s3 = boto3.client("s3",
            endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            config=Config(retries={"max_attempts": 5, "mode": "standard"},
                          max_pool_connections=WORKERS + 8), region_name="auto")
    return _s3


def one(row):
    sku = f"WLT-{int(row['source_idx']):06d}"
    key = f"{PREFIX}{sku}.png"
    try:
        art = styles2.render(break_lines(row["slogan"]), int(row["look"]),
                             int(row["palette_idx"]), seed=int(row["source_idx"]))
        h = int(art.height * (PRINT_W / art.width))
        art = art.resize((PRINT_W, h), Image.LANCZOS)
        buf = io.BytesIO()
        art.save(buf, "PNG", optimize=True, dpi=(300, 300))
        buf.seek(0)
        s3().upload_fileobj(buf, BUCKET, key,
                            ExtraArgs={"ContentType": "image/png",
                                       "CacheControl": "public, max-age=31536000"})
        return 1
    except Exception as e:
        print(f"  FAILED {sku}: {type(e).__name__}: {str(e)[:120]}", flush=True)
        return -1


def done_already():
    have, tok = set(), None
    c = s3()
    while True:
        kw = {"Bucket": BUCKET, "Prefix": PREFIX, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = c.list_objects_v2(**kw)
        have.update(o["Key"] for o in r.get("Contents", []))
        if not r.get("IsTruncated"): return have
        tok = r["NextContinuationToken"]


def copy_mock(sku):
    """Server-side copy v2/<SKU>.jpg -> art/mock/<SKU>.jpg. No download."""
    try:
        s3().copy_object(Bucket=BUCKET, Key=f"art/mock/{sku}.jpg",
                         CopySource={"Bucket": BUCKET, "Key": f"v2/{sku}.jpg"},
                         ContentType="image/jpeg", MetadataDirective="REPLACE",
                         CacheControl="public, max-age=31536000")
        return 1
    except Exception as e:
        print(f"  copy FAILED {sku}: {type(e).__name__}", flush=True)
        return -1


def mocks_present():
    have, tok = set(), None
    c = s3()
    while True:
        kw = {"Bucket": BUCKET, "Prefix": "art/mock/WLT-", "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = c.list_objects_v2(**kw)
        have.update(o["Key"].split("/")[-1][:-4] for o in r.get("Contents", []))
        if not r.get("IsTruncated"): return have
        tok = r["NextContinuationToken"]


def main():
    rows = [r for r in csv.DictReader(open("FINAL_V7.csv")) if r.get("slogan")]
    skus = [f"WLT-{int(r['source_idx']):06d}" for r in rows]
    have_m = mocks_present()
    todo_m = [s for s in skus if s not in have_m]
    print(f"mockups to copy into art/mock/: {len(todo_m):,}", flush=True)
    if todo_m:
        t0 = time.time()
        with Pool(WORKERS) as p:
            for i, _ in enumerate(p.imap_unordered(copy_mock, todo_m, chunksize=32), 1):
                if i % 10000 == 0:
                    print(f"  copied {i:,}/{len(todo_m):,}", flush=True)
        print(f"mockups copied in {(time.time()-t0)/60:.1f} min", flush=True)
    have = done_already()
    todo = [r for r in rows
            if f"{PREFIX}WLT-{int(r['source_idx']):06d}.png" not in have]
    print(f"{len(rows):,} designs, {len(have):,} already done, {len(todo):,} to go, "
          f"{WORKERS} workers, {PRINT_W}px wide", flush=True)
    if not todo: return
    t0 = time.time(); ok = bad = 0
    with Pool(WORKERS) as p:
        for i, r in enumerate(p.imap_unordered(one, todo, chunksize=16), 1):
            ok += (r == 1); bad += (r == -1)
            if i % 2000 == 0:
                rate = i / (time.time() - t0)
                print(f"  {i:,}/{len(todo):,}  {rate:.0f}/s  "
                      f"eta {(len(todo)-i)/rate/60:.0f} min  ({bad} failed)", flush=True)
    print(f"\nDONE  {ok:,} print files, {bad:,} failed, {(time.time()-t0)/60:.1f} min", flush=True)
    s3().put_object(Bucket=BUCKET, Key="v2/_DONE_PRINT.txt",
                    Body=f"print={ok} failed={bad}".encode(), ContentType="text/plain")


if __name__ == "__main__":
    main()
