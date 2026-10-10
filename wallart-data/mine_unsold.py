#!/usr/bin/env python3
"""The seller's own unsold wall-art export - and the Watchers column in it.

This is the only first-party engagement signal in the whole project. Every
other "what sells" number so far has been competitor listing volume, which is
supply read as demand. A watcher is a real person who saved a real listing.

The file is an eBay unsold-listings template: three #INFO lines, then the
header on line 4, then one parent row per listing followed by variation rows.
"""
import csv, collections, json, os, re, sys

csv.field_size_limit(10**9)
P = "/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/ebay/RELIST_old_wall_art_FINAL.csv"
f = open(P, newline="", encoding="utf-8-sig", errors="replace")
for _ in range(3):
    f.readline()
r = csv.reader(f)
hdr = [h.strip() for h in next(r)]
ix = {h: i for i, h in enumerate(hdr)}
print("columns:", len(hdr))
for k in ("Title", "Watchers", "Bids", "High Bid", "Status", "Start price", "Relationship details"):
    print(f"  {k!r} -> index {ix.get(k)}")

def g(row, k):
    i = ix.get(k)
    return row[i].strip() if i is not None and i < len(row) else ""

n = 0
watch = collections.Counter()
titled = []
status = collections.Counter()
for row in r:
    if not row or not g(row, "Title"):
        continue
    n += 1
    t = g(row, "Title")
    w = g(row, "Watchers")
    try:
        wn = int(w) if w else 0
    except ValueError:
        wn = 0
    watch[wn] += 1
    status[g(row, "Status")] += 1
    titled.append((wn, t))

print(f"\n{n:,} listings with a title")
print("status:", dict(status.most_common(5)))
tot_w = sum(k * v for k, v in watch.items())
nz = sum(v for k, v in watch.items() if k > 0)
print(f"total watchers across the catalogue: {tot_w:,}")
print(f"listings with at least one watcher:  {nz:,}  ({nz/n*100:.2f}%)")
print("watcher histogram:", {k: v for k, v in sorted(watch.items())[:10]})

# what did the watched listings have in common?
STOP = set("framed art print wall poster canvas picture the a of and in on with for to".split())
def words(t):
    return [w for w in re.findall(r"[a-z]+", t.lower()) if w not in STOP and len(w) > 2]

allw = collections.Counter()
watw = collections.Counter()
for wn, t in titled:
    ws = set(words(t))
    allw.update(ws)
    if wn > 0:
        watw.update(ws)

# Significance, not just lift. With only 1,770 watched listings out of 168,819,
# a lift computed over thousands of words will throw up large ratios by chance.
# Expected watched for a word = (listings carrying it) x base rate; the excess
# is scored in Poisson standard deviations, and only >=3 sigma is reported.
base = nz / n
scored = []
for w, tot in allw.items():
    if tot < 150:
        continue
    c = watw.get(w, 0)
    exp = tot * base
    if exp <= 0:
        continue
    z = (c - exp) / (exp ** 0.5)
    scored.append((z, c, tot, exp, w))

print(f"\nbase rate: {base*100:.2f}% of listings get a watcher")
print(f"words tested (>=150 listings): {len(scored):,}")
print(f"\nOVER-PERFORMING WORDS (>= 3 sigma above the base rate)")
print(f"  {'z':>6}  {'watched':>8} {'listings':>9} {'exp':>7}  {'rate':>6}  word")
hits = [x for x in scored if x[0] >= 3]
for z, c, tot, exp, w in sorted(hits, reverse=True)[:35]:
    print(f"  {z:6.1f}  {c:>8,} {tot:>9,} {exp:>7.1f}  {c/tot*100:5.2f}%  {w}")
if not hits:
    print("  none")

print(f"\nUNDER-PERFORMING WORDS (<= -3 sigma), min 1,500 listings")
lows = [x for x in scored if x[0] <= -3 and x[2] >= 1500]
for z, c, tot, exp, w in sorted(lows)[:25]:
    print(f"  {z:6.1f}  {c:>8,} {tot:>9,} {exp:>7.1f}  {c/tot*100:5.2f}%  {w}")
if not lows:
    print("  none")

json.dump({"listings": n, "watchers_total": tot_w, "with_watcher": nz,
           "base_rate": base,
           "scored": [{"word": w, "z": round(z, 2), "watched": c,
                       "listings": tot, "rate": round(c / tot, 5)}
                      for z, c, tot, exp, w in sorted(scored, reverse=True)]},
          open("/tmp/claude-0/-home-user-wonderleaf-books/af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/learn/unsold_stats.json", "w"), indent=1)
print("\nsaved unsold_stats.json")
