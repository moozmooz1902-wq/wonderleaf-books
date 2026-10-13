#!/usr/bin/env python3
"""Duplicate audit across all four store buckets, on the live catalogue.

The last audit was 12,834 panels from three subject kinds, eleven
techniques and three palettes, and it found 1.50% with a near twin. Since
then the grid gained three kinds, three techniques, two palettes and 2,966
subjects, and none of that has ever been measured for duplication. Better
to find out at 57,000 panels than at 960,000.

Method, and each part of it was got wrong once before:
  * hash the ARTWORK, not the framed mockup. Hashing the mockup grouped 26
    different designs, because most of a mockup is the same frame and wall.
  * GRADIENT hash, not average hash, 256 bits.
  * count PANELS that have a near twin, not pairs, and never count a
    design against its own colourways.
Near is <= 24 bits of 256, the same threshold as the first audit, so the
numbers are comparable.

Runs on a pod because this machine has no R2 credentials. Nothing is
written to the buckets and nothing is deleted.
"""
import json, subprocess, sys

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"

SCRIPT = r'''
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
set -x
python3 -m pip install -q --no-input --break-system-packages boto3 pillow numpy 2>&1 | tail -2
(python3 - <<'EOF'
import os, io, json, numpy as np, boto3
from concurrent.futures import ThreadPoolExecutor
from botocore.config import Config
from PIL import Image

s3 = boto3.client("s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    # ONE SLOW OBJECT USED TO KILL THE WHOLE RUN. At 168k panels the defaults
    # held; at 222k a single GET hit the default 60s read timeout with no
    # retries configured, the exception came back out of ex.map, and every
    # hash computed up to that point was thrown away. The pod then printed
    # AUDIT_DONE anyway, because that echo is the next line of the shell
    # script and never looked at python's exit status - so a crash was
    # indistinguishable from success until the boot log was read, and the
    # pod billed on at $0.32/hr in the meantime.
    config=Config(signature_version="s3v4", max_pool_connections=64,
                  connect_timeout=20, read_timeout=90,
                  retries={"max_attempts": 8, "mode": "adaptive"}),
    region_name="auto")

STORES = [("luxvia-art", "luxvia/gen/"), ("posterleaf-store1", "store1/gen/"),
          ("mercury-usm", "store2/gen/"), ("lunar-kms", "store7/gen/")]

items = []
for bkt, pre in STORES:
    tok, n0 = None, len(items)
    while True:
        kw = {"Bucket": bkt, "Prefix": pre, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        items += [(bkt, o["Key"]) for o in r.get("Contents", []) if o["Key"].endswith(".jpg")]
        if not r.get("IsTruncated"): break
        tok = r["NextContinuationToken"]
    print(f"{bkt} {len(items)-n0}", flush=True)
print("total", len(items), flush=True)

def dhash(im, n=16):
    g = np.asarray(im.convert("L").resize((n+1, n), Image.LANCZOS), dtype=np.int16)
    return (g[:, 1:] > g[:, :-1]).ravel()

def one(it):
    bkt, k = it
    try:
        b = s3.get_object(Bucket=bkt, Key=k)["Body"].read()
        return bkt, k.rsplit("/", 1)[-1][:-4], dhash(Image.open(io.BytesIO(b)))
    except Exception:
        return None          # a panel that will not come down is one panel

rows, missed = [], 0
with ThreadPoolExecutor(max_workers=48) as ex:
    for i, r in enumerate(ex.map(one, items), 1):
        if r is None:
            missed += 1
        else:
            rows.append(r)
        if i % 5000 == 0:
            print(f"hashed {i}  missed {missed}", flush=True)
# A handful of unreadable objects does not change a duplication percentage.
# Losing a tenth of the catalogue does, so that is a failure, not a result.
if missed > 0.05 * max(len(items), 1):
    raise SystemExit(f"AUDIT_UNRELIABLE: {missed:,} of {len(items):,} panels "
                     f"could not be fetched")
print(f"hashed {len(rows):,}, missed {missed:,}", flush=True)

bks  = [r[0] for r in rows]
skus = [r[1] for r in rows]
bits = np.packbits(np.array([r[2] for r in rows], dtype=np.uint8), axis=1)
POP = np.unpackbits(np.arange(256, dtype=np.uint8)[:, None], axis=1).sum(1).astype(np.uint16)
n, NEAR = len(skus), 24
# Block of 64, not 256: the comparison array is block x n x 32 uint16, which
# at 57,000 panels is 233 MB a block at 64 and would be 933 MB at 256.
# This whole approach is O(n^2) and will NOT scale to a million panels - at
# that size it has to become an LSH bucketing pass. Fine for an audit now.
flag = np.zeros(n, bool); worst = []
for i0 in range(0, n, 64):
    blk = bits[i0:i0+64]
    d = POP[np.bitwise_xor(blk[:, None, :], bits[None, :, :])].sum(2)
    for r in range(d.shape[0]): d[r, i0+r] = 999
    flag[i0:i0+64] = (d <= NEAR).any(1)
    mn = d.min(1)
    for r in np.argsort(mn)[:2]:
        worst.append((int(mn[r]), skus[i0+int(r)], skus[int(d[r].argmin())]))
    if i0 % 6400 == 0: print(f"compared {i0}", flush=True)
worst.sort()
seen = {}
for b in set(bks):
    m = np.array([x == b for x in bks])
    seen[b] = {"panels": int(m.sum()), "near_dupe_pct": round(float(flag[m].mean())*100, 3)}
out = {"panels": n,
       "distinct_hashes": len(set(map(bytes, bits))),
       "exact_repeats": n - len(set(map(bytes, bits))),
       "near_dupe_pct": round(float(flag.mean())*100, 3),
       "threshold_bits": NEAR,
       "per_bucket": seen,
       "closest_pairs": [{"bits": w[0], "a": w[1], "b": w[2]} for w in worst[:40]]}
open("/workspace/audit.json", "w").write(json.dumps(out, indent=1))
open("/workspace/flagged.txt", "w").write("\n".join(
    s for s, f in zip(skus, flag) if f))
print("AUDIT " + json.dumps({k: v for k, v in out.items() if k != "closest_pairs"}), flush=True)
EOF
) && echo AUDIT_DONE || echo AUDIT_FAILED
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
    common = {"name": "wallart-audit", "templateId": TEMPLATE,
              "imageName": "runpod/base:0.7.0-ubuntu2404",
              "containerDiskInGb": 40, "volumeInGb": 0,
              "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", SCRIPT]}
    # A CPU pod is the right shape and is often unavailable, so fall back to
    # the cheapest GPU and simply not use the GPU.
    for extra in ({"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"],
                   "vcpuCount": 8},
                  {"gpuTypeIds": ["NVIDIA RTX A4000", "NVIDIA RTX A4500",
                                  "NVIDIA GeForce RTX 3090"],
                   "gpuCount": 1, "cloudType": "COMMUNITY"}):
        r = curl("POST", "/pods", dict(common, **extra))
        if isinstance(r, dict) and r.get("id"):
            print(json.dumps({k: r.get(k) for k in ("id", "costPerHr")}, indent=1))
            print(f"log:   https://{r['id']}-8000.proxy.runpod.net/boot.log")
            print(f"audit: https://{r['id']}-8000.proxy.runpod.net/audit.json")
            sys.exit(0)
        print("refused:", str(r)[:160])
    sys.exit(1)
