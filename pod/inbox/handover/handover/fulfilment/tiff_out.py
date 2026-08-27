"""
tiff_out.py — write the CMYK + white-spot TIFF the printer expects.

WHAT THE DESIGNER'S FILE ACTUALLY IS
    Reading a sample he produced:
        CMYK, plus a 5th channel
        SamplesPerPixel 5, ExtraSamples (0,)
        the 5th channel is the WHITE plate, stored INVERTED —
        0 means full white ink, 255 means none, which is the Photoshop
        spot-channel convention
        the white is choked: only 0.2% of it falls outside the artwork

    That is what this writes, so the file can go straight to the printer
    without anyone opening Photoshop.

Needs tifffile:  pip3 install tifffile imagecodecs
"""

import numpy as np
from PIL import Image, ImageCms, ImageFilter

DPI = 300


def rgba_to_cmyk_spot(rgba, choke_px=2, white_floor=110):
    """
    Turn transparent RGBA artwork into the five planes the printer wants.

    Returns an (H, W, 5) uint8 array: C, M, Y, K, white-spot.
    """
    a = np.asarray(rgba)
    alpha = a[..., 3]

    # --- CMYK from RGB ----------------------------------------------------
    # A plain arithmetic conversion, not a profiled one. The RIP applies the
    # printer's own profile anyway, and a wrong profile here would be worse
    # than none. Matches how the sample file was built.
    rgb = a[..., :3].astype(np.float32) / 255.0
    k = 1.0 - rgb.max(axis=2)
    denom = np.clip(1.0 - k, 1e-6, None)
    c = (1.0 - rgb[..., 0] - k) / denom
    m = (1.0 - rgb[..., 1] - k) / denom
    y = (1.0 - rgb[..., 2] - k) / denom
    cmyk = np.clip(np.stack([c, m, y, k], axis=2), 0, 1) * 255.0

    # transparent areas carry no ink at all
    off = alpha < 8
    cmyk[off] = 0

    # --- white plate ------------------------------------------------------
    # Choked in from the colour edge so it cannot show as a halo when the
    # film and shirt are a fraction out of register.
    wm = Image.fromarray(alpha, "L")
    for _ in range(choke_px):
        wm = wm.filter(ImageFilter.MinFilter(3))
    w = np.asarray(wm).astype(np.float32)
    # partial coverage dithers the white and prints thin; anything meaningfully
    # inside gets the full plate
    w = np.where(w > white_floor, 255.0, w * 0.6)

    # stored INVERTED, as Photoshop does: 0 = full ink
    spot = 255.0 - w

    out = np.concatenate([cmyk, spot[..., None]], axis=2)
    return np.clip(out, 0, 255).astype(np.uint8)


def save_tiff(rgba, path, dpi=DPI, spot_name="White"):
    """Write the 5-channel TIFF."""
    import tifffile

    planes = rgba_to_cmyk_spot(rgba)
    tifffile.imwrite(
        path,
        planes,
        photometric="separated",       # CMYK
        extrasamples=("unspecified",),  # the 5th plane
        planarconfig="contig",
        compression="lzw",
        resolution=(dpi, dpi),
        resolutionunit="inch",
        metadata=None,
    )
    return path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        raise SystemExit("usage: python3 tiff_out.py artwork.png out.tif")
    im = Image.open(sys.argv[1]).convert("RGBA")
    save_tiff(im, sys.argv[2])
    print("wrote", sys.argv[2])
