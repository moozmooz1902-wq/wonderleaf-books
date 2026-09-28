#!/usr/bin/env python3
"""Upload each store's finished eBay CSVs to its own bucket, under ebay-upload/,
so they can be downloaded straight from the Cloudflare dashboard."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from publish import s3

client = s3()
for folder in sorted((HERE / "out" / "ebay").iterdir()):
    if not folder.is_dir():
        continue
    for f in sorted(folder.glob("*.csv")):
        client.upload_file(str(f), folder.name, f"ebay-upload/{f.name}",
                           ExtraArgs={"ContentType": "text/csv"})
        print(f"{folder.name}/ebay-upload/{f.name}")
