#!/usr/bin/env python3
"""Twenty-four illustrated listings on the mockup, picked across the spread."""
import csv, os
from PIL import Image, ImageDraw, ImageFont
import compose, mockup
csv.field_size_limit(10**7)

mp = dict(l.rstrip("\n").split("\t") for l in open("ILLUS_MAP.tsv"))
want = {}
rows = []
with open("FINAL_V7.csv", newline="", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f):
        sku = f"WLT-{int(r['source_idx']):06d}"
        if sku in mp:
            rows.append((sku, mp[sku], r))
step = max(1, len(rows) // 24)
pick = rows[::step][:24]

base = mockup.make_blank()
cells = []
for sku, slug, r in pick:
    illus = Image.open(f"illus_lib/{slug}.png").convert("RGBA")
    art = compose.design_for(r, illus)
    cells.append((mockup.place(art, base.copy()).resize((300, 300)),
                  f"{slug[:24]}  |  {r['slogan'][:34]}"))

cols = 6
rows_n = (len(cells) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 300, rows_n * 322), "white")
d = ImageDraw.Draw(sheet)
try:
    fnt = ImageFont.truetype("fonts/BigShoulders-Bold.ttf", 14)
except Exception:
    fnt = ImageFont.load_default()
for i, (c, lab) in enumerate(cells):
    x, y = (i % cols) * 300, (i // cols) * 322
    sheet.paste(c, (x, y))
    d.text((x + 4, y + 304), lab, font=fnt, fill=(40, 40, 40))
sheet.save("ILLUS_COMPOSED.png")
print(sheet.size, len(cells))
