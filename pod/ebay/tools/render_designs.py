#!/usr/bin/env python3
"""
Render slogan designs to print-ready PNGs for BLACK garments.

Wonderleaf sells on black tees only, so every design is light ink on a
transparent background - no colour separation problems, one file per design.

Layout is the STACKED LOCKUP observed on the competitor artwork: each line is
scaled individually so all lines share the same optical width, which makes the
block read as one solid shape in a 250px eBay thumbnail. The longest line is
promoted to the accent colour.

Output: 4500 x 5400 px, transparent PNG, sRGB - the standard POD print file.

Fonts: SIL Open Font Licence display faces (Anton, Bebas Neue, Oswald, Archivo
Black, Alfa Slab One, Staatliches, Press Start 2P). OFL permits commercial use
including merchandise. Point --fonts at the directory holding the .ttf files.

Usage:
    python3 render_designs.py --designs designs.json --fonts ./fonts --out ./art
    python3 render_designs.py --designs designs.json --fonts ./fonts --out ./art --limit 12 --preview
"""

import argparse, json, random, sys, zlib
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 4500, 5400
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 260, 420, 420
BOX_W = W - 2 * MARGIN_X
BOX_H = H - MARGIN_TOP - MARGIN_BOT

INK = (255, 255, 255)
ACCENTS = [(233, 196, 106), (231, 111, 81), (138, 177, 125),
           (129, 178, 214), (224, 122, 148), (255, 255, 255)]

# tone -> (emphasis face, supporting face)
PAIRINGS = {
    "wry":     ("Anton-Regular.ttf",       "Oswald.ttf"),
    "flat":    ("BebasNeue-Regular.ttf",   "Oswald.ttf"),
    "dark":    ("ArchivoBlack-Regular.ttf","Oswald.ttf"),
    "pun":     ("AlfaSlabOne-Regular.ttf", "Staatliches-Regular.ttf"),
    "sincere": ("Oswald.ttf",              "Oswald.ttf"),
    "warm":    ("Staatliches-Regular.ttf", "Oswald.ttf"),
    "visual":  ("Anton-Regular.ttf",       "Staatliches-Regular.ttf"),
}
FALLBACK = ("Anton-Regular.ttf", "Oswald.ttf")


@lru_cache(maxsize=4096)
def load_font(fonts_dir, name, size):
    """Cached: a binary search reloaded the same TTF ~10x per line otherwise."""
    p = Path(fonts_dir) / name
    if not p.exists():                       # graceful degradation
        p = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    return ImageFont.truetype(str(p), size)


REF_SIZE = 200


def fit_line(fonts_dir, face, text, target_w, max_size=900):
    """Size the text to fill target_w.

    Glyph advance is linear in point size, so measure once at a reference size
    and scale - then one correction step. That is 2 measurements instead of the
    ~10 a binary search needs, and it is the difference between rendering a
    catalogue in minutes and in hours.
    """
    ref = load_font(fonts_dir, face, REF_SIZE)
    bb = ref.getbbox(text)
    ref_w = bb[2] - bb[0]
    if ref_w <= 0:
        return REF_SIZE, ref
    size = max(8, min(max_size, int(REF_SIZE * target_w / ref_w)))
    f = load_font(fonts_dir, face, size)
    bb = f.getbbox(text)
    w = bb[2] - bb[0]
    if w > target_w and size > 8:            # correct any rounding overshoot
        size = max(8, int(size * target_w / w))
        f = load_font(fonts_dir, face, size)
    return size, f


# DTF will not print semi-transparent ink. The adhesive powder needs a dot of
# roughly half a millimetre to grip; anything finer sheds in the shaker and
# lifts off the shirt after a wash or two. At 300 dpi half a millimetre is
# about 6 px, so no speck and no hole may be smaller than that.
MIN_FEATURE_PX = 6


def distress(layer, seed, strength=0.30):
    """
    Knock speckled holes in the ink so it reads as a worn screen print,
    without leaving semi-transparent ink behind.

    This used to multiply the glyph alpha by a BLURRED GREYSCALE mask, which
    left most of the ink at partial alpha - on a measured sample only 42% of
    the inked pixels came out fully opaque. The RIP dithers a thin white
    underbase under everything below full alpha and the colour then lays down
    weak and patchy, which is exactly the "not enough opacity" complaint.

    The mask is now hard-thresholded to 0 or 255 and upsampled with NEAREST,
    so every speck is a whole number of MIN_FEATURE_PX blocks and the ink is
    either fully there or fully absent. Only the anti-aliased edge of the
    letterforms stays partial, and that is a pixel or two wide - which is
    normal for any print file and is what keeps the type from looking jagged.
    """
    # Built and blurred at 1/MIN_FEATURE_PX scale, THEN upsampled. Blurring a
    # 24-megapixel image was the single most expensive step in the renderer.
    sc = MIN_FEATURE_PX
    small = (Image.effect_noise((W // sc, H // sc), 44)
             .filter(ImageFilter.GaussianBlur(1)))

    # Take the cut from the noise's own histogram rather than from a fixed
    # number. A hard threshold at the old fixed value removed 55% of the
    # glyph - the soft mask only FADED those pixels, so the same number cuts
    # far more when it is binary. Working in percentage-of-holes keeps the
    # amount of wear the same whatever the noise or blur settings are.
    holes = strength * 0.45
    hist = small.histogram()
    target = holes * sum(hist)
    run = 0
    cut = 0
    for v, n in enumerate(hist):
        run += n
        if run >= target:
            cut = v
            break
    small = small.point(lambda v: 255 if v > cut else 0)
    # NEAREST, not BILINEAR: interpolating a binary mask reintroduces the
    # partial alpha this whole change exists to remove.
    mask = small.resize((W, H), Image.NEAREST)
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    return layer


def render(design, fonts_dir, distress_on=False):
    lines = design["art"]["lines"]
    emph = design["art"].get("emphasis_line", 0)
    emph_face, body_face = PAIRINGS.get(design.get("tone"), FALLBACK)

    # crc32, not hash(). Python randomises string hashing per process, so
    # hash() gave a design a different accent colour on every re-render - a
    # print file regenerated later would not match the photo the buyer bought
    # from. crc32 is stable across processes, machines and versions.
    seed = zlib.crc32(design["design_id"].encode()) % (2 ** 31)
    accent = ACCENTS[seed % len(ACCENTS)]

    # every line scaled to the same optical width - the stacked-lockup look
    fitted = []
    for i, ln in enumerate(lines):
        face = emph_face if i == emph else body_face
        size, font = fit_line(fonts_dir, face, ln.upper(), BOX_W)
        bb = font.getbbox(ln.upper())
        fitted.append({"text": ln.upper(), "font": font,
                       "w": bb[2] - bb[0], "h": bb[3] - bb[1],
                       "off": (bb[0], bb[1]), "accent": i == emph})

    # a single-line slogan scaled to full width is a thin strip lost on the chest.
    # Cap any one line's height so the stack keeps sane proportions.
    max_line_h = int(BOX_H * (0.55 if len(fitted) == 1 else 0.42))
    capped = []
    for f in fitted:
        if f["h"] > max_line_h:
            k = max_line_h / f["h"]
            face = emph_face if f["accent"] else body_face
            font = load_font(fonts_dir, face, max(8, int(f["font"].size * k)))
            bb = font.getbbox(f["text"])
            f = {**f, "font": font, "w": bb[2] - bb[0], "h": bb[3] - bb[1], "off": (bb[0], bb[1])}
        capped.append(f)
    fitted = capped

    gap = int(BOX_H * 0.035)
    total = sum(f["h"] for f in fitted) + gap * (len(fitted) - 1)
    if total > BOX_H:                        # too tall - shrink the whole stack
        k = BOX_H / total
        rescaled = []
        for f in fitted:
            new_size = max(8, int(f["font"].size * k))
            face = emph_face if f["accent"] else body_face
            font = load_font(fonts_dir, face, new_size)
            bb = font.getbbox(f["text"])
            rescaled.append({**f, "font": font, "w": bb[2] - bb[0],
                             "h": bb[3] - bb[1], "off": (bb[0], bb[1])})
        fitted = rescaled
        gap = int(gap * k)
        total = sum(f["h"] for f in fitted) + gap * (len(fitted) - 1)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = MARGIN_TOP + (BOX_H - total) // 2
    for f in fitted:
        x = (W - f["w"]) // 2
        d.text((x - f["off"][0], y - f["off"][1]), f["text"],
               font=f["font"], fill=(*(accent if f["accent"] else INK), 255))
        y += f["h"] + gap

    if distress_on:
        img = distress(img, seed)
    return img


def mockup(art, garment=(26, 26, 28), size=1200):
    """Flat-lay style preview: art composited on a plain garment-coloured square.

    Matches the competitor mockup convention (no model, garment fills the frame,
    plain background). Good enough to eyeball a design - not a substitute for a
    real product photo.
    """
    m = Image.new("RGB", (size, size), (245, 245, 245))
    tee = Image.new("RGB", (int(size * 0.78), int(size * 0.88)), garment)
    m.paste(tee, ((size - tee.width) // 2, (size - tee.height) // 2))
    a = art.copy()
    a.thumbnail((int(size * 0.60), int(size * 0.55)), Image.LANCZOS)
    m.paste(a, ((size - a.width) // 2, int(size * 0.22)), a)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--designs", required=True)
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--preview", action="store_true", help="also write a black-tee mockup JPEG")
    ap.add_argument("--contact-sheet", help="write a grid of the first 12 mockups here")
    # Solid by default. The distressed texture prints badly on DTF: even
    # made binary it is holes in the ink, and holes are where the powder has
    # nothing to grip. A design that cannot be made solid goes through
    # halftone.py instead, which is what that module is for.
    ap.add_argument("--distress", action="store_true",
                    help="add the worn-screen-print texture. Off by default: "
                         "solid ink is what DTF prints reliably")
    ap.add_argument("--no-distress", action="store_true",
                    help=argparse.SUPPRESS)   # kept so old commands still run
    ap.add_argument("--compress", type=int, default=6,
                    help="PNG compress_level 1-9. 6 is the size/speed sweet spot; "
                         "1 is ~2x faster and ~60%% larger.")
    a = ap.parse_args()

    designs = json.loads(Path(a.designs).read_text())
    if a.limit:
        designs = designs[:a.limit]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    sheet = []
    for i, dsg in enumerate(designs, 1):
        art = render(dsg, a.fonts, distress_on=a.distress)
        # optimize=True costs 3.9s vs 0.65s at level 6 for a 5% size saving.
        # At catalogue scale that is hours of wall-clock for nothing.
        art.save(out / f"{dsg['design_id']}.png", compress_level=a.compress)
        if a.preview or a.contact_sheet:
            mk = mockup(art)
            if a.preview:
                mk.save(out / f"{dsg['design_id']}_mockup.jpg", quality=88)
            if a.contact_sheet and len(sheet) < 12:
                sheet.append((mk, dsg["stem"]))
        if i % 250 == 0:
            print(f"  ... {i:,}/{len(designs):,}", file=sys.stderr)

    if a.contact_sheet and sheet:
        cols, cell = 4, 460
        rows = (len(sheet) + cols - 1) // cols
        cs = Image.new("RGB", (cols * cell, rows * cell), (255, 255, 255))
        for i, (mk, _) in enumerate(sheet):
            t = mk.resize((cell, cell), Image.LANCZOS)
            cs.paste(t, ((i % cols) * cell, (i // cols) * cell))
        cs.save(a.contact_sheet, quality=90)
        print(f"contact sheet -> {a.contact_sheet}")

    print(f"{len(designs):,} designs rendered -> {out}")


if __name__ == "__main__":
    main()
