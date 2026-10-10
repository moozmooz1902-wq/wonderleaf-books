import os, re, json, collections
D = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/harvest2/displate"
dem = json.load(open(os.path.join(D, "demand.json")))
queries, brands = dem["queries"], dem["brands"]

# Full-phrase brand match. The earlier single-word filter was too loose: splitting
# "star-wars" made "star" a brand word, so any query containing "star" scored as IP.
phrases = sorted({b.replace("-", " ") for b in brands}, key=len, reverse=True)
# plus the franchise words that are unambiguous on their own
solo = ["naruto","pokemon","batman","superman","spiderman","spider man","harry potter",
        "james bond","doctor who","breaking bad","mandalorian","minecraft","zelda",
        "mario","sonic","gundam","evangelion","attack on titan","death star","hogwarts",
        "jurassic park","terminator","rambo","rocky","scarface","godfather","pulp fiction",
        "joker","venom","deadpool","wolverine","iron man","thor","hulk","avengers"]
hit = collections.Counter(); matched = set()
for q in queries:
    for p in phrases + solo:
        if re.search(r"(?<![a-z])" + re.escape(p) + r"(?![a-z])", q):
            hit[p] += 1; matched.add(q); break
print(f"queries                      {len(queries):,}")
print(f"match a licensed brand phrase {len(matched):,}  ({len(matched)/len(queries)*100:.1f}%)")
print(f"  (floor, not ceiling: only Displate's own 191 partners + {len(solo)} obvious franchises)")
print("\ntop 25 franchise phrases by query count:")
for p, c in hit.most_common(25):
    print(f"  {c:>4}  {p}")

rest = [q for q in queries if q not in matched]
print(f"\nremaining queries            {len(rest):,}")
# what are the non-franchise queries about? score against the subject vocabulary
SUBJ = {"animal":["cat","cats","dog","dogs","horse","bird","birds","lion","tiger","wolf","fox",
                  "elephant","owl","deer","bear","whale","shark","butterfly","bee","hummingbird"],
        "botanical":["flower","flowers","floral","rose","roses","leaf","leaves","plant","palm",
                     "botanical","tree","trees","fern","cactus","sunflower","tulip","orchid"],
        "landscape":["mountain","mountains","forest","ocean","sea","beach","sunset","sunrise",
                     "lake","river","desert","waterfall","aurora","valley","cliff","island"],
        "space":["space","galaxy","nebula","planet","moon","stars","astronaut","solar","cosmos"],
        "abstract":["abstract","geometric","minimal","minimalist","pattern","shapes","gradient"],
        "vehicle":["car","cars","motorcycle","plane","aircraft","train","ship","boat","truck","bike"],
        "city":["city","skyline","cityscape","street","building","architecture","bridge","map"],
        "food":["coffee","wine","cocktail","beer","food","kitchen","fruit","tea","whisky"],
        "sport":["football","soccer","boxing","surf","surfing","golf","basketball","cycling","ski"],
        "typography":["quote","quotes","text","word","words","lettering","typography","sign"]}
cnt = collections.Counter()
for q in rest:
    toks = set(re.findall(r"[a-z]+", q))
    for k, ws in SUBJ.items():
        if toks & set(ws):
            cnt[k] += 1
print("non-franchise query demand by subject bucket:")
for k, c in cnt.most_common():
    print(f"  {k:<12} {c:>5}  ({c/len(rest)*100:4.1f}% of non-franchise queries)")
json.dump({"franchise_matched": sorted(matched), "rest": rest}, open(os.path.join(D, "demand_split.json"), "w"))
