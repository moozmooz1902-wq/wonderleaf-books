#!/usr/bin/env python3
"""Rebuild every t-shirt title on the live catalogue's proven formula.

Shape, taken from the 244,838 live listings (only 11 of which depart from it):

    {head}  Mens Womens T-Shirt  [theme]  {tail}

The live keyword coverage this reproduces: Mens 100%, Womens 100%,
T-Shirt 100%, Unisex 97.5%, Novelty 89.4%, Gift 81.6%, Tee 67.6%. Because
Gift and Tee are not universal there, the tail has faithful shorter variants,
which buy head characters when a title needs to be made unique.

Uniqueness is enforced, not hoped for. Each listing gets an ordered pool of
candidate words - the distinctive words of its old title, then its slogan,
then its subject - and the builder searches head lengths and tail variants
until it finds a combination that fits 80 characters and has not been used.
"""
import csv, re, collections, json

csv.field_size_limit(20 << 20)
LIMIT   = 80
GARMENT = "Mens Womens T-Shirt"
TAILS   = ["Unisex Novelty Gift Tee",      # 13,412 live + the two padded forms
           "Unisex Novelty Gift",          #  4,204 live
           "Unisex Novelty Tee",
           "Unisex Novelty"]               #  3,274 live
EXTRAS  = ["Funny", "Present"]             # live pads with these, in this order

THEME = {"humour": "Funny", "football": "Football", "music": "Music",
         "birthday": "Birthday", "seasonal": "Christmas", "pets": "Pet",
         "biker": "Biker", "nerd": "Geek", "fishing2": "Fishing",
         "fishing": "Fishing", "family": "Family", "gym": "Gym",
         "patriotic": "Patriotic", "trades": "Trade", "drinking": "Beer",
         "gaming": "Gaming", "veteran": "Veteran", "awareness": "Awareness",
         "farming": "Farming", "faith": "Faith", "rude": "Rude",
         "memorial": "Memorial"}

STOP = {"mens", "men", "mens'", "men's", "womens", "women", "women's", "unisex",
        "t-shirt", "tshirt", "t", "shirt", "shirts", "tee", "tees", "top", "tops",
        "novelty", "gift", "gifts", "present", "presents", "idea", "ideas",
        "joke", "jokes", "funny", "adult", "adults", "humour", "humor",
        "ladies", "boys", "girls", "clothing", "apparel", "gents"}

def clean(words):
    out, seen = [], set()
    for w in words:
        k = re.sub(r"[^a-z0-9'-]", "", w.lower())
        if not k or k in STOP or k in seen:
            continue
        seen.add(k); out.append(w)
    return out

def assemble(head, theme, tail, extras):
    parts = [" ".join(head), GARMENT] + ([theme] if theme else []) + [tail] + extras
    return " ".join(p for p in parts if p)

def norm(t):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", t.lower()).split())

# ---- load ------------------------------------------------------------------
src = {}
for r in csv.DictReader(open("v7.csv", newline="", encoding="utf-8")):
    if r["slogan"]:
        src[f"WLT-{int(r['source_idx']):06d}"] = r

rows = []
with open("/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv",
          newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if not (row.get("Relationship") or "").strip():
            rows.append((row["CustomLabel"].strip(), row["*Title"].strip()))
print(f"listings {len(rows):,} | source rows {len(src):,}", flush=True)

seen, out, dropped = set(), {}, []
for sku, old in rows:
    s = src.get(sku) or {}
    theme = THEME.get(s.get("theme", ""), "")
    pool = clean(old.split()
                 + s.get("slogan", "").title().split()
                 + s.get("subject", "").title().split())
    if not pool:
        dropped.append(sku); continue

    placed = False
    # Prefer a theme word (it is a real search term) but drop it if that is
    # what stands between this listing and a unique title.
    for th in ([theme, ""] if theme else [""]):
        for tail in TAILS:
            # longest head that fits with this tail, then shrink one word at a time
            n = len(pool)
            while n > 0 and len(assemble(pool[:n], th, tail, [])) > LIMIT:
                n -= 1
            for k in range(n, 0, -1):
                head = pool[:k]
                extras = []
                for e in EXTRAS:
                    if len(assemble(head, th, tail, extras + [e])) <= LIMIT:
                        extras.append(e)
                for ex in (extras, extras[:1], []):
                    t = assemble(head, th, tail, ex)
                    if len(t) <= LIMIT and norm(t) not in seen:
                        seen.add(norm(t)); out[sku] = t; placed = True
                        break
                if placed: break
            if placed: break
        if placed: break
    if not placed:
        dropped.append(sku)

print(f"\nbuilt   {len(out):,}")
print(f"dropped {len(dropped):,}")

ts = list(out.values()); L = [len(t) for t in ts]
print(f"\nlength: min {min(L)} max {max(L)} mean {sum(L)/len(L):.1f} | over 80: {sum(1 for x in L if x > 80)}")
print(f"exact duplicates      {len(ts) - len(set(ts)):,}")
print(f"normalised duplicates {len(ts) - len(set(norm(t) for t in ts)):,}")

def cov(p):
    p = p.lower(); return 100 * sum(1 for t in ts if p in t.lower()) / len(ts)
print("\nkeyword coverage:")
for k in ("Mens", "Womens", "Mens Womens", "T-Shirt", "Unisex", "Novelty", "Gift", "Tee", "Funny"):
    print(f"   {k:<14}{cov(k):6.1f}%")

print("\nsamples:")
for sku, _ in rows[:12]:
    if sku in out: print(f"   {len(out[sku]):>2}  {out[sku]}")

json.dump({"titles": out, "dropped": dropped}, open("new_titles.json", "w"))
print("\nwrote new_titles.json")
