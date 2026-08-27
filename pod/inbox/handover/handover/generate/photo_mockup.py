"""
photo_mockup.py — composites artwork onto the real photographed blank.

Everything is derived from the photo itself, so this same module works for any
garment photo you drop in later (different blank, on-model, second angle):

  mask   : garment vs background, from luminance + flood fill from the corners
  shade  : the photo's own luminance, normalised — real folds and lighting
  disp   : gradient of that luminance — the print bends where the fabric bends

Print placement is set once in PRINT_BOX as a fraction of the garment bbox,
so it stays correct even if the photo is re-cropped.
"""

import os
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import (binary_fill_holes, gaussian_filter, map_coordinates,
                           binary_erosion, label)

# Look for the blank tee next to this script first, then fall back to any
# path in the BLANK_TEE env var. Hardcoding an absolute path breaks the moment
# the code moves to another machine.
BLANK = os.environ.get("BLANK_TEE") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "blank.png")
if not os.path.exists(BLANK):
    raise SystemExit(f"blank tee image not found at {BLANK} — "
                     "put blank.png beside this script or set BLANK_TEE")
# The mockup IS the listing image — it does the selling, so it should support
# eBay's zoom rather than scrape the minimum. 1600 was the floor; 2400 lets a
# buyer zoom into the artwork.
#
# The blank photo is only 1086x1448, so the garment itself is upscaled. That is
# acceptable because the shirt is largely flat black, while the ARTWORK is
# composited from a 3600x4800 source and stays genuinely sharp.
# Square, and cropped to the garment. Measured against competitors on an eBay
# results row: their shirts filled 96-98% of the thumbnail, ours only 78%,
# because the blank photo carries a band of empty space above and below the
# shirt. On a scrolling page that makes the listing look smaller and weaker.
OUT_W, OUT_H = 2000, 2000

# Fraction of the frame left as breathing room around the garment.
FRAME_MARGIN = 0.025

# ---- print window, as fractions of the GARMENT bounding box ----
# Sized to a real A3 transfer (11.7 x 16.5in), which is what the DTF press
# takes. That lands around 52% of garment width — in line with what the
# high-volume sellers actually print, and well clear of the sleeve seams
# where a transfer edge would crease and lift.
# Narrower than before. Measured on a reference design he liked, the artwork
# was 39% of the shirt width; this was 52%, which ran too close to the seams.
PRINT_BOX = (0.300, 0.200, 0.700, 0.560)

# Tall designs (illustration stacked with text) get a deeper window so they
# do not shrink to fit; wide designs use the standard one.
TALL_Y1 = 0.740

DISPLACE = 9.0      # px of warp at full fold gradient
SHADE_MIX = 1.00    # 1.0 = folds fully modulate the ink
INK_OPACITY = 0.94  # ink sits into the weave, never a flat sticker

# INK_RGB is used ONLY when the artwork is a single-colour design (the text
# pipeline). Full-colour graphics keep their own colours — the earlier version
# painted every design flat white, which is why colourful dragons came out as
# greyscale prints.
INK_RGB = (246, 246, 243)   # white plastisol/DTG, not pure #FFF
FORCE_WHITE = False         # set True only for single-colour text designs


def _load():
    img = Image.open(BLANK).convert("RGB")

    # Crop the blank down to the garment before anything else, so the shirt
    # fills the frame instead of floating in white space.
    a0 = np.asarray(img.convert("L"))
    sm = a0 < 118
    ys0, xs0 = np.where(sm)
    if len(ys0):
        pad_x = int((xs0.max() - xs0.min()) * FRAME_MARGIN)
        pad_y = int((ys0.max() - ys0.min()) * FRAME_MARGIN)
        box = (max(0, xs0.min() - pad_x), max(0, ys0.min() - pad_y),
               min(img.width, xs0.max() + pad_x),
               min(img.height, ys0.max() + pad_y))
        # Square, but NEVER outside the source image.
        #
        # The first version took max(width, height) around the shirt's centre.
        # The shirt is taller than it is wide, so the crop ran past the left
        # and right edges — and PIL fills out-of-bounds with BLACK. Live
        # listings showed a black bar down each side of the photo, on those
        # two sides only, because that was the dimension that did not fit.
        #
        # Clamp the square to what actually exists, then pad the remainder
        # with the blank's own background colour rather than black.
        bw, bh = box[2] - box[0], box[3] - box[1]
        cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
        side = min(max(bw, bh), img.width, img.height)
        half = side // 2
        x0 = max(0, min(cx - half, img.width - side))
        y0 = max(0, min(cy - half, img.height - side))
        img = img.crop((x0, y0, x0 + side, y0 + side))

    img = img.resize((OUT_W, OUT_H), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32)
    lum = arr.mean(2)

    # --- garment mask: dark region, flood-filled, largest component only ---
    m = lum < 118
    m = binary_fill_holes(m)
    lbl, n = label(m)
    if n > 1:
        sizes = np.bincount(lbl.ravel())
        sizes[0] = 0
        m = lbl == sizes.argmax()
    mask = gaussian_filter(m.astype(np.float32), 1.2)

    # --- shading: the photo's own luminance inside the garment ---
    inside = binary_erosion(m, iterations=6)
    vals = lum[inside]
    mid = np.median(vals)
    shade = np.clip(lum / max(mid, 1.0), 0.35, 2.2)
    shade = gaussian_filter(shade, 1.5).astype(np.float32)

    return img, arr, lum, m, mask, shade


BASE_IMG, BASE_ARR, LUM, MASK_BOOL, MASK, SHADE = _load()

ys, xs = np.where(MASK_BOOL)
GX0, GX1, GY0, GY1 = xs.min(), xs.max(), ys.min(), ys.max()
GW, GH = GX1 - GX0, GY1 - GY0

# --- displacement field from the fold structure ---
_s = gaussian_filter(LUM, 6)
_gy, _gx = np.gradient(_s)
_n = max(np.abs(_gx).max(), np.abs(_gy).max(), 1e-6)
_gx, _gy = (_gx / _n).astype(np.float32), (_gy / _n).astype(np.float32)
_YY, _XX = np.mgrid[0:OUT_H, 0:OUT_W].astype(np.float32)
_COORDS = np.stack([_YY + _gy * DISPLACE, _XX + _gx * DISPLACE])


def print_window():
    x0 = GX0 + PRINT_BOX[0] * GW
    y0 = GY0 + PRINT_BOX[1] * GH
    x1 = GX0 + PRINT_BOX[2] * GW
    y1 = GY0 + PRINT_BOX[3] * GH
    return int(x0), int(y0), int(x1), int(y1)


PX0, PY0, PX1, PY1 = print_window()

# soft-edged print mask so ink can't spill onto the background or sleeves
_pw = np.zeros((OUT_H, OUT_W), np.float32)
_pw[PY0:int(GY0 + (TALL_Y1 + 0.02) * GH), PX0:PX1] = 1.0
PRINT_MASK = gaussian_filter(_pw, 2.5) * MASK


def build(art_path, out_path):
    art = Image.open(art_path)

    # No resolution guard here. Measured: the artwork lands at ~688px inside
    # an 1800px mockup, so even a 1024 source is DOWNSCALED and stays sharp.
    # An earlier version warned below 1600px, based on a measurement that
    # mistook the faint vignette fade for artwork.
    # The print file is 3600x4800 but the mockup only needs ~1000px of it.
    # draft() decodes at a reduced size, which is far faster and loses nothing
    # because the artwork is downscaled either way.
    art.draft("RGBA", (OUT_W, OUT_H))
    art = art.convert("RGBA")
    bb = art.getbbox()
    if bb:
        art = art.crop(bb)

    # The print window is wide, so a tall design (text above and below an
    # illustration) fits by height and lands too small. Extend the window
    # downward for tall artwork so it prints at a usable size either way.
    aspect = art.width / art.height
    py1 = int(GY0 + TALL_Y1 * GH) if aspect < 1.05 else PY1
    bw, bh = PX1 - PX0, py1 - PY0

    s = bw / art.width
    if art.height * s > bh:
        s = bh / art.height
    art = art.resize((max(1, int(art.width * s)), max(1, int(art.height * s))),
                     Image.LANCZOS)

    layer = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    layer.alpha_composite(art, (PX0 + (bw - art.width) // 2,
                                PY0 + (bh - art.height) // 2))
    a = np.asarray(layer).astype(np.float32)
    a = np.stack([map_coordinates(a[..., c], _COORDS, order=1, mode="nearest")
                  for c in range(4)], axis=-1)

    alpha = np.clip(a[..., 3] / 255.0 * PRINT_MASK * INK_OPACITY, 0, 1)[..., None]

    if FORCE_WHITE:
        ink = np.zeros((OUT_H, OUT_W, 3), np.float32)
        for i, c in enumerate(INK_RGB):
            ink[..., i] = c
    else:
        # Keep the artwork's own colour. The garment's folds still modulate
        # it below, so the print sits in the weave rather than floating.
        ink = a[..., :3].astype(np.float32)
    ink *= (1.0 - SHADE_MIX + SHADE_MIX * SHADE)[..., None]

    out = BASE_ARR * (1 - alpha) + np.clip(ink, 0, 255) * alpha
    img_out = Image.fromarray(out.astype(np.uint8), "RGB")
    # A touch of unsharp recovers the crispness lost upscaling the blank.
    # Kept light — heavy sharpening produces halos around the print edge.
    img_out = img_out.filter(
        ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=3))
    img_out.save(out_path, quality=95, subsampling=0, optimize=True)
    return out_path


if __name__ == "__main__":
    os.makedirs("mock", exist_ok=True)
    from render import render_to_canvas
    render_to_canvas("Never Underestimate A Bricklayer", "bold", "light", 7).save("art_test.png")
    print(build("art_test.png", "mock/_photo_test.jpg"))
    print("garment bbox", (GX0, GY0, GX1, GY1), "print window", (PX0, PY0, PX1, PY1))
