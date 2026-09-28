#!/usr/bin/env python3
"""Stop the pod run if the rebuilt catalogue differs from the one that was reviewed.

generate.py is deterministic, so a rebuild on any machine must give the same
rows and SKUs. pod/catalogue_manifest.json holds the SHA-256 of each store's
uncompressed CSV from the reviewed build.
"""
import gzip, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
want = json.loads((HERE / "pod" / "catalogue_manifest.json").read_text())
bad = 0
for bucket, meta in want.items():
    h = hashlib.sha256()
    rows = 0
    with gzip.open(HERE / "out" / f"{bucket}.csv.gz", "rb") as fh:
        for line in fh:
            h.update(line)
            rows += 1
    same = h.hexdigest() == meta["sha256"]
    bad += not same
    print(f"{bucket:20s} {rows - 1:>9,} rows  {'OK' if same else 'DIFFERENT from the reviewed build'}")
sys.exit(1 if bad else 0)
