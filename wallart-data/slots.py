#!/usr/bin/env python3
"""For each big template, what actually fills the slot? These lists ARE the
generator's input, so they need to be extracted rather than guessed."""
import csv, re, collections, json
csv.field_size_limit(50 << 20)
BASE = ("/tmp/claude-0/-home-user-wonderleaf-books/"
        "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/an/")
BOIL = re.compile(r"\s*(framed\s+)?wall art poster canvas print picture.*$", re.I)
TAIL = re.compile(r"\s*art print\s*$", re.I)
NUM  = re.compile(r"\s+\d+\s*$")
subs = []
with open(BASE + "titles.csv", newline="", encoding="utf-8") as f:
    r = csv.reader(f); next(r)
    for p in r:
        if len(p) >= 3:
            s = NUM.sub("", TAIL.sub("", BOIL.sub("", p[2])).strip(' "')).strip()
            if s: subs.append(s)
print(f"{len(subs):,} subject phrases\n")

def after(pat, n=30):
    """values following a phrase"""
    rx = re.compile(pat + r"\s+(.{2,40}?)(?:$|,)", re.I)
    c = collections.Counter()
    for s in subs:
        m = rx.search(s)
        if m: c[m.group(1).strip().lower()] += 1
    return c

def before(pat, n=30):
    rx = re.compile(r"(?:^|,)\s*(.{2,40}?)\s+" + pat, re.I)
    c = collections.Counter()
    for s in subs:
        m = rx.search(s)
        if m: c[m.group(1).strip().lower()] += 1
    return c

JOBS = [
 ("IN THE STYLE OF {X}",        after, r"in the style of"),
 ("INSPIRED BY {X}",            after, r"inspired by"),
 ("{X} IN THE GARDEN",          before, r"in the garden"),
 ("{X} IN THE FOREST",          before, r"in the forest"),
 ("{X} ON THE BEACH",           before, r"on the beach"),
 ("{X} IN THE MOUNTAINS",       before, r"in the mountains"),
 ("{X} IN A VASE",              before, r"in a vase"),
 ("PORTRAIT OF A {X}",          after,  r"portrait of a"),
 ("PAINTING OF A {X}",          after,  r"painting of a"),
 ("{X} WITH A CAT",             before, r"with a cat"),
 ("{X} DEFINITION",             before, r"definition"),
 ("{X} SKYLINE",                before, r"skyline"),
 ("{X} MAP",                    before, r"\bmap\b"),
 ("WINDOW VIEW OF {X}",         after,  r"window view of"),
 ("{X} VINTAGE TRAVEL POSTER",  before, r"vintage travel poster"),
 ("TRAVEL POSTER FOR {X}",      after,  r"travel poster for"),
 ("{X} MID CENTURY MODERN",     before, r"mid century modern"),
 ("COLOURFUL {X} ILLUSTRATION", after,  r"colourful"),
]
out = {}
for name, fn, pat in JOBS:
    c = fn(pat)
    out[name] = c.most_common(400)
    print(f"--- {name}: {len(c):,} distinct values, {sum(c.values()):,} uses")
    print("    " + ", ".join(f"{k}({v})" for k, v in c.most_common(22)))
    print()
json.dump(out, open(BASE + "slotvalues.json", "w"), indent=1)
print("saved slotvalues.json")
