"""Check the generated CSVs are structurally what eBay expects."""
import csv, glob, sys, collections
csv.field_size_limit(2**31 - 1)
files = sorted(glob.glob(sys.argv[1]))
ACTION = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=745|CC=UTF-8)"
tot_parent = tot_child = 0
titles = set(); labels = set(); bad = collections.Counter(); longt = 0
for fn in files:
    with open(fn, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    group, expect = None, 0
    for r in rows:
        if r[ACTION] == "Add":
            if group is not None and group != expect:
                bad["parent with wrong child count"] += 1
            # The parent declares its own sizes, so the expected child count
            # comes from the file rather than from a constant here.
            expect = len([x for x in r["RelationshipDetails"]
                          .replace("Size=", "").split(";") if x])
            group = 0
            tot_parent += 1
            if not r["CustomLabel"]: bad["parent missing CustomLabel"] += 1
            if r["*StartPrice"]: bad["parent has a price"] += 1
            if r["*Quantity"]: bad["parent has a quantity"] += 1
            if r["*C:Size"]: bad["parent has a size"] += 1
            if not r["PicURL"].startswith("https://"): bad["parent PicURL"] += 1
            if not r["*Description"]: bad["parent missing description"] += 1
            if not r["ShippingProfileName"]: bad["parent missing profile"] += 1
            if r["*Title"] in titles: bad["duplicate title"] += 1
            titles.add(r["*Title"])
            if len(r["*Title"]) > 80: longt += 1
            labels.add(r["CustomLabel"])
        elif r["Relationship"] == "Variation":
            group = (group or 0) + 1
            tot_child += 1
            if r["CustomLabel"]: bad["child has a CustomLabel"] += 1
            if r["PicURL"]: bad["child has a PicURL"] += 1
            if r["*Description"]: bad["child has a description"] += 1
            if not r["*StartPrice"]: bad["child missing price"] += 1
            if not r["*C:Size"]: bad["child missing size"] += 1
            if r["ShippingProfileName"]: bad["child has a profile"] += 1
        else:
            bad["row that is neither parent nor variation"] += 1
    if group is not None and group != expect:
        bad["last group in file incomplete"] += 1

print(f"  files            {len(files)}")
print(f"  parents          {tot_parent:,}")
print(f"  variation rows   {tot_child:,}   ({tot_child/max(tot_parent,1):.1f} per listing)")
print(f"  unique titles    {len(titles):,}")
print(f"  unique labels    {len(labels):,}")
print(f"  titles over 80   {longt}")
print(f"  every title has 'T-Shirt': {all('t-shirt' in t.lower() for t in titles)}")
print("  problems: " + ("NONE" if not bad else ""))
for k, v in bad.most_common():
    print(f"    {v:,}  {k}")
