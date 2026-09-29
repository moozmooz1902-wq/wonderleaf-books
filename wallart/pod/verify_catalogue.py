#!/usr/bin/env python3
"""Stop the pod run if a rebuilt catalogue differs from the one that was reviewed.

generate.py, visual_bank.py and images_bank.py are deterministic, so a rebuild
on any machine must give the same rows and SKUs. pod/catalogue_manifest.json
holds the SHA-256 of each uncompressed catalogue file from the reviewed build.

    python3 pod/verify_catalogue.py            every file in the manifest
    python3 pod/verify_catalogue.py _ai        only names containing _ai
"""
import gzip, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
want = json.loads((HERE / "pod" / "catalogue_manifest.json").read_text())
only = sys.argv[1] if len(sys.argv) > 1 else ""
bad = 0
for name, meta in want.items():
    if only and only not in name:
        continue
    h = hashlib.sha256()
    rows = 0
    try:
        with gzip.open(HERE / "out" / f"{name}.csv.gz", "rb") as fh:
            for line in fh:
                h.update(line)
                rows += 1
    except FileNotFoundError:
        print(f"{name:28s} MISSING"); bad += 1; continue
    same = h.hexdigest() == meta["sha256"]
    bad += not same
    print(f"{name:28s} {rows - 1:>9,} rows  {'OK' if same else 'DIFFERENT from the reviewed build'}")
sys.exit(1 if bad else 0)
