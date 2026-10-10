#!/usr/bin/env python3
"""Deep mine of all 1,463,031 competitor listings.

The first pass pulled headline template counts. This one builds the full
vocabulary: every recurring phrasing, the slot values that fill each one, how
subject and style co-occur, and the complete subject lexicon - the raw material
for a generator rather than a summary for a human.
"""
import csv, re, collections, json, itertools, sys
csv.field_size_limit(50 << 20)
BASE = ("/tmp/claude-0/-home-user-wonderleaf-books/"
        "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/an/")
BOIL = re.compile(r"\s*(framed\s+)?wall art poster canvas print picture.*$", re.I)
TAIL = re.compile(r"\s*art print\s*$", re.I)
NUM  = re.compile(r"\s+\d+\s*$")

rows = []
with open(BASE + "titles.csv", newline="", encoding="utf-8") as f:
    r = csv.reader(f); next(r)
    for p in r:
        if len(p) >= 3:
            s = TAIL.sub("", BOIL.sub("", p[2])).strip(' "')
            s = NUM.sub("", s).strip()
            if s:
                rows.append((p[0], s))
print(f"subject phrases {len(rows):,}", flush=True)
low = [(st, s.lower()) for st, s in rows]

# ---- 1. every n-gram that recurs, 2..6 words -------------------------------
print("\n=== recurring phrases (the template bodies) ===", flush=True)
grams = collections.Counter()
for _, s in low:
    w = s.split()
    for n in (2, 3, 4, 5):
        for i in range(len(w) - n + 1):
            grams[" ".join(w[i:i+n])] += 1
# keep phrases that look like scaffolding: recur a lot and contain a connective
CONN = set("of in the a with and on at for into from by to is are".split())
cand = [(c, g) for g, c in grams.items() if c >= 400 and len(g.split()) >= 3]
cand.sort(reverse=True)
for c, g in cand[:70]:
    print(f"   {c:>8,}  {g}")
json.dump(cand[:4000], open(BASE + "phrases.json", "w"))

# ---- 2. the leading and trailing word vocabularies -------------------------
print("\n=== commonest FIRST words (what a title opens on) ===", flush=True)
for w, c in collections.Counter(s.split()[0] for _, s in low if s.split()).most_common(40):
    print(f"   {c:>8,}  {w}")
print("\n=== commonest LAST words (what a title closes on) ===", flush=True)
for w, c in collections.Counter(s.split()[-1] for _, s in low if s.split()).most_common(40):
    print(f"   {c:>8,}  {w}")
