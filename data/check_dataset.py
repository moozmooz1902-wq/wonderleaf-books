"""Report on dataset health across both stages of the pipeline.

    python3 data/check_dataset.py

Stage 1 (data/designs.jsonl) comes from tools/ingest.py — the CSV rows plus
downloaded images. Stage 2 (data/analyzed.jsonl) comes from tools/analyze.py
— the vision fingerprints.
"""

import json
import sys
from collections import Counter
from pathlib import Path

DATA = Path(__file__).parent
IMAGES = DATA / "images"


def load(name):
    path = DATA / name
    rows, errors = [], []
    if not path.exists():
        return rows, errors
    for n, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            errors.append(f"{name} line {n}: bad JSON — {e}")
    return rows, errors


def main():
    designs, errors = load("designs.jsonl")
    analyzed, more = load("analyzed.jsonl")
    errors += more

    if not designs:
        print("No designs yet.\n")
        print("  1. Copy data/input_template.csv and fill it with your rows")
        print("  2. python3 tools/ingest.py your.csv")
        print("  3. python3 tools/analyze.py")
        print("  4. python3 tools/distill.py --prompt")
        return 0

    seen = set()
    for row in designs:
        rid = row.get("id")
        if rid in seen:
            errors.append(f"duplicate id {rid}")
        seen.add(rid)
        for field in ("id", "image_file", "title"):
            if not row.get(field):
                errors.append(f"{rid}: missing '{field}'")
        img = row.get("image_file")
        if img and not (IMAGES / img).exists():
            errors.append(f"{rid}: image missing — data/images/{img}")

    total = len(designs)
    done = {r["id"] for r in analyzed}
    print(f"{total} designs ingested, {len(done)} analysed\n")

    if errors:
        print("PROBLEMS")
        for e in errors[:25]:
            print(f"  - {e}")
        print()

    niches = Counter(r.get("niche") or "(unset)" for r in designs)
    print("PER NICHE (aim for 30-50 in one niche before generating)")
    for niche, count in niches.most_common():
        flag = "  <- ready" if count >= 30 else ""
        print(f"  {count:4d}  {niche:<30} {'#' * min(count, 40)}{flag}")
    print()

    with_perf = sum(1 for r in designs if r.get("performance"))
    negatives = sum(1 for r in designs if r.get("label") == "negative")
    print("COVERAGE")
    print(f"  performance data  : {with_perf}/{total}"
          f"{'  <- the field that decides what the spec learns' if with_perf < total else ''}")
    print(f"  negative examples : {negatives}/{total}"
          f"{'  <- add some, contrast teaches' if negatives < total * 0.15 else ''}")
    print(f"  analysed          : {len(done)}/{total}"
          f"{'  <- run tools/analyze.py' if len(done) < total else ''}")

    if analyzed:
        risky = [r for r in analyzed if r.get("ip_risk") in ("possible", "clear")]
        if risky:
            print(f"\n  {len(risky)} design(s) flagged for IP risk — "
                  f"see data/STYLE_SPEC.md")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
