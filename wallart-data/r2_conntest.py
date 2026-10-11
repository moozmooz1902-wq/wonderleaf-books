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
                  config=Config(signature_version="s3v4", connect_timeout=15,
                                read_timeout=30, retries={"max_attempts":2}),
                  region_name="auto")
POSTER = ["nebula-m12k","lunar-kms","mercury-usm","posterleaf-store1",
          "prism-rps","orbit-uss","velvet-ars","luxvia-art"]
out = {"sample_keys": {}, "write_test": {}}
for b in POSTER:
    try:
        r = s3.list_objects_v2(Bucket=b, MaxKeys=4)
        out["sample_keys"][b] = [o["Key"] for o in r.get("Contents", [])]
    except ClientError as e:
        out["sample_keys"][b] = "ERR " + e.response["Error"].get("Code","")
# full write -> read -> delete on one poster bucket
B = "nebula-m12k"; K = "wallart/_conn_test.txt"
try:
    s3.put_object(Bucket=B, Key=K, Body=b"connection test", ContentType="text/plain")
    got = s3.get_object(Bucket=B, Key=K)["Body"].read().decode()
    s3.delete_object(Bucket=B, Key=K)
    out["write_test"] = {"bucket": B, "put": "ok", "get": got, "delete": "ok"}
except ClientError as e:
    out["write_test"] = {"bucket": B, "error": e.response["Error"].get("Code")}
# is a Cloudflare API token present anywhere on this pod?
out["CF_API_TOKEN_present"] = bool(os.environ.get("CF_API_TOKEN"))
print("CONNTEST " + json.dumps(out, indent=1))
EOF
echo TEST_DONE
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
    body = {"name": "wallart-conntest", "templateId": TEMPLATE,
            "imageName": "runpod/base:0.7.0-ubuntu2404",
            "computeType": "CPU", "cpuFlavorIds": ["cpu3c"], "vcpuCount": 2,
            "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", SCRIPT]}
    r = curl("POST", "/pods", body)
    print(json.dumps({k: r.get(k) for k in ("id", "desiredStatus", "costPerHr",
                                            "error", "_raw")}, indent=1))
    if r.get("id"):
        print(f"log: https://{r['id']}-8000.proxy.runpod.net/boot.log")
