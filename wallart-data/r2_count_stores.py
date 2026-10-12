#!/usr/bin/env python3
"""Count the panels in the four store buckets. Nothing else.

Since the pods started being relaunched their done.txt counters restart at
zero, so summing them stopped giving the catalogue total and the number in
every report became an estimate. Listing is cheap - about a minute for a
hundred thousand keys, and only LIST calls - so this exists to make the
number exact again without running the whole duplicate audit.

Writes count.json and deletes its own pod.
"""
import json, subprocess, sys, time

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"

SCRIPT = r'''
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
set -x
python3 -m pip install -q --no-input --break-system-packages boto3 2>&1 | tail -1
python3 - <<'EOF'
import os, json, boto3
from botocore.config import Config
s3 = boto3.client("s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4"), region_name="auto")
STORES = [("luxvia-art","luxvia/gen/"), ("posterleaf-store1","store1/gen/"),
          ("mercury-usm","store2/gen/"), ("lunar-kms","store7/gen/")]
out, tot = {}, 0
for bkt, pre in STORES:
    n, tok = 0, None
    while True:
        kw = {"Bucket": bkt, "Prefix": pre, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        n += sum(1 for o in r.get("Contents", []) if o["Key"].endswith(".jpg"))
        if not r.get("IsTruncated"): break
        tok = r["NextContinuationToken"]
    out[bkt] = n; tot += n
    print(bkt, n, flush=True)
out["total"] = tot
out["listings"] = tot * 4
open("/workspace/count.json","w").write(json.dumps(out, indent=1))
print("COUNT " + json.dumps(out), flush=True)
EOF
echo COUNT_DONE
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
        return {"_raw": out[:300]}


if __name__ == "__main__":
    common = {"name": "wallart-count", "templateId": TEMPLATE,
              "imageName": "runpod/base:0.7.0-ubuntu2404",
              "containerDiskInGb": 20, "volumeInGb": 0,
              "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", SCRIPT]}
    pid = None
    for extra in ({"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"],
                   "vcpuCount": 4},
                  {"gpuTypeIds": ["NVIDIA RTX A4000", "NVIDIA RTX A4500",
                                  "NVIDIA GeForce RTX 3090"],
                   "gpuCount": 1, "cloudType": "COMMUNITY"}):
        r = curl("POST", "/pods", dict(common, **extra))
        if isinstance(r, dict) and r.get("id"):
            pid = r["id"]
            print(f"pod {pid} ${r.get('costPerHr')}/hr", flush=True)
            break
    if not pid:
        sys.exit("no pod")
    try:
        for i in range(45):
            time.sleep(20)
            out = subprocess.run(
                ["curl", "-sS", "--max-time", "60",
                 f"https://{pid}-8000.proxy.runpod.net/count.json"],
                capture_output=True, text=True).stdout
            try:
                d = json.loads(out)
            except Exception:
                continue
            print(json.dumps(d, indent=1))
            print(f"\n{d['total']:,} panels  ->  {d['listings']:,} listings")
            sys.exit(0)
        print("gave up waiting")
    finally:
        curl("DELETE", f"/pods/{pid}")
        print(f"pod {pid} deleted")
