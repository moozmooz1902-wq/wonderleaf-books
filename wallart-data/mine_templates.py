#!/usr/bin/env python3
"""Find the title templates each competitor actually generates from.

Method: strip the boilerplate tail, then replace the rare words in a title with
a slot and count the resulting skeletons. A word is "rare" if it appears in
fewer than RARE titles - those are the subjects being swapped in. The words
that survive are the template's fixed scaffolding.

Reported per set, because the three sets are three different builders.
"""
import csv, collections, json, os, re

csv.field_size_limit(10**9)
B = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/learn"
RARE = 400
TAILS = ["framed wall art poster canvas print picture", "poster canvas print picture",
         "wall art poster canvas print picture", "art print", "poster art print"]

titles = collections.defaultdict(list)
r = csv.reader(open(os.path.join(B, "rows.tsv"), newline="", encoding="utf-8"), delimiter="\t")
hdr = next(r); ix = {h: i for i, h in enumerate(hdr)}
seen = collections.defaultdict(set)
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
    titles[s].append(t)

for s in titles:
    print(f"\n{'='*70}\n{s.upper()}  {len(titles[s]):,} distinct titles")
    # strip boilerplate
    stripped = []
    for t in titles[s]:
        low = t.lower()
        for tail in TAILS:
            if low.endswith(tail):
                low = low[: -len(tail)].strip()
                break
        stripped.append(low)
    df = collections.Counter()
    for t in stripped:
        df.update(set(re.findall(r"[a-z]+", t)))
    skel = collections.Counter()
    for t in stripped:
        ws = re.findall(r"[a-z]+|\d+", t)
        sk = " ".join(w if (w.isalpha() and df[w] >= RARE) else "{}" for w in ws)
        sk = re.sub(r"(\{\} ?){2,}", "{} ", sk).strip()
        if sk:
            skel[sk] += 1
    print(f"  distinct skeletons: {len(skel):,}")
    cov = 0
    for sk, c in skel.most_common(18):
        cov += c
        print(f"    {c:>7,}  {sk[:88]}")
    print(f"  top 18 cover {cov/len(stripped)*100:.1f}% of this set's distinct titles")
    # the high-frequency scaffolding words
    print("  scaffolding words (in >2% of titles):")
    sc = [(w, c) for w, c in df.most_common(40) if c / len(stripped) > 0.02]
    print("    " + "  ".join(f"{w}={c/len(stripped)*100:.1f}%" for w, c in sc[:24]))
