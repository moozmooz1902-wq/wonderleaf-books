#!/usr/bin/env python3
"""Decide which listings get which illustration."""
import csv, json, re, sys
from collections import Counter, defaultdict
csv.field_size_limit(10**7)

keep = [l.strip() for l in open("KEEP.txt") if l.strip()]
phrase = {k: k.replace("-", " ").strip() for k in keep}
norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).split()
by_phrase = {v: k for k, v in phrase.items()}
words = {k: set(norm(v)) for k, v in phrase.items()}

def match(il):
    il = (il or "").strip().lower()
    if not il:
        return None
    if il in by_phrase:
        return by_phrase[il]
    w = set(norm(il))
    if not w:
        return None
    best = None
    for k, kw in words.items():
        if w <= kw or kw <= w:
            # prefer the closest-sized phrase, so "skull" does not grab
            # "skull with diving gear and stopwatch" when "skull" exists
            d = abs(len(kw) - len(w))
            if best is None or d < best[0]:
                best = (d, k)
    return best[1] if best else None

rows = []
with open("FINAL_V7.csv", newline="", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f):
        m = match(r.get("illustration"))
        if m:
            rows.append((f"WLT-{int(r['source_idx']):06d}", m,
                         int(r.get("look") or 0), int(r.get("palette_idx") or 0)))

print(f"{len(rows)} listings matched to {len(set(r[1] for r in rows))} illustrations")
combo = Counter((m, l, p) for _, m, l, p in rows)
dupes = sum(v - 1 for v in combo.values() if v > 1)
print(f"{len(combo)} distinct picture+layout+palette combinations, {dupes} repeats")
print("worst combo:", combo.most_common(3))
with open("ILLUS_MAP.tsv", "w") as g:
    for sku, m, l, p in rows:
        g.write(f"{sku}\t{m}\n")
print("wrote ILLUS_MAP.tsv")
