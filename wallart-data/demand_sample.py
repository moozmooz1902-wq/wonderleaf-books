import os, re, json, random
D = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/harvest2/displate"
rest = json.load(open(os.path.join(D, "demand_split.json")))["rest"]
SUBJWORDS = set("""cat cats dog dogs horse bird birds lion tiger wolf fox elephant owl deer bear
whale shark butterfly bee hummingbird flower flowers floral rose roses leaf leaves plant palm
botanical tree trees fern cactus sunflower tulip orchid mountain mountains forest ocean sea beach
sunset sunrise lake river desert waterfall aurora valley cliff island space galaxy nebula planet
moon stars astronaut solar cosmos abstract geometric minimal minimalist pattern shapes gradient
car cars motorcycle plane aircraft train ship boat truck bike city skyline cityscape street
building architecture bridge map coffee wine cocktail beer food kitchen fruit tea whisky football
soccer boxing surf surfing golf basketball cycling ski quote quotes text word words lettering
typography sign""".split())
plain = [q for q in rest if not (set(re.findall(r"[a-z]+", q)) & SUBJWORDS)]
print(f"neither franchise-matched nor subject-matched: {len(plain):,} ({len(plain)/34789*100:.1f}% of all queries)\n")
random.seed(7)
for q in random.sample(plain, 60):
    print("  " + q)
print("\nword count distribution of those queries:")
import collections
wc = collections.Counter(len(q.split()) for q in plain)
for k in sorted(wc): print(f"  {k} word(s): {wc[k]:,}")
