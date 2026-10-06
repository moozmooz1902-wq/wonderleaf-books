#!/usr/bin/env python3
"""Contact sheet of the finished print files, as they will appear on the tee.

These are already through dtf.flatten on the pod, so nothing is reprocessed
here - what is drawn is exactly what gets printed.
"""
import glob, os
from PIL import Image, ImageDraw, ImageFont
import mockup

files = sorted(glob.glob("illus400/*.png"))
base = mockup.make_blank()
cols, cell = 8, 260
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, rows * (cell + 22)), "white")
d = ImageDraw.Draw(sheet)
try:
    fnt = ImageFont.truetype("fonts/BigShoulders-Bold.ttf", 15)
except Exception:
    fnt = ImageFont.load_default()
for i, f in enumerate(files):
    art = Image.open(f).convert("RGBA")
    x, y = (i % cols) * cell, (i // cols) * (cell + 22)
    sheet.paste(mockup.place(art, base.copy()).resize((cell, cell)), (x, y))
    d.text((x + 4, y + cell + 3), os.path.basename(f)[:-4][:34], font=fnt, fill=(40, 40, 40))
sheet.save("ILLUS_400.png")
print(sheet.size, len(files), "designs")
