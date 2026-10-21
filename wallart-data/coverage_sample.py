import json, os, random, sys, urllib.request, collections, math
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/user/wonderleaf-books/wallart-data")
sys.path.insert(0, "/home/user/wonderleaf-books/wallart-data/gen")
import grid, allocate
PLAN = json.load(open("/home/user/wonderleaf-books/wallart-data/stores.json"))
BY = {s["bucket"]: s for s in PLAN["stores"]}
subjects = json.load(open("/home/user/wonderleaf-books/wallart-data/gen/subjects.json"))
skus = sorted(grid.sku_for(j) for j in grid.expand(subjects))[:960000]
byb = collections.defaultdict(list)
for s in skus: byb[allocate.store_for(s)["bucket"]].append(s)
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
def head(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=dict(UA,Range="bytes=0-32")),timeout=40) as r:
            return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception: return "ERR"
N=150; random.seed(23)
print(f"{'bucket':<20}{'hosted':>10}  {'rate':>7}  95% CI            panels      listings (x4)")
tot_l=0
for b in BY:
    s=BY[b]; samp=random.sample(byb[b],N)
    urls=[f"{s['pic_base']}/{s['key_prefix']}/listing/{k}-0-black.jpg" for k in samp]
    with ThreadPoolExecutor(max_workers=10) as ex: res=list(ex.map(head,urls))
    ok=sum(1 for c in res if c in (200,206)); err=[c for c in res if c not in (200,206,404)]
    p=ok/N; se=math.sqrt(p*(1-p)/N); lo,hi=max(0,p-1.96*se),min(1,p+1.96*se)
    est=int(p*len(byb[b])); tot_l+=est*4
    print(f"{b:<20}{ok:>6}/{N}  {p*100:6.1f}%  [{lo*100:5.1f}%,{hi*100:5.1f}%]  {est:>9,}  {est*4:>12,}"
          + (f"   non-404 errors: {collections.Counter(err)}" if err else ""))
print(f"\nestimated total listings available to build now: {tot_l:,}")
