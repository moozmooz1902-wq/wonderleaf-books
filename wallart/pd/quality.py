#!/usr/bin/env python3
"""Cut the public-domain catalogue down to the artworks that look good printed.

`curate.py` already filters on what the museums SAY about a work - licence,
copyright, theme, demand, duplicates - and gets 1,090,421 records down to
153,178. What it cannot filter on is what the scan actually looks like, and
that is the whole problem with this product line: a faded mezzotint on
yellowed paper passes every metadata test and is still something nobody
wants on their wall.

Unlike the t-shirt illustrations, where "is this a recognisable motorcycle"
defeated four different pixel statistics and needed a vision model, the
defect here IS photometric. Faded, low-contrast, yellow-cast, washed-out -
those are measurements. So they get measured.

    python3 pd/quality.py --fetch       # thumbnails -> pd/thumbs/   (pod job)
    python3 pd/quality.py --score       # measure and rank
    python3 pd/quality.py --keep 18000  # write pd/KEEP.txt

Needs open outbound network: the museum IIIF hosts are not on the Claude
environment's allowlist, so --fetch runs on a pod.
"""
import argparse, gzip, io, json, os, sys, threading, time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

SRC = "pd/artworks.jsonl.gz"
CAP = int(os.environ.get("CAP", "0"))     # 0 = no cap on the shortlist
SHORT = "pd/shortlist.tsv.gz"
THUMBS = "pd/thumbs"
MIN_PX = 3508          # A3 at 300 dpi on the long side; below this it cannot print
MIN_SCORE = 40
THUMB = 400
MAX_BYTES = 3 * 1024 * 1024        # a 400px rendition is far under this


def shortlist():
    """Everything worth paying to look at: big enough to print, scored well.

    On a pod there is no artworks.jsonl.gz - the museum hosts are not on the
    Claude environment's allowlist, so the fetch has to run somewhere with
    open network, and shipping the 1,090,421-record file there is wasteful.
    A three-column shortlist is written next to this script instead.
    """
    if os.path.exists(SHORT) and not os.path.exists(SRC):
        out = []
        for line in gzip.open(SHORT, "rt"):
            aid, url, theme = line.rstrip("\n").split("\t")
            out.append({"artwork_id": aid, "iiif_base": url if "/iiif" in url or
                        not url.endswith((".jpg", ".png")) else "",
                        "image_url": url, "theme": theme, "store": ""})
        return out
    out = []
    for line in gzip.open(SRC, "rt"):
        r = json.loads(line)
        if max(r.get("image_width") or 0, r.get("image_height") or 0) < MIN_PX:
            continue
        if (r.get("score") or 0) < MIN_SCORE:
            continue
        out.append(r)
    return out


def heartbeat(path="pd.log", every=60):
    """Push the log to R2 while the job runs, not only when it finishes.

    The first two attempts at this ran for 50 and 110 minutes with the log
    uploading only at the end, so there was no way to tell a slow fetch from
    a stuck one - and the second was killed on suspicion with nothing to
    show. A job that takes an hour has to say what it is doing while it does
    it.
    """
    def push():
        try:
            import boto3
            c = boto3.client("s3",
                endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                region_name="auto")
        except Exception:
            return
        while True:
            time.sleep(every)
            try:
                if os.path.exists(path):
                    c.upload_file(path, os.environ["R2_BUCKET"], "pd/progress.log",
                                  ExtraArgs={"ContentType": "text/plain",
                                             "CacheControl": "no-store"})
            except Exception:
                pass
    t = threading.Thread(target=push, daemon=True)
    t.start()


def thumb_url(r):
    """A SMALL version of the image, from whichever host holds it.

    This is where the job went wrong twice. 42,305 of the shortlist carry an
    IIIF base and were correctly asked for 400px. The other 13,055 fell back
    to `image_url`, which is the archival master - Cleveland serves
    `<id>_full.tif`, the Met serves `/original/`. Downloading those filled a
    60 GB volume, raised DecompressionBombWarnings on 164-megapixel files,
    and dragged the rate to 9 a second. It read as a hang; it was a disk.

    Every host gets asked for a small rendition, and anything with no small
    rendition is skipped rather than guessed at.
    """
    base = r.get("iiif_base")
    if base:
        return f"{base}/full/{THUMB},/0/default.jpg"
    u = r.get("image_url") or ""
    if "openaccess-cdn.clevelandart.org" in u:
        return u.replace("_full.tif", "_web.jpg")
    if "images.metmuseum.org" in u:
        return u.replace("/original/", "/web-large/")
    return None


def fetch_and_score(rows, workers=96, budget_s=0):
    """Fetch and measure in one pass, in memory, writing no image to disk.

    The previous version wrote 16,000 thumbnails to the volume and scored
    them afterwards. Nothing needs them twice: a few numbers per artwork is
    all that survives, so the bytes are measured and dropped. That removes
    the disk entirely, parallelises the measuring, and makes a failed run
    cost nothing but time.
    """
    import urllib.request
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None          # the cap is MAX_BYTES, not pixels
    rows = [r for r in rows if thumb_url(r)]
    rows.sort(key=lambda r: -(r.get("score") or 0))
    print(f"{len(rows)} with a small rendition, {workers} workers", flush=True)
    t0 = time.time(); n = [0]; bad = [0]; codes = {}; out = []
    lock = threading.Lock(); stop = []

    def one(r):
        if stop:
            return
        try:
            req = urllib.request.Request(thumb_url(r), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError(f"over {MAX_BYTES//1024}KB after resize")
            m = measure_bytes(data)
            with lock:
                out.append({"artwork_id": r["artwork_id"], "theme": r["theme"],
                            "store": r.get("store", ""), "q": round(quality(m), 4),
                            **{k: round(v, 4) for k, v in m.items()}})
        except Exception as e:
            bad[0] += 1
            k = f"{type(e).__name__}: {str(e)[:40]}"
            with lock:
                codes[k] = codes.get(k, 0) + 1
        n[0] += 1
        if n[0] % 500 == 0:
            el = time.time() - t0
            print(f"  {n[0]}/{len(rows)}  {n[0]/el:.0f}/s  {bad[0]} failed  "
                  f"{el/60:.0f} min", flush=True)
            if budget_s and el > budget_s:
                stop.append(True)
                print(f"  time budget reached at {len(out)} measured", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, rows))
    print(f"measured {len(out)}, failed {bad[0]}, {(time.time()-t0)/60:.1f} min", flush=True)
    for k, v in sorted(codes.items(), key=lambda kv: -kv[1])[:6]:
        print(f"    {v:>6}  {k}", flush=True)
    with open("pd/quality.jsonl", "w") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    return out


def measure_bytes(data):
    """What a faded scan looks like, in numbers.

    contrast  spread between the 5th and 95th percentile of luminance. A
              crisp engraving uses the whole range; a faded one sits in a
              narrow band in the middle.
    ink       share of the image darker than mid grey - a print with real
              blacks in it, as opposed to a grey wash.
    sat       mean saturation. Separates a colour woodblock from a sepia one.
    cast      how far the average colour sits from neutral towards yellow,
              which is what aged paper does.
    """
    from PIL import Image, ImageStat
    im = Image.open(io.BytesIO(data))
    im.draft("RGB", (256, 256))         # let the JPEG decoder do the shrinking
    im = im.convert("RGB")
    im.thumbnail((256, 256))
    g = im.convert("L")
    h = g.histogram()
    tot = sum(h) or 1
    acc, lo, hi = 0, 0, 255
    for v, c in enumerate(h):
        acc += c
        if lo == 0 and acc >= tot * 0.05:
            lo = v
        if acc >= tot * 0.95:
            hi = v
            break
    dark = sum(h[:110]) / tot
    s = im.convert("HSV").getchannel("S")
    sat = ImageStat.Stat(s).mean[0] / 255
    r, gg, b = ImageStat.Stat(im).mean
    cast = (r + gg) / 2 - b
    return {"contrast": (hi - lo) / 255, "ink": dark, "sat": sat, "cast": cast / 255}


def quality(m):
    """One number. Contrast carries it; a strong yellow cast is penalised."""
    q = 0.55 * m["contrast"] + 0.25 * min(m["ink"] / 0.35, 1.0) + 0.20 * min(m["sat"] / 0.45, 1.0)
    return q - max(0.0, m["cast"] - 0.06) * 1.2


def keep(rows, target):
    """Take the best, but with a quota per theme so one does not swamp it.

    Landscapes and city views are half the shortlist by count and the least
    distinctive by eye. Without a quota the survivors would be mostly those,
    which is how a catalogue ends up looking like a job lot.
    """
    by = defaultdict(list)
    for r in rows:
        by[r["theme"]].append(r)
    for v in by.values():
        v.sort(key=lambda r: -r["q"])
    quota = max(1, target // max(1, len(by)))
    out, spare = [], []
    for t, v in by.items():
        out += v[:quota]
        spare += v[quota:]
    spare.sort(key=lambda r: -r["q"])
    out += spare[:max(0, target - len(out))]
    out.sort(key=lambda r: -r["q"])
    with open("pd/KEEP.txt", "w") as f:
        f.write("\n".join(r["artwork_id"] for r in out))
    per = defaultdict(int)
    for r in out:
        per[r["theme"]] += 1
    print(f"kept {len(out)}")
    for t, n in sorted(per.items(), key=lambda kv: -kv[1]):
        print(f"  {t:<22} {n:>6}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--keep", type=int, default=0)
    ap.add_argument("--workers", type=int, default=96)
    ap.add_argument("--budget", type=int, default=0, help="seconds to spend fetching")
    a = ap.parse_args()
    heartbeat()
    rows = shortlist()
    if CAP:
        rows.sort(key=lambda r: -(r.get("score") or 0))
        rows = rows[:CAP]
    print(f"shortlist: {len(rows):,} of 153,178 are >= {MIN_PX}px and score >= {MIN_SCORE}"
          + (f", capped at {CAP:,}" if CAP else ""), flush=True)
    scored = fetch_and_score(rows, a.workers, a.budget) if a.fetch else \
        [json.loads(l) for l in open("pd/quality.jsonl")]
    if a.keep:
        keep(scored, a.keep)


if __name__ == "__main__":
    main()
