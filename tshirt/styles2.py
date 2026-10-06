#!/usr/bin/env python3
"""Richer designs, built against what actually sells in the seller's data.

Their best dark-garment sellers (7,863u down to 718u) share things the flat
two-colour layouts did not have:

  * distressed ink - the print looks worn, not vinyl-sharp
  * retro arc stripes behind the type (Monkey Magic, 1,342u)
  * badge and emblem lockups with a real frame (S.H.A.D.O, USCSS Nostromo)
  * three or four inks, not one accent
  * type HIERARCHY - a display line, a condensed line, small caps detail

So: eight layouts, twelve palettes of 3-4 inks, a distress pass, and an
ornament library. Measured context: distressed is the biggest style in
their catalogue at 10.91 units/design, typography_only leads at 13.38.
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import os

F = os.environ.get("FONT_DIR") or next(
    (p for p in ("fonts", "/mnt/skills/examples/canvas-design/canvas-fonts")
     if os.path.isdir(p)), "fonts")
FONTS = {
    "display":  f"{F}/Boldonse-Regular.ttf",
    "condensed":f"{F}/BigShoulders-Bold.ttf",
    "grotesk":  f"{F}/InstrumentSans-Bold.ttf",
    "serif":    f"{F}/YoungSerif-Regular.ttf",
    "slab":     f"{F}/NationalPark-Bold.ttf",
    "mono":     f"{F}/GeistMono-Bold.ttf",
}
W, H = 1100, 1100          # artwork canvas, cropped before placing


def font(k, s):
    return ImageFont.truetype(FONTS[k], max(8, int(s)))


# ---------------------------------------------------------------- palettes
# Each is (name, ink, accent, extra, deep). Built for black garments: a light
# primary, a saturated accent, a secondary and a muted shadow tone.
PALETTES = [
 ("sunset",    (247,240,228), (232, 93, 42), (243,176, 68), (118, 52, 48)),
 ("coral",     (245,238,230), (231, 86, 94), (247,183,106), (104, 48, 62)),
 ("surf",      (238,245,244), ( 72,176,168), (240,206, 96), ( 36, 86, 92)),
 ("rust",      (244,235,221), (191, 86, 44), (214,151, 72), ( 94, 50, 36)),
 ("neon",      (240,240,245), (232, 62,140), ( 86,204,214), ( 58, 42,104)),
 ("forest",    (238,243,233), (118,176, 88), (226,190, 86), ( 46, 78, 54)),
 ("ice",       (236,242,248), ( 92,164,222), (198,224,240), ( 38, 70,110)),
 ("ember",     (246,238,226), (226,122, 42), (242,196, 92), (106, 54, 34)),
 ("violet",    (242,238,248), (158,124,212), (238,176,214), ( 62, 46,102)),
 ("gold",      (245,239,224), (214,168, 68), (236,214,158), ( 96, 72, 34)),
 ("mono-bone", (244,242,236), (244,242,236), (186,184,176), (120,118,112)),
 ("red-white", (246,244,240), (206, 58, 48), (236,170,160), ( 96, 30, 28)),
]


def pal(i):
    return PALETTES[i % len(PALETTES)]


# ---------------------------------------------------------------- texture
def distress(img, seed, strength=0.10):
    """A light worn-print texture.

    The first attempt removed about half the ink and turned every design into
    noise. This keeps ~92% of it: coarse speckle plus a few hairline scratches,
    enough to stop the print looking like vinyl, not enough to read as damage.
    """
    rnd = random.Random(seed)
    w, h = img.size
    n = Image.effect_noise((max(8, w // 6), max(8, h // 6)), 60).resize((w, h), Image.BILINEAR)
    n = n.filter(ImageFilter.GaussianBlur(1.6))
    cut = int(40 + strength * 120)          # ~52 -> keeps the great majority
    mask = n.point(lambda v: 255 if v > cut else 70)
    sc = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(sc)
    for _ in range(rnd.randint(2, 5)):
        y = rnd.randint(0, h)
        d.line([(0, y + rnd.randint(-3, 3)), (w, y + rnd.randint(-3, 3))],
               fill=120, width=1)
    mask = ImageChops.darker(mask, sc)
    img.putalpha(ImageChops.darker(img.getchannel("A"), mask))
    return img


# ---------------------------------------------------------------- ornament
def sunburst(d, cx, cy, r, cols, n=7):
    """The retro arc stripes behind the type - straight off their 1,342u design."""
    step = r / (n + 1.4)
    for i in range(n):
        rr = r - i * step
        d.ellipse([cx - rr, cy - rr * 0.62, cx + rr, cy + rr * 0.62],
                  fill=cols[i % len(cols)])


def rays(d, cx, cy, r, col, n=18):
    for i in range(n):
        a0 = (360 / n) * i
        d.pieslice([cx - r, cy - r, cx + r, cy + r], a0, a0 + 360 / (n * 2), fill=col)


def stars(d, x, y, w, col, n=3, s=9):
    gap = w / (n + 1)
    for i in range(n):
        cx = x + gap * (i + 1)
        pts = []
        for k in range(10):
            rr = s if k % 2 == 0 else s * .42
            a = math.radians(-90 + k * 36)
            pts.append((cx + rr * math.cos(a), y + rr * math.sin(a)))
        d.polygon(pts, fill=col)


def fit(d, text, key, box, size):
    f = font(key, size)
    while d.textlength(text, font=f) > box and size > 9:
        size -= 1; f = font(key, size)
    return f


def centre(d, y, text, f, fill, cx=W // 2, track=0):
    wdt = d.textlength(text, font=f) + track * max(0, len(text) - 1)
    x = cx - wdt / 2
    if track:
        for ch in text:
            d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    else:
        d.text((x, y), text, font=f, fill=fill)
    bb = d.textbbox((0, 0), text or "H", font=f)
    return y + max(bb[3] - bb[1], f.size)


# ---------------------------------------------------------------- layouts
# Each takes (draw, lines, palette, seed) and composes on a transparent canvas.

def L_sunburst(d, L, P, seed):
    """Retro arc stripes BEHIND big type. Their 1,342u shape.

    First attempt drew the stripes at the same scale as the text and buried
    it. The burst is now a band behind the words, and the type is the
    biggest thing on the shirt.
    """
    ink, acc, ex, deep = P
    cx, cy = W // 2, int(H * .46)
    sunburst(d, cx, cy, int(W * .46), [deep, acc, ex, deep, acc, ex, deep], n=6)
    fs, hs = [], []
    for i, ln in enumerate(L):
        big = i == len(L) - 1
        f = fit(d, ln.upper(), "display" if big else "condensed",
                int(W * .80), 104 if big else 62)
        bb = d.textbbox((0, 0), ln.upper(), font=f)
        fs.append(f); hs.append(bb[3] - bb[1])
    y = cy - sum(h + 12 for h in hs) / 2
    for i, (ln, f, h) in enumerate(zip(L, fs, hs)):
        big = i == len(L) - 1
        centre(d, y, ln.upper(), f, ink if not big else (18, 18, 20))
        y += h + 12


def L_badge(d, L, P, seed):
    """Emblem in a double ring with a banner - the S.H.A.D.O / Nostromo shape."""
    ink, acc, ex, deep = P
    cx, cy, r = W // 2, int(H * .45), int(W * .33)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=9)
    d.ellipse([cx - r + 20, cy - r + 20, cx + r - 20, cy + r - 20], outline=acc, width=4)
    stars(d, cx - 70, cy - r + 54, 140, ex, 3, 10)
    y = cy - len(L) * 26
    for i, ln in enumerate(L):
        big = i == len(L) - 1
        f = fit(d, ln.upper(), "slab" if big else "grotesk", 2 * r - 70, 70 if big else 38)
        y = centre(d, y, ln.upper(), f, acc if big else ink) + 6
    d.rectangle([cx - 96, cy + r - 72, cx + 96, cy + r - 64], fill=acc)


def L_stack(d, L, P, seed):
    """Heavy stacked type, one line boxed. Hierarchy by size, not decoration."""
    ink, acc, ex, deep = P
    y = int(H * .26)
    hero = max(range(len(L)), key=lambda i: len(L[i]))
    for i, ln in enumerate(L):
        if i == hero:
            f = fit(d, ln.upper(), "display", int(W * .80), 112)
            wdt = d.textlength(ln.upper(), font=f)
            bb = d.textbbox((0, 0), ln.upper(), font=f)
            d.rectangle([W//2 - wdt/2 - 22, y - 12, W//2 + wdt/2 + 22, y + (bb[3]-bb[1]) + 20], fill=acc)
            centre(d, y - bb[1] + 2, ln.upper(), f, (18, 18, 20))
            y += (bb[3] - bb[1]) + 40
        else:
            f = fit(d, ln.upper(), "condensed", int(W * .74), 66)
            y = centre(d, y, ln.upper(), f, ink, track=2) + 12


def L_banner(d, L, P, seed):
    """Rules above and below, small-caps kicker, display payload."""
    ink, acc, ex, deep = P
    y = int(H * .28)
    d.rectangle([W//2 - 190, y - 30, W//2 + 190, y - 22], fill=acc)
    for i, ln in enumerate(L[:-1]):
        f = fit(d, ln.upper(), "grotesk", int(W * .66), 52)
        y = centre(d, y, ln.upper(), f, ink, track=4) + 10
    y += 14
    f = fit(d, L[-1].upper(), "display", int(W * .82), 118)
    y = centre(d, y, L[-1].upper(), f, acc) + 14
    d.rectangle([W//2 - 190, y + 10, W//2 + 190, y + 18], fill=ex)
    stars(d, W//2 - 60, y + 54, 120, ink, 3, 8)


def L_arch(d, L, P, seed):
    """Text on an arc over a solid slab - the vintage motorcycle poster shape."""
    ink, acc, ex, deep = P
    cx, cy = W // 2, int(H * .50)
    top = L[0].upper()
    f = font("slab", 56)
    n = len(top)
    span = 130
    for k, ch in enumerate(top):
        a = math.radians(-90 - span/2 + (span/max(1, n-1)) * k)
        r = int(W * .30)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        img = Image.new("RGBA", (90, 90), (0,0,0,0))
        ImageDraw.Draw(img).text((45, 45), ch, font=f, fill=ink, anchor="mm")
        img = img.rotate(-math.degrees(a) - 90, resample=Image.BICUBIC)
        d._image.alpha_composite(img, (int(x) - 45, int(y) - 45))
    y = cy - 40
    for i, ln in enumerate(L[1:]):
        big = i == len(L) - 2
        f = fit(d, ln.upper(), "display" if big else "condensed", int(W*.60), 84 if big else 48)
        y = centre(d, y, ln.upper(), f, acc if big else ink) + 8
    d.rectangle([cx - 150, y + 16, cx + 150, y + 24], fill=ex)


def L_split(d, L, P, seed):
    """Two colour blocks stacked, type reversed out - bold and very legible."""
    ink, acc, ex, deep = P
    y = int(H * .28)
    for i, ln in enumerate(L):
        f = fit(d, ln.upper(), "condensed", int(W * .78), 84)
        bb = d.textbbox((0, 0), ln.upper(), font=f)
        h = bb[3] - bb[1]
        wdt = d.textlength(ln.upper(), font=f)
        if i % 2 == 0:
            d.rectangle([W//2 - wdt/2 - 18, y - 10, W//2 + wdt/2 + 18, y + h + 16], fill=ink)
            centre(d, y - bb[1] + 3, ln.upper(), f, (18, 18, 20))
        else:
            centre(d, y - bb[1] + 3, ln.upper(), f, acc)
        y += h + 26


def L_stamp(d, L, P, seed):
    """Boxed frame with corner marks and a mono kicker - utility/military feel."""
    ink, acc, ex, deep = P
    x0, y0, x1, y1 = int(W*.17), int(H*.26), int(W*.83), int(H*.68)
    d.rectangle([x0, y0, x1, y1], outline=ink, width=7)
    for cx_, cy_ in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        d.rectangle([cx_-12, cy_-12, cx_+12, cy_+12], fill=acc)
    y = y0 + 44
    f = font("mono", 30)
    y = centre(d, y, "EST. ORIGINAL", f, ex, track=6) + 18
    for i, ln in enumerate(L):
        big = i == len(L) - 1
        f = fit(d, ln.upper(), "display" if big else "condensed", x1 - x0 - 60, 84 if big else 50)
        y = centre(d, y, ln.upper(), f, acc if big else ink) + 8


def L_rays(d, L, P, seed):
    """Radiating burst behind large reversed type."""
    ink, acc, ex, deep = P
    cx, cy = W // 2, int(H * .46)
    rays(d, cx, cy, int(W * .48), deep, 24)
    d.ellipse([cx-int(W*.36), cy-int(W*.26), cx+int(W*.36), cy+int(W*.26)], fill=acc)
    fs, hs = [], []
    for i, ln in enumerate(L):
        big = i == len(L) - 1
        f = fit(d, ln.upper(), "display" if big else "grotesk", int(W*.62), 88 if big else 46)
        bb = d.textbbox((0, 0), ln.upper(), font=f)
        fs.append(f); hs.append(bb[3] - bb[1])
    y = cy - sum(h + 10 for h in hs) / 2
    for ln, f, h in zip(L, fs, hs):
        centre(d, y, ln.upper(), f, (18, 18, 20)); y += h + 10


LAYOUTS = [("sunburst", L_sunburst), ("badge", L_badge), ("stack", L_stack),
           ("banner", L_banner), ("arch", L_arch), ("split", L_split),
           ("stamp", L_stamp), ("rays", L_rays)]


def render(lines, layout_i, pal_i, seed=0, worn=True):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d._image = img
    LAYOUTS[layout_i % len(LAYOUTS)][1](d, lines, pal(pal_i)[1:], seed)
    if worn:
        img = distress(img, seed)
    bb = img.getbbox()
    return img.crop(bb) if bb else img
