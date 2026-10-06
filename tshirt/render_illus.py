#!/usr/bin/env python3
"""Render every listing photo at the size the seller's team already handles.

The listing photos were being written at 1200x1200. Every image already in
the seller's buckets is 2000x2000 - 14 of 14 sampled at random from a real
listing of the bucket - and their team runs a tool over these that finds the
print area and crops away the rest. A different canvas size is a different
crop, so 1200 was wrong even though it looked fine.

So this re-renders all 116,355 listing photos at 2000x2000: the 13,313 that
matched an illustration keep the picture-over-type design, the rest are
type-only as before. SKUs do not change, so the URLs do not change and the
eBay file is untouched.

    art/mock/<SKU>.jpg   listing photo, 2000x2000
    art/raw/<SKU>.png    print master - NOT rewritten here, the print file is
                         a physical size and does not follow the photo

Both paths are what the seller's fulfilment tool resolves a custom label to,
so writing anywhere else means it finds nothing when an order comes in.
"""
import csv, io, os, sys, time
from multiprocessing import Pool, cpu_count
from PIL import Image

import compose, dtf, mockup, styles2
from linebreak import break_lines

SIZE    = int(os.environ.get("SIZE", "2000"))   # what their tool already crops
PRINT_W = int(os.environ.get("PRINT_W", "2600"))     # 22cm @ 300dpi
PRINT_H = int(os.environ.get("PRINT_H", "3600"))     # 30cm, the tall limit
QUALITY = int(os.environ.get("QUALITY", "86"))
WORKERS = int(os.environ.get("WORKERS", str(cpu_count())))
BUCKET  = os.environ["R2_BUCKET"]
MOCK_ONLY = os.environ.get("MOCK_ONLY", "") == "1"
SRC     = os.environ.get("ILLUS_PREFIX", "illusv2/raw/")

_s3 = None
_blank = None
_lib = {}
_tint = {}


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


def init():
    global _blank
    _blank = Image.open(mockup.BLANK).convert("RGBA")


def illus(slug):
    if slug not in _lib:
        _lib[slug] = Image.open(f"illus_lib/{slug}.png").convert("RGBA")
    return _lib[slug]


def tinted(slug, pal_i):
    """Recolouring is the slow step - 246 pictures in 12 palettes, not 13,313.

    Done per listing it is a million-pixel remap each time and the whole job
    takes a day; cached it is 2,952 remaps and the listings are pastes. The
    cache only pays off because the jobs are sorted by picture and palette
    before they are handed out, so a worker gets a contiguous run that shares
    one tint instead of a random spread that shares none.
    """
    key = (slug, pal_i)
    if key not in _tint:
        if len(_tint) > 64:
            _tint.clear()
        _tint[key] = compose._crop(
            compose.recolour_to(illus(slug), list(styles2.pal(pal_i)[1:])))
    return _tint[key]


def inks(pal_i):
    p = list(styles2.pal(pal_i)[1:])
    return p + [compose._visible(c) for c in p] + [(18, 18, 20)]


def put(key, img, fmt, **kw):
    buf = io.BytesIO()
    img.save(buf, fmt, **kw)
    buf.seek(0)
    ct = "image/jpeg" if fmt == "JPEG" else "image/png"
    s3().upload_fileobj(buf, BUCKET, key,
                        ExtraArgs={"ContentType": ct,
                                   "CacheControl": "public, max-age=31536000"})


def one(job):
    sku, slug, row = job
    try:
        li = int(row.get("look") or 0)
        pi = int(row.get("palette_idx") or 0)
        seed = int(row["source_idx"])
        text = styles2.render(break_lines(row["slogan"]), li, pi, seed=seed)
        # slug is None for the type-only majority: they get the text design
        art = compose.stack(tinted(slug, pi), text) if slug else text

        mock = mockup.place(art, _blank).resize((SIZE, SIZE), Image.LANCZOS)
        put(f"art/mock/{sku}.jpg", mock, "JPEG", quality=QUALITY, optimize=True)
        if MOCK_ONLY:
            return 1                      # the print file is a physical
                                          # size and does not follow the photo

        # 22cm wide unless that would make it taller than 30cm: a picture
        # over type is a much taller shape than type alone, and a 36cm print
        # is both a bigger transfer than it needs to be and lower on the
        # chest than the placement the seller signed off.
        scale = min(PRINT_W / art.width, PRINT_H / art.height)
        master = dtf.snap(art.resize((max(1, int(art.width * scale)),
                                      max(1, int(art.height * scale))),
                                     Image.LANCZOS), inks(pi))
        put(f"art/raw/{sku}.png", master, "PNG", optimize=True, dpi=(300, 300))
        return 1
    except Exception as e:
        print(f"  FAILED {sku}: {type(e).__name__}: {str(e)[:140]}", flush=True)
        return -1


ALL_ROWS = os.environ.get("ALL_ROWS", "") == "1"


def main():
    mp = dict(l.rstrip("\n").split("\t") for l in open("ILLUS_MAP.tsv"))
    jobs = []
    with open("FINAL_V7.csv", newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            sku = f"WLT-{int(r['source_idx']):06d}"
            if sku in mp or ALL_ROWS:
                jobs.append((sku, mp.get(sku), {k: r[k] for k in
                            ("source_idx", "slogan", "look", "palette_idx")}))
    jobs.sort(key=lambda j: (j[1] or "", int(j[2]["palette_idx"] or 0)))
    print(f"{len(jobs)} illustrated listings, {WORKERS} workers", flush=True)

    # one before the rest: a smoke test is cheaper than a wasted pod-hour
    init()
    if one(jobs[0]) != 1:
        sys.exit("the first listing failed - stopping before the other 13,312")
    print("smoke test passed", flush=True)

    t0 = time.time(); ok = bad = 0
    with Pool(WORKERS, initializer=init) as p:
        for i, res in enumerate(p.imap_unordered(one, jobs[1:], chunksize=64), 2):
            ok += res == 1; bad += res == -1
            if i % 500 == 0:
                print(f"  {i}/{len(jobs)}  {i/(time.time()-t0):.1f}/s  "
                      f"{bad} failed", flush=True)
    print(f"DONE {ok} rendered, {bad} failed, {(time.time()-t0)/60:.1f} min", flush=True)
    s3().put_object(Bucket=BUCKET, Key="illusv2/_RENDERED.txt",
                    Body=f"rendered={ok} failed={bad}".encode(),
                    ContentType="text/plain")


if __name__ == "__main__":
    main()
