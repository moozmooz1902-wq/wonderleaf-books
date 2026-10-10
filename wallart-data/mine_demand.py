import os, re, json, collections, urllib.parse
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "displate")

def locs(fn):
    return re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(D, fn), encoding="utf-8").read())

# the 191 licensed brands are a negative list: never generate these
brands = [u.rsplit("/", 1)[-1] for u in locs("brands_sitemap1.xml")]
brandwords = set()
for b in brands:
    for w in b.split("-"):
        if len(w) > 3:
            brandwords.add(w)

queries = []
for u in locs("popular_searches_sitemap1.xml"):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query).get("q", [""])[0]
    q = urllib.parse.unquote_plus(q).strip().lower()
    if q:
        queries.append(q)
print(f"search queries      {len(queries):,}   (distinct {len(set(queries)):,})")
print(f"licensed brands     {len(brands)}  -> {len(brandwords)} brand words")

# split: a query touching any brand word is IP-contaminated
ip, clean = [], []
for q in queries:
    toks = set(re.findall(r"[a-z0-9]+", q))
    (ip if toks & brandwords else clean).append(q)
print(f"IP-contaminated     {len(ip):,}  ({len(ip)/len(queries)*100:.1f}%)")
print(f"clean of brands     {len(clean):,}  ({len(clean)/len(queries)*100:.1f}%)")

# what do the clean queries actually ask for?
uni = collections.Counter()
for q in clean:
    for w in re.findall(r"[a-z]{3,}", q):
        uni[w] += 1
print("\ntop 60 words in brand-clean queries:")
line = []
for w, c in uni.most_common(60):
    line.append(f"{w}({c})")
print("  " + "  ".join(line))

# single-word queries are the purest generic demand
single = sorted(set(q for q in clean if " " not in q and re.fullmatch(r"[a-z]{3,}", q)))
print(f"\nsingle-word brand-clean queries: {len(single):,}")
print("  " + "  ".join(single[:80]))

json.dump({"queries": queries, "clean": clean, "ip": ip,
           "brands": brands, "single": single},
          open(os.path.join(D, "demand.json"), "w"), ensure_ascii=False)
