#!/usr/bin/env python3
"""The owed text sweep over panels written before 11 Oct 22:00.

WHY THE METHOD IN RESUME.md CANNOT WORK. It said "run EasyOCR over the
bottom fifth of each panel". The gate that let these panels through
(777dae2^) ran readtext() on the CROPPED panel with MIN_CONF 0.35,
MIN_AREA 0.0012, MIN_CHARS 2 - and the stored panel IS that cropped panel,
with the same dimensions, so MIN_AREA normalises identically. Anything
readtext() would flag today it flagged then and the panel was never stored.
Re-running it is a no-op by construction, and would have produced a clean
report that meant nothing.

What is actually left in those panels is the top two millimetres of a row of
letters - the GUATEMALA case was caught BY EYE, so it is visible, but
mutilated glyphs are exactly what recognition will not score confidently.
Hence detection without recognition: reader.detect() returns candidate text
boxes and is far more robust to clipped glyphs than readtext(). It is run on
the bottom strip only, where a straddling title has to be.

--sample N measures the rate on N random pre-cutoff panels and builds a
contact sheet of the strongest candidates, because a detector tuned on
nothing is worth nothing and the people gate was settled the same way - by
looking at sixty panels. Without --sample it sweeps all of them.

Nothing is written to the buckets and nothing is deleted. The launcher reaps
the pod; the pod is given no API key.
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
nvidia-smi | head -12
python3 -m pip install -q --no-input --break-system-packages \
    boto3==1.43.114 pillow numpy easyocr==1.7.2 2>&1 | tail -3
(python3 - <<'EOF'
import os, io, json, random, numpy as np, boto3
from concurrent.futures import ThreadPoolExecutor
from botocore.config import Config
from datetime import datetime, timezone
from PIL import Image

SAMPLE = __SAMPLE__
STRIP = 0.10          # bottom tenth: where the old crop line fell
MIN_BOX_AREA = 0.0008

s3 = boto3.client("s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", max_pool_connections=192,
                  connect_timeout=20, read_timeout=90,
                  retries={"max_attempts": 8, "mode": "adaptive"}),
    region_name="auto")

STORES = [("luxvia-art", "luxvia/gen/"), ("posterleaf-store1", "store1/gen/"),
          ("mercury-usm", "store2/gen/"), ("lunar-kms", "store7/gen/")]
CUT = datetime.fromisoformat("__CUTOFF__")

items = []
for bkt, pre in STORES:
    tok = None
    while True:
        kw = {"Bucket": bkt, "Prefix": pre, "MaxKeys": 1000}
        if tok: kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            if not o["Key"].endswith(".jpg"): continue
            t = o["LastModified"]
            if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
            if t < CUT: items.append((bkt, o["Key"]))
        if not r.get("IsTruncated"): break
        tok = r["NextContinuationToken"]
print(f"pre-cutoff panels: {len(items)}", flush=True)
random.Random(0).shuffle(items)
if SAMPLE: items = items[:SAMPLE]
print(f"examining {len(items)}", flush=True)

import easyocr
reader = easyocr.Reader(["en"], gpu=True, verbose=False)

MIN_CONF, MIN_AREA, MIN_CHARS = 0.35, 0.0012, 2

def fetch(it):
    bkt, k = it
    try:
        b = s3.get_object(Bucket=bkt, Key=k)["Body"].read()
        return bkt, k.rsplit("/", 1)[-1][:-4], Image.open(io.BytesIO(b)).convert("RGB")
    except Exception:
        return None

recog_hits, det_hits, missed, seen = [], [], 0, 0
cands = []
with ThreadPoolExecutor(max_workers=64) as ex:
    for res in ex.map(fetch, items):
        if res is None:
            missed += 1
            continue
        bkt, sku, im = res
        seen += 1
        W, H = im.size
        a = np.asarray(im)

        # (A) the OLD gate, verbatim, on the stored panel. Expected to find
        # nothing - that is the point being demonstrated, not assumed.
        for box, txt, conf in reader.readtext(a):
            t = "".join(c for c in txt if c.isalnum())
            if len(t) < MIN_CHARS or conf < MIN_CONF: continue
            xs = [p[0] for p in box]; ys = [p[1] for p in box]
            if (max(xs)-min(xs)) * (max(ys)-min(ys)) / (W*H) >= MIN_AREA:
                recog_hits.append({"sku": sku, "txt": txt,
                                   "conf": round(float(conf), 2)})
                break

        # (B) DETECTION ONLY, bottom strip. Robust to clipped glyphs.
        y0 = int(H * (1 - STRIP))
        strip = a[y0:, :, :]
        try:
            res_d = reader.detect(strip)
            boxes = res_d[0][0] if res_d and res_d[0] else []
        except Exception as e:
            boxes = []
        best = 0.0
        for bx in boxes:
            x1, x2, y1, y2 = bx[0], bx[1], bx[2], bx[3]
            ar = abs(x2-x1) * abs(y2-y1) / (W * strip.shape[0])
            best = max(best, ar)
        if best >= MIN_BOX_AREA:
            det_hits.append({"sku": sku, "area": round(best, 4)})
            cands.append((best, sku, im.crop((0, y0, W, H))))
        if seen % 200 == 0:
            print(f"examined {seen}  recog {len(recog_hits)}  "
                  f"detect {len(det_hits)}", flush=True)

out = {"pre_cutoff_total": len(items) if not SAMPLE else None,
       "examined": seen, "missed": missed,
       "old_gate_rerun_hits": len(recog_hits),
       "old_gate_rerun_pct": round(100.0 * len(recog_hits) / max(seen, 1), 3),
       "detector_hits": len(det_hits),
       "detector_pct": round(100.0 * len(det_hits) / max(seen, 1), 3),
       "strip": STRIP, "min_box_area": MIN_BOX_AREA,
       "recog_examples": recog_hits[:20],
       "detector_examples": sorted(det_hits, key=lambda d: -d["area"])[:40]}
open("/workspace/sweep.json", "w").write(json.dumps(out, indent=1))
print("SWEEP " + json.dumps({k: v for k, v in out.items()
                             if not k.endswith("examples")}), flush=True)

# A contact sheet of the strongest candidates, so a person can see whether
# the detector is finding letters or finding texture.
cands.sort(key=lambda c: -c[0])
cands = cands[:40]
if cands:
    cw = 352
    rows = [c[2].resize((cw, max(1, int(c[2].height * cw / c[2].width))))
            for c in cands]
    rh = max(r.height for r in rows)
    cols, per = 2, (len(rows) + 1) // 2
    sheet = Image.new("RGB", (cw * cols, rh * per), "white")
    for i, r in enumerate(rows):
        sheet.paste(r, ((i % cols) * cw, (i // cols) * rh))
    sheet.save("/workspace/sheet.jpg", quality=88)
    open("/workspace/sheet_skus.txt", "w").write(
        "\n".join(f"{a:.4f}\t{s}" for a, s, _ in cands))
    print(f"sheet: {len(cands)} strips", flush=True)
EOF
) && echo SWEEP_DONE || echo SWEEP_FAILED
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
    known = {"--dry-run", "--sample"}
    bad = [a for a in sys.argv[1:] if a.startswith("-") and a not in known]
    if bad:
        print(f"unknown flag {bad[0]} - this script starts a billing pod. "
              f"Known: {' '.join(sorted(known))}")
        sys.exit(2)
    sample = 0
    if "--sample" in sys.argv:
        sample = int(sys.argv[sys.argv.index("--sample") + 1].replace(",", ""))
    script = (SCRIPT.replace("__SAMPLE__", str(sample))
                    .replace("__CUTOFF__", CUTOFF))
    assert "__SAMPLE__" not in script and "__CUTOFF__" not in script
    print(f"sweep: {'all pre-cutoff panels' if not sample else f'{sample:,} sampled'}")
    if "--dry-run" in sys.argv:
        print(f"dry run, nothing created. {len(script):,} chars")
        sys.exit(0)
    common = {"name": "wallart-sweep", "templateId": TEMPLATE,
              "imageName": "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04",
              "containerDiskInGb": 40, "volumeInGb": 0,
              "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", script]}
    for gpus in (["NVIDIA RTX A4500", "NVIDIA RTX A4000", "NVIDIA RTX A5000"],
                 ["NVIDIA GeForce RTX 3090", "NVIDIA RTX 4000 Ada Generation"]):
        r = curl("POST", "/pods", dict(common, gpuTypeIds=gpus, gpuCount=1,
                                       cloudType="COMMUNITY"))
        if isinstance(r, dict) and r.get("id"):
            pid = r["id"]
            print(f"pod {pid} ${r.get('costPerHr')}")
            break
        print("refused:", str(r)[:160])
    else:
        sys.exit(1)

    import time
    try:
        for _ in range(90):
            time.sleep(20)
            out = subprocess.run(
                ["curl", "-sS", "--max-time", "60",
                 f"https://{pid}-8000.proxy.runpod.net/sweep.json"],
                capture_output=True, text=True).stdout
            try:
                d = json.loads(out)
            except Exception:
                continue
            print(json.dumps(d, indent=1)[:1500])
            for name in ("sheet.jpg", "sheet_skus.txt", "sweep.json"):
                subprocess.run(
                    ["curl", "-sS", "--max-time", "120", "-o",
                     f"/tmp/sweep_{name}",
                     f"https://{pid}-8000.proxy.runpod.net/{name}"])
            print("downloaded sheet.jpg, sheet_skus.txt, sweep.json to /tmp")
            sys.exit(0)
        print("gave up waiting")
    finally:
        curl("DELETE", f"/pods/{pid}")
        print(f"pod {pid} deleted")
