#!/usr/bin/env python3
"""Collect live Fy! artwork URLs. Their product JSON carries exactly one image
per product and it is the flat artwork - no frame, no room mockup, no watermark -
which is what we need to study."""
import json, urllib.request, time, os, sys, random

OUT = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/soul/meta"
COLLECTIONS = [
 "bestselling-wall-art", "bestselling-canvas-prints", "art-prints",
 "botanical-art-prints", "abstract-art-prints", "animals-art-prints",
 "birds-art-prints", "coastal-art-prints", "cities-art-prints",
 "vintage-art-prints", "illustration-art-prints", "flowers-art-prints",
 "landscapes-art-prints", "bohemian-art-prints", "cottage-core-art-prints",
 "scandinavian-art-prints", "art-nouveau-art-prints", "art-deco-art-prints",
 "black-and-white-art-prints", "blue-art-prints", "green-art-prints",
 "mid-century-modern-art-prints", "minimalist-art-prints", "cats-art-prints",
 "dogs-art-prints", "food-and-drinks-art-prints", "travel-art-prints",
 "line-art-art-prints", "watercolor-art-prints", "trees-and-forests-art-prints",
]
def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

ok = bad = 0
for c in COLLECTIONS:
    path = f"{OUT}/{c}.json"
    if os.path.exists(path):
        print(f"  have {c}"); ok += 1; continue
    try:
        d = get(f"https://iamfy.co/collections/{c}/products.json?limit=250")
        prods = d.get("products", [])
        if not prods:
            print(f"  EMPTY {c}"); bad += 1; continue
        json.dump(prods, open(path, "w"))
        print(f"  {len(prods):>4} products  {c}")
        ok += 1
    except Exception as e:
        print(f"  FAIL {c}: {type(e).__name__} {str(e)[:60]}"); bad += 1
    time.sleep(1.2)
print(f"\ncollections ok {ok} failed {bad}")
