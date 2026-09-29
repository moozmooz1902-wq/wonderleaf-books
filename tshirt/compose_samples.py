#!/usr/bin/env python3
"""Render each house look as transparent artwork and drop it on the real tee."""
from PIL import Image, ImageDraw
import styles, mockup

W, H = styles.W, styles.H
SAMPLES = styles.SAMPLES


def artwork(fn, lines, pal):
    """Draw a direction onto transparency and trim to what was actually drawn."""
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(canvas), lines, pal)
    bb = canvas.getbbox()
    return canvas.crop(bb) if bb else canvas


def sheet(sample_idx, path, blank):
    lines = SAMPLES[sample_idx]
    tiles = []
    for name, fn, pal in styles.DIRECTIONS:
        art = artwork(fn, lines, pal)
        tiles.append((name, mockup.place(art, blank)))
    tw = 820
    out = Image.new("RGB", (tw * len(tiles), tw + 70), (250, 250, 252))
    d = ImageDraw.Draw(out)
    lab = styles.font("grotesk", 30)
    for i, (name, im) in enumerate(tiles):
        im = im.resize((tw, tw), Image.LANCZOS)
        out.paste(im, (i * tw, 62))
        d.text((i * tw + 26, 20), name, font=lab, fill=(26, 26, 30))
        d.line([(i * tw, 0), (i * tw, tw + 70)], fill=(222, 222, 228), width=2)
    out.save(path)
    return path


if __name__ == "__main__":
    blank = Image.open(mockup.BLANK)
    for i in range(3):
        print(sheet(i, f"MOCKUP_SHEET_{i+1}.png", blank))
