#!/usr/bin/env python3
"""
Harvest the Metropolitan Museum's open-access collection.

    python3 harvest_met.py --out met_raw.jsonl

The Met publishes ~42,600 public domain paintings with images under CC0,
and serves the full-resolution files openly. A spot check came back at
4000x3184 - A3 at 300dpi with no upscaling at all.

The Art Institute of Chicago has a nicer bulk API but its image server
refuses automated requests with a 403, so its metadata is useless to us on
its own. The Met is the source that actually hands over pictures.

These are real artworks people already search for by name, which is the
whole point. canvasartshop, at 92,000 items sold, is selling little else:
Hokusai, Waterhouse, Van Gogh, Turner, Lowry, Morris, Goya, Mucha.

Two stages, because the Met has no bulk endpoint:
  1. /search per department and per subject word, for object ids
  2. /objects/<id> for each one, a few at a time
"""

import argparse
import json
import os
import queue
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://collectionapi.metmuseum.org/public/collection/v1"
UA = "wonderleaf-catalogue/1.0 (print-on-demand research)"

# Departments worth putting on a wall. Coins, arms and armour, musical
# instruments and costume are skipped - the object photography does not make
# a print anybody wants.
DEPARTMENTS = {
    11: "European Paintings",
    9: "Drawings and Prints",
    6: "Asian Art",
    19: "Photographs",
    21: "Modern and Contemporary Art",
    14: "Islamic Art",
    13: "Greek and Roman Art",
    10: "Egyptian Art",
}

# A department search alone misses a great deal, so sweep the subject words
# a print buyer actually types as well.
TERMS = [
    "painting", "landscape", "portrait", "flowers", "botanical", "bird",
    "map", "japanese woodblock", "still life", "seascape", "garden", "cat",
    "dog", "horse", "ship", "mountain", "river", "tree", "moon", "fruit",
    "butterfly", "fish", "castle", "angel", "mythology", "dancer", "wave",
    "snow", "autumn", "sunflower", "poppy", "rose", "owl", "tiger", "lion",
    "elephant", "deer", "hare", "fox", "coast", "harbour", "windmill",
    "bridge", "cathedral", "street", "night", "storm", "forest",
]


def get(url, tries=4, timeout=60):
    """Fetch JSON, backing off rather than hammering a free public API."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1.5 ** i)
        except Exception:
            time.sleep(1.5 ** i)
    return None


def object_ids():
    """Every public-domain, image-bearing object id worth fetching."""
    ids = set()
    for dept, name in DEPARTMENTS.items():
        d = get(f"{API}/search?isPublicDomain=true&hasImages=true"
                f"&departmentId={dept}&q=*")
        n = (d or {}).get("objectIDs") or []
        ids.update(n)
        print(f"  {name:<30} {len(n):>7,}   total {len(ids):,}", flush=True)
        time.sleep(0.3)
    for term in TERMS:
        d = get(f"{API}/search?isPublicDomain=true&hasImages=true"
                f"&q={urllib.parse.quote(term)}")
        n = (d or {}).get("objectIDs") or []
        ids.update(n)
        print(f"  term {term:<25} {len(n):>7,}   total {len(ids):,}",
              flush=True)
        time.sleep(0.3)
    return sorted(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="met_raw.jsonl")
    ap.add_argument("--ids", default="met_ids.json")
    ap.add_argument("--workers", type=int, default=6,
                    help="the Met asks for restraint - free API, no key")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    if os.path.exists(a.ids):
        ids = json.load(open(a.ids))
        print(f"  {len(ids):,} object ids already listed")
    else:
        print("  finding object ids\n")
        ids = object_ids()
        json.dump(ids, open(a.ids, "w"))
        print(f"\n  {len(ids):,} distinct object ids\n")

    # Resume: this takes a while and a dropped connection should not mean
    # starting again.
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            try:
                done.add(json.loads(line)["objectID"])
            except Exception:
                pass
        print(f"  resuming, {len(done):,} already held")

    todo = [i for i in ids if i not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"  {len(todo):,} to fetch\n")

    q = queue.Queue()
    for i in todo:
        q.put(i)
    lock = threading.Lock()
    fh = open(a.out, "a", encoding="utf-8")
    state = {"n": 0, "kept": 0}

    def worker():
        while True:
            try:
                oid = q.get_nowait()
            except queue.Empty:
                return
            d = get(f"{API}/objects/{oid}", timeout=45)
            with lock:
                state["n"] += 1
                if d and d.get("isPublicDomain") and d.get("primaryImage"):
                    fh.write(json.dumps(d, ensure_ascii=False) + "\n")
                    state["kept"] += 1
                if state["n"] % 500 == 0:
                    fh.flush()
                    print(f"  {state['n']:,}/{len(todo):,} fetched, "
                          f"{state['kept']:,} usable", flush=True)
            time.sleep(0.05)

    ts = [threading.Thread(target=worker, daemon=True)
          for _ in range(a.workers)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    fh.close()
    print(f"\n  {state['kept']:,} usable artworks -> {a.out}")


if __name__ == "__main__":
    main()
