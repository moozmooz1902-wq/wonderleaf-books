#!/usr/bin/env python3
"""How old are the panels in the four store buckets?

Written to size the OWED TEXT SWEEP. RESUME.md put that at "about 14
GPU-hours for a million panels", which is the cost of sweeping EVERYTHING -
but the panels that need sweeping are only those generated before
11 Oct 22:00, when the text gate still read the CROPPED image and a title
straddling the crop line could pass. Everything after that was gated on the
full generation and does not need looking at again.

So the real size of the job is the number of objects older than that cutoff,
and nobody had counted them. If it is 30,000 the sweep is twenty minutes and
can be done now; if it is 400,000 it is an end-of-run job as written.

Listing only - no GETs, nothing downloaded, nothing written. The pod deletes
itself. R2's list_objects_v2 already returns LastModified, so the answer
costs one listing pass.
"""
import json, subprocess, sys

API = "https://rest.runpod.io/v1"
TEMPLATE = "vbsgwyibn1"
CUTOFF = "2026-10-11T22:00:00+00:00"

SCRIPT = r'''
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
mkdir -p /workspace
cat > /workspace/run.sh <<'EOS'
export PATH=/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH
( while true; do python3 -m http.server 8000 --directory /workspace >/dev/null 2>&1; sleep 3; done ) &
set -x
python3 -m pip install -q --no-input --break-system-packages boto3 2>&1 | tail -2
(python3 - <<'EOF'
import os, json, collections, boto3
from botocore.config import Config
from datetime import datetime, timezone

s3 = boto3.client("s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", connect_timeout=20,
                  read_timeout=90, retries={"max_attempts": 8,
                                            "mode": "adaptive"}),
    region_name="auto")

STORES = [("luxvia-art", "luxvia/gen/"), ("posterleaf-store1", "store1/gen/"),
          ("mercury-usm", "store2/gen/"), ("lunar-kms", "store7/gen/")]
CUT = datetime.fromisoformat("__CUTOFF__")

byday = collections.Counter()
before = collections.Counter()
total = 0
for bkt, pre in STORES:
    tok = None
    while True:
        kw = {"Bucket": bkt, "Prefix": pre, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            if not o["Key"].endswith(".jpg"):
                continue
            total += 1
            t = o["LastModified"]
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            byday[t.strftime("%Y-%m-%d")] += 1
            if t < CUT:
                before[bkt] += 1
        if not r.get("IsTruncated"): break
        tok = r["NextContinuationToken"]
    print(f"listed {bkt} running total {total}", flush=True)

out = {"total": total,
       "cutoff": "__CUTOFF__",
       "older_than_cutoff": sum(before.values()),
       "older_per_bucket": dict(before),
       "by_day": dict(sorted(byday.items()))}
open("/workspace/ages.json", "w").write(json.dumps(out, indent=1))
print("AGES " + json.dumps(out), flush=True)
EOF
) && echo AGES_DONE || echo AGES_FAILED
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
    known = {"--dry-run"}
    bad = [a for a in sys.argv[1:] if a.startswith("-") and a not in known]
    if bad:
        print(f"unknown flag {bad[0]} - this script starts a billing pod. "
              f"Known: {' '.join(sorted(known))}")
        sys.exit(2)
    script = SCRIPT.replace("__CUTOFF__", CUTOFF)
    assert "__CUTOFF__" not in script
    if "--dry-run" in sys.argv:
        print(f"dry run, nothing created. {len(script):,} chars, "
              f"cutoff {CUTOFF}")
        sys.exit(0)
    common = {"name": "wallart-ages", "templateId": TEMPLATE,
              "imageName": "runpod/base:0.7.0-ubuntu2404",
              "containerDiskInGb": 20, "volumeInGb": 0,
              "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", script]}
    for extra in ({"computeType": "CPU", "cpuFlavorIds": ["cpu3g", "cpu3c"],
                   "vcpuCount": 4},
                  {"gpuTypeIds": ["NVIDIA RTX A4000", "NVIDIA RTX A4500"],
                   "gpuCount": 1, "cloudType": "COMMUNITY"}):
        r = curl("POST", "/pods", dict(common, **extra))
        if isinstance(r, dict) and r.get("id"):
            pid = r["id"]
            print(f"pod {pid} ${r.get('costPerHr')}")
            break
        print("refused:", str(r)[:160])
    else:
        sys.exit(1)

    # THE LAUNCHER REAPS IT, not the pod itself. An in-pod delete needs
    # $RUNPOD_POD_ID and an API key inside the container, and if either is
    # missing the pod simply bills on with nobody watching. This is the shape
    # r2_count_stores.py uses, and that one has never left a stray.
    import time
    try:
        for _ in range(45):
            time.sleep(20)
            out = subprocess.run(
                ["curl", "-sS", "--max-time", "60",
                 f"https://{pid}-8000.proxy.runpod.net/ages.json"],
                capture_output=True, text=True).stdout
            try:
                d = json.loads(out)
            except Exception:
                continue
            cut = d["older_than_cutoff"]
            print(f"\n{d['total']:,} panels listed")
            print(f"{cut:,} made before {d['cutoff']} - these are the ones "
                  f"the text sweep owes")
            print(f"  per bucket: {d['older_per_bucket']}")
            print(f"\nat ~50 ms a panel that sweep is "
                  f"{cut * 0.05 / 3600:.2f} GPU-hours "
                  f"(${cut * 0.05 / 3600 * 0.19:.2f} on an A4500)")
            print("\nby day:")
            for day, k in d["by_day"].items():
                print(f"  {day}  {k:>8,}")
            open("notes/panel_ages.json", "w").write(json.dumps(d, indent=1))
            print("\nsaved notes/panel_ages.json")
            sys.exit(0)
        print("gave up waiting")
    finally:
        curl("DELETE", f"/pods/{pid}")
        print(f"pod {pid} deleted")
