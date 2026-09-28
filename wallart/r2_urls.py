#!/usr/bin/env python3
"""Find each store bucket's public picture URL and write it into plan.json.

The eBay files need a real https:// picture URL per listing. Each R2 bucket's
public address (https://pub-<32 hex>.r2.dev) is looked up in this order:

  1. PIC_BASE_<BUCKET> env var, e.g. PIC_BASE_LUXVIA_ART=https://pub-....r2.dev
  2. Cloudflare API (needs CF_API_TOKEN with R2 read + R2_ACCOUNT_ID): the
     bucket's r2.dev public URL
  3. whatever is already in plan.json stores[].pic_base

Then each URL is tested by fetching a real uploaded image, so a wrong or
private URL is caught before any eBay file is built.

    python3 r2_urls.py            look up + save
    python3 r2_urls.py --test     also check a sample image loads
"""
import argparse, json, os, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def from_api(bucket):
    tok, acct = os.environ.get("CF_API_TOKEN"), os.environ.get("R2_ACCOUNT_ID")
    if not (tok and acct):
        return None
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/r2/buckets/{bucket}/domains/managed"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read())["result"]
    except Exception as e:
        print(f"  {bucket}: Cloudflare API lookup failed ({e})", file=sys.stderr)
        return None
    if not res.get("enabled"):
        print(f"  {bucket}: public r2.dev access is OFF - turn it on in Cloudflare -> R2 -> "
              f"{bucket} -> Settings -> Public access, or pictures will not load on eBay", file=sys.stderr)
        return None
    return "https://" + res["domain"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    plan_path = HERE / "plan.json"
    plan = json.loads(plan_path.read_text())
    ok = True
    for st in plan["stores"]:
        b = st["bucket"]
        env = os.environ.get("PIC_BASE_" + b.upper().replace("-", "_"))
        base = (env or from_api(b) or st.get("pic_base") or "").rstrip("/")
        st["pic_base"] = base
        print(f"{b:20s} {base or 'MISSING'}")
        if not base.startswith("https://"):
            ok = False
            continue
        if a.test:
            import boto3
            from publish import s3
            keys = s3().list_objects_v2(Bucket=b, Prefix="art/mock/", MaxKeys=1).get("Contents", [])
            if keys:
                try:
                    with urllib.request.urlopen(f"{base}/{keys[0]['Key']}", timeout=30) as r:
                        print(f"  sample image loads: HTTP {r.status}")
                except Exception as e:
                    ok = False
                    print(f"  sample image FAILED to load from {base}: {e}")
    plan_path.write_text(json.dumps(plan, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
