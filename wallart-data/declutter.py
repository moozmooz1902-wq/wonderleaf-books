#!/usr/bin/env python3
"""Erase the fake artist's signature that FLUX scrawls along the bottom of a panel.

Found by looking at 129 real panels: the OCR gate in gen_gated.py catches
printed lettering - "SKYE", "LALE", "Ma2,2018" - but not a cursive signature,
because EasyOCR does not read a scribble as characters. Roughly one panel in
three carried one. It is both the clearest sign the work is generated and a
claim of authorship by a painter who does not exist, so it is the most
important defect left in the pipeline.

HOW, and why the obvious method fails. The first attempt estimated the
background by blurring and then only touched pixels sitting on "flat" ground.
Measured on the panels, that catches nothing: the signature contaminates its
own neighbourhood, so local spread where a signature sits came out at 53 and
18 against a threshold of 9. The test rejected exactly the pixels it existed
to find.

The right tool is a morphological top-hat. A grayscale CLOSING - dilate then
erode with a window wider than the stroke - removes thin DARK marks and
leaves everything else, so `closed - image` is large on a signature and near
zero everywhere else. An OPENING does the same for thin LIGHT marks. Neither
is fooled by the mark, because the mark is what the operator deletes.

Fur and grass are thin dark marks too, so a second test is needed: signatures
are SPARSE and LOCAL. The band is cut into tiles and a tile is only cleaned if
its marked pixels are a small minority. A tile full of fur is left alone.

The filters are separable running max/min in numpy, so a panel costs a few
tens of milliseconds, not the seconds PIL's MaxFilter would.
"""
import numpy as np
from PIL import Image

BAND = 0.22        # bottom share of the panel to inspect
K = 21             # window: wider than a signature stroke, narrower than real shapes
# A hard threshold leaves the anti-aliased edge of every stroke behind, so the
# signature comes out as a legible ghost rather than gone. The response is
# used as an alpha instead: fully replaced above HI, untouched below LO, and
# blended between. SOLID is the level at which a pixel counts as "a mark" for
# the tile sparsity test.
LO, SOLID, HI = 6.0, 16.0, 26.0
# Measured on five panels with a known signature, against a clean patch of
# the same band (mark density at SOLID):
#     flat ground   signature 0.13-0.83   clean 0.001-0.29
#     busy artwork  signature 0.49-0.52   clean 0.45-0.85
# So density alone cannot separate them - on a splattered or linocut ground
# the whole band reads as marks. What does separate them is the NEIGHBOURHOOD:
# a signature is a busy little patch sitting in quiet space, while fur, grass
# and gouge marks are busy patches surrounded by more of the same. Tiles are
# therefore small, and one is only cleaned when the tiles around it are quiet.
TILE = (8, 20)        # rows, cols: about 28 x 35 px each at 704x1008
MIN_DENSITY = 0.04    # there has to be something here
MAX_DENSITY = 0.75    # a solid black shape is not a signature
QUIET = 0.055         # and the ring of tiles around it has to be this empty
MIN_PIXELS = 12


def _roll_reduce(a, k, axis, op):
    r = k // 2
    pad = np.pad(a, [(r, r) if i == axis else (0, 0) for i in range(a.ndim)],
                 mode="edge")
    sl = [slice(None)] * a.ndim
    out = None
    for i in range(k):
        sl[axis] = slice(i, i + a.shape[axis])
        v = pad[tuple(sl)]
        out = v if out is None else op(out, v)
    return out


def _maxf(a, k):
    return _roll_reduce(_roll_reduce(a, k, 0, np.maximum), k, 1, np.maximum)


def _minf(a, k):
    return _roll_reduce(_roll_reduce(a, k, 0, np.minimum), k, 1, np.minimum)


def analyse(img, band=BAND, k=K):
    """Returns (hat, fill, band_array, y0). `fill` is the band with thin marks
    morphologically removed - the right colour to paint them out with."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    H = a.shape[0]
    y0 = int(H * (1 - band))
    sub = a[y0:]
    closed = _minf(_maxf(sub, k), k)      # thin DARK marks gone
    opened = _maxf(_minf(sub, k), k)      # thin LIGHT marks gone
    dark = (closed - sub).max(axis=2)
    light = (sub - opened).max(axis=2)
    darker = dark >= light
    hat = np.where(darker, dark, light)
    fill = np.where(darker[..., None], closed, opened)
    return hat, fill, sub, y0


def strip_marks(img, band=BAND, k=K, tile=TILE, quiet=QUIET):
    """Returns (cleaned image, share of the band painted out)."""
    hat, fill, sub, y0 = analyse(img, band, k)
    mask = hat >= SOLID
    h, w = mask.shape
    rows, cols = tile
    ry = [slice(r * h // rows, (r + 1) * h // rows) for r in range(rows)]
    rx = [slice(c * w // cols, (c + 1) * w // cols) for c in range(cols)]
    dens = np.array([[mask[y, x].mean() for x in rx] for y in ry])
    cnt = np.array([[mask[y, x].sum() for x in rx] for y in ry])

    pad = np.pad(dens, 1, mode="edge")
    ring = np.stack([pad[i:i + rows, j:j + cols]
                     for i in range(3) for j in range(3) if (i, j) != (1, 1)])
    # the quietest two thirds of the ring: a signature often touches the
    # subject on one side, and one busy neighbour should not disqualify it
    calm = np.sort(ring, axis=0)[:5].mean(axis=0)

    keep = np.zeros_like(mask)
    for r in range(rows):
        for c in range(cols):
            if (cnt[r, c] >= MIN_PIXELS and MIN_DENSITY <= dens[r, c] <= MAX_DENSITY
                    and calm[r, c] <= quiet):
                keep[ry[r], rx[c]] = mask[ry[r], rx[c]]
    frac = float(keep.mean())
    if frac == 0:
        return img, 0.0
    # reach out from every solid mark so the faint tail of the stroke is
    # inside the region we are allowed to touch
    region = keep.copy()
    for _ in range(3):
        g = region.copy()
        g[1:] |= region[:-1]; g[:-1] |= region[1:]
        g[:, 1:] |= region[:, :-1]; g[:, :-1] |= region[:, 1:]
        region = g
    alpha = np.clip((hat - LO) / (HI - LO), 0.0, 1.0) * region
    out = np.asarray(img.convert("RGB"), dtype=np.float32).copy()
    a3 = alpha[..., None]
    out[y0:] = sub * (1 - a3) + fill * a3
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), frac


if __name__ == "__main__":
    import sys, glob, os, time
    files = sorted(glob.glob(sys.argv[1] + "/*.jpg"))
    outdir = sys.argv[2] if len(sys.argv) > 2 else None
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    t0 = time.time(); hit = 0; fr = []
    for f in files:
        cleaned, frac = strip_marks(Image.open(f))
        if frac > 0:
            hit += 1; fr.append(frac)
        if outdir:
            cleaned.save(os.path.join(outdir, os.path.basename(f)), "JPEG", quality=92)
    el = time.time() - t0
    print(f"{len(files)} panels: {hit} had marks painted out "
          f"(median {np.median(fr)*100:.2f}% of the band, max {max(fr)*100:.2f}%)   "
          f"{el/len(files)*1000:.0f} ms each")
