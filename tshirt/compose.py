#!/usr/bin/env python3
"""Put a real illustration above the slogan, in the listing's own colours.

Their data is the reason this exists and also the reason it is a minority
format: type-only designs averaged 10.53 units, type-with-picture 9.66, and
picture-only 6.08. So the catalogue stays mostly type, and the picture is
added only where there is a real illustration of the thing the listing is
already about - a motorcycle slogan gets the motorcycle.

The illustration is recoloured into the row's own palette rather than
dropped in as-is. That does two things at once: the picture stops clashing
with the type under it, and one drawing of a motorcycle becomes twelve
visibly different motorcycles, so 1,466 motorcycle listings do not all carry
the same picture. Near-duplication is the failure the wall-art branch blamed
for 424k listings not selling; it is not worth repeating here to save work.
"""
import colorsys
from PIL import Image

import styles2
from linebreak import break_lines

GAP       = 0.05     # space between picture and type, as a share of width
ILLUS_W   = 0.72     # picture width, as a share of the type block's width
MIN_H     = 0.60     # and its height, clamped against the type block's
MAX_H     = 1.60
MIN_LUM   = 70       # an ink darker than this is invisible on a black shirt


def _inks(img):
    """The flat colours actually used, commonest first."""
    px = [p[:3] for p in img.convert("RGBA").getdata() if p[3] >= 128]
    from collections import Counter
    return [c for c, _ in Counter(px).most_common()]


def _visible(c):
    """Lift one palette colour until it reads on black, keeping its hue.

    The palettes were written for type, where the deep tone is an outline or
    a shadow and never has to carry a shape on its own. An illustration's
    darkest ink does have to, so (62,46,102) - the violet palette's deep -
    comes out as a hole in the middle of the drawing. Same rule as
    dtf.plan_inks: hue kept, brightness and saturation floored.
    """
    r, g, b = [x / 255 for x in c]
    h, sat, v = colorsys.rgb_to_hsv(r, g, b)
    if 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2] >= MIN_LUM:
        return tuple(c)
    if sat < 0.18:
        sat, v = 0.0, 0.95
    else:
        sat, v = max(sat, 0.55), max(v, 0.80)
    return tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(h, sat, v))


def recolour_to(img, palette):
    """Map the illustration's flat inks onto the listing's palette.

    Both are short lists of flat colours, so this is a relabelling, not a
    filter - no blending, no new tones, nothing that would break the DTF
    rule that every ink is solid. Inks are matched light-to-light so the
    drawing keeps its internal contrast: whatever was the brightest part of
    the picture stays the brightest part.
    """
    img = img.convert("RGBA")
    src = _inks(img)
    if not src:
        return img
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    order = sorted(range(len(src)), key=lambda i: -lum(src[i]))
    tgt = sorted((_visible(c) for c in palette), key=lambda c: -lum(c))
    mapping = {}
    for rank, i in enumerate(order):
        mapping[src[i]] = tgt[min(rank, len(tgt) - 1)]
    out = Image.new("RGBA", img.size)
    out.putdata([(*mapping.get(p[:3], p[:3]), p[3]) if p[3] >= 128 else (0, 0, 0, 0)
                 for p in img.getdata()])
    return out


def _crop(img):
    bb = img.getbbox()
    return img.crop(bb) if bb else img


def stack(art, text):
    """Picture over type, both already cropped, centred on one canvas.

    The picture is sized off the type block's WIDTH, not its height. Sizing
    by height made a one-line slogan produce a postage stamp and a four-line
    one produce a poster; the width is stable, so the picture keeps a
    consistent presence whatever the slogan does.
    """
    W = max(text.width, 1)
    scale = (W * ILLUS_W) / max(art.width, 1)
    h = art.height * scale
    lo, hi = text.height * MIN_H, text.height * MAX_H
    if h < lo or h > hi:
        scale *= (lo if h < lo else hi) / h
    art = art.resize((max(1, int(art.width * scale)),
                      max(1, int(art.height * scale))), Image.LANCZOS)

    gap = int(W * GAP)
    out = Image.new("RGBA", (max(W, art.width), art.height + gap + text.height),
                    (0, 0, 0, 0))
    out.paste(art, ((out.width - art.width) // 2, 0), art)
    out.paste(text, ((out.width - text.width) // 2, art.height + gap), text)
    return _crop(out)


def compose(lines, illus, layout_i, pal_i, seed, worn=True):
    """Render the type, tint the picture to match it, and stack the two."""
    text = styles2.render(lines, layout_i, pal_i, seed=seed, worn=worn)
    art = _crop(recolour_to(illus, list(styles2.pal(pal_i)[1:])))
    return stack(art, text)


def design_for(row, illus_png, worn=True):
    """The artwork for one catalogue row that has an illustration to use."""
    return compose(break_lines(row["slogan"]), illus_png,
                   int(row.get("look") or 0), int(row.get("palette_idx") or 0),
                   seed=int(row["source_idx"]), worn=worn)
