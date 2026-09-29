#!/usr/bin/env python3
"""Public-domain museum art listings (pd/artworks.jsonl.gz -> out/<bucket>_pd.csv.gz).

153k CC0 / public-domain artworks curated by pd/curate.py: artist died by 1955
(UK copyright is life + 70), English title, wall-worthy, not a duplicate. Each
artwork goes to exactly one store. Titles are re-checked by compliance.py and
always carry "Wall Art" and "Print"; no museum names (implied endorsement).

    python3 pd_bank.py --stats
    python3 pd_bank.py
"""
import argparse, csv, gzip, json, random
from collections import Counter, defaultdict
from pathlib import Path

from compliance import check as ip_check
from generate import fit

HERE = Path(__file__).resolve().parent
SRC = HERE / "pd" / "artworks.jsonl.gz"
SKU = {"luxvia-art": "LX", "mercury-usm": "MC", "lunar-kms": "LN", "posterleaf-store1": "PL"}
ROOMS = {
    "landscapes": ["Living Room", "Hallway", "Bedroom", "Office"], "seascapes_ships": ["Living Room", "Hallway", "Study"],
    "city_architecture": ["Living Room", "Hallway", "Office"], "famous_masters": ["Living Room", "Bedroom", "Study"],
    "japanese_woodblock": ["Living Room", "Bedroom", "Hallway"], "portraits": ["Living Room", "Study", "Hallway"],
    "maps_vintage": ["Study", "Office", "Hallway"], "posters_vintage": ["Kitchen", "Living Room", "Man Cave"],
    "religious_art": ["Living Room", "Bedroom", "Hallway"], "botanical_flowers": ["Kitchen", "Bedroom", "Bathroom", "Living Room"],
    "fruit_food": ["Kitchen", "Dining Room"], "still_life": ["Kitchen", "Dining Room", "Living Room"],
    "birds": ["Living Room", "Hallway", "Bedroom"], "horses": ["Living Room", "Study", "Hallway"],
    "dogs": ["Living Room", "Hallway", "Boot Room"], "cats": ["Living Room", "Bedroom"],
    "farm_animals": ["Kitchen", "Living Room", "Hallway"], "wild_animals": ["Living Room", "Study"],
    "sea_life": ["Bathroom", "Living Room"], "insects_butterflies": ["Bedroom", "Study"],
    "abstract_modern": ["Living Room", "Office"], "other": ["Living Room", "Hallway"],
}
import re
BOOKISH = re.compile(r"\b(album|book|binding|folio|title page|frontispiece|page from|leaf from|verso|recto|"
                     r"manuscript|letter|pamphlet|broadside|text)\b", re.I)
FIELDS = ["sku", "store", "kind", "niche", "title", "room", "colour", "image_url", "iiif_base", "source",
          "artwork_id", "artist", "work_title", "image_width", "image_height", "img_path"]


def rows():
    with gzip.open(SRC, "rt", encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)


def build(write=True):
    by_store = defaultdict(list)
    seen, blocked, dup = set(), 0, 0
    for a in rows():
        if a["theme"] == "other" or BOOKISH.search(a.get("title") or ""):
            blocked += 1
            continue
        t = a["ebay_title"]
        low = t.lower()
        parts = [t]
        if "wall art" not in low:
            parts.append("Wall Art")
        if "print" not in low:
            parts.append("Print")
        title = fit(parts, keep=len(parts) - 1)
        if "?" in title.rstrip("?") or "\ufffd" in title:   # mangled characters from the source record
            blocked += 1
            continue
        if ip_check(title) or ip_check(a.get("artist") or ""):
            blocked += 1
            continue
        if title in seen:
            dup += 1
            continue
        seen.add(title)
        by_store[a["store"]].append((a, title))
    if write:
        (HERE / "out").mkdir(exist_ok=True)
        for store, items in by_store.items():
            items.sort(key=lambda x: x[0]["artwork_id"])          # stable order before the seeded shuffle
            random.Random(f"pd-{store}").shuffle(items)
            with gzip.open(HERE / "out" / f"{store}_pd.csv.gz", "wt", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=FIELDS)
                w.writeheader()
                for n, (a, title) in enumerate(items, 1):
                    sku = f"{SKU[store]}PD{n:07d}"
                    w.writerow({"sku": sku, "store": store, "kind": "pd", "niche": a["theme"], "title": title,
                                "room": random.Random(sku).choice(ROOMS.get(a["theme"], ["Living Room"])), "colour": "",
                                "image_url": a["image_url"], "iiif_base": a.get("iiif_base") or "", "source": a["source"],
                                "artwork_id": a["artwork_id"], "artist": a.get("artist") or "",
                                "work_title": a.get("work_title") or "", "image_width": a.get("image_width") or "",
                                "image_height": a.get("image_height") or "", "img_path": f"/art/mock/{sku}.jpg"})
    return {s: Counter(a["theme"] for a, _ in v) for s, v in by_store.items()}, dup, blocked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    stats, dup, blocked = build(write=not a.stats)
    tot = 0
    for s, c in stats.items():
        n = sum(c.values()); tot += n
        print(f"{s:20s} {n:>7,}  " + ", ".join(f"{k} {v:,}" for k, v in c.most_common(6)))
    print(f"{'TOTAL':20s} {tot:>7,}   (duplicate titles dropped {dup}, IP-blocked {blocked})")


if __name__ == "__main__":
    main()
