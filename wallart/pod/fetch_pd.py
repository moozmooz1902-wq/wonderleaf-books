#!/usr/bin/env python3
"""CPU pod: download the public-domain artworks and upload them to R2.

For each row of out/<bucket>_pd.csv.gz (built by pd_bank.py):
    download the museum image (IIIF servers asked for an A4-sized version)
    -> art/raw/<SKU>.png   the artwork centred on a pure white A4 page, 300 dpi
    -> art/mock/<SKU>.jpg  the listing photo: that page in the black frame

Polite to the museums: a few connections per host, retries with back-off.
Resumable (skips SKUs already uploaded) and shardable (--part k/n).

    python3 pod/fetch_pd.py --bucket luxvia-art --limit 20
    python3 pod/fetch_pd.py --all
"""
import argparse, csv, gzip, io, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
BUCKETS = ["luxvia-art", "mercury-usm", "lunar-kms", "posterleaf-store1"]
A4 = (2480, 3508)
UA = "WonderleafPrints/1.0 (wall art; contact via eBay)"
_host_locks = {}
_lock = threading.Lock()


def host_sem(url, per_host=4):
    h = urlparse(url).netloc
    with _lock:
        if h not in _host_locks:
            _host_locks[h] = threading.Semaphore(per_host)
        return _host_locks[h]


def fetch(row, session):
    urls = []
    if row["iiif_base"]:
        urls.append(f"{row['iiif_base']}/full/!{A4[0]},{A4[1]}/0/default.jpg")     # IIIF best-fit
    urls.append(row["image_url"])
    headers = {"User-Agent": UA, "AIC-User-Agent": UA}
    for url in urls:
        for attempt in range(4):
            try:
                with host_sem(url):
                    r = session.get(url, headers=headers, timeout=60)
                if r.status_code == 200 and len(r.content) > 2000:
                    return r.content
                if r.status_code in (429, 503):
                    time.sleep(5 * (attempt + 1)); continue
                break
            except Exception:
                time.sleep(3 * (attempt + 1))
    return None


def trim(im, tol=38, pad=0.05):
    """Crop to the picture: remove the blank paper sheet / scan backdrop around it.
    Works on a small blurred copy so paper grain and foxing don't count as content,
    and keeps a small margin so plate marks and captions near the image survive."""
    import numpy as np
    from PIL import ImageFilter
    small = im.convert("L").resize((max(1, im.width // 8), max(1, im.height // 8))).filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(small).astype(int)
    border = np.concatenate([a[:3].ravel(), a[-3:].ravel(), a[:, :3].ravel(), a[:, -3:].ravel()])
    paper = np.median(border)
    mask = np.abs(a - paper) > tol
    rows, cols = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return im
    y0, y1, x0, x1 = rows[0] * 8, (rows[-1] + 1) * 8, cols[0] * 8, (cols[-1] + 1) * 8
    if (x1 - x0) * (y1 - y0) < 0.08 * im.width * im.height:      # found only a speck - leave it alone
        return im
    px, py = int((x1 - x0) * pad), int((y1 - y0) * pad)
    return im.crop((max(0, x0 - px), max(0, y0 - py), min(im.width, x1 + px), min(im.height, y1 + py)))


def reject(im):
    """Object photos (book spreads, albums shot on black) and odd shapes do not sell as prints."""
    import numpy as np
    a = np.asarray(im.convert("L").resize((200, 200)))
    border = np.concatenate([a[:8].ravel(), a[-8:].ravel(), a[:, :8].ravel(), a[:, -8:].ravel()])
    ratio = im.width / im.height
    if border.mean() < 70:
        return "dark surround (object photo)"
    if ratio > 2.2 or ratio < 0.42:
        return "extreme shape"
    return None


def to_page(data):
    """Artwork centred on a pure white A4 page, portrait or landscape to match the art."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(io.BytesIO(data)).convert("RGB")
    why = reject(im)
    if why:
        return None, why
    im = trim(im)                 # 1st pass: scanner backdrop
    inner = trim(im)              # 2nd pass: the blank paper sheet round a small plate
    if inner.width * inner.height >= 0.2 * im.width * im.height:
        im = inner
    size = A4 if im.height >= im.width else (A4[1], A4[0])
    m = int(min(size) * 0.07)
    box = (size[0] - 2 * m, size[1] - 2 * m)
    s = min(box[0] / im.width, box[1] / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    page = Image.new("RGB", size, (255, 255, 255))
    page.paste(im, ((size[0] - im.width) // 2, (size[1] - im.height) // 2))
    return page, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", choices=BUCKETS)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--part", default="1/1")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--dry-run", action="store_true", help="save to out/pd_preview/ instead of R2")
    a = ap.parse_args()
    import requests
    from render import mockup
    buckets = BUCKETS if a.all else [a.bucket]
    k, n = map(int, a.part.split("/"))
    if a.dry_run:
        client, done = None, {}
        prev = HERE / "out" / "pd_preview"; prev.mkdir(parents=True, exist_ok=True)
    else:
        from publish import s3, existing
        client = s3()
        done = {b: existing(client, b, "art/mock/") for b in buckets}
    rows = []
    for b in buckets:
        with gzip.open(HERE / "out" / f"{b}_pd.csv.gz", "rt", encoding="utf-8") as fh:
            for i, r in enumerate(csv.DictReader(fh)):
                if i % n == k - 1 and f"art/mock/{r['sku']}.jpg" not in done.get(b, ()):
                    rows.append(r)
                    if a.limit and len(rows) >= a.limit:
                        break
    print(f"{len(rows):,} artworks to fetch", flush=True)
    session = requests.Session()
    ok = failed = 0
    t0 = time.time()
    stat_lock = threading.Lock()
    rejected = {}

    def one(r):
        nonlocal ok, failed
        data = fetch(r, session)
        if not data:
            with stat_lock:
                failed += 1
            return
        page, why = to_page(data)
        if page is None:
            with stat_lock:
                failed += 1
                rejected[why] = rejected.get(why, 0) + 1
            return
        raw = io.BytesIO(); page.save(raw, "PNG", dpi=(300, 300), compress_level=6)
        mock = io.BytesIO(); mockup(page, 1600, framed=True).save(mock, "JPEG", quality=88, optimize=True)
        if a.dry_run:
            (prev / f"{r['sku']}.jpg").write_bytes(mock.getvalue())
        else:
            for key, body, ct in ((f"art/raw/{r['sku']}.png", raw.getvalue(), "image/png"),
                                  (f"art/mock/{r['sku']}.jpg", mock.getvalue(), "image/jpeg")):
                client.put_object(Bucket=r["store"], Key=key, Body=body, ContentType=ct,
                                  CacheControl="public, max-age=31536000, immutable")
        with stat_lock:
            ok += 1
            if ok % 500 == 0:
                rate = ok / (time.time() - t0)
                print(f"  {ok:,}/{len(rows):,}  {rate * 3600:,.0f}/hour  failed {failed}", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(one, rows))
    print(f"done: {ok:,} uploaded, {failed:,} skipped (not downloadable or rejected: {rejected}); "
          "skipped artworks are left out of the eBay files")


if __name__ == "__main__":
    main()
