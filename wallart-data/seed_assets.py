#!/usr/bin/env python3
"""Put gen/subjects.json into R2 so pod start commands stop carrying it.

WHY THIS EXISTS. A pod's dockerStartCmd has a hard length limit between
60,000 and 70,000 characters - bisected on 11 Oct, 60k creates, 70k does
not. Over it, RunPod answers "create pod: Something went wrong. Please try
again later or contact support", which is indistinguishable from a real
fault and which relaunch.sh was reporting as NO CAPACITY. That is what
idled six shards for three hours: the subject expansion took the embedded
bundle from about 25,000 characters to 80,371, and EVERY launch after it
failed while the cards were sitting there free.

So the bundle stops growing with the catalogue. subjects.json goes into R2
once, under a public prefix, and every later pod curls it. The code bundle
on its own is 29,016 characters compressed, and it grows slowly.

The chicken and egg - this machine has no R2 credentials, only the pods do
- is settled by making the upload itself a pod. Its start command carries
subjects.json and nothing else: 40,700 characters, comfortably under the
limit, and it does not grow unless the subject lists do.

    python3 seed_assets.py            # upload and verify
"""
import base64, json, lzma, os, subprocess, sys, time

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"
KEY = "wallart/assets/subjects.json"
PUBLIC = "https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev"
HERE = os.path.dirname(os.path.abspath(__file__))


def curl(method, path, body=None):
    cmd = ["curl", "-sS", "--max-time", "90", "-X", method, f"{API}{path}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"error": out[:200]}


def start_cmd(b64):
    return ["bash", "-c", f"""export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace
cat > /workspace/seed.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
set -x
python3 -m pip install -q --no-input --break-system-packages boto3 2>&1 | tail -2
echo '{b64}' | base64 -d | python3 -c "import lzma,sys;sys.stdout.buffer.write(lzma.decompress(sys.stdin.buffer.read()))" > /workspace/subjects.json
python3 - <<'EOF'
import os, boto3
from botocore.config import Config
s3 = boto3.client("s3",
    endpoint_url=f"https://{{os.environ['R2_ACCOUNT_ID']}}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4"), region_name="auto")
b = open("/workspace/subjects.json", "rb").read()
s3.put_object(Bucket=os.environ["R2_BUCKET"], Key="{KEY}", Body=b,
              ContentType="application/json")
print("SEEDED", len(b), "bytes")
EOF
echo SEED_DONE
EOS
nohup bash /workspace/seed.sh > /workspace/boot.log 2>&1 &
if [ -x /start.sh ]; then exec /start.sh; else sleep infinity; fi
"""]


def main():
    raw = open(os.path.join(HERE, "gen", "subjects.json"), "rb").read()
    b64 = base64.b64encode(lzma.compress(raw, preset=9)).decode()
    cmd = start_cmd(b64)
    n = sum(len(x) for x in cmd)
    print(f"subjects.json {len(raw):,} bytes -> start command {n:,} chars")
    if n > 58000:
        raise SystemExit("start command too long - the limit is between 60k and 70k")
    body = {"name": "wa-seed-assets", "imageName": "runpod/base:0.7.0-ubuntu2404",
            "templateId": TEMPLATE,
            "gpuTypeIds": ["NVIDIA RTX A4000", "NVIDIA RTX A4500",
                           "NVIDIA GeForce RTX 3090", "NVIDIA RTX 4000 Ada Generation"],
            "gpuCount": 1, "cloudType": "COMMUNITY",
            "containerDiskInGb": 20, "volumeInGb": 0,
            "ports": ["8000/http"], "dockerStartCmd": cmd}
    r = curl("POST", "/pods", body)
    pid = r.get("id") if isinstance(r, dict) else None
    if not pid:
        raise SystemExit(f"no pod: {r}")
    print(f"pod {pid} at ${r.get('costPerHr')}/hr")
    try:
        url = f"{PUBLIC}/{KEY}"
        for i in range(60):
            time.sleep(20)
            got = subprocess.run(["curl", "-sS", "--max-time", "60", "-o", "/dev/null",
                                  "-w", "%{http_code} %{size_download}", url],
                                 capture_output=True, text=True).stdout.split()
            print(f"  {i*20:>4}s  {url} -> {' '.join(got)}", flush=True)
            if got and got[0] == "200" and int(got[1]) == len(raw):
                print("SEEDED AND VERIFIED")
                return 0
        print("gave up waiting")
        return 1
    finally:
        curl("DELETE", f"/pods/{pid}")
        print(f"pod {pid} deleted")


if __name__ == "__main__":
    sys.exit(main())
