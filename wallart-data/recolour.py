#!/usr/bin/env python3
"""The zero-GPU multiplier: one diffusion image, several colourways.

Why this is the whole cost argument. In gen/prompts.py the palette is a
generation axis, so a catalogue of N designs costs N GPU images. Palette is the
one axis that does not need the model: the composition, the subject and the
technique texture are identical between colourways, only the mapping from
lightness to colour changes. Doing it here instead costs about 25 ms of CPU and
cuts the GPU bill by the size of the palette axis - a factor of three.

The cap is not arbitrary. The wall-art branch measured store 1's 424k listings
as 89% near-duplicates and set the rule that a design may appear in at most
four colourways. Three is inside that rule, and is what Displate and Fy! do
with their own best sellers.

Method: build a lightness ramp through the palette's colours and look every
pixel's L up in it. Texture - paper grain, gouge marks, brush drag - survives
because it lives in L, which is what is being indexed, not replaced.
"""
import numpy as np
from PIL import Image

# the three measured colour strategies, as ramps from shadow to highlight
RAMPS = {
    "C1_complementary": ["#17313F", "#2E5A6B", "#C85A28", "#E2956A", "#F0E6D6"],
    "C2_warm_neutral":  ["#4A3A30", "#8A5A42", "#C8613A", "#CFC3AE", "#F3EDE2"],
    "C3_cool_sage":     ["#223129", "#466153", "#7E9C84", "#C3CFBE", "#EFF1E8"],
    "C4_ink_duotone":   ["#1B1B22", "#3A3E52", "#6F7490", "#B4B8C8", "#EDEEF3"],
}


def _hx(s):
    s = s.lstrip("#")
    return [int(s[i:i + 2], 16) for i in (0, 2, 4)]


def _lut(stops, n=256):
    """A 256x3 lookup table interpolated through the stop colours."""
    c = np.array([_hx(s) for s in stops], dtype=np.float32)
    x = np.linspace(0, len(c) - 1, n)
    i = np.clip(x.astype(int), 0, len(c) - 2)
    f = (x - i)[:, None]
    return (c[i] * (1 - f) + c[i + 1] * f).astype(np.uint8)


def recolour(img, ramp="C1_complementary", keep=0.18):
    """Map `img`'s lightness through the ramp. `keep` blends a little of the
    original hue back so the result is not a flat duotone poster."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    l = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])
    # stretch the lightness to the full range first, or a low-contrast panel
    # only ever touches the middle of the ramp and every colourway looks alike
    lo, hi = np.percentile(l, 1), np.percentile(l, 99)
    l = np.clip((l - lo) / max(hi - lo, 1e-3), 0, 1)
    out = _lut(RAMPS[ramp])[(l * 255).astype(np.uint8)].astype(np.float32)
    out = out * (1 - keep) + a * keep
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    import sys, os
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    im = Image.open(src)
    stem = os.path.splitext(os.path.basename(src))[0]
    for r in RAMPS:
        recolour(im, r).save(os.path.join(outdir, f"{stem}__{r}.png"))
        print(f"  {stem}__{r}.png")
