#!/usr/bin/env python3
"""Subject block volumes, recomputed on the corrected title extraction.

competitor_data_analysis.md was written from an extraction that flattened
tabs but not newlines and took only two columns, and its subject ranking was
already corrected once. This recomputes from rows.tsv, which is verified:
93 files, no double counting, 13,727,739 rows, 1,372,755 titled listings.

Counted per LISTING (titled rows only), per set, so the three builders can be
compared rather than merged.
"""
import csv, collections, re

csv.field_size_limit(10**9)
B = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/learn/rows.tsv"

BLOCKS = {
 "animals":    r"\b(cat|cats|kitten|dog|dogs|puppy|horse|pony|bird|birds|owl|eagle|robin|"
               r"lion|tiger|leopard|wolf|fox|bear|deer|stag|elephant|giraffe|zebra|rabbit|hare|"
               r"whale|dolphin|shark|fish|octopus|turtle|frog|snake|highland cow|cow|sheep|"
               r"butterfly|bee|dragonfly|moth|beetle|crab|duck|swan|heron|puffin|penguin)\b",
 "botanical":  r"\b(flower|flowers|floral|rose|roses|tulip|peony|poppy|sunflower|orchid|lily|"
               r"daisy|lavender|fern|palm|leaf|leaves|cactus|succulent|botanical|herbarium|"
               r"mushroom|tree|trees|forest|branch|foliage|eucalyptus|monstera)\b",
 "landscape":  r"\b(mountain|mountains|hill|hills|valley|coast|coastal|beach|sea|ocean|wave|"
               r"waves|lake|loch|river|waterfall|sunset|sunrise|desert|dune|field|fields|"
               r"meadow|cliff|island|glacier|aurora|fjord|canyon|moor|moorland)\b",
 "city/place": r"\b(city|cityscape|skyline|street|bridge|map|town|village|harbour|harbor|"
               r"london|paris|new york|tokyo|rome|venice|edinburgh|amsterdam|barcelona|"
               r"travel poster|affiche)\b",
 "abstract":   r"\b(abstract|geometric|shapes|minimal|minimalist|bauhaus|pattern|gradient|"
               r"brushstroke|organic|arch|circle|line art|monoline)\b",
 "figure":     r"\b(woman|man|girl|boy|portrait|figure|nude|body|face|lady|dancer|silhouette)\b",
 "food/drink": r"\b(coffee|tea|wine|cocktail|beer|whisky|gin|lemon|fruit|kitchen|bread|"
               r"cheese|pasta|sushi|cake|bar cart)\b",
 "space":      r"\b(moon|space|galaxy|nebula|planet|star|stars|astronaut|constellation|"
               r"solar|celestial|zodiac)\b",
 "typography": r"\b(quote|quotes|definition|meaning|typography|lettering|word|words|"
               r"keep calm|motivational|affirmation)\b",
 "vehicle":    r"\b(car|cars|motorcycle|motorbike|chopper|bike|bicycle|plane|aircraft|"
               r"train|locomotive|ship|boat|yacht|sailing|tractor)\b",
 "sport":      r"\b(football|soccer|rugby|cricket|golf|tennis|boxing|cycling|surf|surfing|"
               r"ski|skiing|climbing|running|swimming)\b",
 "vintage/ad": r"\b(vintage|retro|antique|advert|advertisement|poster art|art deco|"
               r"nouveau|1920s|1930s|1950s|1960s|1970s)\b",
}
RX = {k: re.compile(v, re.I) for k, v in BLOCKS.items()}

counts = collections.defaultdict(collections.Counter)
tot = collections.Counter()
seen = collections.defaultdict(set)
r = csv.reader(open(B, newline="", encoding="utf-8"), delimiter="\t")
hdr = next(r); ix = {h: i for i, h in enumerate(hdr)}
for row in r:
    if len(row) != len(hdr):
        continue
    t = row[ix["title"]].strip()
    if not t:
        continue
    s = row[ix["set"]]
    if t in seen[s]:
        continue
    seen[s].add(t)
    tot[s] += 1
    for k, rx in RX.items():
        if rx.search(t):
            counts[s][k] += 1

sets = ["fy", "displate", "raw800k"]
print(f"{'block':<13} " + "".join(f"{s:>22}" for s in sets))
print(f"{'':13} " + "".join(f"{'(distinct titles)':>22}" for s in sets))
print("-" * 80)
for k in BLOCKS:
    line = f"{k:<13} "
    for s in sets:
        n = counts[s][k]; T = tot[s] or 1
        line += f"{n:>12,} {n/T*100:>6.1f}% "
    print(line)
print("-" * 80)
print(f"{'TOTAL':<13} " + "".join(f"{tot[s]:>12,} {'100.0%':>7} " for s in sets))
