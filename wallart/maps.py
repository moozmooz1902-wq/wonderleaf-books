#!/usr/bin/env python3
"""Country map prints drawn from Natural Earth (public domain) outlines.

Styles
  solid     filled silhouette
  outline   thin outline only
  dots      halftone dot grid clipped to the country
  lines     horizontal stripe fill (retro)
  home      silhouette + heart on a city + "Home" / city name
  split     silhouette over a colour block with big country name

    python3 maps.py "Italy" --style home --city Rome --palette terracotta --out it.png
    python3 maps.py --list          countries available
"""
import argparse, json, math
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

from render import font, hexrgb, mix, measure, draw_tracked, ornament, RATIO
from styles import PALETTES, FONTSETS

GEO = Path(__file__).resolve().parent / "assets" / "geo"
SS = 3                                   # supersampling for smooth edges
SHORT = {"United States of America": "USA", "United Kingdom": "UK", "Dem. Rep. Congo": "DR Congo",
         "Central African Rep.": "Central African Republic", "Bosnia and Herz.": "Bosnia",
         "Dominican Rep.": "Dominican Republic", "Czechia": "Czech Republic"}
# "split" (solid colour block) is not generated any more - it uses too much ink
STYLES = ["outline", "dots", "lines", "solid", "home"]


@lru_cache(maxsize=1)
def countries():
    out = {}
    for f in ("countries_10m.geojson", "uk_nations.geojson"):
        for feat in json.load(open(GEO / f))["features"]:
            p = feat["properties"]
            name = p.get("SUBUNIT") if f.startswith("uk") else p["NAME"]
            g = feat["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            out[name] = [poly[0] for poly in polys]          # outer rings only
    return out


@lru_cache(maxsize=1)
def places():
    by = {}
    for feat in json.load(open(GEO / "places.geojson"))["features"]:
        p = feat["properties"]
        by.setdefault(p["adm0name"], []).append((p["name"], p["longitude"], p["latitude"], p["pop_max"]))
    for k in by:
        by[k].sort(key=lambda t: -t[3])
    return by


def ring_area(r):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1]))) / 2


def main_rings(rings):
    """Drop far-flung islands and overseas territories: keep rings that are
    reasonably large and close to the biggest one."""
    big = max(rings, key=ring_area)
    A = ring_area(big)
    bx = sum(p[0] for p in big) / len(big); by = sum(p[1] for p in big) / len(big)
    span = max(max(p[0] for p in big) - min(p[0] for p in big), max(p[1] for p in big) - min(p[1] for p in big), 1)
    keep = []
    for r in rings:
        cx = sum(p[0] for p in r) / len(r); cy = sum(p[1] for p in r) / len(r)
        if ring_area(r) >= A * 0.002 and math.hypot(cx - bx, cy - by) < span * 1.6:
            keep.append(r)
    return keep


def project(rings, box):
    """Equal-ish projection around the country's mid latitude, fitted into box."""
    lat0 = sum(p[1] for r in rings for p in r) / sum(len(r) for r in rings)
    k = math.cos(math.radians(lat0))
    pts = [[(x * k, -y) for x, y in r] for r in rings]
    xs = [p[0] for r in pts for p in r]; ys = [p[1] for r in pts for p in r]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    bx0, by0, bx1, by1 = box
    s = min((bx1 - bx0) / (x1 - x0), (by1 - by0) / (y1 - y0))
    ox = bx0 + ((bx1 - bx0) - (x1 - x0) * s) / 2
    oy = by0 + ((by1 - by0) - (y1 - y0) * s) / 2
    f = lambda x, y: (ox + (x * k - x0) * s, oy + (-y - y0) * s)
    return [[f(x, y) for x, y in r] for r in rings], f


def country_mask(poly_px, size):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for r in poly_px:
        if len(r) > 2:
            d.polygon(r, fill=255)
    return m


def render_map(country, style="solid", palette="bw", fonts="classic_serif", city=None,
               title=None, subtitle=None, width=1000):
    W, H = int(width), int(width * RATIO)
    _, bg, ink, acc = PALETTES[palette]
    bg, ink, acc = hexrgb(bg), hexrgb(ink), hexrgb(acc)
    fs = FONTSETS[fonts]
    rings = countries()[country]
    if country == "United States of America":          # mainland only, as sellers show it
        rings = [r for r in rings if min(p[0] for p in r) > -130 and min(p[1] for p in r) > 23]
    rings = main_rings(rings)

    S = SS
    big = (W * S, H * S)
    img = Image.new("RGB", big, bg)
    d = ImageDraw.Draw(img)
    m = W * S * 0.12
    top = H * S * (0.10 if style != "split" else 0.08)
    bottom = H * S * (0.70 if style != "split" else 0.58)
    poly, f = project(rings, (m, top, W * S - m, bottom))
    mask = country_mask(poly, big)

    if style == "split":
        d.rectangle([0, H * S * 0.66, W * S, H * S], fill=ink)
    if style in ("solid", "home", "split"):
        img.paste(Image.new("RGB", big, ink if style != "split" else acc), (0, 0), mask)
    elif style == "outline":
        for r in poly:
            d.line(r + r[:1], fill=ink, width=max(2, int(W * S * 0.004)), joint="curve")
    elif style == "dots":
        step = W * S / 70
        dots = Image.new("L", big, 0)
        dd = ImageDraw.Draw(dots)
        rad = step * 0.36
        y = 0.0
        while y < H * S:
            x = 0.0
            while x < W * S:
                dd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=255)
                x += step
            y += step
        img.paste(Image.new("RGB", big, ink), (0, 0), ImageChops.multiply(dots, mask))
    elif style == "lines":
        stripes = Image.new("L", big, 0)
        sd = ImageDraw.Draw(stripes)
        step = int(W * S / 90)
        for i, y in enumerate(range(0, H * S, step)):
            if i % 2 == 0:
                sd.rectangle([0, y, W * S, y + step * 0.55], fill=255)
        img.paste(Image.new("RGB", big, ink), (0, 0), ImageChops.multiply(stripes, mask))
        for r in poly:
            d.line(r + r[:1], fill=ink, width=max(2, int(W * S * 0.002)))

    if style == "home" and city:
        c = next((p for p in places().get(country, []) + places().get("United Kingdom", [])
                  if p[0].lower() == city.lower()), None)
        if c:
            x, y = f(c[1], c[2])
            ornament(d, "heart", x, y, W * S * 0.07, ink, acc if acc != ink else bg, ink)

    img = img.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img)

    # typography
    name = (title or SHORT.get(country, country)).upper()
    tf = font(fs[0], fs[1], 200)
    w, _, _ = measure(name, tf)
    size = min(200 * W * 0.76 / max(w, 1), W * 0.13)
    tf = font(fs[0], fs[1], size)
    tw, ttop, tbot = measure(name, tf, size * 0.08)
    ty = H * (0.76 if style != "split" else 0.72)
    colour = bg if style == "split" else ink
    draw_tracked(d, W / 2 - tw / 2, ty - ttop, name, tf, colour, size * 0.08)
    sub = subtitle or (city.upper() if (style == "home" and city) else None)
    if sub:
        sf = font(fs[3], fs[4], W * 0.03)
        sw, stop, _ = measure(sub, sf, W * 0.012)
        draw_tracked(d, W / 2 - sw / 2, ty + (tbot - ttop) + H * 0.025 - stop, sub, sf,
                     acc if style != "split" else bg, W * 0.012)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("country", nargs="?")
    ap.add_argument("--style", default="solid", choices=STYLES)
    ap.add_argument("--palette", default="bw")
    ap.add_argument("--fonts", default="classic_serif")
    ap.add_argument("--city")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--out", default="map.png")
    a = ap.parse_args()
    if a.list:
        print(len(countries()), sorted(countries()))
        return
    render_map(a.country, a.style, a.palette, a.fonts, a.city).save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
