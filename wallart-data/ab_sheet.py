#!/usr/bin/env python3
"""Two contact sheets, same size, same layout: new prompt beside old prompt.

The A/B that matters is not only the reject rate. Moving the no-people
clause into CLIP's 77-token window cost six tokens off the tail of the
grammar clause, and if that made the compositions worse the change has to
come out however much it helps the gate. A number cannot answer that. This
fetches a sample of panels from the shard running the new prompt and the
same number from a shard still running the old one, tiles each into a
sheet, and leaves them on the pod's web port to be looked at.

Takes two files of SKUs, one per line, and ships them in the command.
Nothing is written to the store buckets and nothing is deleted.

The pod does NOT delete itself. Delete it when the sheets are down.
"""
import base64, json, subprocess, sys

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"

BODY = r'''
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace
echo '__SKUS__' | base64 -d > /workspace/skus.json
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
set -x
python3 -m pip install -q --no-input --break-system-packages boto3 pillow 2>&1 | tail -1
python3 - <<'EOF'
import os, io, json, boto3
from concurrent.futures import ThreadPoolExecutor
from botocore.config import Config
from PIL import Image

s3 = boto3.client("s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", max_pool_connections=32),
    region_name="auto")

# A SKU is routed to one of four buckets at creation and the routing is not
# recorded anywhere this script can see, so each bucket is simply tried.
# Four HEADs per SKU at worst, which is nothing next to the GET.
STORES = [("luxvia-art","luxvia/gen/"), ("posterleaf-store1","store1/gen/"),
          ("mercury-usm","store2/gen/"), ("lunar-kms","store7/gen/")]

def fetch(sku):
    for bkt, pre in STORES:
        try:
            o = s3.get_object(Bucket=bkt, Key=f"{pre}{sku}.jpg")
            return Image.open(io.BytesIO(o["Body"].read())).convert("RGB")
        except Exception:
            continue
    return None

def sheet(skus, name, cols=6, cell=300):
    with ThreadPoolExecutor(24) as ex:
        imgs = [im for im in ex.map(fetch, skus) if im is not None]
    rows = (len(imgs) + cols - 1) // cols
    out = Image.new("RGB", (cols*cell, max(rows,1)*cell), "white")
    for i, im in enumerate(imgs):
        im.thumbnail((cell-6, cell-6))
        out.paste(im, ((i%cols)*cell+3, (i//cols)*cell+3))
    out.save(f"/workspace/{name}.jpg", "JPEG", quality=86)
    print(f"{name}: {len(imgs)} of {len(skus)} found", flush=True)

d = json.load(open("/workspace/skus.json"))
sheet(d["new"], "sheet_new")
sheet(d["old"], "sheet_old")
print("SHEETS_DONE", flush=True)
EOF
echo AB_DONE
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
    new = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    old = [l.strip() for l in open(sys.argv[2]) if l.strip()]
    blob = base64.b64encode(json.dumps({"new": new, "old": old}).encode()).decode()
    script = BODY.replace("__SKUS__", blob)
    common = {"name": "wallart-absheet", "templateId": TEMPLATE,
              "imageName": "runpod/base:0.7.0-ubuntu2404",
              "containerDiskInGb": 30, "volumeInGb": 0,
              "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", script]}
    n = sum(len(x) for x in common["dockerStartCmd"])
    if n > 58000:
        print(json.dumps({"error": f"start command {n:,} chars, too long - "
                                   f"send fewer SKUs"}))
        raise SystemExit(2)
    for extra in ({"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"],
                   "vcpuCount": 8},
                  {"gpuTypeIds": ["NVIDIA RTX A4000", "NVIDIA RTX A4500"],
                   "gpuCount": 1, "cloudType": "COMMUNITY"}):
        r = curl("POST", "/pods", dict(common, **extra))
        if isinstance(r, dict) and r.get("id"):
            print(json.dumps({k: r.get(k) for k in ("id", "costPerHr")}, indent=1))
            for s in ("sheet_new.jpg", "sheet_old.jpg", "boot.log"):
                print(f"  https://{r['id']}-8000.proxy.runpod.net/{s}")
            raise SystemExit(0)
        print("refused:", str(r)[:200])
    raise SystemExit(1)
