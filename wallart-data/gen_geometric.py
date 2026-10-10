#!/usr/bin/env python3
"""Grammar G11, the hard-edge geometric block, drawn with code.

Why code and not diffusion: the research found this block is 9.12% of the
competitor corpus (122,958 listings) and consists of circles, arcs, half-discs
and a horizon split in three flat colours with no texture at all. Procedural
output is free, instant and pixel-perfect; diffusion would be slower, dearer
and worse at exactly the hard edges that define it.

Palettes are the three colour strategies the research measured, not invented:
C1 a complementary pair, C2 warm neutral with one hot accent, C3 full spectrum
at uniform saturation. Rendered at 4x and downsampled, so the edges are clean
without anti-aliasing artefacts.
"""
import os, random, sys
from PIL import Image, ImageDraw

W, H = 1106, 1598           # the frame aperture from frames.py
SS = 3                      # supersample

# C1 complementary pairs - the house trick: complementaries hold contrast at
# distance, where tonal differences collapse. Five of the first eleven images
# studied used orange against blue.
C1 = [(("#C85A28", "#1C3A4B"), "#E9DCC9"), (("#D96A33", "#13303F"), "#F0E6D6"),
      (("#E07A3C", "#223A5E"), "#EDE4D3"), (("#B2452A", "#2E4A52"), "#E8DFD0"),
      (("#CC5C2E", "#35576B"), "#F2EADB")]
# C2 warm neutral plus one hot accent at roughly 5% of the surface
C2 = [(("#C8613A", "#CFC3AE"), "#EFE8DB"), (("#B9543B", "#D6CBB6"), "#F3EDE2"),
      (("#A8513C", "#C9BFA8"), "#EEE7D9")]
# C3 full spectrum held together by one consistent saturation and a pale ground
C3 = [(("#D9743F", "#4C7A8A", "#C9A227", "#7A5B8B"), "#E7E0D2"),
      (("#CC6B4A", "#5B8C7B", "#D4A63C", "#6E5A7D"), "#EDE7DA")]


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def design(rng):
    pal = rng.choice(["C1", "C1", "C1", "C2", "C2", "C3"])     # weight toward C1
    if pal == "C3":
        cols, ground = rng.choice(C3)
    elif pal == "C2":
        cols, ground = rng.choice(C2)
    else:
        cols, ground = rng.choice(C1)
    cols = [hx(c) for c in cols]
    g = hx(ground)
    w, h = W * SS, H * SS
    im = Image.new("RGB", (w, h), g)
    d = ImageDraw.Draw(im)

    # the horizon split: one flat band, never a gradient (gradients are the
    # clearest tell of cheap generated work)
    hy = int(h * rng.uniform(0.52, 0.70))
    d.rectangle([0, hy, w, h], fill=cols[1 % len(cols)])

    kind = rng.choice(["disc", "arcs", "halfdisc", "stack", "columns"])
    cx = int(w * rng.uniform(0.34, 0.66))
    if kind == "disc":
        r = int(w * rng.uniform(0.26, 0.38))
        d.ellipse([cx - r, hy - r, cx + r, hy + r], fill=cols[0])
    elif kind == "halfdisc":
        r = int(w * rng.uniform(0.30, 0.42))
        d.pieslice([cx - r, hy - r, cx + r, hy + r], 180, 360, fill=cols[0])
    elif kind == "arcs":
        for i in range(rng.randint(3, 5)):
            r = int(w * (0.42 - i * 0.07))
            d.pieslice([cx - r, hy - r, cx + r, hy + r], 180, 360,
                       fill=cols[i % len(cols)])
    elif kind == "stack":
        n = rng.randint(3, 5)
        bh = int(h * 0.09)
        for i in range(n):
            yy = int(h * 0.20) + i * int(bh * 1.5)
            iw = int(w * rng.uniform(0.34, 0.74))
            x0 = (w - iw) // 2
            d.rectangle([x0, yy, x0 + iw, yy + bh], fill=cols[i % len(cols)])
    else:
        n = rng.randint(3, 6)
        gap = int(w * 0.035)
        cw = (w - gap * (n + 1)) // n
        for i in range(n):
            ch = int(h * rng.uniform(0.22, 0.56))
            x0 = gap + i * (cw + gap)
            d.rectangle([x0, hy - ch, x0 + cw, hy], fill=cols[i % len(cols)])

    return im.resize((W, H), Image.LANCZOS), pal, kind


if __name__ == "__main__":
    outdir = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    os.makedirs(outdir, exist_ok=True)
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 11)
    for i in range(n):
        im, pal, kind = design(rng)
        p = os.path.join(outdir, f"geo_{i:02d}_{pal}_{kind}.png")
        im.save(p)
        print(f"  {os.path.basename(p)}  {im.size}")
