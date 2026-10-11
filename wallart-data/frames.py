#!/usr/bin/env python3
"""Listing mockups: three frame colours x four frame styles.

The geometry is NOT a design choice. The seller's team runs a crop tool that
finds the dark moulding and cuts everything outside it, so the canvas size and
the moulding's OUTER edge are an interface other software depends on. From
wallart/size_contract.py on the wall-art branch:

    canvas     2000 x 2000 on wall #EDE9E3
    moulding   outer edge (406, 160) to (1593, 1840)   -> 1188 x 1680

Every style below keeps that outer edge identical and varies only what happens
INSIDE it, so the cropper is unaffected whichever is chosen.

    A  thin moulding, art to the edge      - modern, most art per listing
    B  thin moulding + white mount         - CHOSEN by the seller, 11 Oct 2026
    C  wide moulding, art to the edge      - bolder, more substantial
    D  wide moulding + white mount         - most traditional

Black stays the main listing image: the cropper keys on the dark band and a
white moulding is not dark enough for it to find.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter

CANVAS = 2000
WALL   = (0xED, 0xE9, 0xE3)
RATIO  = 2 ** 0.5
PH     = int(CANVAS * 0.84)        # 1680
PW     = int(PH / RATIO)           # 1188
X      = (CANVAS - PW) // 2        # 406
Y      = (CANVAS - PH) // 2        # 160

COLOURS = {
    "black": ((22, 22, 22),    (8, 8, 8),       None),
    "white": ((250, 250, 248), (214, 211, 205), None),
    "oak":   ((193, 154, 107), (150, 115, 76),  "wood"),
}
# style -> (moulding width as a fraction of PW, mount width as a fraction)
STYLES = {
    "A": (0.035, 0.00),
    "B": (0.035, 0.075),
    "C": (0.075, 0.00),
    "D": (0.075, 0.065),
}
MOUNT = (252, 251, 248)


def _grain(im, box):
    import random
    d = ImageDraw.Draw(im); rng = random.Random(7)
    x0, y0, x1, y1 = box
    for _ in range(1100):
        x = rng.randint(x0, x1); h = rng.randint(30, 260)
        y = rng.randint(y0, max(y0, y1 - h)); v = rng.randint(-16, 12)
        d.line([x, y, x, y + h], fill=(193 + v, 154 + v, 107 + v), width=1)


DEFAULT_STYLE = "B"          # the seller picked B from the option sheet


def mockup(art, colour="black", style=DEFAULT_STYLE):
    moulding, lip, grain = COLOURS[colour]
    fw = max(8, int(PW * STYLES[style][0]))
    mw = int(PW * STYLES[style][1])
    canvas = Image.new("RGB", (CANVAS, CANVAS), WALL)

    sh = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(sh).rectangle([X + 6, Y + 10, X + PW + 6, Y + PH + 12], fill=110)
    canvas.paste(Image.new("RGB", (CANVAS, CANVAS), (60, 55, 50)), (0, 0),
                 sh.filter(ImageFilter.GaussianBlur(14)))

    d = ImageDraw.Draw(canvas)
    d.rectangle([X, Y, X + PW, Y + PH], fill=moulding)      # outer edge: FIXED
    if grain == "wood":
        _grain(canvas, (X, Y, X + PW, Y + PH))
    if lip:
        d.rectangle([X, Y, X + PW, Y + PH], outline=lip, width=3)
        d.rectangle([X + fw - 3, Y + fw - 3, X + PW - fw + 3, Y + PH - fw + 3],
                    outline=lip, width=3)
    if mw:
        d.rectangle([X + fw, Y + fw, X + PW - fw, Y + PH - fw], fill=MOUNT)
        d.rectangle([X + fw + mw - 2, Y + fw + mw - 2,
                     X + PW - fw - mw + 2, Y + PH - fw - mw + 2],
                    outline=(228, 225, 219), width=2)

    inset = fw + mw
    iw, ih = PW - 2 * inset, PH - 2 * inset
    a = art.convert("RGB")
    s = max(iw / a.width, ih / a.height)
    a = a.resize((max(iw, int(a.width * s + .5)), max(ih, int(a.height * s + .5))), Image.LANCZOS)
    a = a.crop(((a.width - iw) // 2, (a.height - ih) // 2,
                (a.width - iw) // 2 + iw, (a.height - ih) // 2 + ih))
    canvas.paste(a, (X + inset, Y + inset))
    return canvas


def frame_box(photo):
    g = photo.convert("L"); w, h = g.size; px = g.load()
    xs = [x for x in range(w) if px[x, h // 2] < 60]
    ys = [y for y in range(h) if px[w // 2, y] < 60]
    return (min(xs), min(ys), max(xs), max(ys)) if xs and ys else None


if __name__ == "__main__":
    art = Image.open(sys.argv[1]); outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    for st in STYLES:
        for col in COLOURS:
            im = mockup(art, col, st)
            im.save(os.path.join(outdir, f"{st}_{col}.jpg"), "JPEG", quality=92)
        print(f"style {st}: black frame box {frame_box(mockup(art, 'black', st))}")
