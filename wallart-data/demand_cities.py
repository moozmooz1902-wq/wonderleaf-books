import os, json, re, collections
D = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/harvest2/displate"
dem = json.load(open(os.path.join(D, "demand.json")))
queries = dem["queries"]

# Unambiguous UK city/town names only. Names that are also common English words
# (Bath, Wells, Derby, Lincoln, Perth, Boston, Hull, Bangor, Newport, Richmond,
# Washington, Hamilton, Preston, Lancaster, Chester) are excluded rather than
# guessed at - the naive match on river names showed what that costs.
CITIES = """london birmingham glasgow liverpool manchester edinburgh bristol cardiff
coventry nottingham leicester sunderland belfast brighton plymouth wolverhampton
swansea southampton salford aberdeen portsmouth peterborough dundee oxford norwich
cambridge salisbury exeter gloucester carlisle worcester durham inverness stirling
canterbury lichfield ripon truro doncaster colchester wrexham dunstable elgin
leeds sheffield bradford wakefield stoke westminster york""".split()

# queries that mention a city, with the foreign homonym stripped out
FOREIGN = {"york": ["new york", "new yorker", "newyork", "yorkshire"]}
hits = collections.Counter(); examples = collections.defaultdict(list)
for q in queries:
    toks = set(re.findall(r"[a-z]+", q))
    for c in CITIES:
        if c not in toks:
            continue
        if any(f in q for f in FOREIGN.get(c, [])):
            continue
        hits[c] += 1
        if len(examples[c]) < 6:
            examples[c].append(q)

print(f"UK city names checked: {len(CITIES)}")
print(f"cities with >=1 Displate search: {len(hits)}")
print(f"total city-bearing queries: {sum(hits.values()):,} of {len(queries):,} ({sum(hits.values())/len(queries)*100:.2f}%)\n")
for c, n in hits.most_common():
    print(f"  {n:>3}  {c:<14} {'; '.join(examples[c])}")
print("\ncities with ZERO searches:")
print("  " + ", ".join(c for c in CITIES if c not in hits))
