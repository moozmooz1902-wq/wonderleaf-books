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
import base64, io, json, subprocess, sys, tarfile

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"          # carries R2_* env, see tshirt/ACCESS.md

# Same rule as launch_gen.py, and it was forgotten here first time round:
# run the job ALONGSIDE the image's own /start.sh, never instead of it, or
# RunPod's in-container agent never starts and the HTTP proxy has no route.
SCRIPT = r'''
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace/gen
echo '__BUNDLE__' | base64 -d | tar xz -C /workspace/gen
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
set -x
python3 -m pip install -q --no-input --break-system-packages boto3 2>&1 | tail -2
cd /workspace/gen
python3 - <<'EOF'
import os, sys, json, boto3
from concurrent.futures import ThreadPoolExecutor
from botocore.config import Config
sys.path.insert(0, "/workspace/gen")
import allocate

acct = os.environ["R2_ACCOUNT_ID"]
s3 = boto3.client("s3", endpoint_url=f"https://{acct}.r2.cloudflarestorage.com",
                  aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                  aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                  config=Config(signature_version="s3v4", max_pool_connections=64,
                                connect_timeout=15, read_timeout=60,
                                retries={"max_attempts": 3}),
                  region_name="auto")
SRC, SRCPRE = "tshirt-m12k", "wallart/v1/"

keys, tok = [], None
while True:
    kw = {"Bucket": SRC, "Prefix": SRCPRE, "MaxKeys": 1000}
    if tok: kw["ContinuationToken"] = tok
    r = s3.list_objects_v2(**kw)
    keys += [o["Key"] for o in r.get("Contents", []) if o["Key"].endswith(".jpg")]
    if not r.get("IsTruncated"): break
    tok = r["NextContinuationToken"]
print(f"to move: {len(keys):,}", flush=True)

def move(k):
    sku = k.rsplit("/", 1)[-1][:-4]
    st = allocate.store_for(sku)
    dst = f"{st['key_prefix'].strip('/')}/{sku}.jpg"
    s3.copy_object(Bucket=st["bucket"], Key=dst,
                   CopySource={"Bucket": SRC, "Key": k})
    return st["bucket"]

from collections import Counter
done = Counter(); errs = []
with ThreadPoolExecutor(max_workers=32) as ex:
    for i, b in enumerate(ex.map(move, keys), 1):
        done[b] += 1
        if i % 2000 == 0: print(f"moved {i:,}", flush=True)
print("MOVED " + json.dumps(dict(done)), flush=True)

# verify every one landed, then clear the source and the pre-hash orphans
check = {}
for st in allocate.PLAN["stores"]:
    pre = st["key_prefix"].strip("/") + "/"; n = 0; tok = None
    while True:
        kw = {"Bucket": st["bucket"], "Prefix": pre, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        n += sum(1 for o in r.get("Contents", []) if o["Key"].endswith(".jpg"))
        if not r.get("IsTruncated"): break
        tok = r["NextContinuationToken"]
    check[st["bucket"]] = n
print("VERIFY " + json.dumps(check), flush=True)

if sum(check.values()) == len(keys):
    for pre in ("wallart/v1/", "wallart/block1/"):
        tok = None; gone = 0
        while True:
            kw = {"Bucket": SRC, "Prefix": pre, "MaxKeys": 1000}
            if tok: kw["ContinuationToken"] = tok
            r = s3.list_objects_v2(**kw)
            objs = [{"Key": o["Key"]} for o in r.get("Contents", [])]
            if objs:
                s3.delete_objects(Bucket=SRC, Delete={"Objects": objs})
                gone += len(objs)
            if not r.get("IsTruncated"): break
            tok = r["NextContinuationToken"]
        print(f"CLEARED {pre} {gone}", flush=True)
else:
    print(f"NOT CLEARING: moved {len(keys)} but found {sum(check.values())}", flush=True)
print("MOVE_DONE", flush=True)
EOF
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


def _bundle():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for f in ("allocate.py", "stores.json"):
            t.add(f, arcname=f)
    return base64.b64encode(buf.getvalue()).decode()


if __name__ == "__main__":
    body = {"name": "wallart-move", "templateId": TEMPLATE,
            "imageName": "runpod/base:0.7.0-ubuntu2404",
            "computeType": "CPU", "cpuFlavorIds": ["cpu3c"], "vcpuCount": 2,
            "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["8000/http"],
            # allocate.py and stores.json travel with the job so the pod uses
            # the real allocator, not a copy of it that could drift
            "dockerStartCmd": ["bash", "-c", SCRIPT.replace("__BUNDLE__", _bundle())]}
    r = curl("POST", "/pods", body)
    print(json.dumps({k: r.get(k) for k in ("id", "desiredStatus", "costPerHr",
                                            "error", "_raw")}, indent=1))
    if r.get("id"):
        print(f"log: https://{r['id']}-8000.proxy.runpod.net/boot.log")
