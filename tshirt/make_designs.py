#!/usr/bin/env python3
"""Render the catalogue: slogan -> artwork -> composited on the real tee.

Looks are mixed across the catalogue rather than picking one, so the store
does not read as auto-generated, and so the sales data can tell us later
which look actually wins. Assignment is seeded off source_idx, so a rerun
gives the same listing the same look.
"""
import csv, os, random, sys
from PIL import Image, ImageDraw
import styles, mockup
from linebreak import break_lines

# A and B are the most legible at thumbnail size, so they carry the weight
LOOKS = [("A", styles.a_two_tone,   styles.DIRECTIONS[0][2], 35),
         ("B", styles.b_single_ink, styles.DIRECTIONS[1][2], 30),
         ("C", styles.c_badge,      styles.DIRECTIONS[2][2], 15),
         ("D", styles.d_serif_block,styles.DIRECTIONS[3][2], 20)]
_W = [l[3] for l in LOOKS]


def look_for(idx):
    return random.Random(f"look-{idx}").choices(LOOKS, _W)[0]


def artwork(fn, lines, pal):
    canvas = Image.new("RGBA", (styles.W, styles.H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(canvas), lines, pal)
    bb = canvas.getbbox()
    return canvas.crop(bb) if bb else canvas


def design(row, blank=None):
    name, fn, pal, _ = look_for(row["source_idx"])
    lines = break_lines(row["slogan"])
    return name, mockup.place(artwork(fn, lines, pal), blank)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    rows = [r for r in csv.DictReader(open("REPLICA_V3.csv"))
            if r["slogan"] and r["layout"] == "text_only"]
    print(f"{len(rows):,} text-only rows available")
    rng = random.Random(4)
    pick = rng.sample(rows, n)
    blank = Image.open(mockup.BLANK)
    TH = 560
    cols = 4
    sheet = Image.new("RGB", (cols*TH, ((n+cols-1)//cols)*(TH+34)), (250,250,252))
    d = ImageDraw.Draw(sheet); lab = styles.font("grotesk", 19)
    for k, r in enumerate(pick):
        nm, im = design(r, blank)
        im = im.resize((TH-10, TH-10), Image.LANCZOS)
        x, y = (k % cols)*TH+5, (k//cols)*(TH+34)+5
        sheet.paste(im, (x, y))
        d.text((x+2, y+TH-4), f"{nm}  {r['slogan'][:44]}", font=lab, fill=(40,40,46))
    sheet.save("DESIGN_SAMPLE.png")
    print("wrote DESIGN_SAMPLE.png")
