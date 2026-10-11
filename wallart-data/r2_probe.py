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
# `pip` and `python3` can be different interpreters on this image -
# the first run installed boto3 somewhere python3.13 could not see it.
python3 -m pip install -q --no-input --break-system-packages boto3 2>&1 | tail -2
python3 - <<'EOF'
import os, json, boto3
from botocore.config import Config
acct = os.environ.get("R2_ACCOUNT_ID","")
out = {"have_account": bool(acct) and "PASTE" not in acct,
       "have_key": bool(os.environ.get("R2_ACCESS_KEY_ID","")) and "PASTE" not in os.environ.get("R2_ACCESS_KEY_ID",""),
       "bucket": os.environ.get("R2_BUCKET"),
       "public_base": os.environ.get("R2_PUBLIC_BASE")}
try:
    s3 = boto3.client("s3", endpoint_url=f"https://{acct}.r2.cloudflarestorage.com",
                      aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                      config=Config(signature_version="s3v4"), region_name="auto")
    try:
        out["buckets"] = [b["Name"] for b in s3.list_buckets().get("Buckets",[])]
    except Exception as e:
        out["buckets_error"] = str(e)[:200]
    try:
        s3.put_object(Bucket=os.environ["R2_BUCKET"], Key="probe/hello.txt",
                      Body=b"wallart probe", ContentType="text/plain")
        out["write_existing"] = "ok"
    except Exception as e:
        out["write_existing"] = str(e)[:200]
    for name in ("wallart-m12k",):
        try:
            s3.create_bucket(Bucket=name); out["create_"+name] = "created"
        except Exception as e:
            msg = str(e)[:200]
            out["create_"+name] = "exists" if "Already" in msg or "exists" in msg.lower() else msg
    try:
        s3.put_object(Bucket="wallart-m12k", Key="probe/hello.txt",
                      Body=b"wallart probe", ContentType="text/plain")
        out["write_wallart"] = "ok"
    except Exception as e:
        out["write_wallart"] = str(e)[:200]
except Exception as e:
    out["fatal"] = str(e)[:300]
open("/workspace/r2.json","w").write(json.dumps(out, indent=1))
print("R2PROBE " + json.dumps(out))
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
    body = {"name": "wallart-r2-probe", "templateId": TEMPLATE,
            "imageName": "runpod/base:0.7.0-ubuntu2404",
            "computeType": "CPU", "cpuFlavorIds": ["cpu3c"], "vcpuCount": 2,
            "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", SCRIPT]}
    r = curl("POST", "/pods", body)
    print(json.dumps({k: r.get(k) for k in ("id", "desiredStatus", "costPerHr",
                                            "error", "_raw")}, indent=1))
    if r.get("id"):
        print(f"log: https://{r['id']}-8000.proxy.runpod.net/boot.log")
