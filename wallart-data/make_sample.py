#!/usr/bin/env python3
"""Turn raw FLUX panels into what the buyer actually sees, and a contact sheet.

panel -> art_border.with_border (white paper margin, printed into the design)
      -> frames.mockup (style A, plain moulding, no mount) in black / white / oak

Black is written first and named *_1.jpg because it is the main listing image
and the crop tool keys on the dark moulding.
"""
import os, sys, glob
from PIL import Image, ImageDraw
from art_border import with_border
from frames import mockup

MARGIN = 0.06          # 6% of the short edge; the seller's "white bits"


def one(panel_path, outdir, margin=MARGIN):
    stem = os.path.splitext(os.path.basename(panel_path))[0]
    sheet = with_border(Image.open(panel_path), margin=margin)
    sheet.save(os.path.join(outdir, f"{stem}_print.jpg"), "JPEG", quality=94)
    out = []
    for n, col in enumerate(("black", "white", "oak"), 1):
        p = os.path.join(outdir, f"{stem}_{n}_{col}.jpg")
        mockup(sheet, col).resize((1400, 1400), Image.LANCZOS).save(p, "JPEG", quality=90)
        out.append(p)
    return out


def contact(paths, out, cols=4, cell=440, labels=None):
    rows = (len(paths) + cols - 1) // cols
    pad, lab = 10, (26 if labels else 0)
    sh = Image.new("RGB", (cols * (cell + pad) + pad,
                           rows * (cell + pad + lab) + pad), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for i, p in enumerate(paths):
        x = pad + (i % cols) * (cell + pad)
        y = pad + (i // cols) * (cell + pad + lab)
        sh.paste(Image.open(p).resize((cell, cell), Image.LANCZOS), (x, y))
        if labels:
            d.text((x + 2, y + cell + 6), labels[i][:54], fill=(40, 40, 40))
    sh.save(out, "JPEG", quality=88)
    return out


if __name__ == "__main__":
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    panels = sorted(glob.glob(os.path.join(src, "*.png")) + glob.glob(os.path.join(src, "*.jpg")))
    panels = [p for p in panels if "_print" not in p and "_black" not in p]
    made = []
    for p in panels:
        made += one(p, outdir)
        print(p)
    print(contact([m for m in made if "_1_black" in m], os.path.join(outdir, "CONTACT_black.jpg")))
