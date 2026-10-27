#!/usr/bin/env python3
"""OnBuy upload files for the image-based wall-art catalogue.

READ THIS BEFORE SUBMITTING ANYTHING. The eBay builder beside this one can
say its format is copied from files eBay has already accepted on these
accounts. THIS ONE CANNOT. There is no accepted OnBuy file to copy, because
nothing has ever been uploaded to OnBuy from here, and OnBuy's column names
live in a spreadsheet - the Product Create Template - that is handed out
from inside the seller dashboard and is not reachable from this machine.

So the work is split in two, and the split is the whole design:

  * rows.jsonl       the DATA. One JSON object per variant, with canonical
                     field names of my choosing. Every fact OnBuy asks for
                     is in here and it is independent of any column layout.
  * <bucket>_onbuy_<n>.csv
                     a RENDERING of that data, with the column names taken
                     from onbuy_plan.json["columns"].

Correct the names in onbuy_plan.json against the template's Explanation tab
and re-run; the CSV changes and nothing else does. If OnBuy's template turns
out to want a different row shape entirely, rows.jsonl still holds the data
and remapping it is a short script rather than a rebuild.

THREE THINGS CANNOT BE FILLED IN FROM HERE, and the file says so loudly
rather than guessing:

1. CATEGORY ID. OnBuy's ids come from the Category Sheet in the template or
   from GET /v2/categories with the seller's API keys. Neither is reachable.
   Every row carries NEEDS-CATEGORY-ID until onbuy_plan.json has the real
   one. A guessed id files 10,000 listings in the wrong department, which is
   worse than a rejected file.
2. BARCODES. OnBuy runs a CATALOGUE and a new product normally needs a GS1
   GTIN. 10,000 designs is 10,000 products; buying that many GTINs is not
   sensible and inventing them is worse than leaving the column empty.
   The route is the exemption OnBuy grants on a UK or EU trademark for the
   brand - which is why the brand here is Walryvo and not 'Unbranded'.
   Rows carry NEEDS-BARCODE-EXEMPTION.
3. DELIVERY WEIGHTS are estimates. See onbuy_plan.json. OnBuy prices
   delivery off them, so an estimate too low is paid for on every order.

WHAT IS DIFFERENT FROM THE EBAY FILE, deliberately:

  * FRAMED ONLY, nine variants, not twelve. The eBay listing sells an
    unframed option whose row carries no picture, so eBay shows the main
    image - the black frame - and the seller approved that for their own
    account. It does not transfer to a marketplace that shows a picture per
    variant: that would be a framed photograph on a product with no frame.
    No unframed photograph exists in this bucket and none can be made here.
    The long version is in onbuy_plan.json["_unframed_note"].
  * ONE COLOURWAY PER DESIGN. 10,000 distinct designs rather than 2,500
    designs four times over.
  * DEDUPLICATED AGAINST ITSELF on the 256-bit gradient hash of the cropped
    artwork, <= 24 bits, the same threshold as every audit before it.
    luxvia-art is the one bucket with no drop list, so this is the first
    time its near-duplicates have been measured.
  * ITS OWN DESCRIPTION. listing_text.description() names the unframed
    option, so it would be wrong here. title() is reused unchanged.

  usage: build_onbuy.py                       10,000 listings
         build_onbuy.py --limit 500 --tag first
         build_onbuy.py --check out/onbuy
"""
import argparse, csv, hashlib, json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import listing_text as LT

P = json.load(open(os.path.join(HERE, "onbuy_plan.json")))
STORES = {s["bucket"]: s for s in
          json.load(open(os.path.join(HERE, "stores.json")))["stores"]}

ROWS_PER_LISTING = 1 + len(P["frames"]) * len(P["sizes"])   # parent + 9

NO_CATEGORY = "NEEDS-CATEGORY-ID"
NO_BARCODE = "NEEDS-BARCODE-EXEMPTION"

# Same guards as build_ebay.py: a row may only ever reference this run's own
# generated work. The buckets also hold the seller's EXISTING catalogue,
# already listed elsewhere, and nothing in it has this shape.
import re
SKU_RE = re.compile(r"^WA-[0-9a-f]{16}-[0-3]$")
PIC_RE = re.compile(r"^https://[^/]+/[^/]+/gen/listing/WA-[0-9a-f]{16}-[0-3]-"
                    r"(black|white|oak)\.jpg$")

# RESTRICTED SUBJECTS, copied character for character from
# web/catalogue/select.py, where the reasoning is written out: a print
# DEPICTING a negroni is not an alcoholic drink, but marketplace screening
# is automated and reads the title, where the word sits in plain text. The
# first draft of this file had no such screen and the third listing it
# selected was titled "Ink Wash Beer Print". The downside of a wrong call is
# a restricted-product action on a brand-new OnBuy account; the upside of
# keeping a handful of drinks prints is nothing.
RESTRICTED = re.compile(
    r"\b(negroni|martini|old[- ]fashioned|whisky|whiskey|gin|rum|vodka|"
    r"tequila|mezcal|brandy|cognac|wine|champagne|prosecco|beer|ale|lager|"
    r"stout|cider|cocktail|aperol|campari|absinthe|sherry|vermouth|liqueur|"
    r"bourbon|sake|spritz|margarita|mojito|daiquiri|highball|negroni|"
    r"tobacco|cigar|cigarette|pipe smoke|vape)\b", re.I)


# A browsable theme, not our grammar codes. Same mapping the eBay builder
# uses, so one design is filed under the same theme on both marketplaces.
THEME = {"botanical": "Flowers & Plants", "creature": "Animals",
         "place": "Landscapes", "celestial": "Astronomy & Space",
         "stilllife": "Still Life", "architecture": "Architecture"}
ROOM = {"botanical": "Living Room", "creature": "Bedroom",
        "place": "Living Room", "celestial": "Bedroom",
        "stilllife": "Kitchen", "architecture": "Study"}


def pic(store, sku, colour):
    return (f'{store["pic_base"].rstrip("/")}/'
            f'{store["key_prefix"].strip("/")}/listing/'
            f'{sku}-{colour.lower()}.jpg')


def article(word):
    """'a impasto style' is wrong, and listing_text.description() writes it.
    Not fixed there, because that text is already live on eBay listings and
    changing it would revise 3.77M descriptions for a grammar nit. Fixed
    here, where the copy is new."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def describe(job, title):
    """Plain HTML, framed only, and NOT ONE CLAIM THE SHOP CANNOT STAND
    BEHIND.

    Every material statement here is copied from web/business.config.json
    and web/site/src/components/Craft.astro, which are the single source the
    website, the Merchant Center feed and the policy pages all read. That is
    deliberate: the same product must not be described one way on OnBuy and
    another way on walryvo.com. In particular, and all four learnt the hard
    way somewhere else in this repo -

      * no gsm and no 'archival': the seller stated the paper and the ink,
        not a weight or a fade rating, and an unsupported material claim is
        the cheapest misrepresentation finding there is;
      * no naming of the glazing material. The first draft of this function
        said 'shatterproof acrylic rather than glass', which nobody here
        knows to be true. The website says 'framed behind glazing', and so
        does this;
      * nothing hand-painted, original or signed, which is a legal control
        and not a quality one - see wallart-data/ip_check.py;
      * dispatch is the real 3 working days, never shortened to look
        better.

    THE COMPOSITION AND PALETTE GO IN A SPEC LIST, NOT INTO PROSE. The
    grammar codes read as English in isolation but not inside a sentence:
    'composed as In A Vase' and 'in a Impasto Style style' are both things
    an earlier version of this copy wrote across millions of listings. A
    list has no articles to get wrong.
    """
    kind = LT.KIND.get(job["kind"], "").lower()
    tech = LT.TECH.get(job["tech"], job["tech"])
    pal = LT.PAL.get(job["pal"], "")
    gram = LT.GRAM.get(job["gram"], "")
    sizes = ", ".join(f'{s["label"]} ({s["dims"]})' for s in P["sizes"])
    frames = ", ".join(P["frames"][:-1]).lower() + \
        " or " + P["frames"][-1].lower()
    spec = [("Theme", THEME.get(job["kind"], "Abstract")),
            ("Style", tech), ("Composition", gram), ("Palette", pal),
            ("Finish", "Framed, ready to hang"),
            ("Paper", "Premium satin art paper"),
            ("Inks", "Pigment inks")]
    bits = [
        f'<h2>{title}</h2>',
        f'<p>{article(kind).capitalize()} {kind} wall art print, framed '
        f'and ready to hang. Printed to order on premium satin art paper with pigment '
        f'inks. Choose the frame in {frames}, and the size in '
        f'{sizes}.</p>',
        '<h3>Details</h3>',
        '<ul>' + "".join(f'<li><b>{k}:</b> {v}</li>'
                         for k, v in spec if v) + '</ul>',
        '<h3>Made to order</h3>',
        f'<p>Each print is made after you order it, in the '
        f'{P["location"]}, which is why the choice is this wide. Dispatch '
        f'is within {P["handling_days"]} working days. It arrives framed '
        f'behind glazing with the hanging fixture already fitted.</p>',
        '<h3>Please note</h3>',
        '<p>This is a digitally created design, printed and framed to '
        'order. It is not a hand-painted original and it is not signed. '
        'The photographs show the print in each frame colour.</p>',
    ]
    return ('<div style="font-family:Arial,Helvetica,sans-serif;'
            'max-width:720px">' + "".join(bits) + '</div>')


def load_pool():
    p = os.path.join(HERE, "pool_jobs.json")
    if not os.path.exists(p):
        sys.exit("pool_jobs.json is missing. Rebuild it with grid.expand() "
                 "over gen/subjects.json - see RESUME.md.")
    return {j["sku"]: j for j in json.load(open(p))}


def load_hashes(bucket):
    """sku -> the 256-bit gradient hash, for this bucket only."""
    import numpy as np
    out = {}
    for d in sorted(os.listdir(HERE)):
        full = os.path.join(HERE, d)
        if not (d == "hashes" or d.startswith("hashes_")) \
                or not os.path.isdir(full):
            continue
        for fn in sorted(os.listdir(full)):
            if not fn.endswith(".jsonl"):
                continue
            for line in open(os.path.join(full, fn)):
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if r["bucket"] == bucket:
                    out[r["sku"]] = np.frombuffer(
                        r["h"].encode(), dtype=np.uint8) - 48
    return out


def select(pool, hashes, want, near_bits, max_per_subject):
    """Choose `want` listings: widest mix, no near-duplicates, one colourway
    per design.

    The order is a SECOND hash with its own salt, independent of the SKU
    hash that put the grid in order. Without that the four colourways of a
    design travel together and the selection clusters; build_ebay.py learnt
    the same lesson about write order.
    """
    import numpy as np
    cand = [s for s in hashes if s in pool]
    cand.sort(key=lambda s: hashlib.blake2b(
        f"onbuy|{s}".encode(), digest_size=8).digest())
    print(f"candidates: {len(cand):,} panels "
          f"(rendered and present in the job grid)")

    kept = []
    # A PREALLOCATED buffer, not a growing list rebuilt into an array on
    # every candidate. The first version called np.array(kept_bits) inside
    # the loop, which re-copies the whole set of accepted hashes once per
    # candidate: quadratic in allocation and several gigabytes of copying by
    # the time it reaches ten thousand.
    kept_bits = np.zeros((want, 32), dtype=np.uint8)
    nkept = 0
    subj = collections.Counter()
    skipped_dup = skipped_subj = skipped_text = skipped_restricted = 0
    POP = np.unpackbits(np.arange(256, dtype=np.uint8)[:, None],
                        axis=1).sum(1).astype(np.uint16)

    for s in cand:
        if len(kept) >= want:
            break
        job = pool[s]
        if RESTRICTED.search(str(job["subject"])):
            skipped_restricted += 1
            continue
        if subj[job["subject"]] >= max_per_subject:
            skipped_subj += 1
            continue
        # Near-duplicate against everything already taken. Packed bits and
        # a popcount table, so 10,000 x 10,000 is a second rather than an
        # afternoon. Brute force is fine at this size - dup_audit.py's
        # banding exists for 960,000, where it is not.
        v = np.packbits(hashes[s])
        if nkept:
            d = POP[np.bitwise_xor(kept_bits[:nkept], v)].sum(1)
            if int(d.min()) <= near_bits:
                skipped_dup += 1
                continue
        # ONE COLOURWAY PER DESIGN, picked by hash so it is spread over all
        # four and a rebuild reproduces the same choice.
        ci = int(hashlib.blake2b(f"ci|{s}".encode(),
                                 digest_size=2).hexdigest(), 16) % 4
        j = {**job, "sku": f"{s}-{ci}"}
        title = LT.title(j)
        if LT.check(title):
            skipped_text += 1
            continue
        kept.append((s, ci, title))
        kept_bits[nkept] = v
        nkept += 1
        subj[job["subject"]] += 1

    print(f"selected: {len(kept):,}   "
          f"skipped: {skipped_dup:,} near-duplicate, "
          f"{skipped_restricted:,} restricted subject, "
          f"{skipped_subj:,} over the {max_per_subject}-per-subject cap, "
          f"{skipped_text:,} title rejected")
    return kept


def rows_for(sku_ci, title, job, store):
    """One PARENT row for the design, then nine VARIANT rows: three frames
    x three sizes.

    THE PARENT/VARIANT SPLIT IS NOT COSMETIC, and it is not only about
    matching the shape OnBuy's template asks for. The first version of this
    function wrote the product name, the category, the brand and the whole
    description HTML onto all nine variant rows. Identical bytes, nine
    times, ten thousand times over: the CSV came out at 146 MB, which is not
    a file anyone opens in a spreadsheet and not a file anyone attaches to a
    support ticket. The parent carries what belongs to the PRODUCT and the
    variant rows carry only what differs - sku, the two axes, price, stock,
    handling and weight. Same information, a fifth of the bytes.

    EVERY VARIANT STILL LEADS WITH ITS OWN FRAME. The parent carries the
    three photographs with black first, because black is the main image the
    seller asked for; each variant row then carries the photograph of the
    frame IT sells. A variant showing a different frame's photograph is the
    kind of mismatch that gets an account looked at, and check() asserts it
    on every row.
    """
    desc = describe(job, title)
    pics = {c: pic(store, sku_ci, c) for c in P["frames"]}
    if not SKU_RE.match(sku_ci) or not all(PIC_RE.match(u)
                                           for u in pics.values()):
        return None, f"not this run's work: {sku_ci}"
    blank = {k: "" for k in P["columns"] if not k.startswith("_")}
    meta = {
        # Carried in rows.jsonl for the record, never written to the CSV:
        # these are what the item-specific columns get filled from once the
        # template names them.
        "_theme": THEME.get(job["kind"], "Abstract"),
        "_room": ROOM.get(job["kind"], "Living Room"),
        "_subject": LT._sub(job["subject"]),
        "_kind": job["kind"], "_tech": job["tech"],
        "_gram": job["gram"], "_pal": job["pal"],
    }
    parent = {**blank, **meta,
              "_row": "product",
              "sku": sku_ci,
              "group_sku": sku_ci,
              "product_name": title,
              "description": desc,
              "category_id": P["category_id"] or NO_CATEGORY,
              "brand": P["brand"],
              "barcode": NO_BARCODE,
              "condition": P["condition"],
              "image_1": pics[P["frames"][0]],
              "image_2": pics[P["frames"][1]],
              "image_3": pics[P["frames"][2]]}
    out = [parent]
    for c in P["frames"]:
        for s in P["sizes"]:
            out.append({**blank, **meta,
                        "_row": "variant",
                        "sku": f'{sku_ci}-{c[:1].upper()}{s["label"]}',
                        "group_sku": sku_ci,
                        "condition": P["condition"],
                        "price": f'{s["framed"]:.2f}',
                        "stock": str(P["quantity"]),
                        "handling_time": str(P["handling_days"]),
                        "delivery_weight": f'{s["weight_kg"]:.2f}',
                        "image_1": pics[c],
                        "variant_colour": c,
                        "variant_size": f'{s["label"]} ({s["dims"]})'})
    return out, None


def write(rows, out_dir, bucket, tag):
    os.makedirs(out_dir, exist_ok=True)
    cols = {k: v for k, v in P["columns"].items() if not k.startswith("_")}
    n = len(rows)

    jl = os.path.join(out_dir, f"{bucket}_onbuy_{tag}_rows.jsonl")
    with open(jl, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    written = [(jl, n)]
    # SHARD ON WHOLE LISTINGS, never on a row count. A product row and its
    # nine variants have to travel in the same file: a variant whose parent
    # is in another file is a variant OnBuy cannot attach to anything, and
    # slicing a flat list at a fixed offset splits one sooner or later.
    # build_ebay.py learnt the same thing against eBay's 500,000-row cap,
    # where checking the buffer only between whole listings is what keeps
    # the files under it.
    # Balanced, not greedy. Filling each file to the cap and letting the
    # last one take the remainder gave 4,999 + 4,999 + 2 listings - a third
    # file holding twenty rows, which looks like something went wrong.
    # Work out how many files are needed, then share the listings evenly.
    cap = P["max_rows_per_file"] - 1
    per_file = max(1, cap // ROWS_PER_LISTING)
    nlist = sum(1 for r in rows if r["_row"] == "product")
    nfiles = max(1, -(-nlist // per_file))
    each = -(-nlist // nfiles)
    shards, cur, seen = [], [], 0
    for r in rows:
        if r["_row"] == "product":
            if seen and seen % each == 0:
                shards.append(cur)
                cur = []
            seen += 1
        cur.append(r)
    if cur or not shards:
        shards.append(cur)
    for i, shard in enumerate(shards, 1):
        name = (f"{bucket}_onbuy_{tag}.csv" if len(shards) == 1
                else f"{bucket}_onbuy_{tag}_{i:02d}.csv")
        path = os.path.join(out_dir, name)
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow([cols[k] for k in cols])
            for r in shard:
                w.writerow([r[k] for k in cols])
        written.append((path, len(shard)))
    for p, k in written:
        print(f"wrote {p}  ({k:,} rows, {os.path.getsize(p)/1e6:.1f} MB)")
    return written


def report(rows):
    """What the mix actually came out as. The seller asked for a mix; this is
    the number, not the intention."""
    lis = {r["group_sku"]: r for r in rows if r["_row"] == "product"}
    nvar = sum(1 for r in rows if r["_row"] == "variant")
    print(f"\nlistings {len(lis):,}   variant rows {nvar:,}   "
          f"rows in file {len(rows):,}")
    for field, label in (("_kind", "theme"), ("_tech", "technique"),
                         ("_pal", "palette")):
        c = collections.Counter(r[field] for r in lis.values())
        top = ", ".join(f"{k} {v*100/len(lis):.0f}%"
                        for k, v in c.most_common(6))
        print(f"  {label:<10} {len(c):>3} distinct   {top}")
    subj = collections.Counter(r["_subject"] for r in lis.values())
    print(f"  {'subject':<10} {len(subj):>3} distinct   "
          f"most repeated {subj.most_common(1)[0][1]}x "
          f"({subj.most_common(1)[0][0]})")
    print(f"  colourways used: "
          f"{sorted(collections.Counter(k[-1] for k in lis).items())}")


def check(out_dir):
    """Refuse the upload while anything in it is a placeholder, and assert
    the things that would quietly break it."""
    bad = {}
    def note(k, n=1):
        bad[k] = bad.get(k, 0) + n
    files = [f for f in sorted(os.listdir(out_dir)) if f.endswith(".csv")]
    if not files:
        print("no CSV in", out_dir)
        return 1
    cols = {k: v for k, v in P["columns"].items() if not k.startswith("_")}
    inv = {v: k for k, v in cols.items()}
    for fn in files:
        path = os.path.join(out_dir, fn)
        with open(path, encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        if len(rows) + 1 > P["max_rows_per_file"]:
            note("files over the row cap")
        groups = collections.Counter()
        skus = set()
        for r in rows:
            g = {inv[k]: v for k, v in r.items() if k in inv}
            # A PARENT ROW IS THE ONE WHOSE SKU IS ITS OWN GROUP. The CSV
            # carries no _row column - that is bookkeeping, and a column
            # OnBuy did not ask for is a column that could confuse an
            # importer - so the distinction is re-derived here from the
            # data itself. That is on purpose: it means these checks read
            # the file the way OnBuy will, not the way the builder meant it.
            parent = g["sku"] == g["group_sku"]
            if not SKU_RE.match(g["group_sku"]):
                note("rows that are not this run's work")
            if g["sku"] in skus:
                note("duplicate SKUs")
            skus.add(g["sku"])
            if parent:
                if g["category_id"] == NO_CATEGORY:
                    note("products with no category id")
                if g["barcode"] == NO_BARCODE:
                    note("products with no barcode or exemption")
                if not g["product_name"] or not g["description"]:
                    note("products missing a name or description")
                if len(g["product_name"]) > LT.MAX_TITLE:
                    note("titles over the limit")
                if RESTRICTED.search(g["product_name"]):
                    note("titles naming a restricted subject")
                if g["variant_colour"] or g["variant_size"]:
                    note("product rows carrying variant axes")
                for n in ("image_1", "image_2", "image_3"):
                    if not PIC_RE.match(g[n]):
                        note("bad picture urls")
            else:
                groups[g["group_sku"]] += 1
                if not (g["variant_colour"] and g["variant_size"]):
                    note("variant rows missing an axis")
                if not PIC_RE.match(g["image_1"]):
                    note("bad picture urls")
                # the variant must lead with the frame IT sells
                if f'-{g["variant_colour"].lower()}.jpg' not in g["image_1"]:
                    note("variants whose main image is another frame")
                if not g["price"] or float(g["price"]) <= 0:
                    note("non-positive prices")
                # EVERY PRICE IN THE FILE MUST BE ONE OF THE FRAMED PRICES
                # FOR ITS SIZE. This catches two different mistakes with one
                # assertion: a file left over from before a price change
                # (the prices moved on 27 Oct and a stale CSV would still
                # read 24.99), and an unframed price leaking onto a framed
                # row. onbuy_plan.json carries unframed_when_available for
                # the day the unframed variant can be added, and until then
                # it must appear nowhere.
                want = {f'{z["framed"]:.2f}' for z in P["sizes"]
                        if g["variant_size"].startswith(z["label"])}
                if want and g["price"] not in want:
                    note("prices that are not this size's framed price")
                if g["price"] in {f'{z.get("unframed_when_available", -1):.2f}'
                                  for z in P["sizes"]}:
                    note("unframed prices on a framed-only file")
                if float(g["delivery_weight"] or 0) <= 0:
                    note("variants with no delivery weight")
        wrong = sum(1 for v in groups.values()
                    if v != len(P["frames"]) * len(P["sizes"]))
        if wrong:
            note("listings without exactly nine variants", wrong)
        orphan = set(groups) - {r[cols["sku"]] for r in rows
                                if r[cols["sku"]] == r[cols["group_sku"]]}
        if orphan:
            # A variant whose parent is in ANOTHER file is a variant OnBuy
            # cannot attach to anything. Sharding splits on whole listings
            # to prevent it; this is the assertion that it worked.
            note("variants whose product row is in another file",
                 len(orphan))
    print(f"checked {len(files)} file(s)")
    for k in sorted(bad):
        print(f"  [BLOCK] {k}: {bad[k]:,}")
    if not bad:
        print("  no problems. The file is structurally ready.")
    return len(bad)


def verify_pictures(out_dir, n):
    """Fetch a random sample of the picture URLs the file actually carries.

    build_ebay.py takes "does a picture exist" from the render stage's hash
    files, which is the right authority for 3.77M rows - but it is an
    authority one step removed from the URL written into the file. At 10,000
    listings the URLs themselves can simply be fetched, and a sample that
    comes back 200 image/jpeg proves the whole chain: the key convention,
    the public base, and the bucket's own contents.

    CONCURRENCY IS DELIBERATELY LOW. stores.json records that these r2.dev
    hostnames answered Cloudflare error 1015 for 7,142 of 12,834 requests at
    roughly 70/s, and 599 of 600 at 48 concurrent and 19/s. A verifier that
    trips the rate limit reports missing pictures that are not missing.
    """
    import random, subprocess
    from concurrent.futures import ThreadPoolExecutor
    cols = {k: v for k, v in P["columns"].items() if not k.startswith("_")}
    urls = set()
    for fn in sorted(os.listdir(out_dir)):
        if not fn.endswith(".csv"):
            continue
        with open(os.path.join(out_dir, fn), encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                for c in ("image_1", "image_2", "image_3"):
                    u = r.get(cols[c], "")
                    if u:
                        urls.add(u)
    urls = sorted(urls)
    random.seed(7)
    sample = random.sample(urls, min(n, len(urls)))
    print(f"{len(urls):,} distinct picture urls in the file; "
          f"checking {len(sample):,}")

    def head(u):
        # curl, not urllib: tshirt/ACCESS.md records that urllib gets 403
        # through this environment's proxy on these hosts.
        r = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "--max-time", "30",
             "-w", "%{http_code} %{content_type} %{size_download}", u],
            capture_output=True, text=True)
        return u, r.stdout.strip()

    bad = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        for u, res in ex.map(head, sample):
            code, _, rest = res.partition(" ")
            ctype, _, size = rest.partition(" ")
            if code != "200" or "image" not in ctype or int(size or 0) < 5000:
                bad.append((u, res))
    if bad:
        print(f"  [BLOCK] {len(bad)} of {len(sample)} pictures did not come "
              f"back as a usable image:")
        for u, res in bad[:6]:
            print(f"    {res}  {u}")
        return 1
    print(f"  all {len(sample):,} sampled pictures: HTTP 200, image, "
          f">5 KB")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "out", "onbuy"))
    ap.add_argument("--limit", type=int, default=10000,
                    help="listings, not rows. Each is nine variant rows.")
    ap.add_argument("--tag", default="")
    ap.add_argument("--bucket", default=P["bucket"])
    ap.add_argument("--check", metavar="DIR")
    ap.add_argument("--verify-pictures", type=int, default=0, metavar="N",
                    help="with --check: fetch N of the file's picture urls")
    a = ap.parse_args()
    if a.check:
        bad = check(a.check)
        if a.verify_pictures:
            bad += verify_pictures(a.check, a.verify_pictures)
        sys.exit(1 if bad else 0)

    store = STORES[a.bucket]
    pool = load_pool()
    print(f"job grid: {len(pool):,} designs")
    hashes = load_hashes(a.bucket)
    print(f"{a.bucket}: {len(hashes):,} panels rendered")

    picked = select(pool, hashes, a.limit, P["near_duplicate_bits"],
                    P["max_per_subject"])
    if len(picked) < a.limit:
        print(f"NOTE: asked for {a.limit:,}, got {len(picked):,}")

    rows, blocked = [], 0
    for sku, ci, title in picked:
        rs, bad = rows_for(f"{sku}-{ci}", title, pool[sku], store)
        if bad:
            blocked += 1
            continue
        rows.extend(rs)
    if blocked:
        print(f"blocked: {blocked:,}")
    report(rows)
    tag = a.tag or f"{len(rows)//(len(P['frames'])*len(P['sizes']))}"
    write(rows, a.out, a.bucket, tag)
    print()
    check(a.out)


if __name__ == "__main__":
    main()
