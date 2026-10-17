#!/usr/bin/env python3
"""Prove the range partition in r2_count_stores.py counts every key once.

Runs the REAL shipped listing body - extracted from the SCRIPT heredoc, not
a paraphrase of it - against a fake R2 that honours Prefix, StartAfter,
ContinuationToken and MaxKeys, with a key set chosen to break a careless
partition: keys sorting before the first boundary and after the last, keys
sitting exactly ON a boundary, non-.jpg keys, and an empty bucket.
"""
import importlib.util, json, os, random, sys, types

spec = importlib.util.spec_from_file_location(
    "rcs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "r2_count_stores.py"))
rcs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rcs)
body = rcs.SCRIPT.split("python3 - <<'EOF'\n", 1)[1].split("\nEOF\n", 1)[0]

PRES = {"luxvia-art": "luxvia/gen/", "posterleaf-store1": "store1/gen/",
        "mercury-usm": "store2/gen/", "lunar-kms": "store7/gen/"}

random.seed(7)
BUCKETS, TRUTH = {}, {}
for i, (bkt, pre) in enumerate(PRES.items()):
    keys = []
    if bkt != "lunar-kms":                       # one bucket left empty
        for _ in range(4000 + i * 1500):
            keys.append(f"{pre}WA-{random.getrandbits(64):016x}.jpg")
        keys += [
            pre + "WA-0",                        # exactly ON a boundary
            pre + "WA-f",                        # exactly ON the last
            pre + "AAearly.jpg",                 # sorts BEFORE WA-0
            pre + "zzlate.jpg",                  # sorts AFTER WA-g
            pre + "WA-" + "0" * 16 + ".txt",     # not a .jpg
            pre + "WA-" + "f" * 16 + ".jpg",     # top of the last real range
        ]
    keys += ["unrelated/other.jpg", pre.rstrip("/") + "X/strayWA-1.jpg"]
    BUCKETS[bkt] = sorted(set(keys))
    TRUTH[bkt] = sum(1 for k in BUCKETS[bkt]
                     if k.startswith(pre) and k.endswith(".jpg"))

CALLS = [0]


class FakeClient:
    def list_objects_v2(self, **kw):
        CALLS[0] += 1
        keys = [k for k in BUCKETS[kw["Bucket"]] if k.startswith(kw["Prefix"])]
        start = kw.get("ContinuationToken") or kw.get("StartAfter")
        if start is not None:
            keys = [k for k in keys if k > start]
        mk = kw.get("MaxKeys", 1000)
        page, rest = keys[:mk], keys[mk:]
        return {"Contents": [{"Key": k} for k in page],
                "IsTruncated": bool(rest),
                "NextContinuationToken": page[-1] if page and rest else None}


# The body does its own `import os, json, time, boto3` and
# `from botocore.config import Config`, so the stubs go in sys.modules - the
# point is to run the shipped text unedited, not a copy with the imports cut.
fake_boto3 = types.ModuleType("boto3")
fake_boto3.client = lambda *a, **k: FakeClient()
sys.modules["boto3"] = fake_boto3
fake_botocore = types.ModuleType("botocore")
fake_cfg = types.ModuleType("botocore.config")
fake_cfg.Config = lambda **k: None
fake_botocore.config = fake_cfg
sys.modules["botocore"] = fake_botocore
sys.modules["botocore.config"] = fake_cfg

# Real os - stubbing the module broke logging, which concurrent.futures
# imports. Only the three values the body reads are faked, and they are
# placeholders: the real keys live on the RunPod template and never here.
import os
os.environ.update({"R2_ACCOUNT_ID": "x", "R2_ACCESS_KEY_ID": "y",
                   "R2_SECRET_ACCESS_KEY": "z"})

written = {}
g = {
    "print": lambda *a, **k: None,
    "open": lambda p, m="r": type("W", (), {
        "write": lambda _s, d: written.__setitem__(p, d)})(),
}
exec(compile(body, "SCRIPT-body", "exec"), g)

got = json.loads(written["/workspace/count.json"])
print(f"{CALLS[0]} LIST calls")
ok = True
for bkt in PRES:
    mark = "ok" if got[bkt] == TRUTH[bkt] else "WRONG"
    if got[bkt] != TRUTH[bkt]:
        ok = False
    print(f"  {bkt:20s} partitioned {got[bkt]:6d}   truth {TRUTH[bkt]:6d}  {mark}")
tt = sum(TRUTH.values())
print(f"  {'TOTAL':20s} partitioned {got['total']:6d}   truth {tt:6d}  "
      f"{'ok' if got['total'] == tt else 'WRONG'}")
print(f"  listings {got['listings']:,} == total*4 "
      f"{'ok' if got['listings'] == got['total'] * 4 else 'WRONG'}")
if got["total"] != tt or not ok:
    sys.exit("PARTITION IS NOT EXHAUSTIVE")
print("\nPASS: every key counted exactly once, boundaries and strays included")
