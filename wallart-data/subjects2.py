#!/usr/bin/env python3
"""Re-run on the SUBJECT phrase only, with the seller's boilerplate stripped.

Every one of the 874,816 titles ends "... Wall Art Poster Canvas Print Picture",
which is the seller's own eBay suffix, not the source site's wording. Analysing
the full string made "poster" match every row. The subject is what precedes it.
"""
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
            if s:
                subs.append((p[0], s))
N = len(subs)
low = [s.lower() for _, s in subs]
print(f"subject phrases {N:,}")
L = [len(s) for _, s in subs]
print(f"subject length mean {sum(L)/len(L):.1f} max {max(L)}")
print(f"distinct subjects {len(set(low)):,}  (duplicates {N-len(set(low)):,})")

def pct(pat):
    rx = re.compile(pat); n = sum(1 for t in low if rx.search(t))
    return n, 100*n/N

G = {
 "PLACE map/city/skyline/flag": r"\b(map|maps|city|cityscape|skyline|flag|metro|transit|street map)\b",
 "BOTANICAL                  ": r"\b(flower|flowers|floral|botanical|leaf|leaves|plant|palm|monstera|fern|rose|tulip|peony|peonies|sunflower|lavender|eucalyptus|olive|cactus|succulent|mushroom|tree|trees|forest)\b",
 "LANDSCAPE/NATURE           ": r"\b(landscape|mountain|mountains|sunset|sunrise|beach|ocean|sea|lake|river|waterfall|desert|field|meadow|sky|clouds|aurora)\b",
 "ANIMALS                    ": r"\b(cat|cats|dog|dogs|horse|lion|tiger|wolf|bear|elephant|fox|deer|stag|owl|eagle|bird|birds|butterfly|whale|shark|fish|cow|rabbit|hare|hedgehog|badger|panda|giraffe|zebra|monkey|bee|dragonfly)\b",
 "ABSTRACT/GEOMETRIC         ": r"\b(abstract|geometric|minimal|minimalist|shapes|pattern|patterns|line art|bauhaus|mid.?century|organic)\b",
 "PEOPLE/PORTRAIT/FASHION    ": r"\b(portrait|woman|man|girl|boy|face|fashion|model|dancer|ballet|silhouette)\b",
 "TYPOGRAPHY/QUOTES          ": r"\b(quote|quotes|typography|lyrics|poem|saying|definition|slogan)\b",
 "CELESTIAL                  ": r"\b(moon|star|stars|constellation|galaxy|nebula|planet|space|zodiac|astrology|eclipse|celestial)\b",
 "VEHICLES                   ": r"\b(car|cars|motorcycle|motorbike|bicycle|train|plane|aircraft|boat|ship|yacht|tractor|truck|bus|formula)\b",
 "FILM/TV/GAMING             ": r"\b(movie|film|cinema|tv series|anime|manga|video game|gaming|console)\b",
 "FOOD & DRINK               ": r"\b(coffee|tea|wine|beer|cocktail|whisky|gin|pizza|sushi|cake|fruit|lemon|kitchen|chef)\b",
 "SPORT                      ": r"\b(football|soccer|boxing|golf|tennis|cricket|rugby|basketball|baseball|surf|ski|cycling|gym|yoga)\b",
 "VINTAGE/RETRO              ": r"\b(vintage|retro|antique|classic|victorian|art deco|art nouveau)\b",
 "NURSERY/KIDS               ": r"\b(nursery|baby|kids|children|dinosaur|unicorn|safari|woodland|alphabet)\b",
 "MUSIC                      ": r"\b(music|album|guitar|piano|vinyl|record|band|jazz|concert)\b",
 "RELIGION/SPIRITUAL         ": r"\b(god|jesus|bible|faith|buddha|zen|mandala|chakra|spiritual|prayer)\b",
}
print("\n=== subject blocks (share of 874,816; a title can match several) ===")
for k, rx in sorted(G.items(), key=lambda x: -pct(x[1])[0]):
    n, p = pct(rx); print(f"   {k} {n:>8,}  {p:5.2f}%")

print("\n=== top 80 subject words (boilerplate removed) ===")
STOP = set("""the a an of and for in on with to is are at by from as it its this that or
your you my i we not no so very art print poster wall canvas picture framed""".split())
wc = collections.Counter()
for _, s in subs:
    for w in re.findall(r"[A-Za-z][A-Za-z'&-]{2,}", s):
        lw = w.lower()
        if lw not in STOP:
            wc[lw] += 1
for w, n in wc.most_common(80):
    print(f"   {n:>7,}  {w}")
json.dump({"wordfreq": wc.most_common(6000),
           "sample": [s for _, s in subs[:3000]]},
          open(BASE + "subjects.json", "w"))
print("\n=== 25 example subject phrases ===")
for _, s in subs[:25]:
    print("   ", s[:92])
