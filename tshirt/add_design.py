#!/usr/bin/env python3
"""Add a "This design" block to every description.

Two listings can share a theme - two different Happy Birthday shirts - and the
photo and print file already differ. Saying in words what makes this one
different gives a buyer, and anyone reviewing the listing, something concrete
to tell them apart by: the drawing style, the layout, the colourway and the
illustration subject. All four come from the catalogue's own design record.
"""
import csv, html, os

csv.field_size_limit(20 << 20)
SRC = "/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv"
TMP = SRC + ".new"
ANCHOR = "<p>Printed on a heavyweight black cotton t-shirt, chest centred.</p>"

STYLE = {"line_art": "Line art", "distressed": "Distressed vintage print",
         "typography_only": "Typography", "cartoon": "Cartoon illustration",
         "flat_vector": "Flat vector artwork", "photographic": "Photographic"}
LAYOUT = {"text_only": "wording only, no illustration",
          "text_above_image": "wording above the illustration",
          "image_only": "illustration only, no wording",
          "text_below_image": "wording below the illustration",
          "two_panel": "a two-panel layout"}

src = {}
for r in csv.DictReader(open("v7.csv", newline="", encoding="utf-8")):
    if r["slogan"]:
        src[f"WLT-{int(r['source_idx']):06d}"] = r

def block(s):
    style  = STYLE.get(s.get("style", ""), "Original artwork")
    layout = LAYOUT.get(s.get("layout", ""), "a centred layout")
    pal    = (s.get("palette", "") or "").replace("-", " ").strip()
    bits = [f"{style}, {layout}"]
    if pal:
        bits.append(f'in a <b>{html.escape(pal)}</b> colourway')
    sent = " ".join(bits) + "."
    illus = (s.get("illustration", "") or "").strip()
    extra = (f" Illustration: {html.escape(illus)}." if illus else "")
    return ("<h3>This design</h3><p>" + sent + extra +
            " Printed for this listing only &mdash; each of our designs is drawn "
            "separately, so the artwork, wording and colours differ from listing "
            "to listing.</p>")

added = missing = noanchor = 0
with open(SRC, newline="", encoding="utf-8") as f, \
     open(TMP, "w", newline="", encoding="utf-8") as o:
    r = csv.reader(f); w = csv.writer(o, lineterminator="\r\n")
    hdr = next(r); w.writerow(hdr)
    IREL = hdr.index("Relationship")
    for row in r:
        if (row[IREL] or "").strip() != "Variation":
            s = src.get(row[1].strip())
            if s is None:
                missing += 1
            elif ANCHOR in row[4]:
                row[4] = row[4].replace(ANCHOR, ANCHOR + block(s), 1)
                added += 1
            else:
                noanchor += 1
        w.writerow(row)
os.replace(TMP, SRC)
print(f"design blocks added     {added:,}")
print(f"no source row           {missing:,}")
print(f"anchor paragraph absent {noanchor:,}")
