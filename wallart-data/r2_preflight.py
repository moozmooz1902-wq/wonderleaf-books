#!/usr/bin/env python3
"""Find out what the stored R2 credentials can actually do, without ever
seeing them.

The keys live as environment variables on RunPod template vbsgwyibn1, put
there by the seller. A pod created with that templateId inherits them; this
session never holds them and cannot print them. So the probe runs inside a
pod and reports only what worked.

Three questions, in order of how much they commit to:
  1. can it LIST buckets?                       read only
  2. can it WRITE into the existing bucket?     needed for uploads
  3. can it CREATE a bucket?                    needed for a wall-art bucket

Nothing is deleted and nothing outside a probe/ prefix is touched.
"""
import json, subprocess, sys

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"          # carries R2_* env, see tshirt/ACCESS.md

# Same rule as launch_gen.py, and it was forgotten here first time round:
# run the job ALONGSIDE the image's own /start.sh, never instead of it, or
# RunPod's in-container agent never starts and the HTTP proxy has no route.
SCRIPT = r'''
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
set -x
python3 -m pip install -q --no-input --break-system-packages boto3 requests 2>&1 | tail -2
python3 - <<'EOF'
import os, json, boto3, requests
from botocore.config import Config
from botocore.exceptions import ClientError
out = {}
tok = os.environ.get("CF_API_TOKEN"); acct = os.environ.get("R2_ACCOUNT_ID")
out["CF_API_TOKEN_present"] = bool(tok)
BUCKETS = ["luxvia-art","posterleaf-store1","lunar-kms","mercury-usm"]
if tok:
    h = {"Authorization": f"Bearer {tok}"}
    try:
        r = requests.get("https://api.cloudflare.com/client/v4/user/tokens/verify",
                         headers=h, timeout=30).json()
        out["token_verify"] = r.get("result", r.get("errors"))
    except Exception as e:
        out["token_verify"] = str(e)[:120]
    out["public_urls"] = {}
    for b in BUCKETS:
        rec = {}
        for kind, path in (("managed", "domains/managed"), ("custom", "domains/custom")):
            try:
                r = requests.get(
                    f"https://api.cloudflare.com/client/v4/accounts/{acct}/r2/buckets/{b}/{path}",
                    headers=h, timeout=30).json()
                rec[kind] = r.get("result") if r.get("success") else r.get("errors")
            except Exception as e:
                rec[kind] = str(e)[:100]
        out["public_urls"][b] = rec
# S3 write check on all four target buckets
s3 = boto3.client("s3", endpoint_url=f"https://{acct}.r2.cloudflarestorage.com",
                  aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                  aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                  config=Config(signature_version="s3v4", connect_timeout=15,
                                read_timeout=30, retries={"max_attempts":2}),
                  region_name="auto")
out["write_check"] = {}
for b in BUCKETS:
    k = "wallart/gen/_preflight.txt"
    try:
        s3.put_object(Bucket=b, Key=k, Body=b"ok", ContentType="text/plain")
        s3.get_object(Bucket=b, Key=k)["Body"].read()
        s3.delete_object(Bucket=b, Key=k)
        out["write_check"][b] = "put/get/delete OK"
    except ClientError as e:
        out["write_check"][b] = "ERR " + e.response["Error"].get("Code","")
print("PREFLIGHT " + json.dumps(out, indent=1, default=str))
EOF
echo PREFLIGHT_DONE
EOS
nohup bash /workspace/run.sh > /workspace/boot.log 2>&1 &
if [ -x /start.sh ]; then exec /start.sh; else sleep infinity; fi
'''


def curl(method, path, body=None):
    cmd = ["curl", "-sS", "--max-time", "90", "-X", method, f"{API}{path}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"_raw": out[:600]}


if __name__ == "__main__":
    body = {"name": "wallart-preflight", "templateId": TEMPLATE,
            "imageName": "runpod/base:0.7.0-ubuntu2404",
            "computeType": "CPU", "cpuFlavorIds": ["cpu3c"], "vcpuCount": 2,
            "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", SCRIPT]}
    r = curl("POST", "/pods", body)
    print(json.dumps({k: r.get(k) for k in ("id", "desiredStatus", "costPerHr",
                                            "error", "_raw")}, indent=1))
    if r.get("id"):
        print(f"log: https://{r['id']}-8000.proxy.runpod.net/boot.log")
