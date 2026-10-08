#!/usr/bin/env python3
"""Fy!'s export is split one file per collection, so it is a LABELLED dataset:
how many listings each subject/room/colour collection holds, and what the
titles in it look like."""
import collections, re, json
BASE = ("/tmp/claude-0/-home-user-wonderleaf-books/"
        "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/an/")
rows = collections.defaultdict(list)
with open(BASE + "titles.tsv", encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3 and p[0] == "fy300k":
            rows[p[1].replace(".csv", "")].append(p[2])
print(f"collections {len(rows)} | listings {sum(len(v) for v in rows.values()):,}\n")
print(f"{'listings':>9}  {'distinct':>9}  collection")
for c, v in sorted(rows.items(), key=lambda x: -len(x[1])):
    print(f"{len(v):>9,}  {len(set(v)):>9,}  {c}")

ALL = [t for v in rows.values() for t in v]
print(f"\ntotal {len(ALL):,} | distinct {len(set(ALL)):,}")
L = [len(t) for t in ALL]
print(f"title length mean {sum(L)/len(L):.1f} max {max(L)} over80 {sum(1 for x in L if x>80):,}")

# Fy! titles name artists and movements - that is the copyright surface
ART = {
 "pre-1956 artists (safe)": r"\b(matisse|van gogh|monet|klimt|hokusai|mucha|cezanne|renoir|degas|turner|morris|kandinsky|klee|munch|vermeer|rembrandt|hiroshige|utamaro|redoute|audubon|haeckel|besler)\b",
 "post-1955 artists (NOT safe)": r"\b(picasso|dali|warhol|rothko|hopper|pollock|o'keeffe|basquiat|haring|lichtenstein|hockney|kusama|escher|magritte|miro|banksy|riley)\b",
 "movement names": r"\b(impressionism|impressionist|cubism|surrealism|expressionism|bauhaus|art deco|art nouveau|fauvism|baroque|renaissance|ukiyo|post.?impressionism)\b",
}
low = [t.lower() for t in ALL]
print("\n=== artist and movement naming in Fy! titles ===")
for k, rx in ART.items():
    r = re.compile(rx); n = sum(1 for t in low if r.search(t))
    print(f"   {k:<30}{n:>8,}  {100*n/len(ALL):5.2f}%")
    hits = collections.Counter()
    for t in low:
        for m in r.findall(t): hits[m] += 1
    print("      ", dict(hits.most_common(12)))

print("\n=== sample titles per big collection ===")
for c, v in sorted(rows.items(), key=lambda x: -len(x[1]))[:8]:
    print(f"--- {c} ({len(v):,})")
    for t in v[:4]: print("    ", t[:94])
json.dump({c: len(v) for c, v in rows.items()}, open(BASE + "fy_collections.json", "w"))
