#!/usr/bin/env python3
"""Chart and map listings (drawn in code, no AI, no licence issues).

  charts  -> lunar-kms          educational wall charts (charts.py)
  maps    -> posterleaf-store1  country maps in 4 styles, and "Home" city prints (maps.py)

    python3 visual_bank.py --stats
    python3 visual_bank.py          -> out/<bucket>_visual.csv.gz
"""
import argparse, csv, gzip, json, random
from collections import Counter, defaultdict
from pathlib import Path

from charts import CHARTS, all_specs, chart_title
from compliance import check as ip_check
from generate import fit
from maps import countries, places, SHORT
from styles import PALETTES

HERE = Path(__file__).resolve().parent
SKU = {"luxvia-art": "LX", "mercury-usm": "MC", "lunar-kms": "LN", "posterleaf-store1": "PL"}

CHART_PALETTES = ["rainbow", "pastel", "bw", "navy", "sage", "terracotta", "teal", "plum"]
CHART_FONTS = {"kids_round": "Kids", "geometric": "Modern"}
MAP_PALETTES = ["bw", "navy", "sage", "terracotta", "forest", "charcoal", "burgundy", "teal"]
MAP_STYLES = {"outline": "Outline", "dots": "Dotted", "lines": "Striped", "solid": "Silhouette"}
HOME_PALETTES = ["bw", "navy", "sage", "terracotta", "blush", "forest"]
MAP_FONTS = ["geometric", "classic_serif", "roman", "josefin"]

FIELDS = ["sku", "store", "kind", "niche", "spec", "palette", "fonts", "title", "room", "colour", "img_path"]


def chart_rows():
    for cid, var in all_specs():
        for pal in CHART_PALETTES:
            for fset, word in CHART_FONTS.items():
                name = chart_title(cid, var)
                colour = PALETTES[pal][0]
                title = fit([f"{name} Poster {word} {colour}", CHARTS[cid]["keywords"], "Classroom", "Kids",
                             "A4 A3 A2", "Wall Chart"])
                yield dict(store="lunar-kms", kind="chart", niche="charts", spec=f"{cid}|{var}", palette=pal,
                           fonts=fset, title=title, room=random.Random(title).choice(["Classroom", "Kids Bedroom", "Playroom", "Study"]),
                           colour=colour)


def map_rows():
    names = sorted(countries())
    for c in names:
        label = SHORT.get(c, c)
        for style, sword in MAP_STYLES.items():
            for i, pal in enumerate(MAP_PALETTES):
                colour = PALETTES[pal][0]
                title = fit([f"{label} Map Print {sword} {colour}", "Country Outline", "Wall Art", "Travel Gift",
                             "A4 A3 A2", "Poster"])
                yield dict(store="posterleaf-store1", kind="map", niche="maps_country", spec=f"{c}|{style}|",
                           palette=pal, fonts=MAP_FONTS[i % len(MAP_FONTS)], title=title,
                           room=random.Random(title).choice(["Living Room", "Hallway", "Office", "Study"]), colour=colour)
    known = set(names)
    for adm, cities in sorted(places().items()):
        if adm not in known:
            continue
        for city, lon, lat, pop in cities:
            if pop < 100000:
                continue
            label = SHORT.get(adm, adm)
            for i, pal in enumerate(HOME_PALETTES):
                colour = PALETTES[pal][0]
                title = fit([f"Home {city} {label} Map Print Heart {colour}", "Hometown", "Wall Art",
                             "New Home Gift", "A4 A3 A2"])
                yield dict(store="posterleaf-store1", kind="map", niche="maps_home", spec=f"{adm}|home|{city}",
                           palette=pal, fonts=MAP_FONTS[i % len(MAP_FONTS)], title=title,
                           room=random.Random(title).choice(["Living Room", "Hallway", "Bedroom"]), colour=colour)


def build(write=True):
    by_store = defaultdict(list)
    seen, dup, blocked = set(), 0, 0
    for r in list(chart_rows()) + list(map_rows()):
        if ip_check(r["title"]):
            blocked += 1
            continue
        if r["title"] in seen:
            dup += 1
            continue
        seen.add(r["title"])
        by_store[r["store"]].append(r)
    if write:
        (HERE / "out").mkdir(exist_ok=True)
        for store, rows in by_store.items():
            random.Random(f"visual-{store}").shuffle(rows)
            with gzip.open(HERE / "out" / f"{store}_visual.csv.gz", "wt", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=FIELDS)
                w.writeheader()
                for n, r in enumerate(rows, 1):
                    r["sku"] = f"{SKU[store]}VS{n:07d}"
                    r["img_path"] = f"/art/mock/{r['sku']}.jpg"
                    w.writerow(r)
    return {s: Counter(r["niche"] for r in rows) for s, rows in by_store.items()}, dup, blocked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    stats, dup, blocked = build(write=not a.stats)
    tot = 0
    for s, c in stats.items():
        n = sum(c.values()); tot += n
        print(f"{s:20s} {n:>7,}  " + ", ".join(f"{k} {v:,}" for k, v in c.items()))
    print(f"{'TOTAL':20s} {tot:>7,}   (duplicate titles dropped {dup}, IP-blocked {blocked})")


if __name__ == "__main__":
    main()
