#!/usr/bin/env python3
"""Find the slot templates behind the catalogue - the mechanism that turns a few
hundred phrasings into hundreds of thousands of listings."""
import collections, re, json
BASE = ("/tmp/claude-0/-home-user-wonderleaf-books/"
        "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/an/")
BOIL = re.compile(r"\s*(framed\s+)?wall art poster canvas print picture.*$", re.I)
subs = []
with open(BASE + "titles.tsv", encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            s = BOIL.sub("", p[2]).strip(' "')
            if s: subs.append(s)
print(f"subjects {len(subs):,}")

# A template is the phrase with its distinctive noun blanked. Find them by
# looking for repeated word-skeletons: keep the function/structure words and
# replace the rest with {}.
COMMON = collections.Counter()
for s in subs:
    for w in re.findall(r"[A-Za-z']+", s.lower()):
        COMMON[w] += 1
# "structure" words are the very frequent ones that form the scaffolding
struct = {w for w, n in COMMON.items() if n >= 2000}

tpl = collections.Counter()
for s in subs:
    ws = re.findall(r"[A-Za-z']+", s)
    if not (2 <= len(ws) <= 7):
        continue
    sk = " ".join(w.lower() if w.lower() in struct else "{}" for w in ws)
    if "{}" in sk and sk.count("{}") <= 3:
        tpl[sk] += 1
print("\n=== top 55 slot templates ===")
for t, n in tpl.most_common(55):
    print(f"   {n:>7,}  {t}")

# the explicit formula families, counted
FAM = {
 "{X} Definition":        r"\bdefinition\b",
 "{X} Meaning":           r"\bmeaning\b",
 "Straight Outta {X}":    r"\bstraight outta\b",
 "{X} Rocks":             r"\brocks\b",
 "Peace Love {X}":        r"\bpeace love\b",
 "{X} On The Brain":      r"\bon the brain\b",
 "I Love {X}":            r"\bi love\b",
 "Keep Calm {X}":         r"\bkeep calm\b",
 "{X} Skyline":           r"\bskyline\b",
 "{X} Map":               r"\bmap\b",
 "{X} Flag":              r"\bflag\b",
 "{X} Coordinates":       r"\bcoordinates\b",
 "Est/Established {YEAR}":r"\b(est|established)\b",
 "Home Sweet {X}":        r"\bhome sweet\b",
 "{X} Life":              r"\blife\b",
 "{X} Vibes":             r"\bvibes\b",
 "{X} Lover":             r"\blover\b",
 "World's Best {X}":      r"\bworld'?s best\b",
 "{X} Mode":              r"\bmode\b",
 "Live Laugh {X}":        r"\blive laugh\b",
 "{X} Squad":             r"\bsquad\b",
 "{X} Energy":            r"\benergy\b",
 "{X} Season":            r"\bseason\b",
 "{X} Club":              r"\bclub\b",
 "Good Vibes {X}":        r"\bgood vibes\b",
}
print("\n=== formula families ===")
low = [s.lower() for s in subs]
for k, rx in sorted(FAM.items(), key=lambda kv: -sum(1 for s in low if re.search(kv[1], s))):
    n = sum(1 for s in low if re.search(rx, s))
    if n: print(f"   {n:>7,}  {k}")

# how deep does one template go? sample the Definition family
dfn = [s for s in subs if re.search(r"\bdefinition\b", s, re.I)]
heads = collections.Counter(re.sub(r"\s*definition.*$", "", s, flags=re.I).strip().lower() for s in dfn)
print(f"\n'Definition' family: {len(dfn):,} listings across {len(heads):,} distinct subjects")
print("   examples:", ", ".join(list(heads)[:14]))
json.dump({"templates": tpl.most_common(600)}, open(BASE+"templates.json","w"))
