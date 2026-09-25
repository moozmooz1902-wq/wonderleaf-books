#!/usr/bin/env python3
"""Render a typography design at any size. Flat vector style, no AI, no network.

A design is fully described by five short fields, so it can be rebuilt from a
catalogue row or straight from an image URL:

    phrase   "But first, / *coffee*"     (" / " = line break, *x* = script accent)
    palette  "sage"                      styles.PALETTES
    fonts    "classic_serif"             styles.FONTSETS
    layout   "stack"                     styles.LAYOUTS
    orn      "cup"                       an ornament name below, or "none"

Everything is drawn from primitives at the target resolution, so a 1000px
listing image and a 300dpi A2 print come from the same code with no upscaling.

    python3 render.py "But first, / *coffee*" --palette sage --out test.png
    python3 render.py --demo out_dir/       one of every layout / palette
"""
import argparse, math, re
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from styles import PALETTES, FONTSETS, RAINBOW

FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
RATIO = math.sqrt(2)                      # A-series paper
SMALL_WORDS = {"and", "the", "of", "a", "an", "is", "to", "&", "with", "in", "for",
               "my", "your", "our", "at", "by", "on", "or", "but", "so", "be", "it",
               "are", "as", "from", "all", "we", "you", "me", "i", "this", "that"}
UPPER_FONTS = {"BebasNeue.ttf", "Anton.ttf", "Oswald.ttf", "Cinzel.ttf", "LeagueSpartan.ttf",
               "Montserrat.ttf", "AlfaSlabOne.ttf", "Rye.ttf", "Limelight.ttf", "LuckiestGuy.ttf",
               "AmaticSC.ttf", "Raleway.ttf", "JosefinSans.ttf"}


# ------------------------------------------------------------------ fonts

@lru_cache(maxsize=4096)
def font(file, variation, size):
    f = ImageFont.truetype(str(FONT_DIR / file), max(8, int(size)))
    if variation:
        try:
            f.set_variation_by_name(variation)
        except Exception:
            pass
    return f


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ------------------------------------------------------------------ phrase parsing

def parse(phrase):
    """-> (lines, attribution). Each line is (text, role) with role main|accent|small."""
    attrib = None
    if " ~ " in phrase:
        phrase, attrib = phrase.split(" ~ ", 1)
    if " / " in phrase:
        raw = [l.strip() for l in phrase.split(" / ") if l.strip()]
    else:
        raw = wrap_words(phrase)
    lines = []
    for l in raw:
        if "*" in l:
            lines.append((l.replace("*", "").strip(), "accent"))
        elif l.lower().strip(",.") in SMALL_WORDS and len(raw) >= 3:
            lines.append((l, "small"))
        else:
            lines.append((l, "main"))
    # merge runs of tiny lines so "Be / you" does not become two giant words
    return lines, attrib


def wrap_words(text):
    """Break unmarked text (scripture, long quotes) into balanced lines."""
    words = text.split()
    if len(words) <= 2:
        return [text]
    target = max(9, min(18, int(len(text) ** 0.5 * 1.9)))
    out, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > target:
            out.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        if out and len(cur) < 6:
            out[-1] += " " + cur
        else:
            out.append(cur)
    return out


# ------------------------------------------------------------------ text block

def measure(txt, f, tracking=0):
    b = f.getbbox(txt, anchor="ls")
    w = b[2] - b[0] + tracking * max(0, len(txt) - 1)
    return w, b[1], b[3]          # width, top (negative), bottom


def draw_tracked(d, x, y, txt, f, fill, tracking):
    if not tracking:
        d.text((x, y), txt, font=f, fill=fill, anchor="ls")
        return
    for ch in txt:
        d.text((x, y), ch, font=f, fill=fill, anchor="ls")
        x += f.getlength(ch) + tracking


def build_block(lines, fs, box_w, box_h, mode, upper, cap=0.30):
    """Choose a size for every line so the block fills box_w x box_h.
    mode 'even'   - main lines share one size (classic centred quote)
    mode 'fill'   - every main line stretched to the full width (subway art)"""
    main_f, main_v, acc_f, small_f, small_v = fs
    items = []
    for txt, role in lines:
        t = txt.upper() if (upper and role != "accent") else txt
        if role == "accent":
            items.append([t, acc_f, None, role, 0])
        elif role == "small":
            items.append([t.upper(), small_f, small_v, role, 0.25])
        else:
            items.append([t, main_f, main_v, role, 0])

    ref = 200
    fits = []
    for t, ff, fv, role, tr in items:
        w, _, _ = measure(t, font(ff, fv, ref), tr * ref)
        fits.append(ref * box_w / max(w, 1))
    mains = [f for f, it in zip(fits, items) if it[3] == "main"] or fits
    if mode == "fill":
        sizes = [min(f, box_w * 0.42) if it[3] != "small" else min(f, min(mains) * 0.34, box_w * 0.07)
                 for f, it in zip(fits, items)]
    else:
        base = min(min(mains), box_w * cap)
        sizes = []
        for f, it in zip(fits, items):
            if it[3] == "accent":
                sizes.append(min(f, base * 1.5))
            elif it[3] == "small":
                sizes.append(min(f, base * 0.36, box_w * 0.06))
            else:
                sizes.append(min(f, base))

    def lay(scale):
        rows, total = [], 0
        for (t, ff, fv, role, tr), s in zip(items, sizes):
            s *= scale
            f = font(ff, fv, s)
            w, top, bot = measure(t, f, tr * s)
            gap = s * (0.30 if role == "accent" else 0.22)
            rows.append((t, f, w, top, bot, gap, role, tr * s))
            total += (bot - top) + gap
        total -= rows[-1][5] if rows else 0
        return rows, total

    rows, total = lay(1.0)
    if total > box_h:
        rows, total = lay(box_h / total * 0.98)
    return rows, total


def draw_block(d, rows, total, cx, top, colours, align="center", left=0):
    ink, acc = colours["ink"], colours["acc"]
    y = top
    for i, (t, f, w, tp, bt, gap, role, tr) in enumerate(rows):
        fill = acc if role == "accent" else ink
        if colours.get("rainbow") and role == "main":
            fill = hexrgb(RAINBOW[i % len(RAINBOW)])
        x = left if align == "left" else cx - w / 2
        draw_tracked(d, x, y - tp, t, f, fill, tr)
        y += (bt - tp) + gap
    return y


# ------------------------------------------------------------------ ornaments

def _pts(fn, n=64):
    return [fn(2 * math.pi * i / n) for i in range(n)]


def vesica(cx, cy, length, width, ang):
    pts = []
    for i in range(33):
        t = i / 32
        x = (t - 0.5) * length
        y = math.sin(math.pi * t) * width / 2
        pts.append((x, y))
    pts += [(x, -y) for x, y in reversed(pts)]
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def star_pts(cx, cy, r, points=5, inner=0.45, rot=-math.pi / 2):
    out = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        a = rot + math.pi * i / points
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out


def heart_pts(cx, cy, s):
    return _pts(lambda t: (cx + s * 16 * math.sin(t) ** 3 / 17,
                           cy - s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17))


def ornament(d, name, cx, cy, s, ink, acc, bg):
    """Draw ornament `name` centred on (cx, cy) inside a box roughly s wide."""
    lw = max(2, int(s * 0.035))
    r = s / 2
    if name == "none":
        return
    if name == "heart":
        d.polygon(heart_pts(cx, cy, r * 0.8), fill=acc)
    elif name in ("star",):
        d.polygon(star_pts(cx, cy, r * 0.8), fill=acc)
    elif name == "stars":
        for dx, k in ((-0.7, 0.35), (0, 0.55), (0.7, 0.35)):
            d.polygon(star_pts(cx + dx * r, cy + (0.1 if k < 0.5 else 0) * r, r * k), fill=acc)
    elif name == "sparkle":
        d.polygon(star_pts(cx, cy, r * 0.8, 4, 0.22), fill=acc)
        d.polygon(star_pts(cx + r * 0.75, cy - r * 0.5, r * 0.28, 4, 0.25), fill=acc)
        d.polygon(star_pts(cx - r * 0.7, cy + r * 0.45, r * 0.2, 4, 0.25), fill=acc)
    elif name == "star8":
        d.polygon(star_pts(cx, cy, r * 0.8, 8, 0.72, 0), fill=acc)
        d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=bg)
    elif name in ("sun",):
        d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35], fill=acc)
        for i in range(12):
            a = math.pi * 2 * i / 12
            d.line([(cx + math.cos(a) * r * 0.5, cy + math.sin(a) * r * 0.5),
                    (cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.8)], fill=acc, width=lw)
    elif name in ("moon", "crescent"):
        d.ellipse([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], fill=acc)
        d.ellipse([cx - r * 0.35, cy - r * 0.85, cx + r * 0.95, cy + r * 0.55], fill=bg)
        if name == "crescent":
            d.polygon(star_pts(cx + r * 0.45, cy - r * 0.05, r * 0.22), fill=acc)
    elif name == "cross":
        w = r * 0.14
        d.rectangle([cx - w, cy - r * 0.85, cx + w, cy + r * 0.85], fill=acc)
        d.rectangle([cx - r * 0.5, cy - r * 0.45 - w, cx + r * 0.5, cy - r * 0.45 + w], fill=acc)
    elif name == "dove":
        d.ellipse([cx - r * 0.55, cy - r * 0.15, cx + r * 0.35, cy + r * 0.3], fill=acc)
        d.ellipse([cx + r * 0.2, cy - r * 0.3, cx + r * 0.5, cy], fill=acc)
        d.polygon([(cx + r * 0.48, cy - r * 0.18), (cx + r * 0.68, cy - r * 0.1), (cx + r * 0.46, cy - r * 0.06)], fill=acc)
        d.polygon([(cx - r * 0.2, cy), (cx - r * 0.55, cy - r * 0.75), (cx + r * 0.15, cy - r * 0.05)], fill=acc)
        d.polygon([(cx - r * 0.5, cy + r * 0.1), (cx - r * 0.95, cy - r * 0.05), (cx - r * 0.85, cy + r * 0.3)], fill=acc)
        d.line([(cx + r * 0.05, cy + r * 0.28), (cx + r * 0.25, cy + r * 0.55)], fill=acc, width=lw)
    elif name == "laurel":
        for side in (-1, 1):
            for i in range(7):
                t = i / 6
                a = math.pi * (0.55 + 0.75 * t)
                px = cx + side * math.cos(a) * r * 0.75 * -1
                py = cy + math.sin(a) * r * 0.75 * -1 + r * 0.1
                ang = a + side * 0.9 + (math.pi if side < 0 else 0)
                d.polygon(vesica(px, py, r * 0.32, r * 0.13, -ang if side > 0 else ang), fill=acc)
    elif name in ("leaf", "feather"):
        d.polygon(vesica(cx, cy, s * 0.9, s * (0.36 if name == "leaf" else 0.24), -0.7), fill=acc)
        d.line([(cx - r * 0.62, cy + r * 0.55), (cx + r * 0.3, cy - r * 0.27)], fill=bg, width=max(1, lw // 2))
        if name == "feather":
            for i in range(5):
                t = -0.4 + i * 0.16
                d.line([(cx + t * r, cy - t * r * 0.85), (cx + t * r + r * 0.18, cy - t * r * 0.85 + r * 0.05)], fill=bg, width=max(1, lw // 2))
    elif name == "flower":
        for i in range(5):
            a = 2 * math.pi * i / 5 - math.pi / 2
            px, py = cx + math.cos(a) * r * 0.42, cy + math.sin(a) * r * 0.42
            d.ellipse([px - r * 0.3, py - r * 0.3, px + r * 0.3, py + r * 0.3], fill=acc)
        d.ellipse([cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2], fill=bg)
    elif name == "lotus":
        for a in (-0.9, -0.45, 0, 0.45, 0.9):
            d.polygon(vesica(cx + math.sin(a) * r * 0.4, cy - math.cos(a) * r * 0.25, r * 1.0, r * 0.34, a - math.pi / 2), fill=acc)
        d.line([(cx - r * 0.8, cy + r * 0.5), (cx + r * 0.8, cy + r * 0.5)], fill=acc, width=lw)
    elif name in ("lines", "diamond", "dots"):
        d.line([(cx - r * 1.4, cy), (cx - r * 0.25, cy)], fill=acc, width=max(1, lw // 2))
        d.line([(cx + r * 0.25, cy), (cx + r * 1.4, cy)], fill=acc, width=max(1, lw // 2))
        if name == "dots":
            for k in (-0.12, 0, 0.12):
                d.ellipse([cx + k * s - lw, cy - lw, cx + k * s + lw, cy + lw], fill=acc)
        else:
            q = r * 0.16
            d.polygon([(cx, cy - q), (cx + q, cy), (cx, cy + q), (cx - q, cy)], fill=acc)
    elif name == "arrow":
        d.line([(cx - r * 1.2, cy), (cx + r * 1.1, cy)], fill=acc, width=lw)
        d.polygon([(cx + r * 1.25, cy), (cx + r * 0.95, cy - r * 0.18), (cx + r * 0.95, cy + r * 0.18)], fill=acc)
        for k in (0, 0.2):
            d.line([(cx - r * (1.2 - k), cy), (cx - r * (1.4 - k), cy - r * 0.2)], fill=acc, width=lw)
            d.line([(cx - r * (1.2 - k), cy), (cx - r * (1.4 - k), cy + r * 0.2)], fill=acc, width=lw)
    elif name == "cup":
        d.polygon([(cx - r * 0.5, cy - r * 0.1), (cx + r * 0.4, cy - r * 0.1),
                   (cx + r * 0.3, cy + r * 0.6), (cx - r * 0.4, cy + r * 0.6)], fill=acc)
        d.ellipse([cx + r * 0.22, cy, cx + r * 0.72, cy + r * 0.4], outline=acc, width=lw * 2)
        d.line([(cx - r * 0.65, cy + r * 0.7), (cx + r * 0.55, cy + r * 0.7)], fill=acc, width=lw)
        for k in (-0.2, 0.1):
            d.line(_wave(cx + k * r, cy - r * 0.8, cy - r * 0.2, r * 0.08), fill=acc, width=lw)
    elif name == "beans":
        for dx, a in ((-0.3, -0.5), (0.3, 0.4)):
            px = cx + dx * r
            d.polygon(vesica(px, cy, r * 0.75, r * 0.5, a + math.pi / 2), fill=acc)
            d.line(_wave(px, cy - r * 0.3, cy + r * 0.3, r * 0.05), fill=bg, width=lw)
    elif name == "glass":
        d.polygon([(cx - r * 0.55, cy - r * 0.6), (cx + r * 0.55, cy - r * 0.6), (cx, cy + r * 0.1)], fill=acc)
        d.line([(cx, cy + r * 0.1), (cx, cy + r * 0.65)], fill=acc, width=lw)
        d.line([(cx - r * 0.3, cy + r * 0.65), (cx + r * 0.3, cy + r * 0.65)], fill=acc, width=lw)
        d.ellipse([cx + r * 0.25, cy - r * 0.85, cx + r * 0.5, cy - r * 0.6], fill=acc)
    elif name == "whisk":
        for k in (0.2, 0.35, 0.5):
            d.ellipse([cx - r * k, cy - r * 0.8, cx + r * k, cy + r * 0.2], outline=acc, width=max(1, lw // 2))
        d.rectangle([cx - r * 0.07, cy + r * 0.15, cx + r * 0.07, cy + r * 0.85], fill=acc)
    elif name == "house":
        d.polygon([(cx - r * 0.75, cy - r * 0.05), (cx, cy - r * 0.75), (cx + r * 0.75, cy - r * 0.05)], outline=acc, width=lw)
        d.rectangle([cx - r * 0.55, cy - r * 0.1, cx + r * 0.55, cy + r * 0.65], outline=acc, width=lw)
        d.polygon(heart_pts(cx, cy + r * 0.25, r * 0.22), fill=acc)
    elif name == "key":
        d.ellipse([cx - r * 0.85, cy - r * 0.3, cx - r * 0.25, cy + r * 0.3], outline=acc, width=lw * 2)
        d.line([(cx - r * 0.25, cy), (cx + r * 0.85, cy)], fill=acc, width=lw * 2)
        for k in (0.55, 0.75):
            d.line([(cx + r * k, cy), (cx + r * k, cy + r * 0.25)], fill=acc, width=lw * 2)
    elif name == "rings":
        for dx in (-0.25, 0.25):
            d.ellipse([cx + dx * r - r * 0.42, cy - r * 0.42, cx + dx * r + r * 0.42, cy + r * 0.42], outline=acc, width=lw)
    elif name == "rainbow":
        for i, c in enumerate(RAINBOW[:4]):
            k = 0.9 - i * 0.17
            d.arc([cx - r * k, cy - r * k + r * 0.3, cx + r * k, cy + r * k + r * 0.3], 180, 360, fill=hexrgb(c), width=int(r * 0.15))
    elif name == "cloud":
        for dx, dy, k in ((-0.4, 0.1, 0.35), (0, -0.1, 0.45), (0.4, 0.1, 0.35)):
            d.ellipse([cx + dx * r - k * r, cy + dy * r - k * r, cx + dx * r + k * r, cy + dy * r + k * r], fill=acc)
        d.rectangle([cx - r * 0.75, cy + r * 0.1, cx + r * 0.75, cy + r * 0.45], fill=acc)
    elif name == "pencil":
        d.polygon(vesica(cx, cy, 1, 1, 0)[:0] or [(cx - r * 0.8, cy - r * 0.12), (cx + r * 0.45, cy - r * 0.12),
                                                  (cx + r * 0.85, cy), (cx + r * 0.45, cy + r * 0.12), (cx - r * 0.8, cy + r * 0.12)], fill=acc)
        d.line([(cx + r * 0.45, cy - r * 0.12), (cx + r * 0.45, cy + r * 0.12)], fill=bg, width=lw)
    elif name == "apple":
        d.ellipse([cx - r * 0.6, cy - r * 0.45, cx + r * 0.6, cy + r * 0.65], fill=acc)
        d.line([(cx, cy - r * 0.4), (cx + r * 0.1, cy - r * 0.75)], fill=acc, width=lw)
        d.polygon(vesica(cx + r * 0.3, cy - r * 0.62, r * 0.4, r * 0.18, -0.4), fill=acc)
    elif name == "bubbles":
        for dx, dy, k in ((-0.5, 0.3, 0.25), (0.1, -0.2, 0.38), (0.55, 0.4, 0.18), (-0.1, 0.6, 0.12)):
            d.ellipse([cx + dx * r - k * r, cy + dy * r - k * r, cx + dx * r + k * r, cy + dy * r + k * r], outline=acc, width=lw)
    elif name == "drop":
        d.ellipse([cx - r * 0.45, cy - r * 0.1, cx + r * 0.45, cy + r * 0.8], fill=acc)
        d.polygon([(cx, cy - r * 0.8), (cx - r * 0.42, cy + r * 0.2), (cx + r * 0.42, cy + r * 0.2)], fill=acc)
    elif name == "sock":
        d.polygon([(cx - r * 0.3, cy - r * 0.8), (cx + r * 0.15, cy - r * 0.8), (cx + r * 0.15, cy + r * 0.2),
                   (cx + r * 0.7, cy + r * 0.35), (cx + r * 0.6, cy + r * 0.75), (cx - r * 0.3, cy + r * 0.6)], fill=acc)
        d.rectangle([cx - r * 0.3, cy - r * 0.8, cx + r * 0.15, cy - r * 0.6], fill=bg)
    elif name == "bee":
        d.ellipse([cx - r * 0.2, cy - r * 0.75, cx + r * 0.45, cy - r * 0.1], outline=acc, width=lw)
        d.ellipse([cx - r * 0.55, cy - r * 0.3, cx + r * 0.55, cy + r * 0.35], fill=acc)
        for k in (-0.15, 0.15):
            d.line([(cx + k * r, cy - r * 0.28), (cx + k * r, cy + r * 0.33)], fill=bg, width=lw * 2)
    elif name == "wrench":
        d.line([(cx - r * 0.6, cy + r * 0.6), (cx + r * 0.35, cy - r * 0.35)], fill=acc, width=int(r * 0.2))
        d.ellipse([cx + r * 0.15, cy - r * 0.8, cx + r * 0.8, cy - r * 0.15], fill=acc)
        d.ellipse([cx + r * 0.4, cy - r * 0.9, cx + r * 0.75, cy - r * 0.55], fill=bg)
    elif name == "bolt":
        d.polygon([(cx + r * 0.15, cy - r * 0.85), (cx - r * 0.45, cy + r * 0.1), (cx - r * 0.02, cy + r * 0.1),
                   (cx - r * 0.2, cy + r * 0.85), (cx + r * 0.45, cy - r * 0.15), (cx + r * 0.02, cy - r * 0.15)], fill=acc)
    elif name == "paw":
        d.ellipse([cx - r * 0.4, cy - r * 0.05, cx + r * 0.4, cy + r * 0.6], fill=acc)
        for dx, dy in ((-0.55, -0.2), (-0.2, -0.55), (0.2, -0.55), (0.55, -0.2)):
            d.ellipse([cx + dx * r - r * 0.15, cy + dy * r - r * 0.19, cx + dx * r + r * 0.15, cy + dy * r + r * 0.19], fill=acc)
    elif name == "bone":
        d.rectangle([cx - r * 0.6, cy - r * 0.12, cx + r * 0.6, cy + r * 0.12], fill=acc)
        for dx in (-0.65, 0.65):
            for dy in (-0.15, 0.15):
                d.ellipse([cx + dx * r - r * 0.18, cy + dy * r - r * 0.18, cx + dx * r + r * 0.18, cy + dy * r + r * 0.18], fill=acc)
    elif name == "robin":
        d.ellipse([cx - r * 0.55, cy - r * 0.35, cx + r * 0.35, cy + r * 0.45], fill=ink)
        d.ellipse([cx - r * 0.05, cy - r * 0.15, cx + r * 0.33, cy + r * 0.3], fill=hexrgb("#C8553D"))
        d.ellipse([cx + r * 0.05, cy - r * 0.6, cx + r * 0.45, cy - r * 0.2], fill=ink)
        d.polygon([(cx + r * 0.43, cy - r * 0.45), (cx + r * 0.62, cy - r * 0.4), (cx + r * 0.43, cy - r * 0.33)], fill=ink)
        d.polygon([(cx - r * 0.5, cy), (cx - r * 0.9, cy - r * 0.25), (cx - r * 0.8, cy + r * 0.1)], fill=ink)
        d.line([(cx - r * 0.1, cy + r * 0.45), (cx - r * 0.1, cy + r * 0.7)], fill=ink, width=lw)
    elif name == "pin":
        d.ellipse([cx - r * 0.45, cy - r * 0.8, cx + r * 0.45, cy + r * 0.1], fill=acc)
        d.polygon([(cx - r * 0.4, cy - r * 0.2), (cx + r * 0.4, cy - r * 0.2), (cx, cy + r * 0.8)], fill=acc)
        d.ellipse([cx - r * 0.17, cy - r * 0.52, cx + r * 0.17, cy - r * 0.18], fill=bg)
    elif name == "tree":
        for i, k in enumerate((0.35, 0.55, 0.75)):
            y0 = cy - r * 0.85 + i * r * 0.4
            d.polygon([(cx, y0), (cx - r * k, y0 + r * 0.55), (cx + r * k, y0 + r * 0.55)], fill=acc)
        d.rectangle([cx - r * 0.1, cy + r * 0.45, cx + r * 0.1, cy + r * 0.75], fill=acc)
    elif name == "snow":
        for i in range(3):
            a = math.pi * i / 3
            d.line([(cx - math.cos(a) * r * 0.8, cy - math.sin(a) * r * 0.8),
                    (cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.8)], fill=acc, width=lw)
        for i in range(6):
            a = math.pi * i / 3
            px, py = cx + math.cos(a) * r * 0.5, cy + math.sin(a) * r * 0.5
            for da in (0.6, -0.6):
                d.line([(px, py), (px + math.cos(a + da) * r * 0.2, py + math.sin(a + da) * r * 0.2)], fill=acc, width=lw)
    elif name == "holly":
        d.polygon(vesica(cx - r * 0.35, cy, r * 0.8, r * 0.35, 0.4), fill=acc)
        d.polygon(vesica(cx + r * 0.35, cy, r * 0.8, r * 0.35, -0.4), fill=acc)
        for dx, dy in ((-0.1, -0.3), (0.12, -0.32), (0, -0.12)):
            d.ellipse([cx + dx * r - r * 0.12, cy + dy * r - r * 0.12, cx + dx * r + r * 0.12, cy + dy * r + r * 0.12], fill=hexrgb("#B3261E"))
    elif name == "waves":
        for k in (-0.3, 0, 0.3):
            d.line(_hwave(cx - r * 1.1, cx + r * 1.1, cy + k * r, r * 0.1), fill=acc, width=lw)
    elif name == "anchor":
        d.line([(cx, cy - r * 0.6), (cx, cy + r * 0.75)], fill=acc, width=lw * 2)
        d.ellipse([cx - r * 0.16, cy - r * 0.9, cx + r * 0.16, cy - r * 0.58], outline=acc, width=lw * 2)
        d.line([(cx - r * 0.35, cy - r * 0.35), (cx + r * 0.35, cy - r * 0.35)], fill=acc, width=lw * 2)
        d.arc([cx - r * 0.65, cy - r * 0.1, cx + r * 0.65, cy + r * 0.8], 20, 160, fill=acc, width=lw * 2)
    elif name == "palm":
        d.line([(cx, cy + r * 0.85), (cx + r * 0.1, cy - r * 0.35)], fill=acc, width=lw * 2)
        for a in (-2.6, -2.0, -1.2, -0.5, 0.1):
            d.polygon(vesica(cx + r * 0.1 + math.cos(a) * r * 0.42, cy - r * 0.35 + math.sin(a) * r * 0.3, r * 0.85, r * 0.2, a), fill=acc)
    elif name == "lantern":
        d.polygon([(cx - r * 0.35, cy - r * 0.45), (cx + r * 0.35, cy - r * 0.45), (cx + r * 0.45, cy + r * 0.45),
                   (cx - r * 0.45, cy + r * 0.45)], outline=acc, width=lw)
        d.polygon([(cx - r * 0.35, cy - r * 0.45), (cx, cy - r * 0.8), (cx + r * 0.35, cy - r * 0.45)], fill=acc)
        d.rectangle([cx - r * 0.5, cy + r * 0.45, cx + r * 0.5, cy + r * 0.58], fill=acc)
        d.polygon(star_pts(cx, cy, r * 0.2), fill=acc)
    elif name == "knot":
        for i in range(3):
            a = -math.pi / 2 + 2 * math.pi * i / 3
            px, py = cx + math.cos(a) * r * 0.28, cy + math.sin(a) * r * 0.28
            d.ellipse([px - r * 0.45, py - r * 0.45, px + r * 0.45, py + r * 0.45], outline=acc, width=lw)
    elif name == "bolt":
        pass
    else:
        d.polygon(star_pts(cx, cy, r * 0.6, 4, 0.25), fill=acc)


def _wave(x, y0, y1, amp):
    n = 20
    return [(x + amp * math.sin(i / n * math.pi * 2), y0 + (y1 - y0) * i / n) for i in range(n + 1)]


def _hwave(x0, x1, y, amp):
    n = 40
    return [(x0 + (x1 - x0) * i / n, y + amp * math.sin(i / n * math.pi * 4)) for i in range(n + 1)]


# ------------------------------------------------------------------ layouts

def render(phrase, palette="bw", fonts="classic_serif", layout="stack", orn="none", width=1000):
    W, H = int(width), int(width * RATIO)
    name, bg, ink, acc = PALETTES[palette]
    bg, ink, acc = hexrgb(bg), hexrgb(ink), hexrgb(acc)
    colours = {"ink": ink, "acc": acc, "rainbow": palette == "rainbow"}
    fs = FONTSETS[fonts]
    upper = fs[0] in UPPER_FONTS
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    lines, attrib = parse(phrase)
    m = W * 0.11
    has_orn = orn != "none"
    osz = W * 0.16

    if layout == "badge" and len(lines) > 4:
        layout = "frame"
    if layout == "subway" and len(lines) < 3:
        layout = "stack"

    def attrib_h():
        return W * 0.07 if attrib else 0

    def draw_attrib(y):
        if attrib:
            f = font(fs[3], fs[4], W * 0.028)
            t = attrib.upper()
            w, top, _ = measure(t, f, W * 0.006)
            draw_tracked(d, W / 2 - w / 2, y - top, t, f, acc, W * 0.006)

    if layout in ("stack", "frame", "rules", "arch", "ribbon"):
        if layout == "frame":
            k = W * 0.05
            d.rectangle([k, k, W - k, H - k], outline=ink, width=max(2, int(W * 0.006)))
            k2 = k + W * 0.018
            d.rectangle([k2, k2, W - k2, H - k2], outline=ink, width=max(1, int(W * 0.002)))
        if layout == "arch":
            tint = mix(bg, acc, 0.22)
            ax0, ax1, ay0, ay1 = W * 0.12, W * 0.88, H * 0.12, H * 0.9
            rad = (ax1 - ax0) / 2
            d.rectangle([ax0, ay0 + rad, ax1, ay1], fill=tint)
            d.ellipse([ax0, ay0, ax1, ay0 + 2 * rad], fill=tint)
            m = W * 0.17
        box_w = W - 2 * m
        box_h = H - 2 * m * 1.3 - (osz * 1.3 if has_orn else 0) - attrib_h()
        rows, total = build_block(lines, fs, box_w, box_h, "even", upper)
        gap_rule = W * 0.035 if layout == "rules" else 0
        total_all = total + (osz * 1.25 if has_orn else 0) + attrib_h() + gap_rule * (len(rows) - 1)
        y = (H - total_all) / 2 + (H * 0.04 if layout == "arch" else 0)
        if has_orn:
            ornament(d, orn, W / 2, y + osz / 2, osz, ink, acc, mix(bg, acc, 0.22) if layout == "arch" else bg)
            y += osz * 1.25
        if layout == "rules":
            for i, row in enumerate(rows):
                y = draw_block(d, [row], 0, W / 2, y, colours)
                if i < len(rows) - 1:
                    y += gap_rule / 2 - row[5]
                    d.line([(W * 0.35, y), (W * 0.65, y)], fill=acc, width=max(1, int(W * 0.003)))
                    y += gap_rule / 2 + row[5]
        elif layout == "ribbon":
            big = max(range(len(rows)), key=lambda i: rows[i][4] - rows[i][3])
            for i, row in enumerate(rows):
                if i == big:
                    t, f, w, tp, bt, gap, role, tr = row
                    pad = (bt - tp) * 0.28
                    d.rectangle([W * 0.06, y - pad, W * 0.94, y + (bt - tp) + pad], fill=ink)
                    draw_block(d, [row], 0, W / 2, y, {"ink": bg, "acc": bg})
                    y += (bt - tp) + gap + pad
                else:
                    y = draw_block(d, [row], 0, W / 2, y, colours)
        else:
            y = draw_block(d, rows, total, W / 2, y, colours)
        draw_attrib(y + W * 0.04)

    elif layout == "subway":
        box_w = W - 2 * m
        box_h = H - 2 * m * 1.15 - attrib_h()
        rows, total = build_block(lines, fs, box_w, box_h, "fill", True)
        y = (H - total - attrib_h()) / 2
        y = draw_block(d, rows, total, W / 2, y, colours)
        draw_attrib(y + W * 0.04)

    elif layout in ("left", "corner"):
        box_w = W - 2 * m
        box_h = H * 0.62 - attrib_h()
        rows, total = build_block(lines, fs, box_w, box_h, "even", upper)
        if layout == "left":
            y = H * 0.5 - total / 2
            d.rectangle([m, y - W * 0.08, m + W * 0.12, y - W * 0.065], fill=acc)
            y = draw_block(d, rows, total, 0, y, colours, align="left", left=m)
            if has_orn:
                ornament(d, orn, m + osz * 0.5, H - m - osz * 0.5, osz * 0.8, ink, acc, bg)
        else:
            y = H - m - total - attrib_h()
            if has_orn:
                ornament(d, orn, W - m - osz * 0.8, m + osz * 0.8, osz * 1.5, ink, acc, bg)
            y = draw_block(d, rows, total, 0, y, colours, align="left", left=m)
        if attrib:
            f = font(fs[3], fs[4], W * 0.028)
            draw_tracked(d, m, y + W * 0.05, attrib.upper(), f, acc, W * 0.006)

    elif layout == "badge":
        r = W * 0.36
        cy = H * 0.5
        d.ellipse([W / 2 - r, cy - r, W / 2 + r, cy + r], outline=ink, width=max(2, int(W * 0.007)))
        r2 = r - W * 0.025
        d.ellipse([W / 2 - r2, cy - r2, W / 2 + r2, cy + r2], outline=acc, width=max(1, int(W * 0.002)))
        box = r * 1.25
        rows, total = build_block(lines, fs, box, box * 0.75, "even", upper, cap=0.45)
        y = draw_block(d, rows, total, W / 2, cy - total / 2, colours)
        if has_orn:
            ornament(d, orn, W / 2, cy - r - osz * 0.75, osz * 0.8, ink, acc, bg)
        if attrib:
            draw_attrib(cy + r + W * 0.05)

    elif layout == "block":
        split = H * 0.58
        d.rectangle([0, 0, W, split], fill=ink)
        box_w = W - 2 * m
        rows, total = build_block(lines, fs, box_w, split - 2 * m, "even", upper)
        draw_block(d, rows, total, W / 2, (split - total) / 2, {"ink": bg, "acc": acc if acc != ink else bg})
        if has_orn:
            ornament(d, orn, W / 2, split + (H - split) * 0.42, osz, ink, acc, bg)
        if attrib:
            draw_attrib(split + (H - split) * 0.75)
    return img


def mockup(art, width=1000, wall="#EDE9E3"):
    """Listing photo: the print on a wall with a soft shadow. No frame is shown,
    because the product is an unframed print."""
    W, H = width, int(width * 1.0)
    canvas = Image.new("RGB", (W, H), hexrgb(wall))
    ph = int(H * 0.84)
    pw = int(ph / RATIO)
    art = art.resize((pw, ph), Image.LANCZOS)
    x, y = (W - pw) // 2, (H - ph) // 2
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rectangle([x + 6, y + 10, x + pw + 6, y + ph + 12], fill=90)
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(Image.new("RGB", (W, H), (60, 55, 50)), (0, 0), shadow)
    canvas.paste(art, (x, y))
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phrase", nargs="?")
    ap.add_argument("--palette", default="bw")
    ap.add_argument("--fonts", default="classic_serif")
    ap.add_argument("--layout", default="stack")
    ap.add_argument("--orn", default="none")
    ap.add_argument("--width", type=int, default=1000)
    ap.add_argument("--out", default="out.png")
    a = ap.parse_args()
    img = render(a.phrase, a.palette, a.fonts, a.layout, a.orn, a.width)
    img.save(a.out)
    print(a.out, img.size)


if __name__ == "__main__":
    main()
