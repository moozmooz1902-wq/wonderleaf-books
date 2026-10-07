#!/usr/bin/env python3
"""Compare the live GR- t-shirt titles (which sell) with our new WLT- titles."""
import csv, json, re, collections
csv.field_size_limit(20 << 20)

live = [t[2] for t in json.load(open("tees.json"))]
new  = []
with open("/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if not (row.get("Relationship") or "").strip():
            new.append(row["*Title"].strip())

def cover(titles, phrase):
    p = phrase.lower()
    return sum(1 for t in titles if p in t.lower())

KEYS = ["mens", "womens", "mens womens", "t-shirt", "tshirt", "tee", "unisex",
        "novelty", "gift", "funny", "top", "shirt", "ladies", "boys", "girls",
        "christmas", "birthday", "dad", "mum", "slogan", "graphic", "retro",
        "vintage", "cool", "cute", "men's", "women's"]
print(f"{'keyword':<16}{'LIVE (sells)':>16}{'OURS':>16}")
print("-" * 48)
for k in KEYS:
    a, b = cover(live, k), cover(new, k)
    print(f"{k:<16}{a:>9,} {100*a/len(live):>5.1f}%{b:>9,} {100*b/len(new):>5.1f}%")

print(f"\nlive titles {len(live):,} | ours {len(new):,}")
for name, ts in (("LIVE", live), ("OURS", new)):
    L = [len(t) for t in ts]
    print(f"{name}: length min {min(L)} max {max(L)} mean {sum(L)/len(L):.1f} | over 80 chars: {sum(1 for x in L if x>80)}")

# the trailing boilerplate each catalogue uses
def tail(ts, n=4):
    c = collections.Counter()
    for t in ts:
        w = t.split()
        c[" ".join(w[-n:])] += 1
    return c
print("\ncommonest last-4-words, LIVE:")
for p, c in tail(live).most_common(8): print(f"   {c:>8,}  {p}")
print("\ncommonest last-4-words, OURS:")
for p, c in tail(new).most_common(8): print(f"   {c:>8,}  {p}")

print("\nsample LIVE titles:")
for t in live[:6]: print("   ", t)
print("\nsample OUR titles:")
for t in new[:6]: print("   ", t)
