#!/usr/bin/env python3
"""Render every text design and write it as a JPEG ready for upload.

Runs on all cores. Resumable - it skips anything already rendered, so a
stopped run costs only the file it was mid-way through.

    python3 render_all.py

Output: designs/WLT-<id>.jpg, which is also the R2 object name and the SKU.
"""
import csv, os, sys, time
from multiprocessing import Pool, cpu_count
from PIL import Image

OUT   = "designs"
SIZE  = int(os.environ.get("SIZE", "1200"))
QUAL  = int(os.environ.get("QUALITY", "86"))
WORKERS = int(os.environ.get("WORKERS", str(cpu_count())))

os.makedirs(OUT, exist_ok=True)
_blank = None


def init():
    global _blank
    import mockup
    _blank = Image.open(mockup.BLANK).convert("RGBA")


def one(row):
    import make_designs as md
    sku = f"WLT-{int(row['source_idx']):06d}"
    path = f"{OUT}/{sku}.jpg"
    if os.path.exists(path):
        return 0
    try:
        _, im = md.design(row, _blank)
        im.resize((SIZE, SIZE), Image.LANCZOS).save(
            path, "JPEG", quality=QUAL, optimize=True)
        return 1
    except Exception as e:
        print(f"  FAILED {sku}: {type(e).__name__}: {e}", flush=True)
        return -1


def main():
    rows = [r for r in csv.DictReader(open("REPLICA_V5.csv")) if r["slogan"]]
    print(f"{len(rows):,} text designs to render, {WORKERS} workers")
    done = skipped = failed = 0
    t0 = time.time()
    with Pool(WORKERS, initializer=init) as p:
        for i, r in enumerate(p.imap_unordered(one, rows, chunksize=64), 1):
            if r == 1: done += 1
            elif r == 0: skipped += 1
            else: failed += 1
            if i % 5000 == 0:
                rate = i / (time.time() - t0)
                print(f"  {i:,}/{len(rows):,}  {rate:.0f}/s  "
                      f"eta {(len(rows)-i)/rate/60:.0f} min  "
                      f"({skipped:,} already done, {failed} failed)", flush=True)
    print(f"\nrendered {done:,}, skipped {skipped:,}, failed {failed:,} "
          f"in {(time.time()-t0)/60:.1f} min")
    if failed:
        print("!! some designs failed - do not upload until these are understood")


if __name__ == "__main__":
    main()
