#!/usr/bin/env python3
"""Merge the Fy! and Displate harvests into one shuffled work list.

Shuffled on purpose. The run can be stopped at any point - the balance runs
out, or the spend cap is hit - and a work list in harvest order would leave a
sample biased by sitemap, which for Displate means biased by upload year. In
random order, whatever fraction got done is a usable random sample of the whole
9.1M, so the learning is valid at any stopping point.

External shuffle in two passes so it never holds 9M lines in memory: scatter to
256 buckets at random, then shuffle each bucket and concatenate.
"""
import json, os, random, sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
OUT  = os.path.join(BASE, "urls.jsonl")
TMP  = os.path.join(BASE, "shuf")
os.makedirs(TMP, exist_ok=True)
rng = random.Random(20261010)

srcs = [(os.path.join(BASE, "harvest", "manifest.jsonl"), "fy"),
        (os.path.join(BASE, "harvest", "displate", "displate.jsonl"), "displate")]

bk = [open(os.path.join(TMP, f"b{i:03d}"), "w", encoding="utf-8") for i in range(256)]
n = 0
for path, src in srcs:
    if not os.path.exists(path):
        print(f"MISSING {path}", flush=True); continue
    for line in open(path, encoding="utf-8"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        url = d.get("img") or d.get("url")
        if not url or not url.startswith("http"):
            continue
        rec = {"id": d.get("id") or url[-44:], "url": url, "src": src}
        t = (d.get("title") or "").strip()
        if t:
            rec["title"] = t
        bk[rng.randrange(256)].write(json.dumps(rec, ensure_ascii=False) + "\n")
        n += 1
        if n % 1000000 == 0:
            print(f"  scattered {n:,}", flush=True)
for f in bk:
    f.close()

with open(OUT, "w", encoding="utf-8") as out:
    for i in range(256):
        p = os.path.join(TMP, f"b{i:03d}")
        lines = open(p, encoding="utf-8").readlines()
        rng.shuffle(lines)
        out.writelines(lines)
        os.remove(p)
os.rmdir(TMP)
print(f"{n:,} urls -> {OUT}", flush=True)
