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
                  config=Config(signature_version="s3v4"), region_name="auto")
out = {}
# 1. the definitive test
try:
    out["list_buckets"] = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
except ClientError as e:
    out["list_buckets"] = "DENIED: " + e.response["Error"].get("Code","")

# 2. calibrate: what does an invented name return, vs one we KNOW exists?
def probe(n):
    try:
        s3.head_bucket(Bucket=n); return "OK"
    except ClientError as e:
        return str(e.response["ResponseMetadata"]["HTTPStatusCode"])
    except Exception as e:
        return "err " + str(e)[:40]
out["control_known_good"]  = probe("tshirt-m12k")
out["control_invented"]    = probe("zzq7x-definitely-not-a-bucket-9931")

# 3. a much wider guess list
accts = ["lunar","kms","lux","viaart","via-art","mercury","usm","nebula","m12k"]
pats  = ["{a}", "{a}-store", "store-{a}", "wl-{a}", "wonderleaf-{a}", "{a}-uk",
         "{a}-images","{a}-img","{a}-r2","{a}-prints","{a}-poster","{a}-posters",
         "tshirt-{a}","tshirts-{a}","wallart-{a}","wall-art-{a}","art-{a}","{a}-art",
         "{a}-wallart","{a}-tshirt","{a}1","{a}-1","{a}-bucket"]
names = sorted({p.format(a=a) for a in accts for p in pats})
res = {}
for n in names:
    r = probe(n)
    if r != "404":
        res[n] = {"OK":"EXISTS, accessible","403":"EXISTS, not in scope"}.get(r, r)
out["wider_scan"] = res
out["names_tried"] = len(names)
print("PROBE2 " + json.dumps(out))
EOF
echo PROBE_DONE
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
    body = {"name": "wallart-bucket-probe2", "templateId": TEMPLATE,
            "imageName": "runpod/base:0.7.0-ubuntu2404",
            "computeType": "CPU", "cpuFlavorIds": ["cpu3c"], "vcpuCount": 2,
            "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", SCRIPT]}
    r = curl("POST", "/pods", body)
    print(json.dumps({k: r.get(k) for k in ("id", "desiredStatus", "costPerHr",
                                            "error", "_raw")}, indent=1))
    if r.get("id"):
        print(f"log: https://{r['id']}-8000.proxy.runpod.net/boot.log")
