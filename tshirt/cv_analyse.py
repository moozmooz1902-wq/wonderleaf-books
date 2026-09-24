"""Extract visual features from every image with Pillow. No API, no cost.

    python3 cv_analyse.py hash     # perceptual-hash to find unique artwork
    python3 cv_analyse.py features # garment colour, ink count, coverage, placement

Covers everything measurable without a language model. The API is then only
needed to READ TEXT, and only on the unique designs that actually have text.
"""
import json, sys
from collections import Counter
from pathlib import Path
from PIL import Image

IMG = Path("images")


def load(i):
    return Image.open(IMG / f"{i:06d}.webp")


def dhash(im, size=16):
    """Difference hash of the PRINT AREA ONLY.

    Hashing the whole product photo collapses on garment silhouette - every
    vest tank top hashes alike regardless of what is printed on it. Cropping
    to the chest block first makes the hash describe the artwork.
    """
    w, h = im.size
    im = im.crop((int(w * .26), int(h * .14), int(w * .74), int(h * .66)))
    g = im.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for r in range(size):
        row = px[r * (size + 1):(r + 1) * (size + 1)]
        for c in range(size):
            bits = (bits << 1) | (row[c] < row[c + 1])
    return f"{bits:016x}"


def features(im):
    """Garment colour, ink colours, print coverage and placement."""
    im = im.convert("RGB")
    im.thumbnail((180, 180))
    w, h = im.size
    px = im.load()

    def avg(box):
        x0, y0, x1, y1 = box
        vals = [px[x, y] for y in range(y0, y1, 2) for x in range(x0, x1, 2)]
        n = len(vals) or 1
        return tuple(sum(v[k] for v in vals) // n for k in range(3))

    # shoulders: garment colour, away from the print and away from skin
    g = avg((int(w * .10), int(h * .16), int(w * .26), int(h * .30)))
    mx, mn = max(g), min(g)
    if mx < 68: garment = "black"
    elif mx > 218 and mx - mn < 20: garment = "white"
    elif mx > 170 and mx - mn < 45: garment = "natural"
    elif mx < 125 and mx - mn < 32: garment = "charcoal"
    elif g[2] > g[0] + 22: garment = "navy"
    elif g[1] > g[2] + 12 and g[0] > g[2] + 8: garment = "olive"
    elif mx - mn < 34: garment = "grey"
    else: garment = "other"

    # print area: centre chest block, quantised ink colours
    cx0, cy0, cx1, cy1 = int(w * .28), int(h * .18), int(w * .72), int(h * .62)
    ink = Counter()
    lit = 0
    tot = 0
    for y in range(cy0, cy1, 2):
        for x in range(cx0, cx1, 2):
            p = px[x, y]
            tot += 1
            if sum(abs(p[k] - g[k]) for k in range(3)) > 90:   # differs from garment
                lit += 1
                ink[tuple((v // 40) * 40 for v in p)] += 1
    coverage = lit / max(tot, 1)
    inks = sum(1 for _, n in ink.items() if n / max(lit, 1) >= 0.06)

    # vertical centre of mass of the print -> placement
    ys = []
    for y in range(int(h * .10), int(h * .80), 3):
        row = sum(1 for x in range(int(w * .20), int(w * .80), 3)
                  if sum(abs(px[x, y][k] - g[k]) for k in range(3)) > 90)
        ys.append((y, row))
    mass = sum(n for _, n in ys) or 1
    com = sum(y * n for y, n in ys) / mass / h
    if coverage < 0.03: placement = "minimal"
    elif com < 0.30: placement = "upper_chest"
    elif com > 0.52: placement = "lower_centre"
    else: placement = "centre_chest"

    return dict(garment=garment, ink_colours=inks, coverage=round(coverage, 3),
                placement=placement,
                mono=inks <= 1, full_colour=inks >= 4)


def run_hash():
    rows = json.load(open("all.json"))
    seen = {}
    groups = Counter()
    out = []
    miss = 0
    for i in range(len(rows)):
        p = IMG / f"{i:06d}.webp"
        if not p.exists():
            miss += 1; out.append(None); continue
        try:
            hv = dhash(load(i))
        except Exception:
            miss += 1; out.append(None); continue
        out.append(hv)
        groups[hv] += 1
        seen.setdefault(hv, i)
        if (i + 1) % 25000 == 0:
            print(f"  hashed {i+1:,}", flush=True)
    json.dump(out, open("hashes.json", "w"))
    uniq = len(groups)
    print(f"\nimages hashed   : {len(rows)-miss:,}  (missing {miss:,})")
    print(f"UNIQUE ARTWORK  : {uniq:,}")
    print(f"duplicate listings collapsed: {len(rows)-miss-uniq:,}")
    print(f"\nmost-reused artwork:")
    for h, n in groups.most_common(6):
        print(f"   x{n:<5} first seen as: {rows[seen[h]]['title'][:60]}")


def run_features():
    rows = json.load(open("all.json"))
    hashes = json.load(open("hashes.json")) if Path("hashes.json").exists() else None
    done = set()
    out = open("cv_features.jsonl", "w", encoding="utf-8")
    n = 0
    for i in range(len(rows)):
        if hashes:
            h = hashes[i]
            if h is None or h in done: continue
            done.add(h)
        p = IMG / f"{i:06d}.webp"
        if not p.exists(): continue
        try:
            f = features(load(i))
        except Exception:
            continue
        f.update(idx=i, title=rows[i]["title"], sold=rows[i]["sold"],
                 hash=hashes[i] if hashes else None)
        out.write(json.dumps(f) + "\n")
        n += 1
        if n % 10000 == 0: print(f"  analysed {n:,}", flush=True)
    out.close()
    print(f"\n{n:,} unique designs analysed -> cv_features.jsonl  (cost: $0)")


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "hash": run_hash()
    elif c == "features": run_features()
    else: sys.exit(__doc__)
