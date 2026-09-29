#!/usr/bin/env python3
"""Educational wall charts, drawn in code - the best-selling image prints on
eBay UK (times tables 5,000+ sold, alphabet ~3,000, number square ~2,600,
periodic table ~1,700; see research/IMAGE_DEMAND.md).

Low ink: white paper, coloured text and thin outlines, pale tints only.
Resolution independent: every size is a fraction of the width.

    python3 charts.py --sheet sheet.png
    python3 charts.py times_table --variant 7 --palette rainbow --out t7.png
"""
import argparse, math
from PIL import Image, ImageDraw

from render import font, hexrgb, mix, measure, ornament, RATIO
from styles import PALETTES, FONTSETS, RAINBOW

KIDS_COLOURS = RAINBOW + ["#E76F51", "#2A9D8F"]

CHARTS = {
    "times_table": dict(name="{v} Times Table", keywords="Times Table Maths Poster", variants=[str(i) for i in range(1, 13)]),
    "times_tables_all": dict(name="Times Tables 1-12", keywords="Times Tables Chart Maths Poster", variants=[""]),
    "multiplication_square": dict(name="Multiplication Square", keywords="Times Tables Grid Maths Poster", variants=[""]),
    "number_square": dict(name="Number Square 1-100", keywords="Hundred Square Maths Poster", variants=[""]),
    "counting_1_20": dict(name="Counting 1 to 20", keywords="Numbers Chart Early Years Poster", variants=[""]),
    "alphabet": dict(name="Alphabet", keywords="ABC Alphabet Chart Poster", variants=["upper", "upper_lower"]),
    "shapes": dict(name="2D Shapes", keywords="Shapes Chart Maths Poster", variants=[""]),
    "colours": dict(name="Colours", keywords="Colours Chart Early Years Poster", variants=[""]),
    "days_of_week": dict(name="Days of the Week", keywords="Days Chart Classroom Poster", variants=[""]),
    "months_of_year": dict(name="Months of the Year", keywords="Months Chart Classroom Poster", variants=[""]),
    "telling_time": dict(name="Telling the Time", keywords="Clock Time Chart Maths Poster", variants=[""]),
    "planets": dict(name="The Solar System", keywords="Planets Space Chart Poster", variants=[""]),
    "feelings": dict(name="How Are You Feeling?", keywords="Feelings Emotions Chart Poster", variants=[""]),
    "roman_numerals": dict(name="Roman Numerals", keywords="Roman Numerals Chart Maths Poster", variants=[""]),
    "number_bonds": dict(name="Number Bonds to {v}", keywords="Number Bonds Maths Poster", variants=["10", "20"]),
    "compass": dict(name="Compass Points", keywords="Compass Geography Chart Poster", variants=[""]),
    "periodic_table": dict(name="Periodic Table of Elements", keywords="Periodic Table Science Chart Poster", variants=[""]),
}

WORDS = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                 "apple ball cat dog egg fish goat hat igloo jam kite lion moon nest owl pig queen rain sun tree umbrella van web fox yo-yo zebra".split()))


def all_specs():
    return [(c, v) for c, m in CHARTS.items() for v in m["variants"]]


def chart_title(chart_id, variant):
    return CHARTS[chart_id]["name"].replace("{v}", variant)


class Chart:
    def __init__(self, palette, fonts, width):
        self.W, self.H = int(width), int(width * RATIO)
        _, bg, ink, acc = PALETTES[palette]
        self.bg, self.ink, self.acc = hexrgb(bg), hexrgb(ink), hexrgb(acc)
        self.rainbow = palette in ("rainbow", "pastel")
        self.fs = FONTSETS[fonts]
        self.img = Image.new("RGB", (self.W, self.H), self.bg)
        self.d = ImageDraw.Draw(self.img)
        self.lw = max(2, int(self.W * 0.0028))

    def col(self, i):
        """Colour for item i: cycles bright colours on kids palettes, else accent/ink."""
        if self.rainbow:
            return hexrgb(KIDS_COLOURS[i % len(KIDS_COLOURS)])
        return self.acc if i % 2 else self.ink

    def f(self, size, role="main"):
        f0, v0, f1, f2, v2 = self.fs
        return font(f0, v0, size) if role == "main" else font(f2, v2, size)

    def text(self, xy, s, size, fill, role="main", anchor="mm"):
        self.d.text(xy, s, font=self.f(size, role), fill=fill, anchor=anchor)

    def fit(self, s, size, maxw, role="main"):
        w, _, _ = measure(s, self.f(size, role))
        return size if w <= maxw else size * maxw / w

    def title(self, s):
        W = self.W
        size = self.fit(s, W * 0.085, W * 0.84)
        self.text((W / 2, W * 0.1), s, size, self.ink)
        self.d.line([(W * 0.3, W * 0.165), (W * 0.7, W * 0.165)], fill=self.acc, width=self.lw)
        return W * 0.2                                   # content starts here

    def cell(self, x0, y0, x1, y1, colour, tint=0.0, r=None):
        r = r if r is not None else (x1 - x0) * 0.12
        fill = mix(self.bg, colour, tint) if tint else None
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=colour, width=self.lw, fill=fill)

    def grid(self, cols, rows, top, bottom=None, margin=0.07, gap=0.012):
        W, H = self.W, self.H
        bottom = bottom or H * 0.95
        m, g = W * margin, W * gap
        cw = (W - 2 * m - (cols - 1) * g) / cols
        ch = (bottom - top - (rows - 1) * g) / rows
        for i in range(cols * rows):
            c, r = i % cols, i // cols
            x0 = m + c * (cw + g); y0 = top + r * (ch + g)
            yield i, x0, y0, x0 + cw, y0 + ch


# --------------------------------------------------------------- chart drawers

def times_table(C, v):
    n = int(v)
    top = C.title(f"{n} Times Table")
    rows = 12
    h = (C.H * 0.94 - top) / rows
    size = h * 0.55
    for i in range(1, rows + 1):
        y = top + (i - 0.5) * h
        col = C.col(i - 1)
        C.d.rounded_rectangle([C.W * 0.12, y - h * 0.42, C.W * 0.88, y + h * 0.42], radius=h * 0.2,
                              outline=mix(C.bg, col, 0.55), width=max(1, C.lw // 2))
        for x, s in ((0.24, str(i)), (0.36, "×"), (0.48, str(n)), (0.6, "="), (0.76, str(i * n))):
            C.text((C.W * x, y), s, size, col if s not in "×=" else C.ink)


def times_tables_all(C, v):
    top = C.title("Times Tables")
    for i, x0, y0, x1, y1 in C.grid(3, 4, top):
        n = i + 1
        col = C.col(i)
        C.cell(x0, y0, x1, y1, col)
        C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.09), f"{n} ×", (y1 - y0) * 0.1, col)
        lh = (y1 - y0) * 0.8 / 12
        for k in range(1, 13):
            C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.19 + (k - 0.5) * lh), f"{k} × {n} = {k * n}", lh * 0.72, C.ink, "small")


def multiplication_square(C, v):
    top = C.title("Multiplication Square")
    for i, x0, y0, x1, y1 in C.grid(13, 13, top, C.H * 0.9, margin=0.05, gap=0.004):
        r, c = divmod(i, 13)
        if r == 0 and c == 0:
            C.text(((x0 + x1) / 2, (y0 + y1) / 2), "×", (y1 - y0) * 0.5, C.ink)
            continue
        head = r == 0 or c == 0
        col = C.col(max(r, c) - 1)
        C.cell(x0, y0, x1, y1, col if head else mix(C.bg, C.ink, 0.25), tint=0.12 if head else 0, r=(x1 - x0) * 0.1)
        val = c if r == 0 else r if c == 0 else r * c
        C.text(((x0 + x1) / 2, (y0 + y1) / 2), str(val), (y1 - y0) * (0.42 if head else 0.36), col if head else C.ink,
               "main" if head else "small")


def number_square(C, v):
    top = C.title("Number Square")
    for i, x0, y0, x1, y1 in C.grid(10, 10, top, C.H * 0.9, margin=0.06, gap=0.006):
        col = C.col(i // 10)
        C.cell(x0, y0, x1, y1, col, tint=0.06 if (i + 1) % 10 == 0 else 0)
        C.text(((x0 + x1) / 2, (y0 + y1) / 2), str(i + 1), (y1 - y0) * 0.42, col)


def counting_1_20(C, v):
    top = C.title("Counting 1 to 20")
    for i, x0, y0, x1, y1 in C.grid(4, 5, top):
        n, col = i + 1, C.col(i)
        C.cell(x0, y0, x1, y1, col)
        C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.24), str(n), (y1 - y0) * 0.32, col)
        # dots in rows of 5 underneath
        w = x1 - x0
        dx = w * 0.8 / 5
        rows = math.ceil(n / 5)
        dy = min(dx, (y1 - y0) * 0.46 / 4)
        oy = y0 + (y1 - y0) * 0.47 + (4 - rows) * dy / 2
        rr = min(dx, dy) * 0.32
        for k in range(n):
            cx = x0 + w * 0.1 + (k % 5 + 0.5) * dx
            cy = oy + (k // 5 + 0.5) * dy
            C.d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)


def alphabet(C, v):
    top = C.title("Alphabet")
    for i, x0, y0, x1, y1 in C.grid(5, 6, top):
        if i >= 26:
            break
        L = chr(65 + i)
        col = C.col(i)
        C.cell(x0, y0, x1, y1, col)
        s = L if v == "upper" else L + L.lower()
        C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.42), s, (y1 - y0) * 0.46, col)
        C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.82), WORDS[L], C.fit(WORDS[L], (y1 - y0) * 0.14, (x1 - x0) * 0.85, "small"),
               C.ink, "small")


def _shape(d, name, cx, cy, r, col, lw):
    def poly(n, rot=-math.pi / 2, rr=r):
        return [(cx + rr * math.cos(rot + 2 * math.pi * k / n), cy + rr * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]
    if name == "circle": d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=lw)
    elif name == "oval": d.ellipse([cx - r, cy - r * 0.65, cx + r, cy + r * 0.65], outline=col, width=lw)
    elif name == "triangle": d.polygon(poly(3, rr=r * 1.1), outline=col, width=lw)
    elif name == "square": d.rectangle([cx - r * 0.85, cy - r * 0.85, cx + r * 0.85, cy + r * 0.85], outline=col, width=lw)
    elif name == "rectangle": d.rectangle([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], outline=col, width=lw)
    elif name == "pentagon": d.polygon(poly(5), outline=col, width=lw)
    elif name == "hexagon": d.polygon(poly(6), outline=col, width=lw)
    elif name == "octagon": d.polygon(poly(8, rot=math.pi / 8), outline=col, width=lw)
    elif name == "star":
        pts = [(cx + (r if k % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + math.pi * k / 5),
                cy + (r if k % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + math.pi * k / 5)) for k in range(10)]
        d.polygon(pts, outline=col, width=lw)
    elif name == "heart":
        pts = [(cx + r * 16 * math.sin(t) ** 3 / 17, cy - r * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17)
               for t in [2 * math.pi * k / 80 for k in range(80)]]
        d.polygon(pts, outline=col, width=lw)
    elif name == "diamond": d.polygon([(cx, cy - r), (cx + r * 0.7, cy), (cx, cy + r), (cx - r * 0.7, cy)], outline=col, width=lw)
    elif name == "semicircle":
        d.arc([cx - r, cy - r * 0.6, cx + r, cy + r * 1.4], 180, 360, fill=col, width=lw)
        d.line([(cx - r, cy + r * 0.4), (cx + r, cy + r * 0.4)], fill=col, width=lw)
    elif name == "crescent":
        d.arc([cx - r, cy - r, cx + r, cy + r], 40, 320, fill=col, width=lw)
        d.arc([cx - r * 0.45, cy - r * 0.8, cx + r * 1.15, cy + r * 0.8], 95, 265, fill=col, width=lw)
    elif name == "trapezium": d.polygon([(cx - r * 0.55, cy - r * 0.6), (cx + r * 0.55, cy - r * 0.6), (cx + r, cy + r * 0.6), (cx - r, cy + r * 0.6)], outline=col, width=lw)
    elif name == "parallelogram": d.polygon([(cx - r * 0.6, cy - r * 0.6), (cx + r, cy - r * 0.6), (cx + r * 0.6, cy + r * 0.6), (cx - r, cy + r * 0.6)], outline=col, width=lw)


SHAPES = ["circle", "oval", "triangle", "square", "rectangle", "pentagon", "hexagon", "octagon",
          "star", "heart", "diamond", "semicircle", "crescent", "trapezium", "parallelogram"]


def shapes(C, v):
    top = C.title("2D Shapes")
    for i, x0, y0, x1, y1 in C.grid(3, 5, top):
        name, col = SHAPES[i], C.col(i)
        r = min(x1 - x0, y1 - y0) * 0.3
        _shape(C.d, name, (x0 + x1) / 2, y0 + (y1 - y0) * 0.42, r, col, C.lw * 2)
        C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.86), name, C.fit(name, (y1 - y0) * 0.13, (x1 - x0) * 0.9), C.ink)


COLOURS = [("red", "#D62828"), ("orange", "#F77F00"), ("yellow", "#FCBF49"), ("green", "#2A9D8F"), ("blue", "#1D4ED8"),
           ("purple", "#7B2CBF"), ("pink", "#F472B6"), ("brown", "#8B5E34"), ("black", "#111111"), ("white", "#FFFFFF"),
           ("grey", "#9CA3AF"), ("gold", "#C9A227")]


def colours(C, v):
    top = C.title("Colours")
    for i, x0, y0, x1, y1 in C.grid(3, 4, top):
        name, hx = COLOURS[i]
        c = hexrgb(hx)
        r = min(x1 - x0, y1 - y0) * 0.26
        cx, cy = (x0 + x1) / 2, y0 + (y1 - y0) * 0.4
        C.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c, outline=C.ink if name == "white" else c, width=C.lw)
        C.text((cx, y0 + (y1 - y0) * 0.85), name, (y1 - y0) * 0.14, c if name not in ("white", "yellow") else C.ink)


def _list_chart(C, title, items, sub=None):
    top = C.title(title)
    n = len(items)
    h = (C.H * 0.94 - top) / n
    for i, s in enumerate(items):
        y = top + (i + 0.5) * h
        col = C.col(i)
        C.d.rounded_rectangle([C.W * 0.1, y - h * 0.4, C.W * 0.9, y + h * 0.4], radius=h * 0.3, outline=col, width=C.lw)
        C.text((C.W * 0.5 if not sub else C.W * 0.42, y), s, C.fit(s, h * 0.5, C.W * 0.6), col)
        if sub:
            C.text((C.W * 0.8, y), sub[i], h * 0.32, C.ink, "small")


def days_of_week(C, v):
    _list_chart(C, "Days of the Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])


def months_of_year(C, v):
    m = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    days = ["31 days", "28 or 29", "31 days", "30 days", "31 days", "30 days", "31 days", "31 days", "30 days", "31 days", "30 days", "31 days"]
    _list_chart(C, "Months of the Year", m, days)


def _clock(C, cx, cy, r, hour, minute, col, numbers=True):
    d = C.d
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=C.lw * 2)
    for k in range(60):
        a = math.pi * 2 * k / 60 - math.pi / 2
        r0 = r * (0.86 if k % 5 == 0 else 0.92)
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r * 0.97 * math.cos(a), cy + r * 0.97 * math.sin(a))],
               fill=C.ink, width=max(1, C.lw if k % 5 == 0 else C.lw // 2))
    if numbers:
        for h in range(1, 13):
            a = math.pi * 2 * h / 12 - math.pi / 2
            C.text((cx + r * 0.72 * math.cos(a), cy + r * 0.72 * math.sin(a)), str(h), r * 0.16, C.col(h))
    ah = math.pi * 2 * ((hour % 12) + minute / 60) / 12 - math.pi / 2
    am = math.pi * 2 * minute / 60 - math.pi / 2
    d.line([(cx, cy), (cx + r * 0.45 * math.cos(ah), cy + r * 0.45 * math.sin(ah))], fill=C.ink, width=C.lw * 3)
    d.line([(cx, cy), (cx + r * 0.72 * math.cos(am), cy + r * 0.72 * math.sin(am))], fill=col, width=C.lw * 2)
    d.ellipse([cx - r * 0.04, cy - r * 0.04, cx + r * 0.04, cy + r * 0.04], fill=C.ink)


def telling_time(C, v):
    top = C.title("Telling the Time")
    W, H = C.W, C.H
    _clock(C, W / 2, top + W * 0.3, W * 0.27, 10, 10, C.acc if not C.rainbow else hexrgb(RAINBOW[3]))
    labels = [("o'clock", 3, 0), ("quarter past", 3, 15), ("half past", 3, 30), ("quarter to", 3, 45)]
    y = top + W * 0.72
    for i, (lab, h, m) in enumerate(labels):
        cx = W * (0.14 + i * 0.24)
        col = C.col(i)
        _clock(C, cx, y + W * 0.1, W * 0.09, h, m, col, numbers=False)
        C.text((cx, y + W * 0.25), lab, C.fit(lab, W * 0.033, W * 0.22), col)


PLANETS = [("Mercury", 0.25, "closest to the Sun"), ("Venus", 0.42, "the hottest planet"), ("Earth", 0.44, "our home"),
           ("Mars", 0.33, "the red planet"), ("Jupiter", 1.0, "the biggest planet"), ("Saturn", 0.85, "famous rings"),
           ("Uranus", 0.6, "spins on its side"), ("Neptune", 0.58, "the windiest planet")]


def planets(C, v):
    top = C.title("The Solar System")
    W, H = C.W, C.H
    sun_r = W * 0.1
    C.d.ellipse([W / 2 - sun_r, top + W * 0.02, W / 2 + sun_r, top + W * 0.02 + 2 * sun_r], outline=hexrgb("#F59E0B"), width=C.lw * 2,
                fill=mix(C.bg, hexrgb("#FCD34D"), 0.35))
    C.text((W / 2, top + W * 0.02 + sun_r), "Sun", sun_r * 0.4, C.ink)
    y0 = top + W * 0.28
    h = (H * 0.95 - y0) / 8
    for i, (name, size, fact) in enumerate(PLANETS):
        y = y0 + (i + 0.5) * h
        col = C.col(i)
        r = h * (0.18 + 0.24 * size)
        C.d.ellipse([W * 0.2 - r, y - r, W * 0.2 + r, y + r], outline=col, width=C.lw * 2, fill=mix(C.bg, col, 0.12))
        if name == "Saturn":
            C.d.ellipse([W * 0.2 - r * 1.6, y - r * 0.35, W * 0.2 + r * 1.6, y + r * 0.35], outline=col, width=C.lw)
        C.text((W * 0.4, y - h * 0.14), name, h * 0.4, col, anchor="lm")
        C.text((W * 0.4, y + h * 0.26), fact, h * 0.24, C.ink, "small", anchor="lm")
    C.text((W * 0.9, H * 0.975), "sizes not to scale", W * 0.016, C.ink, "small", anchor="rm")


FEELINGS = ["happy", "sad", "angry", "worried", "surprised", "tired", "excited", "calm", "scared", "silly", "proud", "shy"]


def _face(d, name, cx, cy, r, col, lw):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=lw * 2)
    ey, ex, er = cy - r * 0.2, r * 0.35, r * 0.09
    for sx in (-1, 1):
        if name in ("tired", "calm"):
            d.arc([cx + sx * ex - er * 1.6, ey - er, cx + sx * ex + er * 1.6, ey + er * 1.5], 0, 180, fill=col, width=lw)
        elif name == "silly" and sx == 1:
            d.line([(cx + ex - er * 1.5, ey), (cx + ex + er * 1.5, ey)], fill=col, width=lw)
        else:
            rr = er * (1.5 if name in ("surprised", "scared") else 1)
            d.ellipse([cx + sx * ex - rr, ey - rr, cx + sx * ex + rr, ey + rr], fill=col)
        if name == "angry":
            d.line([(cx + sx * ex * 1.5, ey - r * 0.3), (cx + sx * ex * 0.4, ey - r * 0.16)], fill=col, width=lw)
        if name == "worried":
            d.line([(cx + sx * ex * 1.5, ey - r * 0.18), (cx + sx * ex * 0.4, ey - r * 0.3)], fill=col, width=lw)
    my, mw = cy + r * 0.35, r * 0.45
    if name in ("happy", "excited", "proud", "silly"):
        d.arc([cx - mw, my - mw * 0.9, cx + mw, my + mw * 0.5], 20, 160, fill=col, width=lw * 2)
        if name == "silly":
            d.ellipse([cx - r * 0.1, my + r * 0.05, cx + r * 0.12, my + r * 0.3], outline=col, width=lw)
    elif name in ("sad", "angry"):
        d.arc([cx - mw, my - mw * 0.1, cx + mw, my + mw * 1.2], 200, 340, fill=col, width=lw * 2)
    elif name in ("surprised", "scared"):
        d.ellipse([cx - r * 0.15, my - r * 0.12, cx + r * 0.15, my + r * 0.2], outline=col, width=lw * 2)
    elif name == "shy":
        d.arc([cx - mw * 0.6, my - mw * 0.4, cx + mw * 0.6, my + mw * 0.3], 20, 160, fill=col, width=lw)
        for sx in (-1, 1):
            d.ellipse([cx + sx * r * 0.55 - r * 0.1, cy + r * 0.05, cx + sx * r * 0.55 + r * 0.1, cy + r * 0.2], outline=col, width=lw)
    else:
        d.line([(cx - mw * 0.7, my), (cx + mw * 0.7, my)], fill=col, width=lw * 2)


def feelings(C, v):
    top = C.title("How Are You Feeling?")
    for i, x0, y0, x1, y1 in C.grid(3, 4, top):
        name, col = FEELINGS[i], C.col(i)
        r = min(x1 - x0, y1 - y0) * 0.3
        _face(C.d, name, (x0 + x1) / 2, y0 + (y1 - y0) * 0.42, r, col, C.lw)
        C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.88), name, (y1 - y0) * 0.13, C.ink)


ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"),
         (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def to_roman(n):
    out = ""
    for v, s in ROMAN:
        while n >= v:
            out += s; n -= v
    return out


def roman_numerals(C, v):
    top = C.title("Roman Numerals")
    nums = list(range(1, 21)) + [30, 40, 50, 100, 500, 1000]
    for i, x0, y0, x1, y1 in C.grid(4, 7, top):
        if i >= len(nums):
            break
        n, col = nums[i], C.col(i)
        C.cell(x0, y0, x1, y1, col)
        C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.36), to_roman(n), C.fit(to_roman(n), (y1 - y0) * 0.36, (x1 - x0) * 0.85), col)
        C.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.76), str(n), (y1 - y0) * 0.24, C.ink, "small")


def number_bonds(C, v):
    n = int(v)
    top = C.title(f"Number Bonds to {n}")
    pairs = [(a, n - a) for a in range(0, n + 1)]
    cols = 1 if n <= 10 else 2
    per = math.ceil(len(pairs) / cols)
    h = (C.H * 0.95 - top) / per
    size = min(h * 0.6, C.W * (0.075 if cols == 1 else 0.05))
    for i, (a, b) in enumerate(pairs):
        c, r = divmod(i, per)
        y = top + (r + 0.5) * h
        col = C.col(i)
        base = 0.5 if cols == 1 else (0.27 + c * 0.47)
        span = 0.32 if cols == 1 else 0.2
        for k, s_ in enumerate((str(a), "+", str(b), "=", str(n))):
            x = C.W * (base - span / 2 + k * span / 4)
            C.text((x, y), s_, size, col if s_ not in "+=" else C.ink)


def compass(C, v):
    top = C.title("Compass Points")
    W = C.W
    cx, cy, r = W / 2, top + (C.H * 0.95 - top) / 2, W * 0.36
    d = C.d
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=C.ink, width=C.lw)
    pts = [("N", 0), ("NE", 45), ("E", 90), ("SE", 135), ("S", 180), ("SW", 225), ("W", 270), ("NW", 315)]
    for i, (lab, ang) in enumerate(pts):
        a = math.radians(ang - 90)
        long = len(lab) == 1
        rr = r * (0.82 if long else 0.55)
        col = C.col(i)
        side = r * (0.1 if long else 0.07)
        tip = (cx + rr * math.cos(a), cy + rr * math.sin(a))
        l = (cx + side * math.cos(a - math.pi / 2), cy + side * math.sin(a - math.pi / 2))
        rgt = (cx + side * math.cos(a + math.pi / 2), cy + side * math.sin(a + math.pi / 2))
        d.polygon([tip, l, (cx, cy)], fill=col)
        d.polygon([tip, rgt, (cx, cy)], outline=col, width=C.lw)
        C.text((cx + r * 1.12 * math.cos(a), cy + r * 1.12 * math.sin(a)), lab, W * (0.06 if long else 0.04), col)
    names = "North  ·  East  ·  South  ·  West"
    C.text((cx, C.H * 0.965), names, W * 0.028, C.ink, "small")


# (number, symbol, name, category, row, col)   period rows 1-7, lanthanides row 9, actinides row 10
_EL = """H Hydrogen nm|He Helium ng|Li Lithium am|Be Beryllium ae|B Boron md|C Carbon nm|N Nitrogen nm|O Oxygen nm|F Fluorine hl|Ne Neon ng|
Na Sodium am|Mg Magnesium ae|Al Aluminium pt|Si Silicon md|P Phosphorus nm|S Sulfur nm|Cl Chlorine hl|Ar Argon ng|
K Potassium am|Ca Calcium ae|Sc Scandium tm|Ti Titanium tm|V Vanadium tm|Cr Chromium tm|Mn Manganese tm|Fe Iron tm|Co Cobalt tm|Ni Nickel tm|Cu Copper tm|Zn Zinc tm|Ga Gallium pt|Ge Germanium md|As Arsenic md|Se Selenium nm|Br Bromine hl|Kr Krypton ng|
Rb Rubidium am|Sr Strontium ae|Y Yttrium tm|Zr Zirconium tm|Nb Niobium tm|Mo Molybdenum tm|Tc Technetium tm|Ru Ruthenium tm|Rh Rhodium tm|Pd Palladium tm|Ag Silver tm|Cd Cadmium tm|In Indium pt|Sn Tin pt|Sb Antimony md|Te Tellurium md|I Iodine hl|Xe Xenon ng|
Cs Caesium am|Ba Barium ae|La Lanthanum ln|Ce Cerium ln|Pr Praseodymium ln|Nd Neodymium ln|Pm Promethium ln|Sm Samarium ln|Eu Europium ln|Gd Gadolinium ln|Tb Terbium ln|Dy Dysprosium ln|Ho Holmium ln|Er Erbium ln|Tm Thulium ln|Yb Ytterbium ln|Lu Lutetium ln|Hf Hafnium tm|Ta Tantalum tm|W Tungsten tm|Re Rhenium tm|Os Osmium tm|Ir Iridium tm|Pt Platinum tm|Au Gold tm|Hg Mercury tm|Tl Thallium pt|Pb Lead pt|Bi Bismuth pt|Po Polonium pt|At Astatine hl|Rn Radon ng|
Fr Francium am|Ra Radium ae|Ac Actinium ac|Th Thorium ac|Pa Protactinium ac|U Uranium ac|Np Neptunium ac|Pu Plutonium ac|Am Americium ac|Cm Curium ac|Bk Berkelium ac|Cf Californium ac|Es Einsteinium ac|Fm Fermium ac|Md Mendelevium ac|No Nobelium ac|Lr Lawrencium ac|Rf Rutherfordium tm|Db Dubnium tm|Sg Seaborgium tm|Bh Bohrium tm|Hs Hassium tm|Mt Meitnerium tm|Ds Darmstadtium tm|Rg Roentgenium tm|Cn Copernicium tm|Nh Nihonium pt|Fl Flerovium pt|Mc Moscovium pt|Lv Livermorium pt|Ts Tennessine hl|Og Oganesson ng"""
CATS = {"am": ("Alkali metals", "#E63946"), "ae": ("Alkaline earth metals", "#F4A261"), "tm": ("Transition metals", "#E9C46A"),
        "pt": ("Post-transition metals", "#2A9D8F"), "md": ("Metalloids", "#8AB17D"), "nm": ("Other non-metals", "#3D85C6"),
        "hl": ("Halogens", "#7B2CBF"), "ng": ("Noble gases", "#D63384"), "ln": ("Lanthanides", "#B08968"), "ac": ("Actinides", "#6D597A")}


def elements():
    els = [e.strip().split() for e in _EL.replace("\n", "").split("|") if e.strip()]
    out = []
    for n, (sym, name, cat) in enumerate(els, 1):
        if n <= 2: row, col = 1, (1 if n == 1 else 18)
        elif n <= 10: row, col = 2, (n - 2 if n <= 4 else n + 8)
        elif n <= 18: row, col = 3, (n - 10 if n <= 12 else n)
        elif n <= 36: row, col = 4, n - 18
        elif n <= 54: row, col = 5, n - 36
        elif n <= 86:
            row = 6
            if 57 <= n <= 71: row, col = 9, n - 57 + 3
            else: col = n - 54 if n <= 56 else n - 68
        else:
            row = 7
            if 89 <= n <= 103: row, col = 10, n - 89 + 3
            else: col = n - 86 if n <= 88 else n - 100
        out.append((n, sym, name, cat, row, col))
    return out


def periodic_table(C, v):
    W, H = C.W, C.H
    # landscape content on a portrait sheet: title, then the table rotated 90 degrees reads badly,
    # so the table is laid out across the width with small cells and a legend below
    top = C.title("Periodic Table")
    m = W * 0.035
    cw = (W - 2 * m) / 18
    y_start = top + W * 0.03
    ch = min(cw * 1.9, (H * 0.8 - y_start) / 9.6)
    for n, sym, name, cat, row, col in elements():
        x0 = m + (col - 1) * cw
        y0 = y_start + ((row - 1) if row <= 7 else (row - 1.6)) * ch
        colour = hexrgb(CATS[cat][1])
        C.d.rectangle([x0 + cw * 0.04, y0 + ch * 0.04, x0 + cw * 0.96, y0 + ch * 0.96], outline=colour, width=max(1, C.lw // 2),
                      fill=mix(C.bg, colour, 0.1))
        C.text((x0 + cw / 2, y0 + ch * 0.17), str(n), min(ch * 0.13, cw * 0.28), C.ink, "small")
        C.text((x0 + cw / 2, y0 + ch * 0.47), sym, min(ch * 0.28, cw * 0.5), colour)
        C.text((x0 + cw / 2, y0 + ch * 0.78), name, C.fit(name, cw * 0.17, cw * 0.88, "small"), C.ink, "small")
    # legend
    ly = y_start + 9.8 * ch
    items = list(CATS.values())
    for i, (lab, hx) in enumerate(items):
        cx = m + (i % 2) * (W - 2 * m) / 2
        cy = ly + (i // 2) * W * 0.045
        c = hexrgb(hx)
        C.d.rectangle([cx, cy - W * 0.012, cx + W * 0.024, cy + W * 0.012], outline=c, fill=mix(C.bg, c, 0.25), width=C.lw)
        C.text((cx + W * 0.04, cy), lab, W * 0.024, C.ink, "small", anchor="lm")


DRAW = {k: globals()[k] for k in CHARTS}


def render_chart(chart_id, variant="", palette="rainbow", fonts="kids_round", width=1200):
    C = Chart(palette, fonts, width)
    DRAW[chart_id](C, variant)
    return C.img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chart", nargs="?")
    ap.add_argument("--variant", default="")
    ap.add_argument("--palette", default="rainbow")
    ap.add_argument("--fonts", default="kids_round")
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--out", default="chart.png")
    ap.add_argument("--sheet")
    a = ap.parse_args()
    if a.sheet:
        pals = ["rainbow", "bw", "navy", "pastel", "sage", "terracotta", "teal", "plum"]
        fonts = ["kids_round", "geometric", "condensed", "kids_chewy"]
        ims = []
        for i, c in enumerate(CHARTS):
            v = CHARTS[c]["variants"][len(CHARTS[c]["variants"]) // 2]
            ims.append(render_chart(c, v, pals[i % len(pals)], fonts[i % len(fonts)], 500))
        w, h = ims[0].size
        cols = 6
        sheet = Image.new("RGB", (cols * (w + 10) + 10, math.ceil(len(ims) / cols) * (h + 10) + 10), (190, 190, 190))
        for i, im in enumerate(ims):
            sheet.paste(im, (10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 10)))
        sheet.save(a.sheet)
        return
    render_chart(a.chart, a.variant, a.palette, a.fonts, a.width).save(a.out)


if __name__ == "__main__":
    main()
