#!/usr/bin/env python3
"""Read-only: does every CustomLabel in the eBay file resolve to both objects
the fulfilment tool looks up?  art/mock/<label>.jpg and art/raw/<label>.png"""
import json, boto3, os, subprocess
from botocore.config import Config

# The RunPod API key is injected by the egress proxy into curl, not exposed as a
# shell variable, and urllib gets 403 where curl gets 200 - see ACCESS.md. So
# shell out for the templates and read the R2 keys off the render template.
RP = "/tmp/rp_templates.json"
if not os.path.exists(RP):
    subprocess.run(["curl", "-sS", "--max-time", "60",
                    "https://rest.runpod.io/v1/templates", "-o", RP], check=True)
t = json.load(open(RP))
e = [x for x in t if x.get("id") == "vbsgwyibn1"][0]["env"]
B = e["R2_BUCKET"]
s3 = boto3.client("s3",
    endpoint_url=f"https://{e['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=e["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=e["R2_SECRET_ACCESS_KEY"],
    config=Config(retries={"max_attempts": 5}), region_name="auto")
print("bucket:", B, flush=True)

def keys(prefix):
    out, tok = set(), None
    pages = 0
    while True:
        kw = {"Bucket": B, "Prefix": prefix, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            out.add(o["Key"].split("/")[-1].rsplit(".", 1)[0])
        pages += 1
        if pages % 25 == 0: print(f"   ...{prefix} {len(out):,}", flush=True)
        if not r.get("IsTruncated"): return out
        tok = r["NextContinuationToken"]

want = set(open(os.environ.get("SKUS", "parent_skus.txt")).read().split())
print(f"labels in eBay file: {len(want):,}", flush=True)
print("listing art/mock/WLT- ...", flush=True); mock = keys("art/mock/WLT-")
print("listing art/raw/WLT-  ...", flush=True); raw  = keys("art/raw/WLT-")
print(f"\nart/mock/WLT-*  {len(mock):,}")
print(f"art/raw/WLT-*   {len(raw):,}")
mm, mr = want - mock, want - raw
print(f"\nlabels with NO listing photo (art/mock/<l>.jpg): {len(mm)}  {sorted(mm)[:8]}")
print(f"labels with NO print master (art/raw/<l>.png) : {len(mr)}  {sorted(mr)[:8]}")
extra_m, extra_r = mock - want, raw - want
print(f"WLT objects in mock not in the file: {len(extra_m)}  {sorted(extra_m)[:8]}")
print(f"WLT objects in raw  not in the file: {len(extra_r)}  {sorted(extra_r)[:8]}")

# spot-check that a photo really is 2000x2000 and a master really is transparent
import io
from PIL import Image
sample = sorted(want)[:: max(1, len(want)//6)][:6]
print("\nspot check (6 drawn across the catalogue):")
for sku in sample:
    try:
        m = Image.open(io.BytesIO(s3.get_object(Bucket=B, Key=f"art/mock/{sku}.jpg")["Body"].read()))
        p = Image.open(io.BytesIO(s3.get_object(Bucket=B, Key=f"art/raw/{sku}.png")["Body"].read()))
        alpha = "alpha" if p.mode in ("RGBA", "LA") else f"NO ALPHA ({p.mode})"
        print(f"   {sku}  mock {m.size} {m.mode}   raw {p.size} {alpha}")
    except Exception as ex:
        print(f"   {sku}  ERROR {type(ex).__name__}: {str(ex)[:90]}")

print("\nVERDICT:", "PASS - every label resolves to both objects"
      if not mm and not mr else "FAIL - see missing lists above")
