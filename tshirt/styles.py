#!/usr/bin/env python3
"""Four house looks, rendered on a black tee so they can be compared by eye.

The brief was: same slogans, but our own look - different colour, different
type. Each direction below changes the palette AND the typographic system,
not just the font, so they read as different studios rather than the same
design tinted.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random

F = "/mnt/skills/examples/canvas-design/canvas-fonts"
FONTS = {
  "condensed": f"{F}/BigShoulders-Bold.ttf",
  "grotesk":   f"{F}/InstrumentSans-Bold.ttf",
  "display":   f"{F}/Boldonse-Regular.ttf",
  "serif":     f"{F}/YoungSerif-Regular.ttf",
  "mono":      f"{F}/GeistMono-Bold.ttf",
  "slab":      f"{F}/NationalPark-Bold.ttf",
}
TEE = (22, 22, 24)          # black garment
W, H = 760, 900             # one panel


def font(k, s): return ImageFont.truetype(FONTS[k], s)


def tee(draw):
    """Flat black tee silhouette - enough to judge scale and placement."""
    cx, top = W // 2, 130
    body = [(cx-190, top+60), (cx-190, top+600), (cx+190, top+600), (cx+190, top+60)]
    draw.polygon(body, fill=TEE)
    draw.polygon([(cx-190,top+60),(cx-300,top+150),(cx-250,top+240),(cx-190,top+190)], fill=TEE)
    draw.polygon([(cx+190,top+60),(cx+300,top+150),(cx+250,top+240),(cx+190,top+190)], fill=TEE)
    draw.ellipse([cx-190,top+20,cx+190,top+100], fill=TEE)
    draw.ellipse([cx-58,top+34,cx+58,top+86], fill=(12,12,14))     # collar
    draw.arc([cx-58,top+34,cx+58,top+86], 0, 180, fill=(60,60,64), width=3)


def fit(draw, text, key, box_w, size):
    """Shrink until the line fits the print width."""
    f = font(key, size)
    while draw.textlength(text, font=f) > box_w and size > 10:
        size -= 2; f = font(key, size)
    return f


def centre(draw, y, text, f, fill, track=0, lead=1.08):
    w = draw.textlength(text, font=f) + track * max(0, len(text) - 1)
    x = (W - w) / 2
    if track:
        for ch in text:
            draw.text((x, y), ch, font=f, fill=fill)
            x += draw.textlength(ch, font=f) + track
    else:
        draw.text((x, y), text, font=f, fill=fill)
    # some display faces draw far taller than their nominal size, so advance
    # by what was actually drawn rather than by f.size
    bb = draw.textbbox((0, 0), text or "H", font=f)
    return y + max(bb[3] - bb[1], f.size) * lead


# --------------------------------------------------------------- directions
def a_two_tone(d, lines, pal):
    """A - TWO-TONE BOLD. Off-white condensed, one signal colour, a rule."""
    ink, sig = pal
    y = 300
    d.rectangle([W//2-110, y-26, W//2+110, y-18], fill=sig)
    for i, ln in enumerate(lines):
        f = fit(d, ln.upper(), "condensed", 340, 76 if i else 54)
        col = sig if i == len(lines)-1 and len(lines) > 2 else ink
        y = centre(d, y, ln.upper(), f, col, track=1)
    d.rectangle([W//2-110, y+14, W//2+110, y+22], fill=sig)


def b_single_ink(d, lines, pal):
    """B - ONE BRIGHT INK. A single saturated colour, very graphic."""
    sig = pal[1]
    sizes = [34, 34, 34, 34]
    sizes[-1] = 46                      # the payload line is the loud one
    total = 0
    fs = []
    for i, ln in enumerate(lines):
        f = fit(d, ln.upper(), "display", 310, sizes[min(i, 3)])
        bb = d.textbbox((0, 0), ln.upper(), font=f)
        fs.append((f, bb[3] - bb[1])); total += (bb[3] - bb[1]) * 1.34
    y = 470 - total / 2
    for (f, _), ln in zip(fs, lines):
        y = centre(d, y, ln.upper(), f, sig, lead=1.34)


def c_badge(d, lines, pal):
    """C - BADGE / ROUNDEL. Retro athletic lockup inside a ring."""
    ink, sig = pal
    cx, cy, r = W//2, 470, 172
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=ink, width=6)
    d.ellipse([cx-r+16, cy-r+16, cx+r-16, cy+r-16], outline=sig, width=3)
    n = len(lines)
    y = cy - (n * 36) / 2 - 18
    for i, ln in enumerate(lines):
        f = fit(d, ln.upper(), "slab", 2*r-84, 40 if i == len(lines)-1 else 30)
        col = sig if i == len(lines)-1 else ink
        y = centre(d, y, ln.upper(), f, col) + 4
    d.line([cx-70, cy+r-48, cx+70, cy+r-48], fill=sig, width=3)


def d_serif_block(d, lines, pal):
    """D - SERIF + COLOUR BLOCK. Display serif over a solid panel."""
    ink, sig = pal
    y = 300
    for ln in lines[:-1]:
        f = fit(d, ln.upper(), "grotesk", 300, 34)
        y = centre(d, y, ln.upper(), f, ink, track=3) + 6
    y += 18
    tailw = lines[-1].upper()
    f = fit(d, tailw, "serif", 310, 62)
    bb = d.textbbox((0, 0), tailw, font=f)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    d.rectangle([(W-w)/2-24, y-14, (W+w)/2+24, y+h+20], fill=sig)
    centre(d, y - bb[1] + 2, tailw, f, TEE)


DIRECTIONS = [
  ("A  TWO-TONE BOLD",      a_two_tone,   ((242,240,234), (214,69,47))),
  ("B  ONE BRIGHT INK",     b_single_ink, ((242,240,234), (247,181,56))),
  ("C  BADGE / ROUNDEL",    c_badge,      ((240,236,226), (96,170,158))),
  ("D  SERIF + COLOUR BLOCK",d_serif_block,((240,238,232), (224,110,64))),
]

SAMPLES = [
  ["Never", "Underestimate", "An Old Man", "With A Motorbike"],
  ["This Is What", "An Awesome", "Welder", "Looks Like"],
  ["Weekend Forecast", "Fishing", "With A Chance", "Of Drinking"],
]


def sheet(sample_idx, path):
    lines = SAMPLES[sample_idx]
    cols = len(DIRECTIONS)
    img = Image.new("RGB", (W*cols, H), (248, 248, 250))
    d0 = ImageDraw.Draw(img)
    for i, (name, fn, pal) in enumerate(DIRECTIONS):
        panel = Image.new("RGB", (W, H), (248, 248, 250))
        d = ImageDraw.Draw(panel)
        tee(d)
        fn(d, lines, pal)
        lab = font("grotesk", 28)
        d.text((30, 36), name, font=lab, fill=(28, 28, 32))
        d.text((30, H-58), "black tee  ·  22cm print", font=font("grotesk", 20),
               fill=(120, 120, 128))
        img.paste(panel, (i*W, 0))
        d0.line([(i*W, 0), (i*W, H)], fill=(220, 220, 226), width=2)
    img.save(path)
    return path


for i in range(3):
    print(sheet(i, f"STYLE_SHEET_{i+1}.png"))
