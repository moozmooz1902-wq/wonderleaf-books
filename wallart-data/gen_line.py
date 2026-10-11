#!/usr/bin/env python3
"""Minimal line art, drawn in code. No GPU, no model, no licence question.

This is the block the seller picked out - "line in a desert, line in here,
line in there". It is also the cheapest thing in the catalogue: a design costs
about 0.2 s of one CPU core instead of 4 s of a rented GPU, which is roughly
three thousand times less money. Every design the line families can carry is a
design the diffusion budget does not have to.

Twelve families, each with its own parameters, drawn at 2x and downsampled so
the strokes are clean without relying on PIL's patchy anti-aliasing.

EDGES. Some of these go in the frame full-bleed, and the moulding eats about
1% of each side. Anything that TERMINATES - a disc, the end of an arc, a
closed contour - is kept inside SAFE. Anything that SPANS - a horizon, a dune
ridge, a wave - is drawn deliberately past the edge on both sides, so it
reads as continuing behind the frame instead of stopping just short of it.
That is the difference between a cut-off line and an intentional one.
"""
import math, os, random, sys
from PIL import Image, ImageDraw

W, H = 1200, 1697          # A-series print master
SS = 2                     # supersample factor
SAFE = 0.07                # terminating elements stay this far in, each side
BLEED = 0.06               # spanning elements run this far past the edge

# ink on paper. Measured palette strategies from the corpus, not invented:
# C1 complementary pair, C2 warm neutral with one hot accent, C3 ink duotone.
INKS = [
    ("#1D1D1B", "#F4F1EA", "#C8613A"),   # black on bone, terracotta accent
    ("#2E4A52", "#EDE4D3", "#C85A28"),   # petrol on oatmeal, burnt orange
    ("#4A3A30", "#F3EDE2", "#B9543B"),   # bistre on cream, brick
    ("#1C3A4B", "#E9DCC9", "#D96A33"),   # navy on sand, rust
    ("#223129", "#EFF1E8", "#7E9C84"),   # forest on pale sage, sage
    ("#3A3E52", "#EDEEF3", "#8A94A6"),   # slate on cool white, blue grey
    ("#5B4636", "#EAE0CE", "#A8763E"),   # walnut on parchment, ochre
    ("#2B2B2B", "#E7E2D8", "#6E7A62"),   # charcoal on linen, olive
]


def _hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


class Pad:
    """Draw in 0..1 coordinates; the pad handles supersampling for you."""

    def __init__(self, paper):
        self.w, self.h = W * SS, H * SS
        self.im = Image.new("RGB", (self.w, self.h), paper)
        self.d = ImageDraw.Draw(self.im)

    def P(self, x, y):
        return (x * self.w, y * self.h)

    def line(self, pts, ink, lw):
        self.d.line([self.P(*p) for p in pts], fill=ink,
                    width=max(1, int(lw * self.w)), joint="curve")

    def disc(self, cx, cy, r, fill):
        x, y = self.P(cx, cy); rr = r * self.w
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill)

    def ring(self, cx, cy, r, ink, lw):
        x, y = self.P(cx, cy); rr = r * self.w
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=ink,
                       width=max(1, int(lw * self.w)))

    def poly(self, pts, fill):
        self.d.polygon([self.P(*p) for p in pts], fill=fill)

    def out(self):
        return self.im.resize((W, H), Image.LANCZOS)


def _ridge(rng, y0, amp, n=9, wobble=0.5):
    """A spanning ridge: starts before the left edge, ends after the right."""
    xs = [-BLEED + (1 + 2 * BLEED) * i / (n - 1) for i in range(n)]
    ph = rng.uniform(0, 6.28)
    return [(x, y0 - amp * (math.sin(ph + x * rng.uniform(2.0, 4.5)) * wobble
                            + math.sin(ph * 1.7 + x * 7.3) * (1 - wobble) * 0.4))
            for x in xs]


# ---------------------------------------------------------------- families

def f_dunes(p, rng, ink, accent, lw):
    """The desert line. Spanning ridges, optional sun inside the safe box."""
    n = rng.randint(3, 6)
    if rng.random() < 0.72:
        r = rng.uniform(0.09, 0.17)
        cy = rng.uniform(SAFE + r, 0.46)
        p.disc(rng.uniform(SAFE + r, 1 - SAFE - r), cy, r,
               accent if rng.random() < 0.5 else ink)
    for i in range(n):
        y = 0.42 + 0.52 * (i + 1) / (n + 1) + rng.uniform(-0.02, 0.02)
        p.line(_ridge(rng, y, rng.uniform(0.03, 0.09), wobble=rng.uniform(0.3, 0.9)),
               ink, lw)


def f_mountain(p, rng, ink, accent, lw):
    base = rng.uniform(0.62, 0.74)
    for k in range(rng.randint(1, 3)):
        pk = rng.uniform(0.25, 0.75)
        hgt = rng.uniform(0.18, 0.34) * (1 - k * 0.22)
        pts = [(-BLEED, base), (pk - 0.22, base - hgt * 0.45),
               (pk, base - hgt), (pk + 0.26, base - hgt * 0.38), (1 + BLEED, base)]
        p.line(pts, ink, lw)
    if rng.random() < 0.6:
        r = rng.uniform(0.07, 0.13)
        p.ring(rng.uniform(SAFE + r, 1 - SAFE - r), rng.uniform(SAFE + r, 0.34),
               r, accent, lw)
    p.line([(-BLEED, base + rng.uniform(0.05, 0.12)),
            (1 + BLEED, base + rng.uniform(0.05, 0.12))], ink, lw)


def f_contour(p, rng, ink, accent, lw):
    """Topographic: nested closed curves, all inside the safe box.

    The harmonics are randomised in BOTH frequency and phase. An earlier
    version varied only the phase and produced three visually identical
    designs in a sample of thirteen - the near-duplicate failure in
    miniature, which is the one thing this catalogue cannot repeat.
    """
    cx, cy = rng.uniform(0.36, 0.64), rng.uniform(0.38, 0.60)
    n = rng.randint(4, 12)
    harm = [(rng.randint(2, 6), rng.uniform(0.10, 0.34), rng.uniform(0, 6.28)),
            (rng.randint(5, 11), rng.uniform(0.04, 0.17), rng.uniform(0, 6.28)),
            (rng.randint(2, 4), rng.uniform(0.0, 0.12), rng.uniform(0, 6.28))]
    squash = rng.uniform(0.62, 1.15)
    big = rng.uniform(0.24, 0.40)
    drift = rng.uniform(0.0, 0.035)            # each ring offset from the last
    for k in range(n):
        s_ = (k + 1) / n
        ox, oy = drift * (1 - s_) * rng.uniform(-1, 1), drift * (1 - s_)
        pts = []
        for i in range(121):
            t = 6.283 * i / 120
            rad = big * s_ * (1 + sum(a * math.sin(f * t + ph) for f, a, ph in harm))
            x = cx + ox + rad * math.cos(t) * squash
            y = cy + oy + rad * math.sin(t) * (1.35 - squash * 0.3)
            pts.append((min(max(x, SAFE), 1 - SAFE), min(max(y, SAFE), 1 - SAFE)))
        p.line(pts + [pts[0]], accent if (k == n - 1 and rng.random() < .35) else ink, lw)


def f_waves(p, rng, ink, accent, lw):
    n = rng.randint(7, 16)
    amp = rng.uniform(0.012, 0.035)
    for i in range(n):
        y = 0.14 + 0.72 * i / (n - 1)
        a = amp * (0.4 + 1.2 * math.sin(3.14 * i / max(n - 1, 1)))
        p.line(_ridge(rng, y, a, n=15, wobble=1.0), ink, lw)
    if rng.random() < 0.4:
        r = rng.uniform(0.06, 0.11)
        p.disc(rng.uniform(SAFE + r, 1 - SAFE - r), rng.uniform(SAFE + r, 0.3), r, accent)


def f_arch(p, rng, ink, accent, lw):
    """A portal. Closed, so entirely inside the safe box. Nested or filled -
    the bare outline the first version drew read as an empty sheet."""
    m = rng.uniform(SAFE + 0.03, SAFE + 0.16)
    bot = rng.uniform(0.80, 0.90)
    k = rng.randint(1, 3)
    filled = rng.random() < 0.55
    for j in range(k):
        mm = m + j * rng.uniform(0.045, 0.085)
        if mm > 0.44:
            break
        r = 0.5 - mm
        sh = r * W / H
        top = rng.uniform(0.13, 0.22) + j * 0.04
        # sweep pi -> 0 so the crown runs LEFT to RIGHT. Sweeping 0 -> pi
        # joins the left foot to the right shoulder and the arch draws as an
        # hourglass with the sides crossed.
        crown = [(0.5 + r * math.cos(math.pi - math.pi * i / 48),
                  top + sh - sh * math.sin(math.pi - math.pi * i / 48))
                 for i in range(49)]
        body = [(mm, bot)] + crown + [(1 - mm, bot)]
        if filled and j == 0:
            p.poly(body, accent)
        p.line(body, ink if not (filled and j == 0) else accent, lw * 1.2)
    p.line([(-BLEED, bot), (1 + BLEED, bot)], ink, lw * 1.4)
    if rng.random() < 0.35:
        p.disc(0.5, bot - rng.uniform(0.20, 0.38), rng.uniform(0.04, 0.09),
               ink if filled else accent)


def f_rings(p, rng, ink, accent, lw):
    cx, cy = rng.uniform(0.42, 0.58), rng.uniform(0.40, 0.56)
    n = rng.randint(4, 9)
    rmax = min(cx, 1 - cx, (cy - SAFE), (1 - SAFE - cy) * 0.9) - 0.01
    for i in range(n):
        p.ring(cx, cy, rmax * (i + 1) / n, accent if i == n - 2 else ink, lw)
    if rng.random() < 0.45:
        p.disc(cx, cy, rmax / n * 0.8, accent)


def f_rays(p, rng, ink, accent, lw):
    cx, cy = rng.uniform(0.38, 0.62), rng.uniform(0.52, 0.72)
    n = rng.randint(9, 22)
    for i in range(n):
        a = math.pi * (i + 0.5) / n
        rr = rng.uniform(0.30, 0.46)
        p.line([(cx, cy), (cx + rr * math.cos(a) * 0.9, cy - rr * math.sin(a) * 0.9)], ink, lw)
    p.disc(cx, cy, rng.uniform(0.03, 0.07), accent)
    p.line([(-BLEED, cy), (1 + BLEED, cy)], ink, lw * 1.4)


def f_botanical(p, rng, ink, accent, lw):
    """Four plant forms. The first version drew chevrons for leaves and looked
    like a tally chart; leaves are drawn as closed teardrops now."""
    form = rng.choice(["eucalyptus", "fern", "grass", "stem"])
    x = rng.uniform(0.42, 0.58)
    bot, top = rng.uniform(0.86, 0.93), rng.uniform(SAFE + 0.01, 0.20)
    bend = rng.uniform(-0.05, 0.05)
    stem = [(x + bend * math.sin(3.14 * t), bot - (bot - top) * t)
            for t in [i / 60 for i in range(61)]]

    def leaf(sx, sy, ang, L, w, col):
        pts = []
        for i in range(25):
            t = i / 24
            off = w * math.sin(3.14 * t)
            pts.append((sx + L * t * math.cos(ang) - off * math.sin(ang),
                        sy + L * t * math.sin(ang) + off * math.cos(ang)))
        for i in range(25):
            t = 1 - i / 24
            off = -w * math.sin(3.14 * t)
            pts.append((sx + L * t * math.cos(ang) - off * math.sin(ang),
                        sy + L * t * math.sin(ang) + off * math.cos(ang)))
        p.poly(pts, col) if rng.random() < 0.45 else p.line(pts, col, lw * 0.8)

    if form == "grass":
        for i in range(rng.randint(7, 16)):
            gx = rng.uniform(0.22, 0.78)
            h = rng.uniform(0.18, 0.52)
            sway = rng.uniform(-0.07, 0.07)
            p.line([(gx, bot), (gx + sway * 0.4, bot - h * 0.55),
                    (gx + sway, bot - h)], ink, lw * rng.uniform(0.6, 1.1))
        p.line([(-BLEED, bot), (1 + BLEED, bot)], ink, lw)
        return

    p.line(stem, ink, lw)
    n = {"eucalyptus": rng.randint(8, 16), "fern": rng.randint(14, 24),
         "stem": rng.randint(3, 6)}[form]
    for i in range(n):
        t = 0.08 + 0.88 * i / max(n - 1, 1)
        sx, sy = stem[int(t * 60)]
        side = -1 if i % 2 else 1
        L = {"eucalyptus": rng.uniform(0.09, 0.15),
             "fern": rng.uniform(0.05, 0.11),
             "stem": rng.uniform(0.13, 0.20)}[form] * (1 - 0.35 * t)
        ang = math.atan2(-0.35, side) + rng.uniform(-0.25, 0.25)
        leaf(sx, sy, ang, L, L * rng.uniform(0.16, 0.34),
             accent if rng.random() < 0.18 else ink)


def f_oneline(p, rng, ink, accent, lw):
    """One continuous path that never lifts. Three or four lobes with a slight
    asymmetric warp; more lobes than that and it stops reading as a drawing
    and starts reading as a test pattern."""
    n = rng.randint(2, 4)
    a, warp = rng.uniform(0, 6.28), rng.uniform(0.0, 0.22)
    cx, cy = rng.uniform(0.45, 0.55), rng.uniform(0.44, 0.56)
    amp = rng.uniform(0.22, 0.40)
    pts = []
    for i in range(480):
        t = 6.283 * i / 479
        rad = 0.30 * (1 + amp * math.sin(n * t + a) + warp * math.sin(t + a * 1.7))
        pts.append((min(max(cx + rad * math.cos(t) * 0.80, SAFE), 1 - SAFE),
                    min(max(cy + rad * math.sin(t) * 1.12, SAFE), 1 - SAFE)))
    p.line(pts + [pts[0]], ink, lw * rng.uniform(1.1, 1.8))
    if rng.random() < 0.45:
        p.disc(cx + rng.uniform(-0.12, 0.12), cy + rng.uniform(-0.14, 0.14),
               rng.uniform(0.025, 0.055), accent)


def f_bands(p, rng, ink, accent, lw):
    """Half flat, half line: filled dune bands with a drawn edge."""
    n = rng.randint(2, 4)
    cuts = sorted(rng.uniform(0.32, 0.88) for _ in range(n))
    for i, y in enumerate(cuts):
        r = _ridge(rng, y, rng.uniform(0.03, 0.08))
        fill = accent if i == len(cuts) - 1 and rng.random() < 0.5 else ink
        p.poly(r + [(1 + BLEED, 1 + BLEED), (-BLEED, 1 + BLEED)],
               fill if i == len(cuts) - 1 else fill)
    if rng.random() < 0.6:
        rr = rng.uniform(0.08, 0.15)
        p.disc(rng.uniform(SAFE + rr, 1 - SAFE - rr), rng.uniform(SAFE + rr, 0.34), rr, ink)


def f_grid(p, rng, ink, accent, lw):
    cols, rows = rng.randint(3, 7), rng.randint(4, 9)
    m = SAFE + 0.03
    for r in range(rows):
        for c in range(cols):
            x = m + (1 - 2 * m) * (c + 0.5) / cols
            y = m + (1 - 2 * m) * (r + 0.5) / rows
            k = rng.random()
            col = accent if rng.random() < 0.18 else ink
            if k < 0.4:
                p.disc(x, y, rng.uniform(0.012, 0.03), col)
            elif k < 0.75:
                h = rng.uniform(0.02, 0.05)
                p.line([(x, y - h), (x, y + h)], col, lw)
            else:
                p.ring(x, y, rng.uniform(0.016, 0.032), col, lw)


def f_horizonsun(p, rng, ink, accent, lw):
    y = rng.uniform(0.46, 0.68)
    r = rng.uniform(0.11, 0.20)
    cx = rng.uniform(SAFE + r, 1 - SAFE - r)
    p.disc(cx, y - r * rng.uniform(0.1, 0.8), r, accent)
    for i in range(rng.randint(2, 5)):
        p.line([(-BLEED, y + i * rng.uniform(0.035, 0.075)),
                (1 + BLEED, y + i * rng.uniform(0.035, 0.075))], ink, lw)


def f_hatch(p, rng, ink, accent, lw):
    y0 = rng.uniform(0.30, 0.50)
    n = rng.randint(22, 60)
    for i in range(n):
        x = SAFE + (1 - 2 * SAFE) * i / (n - 1)
        h = rng.uniform(0.10, 0.42) * (0.5 + 0.9 * math.sin(3.14 * i / (n - 1)))
        p.line([(x, y0 + 0.36), (x, y0 + 0.36 - h)],
               accent if rng.random() < 0.12 else ink, lw * 0.8)
    p.line([(-BLEED, y0 + 0.36), (1 + BLEED, y0 + 0.36)], ink, lw * 1.4)


FAMILIES = {
    "dunes": f_dunes, "mountain": f_mountain, "contour": f_contour,
    "waves": f_waves, "arch": f_arch, "rings": f_rings, "rays": f_rays,
    "botanical": f_botanical, "oneline": f_oneline, "bands": f_bands,
    "grid": f_grid, "horizonsun": f_horizonsun, "hatch": f_hatch,
}


def ink_coverage(im):
    """Share of the sheet that differs from the paper. A design that comes out
    under about 1.5% reads as a blank sheet with a scratch on it - the random
    draw can produce one, and it should not reach a listing."""
    import numpy as np
    a = np.asarray(im.convert("L"), dtype=np.int16)
    paper = int(np.bincount(a.ravel(), minlength=256).argmax())
    return float((np.abs(a - paper) > 12).mean())


MIN_INK, MAX_INK = 0.015, 0.93


def design(seed, family=None, palette=None, _depth=0):
    rng = random.Random(seed)
    fam = family or rng.choice(list(FAMILIES))
    inkc, paperc, accentc = INKS[palette if palette is not None else
                                 rng.randrange(len(INKS))]
    ink, paper, accent = _hx(inkc), _hx(paperc), _hx(accentc)
    lw = rng.choice([0.0022, 0.0030, 0.0042, 0.0058, 0.0080])
    p = Pad(paper)
    FAMILIES[fam](p, rng, ink, accent, lw)
    im = p.out()
    cov = ink_coverage(im)
    if (cov < MIN_INK or cov > MAX_INK) and _depth < 4:
        return design(seed * 2654435761 % 2**31, family, palette, _depth + 1)
    return im, fam, inkc


if __name__ == "__main__":
    outdir = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    base = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    fam = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(outdir, exist_ok=True)
    import time
    t0 = time.time()
    for i in range(n):
        im, f, ink = design(base + i, fam)
        im.save(os.path.join(outdir, f"line_{base+i:05d}_{f}.png"))
    el = time.time() - t0
    print(f"{n} designs in {el:.1f}s = {el/n:.3f}s each "
          f"({3600/(el/n):,.0f} per core-hour)")
