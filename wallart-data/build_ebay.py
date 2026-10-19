#!/usr/bin/env python3
"""Build eBay File Exchange upload files for the wall-art catalogue.

WHAT A ROW IS. One generated panel becomes four listings, one per
colourway, exactly as pipeline.py composes them. Each listing is a
MULTI-VARIATION fixed-price listing whose variation axis is the frame
colour - black, white, oak - with the BLACK mockup as the listing's main
image, which is the seller's instruction and also what eBay shows in
search. So each listing is four CSV rows: one parent and three variations.

THE VARIATION FORMAT is the part worth being careful about, because File
Exchange rejects the whole file rather than the bad row:

  parent row     *Action=Add, the title, the description, every picture,
                 and RelationshipDetails listing ALL the values -
                 "Frame Colour=Black;White;Oak"
  variation rows Action and ItemID EMPTY, Relationship=Variation,
                 RelationshipDetails="Frame Colour=Black", the price, the
                 quantity and that frame's own picture

The parent's value list and the children's values must match character for
character - no space after the semicolon, none around the equals sign.
This layout is from eBay seller-community threads rather than the official
manual, which is why build_ebay.py writes a THREE-DESIGN test file as well
as the full set: upload the test file first, confirm eBay accepts it, and
only then upload the rest. Getting this wrong on 3.8M rows is a bad way to
find out.

WHAT THIS DOES NOT DO. It does not upload anything, and it does not create
the mockups - it writes the URLs they will have. render_listings.py makes
the images. A CSV whose pictures are not in R2 yet will upload rows whose
images 404, so the images go first.

  usage: build_ebay.py --test 3            three designs, one file
         build_ebay.py --limit 50          a 50-design sample
         build_ebay.py                     everything, split per store
"""
import argparse, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import allocate, listing_text as LT

# ---- the things the seller sets. One edit changes every row. ------------
PRICE     = "24.99"      # <-- ASSUMPTION. Not given. A3 framed print.
QUANTITY  = "1"          # the seller's standing rule
LOCATION  = "United Kingdom"
CATEGORY  = "360"        # eBay UK wall art, per CLAUDE.md
CONDITION = "1000"       # New
POLICY    = "1"          # shipping / returns / payment profile names
FORMAT    = "FixedPrice" # variations are fixed-price only
DURATION  = "GTC"
SIZE      = "A3 (29.7 x 42 cm)"
FRAMES    = ["Black", "White", "Oak"]      # Black FIRST = the main image
VAR_NAME  = "Frame Colour"
COLOURWAYS = 4
# ------------------------------------------------------------------------

HEADER = ["*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193)",
          "CustomLabel", "*Category", "*Title", "*Description", "*ConditionID",
          "PicURL", "*Quantity", "*StartPrice", "*Format", "*Duration",
          "*Location", "ShippingProfileName", "ReturnProfileName",
          "PaymentProfileName", "Relationship", "RelationshipDetails",
          "C:Brand", "C:Type", "C:Subject", "C:Style", "C:Colour",
          "C:Material", "C:Frame Colour", "C:Orientation", "C:Features",
          "C:Originality", "C:Date of Creation", "C:Size"]

STORES = {s["bucket"]: s for s in json.load(open(os.path.join(HERE, "stores.json")))["stores"]}


def pic(store, sku, frame):
    """Where render_listings.py will put this mockup."""
    return (f'{store["pic_base"]}/{store["key_prefix"].strip("/")}/'
            f'listing/{sku}-{frame.lower()}.jpg')


def rows_for(job, store):
    """Four listings for one panel; four CSV rows each."""
    out = []
    for ci in range(COLOURWAYS):
        sku = f'{job["sku"]}-{ci}'
        j = {**job, "sku": sku}
        title = LT.title(j)
        desc = LT.description(j, title)
        bad = LT.check(title, desc)
        if bad:
            raise SystemExit(f"REFUSING {sku}: {bad}")
        pics = [pic(store, sku, f) for f in FRAMES]
        allvals = ";".join(FRAMES)
        out.append(["Add", sku, CATEGORY, title, desc, CONDITION,
                    "|".join(pics), "", "", FORMAT, DURATION, LOCATION,
                    POLICY, POLICY, POLICY, "", f"{VAR_NAME}={allvals}",
                    "Unbranded", "Print", LT._sub(job["subject"]),
                    LT.GRAM.get(job["gram"], "Contemporary"),
                    LT.PAL.get(job["pal"], ""), "Paper", "",
                    "Portrait", "Framed", "Reproduction", "2020-Now", SIZE])
        for f, p in zip(FRAMES, pics):
            out.append(["", f"{sku}-{f.lower()}", "", "", "", "", p,
                        QUANTITY, PRICE, "", "", "", "", "", "",
                        "Variation", f"{VAR_NAME}={f}",
                        "", "", "", "", "", "", f, "", "", "", "", ""])
    return out


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(HEADER)
        w.writerows(rows)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(HERE, "pool_jobs.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "ebay"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--test", type=int, default=0)
    # eBay File Exchange caps an upload at about 15 MB uncompressed, and a
    # parent row carries a kilobyte of description HTML, so the split has to
    # be by BYTES, not rows: 20,000 rows is 2 MB of children or 25 MB of
    # parents depending on where the chunk falls. Measured on 20,000 designs:
    # 170 MB for 320,000 rows, about 531 bytes a row on average.
    ap.add_argument("--max-bytes", type=int, default=9_000_000)
    ap.add_argument("--rows-per-file", type=int, default=0)
    a = ap.parse_args()
    jobs = json.load(open(a.jobs))
    os.makedirs(a.out, exist_ok=True)

    if a.test:
        rows = []
        for j in jobs[:a.test]:
            rows += rows_for(j, STORES[allocate.store_for(j["sku"])["bucket"]])
        p = write(os.path.join(a.out, f"EBAY_WALLART_TEST_{a.test}.csv"), rows)
        print(f"{p}  {len(rows):,} rows  "
              f"({a.test} designs x {COLOURWAYS} colourways x "
              f"{1+len(FRAMES)} rows)")
        return

    if a.limit:
        jobs = jobs[:a.limit]
    per, counts = {}, {}
    files = []
    for j in jobs:
        b = allocate.store_for(j["sku"])["bucket"]
        per.setdefault(b, []).extend(rows_for(j, STORES[b]))
        counts[b] = counts.get(b, 0) + COLOURWAYS
        if (a.rows_per_file and len(per[b]) >= a.rows_per_file) or \
           (not a.rows_per_file and
                sum(len(x) for r in per[b] for x in r) >= a.max_bytes):
            n = len([f for f in files if f[0] == b]) + 1
            files.append((b, write(os.path.join(
                a.out, f"EBAY_{b}_{n:04d}.csv"), per[b]), len(per[b])))
            per[b] = []
    for b, rows in per.items():
        if rows:
            n = len([f for f in files if f[0] == b]) + 1
            files.append((b, write(os.path.join(
                a.out, f"EBAY_{b}_{n:04d}.csv"), rows), len(rows)))
    print(f"{'bucket':<20}{'files':>7}{'rows':>14}{'listings':>12}")
    for b in sorted(counts):
        fs = [f for f in files if f[0] == b]
        print(f"{b:<20}{len(fs):>7}{sum(f[2] for f in fs):>14,}{counts[b]:>12,}")
    print(f"{'TOTAL':<20}{len(files):>7}{sum(f[2] for f in files):>14,}"
          f"{sum(counts.values()):>12,}")


if __name__ == "__main__":
    main()
