#!/usr/bin/env python3
"""What the competitor titles actually say, per set, measured.

Only parent rows carry a title, so this reads the titled rows and asks three
things: which technique words they use, which colour words, and what the
boilerplate tail is. Counting is per LISTING, not per row, because a listing
is 10 rows and counting rows would multiply everything by ten.
"""
import csv, collections, json, os, re

csv.field_size_limit(10**9)
B = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/learn"

TECH = """watercolour watercolor linocut lino woodcut etching engraving lithograph
screenprint risograph gouache acrylic oil pastel charcoal pencil graphite ink
collage photograph photography digital vector illustration painting drawing
sketch print impasto airbrush halftone silhouette lineart monoline embroidery
batik woodblock ukiyo-e aquatint mezzotint cyanotype blueprint""".split()
MOVE = """abstract impressionism impressionist expressionism expressionist cubism
cubist surrealism surrealist bauhaus minimalist minimalism maximalist art-deco
deco nouveau baroque rococo renaissance gothic romantic realism naive folk
scandinavian scandi boho bohemian mid-century midcentury modernist brutalist
pop-art popart psychedelic retro vintage antique kitsch japandi wabi""".split()
COL = """black white grey gray cream beige ivory bone oatmeal sand greige taupe
brown tan rust terracotta orange coral peach apricot mustard yellow gold ochre
olive sage green emerald teal turquoise aqua cyan blue navy cobalt indigo
petrol lilac lavender purple violet plum magenta pink blush rose red crimson
burgundy maroon copper bronze silver pastel neon monochrome duotone sepia""".split()
ROOM = """living-room livingroom bedroom kitchen bathroom hallway nursery office
dining-room diningroom gym classroom cafe bar pub studio lounge playroom
laundry mancave""".split()

def toks(s):
    return re.findall(r"[a-z]+(?:-[a-z]+)?", s.lower())

sets = collections.Counter()
tech = collections.defaultdict(collections.Counter)
move = collections.defaultdict(collections.Counter)
col  = collections.defaultdict(collections.Counter)
room = collections.defaultdict(collections.Counter)
tails = collections.defaultdict(collections.Counter)
words = collections.defaultdict(collections.Counter)
lens  = collections.defaultdict(list)
titles_seen = collections.defaultdict(set)

r = csv.reader(open(os.path.join(B, "rows.tsv"), newline="", encoding="utf-8"), delimiter="\t")
hdr = next(r); ix = {h: i for i, h in enumerate(hdr)}
for row in r:
    if len(row) != len(hdr):
        continue
    t = row[ix["title"]].strip()
    if not t:
        continue
    s = row[ix["set"]]
    sets[s] += 1
    titles_seen[s].add(t)
    tk = toks(t)
    words[s].update(tk)
    lens[s].append(len(t))
    tset = set(tk)
    for w in TECH:
        if w in tset: tech[s][w] += 1
    for w in MOVE:
        if w in tset: move[s][w] += 1
    for w in COL:
        if w in tset: col[s][w] += 1
    for w in ROOM:
        if w in tset: room[s][w] += 1
    # the boilerplate tail: last 4 words
    tails[s][" ".join(t.split()[-4:])] += 1

print("LISTINGS WITH A TITLE (one per listing)")
for s in sets:
    u = len(titles_seen[s])
    print(f"  {s:<9} {sets[s]:>9,} titled   {u:>9,} distinct  "
          f"({(1-u/sets[s])*100:4.1f}% repeats)  mean len {sum(lens[s])/len(lens[s]):.0f} chars")

def show(name, d, topn=22):
    print(f"\n{name}  (share of that set's titled listings)")
    for s in sets:
        tot = sets[s]
        got = d[s].most_common(topn)
        if not got: 
            print(f"  {s}: none"); continue
        print(f"  {s} ({sum(d[s].values())/tot*100:.1f}% of titles carry one):")
        print("    " + "  ".join(f"{w}={c/tot*100:.2f}%" for w, c in got))

show("TECHNIQUE WORDS", tech)
show("MOVEMENT / STYLE WORDS", move)
show("COLOUR WORDS", col)
show("ROOM WORDS", room)

print("\nBOILERPLATE TAIL (last 4 words), top 6 per set")
for s in sets:
    for t, c in tails[s].most_common(6):
        print(f"  {s:<9} {c:>9,}  ...{t}")

json.dump({"tech": {s: dict(tech[s]) for s in sets},
           "move": {s: dict(move[s]) for s in sets},
           "col":  {s: dict(col[s])  for s in sets},
           "room": {s: dict(room[s]) for s in sets},
           "counts": dict(sets),
           "distinct": {s: len(titles_seen[s]) for s in sets},
           "words": {s: dict(words[s].most_common(400)) for s in sets}},
          open(os.path.join(B, "title_stats.json"), "w"), indent=1)
