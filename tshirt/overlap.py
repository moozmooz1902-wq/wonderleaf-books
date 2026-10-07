#!/usr/bin/env python3
"""Do the new WLT- titles collide with the live GR- titles already on the account?"""
import csv, json, re, collections
csv.field_size_limit(20 << 20)

def norm(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return " ".join(t.split())

tees = json.load(open("tees.json"))
live = {}                                     # normalised title -> [item numbers]
for item, sku, title, sp, bin_, q in tees:
    live.setdefault(norm(title), []).append((item, sku))
print(f"live t-shirts {len(tees):,} | distinct normalised titles {len(live):,}")
dupe_within = sum(len(v) - 1 for v in live.values() if len(v) > 1)
print(f"duplicate titles ALREADY live among themselves: {dupe_within:,}")

new = []
with open("/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if (row.get("Relationship") or "").strip():
            continue
        new.append((row["CustomLabel"].strip(), row["*Title"].strip()))
print(f"new listings {len(new):,}")
newnorm = collections.Counter(norm(t) for _, t in new)
print(f"new distinct normalised titles {len(newnorm):,}")

hits = [(sku, t) for sku, t in new if norm(t) in live]
print(f"\nNEW titles that already exist live: {len(hits):,}"
      f"  ({100*len(hits)/len(new):.1f}% of the upload)")
for s, t in hits[:10]:
    print(f"   {s}  {t[:78]}")

colliding_live = sorted({it for s, t in hits for it, _ in live[norm(t)]})
print(f"\nlive item numbers implicated by those collisions: {len(colliding_live):,}")
json.dump(colliding_live, open("colliding_live_items.json", "w"))

# token-level similarity as a softer signal
livetok = collections.Counter()
for t in live: livetok[t.split()[0] if t else ""] += 1
print(f"\nsample live titles:")
for t in list(live)[:5]: print("   ", t[:80])
