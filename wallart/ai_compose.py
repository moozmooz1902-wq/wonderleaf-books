"""Finishing steps for generated images.

dictionary_page(art, seed) prints a black-ink engraving onto an antique
dictionary page: warm paper, two columns of real Webster's 1913 entries
(public domain), a running head and page number, with the art multiplied
over the text the way a real print on a book page looks.
"""
import random
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from render import font, RATIO

HERE = Path(__file__).resolve().parent
PAPER = (240, 231, 211)
TEXT = (92, 84, 72)


@lru_cache(maxsize=1)
def _entries():
    p = HERE / "assets" / "webster_excerpt.txt"
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else ["Lorem ipsum dolor sit amet."]


def _wrap(d, words, f, width):
    lines, cur = [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=f) > width and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def page_background(width, seed):
    W, H = int(width), int(width * RATIO)
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), PAPER)
    # faint foxing and uneven tone
    noise = Image.effect_noise((W // 8, H // 8), 18).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(W / 200))
    img = Image.blend(img, Image.merge("RGB", [noise.point(lambda v: 225 + v // 12)] * 3), 0.18)
    d = ImageDraw.Draw(img)
    m, gut = W * 0.07, W * 0.04
    colw = (W - 2 * m - gut) / 2
    body = font("CormorantGaramond.ttf", "Medium", W * 0.0165)
    head = font("CormorantGaramond.ttf", "Bold", W * 0.0165)
    entries = _entries()
    start = rnd.randrange(len(entries))
    top = H * 0.075
    d.text((m, H * 0.045), entries[start].split()[0].upper(), font=head, fill=TEXT, anchor="lm")
    d.text((W - m, H * 0.045), str(rnd.randint(40, 1680)), font=body, fill=TEXT, anchor="rm")
    d.line([(m, H * 0.058), (W - m, H * 0.058)], fill=TEXT, width=max(1, W // 900))
    lh = W * 0.0215
    i = start
    for c in range(2):
        x = m + c * (colw + gut)
        y = top
        while y < H * 0.95:
            e = entries[i % len(entries)]; i += 1
            word, rest = (e.split(" ", 1) + [""])[:2]
            lines = _wrap(d, (word.upper() + " " + rest).split(), body, colw)
            for k, line in enumerate(lines):
                if y > H * 0.95:
                    break
                if k == 0:
                    w0 = line.split(" ", 1)[0]
                    d.text((x, y), w0, font=head, fill=TEXT)
                    d.text((x + d.textlength(w0 + " ", font=head), y), line[len(w0) + 1:], font=body, fill=TEXT)
                else:
                    d.text((x + W * 0.012, y), line, font=body, fill=TEXT)
                y += lh
            y += lh * 0.3
    return img


def dictionary_page(art, seed, width=None):
    """Multiply a white-background engraving over a dictionary page."""
    W = int(width or art.width)
    page = page_background(W, seed)
    H = page.height
    # push the engraving's near-white background to pure white so the page shows through
    a = art.convert("RGB").point(lambda v: 255 if v > 214 else int(v * 255 / 214))
    s = min(W * 0.84 / a.width, H * 0.84 / a.height)
    a = a.resize((int(a.width * s), int(a.height * s)), Image.LANCZOS)
    layer = Image.new("RGB", page.size, (255, 255, 255))
    layer.paste(a, ((W - a.width) // 2, (H - a.height) // 2))
    return ImageChops.multiply(page, layer)
