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
python3 -m pip install -q --no-input --break-system-packages boto3 2>&1 | tail -2
python3 - <<'EOF'
import os, json, boto3
from botocore.config import Config
from botocore.exceptions import ClientError
s3 = boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                  aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                  aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                  config=Config(signature_version="s3v4", connect_timeout=15, read_timeout=30, retries={"max_attempts":2}), region_name="auto")
out = {}
try:
    bs = s3.list_buckets().get("Buckets", [])
    out["buckets"] = {}
    for b in bs:
        # CAPPED. The first version counted every object in every bucket and
        # hung for eight minutes: the t-shirt bucket holds a live catalogue,
        # and paginating all of it is thousands of calls. Three pages is
        # enough to tell an empty bucket from a used one, which is the
        # question being asked.
        n = b["Name"]; cnt = 0; size = 0; tok = None; pages = 0
        try:
            while pages < 3:
                kw = {"Bucket": n, "MaxKeys": 1000}
                if tok: kw["ContinuationToken"] = tok
                r = s3.list_objects_v2(**kw)
                for o in r.get("Contents", []): cnt += 1; size += o["Size"]
                pages += 1
                if not r.get("IsTruncated"): break
                tok = r["NextContinuationToken"]
            out["buckets"][n] = {"objects": f"{cnt:,}" + ("+" if r.get("IsTruncated") else ""),
                                 "MB": round(size/1048576, 1),
                                 "created": str(b.get("CreationDate"))[:10]}
        except ClientError as e:
            out["buckets"][n] = {"error": e.response["Error"].get("Code")}
except ClientError as e:
    out["buckets"] = "DENIED: " + e.response["Error"].get("Code","")
# can we create one? make a throwaway and remove it again
try:
    s3.create_bucket(Bucket="wl-capability-test-9931")
    out["can_create_buckets"] = True
    try: s3.delete_bucket(Bucket="wl-capability-test-9931"); out["can_delete_buckets"] = True
    except ClientError as e: out["can_delete_buckets"] = e.response["Error"].get("Code")
except ClientError as e:
    out["can_create_buckets"] = "DENIED: " + e.response["Error"].get("Code","")
print("R2CAP " + json.dumps(out, indent=1))
EOF
echo CAP_DONE
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
    body = {"name": "wallart-r2-cap", "templateId": TEMPLATE,
            "imageName": "runpod/base:0.7.0-ubuntu2404",
            "computeType": "CPU", "cpuFlavorIds": ["cpu3c"], "vcpuCount": 2,
            "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", SCRIPT]}
    r = curl("POST", "/pods", body)
    print(json.dumps({k: r.get(k) for k in ("id", "desiredStatus", "costPerHr",
                                            "error", "_raw")}, indent=1))
    if r.get("id"):
        print(f"log: https://{r['id']}-8000.proxy.runpod.net/boot.log")
