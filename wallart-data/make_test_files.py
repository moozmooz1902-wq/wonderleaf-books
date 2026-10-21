#!/usr/bin/env python3
"""Build a verified 10-listing test file for EVERY bucket, with no pod.

The full per-store build needs a pod because it diffs against a LISTING of
the bucket, and the R2 keys live only on the pod template. A test file does
not: at ten listings we can afford to verify each picture individually over
the public r2.dev URL, which needs no credentials and is stronger evidence
than a bucket listing anyway - it is what eBay itself will fetch.
"""
import json, os, sys, urllib.request, collections
from concurrent.futures import ThreadPoolExecutor

HERE = "/home/user/wonderleaf-books/wallart-data"
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "gen"))
import grid, allocate, build_ebay as B

PANELS_PER_BUCKET = 6          # 6 panels x 4 colourways = 24 candidate listings
WANT_LISTINGS = 10             # cut to this, matching LUXVIA_TEST_10
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"}

def live(url):
    try:
        req = urllib.request.Request(url, headers=dict(UA, Range="bytes=0-32"))
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status in (200, 206)
    except Exception:
        return False

subjects = json.load(open(os.path.join(HERE, "gen/subjects.json")))
jobs = grid.expand(subjects)
jobs = sorted(jobs, key=lambda j: grid.sku_for(j))
for j in jobs:
    j["sku"] = grid.sku_for(j)
pool = jobs[:960000]
print(f"pool {len(pool):,}")

bybucket = collections.defaultdict(list)
for j in pool:
    bybucket[allocate.store_for(j["sku"])["bucket"]].append(j)

out_root = os.path.join(HERE, "ebay", "tests")
os.makedirs(out_root, exist_ok=True)
summary = {}

for bucket, cand in bybucket.items():
    st = B.STORES[bucket]
    picked, i = [], 0
    while len(picked) < PANELS_PER_BUCKET and i < len(cand):
        j = cand[i]; i += 1
        urls = [B.pic(st, f'{j["sku"]}-{ci}', c)
                for ci in range(B.EB["colourways"]) for c in B.EB["colours"]]
        with ThreadPoolExecutor(max_workers=6) as ex:
            oks = list(ex.map(live, urls))
        if all(oks):
            picked.append(j)
        else:
            print(f"  {bucket}: skipped {j['sku']} "
                  f"({sum(1 for o in oks if not o)}/{len(urls)} pictures missing)")
    rows = []
    for j in picked:
        r, bad = B.rows_for(j, st)
        if bad:
            print(f"  {bucket}: {j['sku']} blocked: {bad}"); continue
        rows.extend(r)
    # cut to WANT_LISTINGS whole listings: a parent plus its variation rows
    cut, listings = [], 0
    for r in rows:
        if r.get("Relationship") != "Variation":
            if listings == WANT_LISTINGS: break
            listings += 1
        cut.append(r)
    import csv
    path = os.path.join(out_root, f"{bucket}_TEST_10.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=B.HEADER, extrasaction="ignore")
        w.writeheader(); w.writerows(cut)
    pics = sorted({r["PicURL"] for r in cut if r.get("PicURL")})
    npic = sum(len(p.split("|")) for p in pics)
    summary[bucket] = (listings, len(cut), len(pics), path)
    print(f"{bucket:<20} {listings} listings, {len(cut)} rows -> {path}")

print("\n=== every picture in every test file, re-checked ===")
for bucket, (li, nr, _np, path) in summary.items():
    import csv
    urls = set()
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        for u in (r.get("PicURL") or "").split("|"):
            if u.strip(): urls.add(u.strip())
    with ThreadPoolExecutor(max_workers=8) as ex:
        oks = list(ex.map(live, sorted(urls)))
    print(f"{bucket:<20} {sum(oks)}/{len(urls)} pictures live"
          + ("   ALL OK" if all(oks) else "   *** MISSING ***"))
