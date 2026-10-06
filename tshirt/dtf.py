#!/usr/bin/env python3
"""Force generated artwork into something a DTF transfer can actually print.

Three things kill a DTF print, and the model produces all three however hard
the prompt argues otherwise:

  shading   - a gradient bands into stripes on transfer film
  hairlines - a stroke under ~2mm at print size does not transfer at all,
              it lifts off with the carrier sheet
  dark ink  - these shirts are BLACK, so a charcoal or dark-brown ink is
              invisible no matter how clean the print is

So nothing here trusts the prompt. The pixels are forced.
"""
from PIL import Image, ImageChops, ImageFilter, ImageStat
import colorsys

HARD = 128          # alpha cutoff: no semi-transparent pixel survives
MIN_V = 0.80        # every ink at least this bright, to read on black
MIN_S = 0.55
DROP_V = 0.22       # a neutral this dark is the shirt, not an ink        # and this saturated, unless it is a deliberate neutral
NEUTRAL_S = 0.18    # below this the ink is a grey - send it to off-white


def _hard_alpha(img):
    return img.getchannel("A").point(lambda v: 255 if v >= HARD else 0)


def despeckle(alpha, size=5):
    """Majority vote over a window: removes strokes and holes thinner than it.

    This is the step that decides whether a design is printable. An engraved
    lion's mane is thousands of 1px hairs; after this it is either a solid
    shape or it is gone. Either outcome prints; the hairs would not have.
    """
    return alpha.filter(ImageFilter.ModeFilter(size)).point(
        lambda v: 255 if v >= HARD else 0)


def deshade(rgb, size=7):
    """Collapse tonal variation into blocks before quantising.

    Quantising a smooth gradient straight away just picks four points along
    it and leaves banding. Mode-filtering first turns the gradient into
    plateaus, so the quantiser has flat regions to snap to.
    """
    return rgb.filter(ImageFilter.ModeFilter(size))


def plan_inks(pal, n):
    """Decide what each ink becomes on a BLACK shirt.

    Two rules, both of which exist because the garment is black:

    - A dark neutral ink is dropped to transparent. Printing black onto a
      black shirt costs film and powder and looks identical to printing
      nothing, so the shirt itself becomes that ink. This is also what gives
      the artwork its outlines for free.
    - Every surviving ink is pushed up in brightness and saturation, hue
      kept. The model returns sepia and charcoal whatever the prompt says,
      and sepia on black is invisible.

    Returns the new palette plus the set of indices to knock out.
    """
    out, drop = [], set()
    for i in range(n):
        r, g, b = [c / 255 for c in pal[i * 3:i * 3 + 3]]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        if v <= DROP_V and s < NEUTRAL_S:
            drop.add(i)
            out += [0, 0, 0]
            continue
        if s < NEUTRAL_S:
            s, v = 0.0, 0.95                 # grey -> off-white
        else:
            s = max(s, MIN_S)
            v = max(v, MIN_V)
        out += [int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, s, v)]
    return out + [0] * (768 - len(out)), drop


def _ink_palette(rgba, colours):
    """Pick the flat inks from the ARTWORK only, never the background.

    knockout() zeroes the RGB of the pixels it removes, so a straight
    quantise sees a million pixels of pure black and spends one of its four
    inks describing empty space - which left three badly-chosen inks for the
    design and was why the first flattened sample came out as blobs. So the
    opaque pixels are pulled out into a strip of their own, the palette is
    chosen from that, and only then is it applied to the whole canvas.
    """
    px = [p[:3] for p in rgba.getdata() if p[3] >= HARD]
    if not px:
        return None
    strip = Image.new("RGB", (len(px), 1))
    strip.putdata(px)
    return strip.quantize(colors=colours, method=Image.MEDIANCUT, dither=Image.NONE)


def border_inks(idx, alpha, colours, boxy=0.88, owns=0.45):
    """Strip a painted background panel, and nothing else.

    knockout() floods in from the paper and stops at the first hard colour
    change, so a lion the model set against a red square keeps the square.
    On a black shirt that prints as a visible rectangle, which is the worst
    thing a transfer can look like.

    Two earlier versions of this were too eager and ate the design itself.
    The reliable tell is not colour and not position but SHAPE: artwork that
    was drawn die-cut has a ragged silhouette, while artwork sitting on a
    panel has a silhouette that nearly fills its own bounding box. So the
    test only runs on a near-rectangular silhouette, and then removes the
    one ink that owns most of that rectangle's outline.
    """
    bbox = alpha.getbbox()
    if not bbox:
        return set()
    l, t, r, b = bbox
    area = (r - l) * (b - t)
    if not area or ImageStat.Stat(alpha).sum[0] / 255 / area < boxy:
        return set()                      # ragged silhouette: nothing to strip
    outline = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(5)))
    po, pi = outline.load(), idx.load()
    counts = [0] * colours
    for y in range(t, b):
        for x in range(l, r):
            if po[x, y]:
                counts[pi[x, y]] += 1
    total = sum(counts)
    if not total:
        return set()
    best = max(range(colours), key=lambda i: counts[i])
    return {best} if counts[best] / total > owns else set()


def flatten(img, colours=4, lift=True):
    """knockout() output in, printable flat-ink PNG out."""
    a = despeckle(_hard_alpha(img))
    ref = _ink_palette(img, colours)
    if ref is None:
        return img
    rgb = deshade(img.convert("RGB"))
    idx = rgb.quantize(palette=ref, dither=Image.NONE)
    if not lift:
        out = idx.convert("RGBA"); out.putalpha(a); return out
    # The lift happens AFTER the match, never before. Matching against the
    # lifted palette sends a black pixel to whichever bright ink happens to
    # sit nearest black, which scrambles the design; matching against the
    # true inks and then recolouring the palette keeps every region where
    # the model drew it.
    newpal, drop = plan_inks(ref.getpalette(), colours)
    drop |= border_inks(idx, a, colours)
    if drop:
        lut = [0 if i in drop else 255 for i in range(256)]
        a = ImageChops.multiply(a, idx.point(lut, mode="L"))
        a = a.point(lambda v: 255 if v >= HARD else 0)
    idx.putpalette(newpal)
    out = idx.convert("RGBA")
    out.putalpha(a)
    return out


def ink_coverage(img):
    """Share of the canvas that carries ink. Too little = a speck on a shirt."""
    a = img.getchannel("A")
    return ImageStat.Stat(a).mean[0] / 255


def edge_ratio(img):
    """Perimeter per unit area. High means spindly detail that will not print.

    Measured by eroding the alpha one step and counting what was lost. A
    solid shape loses its outline; a mane of hairs loses most of itself.
    """
    a = _hard_alpha(img)
    inner = a.filter(ImageFilter.MinFilter(3))
    area = ImageStat.Stat(a).sum[0]
    if area == 0:
        return 1.0
    return 1 - ImageStat.Stat(inner).sum[0] / area


def boxiness(img):
    """How close the silhouette is to a filled rectangle.

    A design that was drawn die-cut is ragged. One the model set on a
    painted panel is a block, and a block of ink on a black shirt reads as a
    sticker someone slapped on rather than a print.
    """
    a = _hard_alpha(img)
    bbox = a.getbbox()
    if not bbox:
        return 0.0
    l, t, r, b = bbox
    area = (r - l) * (b - t)
    return ImageStat.Stat(a).sum[0] / 255 / area if area else 0.0


def printable(img, min_cov=0.06, max_cov=0.75, max_edge=0.22, max_box=0.86):
    """Gate a design before it ever reaches a listing.

    Thresholds are loose on purpose: this catches the designs that are
    obviously unprintable, not every borderline one. Measured against a
    24-subject sample, it rejects about one in eight.
    """
    cov, edge, box = ink_coverage(img), edge_ratio(img), boxiness(img)
    if cov < min_cov:
        return False, f"too little ink ({cov:.1%})"
    if cov > max_cov:
        return False, f"covers the whole shirt ({cov:.1%})"
    if edge > max_edge:
        return False, f"too fine to transfer (edge {edge:.2f})"
    if box > max_box:
        return False, f"prints as a rectangle (fill {box:.2f})"
    return True, f"ok  ink {cov:.1%}  edge {edge:.2f}  fill {box:.2f}"


def snap(img, palette):
    """Force a composed, resampled design back to flat ink.

    Scaling artwork up to print size interpolates, and interpolation between
    two flat inks is a gradient - exactly what DTF cannot hold. The design is
    built and scaled first because that is what keeps the type sharp, then
    every pixel is snapped to the nearest colour it is allowed to be and the
    alpha is made binary again. Nothing in the finished print master is a
    tone between two inks.
    """
    cols = list(dict.fromkeys(tuple(c) for c in palette))[:256]
    ref = Image.new("P", (1, 1))
    flat = []
    for c in cols:
        flat += list(c)
    ref.putpalette(flat + [0] * (768 - len(flat)))
    a = _hard_alpha(img)
    out = img.convert("RGB").quantize(palette=ref, dither=Image.NONE).convert("RGBA")
    out.putalpha(a)
    return out
