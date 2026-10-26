#!/usr/bin/env python3
"""Render an unframed photograph for every design in the selection.

WHY THIS HAS TO EXIST. Every picture in the buckets is a framed mockup.
build_ebay.py says so plainly: "no unframed photograph was ever rendered",
and on eBay the unframed rows simply carry no PicURL so eBay falls back to
the main image. That is fine on eBay. It is not fine in a Merchant Center
feed, where every variant carries its own image - an unframed print sold
against a photograph of a framed one is the image/product mismatch that
disapproves a product and, repeated, reads as misrepresentation.

So the unframed option needs its own photograph, and the raw artwork is
already in R2: the render stage writes mockups under <prefix>listing/ and
leaves the generated panel beside it at <prefix><sku>.jpg.

THE CROP IS NOT OPTIONAL. render_worker.py takes CROP = 0.11 off the bottom
of every panel before composing, and the docstring calls it "the signature
fix": FLUX scrawls a fake signature along the bottom edge, and the site
states in writing that nothing is signed. Serving the raw panel would put
those signatures back on the shop. The same 11% comes off here.

    python3 unframed.py            # all designs in selection.json
    python3 unframed.py -n 4       # a few, to look at first
"""
import argparse, concurrent.futures as cf, io, json, os, subprocess, sys
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "site", "public", "unframed")

CROP = 0.11                 # must match render_worker.CROP
CANVAS = 1600               # same square as the framed photographs
WALL = (237, 234, 227)      # the cream every mockup is shot on
MARGIN = 0.14               # of the canvas, each side

HOSTS = {
    "luxvia-art": ("https://pub-6004b56e7a254092b7bfec9a24cf9484.r2.dev", "luxvia"),
    "posterleaf-store1": ("https://pub-0ad8669f94ce487499368f153cdb0c1b.r2.dev", "store1"),
    "lunar-kms": ("https://pub-1f879b9875164bf59a4806f4026100d0.r2.dev", "store7"),
    "mercury-usm": ("https://pub-0393733d8d814d7395f37e1eaf666e62.r2.dev", "store2"),
}


def panel_url(bucket, prefix_hint, sku):
    host, pre = HOSTS[bucket]
    return f"{host}/{prefix_hint or pre}/gen/{sku}.jpg"


def build(im):
    """Artwork on the cream wall, with the soft shadow of a sheet of paper.

    The shadow is the whole point: without it this is just a picture on a
    background and a shopper cannot tell it from the framed one at thumbnail
    size. With it, it reads as a loose print lying on a surface, which is
    what is being sold."""
    w, h = im.size
    art = im.crop((0, 0, w, int(h * (1 - CROP))))
    inner = int(CANVAS * (1 - 2 * MARGIN))
    art.thumbnail((inner, inner), Image.LANCZOS)
    aw, ah = art.size
    x, y = (CANVAS - aw) // 2, (CANVAS - ah) // 2

    canvas = Image.new("RGB", (CANVAS, CANVAS), WALL)
    shadow = Image.new("L", (CANVAS, CANVAS), 0)
    pad = 10
    shadow.paste(60, (x - pad + 14, y - pad + 20, x + aw + pad + 14, y + ah + pad + 20))
    shadow = shadow.filter(ImageFilter.GaussianBlur(26))
    canvas.paste(Image.new("RGB", (CANVAS, CANVAS), (120, 116, 108)), (0, 0), shadow)
    canvas.paste(art, (x, y))
    return canvas


def one(d):
    sku, bucket = d["sku"], d["bucket"]
    dest = os.path.join(OUT, f"{sku}.jpg")
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return "skip"
    url = panel_url(bucket, d.get("_prefix"), sku)
    try:
        # curl, not urllib. tshirt/ACCESS.md: "Python's urllib gets 403
        # through the proxy; curl gets 200." Measured again here - urllib
        # 403s on every panel, curl fetches them all.
        r = subprocess.run(["curl", "-sS", "--fail", "--max-time", "60",
                            "--retry", "4", "--retry-delay", "3",
                            "--retry-all-errors", url],
                           capture_output=True, timeout=180)
        if r.returncode != 0 or not r.stdout:
            raise RuntimeError((r.stderr or b"")[:90].decode("utf-8", "replace"))
        raw = r.stdout
        build(Image.open(io.BytesIO(raw)).convert("RGB")).save(
            dest, "JPEG", quality=88, optimize=True, progressive=True)
        return "ok"
    except Exception as e:
        return f"FAIL {sku}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=0)
    ap.add_argument("-j", type=int, default=8,
                    help="r2.dev is rate limited; a measured run saw 1015s "
                         "at ~70 req/s and none at ~19. Stay low.")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    designs = json.load(open(os.path.join(HERE, "selection.json")))["designs"]
    if a.n:
        designs = designs[:a.n]
    print(f"{len(designs)} designs -> {OUT}")
    res = []
    with cf.ThreadPoolExecutor(a.j) as ex:
        for i, r in enumerate(ex.map(one, designs), 1):
            res.append(r)
            if i % 40 == 0:
                print(f"  {i}/{len(designs)}")
    bad = [r for r in res if r.startswith("FAIL")]
    print(f"written {res.count('ok')}, already there {res.count('skip')}, failed {len(bad)}")
    for b in bad[:5]:
        print("  ", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
