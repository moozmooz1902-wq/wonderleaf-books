#!/usr/bin/env python3
"""The image sizes are an interface. This asserts them.

The seller's team runs a tool over the listing photos that finds the black
frame and crops everything outside it. That makes the canvas size, and the
frame's position inside it, something other people's software depends on -
not a rendering detail someone can nudge while improving a design.

2000x2000 is measured, not chosen: every listing photo already in the
seller's buckets is 2000x2000, checked on 14 drawn at random from a real
listing of the bucket rather than from memory of what was built.

So the numbers below are fixed, and this fails loudly if a change moves
them. Run it after touching render.py, publish.py or serve.py.

    python3 size_contract.py
"""
import sys
from render import render, mockup

# --- the contract -----------------------------------------------------------
LISTING_CANVAS = (2000, 2000)          # art/mock/<SKU>.jpg
FRAME_BOX      = (406, 160, 1593, 1840)   # the black moulding, outer edge
ART_WIDTH      = 1200                  # what the art is drawn at before framing
ART_SIZE       = (1200, 1697)          # A-series ratio at that width
PRINT = {"A4": (2480, 3507),           # art/raw/<SKU>.png, 300 dpi
         "A3": (3508, 4961),
         "A2": (4961, 7015)}
WALL = "#EDE9E3"
# ----------------------------------------------------------------------------

SAMPLE = [("The Maxwell / family / together since 1968", "bw", "classic_serif", "stack", "none"),
          ("Ruby / & / Paul / 2011", "navy", "raleway", "subway", "heart"),
          ("But first, / *coffee*", "sage", "didone", "arch", "cup"),
          ("Gather / here", "bwgrey", "anton", "badge", "none")]


def frame_box(im):
    """Find the moulding the way a cropping tool would: the dark band."""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    xs = [x for x in range(w) if px[x, h // 2] < 60]
    ys = [y for y in range(h) if px[w // 2, y] < 60]
    if not xs or not ys:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def main():
    bad = []
    for phrase, pal, fonts, layout, orn in SAMPLE:
        art = render(phrase, pal, fonts, layout, orn, ART_WIDTH)
        if art.size != ART_SIZE:
            bad.append(f"art is {art.size}, the contract says {ART_SIZE}  [{phrase[:30]}]")
        photo = mockup(art, framed=True)
        if photo.size != LISTING_CANVAS:
            bad.append(f"listing photo is {photo.size}, the contract says {LISTING_CANVAS}")
        fb = frame_box(photo)
        if fb != FRAME_BOX:
            bad.append(f"frame is at {fb}, the contract says {FRAME_BOX}  [{phrase[:30]}]"
                       "  -- this is what the team's cropper keys on")
    for size, want in PRINT.items():
        px = {"A4": 2480, "A3": 3508, "A2": 4961}[size]
        got = render(SAMPLE[0][0], "bw", "classic_serif", "stack", "none", px).size
        if got != want:
            bad.append(f"{size} print file is {got}, the contract says {want}")

    if bad:
        print("SIZE CONTRACT BROKEN\n")
        for b in bad:
            print("  " + b)
        print("\nThe team's crop tool keys on these. Do not change them to fix a design.")
        return 1
    print("size contract holds:")
    print(f"  listing photo  {LISTING_CANVAS[0]}x{LISTING_CANVAS[1]} JPEG on {WALL}")
    print(f"  frame box      {FRAME_BOX}   ({FRAME_BOX[2]-FRAME_BOX[0]}x{FRAME_BOX[3]-FRAME_BOX[1]})")
    print(f"  art            {ART_SIZE[0]}x{ART_SIZE[1]} before framing")
    for k, v in PRINT.items():
        print(f"  {k} print file  {v[0]}x{v[1]} PNG at 300dpi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
