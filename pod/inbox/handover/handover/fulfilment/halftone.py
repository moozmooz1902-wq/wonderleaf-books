"""
halftone.py — turn soft fades into printable dots.

WHY
    DTF cannot print semi-transparent ink. Worse, the adhesive powder needs a
    minimum dot size to grip: where a design fades out into fine sparse pixels
    the specks carry too little glue and either fail to transfer or peel after
    a wash. That is what "the smoky edges do not stick" means.

    Halftoning converts the fade into a pattern of SOLID dots that grow and
    shrink with the intended opacity. Each dot is large enough to hold powder,
    and from normal viewing distance the eye blends them back into a smooth
    gradient. Newspapers have done this for a century.

    It also removes the white halo: with no semi-transparent pixels left,
    nothing triggers a partial white underbase.

SETTINGS
    25-35 LPI at 300dpi is the range the DTF trade recommends. Lower LPI means
    larger dots, which transfer more reliably. 45 degrees is the standard
    single-colour screen angle, being the least visible to the eye.
"""

import numpy as np
from PIL import Image

DEFAULT_LPI = 28          # lines per inch
DEFAULT_ANGLE = 45.0      # degrees
DPI = 300

# The smallest dot that will reliably hold adhesive powder. Below roughly a
# quarter of a millimetre the specks carry too little glue: they either fail
# to transfer or come away in the wash, leaving a dusty speckle around the
# design. Anything that would print smaller than this is dropped instead.
MIN_DOT_MM = 0.25


def _threshold_map(shape, lpi=DEFAULT_LPI, angle=DEFAULT_ANGLE, dpi=DPI):
    """
    A tiled screen whose value rises from the centre of each cell outward.

    Comparing opacity against this map gives a dot that grows as opacity
    rises: at 20% only the cell centre passes, at 80% nearly the whole cell.
    """
    h, w = shape
    cell = dpi / float(lpi)          # pixels per halftone cell
    a = np.deg2rad(angle)

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # rotate into screen space so the dot grid sits at the chosen angle
    u = (xx * np.cos(a) + yy * np.sin(a)) / cell
    v = (-xx * np.sin(a) + yy * np.cos(a)) / cell

    fu = (u % 1.0) - 0.5
    fv = (v % 1.0) - 0.5
    # distance from the cell centre, normalised so a full cell reaches ~1.0
    d = np.sqrt(fu * fu + fv * fv) / 0.5
    return np.clip(d, 0, 1)


def min_opacity_for_dot(lpi=DEFAULT_LPI, dpi=DPI, min_mm=MIN_DOT_MM):
    """
    The lowest opacity worth printing at this screen ruling.

    Below it the dot would be smaller than MIN_DOT_MM and would not hold
    powder, so it is cleared rather than printed as dust.
    """
    cell = dpi / float(lpi)
    min_px = min_mm / 25.4 * dpi
    # radius = sqrt(opacity) * 1.128 * cell / 2, so invert for opacity
    return min(0.5, ((min_px / 2) / (1.128 * cell / 2)) ** 2)


def halftone_alpha(alpha, lpi=DEFAULT_LPI, angle=DEFAULT_ANGLE, dpi=DPI,
                   solid_above=0.92, clear_below=None):
    """
    Replace partial opacity with solid dots.

    alpha        : uint8 array
    solid_above  : opacity above this stays solid and untouched
    clear_below  : opacity below this is dropped — dots that small would not
                   hold powder anyway and print as dust around the design

    Returns a uint8 array containing only 0 and 255.
    """
    if clear_below is None:
        clear_below = min_opacity_for_dot(lpi, dpi)

    a = alpha.astype(np.float32) / 255.0
    screen = _threshold_map(a.shape, lpi, angle, dpi)

    out = np.zeros_like(a)
    out[a >= solid_above] = 1.0

    band = (a > clear_below) & (a < solid_above)
    # A dot forms where the intended opacity beats the screen at that point.
    #
    # The radius has to go as the SQUARE ROOT of the opacity, because a dot's
    # area grows with the square of its radius. Comparing opacity to distance
    # directly printed far too light — 83% opacity came out as 55% coverage.
    # The 1.128 factor is 1/sqrt(pi/4), which makes a full cell reach 100%.
    want = np.sqrt(a[band]) * 1.128
    out[band] = (want > screen[band]).astype(np.float32)

    return (out * 255).astype(np.uint8)


def apply(rgba, lpi=DEFAULT_LPI, angle=DEFAULT_ANGLE, dpi=DPI):
    """Halftone the alpha channel of an RGBA image."""
    arr = np.asarray(rgba).copy()
    arr[..., 3] = halftone_alpha(arr[..., 3], lpi, angle, dpi)
    return Image.fromarray(arr, "RGBA")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        raise SystemExit("usage: python3 halftone.py in.png out.png [lpi]")
    lpi = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_LPI
    im = Image.open(sys.argv[1]).convert("RGBA")
    apply(im, lpi=lpi).save(sys.argv[2])
    print(f"wrote {sys.argv[2]} at {lpi} LPI")
