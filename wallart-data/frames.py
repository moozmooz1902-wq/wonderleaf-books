#!/usr/bin/env python3
"""Listing mockups in the three frame colours the Fy! data sells: black, white, oak.

The geometry is NOT a design choice. The seller's team runs a crop tool that
finds the black moulding and cuts everything outside it, so the canvas size and
the frame's position are an interface other software depends on. Those numbers
come from wallart/size_contract.py on the wall-art branch and are reproduced
here exactly:

    canvas     2000 x 2000 on wall #EDE9E3
    moulding   outer edge (406, 160) to (1593, 1840)   -> 1188 x 1680
    art area   (447, 201) to (1553, 1799)              -> 1106 x 1598

All three colours use the SAME geometry, so the art occupies identical pixels
whichever frame is shown and the crop tool is unaffected. Only the moulding
pixels differ. Black stays the main listing image because it is the one the
crop tool keys on - a white moulding is not dark enough for it to find.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter

CANVAS = 2000
WALL   = (0xED, 0xE9, 0xE3)
RATIO  = 2 ** 0.5                 # A-series
PH     = int(CANVAS * 0.84)       # 1680
PW     = int(PH / RATIO)          # 1188
X      = (CANVAS - PW) // 2       # 406
Y      = (CANVAS - PH) // 2       # 160
FW     = max(8, int(PW * 0.035))  # 41, the moulding width

FRAMES = {
    # name:  (moulding rgb, inner lip rgb or None, grain)
    "black": ((22, 22, 22),    (8, 8, 8),       None),
    "white": ((250, 250, 248), (214, 211, 205), None),
    "oak":   ((193, 154, 107), (150, 115, 76),  "wood"),
}


def _grain(im, box):
    """Faint vertical streaks so the oak reads as timber, not flat tan."""
    import random
    d = ImageDraw.Draw(im)
    rng = random.Random(7)
    x0, y0, x1, y1 = box
    for _ in range(900):
        x = rng.randint(x0, x1)
        h = rng.randint(30, 260)
        y = rng.randint(y0, max(y0, y1 - h))
        v = rng.randint(-16, 12)
        d.line([x, y, x, y + h], fill=(193 + v, 154 + v, 107 + v), width=1)


def mockup(art: Image.Image, frame: str = "black") -> Image.Image:
    """One 2000x2000 listing photo. `art` is fitted to the A-ratio art area."""
    if frame not in FRAMES:
        raise ValueError(f"frame must be one of {sorted(FRAMES)}")
    moulding, lip, grain = FRAMES[frame]
    canvas = Image.new("RGB", (CANVAS, CANVAS), WALL)

    # drop shadow, so the frame sits on the wall rather than floating
    sh = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(sh).rectangle([X + 6, Y + 10, X + PW + 6, Y + PH + 12], fill=110)
    canvas.paste(Image.new("RGB", (CANVAS, CANVAS), (60, 55, 50)), (0, 0),
                 sh.filter(ImageFilter.GaussianBlur(14)))

    d = ImageDraw.Draw(canvas)
    d.rectangle([X, Y, X + PW, Y + PH], fill=moulding)
    if grain == "wood":
        _grain(canvas, (X, Y, X + PW, Y + PH))
    # a white moulding would otherwise vanish into the wall; the lip gives it an edge
    if lip:
        d.rectangle([X, Y, X + PW, Y + PH], outline=lip, width=3)
        d.rectangle([X + FW - 3, Y + FW - 3, X + PW - FW + 3, Y + PH - FW + 3],
                    outline=lip, width=3)

    iw, ih = PW - 2 * FW, PH - 2 * FW
    a = art.convert("RGB")
    # cover-fit then centre-crop, so the art fills the aperture at full size and
    # is never shrunk or letterboxed inside it
    s = max(iw / a.width, ih / a.height)
    a = a.resize((max(iw, int(a.width * s + 0.5)), max(ih, int(a.height * s + 0.5))),
                 Image.LANCZOS)
    a = a.crop(((a.width - iw) // 2, (a.height - ih) // 2,
                (a.width - iw) // 2 + iw, (a.height - ih) // 2 + ih))
    canvas.paste(a, (X + FW, Y + FW))
    return canvas


def contract_ok(photo: Image.Image) -> tuple:
    """Find the moulding the way the team's cropper does: the dark band."""
    g = photo.convert("L"); w, h = g.size; px = g.load()
    xs = [x for x in range(w) if px[x, h // 2] < 60]
    ys = [y for y in range(h) if px[w // 2, y] < 60]
    return (min(xs), min(ys), max(xs), max(ys)) if xs and ys else None


if __name__ == "__main__":
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    art = Image.open(src)
    for name in ("black", "white", "oak"):
        im = mockup(art, name)
        p = os.path.join(outdir, f"{name}.jpg")
        im.save(p, "JPEG", quality=92)
        print(f"{name:<6} {im.size}  {os.path.getsize(p)//1024} KB", end="")
        if name == "black":
            print(f"  frame box {contract_ok(im)}  (contract: (406, 160, 1593, 1840))")
        else:
            print()
