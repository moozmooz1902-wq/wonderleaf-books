"""Validate data/designs.jsonl and report how close the dataset is to usable.

    python data/check_dataset.py
"""

import json
import sys
from collections import Counter
from pathlib import Path

DATA = Path(__file__).parent / "designs.jsonl"
IMAGES = Path(__file__).parent / "images"

REQUIRED = ["id", "image_file", "title", "shirt_text", "niche", "label"]
RECOMMENDED = ["marketplace", "style_tags", "layout", "keywords", "notes"]


def main():
    if not DATA.exists():
        sys.exit(f"Missing {DATA}")

    rows, errors = [], []
    for n, line in enumerate(DATA.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append((n, json.loads(line)))
        except json.JSONDecodeError as e:
            errors.append(f"line {n}: bad JSON — {e}")

    seen_ids = set()
    for n, row in rows:
        for field in REQUIRED:
            if not row.get(field):
                errors.append(f"line {n}: missing required field '{field}'")
        rid = row.get("id")
        if rid in seen_ids:
            errors.append(f"line {n}: duplicate id '{rid}'")
        seen_ids.add(rid)
        if row.get("label") not in ("positive", "negative", None):
            errors.append(f"line {n}: label must be 'positive' or 'negative'")
        img = row.get("image_file")
        if img and not (IMAGES / img).exists():
            errors.append(f"line {n}: image not found — data/images/{img}")

    total = len(rows)
    print(f"{total} rows\n")

    if errors:
        print("PROBLEMS")
        for e in errors:
            print(f"  - {e}")
        print()

    if not total:
        return 1 if errors else 0

    niches = Counter(r.get("niche", "?") for _, r in rows)
    print("PER NICHE (aim for 30-50 in one niche before generating)")
    for niche, count in niches.most_common():
        bar = "#" * min(count, 50)
        flag = "  <- ready" if count >= 30 else ""
        print(f"  {count:4d}  {niche:<30} {bar}{flag}")
    print()

    negatives = sum(1 for _, r in rows if r.get("label") == "negative")
    scored = sum(1 for _, r in rows if (r.get("performance") or {}).get("gut_score"))
    print("COVERAGE")
    print(f"  performance scored : {scored}/{total}"
          f"{'  <- the field that matters most' if scored < total else ''}")
    print(f"  negative examples  : {negatives}/{total}"
          f"{'  <- add some, contrast teaches' if negatives < total * 0.15 else ''}")
    for field in RECOMMENDED:
        filled = sum(1 for _, r in rows if r.get(field))
        print(f"  {field:<18} : {filled}/{total}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
