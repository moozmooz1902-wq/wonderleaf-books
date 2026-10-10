#!/usr/bin/env python3
"""Measure colour and composition across the competitor corpus. No model.

The GPU plan did not survive contact: RunPod's datacenter IPs are throttled by
the Shopify CDN (a pod harvested 8.3 MB in 12 minutes and then stalled, against
1.6 GB in 5 minutes from here). This container fetches at ~25 img/s, and the
colour work needs no GPU at all - it is numpy, and unlike the CLIP style labels
(50-65% accurate against titles that name their own technique) these numbers
are exact.

Resumable: shards of 1000, each written then recorded in done.txt, so it can be
killed and restarted at any point.

  python3 colour_pass.py --list big/urls.jsonl --out big/out
"""
import argparse, gzip, io, json, os, queue, threading, time, urllib.request
import sys
from PIL import Image, ImageFile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pod"))
from colour import feats

Image.MAX_IMAGE_PIXELS = 60_000_000
ImageFile.LOAD_TRUNCATED_IMAGES = True
SHARD = 1000


def small(url, src):
    sep = "&" if "?" in url else "?"
    return url + sep + ("speedsize=w_384" if src == "displate" else "width=384")


def fetcher(jobs, got):
    while True:
        job = jobs.get()
        if job is None:
            jobs.task_done(); return
        try:
            rq = urllib.request.Request(small(job["url"], job.get("src", "")),
                                        headers={"Accept": "image/*"})
            with urllib.request.urlopen(rq, timeout=25) as r:
                b = r.read()
            im = Image.open(io.BytesIO(b))
            im.draft("RGB", (512, 512))
            im = im.convert("RGB")
            im.thumbnail((448, 448), Image.BILINEAR)
            m = feats(im)
            m["id"] = job.get("id", "")
            m["s"] = job.get("src", "")[:2]
            if job.get("title"):
                m["t"] = job["title"]
            got.append(m)
        except Exception:
            pass
        jobs.task_done()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=48)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    donep = os.path.join(a.out, "done.txt")
    done = {l.strip() for l in open(donep)} if os.path.exists(donep) else set()

    jobs, got = queue.Queue(maxsize=a.threads * 4), []
    for _ in range(a.threads):
        threading.Thread(target=fetcher, args=(jobs, got), daemon=True).start()

    out = gzip.open(os.path.join(a.out, "colour.jsonl.gz"), "at", encoding="utf-8")
    t0, seen = time.time(), 0
    buf, sid = [], 0
    with open(a.list, encoding="utf-8") as f:
        for line in f:
            buf.append(line)
            if len(buf) < SHARD:
                continue
            cur, lines, buf = sid, buf, []
            sid += 1
            if str(cur) in done:
                continue
            got.clear()
            for l in lines:
                try:
                    jobs.put(json.loads(l))
                except Exception:
                    pass
            jobs.join()
            for m in got:
                out.write(json.dumps(m, ensure_ascii=False) + "\n")
            out.flush()
            with open(donep, "a") as df:
                df.write(f"{cur}\n")
            seen += len(got)
            el = time.time() - t0
            print(f"shard {cur}  +{len(got)}  total {seen:,}  "
                  f"{seen/max(el,1):.1f} img/s  {el/60:.1f} min", flush=True)
    print(f"DONE {seen:,} images in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
