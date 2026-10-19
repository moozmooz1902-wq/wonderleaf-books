#!/usr/bin/env python3
"""Start a pod that builds one store's eBay upload files and puts them in R2.

The files are large - luxvia-art is about 2 GB of CSV - and the session
container has no R2 credentials, so building here is both faster and the
only way that keeps the credentials on the template where they belong.

The bundle is 29 KB compressed, 39 KB as base64, comfortably inside the
start-command limit. subjects.json is NOT in it: at 90 KB it would not
fit, and the generation run already publishes it to R2, so the pod fetches
it from the same URL the generation pods used. The copy there was checked
byte-for-byte against the local one.

  python3 launch_build.py --store luxvia-art
"""
import argparse, base64, io, json, os, subprocess, sys, tarfile

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"
IMAGE = "runpod/base:0.7.0-ubuntu2404"
HERE = os.path.dirname(os.path.abspath(__file__))
# (path on disk, name inside the bundle)
FILES = [("render/build_pod.py", "build_pod.py"), ("grid.py", "grid.py"),
         ("gen/prompts.py", "prompts.py"), ("build_ebay.py", "build_ebay.py"),
         ("listing_text.py", "listing_text.py"), ("allocate.py", "allocate.py"),
         ("ip_check.py", "ip_check.py"), ("dup_audit.py", "dup_audit.py"),
         ("stores.json", "stores.json"), ("ebay_plan.json", "ebay_plan.json")]


def curl(method, path, body=None):
    cmd = ["curl", "-sS", "--max-time", "90", "-X", method, f"{API}{path}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"_raw": out[:400]}


def bundle():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:xz") as t:
        for src, name in FILES:
            t.add(os.path.join(HERE, src), arcname=name)
    return base64.b64encode(buf.getvalue()).decode()


def start_cmd(b64, store, prefix):
    return ["bash", "-c", f"""export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace/b
echo '{b64}' | base64 -d | tar xJ -C /workspace/b
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
set -x
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
python3 -m pip install -q --no-input --break-system-packages boto3 numpy 2>&1 | tail -2
cd /workspace/b
python3 build_pod.py --store {store} --prefix {prefix} --out /workspace/ebay
echo BUILD_EXIT
EOS
nohup bash /workspace/run.sh > /workspace/boot.log 2>&1 &
if [ -x /start.sh ]; then exec /start.sh; else sleep infinity; fi
"""]


# Enough disk for the CSVs and the zip side by side, and enough RAM for the
# duplicate audit's packed hashes.
TIERS = [{"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"], "vcpuCount": 16},
         {"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"], "vcpuCount": 8},
         {"computeType": "CPU", "cpuFlavorIds": ["cpu5c", "cpu3c"], "vcpuCount": 8}]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--prefix", default="ebay")
    ap.add_argument("--disk", type=int, default=120)
    a = ap.parse_args()
    b64 = bundle()
    cmd = start_cmd(b64, a.store, a.prefix)
    n = sum(len(x) for x in cmd)
    print(f"bundle {len(b64):,} chars, start command {n:,}")
    if n > 60000:
        sys.exit("start command over the pod limit")
    common = {"name": f"wa-build-{a.store}", "templateId": TEMPLATE,
              "imageName": IMAGE, "containerDiskInGb": a.disk,
              "volumeInGb": 0, "ports": ["8000/http"], "dockerStartCmd": cmd}
    for extra in TIERS:
        r = curl("POST", "/pods", dict(common, **extra))
        if isinstance(r, dict) and r.get("id"):
            print(f"  {r['id']}  ${r.get('costPerHr')}/hr  "
                  f"{extra['vcpuCount']} vCPU")
            return
    print("  NO CAPACITY")


if __name__ == "__main__":
    main()
