"""
dtf.py — DTF conversion for painterly artwork on black.

WHY THIS REPLACES vectorise.py FOR GRAPHICS
    vectorise.py was written for flat, bright, text-based designs: knock out
    the background, quantise to a handful of flat colours, trace to vector,
    lift every dark pixel so nothing vanishes on a black shirt.

    Applied to dark painterly art it destroys the image. The corners are
    black, so most of the canvas reads as background; quantising collapses
    the gradients; lifting the blacks turns the whole thing white. That is
    exactly what happened — 40 shirts came out as white rectangles.

THE RIGHT APPROACH FOR THIS ART
    The artwork is ALREADY composed for a black shirt. Dark areas are meant
    to be dark — they become the garment. So:

        alpha  = derived from luminance (black -> transparent, bright -> opaque)
        colour = left exactly as generated
        no quantise, no vectorise, no black lifting

    That is what makes the reference designs work: the subject dissolves into
    the shirt because the dark parts of the artwork simply are not printed.

DTF NOTES
    A soft alpha ramp is correct here, not a hard cut. DTF handles partial
    opacity through the white underbase, and a hard threshold would produce
    a cut-out halo instead of the fade the whole look depends on.
"""

import numpy as np
from PIL import Image, ImageFilter

CANVAS_W, CANVAS_H = 3600, 4800
DPI = 300

# Luminance below this prints nothing — it becomes the shirt.
# A wide ramp (18 to 72) faded every edge over 54 levels of luminance, which
# is what made designs look soft on the sides. Narrowed to 14 levels: still
# anti-aliased so edges are not jagged, but the artwork ends where it ends
# instead of dissolving into the shirt.
BLACK_POINT = 27
# Luminance above this is fully opaque.
WHITE_POINT = 41
# Slight blur on the alpha only, to avoid stair-stepping on the ramp.
ALPHA_SMOOTH = 1.2

# --- vignette ---------------------------------------------------------------
# The model generates a square frame, and artwork that reaches the edges keeps
# a square footprint on the shirt — which reads as a printed box rather than a
# design. A soft radial falloff on the ALPHA (not the colour) fades the corners
# out so every design ends organically.
#
# Deliberately gentle: it only touches the outer region, so a subject that
# genuinely fills the frame is not cropped, it just stops having hard corners.
# The first attempt (0.62 / 1.02) faded the corners but left the mid-edges 88%
# opaque, so the square outline survived. These values fade the edges properly:
#   centre 1.00, mid-edge 0.42, corner 0.00
# A centred subject is untouched; only the frame dissolves.
VIGNETTE = True
VIGNETTE_START = 0.42
VIGNETTE_END = 0.94


# Artwork occupies this fraction of the print canvas. 0.94 filled the full
# 12in width, which spreads a 1024px source to ~93 DPI. 0.80 gives a ~9.6in
# print at ~110 DPI — sharper, and closer to how the reference tees are
# actually sized on the chest.
DEFAULT_MARGIN = 0.80


def to_dtf(src, dst, canvas=(CANVAS_W, CANVAS_H), margin=DEFAULT_MARGIN):
    """
    Convert a generated square image into a print-ready transparent PNG.

    Returns a dict of measurements for QC.
    """
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.float32)

    # --- normalise the black point ----------------------------------------
    # ROOT CAUSE of both the boxes and the high reject rate.
    #
    # SDXL cannot output transparency; every pixel gets a colour. Asking for
    # "pure black" gives a black RECTANGLE, which is fine — as long as it is
    # actually black. It usually is not: the refiner and the VAE lift it to
    # somewhere around 30-60, and "vibrant, high contrast" pushes it higher
    # still.
    #
    # That single fact produced both symptoms. The border check saw a bright
    # edge and rejected the design; the alpha threshold saw ink and printed
    # the rectangle. Every fix so far treated one symptom or the other.
    #
    # So: measure what the background actually sits at and subtract it, then
    # rescale so the artwork keeps its brightness. Background becomes true
    # black, the design is untouched, and both symptoms go with it.
    _l = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    _b = max(4, int(min(_l.shape) * 0.06))
    _edge = np.concatenate([_l[:_b, :].ravel(), _l[-_b:, :].ravel(),
                            _l[:, :_b].ravel(), _l[:, -_b:].ravel()])
    # the 60th percentile of the border: robust when artwork touches an edge,
    # since more than half the border is still background
    black = float(np.clip(np.percentile(_edge, 60), 0, 120))
    if black > 4:
        # rescale against the image's own peak, not 255, so the artwork keeps
        # the brightness it was generated with instead of being dimmed by the
        # amount of pedestal removed
        peak = float(np.percentile(a, 99.5))
        if peak > black + 20:
            a = np.clip((a - black) * (peak / (peak - black)), 0, 255)
            im = Image.fromarray(a.astype(np.uint8), "RGB")

    # Perceptual luminance — a blue glow and a yellow glow of the same
    # brightness should carry the same amount of ink.
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]

    # --- SOLID, BUT SHAPED BY THE ARTWORK ---------------------------------
    # Two failed approaches got us here, and both failure modes matter:
    #
    #   a wide luminance ramp (18-72) followed the artwork's own fade, so
    #   every design glowed out at the edges;
    #
    #   a threshold-and-fill mask gave hard edges but filled any enclosed
    #   region, so artwork spanning the frame became a solid BLOCK. That is
    #   where the boxes came from.
    #
    # The answer is a luminance ramp — which always follows the artwork's real
    # outline and can never make a box — but made STEEP. Below the floor there
    # is nothing, a few levels later it is fully opaque. Solid ink, organic
    # shape, no fill step.
    b = max(4, int(min(lum.shape) * 0.06))
    edge = np.concatenate([lum[:b, :].ravel(), lum[-b:, :].ravel(),
                           lum[:, :b].ravel(), lum[:, -b:].ravel()])
    floor = float(np.clip(np.percentile(edge, 88) + 3.0, 24, 60))

    # 8 levels from nothing to fully opaque: about 2px on a typical edge
    # 4 levels, not 8 — he asked for solid ink. DTF cannot hold a wispy
    # edge: adhesive powder needs enough ink to grip, so anything that fades
    # peels after a wash. A narrower ramp means a pixel is either printed or
    # not, with about one pixel of anti-aliasing so edges are not jagged.
    alpha = np.clip((lum - floor) / 4.0, 0, 1)
    # push everything meaningfully inside to fully opaque
    alpha = np.clip((alpha - 0.18) / 0.64, 0, 1)

    # --- drop a painted background panel, WITHOUT boxing the design ------
    # An earlier attempt cropped to the artwork's bounding box and multiplied
    # the alpha by that rectangle. That was self-defeating: a rectangle is a
    # box, so it replaced one square with a softer one, and it pushed the
    # reject rate up.
    #
    # The panel is a large area of NEARLY CONSTANT brightness. If one exists
    # above the border floor, lift the cut-off just above it. The panel then
    # falls below the threshold and disappears; the artwork, which is much
    # brighter, is untouched. The design keeps its own outline and ends with
    # black around it, instead of being cut to a shape.
    hist, edges = np.histogram(lum[lum > floor], bins=48, range=(floor, 255))
    if hist.sum() > 0:
        share = hist / hist.sum()
        # a flat panel shows up as one narrow band holding a lot of the frame
        for bi in range(len(share) - 1, -1, -1):
            if share[bi] > 0.22 and edges[bi] < 150:
                panel_top = float(edges[bi + 1])
                if panel_top > floor:
                    floor = min(panel_top + 4.0, 150.0)
                break

    # 4 levels, not 8 — he asked for solid ink. DTF cannot hold a wispy
    # edge: adhesive powder needs enough ink to grip, so anything that fades
    # peels after a wash. A narrower ramp means a pixel is either printed or
    # not, with about one pixel of anti-aliasing so edges are not jagged.
    alpha = np.clip((lum - floor) / 4.0, 0, 1)
    # push everything meaningfully inside to fully opaque
    alpha = np.clip((alpha - 0.18) / 0.64, 0, 1)

    # --- lift the colour ---------------------------------------------------
    # He wants strong colour on the garment, not washed out. DTF loses a
    # little saturation into the fabric, so a modest lift here lands closer
    # to what the mockup shows. Kept gentle — 1.12 is visible without going
    # cartoonish, and the clip stops anything blowing out.
    if SATURATION != 1.0:
        _g = a.mean(2, keepdims=True)
        a = np.clip(_g + (a - _g) * SATURATION, 0, 255)
        im = Image.fromarray(a.astype(np.uint8), "RGB")

    alpha_img = Image.fromarray((alpha * 255).astype(np.uint8), "L")

    rgba = Image.merge("RGBA", (*im.split(), alpha_img))

    # trim to the artwork, then place on the print canvas
    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)

    cw, ch = canvas
    s = min(cw * margin / rgba.width, ch * margin / rgba.height)
    rgba = rgba.resize((max(1, int(rgba.width * s)),
                        max(1, int(rgba.height * s))), Image.LANCZOS)

    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    out.alpha_composite(rgba, ((cw - rgba.width) // 2, (ch - rgba.height) // 2))
    out.save(dst, dpi=(DPI, DPI))

    # border measured on the corrected image
    _na = np.asarray(im).astype(np.float32)
    _nb = 0.2126 * _na[..., 0] + 0.7152 * _na[..., 1] + 0.0722 * _na[..., 2]
    _nk = max(4, int(min(_nb.shape) * 0.06))

    arr = np.asarray(out)
    op = arr[..., 3] > 200
    return {
        # Measured on the NORMALISED image, not the original file.
        #
        # This was the bug behind the reject rate. border_luma(src) re-opened
        # the source and measured the raw generation, so it saw the lifted
        # pedestal and rejected the design — even after that pedestal had
        # been removed and the background was true black. Two-thirds of the
        # batch was being thrown away for a fault that had already been
        # fixed a few lines earlier.
        "border": float(np.mean([_nb[:_nk, :].mean(), _nb[-_nk:, :].mean(),
                                 _nb[:, :_nk].mean(), _nb[:, -_nk:].mean()])),
        "coverage": float(op.mean()),
        "transparent": float((arr[..., 3] < 20).mean()),
        "mean_luma": float(arr[..., :3][op].mean()) if op.any() else 0.0,
        "colours": int(len(np.unique(
            arr[..., :3][op].reshape(-1, 3)[::37], axis=0))) if op.any() else 0,
    }


def border_luma(src, band=0.06):
    """
    Mean luminance of the outer border of the GENERATED image.

    This is the reliable test for a light background. Overall ink coverage is
    not: a design can be mostly dark and still sit on a pale ground, and a
    busy design can be bright without having a background at all. What matters
    is whether the edge of the frame is dark — if it is not, the knockout
    leaves a visible box on the shirt.
    """
    im = Image.open(src).convert("L")
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape
    b = max(2, int(min(h, w) * band))
    edge = np.concatenate([
        a[:b, :].ravel(), a[-b:, :].ravel(),
        a[:, :b].ravel(), a[:, -b:].ravel()])
    return float(edge.mean())


# Above this, the generation has a light background and will print as a box.
# Calibrated against real output: a design with decorative elements reaching
# into the corners scores around 58 and is still perfectly usable — it just
# reads as a square footprint rather than a clean fade. A genuine pale ground
# scores 200+. 75 separates the two without culling good work.
BORDER_MAX = 90

# Colour lift applied before printing. 1.0 is off. DTF loses a little
# saturation into the fabric, so a modest lift lands closer to the mockup.
SATURATION = 1.12


def qc(stats):
    """Flag designs that will not print well."""
    issues = []
    if stats["coverage"] < 0.02:
        issues.append("almost nothing to print")
    if stats.get("border", 0) > BORDER_MAX:
        issues.append(f"light background (border luma {stats['border']:.0f})")
    if stats["coverage"] > 0.55:
        issues.append("too much ink coverage")
    if stats["mean_luma"] < 55:
        issues.append("too dark to read on black")
    return issues


if __name__ == "__main__":
    import csv, glob, os, sys
    src = sys.argv[1] if len(sys.argv) > 1 else "raw"
    os.makedirs("print", exist_ok=True)

    rows, flagged = [], 0
    files = [f for f in sorted(os.listdir(src)) if f.lower().endswith(".png")]
    for i, fn in enumerate(files, 1):
        did = os.path.splitext(fn)[0]
        out = f"print/{did}.png"
        try:
            st = to_dtf(os.path.join(src, fn), out)
            iss = qc(st)
        except Exception as e:
            st, iss = {"coverage": 0, "transparent": 0, "mean_luma": 0,
                       "colours": 0}, [f"failed: {str(e)[:60]}"]
        if iss:
            flagged += 1
        rows.append({"design_id": did, "print_file": out,
                     "coverage": f"{st['coverage']:.3f}",
                     "mean_luma": f"{st['mean_luma']:.0f}",
                     "pass": "NO" if iss else "YES",
                     "issues": "; ".join(iss)})
        if i % 100 == 0:
            print(f"  {i}/{len(files)}", flush=True)

    if rows:
        with open("qc_report.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    print(f"\nprocessed {len(rows)} | passed {len(rows)-flagged} | "
          f"flagged {flagged}")
