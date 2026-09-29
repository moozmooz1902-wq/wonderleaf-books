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

# Print box. The source designs run nearly the full chest width; the brief
# is smaller and centred, so the box is 46% of the body width and sits on
# the vertical centre of the chest rather than up under the collar.
BODY_W  = 380
PRINT_W = int(BODY_W * 0.46)        # ~175px  ~=  16cm on an adult chest
PRINT_CY = 470                      # centre of the chest, not the yoke


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
    fs = [fit(d, l.upper(), "condensed", PRINT_W, 30) for l in lines]
    h = sum(max(d.textbbox((0, 0), l.upper(), font=f)[3], f.size) * 1.06
            for l, f in zip(lines, fs))
    y = PRINT_CY - h / 2
    d.rectangle([W//2-PRINT_W//4, y-16, W//2+PRINT_W//4, y-13], fill=sig)
    for i, (ln, f) in enumerate(zip(lines, fs)):
        col = sig if i == len(lines)-1 else ink
        y = centre(d, y, ln.upper(), f, col, track=1, lead=1.06)
    d.rectangle([W//2-PRINT_W//4, y+10, W//2+PRINT_W//4, y+13], fill=sig)


def b_single_ink(d, lines, pal):
    """B - ONE BRIGHT INK. A single saturated colour, very graphic."""
    sig = pal[1]
    fs, total = [], 0
    for i, ln in enumerate(lines):
        f = fit(d, ln.upper(), "display", PRINT_W, 20 if i < len(lines)-1 else 25)
        bb = d.textbbox((0, 0), ln.upper(), font=f)
        fs.append(f); total += (bb[3] - bb[1]) * 1.34
    y = PRINT_CY - total / 2
    for f, ln in zip(fs, lines):
        y = centre(d, y, ln.upper(), f, sig, lead=1.34)


def c_badge(d, lines, pal):
    """C - BADGE / ROUNDEL. Retro athletic lockup inside a ring."""
    ink, sig = pal
    cx, cy, r = W//2, PRINT_CY, PRINT_W//2
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=ink, width=4)
    d.ellipse([cx-r+10, cy-r+10, cx+r-10, cy+r-10], outline=sig, width=2)
    n = len(lines)
    y = cy - (n * 21) / 2 - 10
    for i, ln in enumerate(lines):
        f = fit(d, ln.upper(), "slab", 2*r-34, 22 if i == len(lines)-1 else 17)
        col = sig if i == len(lines)-1 else ink
        y = centre(d, y, ln.upper(), f, col) + 4
    d.line([cx-34, cy+r-26, cx+34, cy+r-26], fill=sig, width=2)


def d_serif_block(d, lines, pal):
    """D - SERIF + COLOUR BLOCK. Display serif over a solid panel."""
    ink, sig = pal
    fs = [fit(d, l.upper(), "grotesk", PRINT_W, 19) for l in lines[:-1]]
    tf = fit(d, lines[-1].upper(), "serif", PRINT_W - 20, 30)
    h = sum(f.size * 1.5 for f in fs) + tf.size + 34
    y = PRINT_CY - h/2
    for ln, f in zip(lines[:-1], fs):
        y = centre(d, y, ln.upper(), f, ink, track=2, lead=1.5)
    y += 10
    tailw = lines[-1].upper()
    f = tf
    bb = d.textbbox((0, 0), tailw, font=f)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    d.rectangle([(W-w)/2-14, y-8, (W+w)/2+14, y+h+12], fill=sig)
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
        d.text((30, H-58), "black tee  ·  16cm print, chest centre", font=font("grotesk", 20),
               fill=(120, 120, 128))
        img.paste(panel, (i*W, 0))
        d0.line([(i*W, 0), (i*W, H)], fill=(220, 220, 226), width=2)
    img.save(path)
    return path


for i in range(3):
    print(sheet(i, f"STYLE_SHEET_{i+1}.png"))
