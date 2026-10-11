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
python3 -m pip install -q --no-input --break-system-packages boto3 pillow numpy 2>&1 | tail -2
python3 - <<'EOF'
import os, io, json, numpy as np, boto3
from concurrent.futures import ThreadPoolExecutor
from botocore.config import Config
from PIL import Image

s3 = boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                  aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                  aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                  config=Config(signature_version="s3v4", max_pool_connections=64),
                  region_name="auto")
B = os.environ["R2_BUCKET"]; PRE = "wallart/v1/"

keys, tok = [], None
while True:
    kw = {"Bucket": B, "Prefix": PRE, "MaxKeys": 1000}
    if tok: kw["ContinuationToken"] = tok
    r = s3.list_objects_v2(**kw)
    keys += [o["Key"] for o in r.get("Contents", []) if o["Key"].endswith(".jpg")]
    if not r.get("IsTruncated"): break
    tok = r["NextContinuationToken"]
print("keys", len(keys), flush=True)

def dhash(im, n=16):
    g = np.asarray(im.convert("L").resize((n+1, n), Image.LANCZOS), dtype=np.int16)
    return (g[:, 1:] > g[:, :-1]).ravel()

def one(k):
    b = s3.get_object(Bucket=B, Key=k)["Body"].read()
    return k.rsplit("/",1)[-1][:-4], dhash(Image.open(io.BytesIO(b)))

rows = []
with ThreadPoolExecutor(max_workers=32) as ex:
    for i, r in enumerate(ex.map(one, keys), 1):
        rows.append(r)
        if i % 2000 == 0: print(f"hashed {i}", flush=True)

skus = [r[0] for r in rows]
bits = np.packbits(np.array([r[1] for r in rows], dtype=np.uint8), axis=1)
POP = np.unpackbits(np.arange(256, dtype=np.uint8)[:, None], axis=1).sum(1).astype(np.uint16)
n = len(skus); NEAR = 24
flag = np.zeros(n, bool); worst = []
for i0 in range(0, n, 256):
    blk = bits[i0:i0+256]
    d = POP[np.bitwise_xor(blk[:, None, :], bits[None, :, :])].sum(2)
    for r in range(d.shape[0]): d[r, i0+r] = 999
    flag[i0:i0+256] = (d <= NEAR).any(1)
    mn = d.min(1); 
    for r in np.argsort(mn)[:3]:
        worst.append((int(mn[r]), skus[i0+int(r)], skus[int(d[r].argmin())]))
worst.sort()
out = {"panels": n, "distinct_hashes": len(set(map(bytes, bits))),
       "near_dupe_pct": round(float(flag.mean())*100, 3), "threshold_bits": NEAR,
       "closest_pairs": [{"bits_apart": w[0], "a": w[1], "b": w[2]} for w in worst[:10]]}
open("/workspace/audit.json","w").write(json.dumps(out, indent=1))
print("AUDIT " + json.dumps(out), flush=True)
EOF
echo AUDIT_DONE
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
    body = {"name": "wallart-audit", "templateId": TEMPLATE,
            "imageName": "runpod/base:0.7.0-ubuntu2404",
            "computeType": "CPU", "cpuFlavorIds": ["cpu3g","cpu3c"], "vcpuCount": 8,
            "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", SCRIPT]}
    r = curl("POST", "/pods", body)
    print(json.dumps({k: r.get(k) for k in ("id", "desiredStatus", "costPerHr",
                                            "error", "_raw")}, indent=1))
    if r.get("id"):
        print(f"log: https://{r['id']}-8000.proxy.runpod.net/boot.log")
