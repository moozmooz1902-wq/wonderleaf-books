import os, re, json, glob, collections
SC   = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad"
D    = os.path.join(SC, "harvest2", "displate")
dem  = json.load(open(os.path.join(D, "demand.json")))

# build the UK place atom set from the already-extracted gazetteer lists
places = {}            # lowercase name -> set of source list names
for fn in glob.glob(os.path.join(SC, "gaz", "out_*.txt")):
    tag = os.path.basename(fn)[4:-4]
    for line in open(fn, encoding="utf-8", errors="replace"):
        nm = line.strip()
        nm = re.sub(r"\s*\([^)]*\)", "", nm).strip()       # drop disambiguators
        if 3 <= len(nm) <= 40 and re.fullmatch(r"[A-Za-z' \-\.]+", nm):
            places.setdefault(nm.lower(), set()).add(tag)
print(f"UK place atoms       {len(places):,}  from {len(glob.glob(os.path.join(SC,'gaz','out_*.txt')))} lists")

queries = dem["queries"]
qset = set(queries)
# a place has demand if it is itself a query, or appears as a whole phrase in one
hit_exact = sorted(p for p in places if p in qset)
print(f"places that are an exact Displate search query: {len(hit_exact):,}")

# phrase containment, for places appearing inside longer queries
inq = collections.Counter()
for q in queries:
    toks = q.split()
    for n in (1, 2, 3):
        for i in range(len(toks) - n + 1):
            g = " ".join(toks[i:i+n])
            if g in places:
                inq[g] += 1
print(f"places appearing in any query (as a phrase):    {len(inq):,}")
print(f"total query-hits on UK places:                  {sum(inq.values()):,}")

print("\ntop 50 UK places by number of distinct Displate searches:")
for p, c in inq.most_common(50):
    src = ",".join(sorted(places[p])[:2])
    mark = "*" if p in qset else " "
    print(f"  {c:>4}{mark}  {p:<28} [{src}]")

json.dump({"atoms": {k: sorted(v) for k, v in places.items()},
           "exact": hit_exact,
           "inq": dict(inq)},
          open(os.path.join(D, "places_demand.json"), "w"), ensure_ascii=False)
