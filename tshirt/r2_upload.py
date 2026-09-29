#!/usr/bin/env python3
"""Upload the rendered designs to R2. Runs on the pod.

Set these in the pod terminal first - they stay on your machine:

    export R2_ACCOUNT_ID=...          # Cloudflare dashboard, R2 overview
    export R2_ACCESS_KEY_ID=...       # from the API token you created
    export R2_SECRET_ACCESS_KEY=...
    export R2_BUCKET=tshirt-m12k

    python3 r2_upload.py designs/

Resumable: it lists what is already in the bucket and skips those, so a
stopped run costs nothing.
"""
import os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    import boto3
    from botocore.config import Config
except ImportError:
    sys.exit("pip install boto3 first")

ACCOUNT = os.environ.get("R2_ACCOUNT_ID")
KEY     = os.environ.get("R2_ACCESS_KEY_ID")
SECRET  = os.environ.get("R2_SECRET_ACCESS_KEY")
BUCKET  = os.environ.get("R2_BUCKET", "tshirt-m12k")
WORKERS = int(os.environ.get("WORKERS", "32"))

if not all((ACCOUNT, KEY, SECRET)):
    sys.exit("set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY")


def client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{ACCOUNT}.r2.cloudflarestorage.com",
        aws_access_key_id=KEY, aws_secret_access_key=SECRET,
        config=Config(retries={"max_attempts": 5, "mode": "standard"},
                      max_pool_connections=WORKERS + 8),
        region_name="auto")


def already_there(s3):
    have, tok = set(), None
    while True:
        kw = {"Bucket": BUCKET, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        have.update(o["Key"] for o in r.get("Contents", []))
        if not r.get("IsTruncated"): return have
        tok = r["NextContinuationToken"]


def main(src):
    files = sorted(Path(src).glob("*.jpg"))
    if not files:
        sys.exit(f"no .jpg files in {src}")
    s3 = client()
    print(f"bucket {BUCKET}: checking what is already uploaded...")
    have = already_there(s3)
    todo = [f for f in files if f.name not in have]
    print(f"{len(files):,} rendered, {len(have):,} already up, {len(todo):,} to send")
    if not todo: return

    t0 = time.time(); n = [0]; bad = {}
    lock = threading.Lock()

    def put(f):
        try:
            s3.upload_file(str(f), BUCKET, f.name,
                           ExtraArgs={"ContentType": "image/jpeg",
                                      "CacheControl": "public, max-age=31536000"})
        except Exception as e:
            k = f"{type(e).__name__}: {str(e)[:110]}"
            with lock:
                bad[k] = bad.get(k, 0) + 1
                if bad[k] == 1: print("  ERROR:", k, flush=True)
            return
        with lock:
            n[0] += 1
            if n[0] % 500 == 0:
                r = n[0] / (time.time() - t0)
                print(f"  {n[0]:,}/{len(todo):,}  {r:.0f}/s  "
                      f"eta {(len(todo)-n[0])/r/60:.0f} min", flush=True)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(put, todo))
    print(f"\nuploaded {n[0]:,} in {(time.time()-t0)/60:.1f} min")
    if bad:
        for k, v in sorted(bad.items(), key=lambda x: -x[1]):
            print(f"  {v:>6,}  {k}")


main(sys.argv[1] if len(sys.argv) > 1 else "designs")
