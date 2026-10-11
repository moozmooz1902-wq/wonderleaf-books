#!/usr/bin/env python3
"""One sheet: four frame styles x three colours, same artwork throughout."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
from frames import mockup, STYLES, COLOURS

art = Image.open(sys.argv[1]); out = sys.argv[2]
cell, pad, hdr = 560, 10, 76
cols = list(COLOURS); rows = list(STYLES)
W = len(cols) * cell + 170
H = len(rows) * cell + hdr
sheet = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(sheet)
def font(sz, bold=True):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try: return ImageFont.truetype(p, sz)
    except Exception: return ImageFont.load_default()
F, f2 = font(34), font(21, False)

LABEL = {"A": ("A", "thin frame\nno mount"), "B": ("B", "thin frame\nwhite mount"),
         "C": ("C", "wide frame\nno mount"), "D": ("D", "wide frame\nwhite mount")}
for j, c in enumerate(cols):
    d.text((170 + j * cell + 20, 24), c.upper() + (" — main image" if c == "black" else ""),
           fill=(15, 15, 15), font=F)
for i, st in enumerate(rows):
    y = hdr + i * cell
    tag, desc = LABEL[st]
    d.text((34, y + cell // 2 - 54), tag, fill=(15, 15, 15), font=font(68))
    d.text((34, y + cell // 2 + 18), desc, fill=(90, 90, 90), font=f2)
    for j, c in enumerate(cols):
        im = mockup(art, c, st).resize((cell - pad * 2, cell - pad * 2), Image.LANCZOS)
        sheet.paste(im, (170 + j * cell + pad, y + pad))
sheet.save(out, "JPEG", quality=90)
print(out, sheet.size)
