#!/usr/bin/env python3
"""Build the image manifest from Fy! and Displate sitemaps.

Resumable by design: every sitemap already processed is recorded, so the job
can be killed at any point - including because the RunPod balance ran out -
and restarted without redoing work or losing anything.

Writes one JSONL line per image: {src, url, title, sitemap}.
"""
import gzip, json, os, re, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "manifest.jsonl")
DONE = os.path.join(BASE, "done_sitemaps.txt")
LOC = re.compile(r"<loc>([^<]+)</loc>")
IMG = re.compile(r"<image:loc>([^<]+)</image:loc>")
URLBLOCK = re.compile(r"<url>(.*?)</url>", re.S)
TITLE = re.compile(r"<image:title>(.*?)</image:title>", re.S)

def fetch(u, timeout=120):
    req = urllib.request.Request(u, headers={"Accept": "application/xml,text/xml,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = r.read()
    if d[:2] == b"\x1f\x8b":
        d = gzip.decompress(d)
    return d.decode("utf-8", "replace")

def unesc(s):
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&apos;", "'")):
        s = s.replace(a, b)
    return s.strip()

def sitemaps():
    out = []
    try:
        idx = fetch("https://www.iamfy.co/sitemap.xml")
        for u in LOC.findall(idx):
            u = unesc(u)
            if "sitemap_products" in u:
                out.append(("fy", u))
    except Exception as e:
        print("fy index failed:", e, flush=True)
    try:
        idx = fetch("https://displate.com/sitemap.xml")
        for u in LOC.findall(idx):
            out.append(("displate", unesc(u)))
    except Exception as e:
        print("displate index failed:", e, flush=True)
    return out

def parse(src, u):
    rows = []
    x = fetch(u)
    for block in URLBLOCK.findall(x):
        img = IMG.search(block)
        if not img:
            continue
        t = TITLE.search(block)
        rows.append({"src": src, "url": unesc(img.group(1)),
                     "title": unesc(t.group(1)) if t else "",
                     "sm": u.rsplit("/", 1)[-1][:60]})
    return rows

def main():
    done = set()
    if os.path.exists(DONE):
        done = set(open(DONE).read().split("\n"))
    sms = [(s, u) for s, u in sitemaps() if u not in done]
    print(f"sitemaps to do: {len(sms):,}  (already done {len(done):,})", flush=True)
    if not sms:
        return
    n = 0
    t0 = time.time()
    with open(OUT, "a", encoding="utf-8") as out, open(DONE, "a") as dn, \
         ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(parse, s, u): (s, u) for s, u in sms}
        for i, f in enumerate(as_completed(futs), 1):
            s, u = futs[f]
            try:
                rows = f.result()
            except Exception as e:
                print(f"  fail {u[-50:]}: {type(e).__name__}", flush=True)
                continue
            for r in rows:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += len(rows)
            dn.write(u + "\n")
            if i % 100 == 0:
                out.flush(); dn.flush()
                el = time.time() - t0
                print(f"  {i:,}/{len(sms):,} sitemaps · {n:,} images · "
                      f"{n/max(el,1):,.0f} img/s · {el/60:.1f} min", flush=True)
    print(f"\nadded {n:,} images -> {OUT}")

if __name__ == "__main__":
    main()
