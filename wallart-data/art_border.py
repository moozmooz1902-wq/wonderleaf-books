#!/usr/bin/env python3
"""Put the white border into the ARTWORK, not into the frame.

The seller's frames are plain black mouldings with no physical mount. What
looks like a mount on a finished print is white paper around the image, and
that belongs in the design file so it is printed, not faked in the mockup.

This also matches the market. Measured across 212,995 competitor images
(measured_colour_and_style.md), border-minus-centre lightness is only +0.018
at the baseline but +0.12 to +0.18 for the margin-print techniques -
watercolour, drawing, collage. A visible paper margin is a differentiator in
itself and costs nothing.

Output is the A-series print master at 1200 x 1697, panel centred on white
with an even margin, slightly deeper at the foot the way a mounted print is
traditionally hung.
"""
from PIL import Image

ART_W, ART_H = 1200, 1697          # A-series ratio, the print master size
PAPER = (255, 255, 255)
MARGIN = 0.085                     # share of the SHORT edge, each side
FOOT_EXTRA = 0.45                  # the foot margin is this much deeper again


def with_border(panel, margin=MARGIN, foot_extra=FOOT_EXTRA, paper=PAPER):
    """Centre `panel` on white paper at the print-master size."""
    m = int(ART_W * margin)
    foot = int(m * (1 + foot_extra))
    iw = ART_W - 2 * m
    ih = ART_H - m - foot
    p = panel.convert("RGB")
    s = max(iw / p.width, ih / p.height)          # cover-fit, never letterbox
    p = p.resize((max(iw, int(p.width * s + .5)), max(ih, int(p.height * s + .5))),
                 Image.LANCZOS)
    p = p.crop(((p.width - iw) // 2, (p.height - ih) // 2,
                (p.width - iw) // 2 + iw, (p.height - ih) // 2 + ih))
    sheet = Image.new("RGB", (ART_W, ART_H), paper)
    sheet.paste(p, (m, m))
    return sheet


if __name__ == "__main__":
    import sys, os
    src, out = sys.argv[1], sys.argv[2]
    im = with_border(Image.open(src))
    im.save(out, "JPEG", quality=94)
    # report the measurement the market is judged on
    import numpy as np
    a = np.asarray(im.convert("L"), dtype=np.float32) / 255
    bw = 10
    border = np.concatenate([a[:bw].ravel(), a[-bw:].ravel(),
                             a[:, :bw].ravel(), a[:, -bw:].ravel()])
    centre = a[a.shape[0]//4:3*a.shape[0]//4, a.shape[1]//4:3*a.shape[1]//4]
    print(f"{out}  {im.size}  border-minus-centre {border.mean()-centre.mean():+.3f}"
          f"   (market margin prints: +0.12 to +0.18)")
