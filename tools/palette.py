"""Measure colours from a design image.

Colours are measured with Pillow rather than guessed by the model — hex
codes a model reads off an image are unreliable, pixel counts are not.
"""

from collections import Counter


# Transparent/near-white pixels are the shirt, not the design.
def extract_palette(path, max_colors=6, alpha_floor=40):
    from PIL import Image

    img = Image.open(path).convert("RGBA")
    img.thumbnail((200, 200))

    pixels = [p for p in img.getdata() if p[3] >= alpha_floor]
    if not pixels:
        return {"palette": [], "color_count": 0, "has_transparency": True}

    has_transparency = len(pixels) < (img.width * img.height) * 0.95

    # Quantise to reduce near-identical shades to one entry.
    def bucket(c):
        return tuple((v // 24) * 24 for v in c[:3])

    counts = Counter(bucket(p) for p in pixels)
    total = sum(counts.values())

    palette = []
    for rgb, n in counts.most_common(max_colors):
        share = n / total
        if share < 0.02:
            break
        palette.append({
            "hex": "#{:02x}{:02x}{:02x}".format(*rgb),
            "share": round(share, 3),
        })

    # Distinct colours carrying real area — the print-cost number.
    significant = sum(1 for rgb, n in counts.items() if n / total >= 0.03)

    return {
        "palette": palette,
        "color_count": significant,
        "has_transparency": has_transparency,
    }
