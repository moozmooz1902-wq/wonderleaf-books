#!/usr/bin/env python3
"""Download a spread of Fy! artwork at a size where brushwork is still visible."""
import json, glob, os, urllib.request, random, re, time
B = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/soul"
random.seed(11)
WEIGHT = {"bestselling-wall-art": 24, "bestselling-canvas-prints": 24, "art-prints": 16}
index = []
for p in sorted(glob.glob(f"{B}/meta/*.json")):
    coll = os.path.basename(p)[:-5]
    prods = json.load(open(p))
    n = WEIGHT.get(coll, 10)
    random.shuffle(prods)
    taken = 0
    for pr in prods:
        imgs = pr.get("images") or []
        if not imgs: continue
        src = imgs[0].get("src")
        if not src: continue
        # ask the CDN for a 760px wide copy
        url = re.sub(r"(\.(jpg|jpeg|png|webp))(\?|$)", r"_760x\1\3", src)
        index.append({"coll": coll, "title": pr.get("title", ""),
                      "handle": pr.get("handle", ""), "tags": pr.get("tags", []),
                      "type": pr.get("product_type", ""), "url": url,
                      "orig": src})
        taken += 1
        if taken >= n: break
print(f"selected {len(index)} images across {len(set(i['coll'] for i in index))} collections")
json.dump(index, open(f"{B}/index.json", "w"), indent=1)

got = fail = 0
for i, rec in enumerate(index):
    fn = f"{B}/img/{i:04d}_{rec['coll'][:18]}.jpg"
    rec["file"] = fn
    if os.path.exists(fn) and os.path.getsize(fn) > 2000:
        got += 1; continue
    try:
        req = urllib.request.Request(rec["url"], headers={"Accept": "image/*"})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = r.read()
        if len(d) < 2000: raise ValueError("tiny")
        open(fn, "wb").write(d); got += 1
    except Exception as e:
        try:
            with urllib.request.urlopen(urllib.request.Request(rec["orig"],
                     headers={"Accept": "image/*"}), timeout=60) as r:
                d = r.read()
            open(fn, "wb").write(d); got += 1
        except Exception as e2:
            fail += 1; rec["file"] = None
    if (i+1) % 50 == 0: print(f"   {i+1}/{len(index)} ok={got} fail={fail}", flush=True)
json.dump(index, open(f"{B}/index.json", "w"), indent=1)
print(f"\ndownloaded {got} failed {fail}")
