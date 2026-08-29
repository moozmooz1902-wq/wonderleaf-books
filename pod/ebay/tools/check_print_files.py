#!/usr/bin/env python3
"""
Check that print files are DTF-safe before a batch is committed to.

    python3 check_print_files.py 'print/*.png'

DTF cannot print semi-transparent ink. Wherever alpha sits between 0 and 255
the RIP dithers a thin white underbase and the colour lays down weak - the
"not enough opacity" complaint. Anti-aliasing on the edge of a letterform is
unavoidable and fine; large interior areas of partial alpha are not.

It also checks the minimum feature size, because adhesive powder needs a dot
of roughly half a millimetre to grip. Finer specks shed in the shaker and
lift off the shirt after a wash.
"""

import glob, sys
import numpy as np
from PIL import Image

DPI = 300
MIN_MM = 0.4                       # smallest dot the powder reliably holds
MIN_PX = MIN_MM / 25.4 * DPI       # ~4.7 px at 300 dpi
SOLID_TARGET = 90.0                # % of inked pixels that must be full alpha


def solid_fraction(a):
    ink = a > 5
    if not ink.any():
        return 0.0, 0
    return (a[ink] > 250).mean() * 100, int(ink.sum())


def thin_features(a):
    """
    Fraction of ink sitting in runs narrower than the minimum dot.

    Measured as horizontal runs, which is enough to catch a mask that has
    been upsampled with interpolation or a hairline stroke.
    """
    soild = a > 128
    thin = total = 0
    step = max(1, a.shape[0] // 400)          # sample rows, not all 5400
    for row in soild[::step]:
        idx = np.flatnonzero(np.diff(np.concatenate(([0], row.view(np.int8),
                                                     [0]))))
        runs = idx[1::2] - idx[0::2]
        total += runs.sum()
        thin += runs[runs < MIN_PX].sum()
    return (thin / total * 100) if total else 0.0


def main():
    pats = sys.argv[1:] or ["*.png"]
    files = sorted(f for p in pats for f in glob.glob(p))
    if not files:
        print("no files matched")
        return 1

    print(f"  {len(files)} file(s). Fails below {SOLID_TARGET:.0f}% of the ink "
          f"fully opaque.\n  'thin' is how much sits in runs under {MIN_MM}mm "
          f"({MIN_PX:.1f}px at {DPI}dpi) - advisory only.\n")
    worst = []
    for f in files:
        im = Image.open(f)
        if im.mode != "RGBA":
            print(f"  [FAIL] {f}  mode is {im.mode}, not RGBA - no transparency")
            worst.append(f)
            continue
        a = np.asarray(im)[..., 3]
        solid, ink = solid_fraction(a)
        thin = thin_features(a)
        # Only opacity fails. The thin figure is advisory: a round halftone
        # dot has short chords at its top and bottom by geometry, so a few
        # per cent is unavoidable and does not mean the file is wrong.
        bad = solid < SOLID_TARGET
        tag = "[FAIL]" if bad else ("[WARN]" if thin > 8.0 else "[ OK ]")
        print(f"  {tag} {f.split('/')[-1]:<34} {solid:5.1f}% solid  "
              f"{thin:4.1f}% thin  {ink/1e6:.1f}M inked px")
        if bad:
            worst.append(f)

    print()
    if worst:
        print(f"  {len(worst)} of {len(files)} would print weak or peel on DTF")
        return 1
    print("  all files are DTF-safe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
