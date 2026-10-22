import csv, json, os, re, sys
HERE="/home/user/wonderleaf-books/wallart-data"
sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,"gen"))
import allocate, build_ebay as B
D=os.path.join(HERE,"ebay","tests")
bad_total=0
for fn in sorted(os.listdir(D)):
    if not fn.endswith(".csv"): continue
    bucket=fn.rsplit("_TEST_",1)[0]
    st=B.STORES[bucket]; base=st["pic_base"].rstrip("/")
    rows=list(csv.DictReader(open(os.path.join(D,fn),encoding="utf-8-sig")))
    probs=[]
    parents=[r for r in rows if r.get("Relationship")!="Variation"]
    kids=[r for r in rows if r.get("Relationship")=="Variation"]
    if len(kids)!=len(parents)*B.VARIATIONS:
        probs.append(f"{len(parents)} parents but {len(kids)} children")
    # parent followed by exactly its own children
    i=0
    while i < len(rows):
        if rows[i].get("Relationship")=="Variation":
            probs.append(f"row {i}: variation with no parent"); break
        n=0; j=i+1
        while j<len(rows) and rows[j].get("Relationship")=="Variation": n+=1; j+=1
        if n!=B.VARIATIONS: probs.append(f"parent at {i} has {n} children")
        i=j
    for r in rows:
        for u in (r.get("PicURL") or "").split("|"):
            u=u.strip()
            if not u: continue
            if not u.startswith(base+"/"):
                probs.append(f"picture on another host: {u[:70]}")
            if f'/{st["key_prefix"].strip("/")}/listing/' not in u:
                probs.append(f"picture outside this store's prefix: {u[:70]}")
        lab=(r.get("CustomLabel") or "").strip()
        if lab:
            if not re.match(r"^WA-[0-9a-f]{16}-[0-3]$",lab):
                probs.append(f"bad SKU {lab}")
            elif allocate.store_for(lab.rsplit("-",1)[0])["bucket"]!=bucket:
                probs.append(f"SKU belongs to another bucket: {lab}")
    prices={r.get("*StartPrice") for r in kids}
    qty={r.get("*Quantity") for r in kids}
    frames=[r.get("C:Frame") for r in kids[:3]]
    firstpic=parents[0]["PicURL"].split("|")[0]
    print(f"{bucket:<20} {len(parents)} listings  {len(rows)} rows  "
          f"price={prices}  qty={qty}  first3frames={frames}")
    print(f"{'':<20} main image is black: {'black.jpg' in firstpic}")
    if probs:
        bad_total+=len(probs)
        for p in probs[:6]: print(f"   PROBLEM: {p}")
    else:
        print(f"{'':<20} structure, hosts, prefixes and SKU ownership: all clean")
print(f"\ntotal problems across all four files: {bad_total}")
