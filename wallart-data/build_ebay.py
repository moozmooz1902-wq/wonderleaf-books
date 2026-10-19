#!/usr/bin/env python3
"""eBay File Exchange upload files for the image-based wall-art catalogue.

THE FORMAT IS COPIED, NOT INVENTED. The seller's warning was that one wrong
thing in a file can ruin the lot, so every structural choice here comes from
files that eBay has already accepted on these accounts:

  * `tshirt/WALLART_REPRICE.csv` is built from their ACTIVE LISTINGS export.
    It shows the live shape: category "Art Prints (360)", a parent row whose
    Relationship details read `Color=Black;Unframed Print Only|Size=A3
    (29.7x42 cm)`, then one Variation row per value carrying only the price.
    So the variation axis on these accounts is **Color**, with the framing
    option as its value, and **Size** is an axis even when it has one value.
  * `wallart/build_ebay.py` on claude/hopeful-rubin-u14pgu is the builder for
    the 2.3M typography catalogue. The column list below is its header, in
    its order, including `CC=UTF-8` in the Action field; the parent/child
    split is its split - a child row leaves Action AND CustomLabel empty and
    carries Relationship, its own details, price, quantity and its own
    aspects, nothing else.
  * `wallart/plan.json` supplies condition 1000, dispatch 3 days, quantity 1,
    business policies all named "1", and the 500,000-row cap per file.

WHAT IS NEW HERE, and it is only this: the variation values are the three
FRAME COLOURS - Black, White, Oak - and the listing carries one picture per
colour with BLACK FIRST, because eBay shows the first picture in search and
the seller asked for black to be the main image.

NO LISTING WITHOUT A PICTURE. --rendered points at the hash files the
render stage wrote to `wallart/hashes/`, which hold one line per panel
whose twelve pictures were made. That is the right authority and it is
also the small one: listing eleven and a half million picture keys to
answer "is this panel done" means eleven thousand LIST calls and half a
gigabyte of text, while the hashes are 960,000 lines and already have to
be fetched for the duplicate audit. A row whose PicURL 404s is a listing
eBay rejects or shows blank, and finding that out across millions of rows
is not recoverable by hand.

--store builds one bucket. luxvia-art is 40% of the catalogue and finishes
rendering well before the others, so its folder can go to that account
while the rest are still being made.

ONE DESIGN GOES TO ONE STORE. allocate.store_for decides, the same hash the
generation run used, so a design cannot appear in two accounts - the seller's
"don't mix data". Files are written per bucket into their own folder so a
folder can be handed to one account and nothing else.

  usage: build_ebay.py --test 3
         build_ebay.py --limit 1000
         build_ebay.py --require-pictures keys.txt
         build_ebay.py --check out/ebay
"""
import argparse, csv, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import re
import allocate, listing_text as LT

# ONLY THIS RUN'S WORK GETS A LISTING. The buckets are not empty and never
# were: alongside <store>/gen/ they hold the seller's EXISTING catalogue -
# luxvia/abstract/, luxvia/birds/, luxvia/boho/, luxvia/botanical/,
# luxvia/cats/, luxvia/celestial/, and loose sequential files like
# store1/0000000_framed.jpg and store2/0000000_raw.jpg. Those are already
# listed on eBay. Putting them in an upload file would list them a second
# time.
#
# The separation is structural rather than a filter, which is why it holds:
# this builder is driven by the rebuilt job GRID, not by listing a bucket.
# Every SKU it can emit is "WA-" plus sixteen hex characters of blake2b over
# the job, plus the colourway index, and every picture it can reference is
# <prefix>/gen/listing/<that SKU>-<colour>.jpg, written by this run's render
# stage. Nothing else in the bucket has that shape, so no old file can be
# reached even in principle.
#
# These two patterns assert it anyway, on every row written and again in
# --check, because "it cannot happen" is how it happens.
SKU_RE = re.compile(r"^WA-[0-9a-f]{16}-[0-3]$")
PIC_RE = re.compile(r"^https://[^/]+/[^/]+/gen/listing/WA-[0-9a-f]{16}-[0-3]-"
                    r"(black|white|oak)\.jpg$")

EB = json.load(open(os.path.join(HERE, "ebay_plan.json")))
STORES = {s["bucket"]: s for s in
          json.load(open(os.path.join(HERE, "stores.json")))["stores"]}

ACTION = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193|CC=UTF-8)"
HEADER = [ACTION, "CustomLabel", "*Category", "StoreCategory", "*Title",
          "Subtitle", "Relationship", "RelationshipDetails", "*ConditionID",
          "*Description", "PicURL", "*Format", "*Duration", "*StartPrice",
          "*Quantity", "*Location", "PostalCode", "DispatchTimeMax",
          "ShippingProfileName", "ReturnProfileName", "PaymentProfileName",
          "C:Brand", "C:Artist", "C:Type", "C:Size", "C:Frame", "C:Framing",
          "C:Subject", "C:Style", "C:Theme", "C:Room", "C:Colour",
          "C:Material", "C:Production Technique", "C:Orientation",
          "C:Features", "C:Unit Type"]

ROWS_PER_LISTING = 1 + len(EB["colours"])
LISTINGS_PER_FILE = (EB["max_rows_per_file"] - 1) // ROWS_PER_LISTING

# eBay wants a Theme a buyer would browse, not our grammar codes.
THEME = {"botanical": "Flowers & Plants", "creature": "Animals",
         "place": "Landscapes", "celestial": "Astronomy & Space",
         "stilllife": "Still Life", "architecture": "Architecture"}
ROOM = {"botanical": "Living Room", "creature": "Bedroom",
        "place": "Living Room", "celestial": "Bedroom",
        "stilllife": "Kitchen", "architecture": "Study"}


def key_for(store, sku, colour):
    return (f'{store["key_prefix"].strip("/")}/listing/'
            f'{sku}-{colour.lower()}.jpg')


def pic(store, sku, colour):
    """The Cloudflare public URL, which is what eBay fetches."""
    return f'{store["pic_base"].rstrip("/")}/{key_for(store, sku, colour)}'


def rows_for(job, store):
    """Four listings for one panel - one per colourway - each a parent plus
    one Variation row per frame colour."""
    out = []
    size = EB["size"]
    vals = ";".join(EB["colours"])
    for ci in range(EB["colourways"]):
        sku = f'{job["sku"]}-{ci}'
        j = {**job, "sku": sku}
        title = LT.title(j)
        desc = LT.description(j, title)
        bad = LT.check(title, desc)
        if bad:
            return None, bad
        pics = [pic(store, sku, c) for c in EB["colours"]]
        if not SKU_RE.match(sku) or not all(PIC_RE.match(u) for u in pics):
            return None, [f"not this run's work: {sku}"]
        p = dict.fromkeys(HEADER, "")
        p.update({
            ACTION: "Add", "CustomLabel": sku, "*Category": EB["category"],
            "*Title": title,
            "RelationshipDetails": f"Color={vals}|Size={size}",
            "*ConditionID": EB["condition_id"], "*Description": desc,
            "PicURL": "|".join(pics),            # black first = main image
            "*Format": "FixedPrice", "*Duration": "GTC",
            "*Location": EB["location"],
            "DispatchTimeMax": str(EB["dispatch_days"]),
            "ShippingProfileName": EB["profiles"]["shipping"],
            "ReturnProfileName": EB["profiles"]["returns"],
            "PaymentProfileName": EB["profiles"]["payment"],
            "C:Brand": EB["brand"], "C:Artist": store["name"],
            "C:Type": "Print",
            "C:Subject": LT._sub(job["subject"]),
            "C:Style": LT.GRAM.get(job["gram"], "Contemporary"),
            "C:Theme": THEME.get(job["kind"], "Abstract"),
            "C:Room": ROOM.get(job["kind"], "Living Room"),
            "C:Material": "Paper",
            "C:Production Technique": "Digital Print",
            "C:Orientation": "Portrait",
            "C:Features": "Framed", "C:Unit Type": "Unit",
        })
        out.append(p)
        for c in EB["colours"]:
            k = dict.fromkeys(HEADER, "")
            k.update({"Relationship": "Variation",
                      "RelationshipDetails": f"Color={c}|Size={size}",
                      "*StartPrice": f'{EB["price"]:.2f}',
                      "*Quantity": str(EB["quantity"]),
                      "PicURL": pic(store, sku, c),
                      "C:Size": size, "C:Frame": c, "C:Framing": "Framed",
                      "C:Colour": c})
            out.append(k)
    return out, None


def build(jobs, out_root, have=None, limit=0, drop=frozenset()):
    os.makedirs(out_root, exist_ok=True)
    buf, files, stats = {}, {}, {}
    def flush(b, final=False):
        rows = buf.get(b) or []
        if not rows:
            return
        d = os.path.join(out_root, b)
        os.makedirs(d, exist_ok=True)
        files[b] = files.get(b, 0) + 1
        path = os.path.join(d, f"{b}_{files[b]:04d}.csv")
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=HEADER, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        buf[b] = []

    n = 0
    for job in jobs:
        b = allocate.store_for(job["sku"])["bucket"]
        st = STORES[b]
        s = stats.setdefault(b, dict(listings=0, blocked=0, nopic=0, dup=0))
        if (b, job["sku"]) in drop:
            s["dup"] += 1
            continue
        if have is not None:
            if (b, job["sku"]) not in have:
                s["nopic"] += 1
                continue
        rows, bad = rows_for(job, st)
        if bad:
            s["blocked"] += 1
            continue
        buf.setdefault(b, []).extend(rows)
        s["listings"] += EB["colourways"]
        if len(buf[b]) >= LISTINGS_PER_FILE * ROWS_PER_LISTING:
            flush(b)
        n += 1
        if limit and n >= limit:
            break
    for b in list(buf):
        flush(b, True)

    print(f"{'bucket':<20}{'listings':>12}{'rows':>14}{'files':>7}"
          f"{'blocked':>9}{'no picture':>12}{'duplicate':>11}")
    for b in sorted(stats):
        s = stats[b]
        print(f"{b:<20}{s['listings']:>12,}"
              f"{s['listings']*ROWS_PER_LISTING:>14,}{files.get(b,0):>7}"
              f"{s['blocked']:>9,}{s['nopic']:>12,}{s['dup']:>11,}")
    tot = sum(s["listings"] for s in stats.values())
    print(f"{'TOTAL':<20}{tot:>12,}{tot*ROWS_PER_LISTING:>14,}"
          f"{sum(files.values()):>7}")
    return files


def zip_stores(out_root):
    for b in sorted(os.listdir(out_root)):
        d = os.path.join(out_root, b)
        if not os.path.isdir(d):
            continue
        z = os.path.join(out_root, f"{b}_ebay_upload.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for f in sorted(os.listdir(d)):
                if f.endswith(".csv"):
                    zf.write(os.path.join(d, f), f"{b}/{f}")
        print(f"  {z}  {os.path.getsize(z)/1e6:.1f} MB")


def check(out_root):
    """Structure, row cap, and the two things that would mix the data:
    a SKU in more than one bucket, and a picture URL whose host is not the
    bucket's own."""
    bad = cap = cross = wrongpic = notours = rows_tot = 0
    seen = {}
    for b in sorted(os.listdir(out_root)):
        d = os.path.join(out_root, b)
        if not os.path.isdir(d):
            continue
        base = STORES[b]["pic_base"].rstrip("/")
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".csv"):
                continue
            with open(os.path.join(d, fn), encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            rows_tot += len(rows)
            if len(rows) + 1 > EB["max_rows_per_file"]:
                cap += 1
            i = 0
            while i < len(rows):
                p = rows[i]
                kids = rows[i + 1:i + 1 + len(EB["colours"])]
                if (p[ACTION] != "Add" or not p["CustomLabel"]
                        or not p["PicURL"] or len(p["*Title"]) > 80
                        or len(kids) != len(EB["colours"])
                        or any(k[ACTION] or k["CustomLabel"]
                               or k["Relationship"] != "Variation"
                               or not k["*StartPrice"] for k in kids)):
                    bad += 1
                if not p["PicURL"].startswith(base):
                    wrongpic += 1
                if not SKU_RE.match(p["CustomLabel"]) or \
                        not all(PIC_RE.match(u) for u in p["PicURL"].split("|")):
                    notours += 1
                if seen.setdefault(p["CustomLabel"], b) != b:
                    cross += 1
                i += 1 + len(kids)
    print(f"rows {rows_tot:,}   structure problems {bad}   "
          f"files over {EB['max_rows_per_file']:,} rows: {cap}")
    print(f"SKUs appearing in more than one bucket: {cross}")
    print(f"pictures pointing at another bucket's host: {wrongpic}")
    print(f"rows that are NOT this run's generated work: {notours}")
    return bad + cap + cross + wrongpic + notours


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=os.path.join(HERE, "pool_jobs.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "ebay"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--test", type=int, default=0)
    ap.add_argument("--rendered", metavar="DIR",
                    help="folder of wallart/hashes/*.jsonl - the panels whose "
                         "pictures exist")
    ap.add_argument("--store", help="build one bucket only")
    ap.add_argument("--check", metavar="DIR")
    ap.add_argument("--drop", metavar="FILE",
                    help="SKUs to leave out, '<bucket>\\t<sku>' per line, "
                         "as dup_audit.py --drop writes them")
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()
    if a.check:
        sys.exit(1 if check(a.check) else 0)
    jobs = json.load(open(a.jobs))
    have = None
    if a.rendered:
        have = set()
        for fn in sorted(os.listdir(a.rendered)):
            if not fn.endswith(".jsonl"):
                continue
            for line in open(os.path.join(a.rendered, fn)):
                line = line.strip()
                if line:
                    r = json.loads(line)
                    have.add((r["bucket"], r["sku"]))
        print(f"panels with pictures rendered: {len(have):,}")
    drop = set()
    if a.drop:
        for line in open(a.drop):
            parts = line.strip().split("\t")
            if len(parts) == 2:
                drop.add((parts[0], parts[1]))
        print(f"near-duplicates to leave out: {len(drop):,}")
    if a.test:
        jobs = jobs[:a.test]
    if a.store:
        jobs = [j for j in jobs
                if allocate.store_for(j["sku"])["bucket"] == a.store]
        print(f"{a.store}: {len(jobs):,} designs")
    build(jobs, a.out, have, a.limit, drop)
    if a.zip:
        zip_stores(a.out)


if __name__ == "__main__":
    main()
