#!/usr/bin/env python3
"""Mine the 3.58M titles from the LIVE Fy! catalogue.

This is 12x the Fy! data the MEGA dump held (297,912) and more than double the
whole dump corpus, so it supersedes the earlier pass for anything Fy!-specific.
"""
import json, re, collections
T = []
for line in open("manifest.jsonl", encoding="utf-8"):
    try: r = json.loads(line)
    except Exception: continue
    t = r.get("title")
    if t: T.append(t)
N = len(T)
print(f"titles {N:,} | distinct {len(set(T)):,}\n")
NUM = re.compile(r"\s+\d+\s*$")
clean = [NUM.sub("", t).strip() for t in T]
low = [t.lower() for t in clean]

print("=== the biggest template families (phrase recurring >=2000) ===")
g = collections.Counter()
for s in low:
    w = s.split()
    for n in (3, 4, 5):
        for i in range(len(w) - n + 1):
            g[" ".join(w[i:i+n])] += 1
top = [(c, p) for p, c in g.items() if c >= 2000]
top.sort(reverse=True)
for c, p in top[:45]:
    print(f"   {c:>8,}  {p}")
json.dump(top[:5000], open("live_phrases.json", "w"))

print("\n=== leading words ===")
for w, c in collections.Counter(s.split()[0] for s in low if s.split()).most_common(30):
    print(f"   {c:>8,}  {w}")
