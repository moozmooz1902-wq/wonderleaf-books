#!/usr/bin/env python3
"""Title every listing with the text actually printed on the shirt.

render_illus.py line 108 draws row["slogan"], so the slogan IS the product.
Titles previously came from the competitor's original title instead, which is
how WLT-023016 ended up titled "Music Raising My Husband Is Exhausting..."
while the shirt reads "THIS IS WHAT AN AWESOME HUSBAND LOOKS LIKE".

    {slogan, in full wherever it fits} T-Shirt Mens [extra] [Funny|theme] [Tee] [Top]

Rules learned the hard way on the first attempt:
  - the WHOLE slogan comes first. Trimming it produced "This is What an
    Awesome T-Shirt Mens", which reads as nonsense. The slogan is only
    shortened when it physically cannot fit, and then the niche noun is kept
    so the subject survives.
  - palette names are internal codes (mono-bone, violet, coral) with no search
    value, so they never appear in a title.
  - extra words come from the niche and subject first, illustration last, and
    are capped so a title stays readable.
"""
import csv, re, collections, json

csv.field_size_limit(20 << 20)
LIMIT = 80
MAX_EXTRA = 4
THEME = {"humour": "Funny", "football": "Football", "music": "Music",
         "birthday": "Birthday", "seasonal": "Christmas", "pets": "Pet",
         "biker": "Biker", "nerd": "Geek", "fishing2": "Fishing",
         "fishing": "Fishing", "family": "Family", "gym": "Gym",
         "patriotic": "Flag", "trades": "Work", "drinking": "Beer",
         "gaming": "Gaming", "veteran": "Veteran", "awareness": "Awareness",
         "farming": "Farming", "faith": "Faith", "rude": "Rude",
         "memorial": "Memorial"}
FUNNY = {"humour", "rude"}
FUNC = {"a","an","the","of","on","in","at","to","by","for","with","and","or",
        "but","is","are","was","be","am","it","its","this","that","my","your",
        "our","i","you","we","me","no","not","so","up","out","as","if","all",
        "any","just","very","too","do","does","did","has","have","had","will",
        "would","can","could","what","who","when","why","how","from","like"}

def ws(s):  return [w for w in re.split(r"\s+", (s or "").strip()) if w]
def key(w): return re.sub(r"[^a-z0-9]", "", w.lower())
def tc(s):  return [w.capitalize() for w in ws(s)]
def norm(t): return " ".join(re.sub(r"[^a-z0-9 ]", " ", t.lower()).split())

def trim_func(x):
    x = x[:]
    while x and key(x[-1]) in FUNC:
        x.pop()
    return x

def candidates(slog, niche, extra, mids):
    """Titles in preference order. The full slogan is tried before any cut."""
    tails = ["Tee Top", "Tee", "Top", ""]
    def make(sl, ne, nm, tail):
        parts = sl + ["T-Shirt", "Mens"] + extra[:ne] + mids[:nm] \
                 + (tail.split() if tail else [])
        return " ".join(parts)
    # 1. whole slogan, shedding tail then theme then extras
    for ne in range(len(extra), -1, -1):
        for nm in range(len(mids), -1, -1):
            for tail in tails:
                t = make(slog, ne, nm, tail)
                if len(t) <= LIMIT:
                    yield t
    # 2. only now shorten the slogan, keeping the niche noun so the subject
    #    survives the cut
    for n in range(len(slog) - 1, 0, -1):
        sl = trim_func(slog[:n])
        if not sl:
            continue
        if niche and key(niche) not in {key(x) for x in sl}:
            sl = sl + [niche.capitalize()]
        for ne in range(len(extra), -1, -1):
            for nm in range(len(mids), -1, -1):
                for tail in tails:
                    t = make(sl, ne, nm, tail)
                    if len(t) <= LIMIT:
                        yield t

src = {}
for r in csv.DictReader(open("v7.csv", newline="", encoding="utf-8")):
    if r["slogan"]:
        src[f"WLT-{int(r['source_idx']):06d}"] = r

skus = []
with open("/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv",
          newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if not (row.get("Relationship") or "").strip():
            skus.append(row["CustomLabel"].strip())
print(f"listings {len(skus):,}", flush=True)

seen, titles, failed = set(), {}, []
full_slogan = 0
for sku in skus:
    s = src.get(sku) or {}
    slog = tc(s.get("slogan", ""))
    if not slog:
        failed.append(sku); continue
    th = s.get("theme", "")
    mids = ["Funny"] if th in FUNNY else []
    tw = THEME.get(th)
    if tw and tw not in mids:
        mids.append(tw)
    have = {key(w) for w in slog}
    extra, eseen = [], set()
    for field in ("niche", "subject", "illustration"):      # palette excluded
        for w in ws(s.get(field, "").replace("-", " ")):
            k = key(w)
            if not k or len(k) < 3 or k in have or k in eseen or k in FUNC:
                continue
            eseen.add(k); extra.append(w.capitalize())
            if len(extra) >= MAX_EXTRA:
                break
        if len(extra) >= MAX_EXTRA:
            break
    placed = False
    for t in candidates(slog, s.get("niche", ""), extra, mids):
        if norm(t) not in seen:
            seen.add(norm(t)); titles[sku] = t; placed = True
            if norm(t).startswith(norm(" ".join(slog))):
                full_slogan += 1
            break
    if not placed:
        failed.append(sku)

print(f"built {len(titles):,} | failed {len(failed):,}")
print(f"titles that open with the COMPLETE printed slogan: {full_slogan:,}"
      f" ({100*full_slogan/len(titles):.1f}%)")
ts = list(titles.values()); L = [len(t) for t in ts]
print(f"length min {min(L)} mean {sum(L)/len(L):.1f} max {max(L)}")
print(f"exact dup {len(ts)-len(set(ts))} | normalised dup {len(ts)-len(set(norm(t) for t in ts))}")
def cov(p):
    p = p.lower(); return 100*sum(1 for t in ts if p in t.lower())/len(ts)
print()
for k in ("T-Shirt","Mens","Funny","Top","Tee","Womens","Unisex","Novelty"):
    print(f"   {k:<10}{cov(k):6.1f}%")
print("\nsamples (printed on shirt -> title):")
for sku in skus[:12]:
    if sku in titles:
        print(f"   {src[sku]['slogan']!r}")
        print(f"     -> {titles[sku]}")
json.dump({"titles": titles, "failed": failed}, open("slogan_titles.json", "w"))
