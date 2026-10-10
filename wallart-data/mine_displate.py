import json, os, collections
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "displate")
lic = collections.Counter(); yr = collections.Counter(); yrlic = collections.Counter()
hashes = collections.Counter(); n = 0; noimg = 0
for line in open(os.path.join(D, "displate.jsonl"), encoding="utf-8"):
    r = json.loads(line); n += 1
    lic[r["lic"]] += 1
    y = r["date"][:4] or "?"
    yr[y] += 1; yrlic[(y, r["lic"])] += 1
    if r["img"]:
        hashes[r["img"].rsplit("/", 1)[-1].split(".")[0]] += 1
    else:
        noimg += 1
print(f"records            {n:,}")
print(f"no image url       {noimg:,}")
for k, v in lic.most_common():
    print(f"  {k:<14} {v:>10,}  {v/n*100:5.1f}%")
print(f"distinct artwork   {len(hashes):,}")
rep = n - noimg - len(hashes)
print(f"repeat listings    {rep:,}  ({rep/(n-noimg)*100:.1f}% of imaged records)")
print("\ntop repeated artwork hashes:")
for h, c in hashes.most_common(5):
    print(f"  {c:>6}x  {h}")
print("\nby upload year (artwork folder date):")
for y in sorted(yr):
    nl = yrlic.get((y, "non-licensed"), 0); l = yrlic.get((y, "licensed"), 0)
    print(f"  {y}  total {yr[y]:>9,}   non-licensed {nl:>9,}   licensed {l:>9,}")
