"""
check_designs.py — inspect designs before printing, and report numbers.

Runs each label through exactly the same conversion the print tool uses, then
measures the things that actually go wrong on a press. Paste the output back
and it can be read without needing the files themselves.

    python3 check_designs.py GR-0524434 GR-0542718 ...
    python3 check_designs.py --file labels.txt
"""

import argparse, io, os, re, ssl, sys, urllib.request

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument("skus", nargs="*")
ap.add_argument("--file")
ap.add_argument("--base",
                default="https://pub-19fad43c12d848caa97d6d53a8695d03.r2.dev")
ap.add_argument("--width", type=float, default=9.6)
args = ap.parse_args()

skus = list(args.skus)
if args.file:
    skus += [l.strip() for l in open(args.file) if l.strip()]
if not skus:
    raise SystemExit("give some labels")

# reuse the real conversion so the numbers reflect what actually prints
import order as _o
_o.args = argparse.Namespace(scale=2, width=args.width, soft=False,
                             no_halftone=False, lpi=28, no_white=False,
                             no_preview=True, out="print", base=args.base,
                             skus=[], file=None)

try:
    import halftone
    HT = True
except ImportError:
    HT = False


def ctxs():
    out = []
    try:
        import certifi
        out.append(ssl.create_default_context(cafile=certifi.where()))
    except Exception:
        pass
    loose = ssl.create_default_context()
    loose.check_hostname = False
    loose.verify_mode = ssl.CERT_NONE
    out.append(loose)
    return out


CTXS = ctxs()
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def fetch(did):
    url = f"{args.base}/art/raw/{did}.png"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for c in CTXS:
        try:
            with urllib.request.urlopen(req, timeout=30, context=c) as r:
                return Image.open(io.BytesIO(r.read())).convert("RGB")
        except Exception as e:
            last = e
    raise last


print(f"{len(skus)} designs\n")
print(f"{'LABEL':<14}{'SHAPE':>7}{'CORNER':>8}{'INK':>7}{'DOTS':>7}"
      f"{'BRIGHT':>8}  VERDICT")
print("-" * 74)

rows = []
for sku in skus:
    m = re.search(r"(\d+)", sku)
    if not m:
        print(f"{sku:<14}  bad label")
        continue
    did = str(int(m.group(1)))
    try:
        src = fetch(did)
        art = _o.to_print(src)
        if HT:
            art = halftone.apply(art, lpi=28)

        a = np.asarray(art)
        al = a[..., 3]
        solid = al > 127
        ys, xs = np.where(solid)
        if len(ys) == 0:
            print(f"{sku:<14}  nothing to print")
            continue

        # does it read as a square block?
        box = solid[ys.min():ys.max(), xs.min():xs.max()]
        fill = box.mean()

        # corners of the bounding box — a square print has ink here
        k = max(40, min(box.shape) // 12)
        corners = np.mean([
            box[:k, :k].mean(), box[:k, -k:].mean(),
            box[-k:, :k].mean(), box[-k:, -k:].mean()])

        ink = solid.mean()
        dots = ((al > 0) & (al < 255)).mean()
        bright = a[..., :3][solid].mean() if solid.any() else 0

        issues = []
        if fill > 0.88 and corners > 0.5:
            issues.append("SQUARE")
        if ink > 0.55:
            issues.append("heavy ink")
        if ink < 0.03:
            issues.append("almost empty")
        if bright < 55:
            issues.append("dark")
        verdict = ", ".join(issues) if issues else "ok"

        print(f"{sku:<14}{fill*100:6.0f}%{corners*100:7.0f}%{ink*100:6.0f}%"
              f"{dots*100:6.1f}%{bright:7.0f}  {verdict}")
        rows.append((sku, fill, corners, ink, bright, verdict))
    except Exception as e:
        print(f"{sku:<14}  FAILED: {str(e)[:44]}")

print()
if rows:
    bad = [r for r in rows if r[5] != "ok"]
    print(f"{len(rows) - len(bad)} of {len(rows)} clean")
    print()
    print("SHAPE   how much of the bounding box is inked. Near 100% with high")
    print("        CORNER means it prints as a square block, not a design.")
    print("CORNER  ink in the four corners. Should be low.")
    print("INK     share of the whole canvas printed. Over ~55% is heavy and")
    print("        will feel stiff on the shirt.")
    print("DOTS    area converted to halftone. Higher on smoky designs.")
    print("BRIGHT  mean brightness of the ink. Under 55 may look muddy on")
    print("        black.")
