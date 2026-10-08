#!/usr/bin/env python3
"""Fy!'s titles are machine-generated from templates. Recover them, and the slot
values each one is filled with - that is the mechanism to copy."""
import collections, re, json
BASE = ("/tmp/claude-0/-home-user-wonderleaf-books/"
        "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/an/")
T = []
with open(BASE + "titles.tsv", encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3 and p[0] == "fy300k":
            T.append(p[2])
print(f"Fy! titles {len(T):,}")

# strip the " Art Print" suffix and any trailing variant number
clean = []
for t in T:
    s = re.sub(r"\s*art print\s*$", "", t, flags=re.I)
    s = re.sub(r"\s+\d+\s*$", "", s)
    clean.append(s.strip())

# a template = the phrase with capitalised content words blanked, keeping the
# connective scaffolding that identifies the pattern
SCAFF = set("""a an the of in on with and or by for at to from into
in the of the in a style inspired after no""".split())
tpl = collections.Counter()
for s in clean:
    ws = s.split()
    if not (3 <= len(ws) <= 12):
        continue
    sk = " ".join(w.lower() if w.lower() in SCAFF else "{}" for w in ws)
    if sk.count("{}") <= len(ws) - 1:          # must retain some scaffolding
        tpl[sk] += 1
print("\n=== Fy! skeletons with scaffolding (top 30) ===")
for k, n in tpl.most_common(30):
    print(f"   {n:>7,}  {k}")

# the named recurring phrasings, which are the real templates
PHRASES = [
 "a window view of", "in the style of", "inspired by", "bird with a flower crown",
 "vintage bird linocut", "linocut of", "black and white analogue photograph",
 "illustration zodiac star sign", "stencil style", "in the manner of",
 "botanical poster", "abstract shapes", "mixed media", "collection",
 "vintage poster", "travel poster", "map of", "skyline", "coastal",
 "flower market", "still life", "line drawing", "gallery wall",
]
low = [s.lower() for s in clean]
print("\n=== recurring Fy! phrasings ===")
rows = []
for p in PHRASES:
    n = sum(1 for s in low if p in s)
    if n: rows.append((n, p))
for n, p in sorted(rows, reverse=True):
    print(f"   {n:>7,}  \"{p}\"")

def slots(phrase, before=False):
    """What values fill the slot around a phrase?"""
    c = collections.Counter()
    for s in clean:
        ls = s.lower()
        i = ls.find(phrase)
        if i < 0: continue
        if before:
            v = s[:i].strip()
        else:
            v = s[i+len(phrase):].strip()
        v = re.sub(r"\s+\d+$", "", v).strip()
        if v: c[v] += 1
    return c

for ph, before in (("a window view of", False), ("in the style of", False),
                   ("bird with a flower crown", False), ("linocut of", False),
                   ("inspired by", False)):
    c = slots(ph, before)
    print(f"\n--- slot values after \"{ph}\": {len(c):,} distinct")
    print("   ", ", ".join(f"{k}({v})" for k, v in c.most_common(22)))

# the window-view family decomposed: city x movement
wv = [s for s in clean if "a window view of" in s.lower()]
cities = collections.Counter(); movs = collections.Counter()
for s in wv:
    m = re.search(r"a window view of (.+?) in the style of (.+)$", s, re.I)
    if m:
        cities[m.group(1).strip()] += 1
        movs[m.group(2).strip()] += 1
print(f"\n=== 'A Window View Of {{CITY}} In The Style Of {{MOVEMENT}}' ===")
print(f"   listings {len(wv):,} | cities {len(cities):,} | movements {len(movs):,}")
print("   cities:", ", ".join(f"{k}({v})" for k, v in cities.most_common(30)))
print("   movements:", ", ".join(f"{k}({v})" for k, v in movs.most_common(30)))
json.dump({"cities": cities.most_common(), "movements": movs.most_common()},
          open(BASE + "windowview.json", "w"))
