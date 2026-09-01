#!/usr/bin/env python3
"""
Harvest open-access museum catalogues into a listable set of artworks.

    python3 harvest_art.py --out art_raw.jsonl

The Art Institute of Chicago publishes its whole collection through a bulk
API, 100 records a page, everything CC0 except the description field. That
is 1,300 requests for the lot rather than one request per object, which is
why it is the first source rather than the Met.

Nothing here generates anything. These are real artworks, out of copyright,
that people already search for by name - which is the whole point. The
research found canvasartshop selling exactly this: Hokusai, Waterhouse, Van
Gogh, Turner, Lowry, Morris, Goya, Mucha.
"""

import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request

AIC = "https://api.artic.edu/api/v1/artworks"
FIELDS = ("id,title,artist_title,artist_display,date_display,date_end,"
          "is_public_domain,image_id,artwork_type_title,classification_title,"
          "medium_display,style_title,place_of_origin,term_titles,"
          "subject_titles,colorfulness")
UA = "wonderleaf-catalogue/1.0 (print-on-demand research)"


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            # 403/429 mean we are going too fast for a free public API.
            # Back off rather than hammer it.
            time.sleep(2 ** i)
        except Exception:
            time.sleep(2 ** i)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="art_raw.jsonl")
    ap.add_argument("--limit-pages", type=int)
    ap.add_argument("--sleep", type=float, default=0.15,
                    help="pause between requests. This is a free public API "
                         "with no key; do not take the whole thing at once")
    a = ap.parse_args()

    # Resume: the harvest takes minutes and a dropped connection should not
    # mean starting again.
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass
        print(f"  resuming, {len(done):,} already held")

    page, kept, seen = 1, len(done), 0
    fh = open(a.out, "a", encoding="utf-8")
    while True:
        url = f"{AIC}?page={page}&limit=100&fields={urllib.parse.quote(FIELDS)}"
        d = get(url)
        if not d or not d.get("data"):
            break
        for r in d["data"]:
            seen += 1
            if not r.get("is_public_domain") or not r.get("image_id"):
                continue
            if r["id"] in done:
                continue
            done.add(r["id"])
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            kept += 1
        fh.flush()
        total_pages = d["pagination"]["total_pages"]
        if page % 25 == 0 or page == 1:
            print(f"  page {page:,}/{total_pages:,}  seen {seen:,}  "
                  f"public domain with an image {kept:,}", flush=True)
        page += 1
        if a.limit_pages and page > a.limit_pages:
            break
        if page > total_pages:
            break
        time.sleep(a.sleep)
    fh.close()
    print(f"\n  {kept:,} usable artworks -> {a.out}")


if __name__ == "__main__":
    main()
