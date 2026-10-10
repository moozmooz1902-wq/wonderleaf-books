#!/usr/bin/env python3
"""Which technique do they use for which subject, and which colours?

Knowing the subject list and the technique list separately still leaves the
pairing to guesswork. This measures it across all 1,463,031 listings: for each
subject, which treatments actually co-occur, and how much more often than
chance.
"""
import csv, re, collections, json, math
csv.field_size_limit(50 << 20)
BASE = ("/tmp/claude-0/-home-user-wonderleaf-books/"
        "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/an/")
BOIL = re.compile(r"\s*(framed\s+)?wall art poster canvas print picture.*$", re.I)
subs = []
with open(BASE + "titles.csv", newline="", encoding="utf-8") as f:
    r = csv.reader(f); next(r)
    for p in r:
        if len(p) >= 3:
            s = BOIL.sub("", p[2]).strip(' "').lower()
            if s: subs.append(s)
N = len(subs)
print(f"{N:,} listings\n")

SUBJ = {
 "fox": r"\bfox(es)?\b", "deer/stag": r"\b(deer|stag)\b", "owl": r"\bowls?\b",
 "cat": r"\bcats?\b", "dog": r"\bdogs?\b", "horse": r"\bhorses?\b",
 "highland cow": r"\bhighland cow|\bcows?\b", "bird": r"\bbirds?\b",
 "butterfly": r"\bbutterfl(y|ies)\b", "bee/insect": r"\b(bees?|insects?|moths?|beetle)\b",
 "whale/sea": r"\b(whale|dolphin|octopus|jellyfish|seahorse)\b",
 "mountain": r"\bmountains?\b", "forest/tree": r"\b(forest|woods|trees?)\b",
 "beach/coast": r"\b(beach|coast|shore|cliff)\b", "lake/river": r"\b(lake|river|loch)\b",
 "sunset": r"\bsunsets?\b", "city/skyline": r"\b(city|skyline|cityscape)\b",
 "flower": r"\b(flower|floral|bloom)s?\b", "rose": r"\broses?\b",
 "tulip": r"\btulips?\b", "sunflower": r"\bsunflowers?\b",
 "leaf/botanical": r"\b(leaf|leaves|botanical|fern|palm)\b",
 "mushroom": r"\bmushrooms?\b", "moon/celestial": r"\b(moon|stars?|celestial|constellation)\b",
 "woman/portrait": r"\b(woman|women|girl|portrait|lady)\b",
 "coffee/tea": r"\b(coffee|tea|espresso|latte)\b",
 "cocktail/wine": r"\b(cocktail|wine|gin|whisky|martini)\b",
 "fruit/veg": r"\b(lemon|orange|fruit|tomato|pear|apple)\b",
 "car/vehicle": r"\b(car|motorcycle|bicycle|train|boat|vespa)\b",
 "dinosaur": r"\bdinosaurs?\b", "map": r"\bmaps?\b",
}
TECH = {
 "watercolour": r"\bwatercolou?r\b", "line art": r"\bline (art|drawing)\b",
 "linocut/woodblock": r"\b(linocut|lino|woodcut|woodblock|block print)\b",
 "oil/impasto": r"\b(oil painting|impasto|palette knife|brushstroke)\b",
 "vintage/antique": r"\b(vintage|antique)\b", "retro": r"\bretro\b",
 "minimalist": r"\bminimal(ist)?\b", "abstract": r"\babstract\b",
 "geometric": r"\bgeometric\b", "collage": r"\bcollage\b",
 "pop art": r"\bpop art\b", "art nouveau": r"\bart nouveau\b",
 "art deco": r"\bart deco\b", "mid century": r"\bmid.?century\b",
 "boho": r"\bboho|bohemian\b", "japanese/ukiyo": r"\b(japanese|ukiyo|sumi)\b",
 "neon": r"\bneon\b", "pencil/sketch": r"\b(pencil|sketch|charcoal)\b",
 "photographic": r"\b(photograph|photo)\b", "silhouette": r"\bsilhouette\b",
 "illustration": r"\billustration\b", "painting": r"\bpainting\b",
 "risograph": r"\brisograph|riso\b", "cyanotype": r"\b(cyanotype|blueprint)\b",
}
sm = {k: re.compile(v) for k, v in SUBJ.items()}
tm = {k: re.compile(v) for k, v in TECH.items()}
S = {k: 0 for k in SUBJ}; T = {k: 0 for k in TECH}
J = collections.Counter()
for s in subs:
    hits_s = [k for k, rx in sm.items() if rx.search(s)]
    hits_t = [k for k, rx in tm.items() if rx.search(s)]
    for k in hits_s: S[k] += 1
    for k in hits_t: T[k] += 1
    for a in hits_s:
        for b in hits_t:
            J[(a, b)] += 1

print("For each subject: the techniques they use MOST relative to chance.")
print("(lift = how many times more often than if pairing were random)\n")
out = {}
for subj in sorted(SUBJ, key=lambda k: -S[k]):
    if S[subj] < 300: continue
    scored = []
    for tech in TECH:
        j = J[(subj, tech)]
        if j < 25: continue
        exp = S[subj] * T[tech] / N
        if exp <= 0: continue
        scored.append((j / exp, j, tech))
    scored.sort(reverse=True)
    if not scored: continue
    out[subj] = [(t, round(l, 1), j) for l, j, t in scored[:6]]
    top = " · ".join(f"{t} (x{l:.1f}, n={j:,})" for l, j, t in scored[:5])
    print(f"{subj:<16} n={S[subj]:>7,}   {top}")
json.dump(out, open(BASE + "pairings.json", "w"), indent=1)
print(f"\ntechnique totals: " + ", ".join(f"{k} {v:,}" for k, v in
      sorted(T.items(), key=lambda x: -x[1])[:12]))
