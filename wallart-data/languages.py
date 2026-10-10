#!/usr/bin/env python3
"""What languages the competitor titles are actually in.

The seller asked for this directly ("I want you to learn all languages because
you need to understand which one"). An earlier pass on a smaller corpus said
>99% English; this re-runs it on all 1.37M titles now extracted, and separates
two different things that get confused: the SCRIPT a title is written in, and
the LANGUAGE it is in when the script is Latin.
"""
import csv, collections, re, unicodedata

csv.field_size_limit(10**9)
B = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/learn/rows.tsv"

def script_of(ch):
    o = ord(ch)
    if o < 0x80:  return "ascii"
    try:    name = unicodedata.name(ch)
    except ValueError: return "other"
    for k in ("CYRILLIC", "GREEK", "ARABIC", "HEBREW", "HIRAGANA", "KATAKANA",
              "CJK", "HANGUL", "THAI", "DEVANAGARI", "ARMENIAN", "GEORGIAN"):
        if k in name: return k.lower()
    if "LATIN" in name: return "latin-accented"
    return "other"

# function words that are decisive for a language when the script is Latin
MARK = {
 "french":  r"\b(de|du|des|le|la|les|voyage|affiche|fleurs|mer|nuit|jardin|ville)\b",
 "german":  r"\b(und|der|die|das|mit|von|blumen|wald|berg|stadt|kunst)\b",
 "spanish": r"\b(el|los|las|flores|ciudad|mar|cielo|arte|noche)\b",
 "italian": r"\b(il|lo|gli|della|citta|mare|fiori|notte|arte)\b",
 "dutch":   r"\b(het|een|van|bloemen|stad|zee)\b",
 "swedish": r"\b(och|med|blommor|stad|hav)\b",
 "portuguese": r"\b(da|dos|flores|cidade|praia|noite)\b",
}
RX = {k: re.compile(v) for k, v in MARK.items()}
# NOT art/print/poster/wall: every title ends with boilerplate containing them,
# so including them made 99.998% of titles "English" by construction.
EN = re.compile(r"\b(the|and|of|with|in|for|on|at|from|by|a|an|is|to)\b")
BOILER = re.compile(r"(framed )?(wall )?art (poster )?(canvas )?print( picture)?|"
                    r"poster canvas print picture|art print|poster", re.I)

scripts = collections.Counter()
langs = collections.Counter()
n = 0
seen = set()
r = csv.reader(open(B, newline="", encoding="utf-8"), delimiter="\t")
hdr = next(r); ix = {h: i for i, h in enumerate(hdr)}
for row in r:
    if len(row) != len(hdr):
        continue
    t = row[ix["title"]].strip()
    if not t or t in seen:
        continue
    seen.add(t)
    n += 1
    sc = collections.Counter(script_of(c) for c in t if not c.isspace())
    nonascii = {k: v for k, v in sc.items() if k != "ascii"}
    scripts[max(nonascii, key=nonascii.get) if nonascii else "ascii"] += 1
    low = BOILER.sub(" ", t.lower())      # strip the tail before deciding
    if EN.search(low):
        langs["english"] += 1
    else:
        hit = [k for k, rx in RX.items() if rx.search(low)]
        langs[hit[0] if len(hit) == 1 else ("ambiguous" if hit else "unknown_or_name_only")] += 1

print(f"{n:,} distinct titles across all three dumps\n")
print("SCRIPT (the dominant non-ASCII script, else ascii)")
for k, v in scripts.most_common():
    print(f"  {k:<16} {v:>9,}  {v/n*100:6.3f}%")
print("\nLANGUAGE (English detected by function words; others only when unambiguous)")
for k, v in langs.most_common():
    print(f"  {k:<22} {v:>9,}  {v/n*100:6.3f}%")
