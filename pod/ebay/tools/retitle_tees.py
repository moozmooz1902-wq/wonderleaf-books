#!/usr/bin/env python3
"""
Rewrite t-shirt titles as keyword stacks, as a controlled test.

    # see the new titles without writing anything
    python3 retitle_tees.py --catalogue catalogue.json --listings active.csv

    # write a Revise file for a 2,000 listing sample
    python3 retitle_tees.py --catalogue catalogue.json --listings active.csv \
        --sample 2000 --out revise_titles

WHY

The competitor research found both high-volume tee sellers writing titles
like this:

    BIKER T-SHIRT Motorbike Motorcycle Cafe Racer Chopper Bike Mens Funny Skull Top

Nine near-synonyms in 80 characters, catching every phrasing a buyer might
type. Ours look like this:

    My Nan Is A Bouncer Mens Womens T-Shirt Funny Novelty Gift Tee Top

The joke leads, and `Mens Womens T-Shirt Funny Novelty Gift Tee Top` is the
same 46 characters on all 50,740 listings, so it distinguishes nothing. The
searchable noun - bouncer - is buried mid-title and appears once.

SAMPLE, NOT EVERYTHING

--sample takes a random slice, so the rest of the catalogue stays as it is
and the two can be compared. Revising all 50,740 at once would change the
titles and leave nothing to measure them against. The picture may well
matter more than the title here; a sample tells you which.
"""

import argparse
import csv
import json
import random
import re
import sys
from pathlib import Path

csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))

ACTION = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=745|CC=UTF-8)"
HEADER = [ACTION, "ItemID", "CustomLabel", "*Title"]
MAX = 80

# Words worth spending title characters on, per family. The subject itself
# always leads; these follow it. Kept to words a buyer would actually type -
# padding with "Novelty" on every listing is what we are moving away from.
KEYWORDS = {
    "occupation": ["Gift", "Funny", "Work", "Job", "Mens", "Womens", "Tee"],
    "hobby": ["Gift", "Funny", "Hobby", "Mens", "Womens", "Tee", "Top"],
    "breed": ["Dog", "Puppy", "Owner", "Lover", "Gift", "Mens", "Womens"],
    "birthday": ["Birthday", "Gift", "Present", "Party", "Mens", "Womens"],
    "biker": ["Biker", "Motorbike", "Motorcycle", "Chopper", "Skull", "Mens"],
    "slogan": ["Funny", "Gift", "Joke", "Humour", "Mens", "Womens", "Tee"],
    "place": ["Pride", "Born", "Gift", "County", "Mens", "Womens", "Tee"],
    "heritage": ["Flag", "Pride", "Roots", "Gift", "Mens", "Womens", "Tee"],
    "grandparent": ["Gift", "Present", "Family", "Funny", "Mens", "Womens"],
    "music": ["Music", "Band", "Rock", "Gift", "Mens", "Womens", "Tee"],
    "military": ["Army", "Forces", "Veteran", "Gift", "Mens", "Womens"],
    "food_drink": ["Funny", "Gift", "Foodie", "Mens", "Womens", "Tee"],
    "gothic": ["Gothic", "Skull", "Dark", "Alternative", "Mens", "Womens"],
    "norse": ["Viking", "Norse", "Odin", "Valhalla", "Mens", "Womens"],
}
FALLBACK = ["Gift", "Funny", "Mens", "Womens", "T-Shirt", "Tee", "Top"]

# Some families read better with a different noun in front of "T-Shirt".
LEAD_NOUN = {"breed": "{s} Dog", "heritage": "{s}", "place": "{s}"}


def subject_of(design_id, cluster):
    """
    oc_bouncer_Nan_6 -> Bouncer.  mo_biker_cafe-racer_0 -> Cafe Racer.

    The searchable noun, which is what should lead the title. It is in the
    design id already; nothing needs looking up.
    """
    parts = design_id.split("_")
    if not parts or len(parts) < 2:
        return ""

    # Motifs: lead with the FAMILY, not the motif. mo_biker_ride-out is a
    # biker shirt, and "biker t shirt" is the search; "ride out t shirt" is
    # not a phrase anybody types.
    if parts[0] == "mo":
        raw = parts[1]
    # Slogans have no subject noun in the id - slg_powered_hiking_tea gave
    # "Powered T-Shirt". The slogan itself has to lead instead.
    elif parts[0] == "slg":
        return ""
    else:
        raw = parts[1]

    if cluster == "birthday" and raw.isdigit():
        return f"{raw}th Birthday"
    raw = raw.replace("-", " ")
    return " ".join(w.capitalize() if w.islower() else w
                    for w in raw.split())


def stack(design):
    """Build the keyword-stacked title for one design."""
    cluster = design.get("cluster", "")
    subj = subject_of(design["design_id"], cluster)
    stem = design.get("stem", "")

    lead = LEAD_NOUN.get(cluster, "{s}").format(s=subj).strip() if subj else ""
    # With no subject noun the slogan leads, which is the honest thing: the
    # slogan IS the product.
    head = f"{lead} T-Shirt" if lead else f"{stem} T-Shirt"

    parts = [head]
    used = len(head)

    # The joke second, so the title matches the picture. Skipped when the
    # slogan is already the head.
    if stem and stem.lower() not in head.lower():
        if used + len(stem) + 1 <= MAX - 14:
            parts.append(stem)
            used += len(stem) + 1

    for word in KEYWORDS.get(cluster, FALLBACK) + FALLBACK:
        if word.lower() in " ".join(parts).lower():
            continue
        if used + len(word) + 1 <= MAX:
            parts.append(word)
            used += len(word) + 1
    return " ".join(parts)[:MAX].strip()


def load_listings(path):
    """SKU -> item number, from a Seller Hub active-listings export."""
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        while True:
            here = fh.tell()
            line = fh.readline()
            if not line:
                raise SystemExit(f"{path}: no header row found")
            if not line.lstrip().startswith("#"):
                fh.seek(here)
                break
        rows = list(csv.DictReader(fh))
    lower = {(k or "").strip().lower(): k for k in rows[0].keys()}
    sku_col = next((lower[n] for n in
                    ("custom label (sku)", "custom label", "sku")
                    if n in lower), None)
    item_col = next((lower[n] for n in
                     ("item number", "item id", "itemid") if n in lower), None)
    if not sku_col or not item_col:
        raise SystemExit("export needs a custom label and an item number "
                         f"column; found {sorted(rows[0].keys())}")
    out = {}
    for r in rows:
        sku, item = (r.get(sku_col) or "").strip(), (r.get(item_col) or "").strip()
        if sku and item.isdigit():
            out.setdefault(sku, item)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", required=True)
    ap.add_argument("--listings", required=True,
                    help="Seller Hub active-listings export, to map the "
                         "custom label to an item number")
    ap.add_argument("--out", help="prefix. Without it, nothing is written")
    ap.add_argument("--sample", type=int, default=2000,
                    help="how many listings to revise. 0 means all of them, "
                         "which leaves nothing to compare against")
    ap.add_argument("--seed", type=int, default=20260830)
    ap.add_argument("--rows", type=int, default=100000)
    a = ap.parse_args()

    designs = json.loads(Path(a.catalogue).read_text())
    live = load_listings(a.listings)
    print(f"  {len(designs):,} designs, {len(live):,} live listings")

    pairs = [(d, live[d["design_id"]]) for d in designs
             if d["design_id"] in live]
    print(f"  {len(pairs):,} designs are live and can be revised")
    if not pairs:
        raise SystemExit("  none of these designs appear in that export - "
                         "is it from the right store?")

    if a.sample and a.sample < len(pairs):
        random.Random(a.seed).shuffle(pairs)
        pairs = pairs[:a.sample]
        print(f"  revising a sample of {len(pairs):,}, leaving the rest as a "
              f"control")

    changed = [(d, item, stack(d)) for d, item in pairs]
    changed = [(d, i, t) for d, i, t in changed if t != d["title"]]
    print(f"  {len(changed):,} titles would change\n")
    print("  before and after:")
    for d, _, t in changed[:8]:
        print(f"    old  {d['title']}")
        print(f"    new  {t}\n")

    lens = sorted(len(t) for _, _, t in changed)
    print(f"  median new title length {lens[len(lens)//2]}, "
          f"longest {lens[-1]}, over 80: {sum(1 for x in lens if x > 80)}")

    if not a.out:
        print("\n  DRY RUN - nothing written. Add --out <prefix> to write it.")
        return

    files, n = [], 1
    for i in range(0, len(changed), a.rows):
        fn = f"{a.out}_{n:02d}.csv"
        with open(fn, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(HEADER)
            for d, item, t in changed[i:i + a.rows]:
                w.writerow(["Revise", item, d["design_id"], t])
        print(f"  {fn}  {min(a.rows, len(changed) - i):,} rows")
        files.append(fn)
        n += 1
    print(f"\n  {len(changed):,} revisions across {len(files)} file(s)")
    print("  Revise only touches the title. Nothing else about the listing, "
          "its item number or its history changes.")


if __name__ == "__main__":
    main()
