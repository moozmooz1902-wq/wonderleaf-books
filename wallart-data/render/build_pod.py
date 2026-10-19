#!/usr/bin/env python3
"""Build one store's eBay upload files, on a pod, and put them in R2.

WHY ON A POD. The files are large - luxvia-art alone is about 2 GB of CSV -
and the session container cannot write to R2: the credentials live on the
RunPod template and nowhere else. Building here means nothing large crosses
the container and the credentials never move.

The one thing that made this awkward was the job grid: rebuilding it needs
subjects.json, 90 KB, against a start-command limit somewhere between 60
and 70 thousand characters. It turned out the generation run had already
solved that - seed_assets.py publishes subjects.json to R2 and the
generation pods fetched it from there rather than carrying it. Same trick,
same URL, and the copy was checked byte-for-byte against the local one
before this was written.

Steps, in order, because each depends on the last:
  1. fetch subjects.json and rebuild the grid - the SAME expand() the
     generation used, so the SKUs match the pictures
  2. read wallart/hashes/*.jsonl, which says which panels were rendered
  3. run the duplicate audit over those hashes and build the drop list
  4. write the CSVs, 500,000 rows a file, into the store's own folder
  5. check them, zip them, upload the zip and the loose files to R2

  usage: build_pod.py --store luxvia-art --out /workspace/ebay
"""
import argparse, io, json, os, sys, time, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boto3
from botocore.config import Config

import grid, allocate, build_ebay, dup_audit
import numpy as np

JOBS_URL = ("https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev/"
            "wallart/assets/subjects.json")


def client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(signature_version="s3v4", max_pool_connections=16,
                      retries={"max_attempts": 10, "mode": "adaptive"}),
        region_name="auto")


def read_hashes(c, bucket):
    """Every wallart/hashes/*.jsonl in this bucket. Listed, not derived:
    a range whose file is missing is a range nobody rendered, and that has
    to show up as missing rather than as zero duplicates."""
    skus, bits, tok = [], [], None
    n_files = 0
    while True:
        kw = {"Bucket": bucket, "Prefix": "wallart/hashes/", "MaxKeys": 1000}
        if tok:
            kw["ContinuationToken"] = tok
        r = c.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            if not o["Key"].endswith(".jsonl"):
                continue
            n_files += 1
            body = c.get_object(Bucket=bucket, Key=o["Key"])["Body"].read()
            for line in body.decode().splitlines():
                if not line.strip():
                    continue
                d = json.loads(line)
                if d["bucket"] != bucket:
                    continue
                skus.append((d["sku"], d["bucket"]))
                bits.append(np.frombuffer(d["h"].encode(), dtype=np.uint8) - 48)
        if not r.get("IsTruncated"):
            break
        tok = r["NextContinuationToken"]
    print(f"{n_files} hash files, {len(skus):,} panels", flush=True)
    return skus, (np.array(bits, dtype=np.uint8) if bits else
                  np.zeros((0, 256), dtype=np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--out", default="/workspace/ebay")
    ap.add_argument("--prefix", default="ebay")
    a = ap.parse_args()
    t0 = time.time()
    c = client()

    import urllib.request
    req = urllib.request.Request(JOBS_URL, headers={"User-Agent": "Mozilla/5.0"})
    subs = json.loads(urllib.request.urlopen(req, timeout=180).read())
    n = sum(len(v) for v in subs.values() if isinstance(v, list))
    if n < 4000:
        sys.exit(f"subjects.json looks truncated: {n} subjects")
    jobs = grid.expand(subs)
    print(f"grid {len(jobs):,} jobs in {time.time()-t0:.0f}s", flush=True)

    skus, V = read_hashes(c, a.store)
    have = set((b, s) for s, b in skus)
    drop = set()
    if len(V):
        flags = dup_audit.audit(skus, V, None)
        drop = {(skus[i][1], skus[i][0]) for i in np.flatnonzero(flags)}
    print(f"near-duplicates to leave out: {len(drop):,}", flush=True)

    jobs = [j for j in jobs
            if allocate.store_for(j["sku"])["bucket"] == a.store]
    print(f"{a.store}: {len(jobs):,} designs in the grid", flush=True)
    os.makedirs(a.out, exist_ok=True)
    build_ebay.build(jobs, a.out, have, 0, drop)
    bad = build_ebay.check(a.out)
    if bad:
        sys.exit(f"REFUSING to upload: {bad} problems")

    d = os.path.join(a.out, a.store)
    names = sorted(f for f in os.listdir(d) if f.endswith(".csv"))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in names:
            z.write(os.path.join(d, f), f"{a.store}/{f}")
    key = f"{a.prefix}/{a.store}_ebay_upload.zip"
    c.put_object(Bucket=a.store, Key=key, Body=buf.getvalue(),
                 ContentType="application/zip")
    print(f"UPLOADED {a.store}/{key}  {buf.tell()/1e6:.0f} MB  "
          f"{len(names)} files", flush=True)
    # the loose CSVs too, for anyone who would rather not unzip 2 GB
    for f in names:
        with open(os.path.join(d, f), "rb") as fh:
            c.put_object(Bucket=a.store, Key=f"{a.prefix}/{a.store}/{f}",
                         Body=fh.read(), ContentType="text/csv")
    print(f"BUILD COMPLETE {a.store}  {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
