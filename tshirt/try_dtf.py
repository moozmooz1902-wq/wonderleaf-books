#!/usr/bin/env python3
"""Re-process the 24 sample illustrations through dtf.flatten and show them
on the shirt, with the printability verdict under each. Costs nothing."""
import glob, os, sys
from PIL import Image, ImageDraw, ImageFont
import dtf, mockup, gen_illus

files = sorted(glob.glob("illus_src3/*.png"))
base = mockup.make_blank()
cells, verdicts = [], []
for f in files:
    im = gen_illus.knockout(Image.open(f).convert("RGB"))
    art = dtf.flatten(im, colours=int(sys.argv[1]) if len(sys.argv) > 1 else 4)
    ok, why = dtf.printable(art)
    verdicts.append((os.path.basename(f)[:-4], ok, why))
    art.save(f"illus_flat/{os.path.basename(f)}")
    cells.append(mockup.place(art, base.copy()).resize((300, 300)))

cols = 6
rows = (len(cells) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 300, rows * 332), "white")
d = ImageDraw.Draw(sheet)
try:
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
except Exception:
    fnt = ImageFont.load_default()
for i, (c, (name, ok, why)) in enumerate(zip(cells, verdicts)):
    x, y = (i % cols) * 300, (i // cols) * 332
    sheet.paste(c, (x, y))
    d.text((x + 4, y + 302), f"{name[:30]}", font=fnt,
           fill=(0, 120, 0) if ok else (190, 0, 0))
    d.text((x + 4, y + 317), why[:40], font=fnt, fill=(90, 90, 90))
sheet.save("ILLUS_DTF.png")
sheet.resize((cols * 180, rows * 199)).save("_id.png")
print(f"{sum(1 for _,o,_ in verdicts if o)}/{len(verdicts)} pass the print gate")
for n, o, w in verdicts:
    print(f"  {'PASS' if o else 'FAIL'}  {n:<36} {w}")
