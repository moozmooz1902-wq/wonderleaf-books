"""Render type-led designs to print-ready PNG, plus a scaled black-tee mockup.

House spec, measured from 140,085 of the seller's own designs:
  garment BLACK, 4-5 spot colours, artwork covering 10-25% of the chest.
Our own style: one condensed grotesk throughout, separated by weight and size
only - deliberately not the sans/serif alternation the source catalogue uses.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

F = "/mnt/skills/examples/canvas-design/canvas-fonts"
DISPLAY = f"{F}/BigShoulders-Bold.ttf"      # heavy condensed - our house face
SECOND  = f"{F}/WorkSans-Bold.ttf"
OUT = Path("designs"); OUT.mkdir(exist_ok=True)

# 4-colour house palette (the measured sweet spot is 4-5 inks)
INK   = (245, 243, 238)     # off-white, the primary ink
ACCENT= (214, 69, 47)       # signal red
WARM  = (232, 173, 63)      # amber
COOL  = (108, 154, 158)     # slate teal
CANVAS = 2400               # width
CANVAS_H = 3400             # height - must exceed the tallest stack or text is lost


def font(path, size): return ImageFont.truetype(path, size)


def centre(d, y, text, f, fill, track=0):
    """Draw text centred on CANVAS, with optional letter-spacing."""
    if track == 0:
        w = d.textlength(text, font=f)
        d.text(((CANVAS - w) / 2, y), text, font=f, fill=fill)
        return w
    w = sum(d.textlength(c, font=f) + track for c in text) - track
    x = (CANVAS - w) / 2
    for c in text:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + track
    return w


def fit(d, text, path, target_w, start=400):
    """Largest size at which text fits target_w."""
    s = start
    while s > 20:
        f = font(path, s)
        if d.textlength(text, font=f) <= target_w: return f
        s -= 4
    return font(path, 20)


def pad(im, m=40):
    """Crop to content, then re-pad - getbbox() alone shaves baselines."""
    b = im.getbbox()
    if not b: return im
    x0, y0, x1, y1 = b
    return im.crop((max(0, x0-m), max(0, y0-m), min(im.width, x1+m), min(im.height, y1+m)))


def new():
    im = Image.new("RGBA", (CANVAS, CANVAS_H), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


# ---------------------------------------------------------------- templates
def never_underestimate(subject, obj_word, who="OLD MAN"):
    im, d = new()
    W = CANVAS * 0.86
    y = 200
    # both lines share ONE size, set by the longer word - they read as one block
    fb = fit(d, "UNDERESTIMATE", DISPLAY, W, 460)
    centre(d, y, "NEVER", fb, INK); y += fb.size * 0.82
    centre(d, y, "UNDERESTIMATE", fb, INK); y += fb.size * 0.88
    f3 = fit(d, f"AN {who}", SECOND, W * 0.62, 200)
    centre(d, y, f"AN {who}", f3, WARM, track=10); y += f3.size * 1.5

    # ILLUSTRATION SLOT - the one element that needs a real artwork pass
    bw, bh = CANVAS * 0.52, CANVAS * 0.26
    bx, by = (CANVAS - bw) / 2, y
    for i in range(0, int(bw), 44):          # dashed outline = placeholder
        d.line([bx+i, by, bx+min(i+24, bw), by], fill=COOL, width=7)
        d.line([bx+i, by+bh, bx+min(i+24, bw), by+bh], fill=COOL, width=7)
    for i in range(0, int(bh), 44):
        d.line([bx, by+i, bx, by+min(i+24, bh)], fill=COOL, width=7)
        d.line([bx+bw, by+i, bx+bw, by+min(i+24, bh)], fill=COOL, width=7)
    fo = font(SECOND, 64)
    lbl = f"ILLUSTRATION: {obj_word}"
    tw = d.textlength(lbl, font=fo)
    d.text(((CANVAS - tw) / 2, by + bh/2 - 40), lbl, font=fo, fill=COOL)
    y = by + bh + 70

    f4 = fit(d, "WITH A", SECOND, W * 0.3, 150)
    centre(d, y, "WITH A", f4, INK, track=14); y += f4.size * 1.35
    f5 = fit(d, subject.upper(), DISPLAY, W, 520)
    centre(d, y, subject.upper(), f5, ACCENT)
    return pad(im)


def problem_solved(obj_word):
    im, d = new()
    box = 560; gap = 150
    total = box * 2 + gap
    x0 = (CANVAS - total) / 2; y0 = 620
    for i, (label, col) in enumerate([("PROBLEM", INK), ("SOLVED", ACCENT)]):
        bx = x0 + i * (box + gap)
        d.rounded_rectangle([bx, y0, bx + box, y0 + box], radius=70, outline=col, width=16)
        if i == 0:                      # two pictogram figures
            for j, dx in enumerate((0.30, 0.66)):
                cx = bx + box * dx
                d.ellipse([cx - 52, y0 + 120, cx + 52, y0 + 224], fill=col)
                d.rounded_rectangle([cx - 62, y0 + 250, cx + 62, y0 + 452], radius=26, fill=col)
            d.text((bx + box * 0.74, y0 + 96), "!", font=font(DISPLAY, 150), fill=WARM)
        else:                            # the object
            fo = fit(d, obj_word, DISPLAY, box * 0.78, 200)
            tw = d.textlength(obj_word, font=fo)
            d.text((bx + (box - tw) / 2, y0 + box * 0.32), obj_word, font=fo, fill=col)
        fl = font(SECOND, 96)
        lw = d.textlength(label, font=fl)
        d.text((bx + (box - lw) / 2, y0 + box + 46), label, font=fl, fill=col)
    return pad(im)


def vintage_badge(subject, year, age):
    im, d = new()
    cx, cy, r = CANVAS / 2, CANVAS_H / 2, CANVAS * 0.36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WARM, width=18)
    d.ellipse([cx - r * .88, cy - r * .88, cx + r * .88, cy + r * .88], outline=INK, width=6)
    f1 = fit(d, "VINTAGE", SECOND, r * 1.1, 170)
    centre(d, cy - r * .62, "VINTAGE", f1, INK, track=18)
    f2 = fit(d, str(year), DISPLAY, r * 1.5, 620)
    centre(d, cy - r * .30, str(year), f2, ACCENT)
    f3 = fit(d, subject.upper(), DISPLAY, r * 1.3, 240)
    centre(d, cy + r * .28, subject.upper(), f3, INK)
    d.rectangle([cx - r * .62, cy + r * .58, cx + r * .62, cy + r * .58 + 90], fill=COOL)
    f4 = font(SECOND, 62)
    t = "PREMIUM QUALITY"
    centre(d, cy + r * .58 + 12, t, f4, (12, 12, 12), track=8)
    return pad(im)


def mockup(art, name, coverage=0.18):
    """Place the artwork on a black tee at the measured MEDIUM print size."""
    S = 1100
    tee = Image.new("RGB", (S, S), (17, 17, 17))
    dd = ImageDraw.Draw(tee)
    dd.rectangle([S*.18, S*.10, S*.82, S*.92], fill=(26, 26, 26))   # body
    dd.ellipse([S*.40, S*.07, S*.60, S*.17], fill=(17, 17, 17))      # neck
    # chest area = the region our coverage % refers to
    cx0, cy0, cx1, cy1 = S*.28, S*.20, S*.72, S*.66
    chest_area = (cx1-cx0)*(cy1-cy0)
    target = chest_area * coverage
    ar = art.width / art.height
    h = (target / ar) ** .5
    w = h * ar
    art2 = art.resize((int(w), int(h)), Image.LANCZOS)
    tee.paste(art2, (int((cx0+cx1)/2 - w/2), int((cy0+cy1)/2 - h/2)), art2)
    dd.text((16, S-30), f"{name}   print coverage {coverage:.0%} (house spec: 10-25%)",
            fill=(120, 120, 120), font=font(SECOND, 20))
    return tee


if __name__ == "__main__":
    jobs = [
        ("never_underestimate_fishing", never_underestimate("Fishing Rod", "OLD MAN"[:0] or "ANGLER", "OLD MAN")),
        ("never_underestimate_darts",   never_underestimate("Set Of Darts", "OCHE", "OLD WOMAN")),
        ("problem_solved_golf",         problem_solved("GOLF")),
        ("vintage_1975_biker",          vintage_badge("Biker", 1975, 51)),
    ]
    for name, art in jobs:
        art.save(OUT / f"{name}_PRINT.png")
        mockup(art, name).save(OUT / f"{name}_MOCKUP.png")
        print(f"  {name:<32} print {art.width}x{art.height}")
    print(f"\n{len(jobs)} designs rendered to designs/")
