#!/usr/bin/env python3
"""Contact sheets of the chosen range, for a human to approve.

WHY THIS IS NEEDED. About 17% of all generated panels carry a small distant
human figure - the for-scale kind, a walker on a clifftop, not a portrait.
That breaks the seller's own no-human-figures rule, and `select.py` can only
hold back the compositions where one is LIKELIEST (street scenes, wide
views). That is a proxy. It is not a detector and it does not pretend to be.

The real detector is render/people_sweep.py, which needs a GPU pod and
therefore money the seller controls. Until that has been run, the cheap and
completely reliable check is a person looking at the pictures - and at 1,000
designs that is about twenty minutes with these sheets, not a day.

    python3 sheet.py                 # all of selection.json
    python3 sheet.py --sample 96     # a sample, to measure the rate first

Each tile is numbered. Note the numbers of anything with a person in it (or
anything else you would not sell) and pass them to --drop:

    python3 sheet.py --drop 14,207,588
    # rewrites selection.json without them, then re-run build_db.py

Images are fetched from the public r2.dev hosts at a deliberately gentle
rate: a measured run saw Cloudflare error 1015 on 7,142 of 12,834 requests
at about 70 req/s, while 600 objects at 48 concurrent and 19 req/s passed
599 of 600. There is no hurry here.
"""
import argparse, concurrent.futures as cf, io, json, os, sys, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WALLART = os.environ.get(
    "WALLART_DIR", "/home/user/wonderleaf-books/wallart-data")
CACHE = os.environ.get(
    "SHEET_CACHE",
    "/tmp/claude-0/-home-user-wonderleaf-books/"
    "af9e3fdd-8129-53fc-a69c-916ae3713d2b/scratchpad/sheet_cache")
sys.path.insert(0, HERE)

STORES = {s["bucket"]: s for s in json.load(
    open(os.path.join(WALLART, "stores.json")))["stores"]}


def url_for(d, colour="black", ci=0):
    st = STORES[d["bucket"]]
    return (f'{st["pic_base"].rstrip("/")}/{st["key_prefix"].strip("/")}/'
            f'listing/{d["sku"]}-{ci}-{colour}.jpg')


def fetch(args):
    i, d = args
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f'{d["sku"]}.jpg')
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        return i, path
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                url_for(d), headers={"User-Agent": "sheet.py/1.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                body = r.read()
            if len(body) < 2000:
                raise OSError("too small")
            open(path, "wb").write(body)
            return i, path
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return i, None


def build_sheets(designs, out_dir, per_row=4, rows=3, tile=500, workers=10):
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    got = {}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, path in ex.map(fetch, list(enumerate(designs))):
            if path:
                got[i] = path
    print(f"fetched {len(got)}/{len(designs)}")

    per = per_row * rows
    label_h = 30
    sheets = []
    for s in range(0, len(designs), per):
        chunk = [(i, designs[i]) for i in range(s, min(s + per,
                                                       len(designs)))]
        W = per_row * tile
        H = rows * (tile + label_h)
        sheet = Image.new("RGB", (W, H), (237, 234, 227))
        dr = ImageDraw.Draw(sheet)
        for n, (i, d) in enumerate(chunk):
            cx = (n % per_row) * tile
            cy = (n // per_row) * (tile + label_h)
            p = got.get(i)
            if p:
                try:
                    im = Image.open(p).convert("RGB")
                    im.thumbnail((tile - 8, tile - 8), Image.LANCZOS)
                    sheet.paste(im, (cx + (tile - im.width) // 2,
                                     cy + (tile - im.height) // 2))
                except Exception:
                    dr.text((cx + 10, cy + 10), "unreadable", fill=(180, 0, 0))
            else:
                dr.text((cx + 10, cy + 10), "missing", fill=(180, 0, 0))
            dr.text((cx + 8, cy + tile + 6),
                    f'#{i}  {d["subject"][:34]}  [{d["tech"]}]',
                    fill=(40, 38, 34))
        path = os.path.join(out_dir, f"sheet_{len(sheets)+1:02d}.png")
        sheet.save(path, optimize=True)
        sheets.append(path)
    return sheets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sel", default=os.path.join(HERE, "selection.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "sheets"))
    ap.add_argument("--sample", type=int, default=0,
                    help="review a random sample instead of everything")
    ap.add_argument("--per-row", type=int, default=4)
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--tile", type=int, default=500)
    ap.add_argument("--drop", default="",
                    help="comma-separated tile numbers to remove from the "
                         "selection")
    a = ap.parse_args()

    sel = json.load(open(a.sel))
    designs = sel["designs"]

    if a.drop:
        drop = {int(x) for x in a.drop.split(",") if x.strip()}
        kept = [d for i, d in enumerate(designs) if i not in drop]
        removed = [designs[i] for i in sorted(drop) if i < len(designs)]
        sel["designs"] = kept
        sel["generated"] = len(kept)
        sel.setdefault("dropped_by_eye", [])
        sel["dropped_by_eye"] += [
            {"sku": d["sku"], "subject": d["subject"], "gram": d["gram"]}
            for d in removed]
        json.dump(sel, open(a.sel, "w"), indent=1)
        print(f"dropped {len(removed)} design(s); {len(kept)} remain")
        for d in removed:
            print(f'  - {d["subject"]} [{d["tech"]}/{d["gram"]}]')
        print("\nNow re-run:  python3 build_db.py && python3 preflight.py")
        return 0

    if a.sample:
        import random
        random.seed(11)
        idx = sorted(random.sample(range(len(designs)),
                                   min(a.sample, len(designs))))
        designs = [dict(designs[i], _orig=i) for i in idx]
        print(f"sampling {len(designs)} of {len(sel['designs'])}")

    sheets = build_sheets(designs, a.out, a.per_row, a.rows, a.tile)
    print(f"\n{len(sheets)} sheet(s) in {a.out}")
    for s in sheets:
        print("  ", s)
    print("\nLook for: people, animal eyes that are wrong, anything that "
          "looks like a signature, anything you would not put your name to.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
