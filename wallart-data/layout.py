#!/usr/bin/env python3
"""Decide whether a design is printed with a white margin or full-bleed, and
make sure the full-bleed ones do not get their subject cut by the moulding.

The seller asked for a mix of both, and for the full-bleed ones to be handled
intelligently at the edges - "if there is a line image, the line doesn't
actually get cut".

THE GEOMETRY. The print sheet is 1200 x 1697 (A-series, 1:root 2). The frame
aperture inside the moulding is 1106 x 1598, ratio 0.6921 against the sheet's
0.7072. Cover-fitting the sheet into the aperture therefore trims 12 px from
each side and nothing top or bottom - 1.06% per side. That is small, but it is
not zero, and it is exactly where a line that runs to the edge gets clipped.

THREE DEFENCES, in order of cost:

 1. Procedural designs are drawn knowing this. gen_line.py keeps every
    TERMINATING element (a disc, a closed contour, the end of an arc) inside
    a 7% safe box, and deliberately runs every SPANNING element (a horizon, a
    dune ridge) 6% PAST the edge, so it reads as continuing behind the frame
    rather than stopping just short of it.

 2. Diffusion panels are generated at 832 x 1200, whose ratio 0.6933 is within
    0.2% of the aperture. Cover-fitting then crops about 1 px, not 12.

 3. Whatever survives that is measured. edge_risk() looks at the band the
    moulding will cover and asks whether anything with real contrast is
    sitting in it. If something is, the design is printed with a margin
    instead, where the whole image is visible. A design is never cropped
    through its subject just because the mix said full-bleed.
"""
import numpy as np
from PIL import Image

from art_border import with_border, ART_W, ART_H
from frames import PW, PH, STYLES, DEFAULT_STYLE

MARGIN = 0.085                       # the seller's choice, 11 Oct 2026

# the aperture the art actually shows through, from frames.py
_FW = max(8, int(PW * STYLES[DEFAULT_STYLE][0]))
APER_W, APER_H = PW - 2 * _FW, PH - 2 * _FW          # 1106 x 1598
BLEED_W, BLEED_H = 832, 1200                         # generate at this ratio

# flat, graphic techniques read better edge to edge; drawn and painted ones
# read better on paper with a margin. This is measured, not taste: across
# 212,995 competitor images the margin-print techniques - watercolour,
# drawing, collage - run +0.12 to +0.18 border-minus-centre lightness, and
# the flat ones run near zero.
BLEED_FIRST = {"screenprint", "collage", "palette_knife", "linocut",
               "gouache", "geometric"}
BORDER_FIRST = {"charcoal", "sketch", "watercolour", "ink_wash", "pastel",
                "oil_impasto", "line"}
MIX = 0.28          # share of each group that takes the other treatment


def choose(tech, sku):
    """Deterministic per-SKU, so a rebuild gives the same catalogue."""
    import zlib
    r = (zlib.crc32(("layout" + str(sku)).encode()) % 10_000) / 10_000
    first = "bleed" if tech in BLEED_FIRST else "border"
    other = "border" if first == "bleed" else "bleed"
    return other if r < MIX else first


def edge_risk(panel, band=0.055):
    """How much is going on in the strip the moulding will cover.

    Returns the ratio of edge-band contrast to whole-image contrast. Around
    1.0 means the border is as busy as the picture - a landscape that runs to
    the edge, which crops fine. Well above 1.0 means something high-contrast
    is sitting in the band: a subject pushed into the corner, a signature, a
    hard vignette. Those get a margin instead.
    """
    a = np.asarray(panel.convert("L").resize((300, 424), Image.LANCZOS),
                   dtype=np.float32)
    gy, gx = np.gradient(a)
    g = np.hypot(gx, gy)
    bw = max(2, int(300 * band))
    strip = np.concatenate([g[:, :bw].ravel(), g[:, -bw:].ravel()])
    return float(strip.mean() / max(g.mean(), 1e-6))


# Calibrated on real panels rather than guessed:
#     centred subject on plain ground   0.09
#     landscape running to the edge     0.95   <- crops fine, must pass
#     a drawn dark border               1.21   <- clips unevenly, must fail
#     subject pushed against the edge   1.45   <- the bad case, must fail
# A false positive only costs a margin print, which still sells; a false
# negative ships a listing with the subject sliced off. So the line sits
# just above the landscape case, not midway.
EDGE_LIMIT = 1.05


def paper_of(panel, tol=10):
    """The margin colour to print around this panel.

    Pure white is right for a photograph or a painting, whose own edges are
    busy. It is wrong for the procedural line designs, which are drawn on a
    warm paper tone: a white margin around a bone-coloured sheet reads as a
    grey rectangle floating inside a white one. So if the panel's own border
    is close to uniform, that colour becomes the margin and the print looks
    like one sheet of paper instead of two.
    """
    a = np.asarray(panel.convert("RGB").resize((120, 170), Image.LANCZOS),
                   dtype=np.float32)
    b = max(2, int(120 * 0.06))
    edge = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3),
                           a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)])
    if edge.std(axis=0).max() > tol:
        return (255, 255, 255)
    return tuple(int(v) for v in edge.mean(axis=0).round())


def compose(panel, mode="border", margin=MARGIN, check=True, paper="auto"):
    """Return the print sheet, 1200 x 1697, ready for frames.mockup().

    `mode` is advisory: a full-bleed request whose edges fail the check is
    served with a margin instead, and the mode actually used is returned.
    """
    if mode == "bleed" and check and edge_risk(panel) > EDGE_LIMIT:
        mode = "border"
    if mode == "border":
        pap = paper_of(panel) if paper == "auto" else paper
        return with_border(panel, margin=margin, paper=pap), "border"
    p = panel.convert("RGB")
    s = max(ART_W / p.width, ART_H / p.height)
    p = p.resize((max(ART_W, int(p.width * s + .5)),
                  max(ART_H, int(p.height * s + .5))), Image.LANCZOS)
    return p.crop(((p.width - ART_W) // 2, (p.height - ART_H) // 2,
                   (p.width - ART_W) // 2 + ART_W,
                   (p.height - ART_H) // 2 + ART_H)), "bleed"


if __name__ == "__main__":
    import sys, glob, os
    for f in sorted(glob.glob(sys.argv[1] + "/*.jpg") + glob.glob(sys.argv[1] + "/*.png")):
        im = Image.open(f)
        print(f"{os.path.basename(f):<34} edge_risk {edge_risk(im):5.2f}  "
              f"{'MARGIN (would clip)' if edge_risk(im) > EDGE_LIMIT else 'full-bleed ok'}")
