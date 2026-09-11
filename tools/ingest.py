"""Download design images listed in a CSV and build data/designs.jsonl.

    python3 tools/ingest.py data/my_designs.csv

Required CSV columns: image_url, title
Optional: listing_url, marketplace, niche, price, rating, review_count,
          bsr, label, notes

Images are saved under data/images/ named by content hash, so re-running
is safe and duplicate artwork collapses to one row.
"""

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "data" / "images"
OUT = ROOT / "data" / "designs.jsonl"

EXT_BY_TYPE = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _session():
    import requests

    s = requests.Session()
    # Honour the environment's CA bundle rather than disabling verification.
    bundle = os.environ.get("REQUESTS_CA_BUNDLE") or "/root/.ccr/ca-bundle.crt"
    if Path(bundle).exists():
        s.verify = bundle
    s.headers["User-Agent"] = "Mozilla/5.0 (compatible; design-research/1.0)"
    return s


def download(session, url):
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    content = resp.content
    ctype = resp.headers.get("content-type", "").split(";")[0].strip()
    ext = EXT_BY_TYPE.get(ctype)
    if ext is None:
        ext = Path(url.split("?")[0]).suffix.lower()
        if ext not in EXT_BY_TYPE.values():
            raise ValueError(f"not an image ({ctype or 'unknown type'})")
    digest = hashlib.sha256(content).hexdigest()[:16]
    path = IMAGES / f"{digest}{ext}"
    if not path.exists():
        path.write_bytes(content)
    return path, digest


def load_existing():
    rows = {}
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("id", "").startswith("example-"):
                continue  # drop the placeholder on first real ingest
            rows[row["id"]] = row
    return rows


def main(csv_path):
    IMAGES.mkdir(parents=True, exist_ok=True)
    rows = load_existing()
    added = skipped = failed = 0

    session = _session()
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        for i, entry in enumerate(csv.DictReader(fh), 2):
            url = (entry.get("image_url") or "").strip()
            title = (entry.get("title") or "").strip()
            if not url:
                continue
            try:
                path, digest = download(session, url)
            except Exception as e:
                print(f"  row {i}: FAILED {url[:70]} — {e}")
                failed += 1
                continue

            if digest in rows:
                skipped += 1
                continue

            row = {
                "id": digest,
                "image_file": path.name,
                "title": title,
                "source_url": url,
                "label": (entry.get("label") or "positive").strip(),
            }
            for field in ("listing_url", "marketplace", "niche", "price",
                          "notes"):
                value = (entry.get(field) or "").strip()
                if value:
                    row[field] = value

            perf = {}
            for field in ("rating", "review_count", "bsr"):
                value = (entry.get(field) or "").strip()
                if value:
                    perf[field] = value
            if perf:
                perf["signal_type"] = "marketplace_data"
                row["performance"] = perf

            rows[digest] = row
            added += 1
            print(f"  row {i}: {path.name}  {title[:55]}")

    with open(OUT, "w", encoding="utf-8") as fh:
        for row in rows.values():
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\n{added} added, {skipped} already had, {failed} failed"
          f"  →  {len(rows)} total in data/designs.jsonl")
    if added:
        print("Next: python3 tools/analyze.py")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
