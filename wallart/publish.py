#!/usr/bin/env python3
"""Render a store's catalogue and upload it to that store's Cloudflare R2 bucket,
in the layout the existing fulfilment tools already read:

    art/mock/<SKU>.jpg   the listing photo: the print in a black frame (the only eBay picture)
    art/raw/<SKU>.png    print file, 300 dpi (order.py / print_tool.py fetch this)

Resumable: files already in the bucket are skipped, so it can be stopped and
restarted, or run on several machines with --part 1/4, 2/4, ...

    export R2_ACCOUNT_ID=...  R2_ACCESS_KEY_ID=...  R2_SECRET_ACCESS_KEY=...
    python3 publish.py --store 3 --bucket wallart-s3 --limit 200      # try a few
    python3 publish.py --store 3 --bucket wallart-s3 --workers 16      # the lot
    python3 publish.py --store 3 --bucket wallart-s3 --mock-only       # print files later

Credentials go in the machine's environment, never in this file or the repo.
"""
import argparse, csv, gzip, io, os, sys, time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRINT_MM = {"A4": 210, "A3": 297, "A2": 420}


def s3():
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(retries={"max_attempts": 8, "mode": "adaptive"}, max_pool_connections=64),
    )


def existing(client, bucket, prefix):
    """Every key already uploaded under prefix (so a restart skips them)."""
    keys = set()
    for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        keys.update(o["Key"] for o in page.get("Contents", []))
    return keys


def art_for(row, width):
    """Draw any catalogue row at `width` px: typography, chart or map."""
    kind = row.get("kind") or "text"
    if kind == "chart":
        from charts import render_chart
        cid, var = row["spec"].split("|")
        return render_chart(cid, var, row["palette"], row["fonts"], width)
    if kind == "map":
        from maps import render_map
        country, style, city = row["spec"].split("|")
        return render_map(country, style, row["palette"], row["fonts"], city or None, width=width)
    from render import render
    return render(row["phrase"], row["palette"], row["fonts"], row["layout"], row["ornament"], width)


def draw(job):
    """Render one row -> {key: bytes}. Runs in a worker process."""
    from render import mockup
    row, want_raw, size, want_mock = job
    out = {}
    if want_mock:
        art = art_for(row, 1200)
        # the ONE listing photo: the print in a black frame on a wall
        buf = io.BytesIO()
        mockup(art, 1600, framed=True).save(buf, "JPEG", quality=88, optimize=True)
        out[f"art/mock/{row['sku']}.jpg"] = (buf.getvalue(), "image/jpeg")
    if want_raw:
        px = round(PRINT_MM[size] / 25.4 * 300)
        buf = io.BytesIO()
        art_for(row, px).save(
            buf, "PNG", dpi=(300, 300), optimize=False, compress_level=6)
        out[f"art/raw/{row['sku']}.png"] = (buf.getvalue(), "image/png")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", type=int, required=True)
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--csv", help="default out/store<N>.csv.gz")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int)
    ap.add_argument("--part", default="1/1", help="k/n: this machine does every n-th row")
    ap.add_argument("--mock-only", action="store_true", help="listing photos only (fast first pass)")
    ap.add_argument("--raw-only", action="store_true", help="print files only (second pass)")
    ap.add_argument("--print-size", default="A4", choices=list(PRINT_MM),
                    help="print file size at 300dpi; A4 by default - the print shop upscales for A3/A2")
    a = ap.parse_args()

    k, n = map(int, a.part.split("/"))
    client = s3()
    kind, ext = ("raw", "png") if a.raw_only else ("mock", "jpg")
    done = existing(client, a.bucket, f"art/{kind}/")
    print(f"{len(done):,} {'print files' if a.raw_only else 'listing photos'} already in {a.bucket}")

    path = Path(a.csv or HERE / "out" / f"store{a.store}.csv.gz")
    rows = []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh)):
            if i % n != k - 1 or f"art/{kind}/{r['sku']}.{ext}" in done:
                continue
            rows.append(r)
            if a.limit and len(rows) >= a.limit:
                break
    print(f"{len(rows):,} to render and upload")

    t0, sent = time.time(), 0
    up = ThreadPoolExecutor(max_workers=32)

    def put(key, body, ctype):
        client.put_object(Bucket=a.bucket, Key=key, Body=body, ContentType=ctype,
                          CacheControl="public, max-age=31536000, immutable")

    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = ((r, not a.mock_only, a.print_size, not a.raw_only) for r in rows)
        futures = []
        for files in pool.map(draw, jobs, chunksize=16):
            # raw first, mock last: a listing photo only exists once its print file does
            for key in sorted(files, key=lambda x: "mock" in x):
                body, ctype = files[key]
                futures.append(up.submit(put, key, body, ctype))
            sent += 1
            if sent % 1000 == 0:
                rate = sent / (time.time() - t0)
                print(f"  {sent:,}/{len(rows):,}  {rate:.1f}/s  eta {(len(rows) - sent) / rate / 3600:.1f} h", flush=True)
        for f in futures:
            f.result()
    up.shutdown()
    print(f"done: {sent:,} designs in {(time.time() - t0) / 60:.0f} min")


if __name__ == "__main__":
    main()
