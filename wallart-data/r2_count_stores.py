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
    TIERS = ({"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"],
                   "vcpuCount": 4},
                  {"gpuTypeIds": ["NVIDIA RTX A4000", "NVIDIA RTX A4500",
                                  "NVIDIA GeForce RTX 3090"],
                   "gpuCount": 1, "cloudType": "COMMUNITY"},
                  # Both of the above came back empty at 20:20 on 13 Oct and
                  # the hourly check had no count at all - the one number the
                  # seller actually reads. The twelve shards were running fine
                  # on exactly these cards, so this is community capacity
                  # fluctuating, not an outage. Two more tiers: the cards the
                  # shards use, and then SECURE, which costs more per hour but
                  # this job lives for about a minute and is billed by the
                  # second. Paying $0.01 instead of $0.003 beats reporting an
                  # estimate.
                  {"gpuTypeIds": ["NVIDIA RTX 4000 Ada Generation",
                                  "NVIDIA RTX A5000", "NVIDIA L4"],
                   "gpuCount": 1, "cloudType": "COMMUNITY"},
                  {"gpuTypeIds": ["NVIDIA RTX A4000", "NVIDIA RTX A4500",
                                  "NVIDIA RTX A5000"],
                   "gpuCount": 1, "cloudType": "SECURE"})

    def start():
        for extra in TIERS:
            r = curl("POST", "/pods", dict(common, **extra))
            if isinstance(r, dict) and r.get("id"):
                print(f"pod {r['id']} ${r.get('costPerHr')}/hr", flush=True)
                return r["id"]
        return None

    def wait(pid, limit):
        """Poll for count.json. True if it answered, False if it never did."""
        for _ in range(limit):
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
            return True
        return False

    # GIVE UP ON A POD THAT WILL NOT BOOT, rather than waiting out the clock.
    # About one run in three gets a host where the pod never serves anything;
    # this used to sit through all fifteen minutes of polling, and twice today
    # the surrounding task was killed first - once by a container restart and
    # once by the 30-minute background limit - which left the pod billing with
    # its finally never reached. A pod that has said nothing in five minutes
    # is not slow, it is the bad case: kill it and take a different host.
    # Two attempts, because the second one has always worked.
    FIRST_CONTACT, ATTEMPTS = 15, 2          # 15 polls x 20s = 5 minutes
    for attempt in range(1, ATTEMPTS + 1):
        pid = start()
        if not pid:
            sys.exit("no pod")
        try:
            if wait(pid, FIRST_CONTACT):
                sys.exit(0)
            print(f"attempt {attempt}: pod {pid} never answered in "
                  f"{FIRST_CONTACT * 20 // 60} minutes", flush=True)
        finally:
            curl("DELETE", f"/pods/{pid}")
            print(f"pod {pid} deleted", flush=True)
    sys.exit("no count after two attempts")
