import os, re, sys, json, subprocess
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
D    = os.path.join(BASE, "displate")
OUT  = os.path.join(D, "displate.jsonl")
DONE = os.path.join(D, "done.txt")

# Displate's sitemap host 403s urllib but answers curl, and displate.com/sitemap.xml
# is a 301 to sitemaps.displate.com - so everything goes through curl -L.
def get(url):
    r = subprocess.run(["curl", "-sSL", "--max-time", "120", url],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""

def indexes():
    urls = []
    for name in ("sitemap-non-licensed-products-index.xml",
                 "sitemap-licensed-products-index.xml"):
        lic = "licensed" if name.startswith("sitemap-licensed") else "non-licensed"
        xml = open(os.path.join(D, ("lic" if lic == "licensed" else "nonlic") + "-index.xml")).read()
        for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
            urls.append((loc, lic))
    return urls

done = set()
if os.path.exists(DONE):
    done = set(l.strip() for l in open(DONE) if l.strip())

todo = [(u, l) for u, l in indexes() if u not in done]
print(f"{len(done)} sitemaps already done, {len(todo)} to go", flush=True)

# one record per <url> block: product page, image URL, the artwork date folder
URLBLOCK = re.compile(r"<url>(.*?)</url>", re.S)
def parse(xml, lic):
    rows = []
    for blk in URLBLOCK.findall(xml):
        loc = re.search(r"<loc>([^<]+)</loc>", blk)
        img = re.search(r"<image:loc>([^<]+)</image:loc>", blk)
        if not loc:
            continue
        iu = img.group(1) if img else ""
        m = re.search(r"/artwork/(\d{4}-\d{2}-\d{2})/", iu)
        rows.append({
            "src": "displate",
            "lic": lic,                                   # licensed IP vs artist original
            "url": loc.group(1),
            "id": loc.group(1).rsplit("/", 1)[-1],
            "img": iu.split("?")[0],                      # drop the speedsize param
            "date": m.group(1) if m else "",
            # no title: Displate's sitemaps carry none, unlike Fy!'s
        })
    return rows

out  = open(OUT, "a", encoding="utf-8")
dlog = open(DONE, "a")
total = 0

def work(job):
    u, lic = job
    xml = get(u)
    if not xml or "<url>" not in xml:
        return u, None
    return u, parse(xml, lic)

with ThreadPoolExecutor(max_workers=6) as ex:
    for i, (u, rows) in enumerate(ex.map(work, todo), 1):
        if rows is None:
            print(f"  FAILED {u}", flush=True)
            continue
        for r in rows:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
        total += len(rows)
        out.flush()
        # record every sitemap as it lands, so a kill at any point resumes here
        dlog.write(u + "\n"); dlog.flush()
        if i % 20 == 0:
            print(f"  {i}/{len(todo)} sitemaps, {total} images", flush=True)

print(f"done: {total} new images -> {OUT}", flush=True)
