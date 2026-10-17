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

    # HOW LONG TO WAIT, measured rather than assumed. About one run in three
    # lands on a host that takes far longer than the usual minute, and the
    # first version of this retry gave up after five - which would have
    # aborted every slow run that actually succeeded. Today's three slow
    # counts took 10, 11 and 14 minutes and all three returned a real number:
    #
    #     01:17 -> 01:31   14 min   650,524 panels
    #     04:18 -> 04:28   10 min   669,605
    #     09:19 -> 09:30   11 min   706,336
    #
    # So slow is not dead, and the cutoff has to sit above 14. Fifteen minutes
    # on the first attempt, ten on the second, which keeps the whole run under
    # the 30-minute limit that killed one of these and left a pod billing.
    #
    # The retry still earns its place: it was two consecutive non-answers at
    # 10:34 that showed the five-minute figure was wrong, and a host that
    # really is dead now costs fifteen minutes instead of an open-ended wait.
    # reap_orphans.py is the backstop for the case this cannot cover - being
    # killed outright, so that the finally below never runs at all.
    # ONE ATTEMPT, AND IT MUST FIT INSIDE WHATEVER WRAPS THIS. The two-attempt
    # version budgeted 15 + 10 minutes, and it was being invoked as
    # `timeout 900 python3 r2_count_stores.py` - a 15-minute wrapper around a
    # 25-minute script. On every slow run the wrapper's SIGTERM landed exactly
    # as attempt 1 gave up, so the finally below never ran and the pod was
    # left billing: 99j8mee6om3ly4 on 17 Oct, and the same shape twice before.
    # The stranded pods were never the harness, they were this mismatch.
    #
    # Sixteen minutes covers every slow success measured - 10, 11 and 14 -
    # with margin. THAT IS 960 SECONDS, SO DO NOT WRAP THIS IN `timeout 900`:
    # a 900s wrapper is the same mismatch again, just smaller, and the test
    # that was meant to confirm the fix printed "inside a 900s wrapper? False"
    # and caught it. Invoke it as `timeout 1500 python3 r2_count_stores.py`,
    # which clears 960s plus pod-creation overhead and still sits well inside
    # the 30-minute background limit. The retry is dropped rather than squeezed:
    # it only ever helped on a host that was never going to answer, and the
    # honest response to that is to re-run the count at the next check rather
    # than to overrun the clock that guarantees cleanup.
    for attempt, limit in ((1, 48),):             # 48 polls x 20s = 16 min
        pid = start()
        if not pid:
            sys.exit("no pod")
        try:
            if wait(pid, limit):
                sys.exit(0)
            print(f"attempt {attempt}: pod {pid} never answered in "
                  f"{limit * 20 // 60} minutes", flush=True)
        finally:
            curl("DELETE", f"/pods/{pid}")
            print(f"pod {pid} deleted", flush=True)
    sys.exit("no count: the pod never answered in 16 minutes")
