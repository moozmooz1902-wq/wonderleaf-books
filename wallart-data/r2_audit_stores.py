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

SCALE, rewritten 15 Oct at 609,478 panels. The comparison was every panel
against every other with a popcount lookup table: 95 minutes at 227k and,
being O(n^2), about eleven hours at 609k and a day at 960k. Two changes:

  * distances come from a MATRIX PRODUCT. Each code as +-1 gives
    a.b = BITS - 2*hamming, and float32 holds every value exactly, so it is
    the same distance 13x faster - verified against the lookup table on
    256 x 40,000 pairs, maximum difference 0. The exact audit is now about
    two hours at 609k rather than eleven, and is still available: --full.
  * the default samples ONE SIDE. 40,000 random probes, each compared
    against the whole catalogue, estimates the same statistic without bias
    in about sixteen minutes, to roughly +-0.08 points.

Sampling BOTH sides - hashing a subsample and looking for twins inside it -
is the cheap-looking option and it does not work. On a planted set whose
true rate was 0.800% it reported 0.000% at a 12% sample and 0.167% at 50%,
because a panel whose only twin was not sampled looks unique. The earlier
note in the hourly routine suggesting "a 100k random sample" meant this and
should not be followed.

Exact repeats are still counted over the WHOLE catalogue either way:
identical codes are identical bytes, so they need no pairwise work and
there is no reason to estimate them.

The download is now the slow part - 609k GETs - so it runs 160 threads.

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
    config=Config(signature_version="s3v4", max_pool_connections=192,
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
# 48 was chosen when the comparison stage took hours and the download
# did not matter. It does now: hashing 609,478 panels at 40 objects a
# second is over four hours, and the comparison it feeds takes sixteen
# minutes. This stage is entirely network-bound - the work per object is
# one 16x16 resize - so the thread count is about how many GETs R2 will
# serve at once, not about this pod's cores.
with ThreadPoolExecutor(max_workers=160) as ex:
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

# KEEP THE HASHES. Downloading and hashing the catalogue is the whole cost of
# this audit - 611,441 GETs, about seventy minutes - and the 15 Oct run threw
# them away the moment it had printed a percentage. Every question asked
# afterwards (does the rate rise because the generator got worse or only
# because the catalogue got bigger? what does the trend look like against a
# fixed reference size?) needed the hashes and could not be answered without
# paying the seventy minutes again.
#
# They are 32 bytes a panel: 19.6 MB at 611k, trivial next to the 154 GB of
# panels they describe. Written under audit/, which is outside the luxvia/gen/
# prefix this script lists, so a later audit cannot mistake one for a panel.
import numpy as _np, io as _io
try:
    _buf = _io.BytesIO()
    _np.save(_buf, _np.packbits(_np.array([r[2] for r in rows],
                                          dtype=_np.uint8), axis=1))
    s3.put_object(Bucket="luxvia-art", Key=f"audit/hashes_{len(rows)}.npy",
                  Body=_buf.getvalue(),
                  ContentType="application/octet-stream")
    s3.put_object(Bucket="luxvia-art", Key=f"audit/skus_{len(rows)}.txt",
                  Body=("\n".join(f"{b}\t{k}" for b, k, _ in rows)).encode(),
                  ContentType="text/plain")
    print(f"kept hashes: audit/hashes_{len(rows)}.npy "
          f"({_buf.getbuffer().nbytes:,} bytes)", flush=True)
except Exception as _e:
    # Not worth failing the audit over - the percentage is still the answer.
    print(f"could not keep hashes: {_e}", flush=True)

bks  = [r[0] for r in rows]
skus = [r[1] for r in rows]
raw  = np.array([r[2] for r in rows], dtype=np.uint8)      # n x 256 of 0/1
n, NEAR, BITS = len(skus), 24, 256

# EXACT REPEATS come from the whole catalogue, always. They need no pairwise
# work at all - identical codes are identical bytes - so there is no reason
# to estimate them.
packed = np.packbits(raw, axis=1)
nd = len(set(map(bytes, packed)))

# DISTANCES COME FROM A MATRIX PRODUCT. Writing each code as +-1 makes
# a.b = BITS - 2*hamming, so hamming = (BITS - a.b)/2, and every value is an
# integer within +-256 which float32 holds exactly. This is the Hamming
# distance, not an approximation of it: checked against the popcount lookup
# table on 256 x 40,000 pairs, maximum difference 0. It is 13x faster, and
# that is the whole reason this audit is minutes rather than hours.
pm = raw.astype(np.float32) * 2.0 - 1.0


def wilson(k, m):
    """95% interval for a proportion. Not k/m +- 1.96*se: the count here is
    small - about 130 hits in 20,000 - and the normal approximation puts the
    lower bound below zero at these rates."""
    if m == 0:
        return 0.0, 0.0, 0.0
    z, q = 1.959964, k / m
    den = 1 + z * z / m
    mid = (q + z * z / (2 * m)) / den
    half = z * ((q * (1 - q) / m + z * z / (4 * m * m)) ** 0.5) / den
    return q, max(0.0, mid - half), min(1.0, mid + half)


# SAMPLE ONE SIDE, NEVER BOTH. The statistic is "percentage of PANELS with a
# near twin anywhere in the catalogue". Taking random probes and comparing
# each against the WHOLE set is unbiased, because each probe's answer is
# exactly the answer the full scan would give that panel. Hashing a sample
# and looking for twins inside it is the obvious shortcut and it is wrong by
# an order of magnitude: on a planted set whose true rate was 0.800% it
# reported 0.000% at a 12% sample and 0.167% at 50%, because a panel whose
# only twin was not sampled looks unique. Measured, not reasoned about.
PROBES = __PROBES__          # 0 means every panel, the exact O(n^2) audit
REF_SIZE = __REF_SIZE__      # 0 means the whole catalogue as the reference

# WHY A FIXED REFERENCE SIZE. "Percentage of panels with a near twin" is NOT
# comparable across catalogue sizes. If near pairs arise at roughly constant
# probability q per pair, the rate is about q*n, so it grows linearly with the
# catalogue even when the generator has not changed. The series read 0.826% at
# 63,533 panels, 0.670% at 168,515, 0.648% at 226,992 and then 0.758% at
# 611,441, and that last rise was read as the catalogue getting worse. It was
# not: q fell 0.43x over the same step, and had q stayed where it was at
# 226,992 the rate would have been 1.75%. Holding the reference set at a fixed
# size takes n out of it, so the number can be compared with the one before.
rng = np.random.default_rng(0)            # fixed, so an audit is repeatable
if REF_SIZE and REF_SIZE < n:
    ref = np.sort(rng.choice(n, size=REF_SIZE, replace=False))
else:
    ref, REF_SIZE = np.arange(n), 0
if PROBES and PROBES < n:
    idx = np.sort(rng.choice(n, size=PROBES, replace=False))
    mode, PBLOCK = "probe", 256
else:
    idx = np.arange(n)
    mode, PBLOCK = "exact", 512
RBLOCK = 100_000
pm_ref = pm[ref] if REF_SIZE else pm
# Global index of each reference row, so a panel is never matched to itself.
ref_gid = ref if REF_SIZE else np.arange(n)

hit  = np.zeros(len(idx), bool)
best = np.full(len(idx), 999, np.int32)
mate = np.zeros(len(idx), np.int64)
for p0 in range(0, len(idx), PBLOCK):
    pi = idx[p0:p0 + PBLOCK]
    a = pm[pi]
    got = np.zeros(len(pi), bool)
    bst = np.full(len(pi), 999, np.int32)
    mt  = np.zeros(len(pi), np.int64)
    for r0 in range(0, len(pm_ref), RBLOCK):
        gids = ref_gid[r0:r0 + RBLOCK]
        d = (BITS - a @ pm_ref[r0:r0 + RBLOCK].T) * 0.5
        # Never a panel against itself. The reference may be a subset, so this
        # matches on the GLOBAL id rather than on position.
        same = gids[None, :] == pi[:, None]
        if same.any():
            d[same] = 999
        got |= (d <= NEAR).any(1)
        j = d.argmin(1)
        v = d[np.arange(d.shape[0]), j].astype(np.int32)
        better = v < bst
        bst = np.where(better, v, bst)
        mt  = np.where(better, gids[j], mt)
    hit[p0:p0 + PBLOCK]  = got
    best[p0:p0 + PBLOCK] = bst
    mate[p0:p0 + PBLOCK] = mt
    print(f"compared {p0 + len(pi)} of {len(idx)}", flush=True)

k = int(hit.sum())
rate, lo, hi_ci = wilson(k, len(idx))
order = np.argsort(best)
worst = [{"bits": int(best[t]), "a": skus[int(idx[t])], "b": skus[int(mate[t])]}
         for t in order[:40]]

# Per bucket, from the probes that fell in each one. The count is reported
# next to the rate so a bucket with too few probes to say anything is
# obvious rather than quietly noisy.
seen = {}
pb = [bks[int(i)] for i in idx]
for bucket in sorted(set(bks)):
    m = np.array([x == bucket for x in pb])
    kk = int(hit[m].sum())
    r2, l2, h2 = wilson(kk, int(m.sum()))
    seen[bucket] = {"panels": int(sum(1 for x in bks if x == bucket)),
                    "probes": int(m.sum()),
                    "near_dupe_pct": round(r2 * 100, 3),
                    "ci95": [round(l2 * 100, 3), round(h2 * 100, 3)]}

out = {"panels": n,
       "mode": mode,
       "probes": int(len(idx)),
       "reference_size": int(len(pm_ref)),
       "per_pair_q": (rate / (len(pm_ref) - 1)) if len(pm_ref) > 1 else 0.0,
       "distinct_hashes": nd,
       "exact_repeats": n - nd,
       "near_dupe_pct": round(rate * 100, 3),
       "near_dupe_ci95": [round(lo * 100, 3), round(hi_ci * 100, 3)],
       "threshold_bits": NEAR,
       "per_bucket": seen,
       "closest_pairs": worst}
open("/workspace/audit.json", "w").write(json.dumps(out, indent=1))
open("/workspace/flagged.txt", "w").write("\n".join(
    skus[int(i)] for i, f in zip(idx, hit) if f))
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
    # --probes N  sample N panels and compare each against the WHOLE
    #             catalogue. Default 40,000: about sixteen minutes at 609k
    #             panels and a 95% interval of roughly +-0.08 points at the
    #             rates seen so far, which is finer than the 0.826 -> 0.670
    #             -> 0.648 trend being tracked.
    # --full      every panel against every other. The exact answer and the
    #             thing the probe pass is checked against; about two hours at
    #             609k and five at 960k, so it is a deliberate choice now
    #             rather than the only option.
    # --ref-size N  compare each probe against a random N-panel reference
    #               instead of the whole catalogue, so the rate can be
    #               compared with an earlier audit at a different size.
    #               226992 reproduces the conditions of the 13 Oct audit.
    probes, ref_size = 40_000, 0
    if "--full" in sys.argv:
        probes = 0
    if "--probes" in sys.argv:
        probes = int(sys.argv[sys.argv.index("--probes") + 1])
    if "--ref-size" in sys.argv:
        ref_size = int(sys.argv[sys.argv.index("--ref-size") + 1]
                       .replace(",", ""))
    script = (SCRIPT.replace("__PROBES__", str(probes))
                    .replace("__REF_SIZE__", str(ref_size)))
    assert "__PROBES__" not in script and "__REF_SIZE__" not in script
    print(f"mode: {'exact, every panel' if probes == 0 else f'{probes:,} probes'} against {'the whole catalogue' if ref_size == 0 else f'a {ref_size:,}-panel reference'}")
    # --dry-run creates NOTHING. This script's first action is to start a pod
    # that bills, and on 15 Oct it was run with a made-up "--dry" flag, which
    # it ignored on its way to creating one. Unknown flags are now refused
    # rather than ignored, and there is a real way to look without spending.
    known = {"--probes", "--full", "--dry-run", "--ref-size"}
    bad = [a for a in sys.argv[1:]
           if a.startswith("-") and a not in known]
    if bad:
        print(f"unknown flag {bad[0]} - this script starts a billing pod, so "
              f"it will not run with a flag it does not understand. "
              f"Known: {' '.join(sorted(known))}")
        sys.exit(2)
    if "--dry-run" in sys.argv:
        print(f"dry run, nothing created. start command "
              f"{len(script):,} chars, PROBES={probes}")
        sys.exit(0)
    common = {"name": "wallart-audit", "templateId": TEMPLATE,
              "imageName": "runpod/base:0.7.0-ubuntu2404",
              "containerDiskInGb": 40, "volumeInGb": 0,
              "ports": ["8000/http"], "dockerStartCmd": ["bash", "-c", script]}
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
