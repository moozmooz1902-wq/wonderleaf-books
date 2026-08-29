#!/usr/bin/env python3
"""
Build the eBay File Exchange CSV for the t-shirt catalogue.

Follows the conventions in ebay_graphics.py, which is the code that produced
the listings currently live on the account. Where the two could differ, this
file follows the live one - the point is a CSV that uploads against the
account exactly as it is configured today.

    python3 build_tee_csv.py \
        --catalogue catalogue.json \
        --img-base https://pub-XXXX.r2.dev \
        --out tshirt_m12k

Writes tshirt_m12k_01.csv, _02.csv ... split so no single file is too large
for File Exchange to accept.

MODES
  (default)   parent + one row per size. The listing appears in size-filtered
              search, which is where most t-shirt buyers narrow down.
  --single    one row, C:Size = One Size, buyer types the size into the
              personalisation box. Uses a tenth of the selling limit and is
              excluded from every size-filtered search.
"""

import argparse, csv, html, json, os, random, sys
from pathlib import Path

ACTION = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=745|CC=UTF-8)"
HEADER = [
    ACTION, "CustomLabel", "*Category", "StoreCategory",
    "Relationship", "RelationshipDetails", "*Title", "Subtitle",
    "*Description", "*ConditionID", "PicURL", "*Format", "*Duration",
    "*StartPrice", "*Quantity", "*Location", "PostalCode",
    "ShippingProfileName", "ReturnProfileName", "PaymentProfileName",
    "*C:Size", "*C:Colour", "C:Brand", "*C:Type", "*C:Style", "C:Department",
    "*C:Material", "C:Sleeve Length", "C:Neckline", "C:Fit", "C:Pattern",
    "C:Size Type", "C:Garment Care", "C:Occasion", "C:Theme",
    "C:Country/Region of Manufacture", "C:Personalise",
    # C:Handmade goes out BLANK on purpose. The personalisation box works
    # without it, and these are print-on-demand, not handmade.
    "C:Personalisation Instructions", "C:Handmade", "C:Features",
]

QTY = 1

# Adults only, one price. Halves the rows per listing against the kids+adults
# ladder, and halves what the catalogue costs against the selling limit.
ADULT = [("S", 11.99), ("M", 11.99), ("L", 11.99), ("XL", 11.99),
         ("2XL", 11.99)]

# The full ladder the earlier listings used, kept for a store that wants it.
# Only the smallest kids size is cheaper.
ALL_SIZES = [
    ("3-4 Yrs", 8.99),
    ("5-6 Yrs", 11.99), ("7-8 Yrs", 11.99),
    ("9-11 Yrs", 11.99), ("12-13 Yrs", 11.99),
] + ADULT

# The word a buyer in this family would actually type, for C:Theme. eBay uses
# item specifics as sidebar filters, so a value nobody searches is a wasted
# field.
THEME = {
    "birthday": "Birthday", "occupation": "Novelty", "hobby": "Hobby",
    "breed": "Animals", "slogan": "Novelty", "place": "Novelty",
    "heritage": "Novelty", "biker": "Biker", "music": "Music",
    "military": "Military", "food": "Food & Drink", "gothic": "Gothic",
    "norse": "Viking Norse",
}

_SZ = [("S", "34-36", "18", "28"), ("M", "38-40", "20", "29"),
       ("L", "42-44", "22", "30"), ("XL", "46-48", "24", "31"),
       ("2XL", "50-52", "26", "32")]
_cell = 'style="padding:6px 9px;border-bottom:1px solid #e5e5e8"'
_ALT = ' style="background:#fafafb"'
_rowlist = []
for _i, (_s, _f, _w, _l) in enumerate(_SZ):
    _bg = _ALT if _i % 2 else ""
    _rowlist.append(
        "<tr" + _bg + ">"
        "<td " + _cell + "><strong>" + _s + "</strong></td>"
        "<td " + _cell + ">" + _f + "&quot;</td>"
        "<td " + _cell + ">" + _w + "&quot;</td>"
        "<td " + _cell + ">" + _l + "&quot;</td></tr>")
_ROWS = "\n".join(_rowlist)

DESC = """<div style="font-family:Arial,Helvetica,sans-serif;max-width:800px;margin:0 auto;color:#222;line-height:1.6">
<div style="background:#111;color:#fff;padding:22px 26px;border-radius:6px 6px 0 0">
<h1 style="margin:0;font-size:24px">{subject}</h1>
<p style="margin:6px 0 0;font-size:14px;opacity:.75">Premium Printed <strong>Black</strong> T-Shirt &middot; Mens (Unisex) &middot; UK Sizing</p>
</div>
<div style="border:1px solid #e3e3e6;border-top:none;padding:26px;border-radius:0 0 6px 6px">

<p style="font-size:15px">A bold <strong>{subject}</strong> design printed on a soft heavyweight <strong>black</strong> cotton tee. Printed in the UK using a professional direct-to-film process, so the print stays crisp and flexible rather than thick or plasticky &mdash; and it holds up wash after wash.</p>

<h2 style="font-size:17px;border-bottom:2px solid #111;padding-bottom:6px;margin-top:26px">Product Details</h2>
<ul style="padding-left:20px;font-size:15px">
<li>Crew Necked T-Shirt</li><li><strong>Colour: Black</strong></li>
<li>Mens (Unisex)</li><li>Classic Fit</li>
<li>180gsm heavy cotton</li><li>Age 3-4 Yrs to 2XL</li>
<li>100% Cotton</li>
<li>Pre-shrunk jersey knit</li><li>Taped neck and shoulders</li>
<li>Twin needle sleeve and bottom hems</li><li>Seamless twin needle collar</li>
<li>Tear away label</li><li>Hard wearing fabric</li>
</ul>
<p style="font-size:15px;margin-top:14px">Printed with eco-friendly inks, which are safe on skin and suitable for children.</p>

<h2 style="font-size:17px;border-bottom:2px solid #111;padding-bottom:6px;margin-top:26px">Size Guide</h2>
<p style="font-size:15px">Measured flat, in inches. Allow up to one inch tolerance.</p>
<table style="width:100%;border-collapse:collapse;font-size:14px;margin-top:10px">
<tr style="background:#111;color:#fff"><th style="padding:7px 9px;text-align:left">Size</th><th style="padding:7px 9px;text-align:left">To Fit Chest</th><th style="padding:7px 9px;text-align:left">Width</th><th style="padding:7px 9px;text-align:left">Length</th></tr>
{rows}
</table>
<p style="font-size:14px;margin-top:14px"><strong>Kids sizes</strong> &mdash; 3-4 Yrs (chest 14&quot;), 5-6 Yrs (15&quot;), 7-8 Yrs (16&quot;), 9-11 Yrs (17&quot;), 12-13 Yrs (18&quot;).</p>
<p style="font-size:15px"><strong>Fit note:</strong> Mens (Unisex) classic fit. These run a little roomier than high street brands &mdash; if you prefer a slim fit, consider going one size down.</p>

<h2 style="font-size:17px;border-bottom:2px solid #111;padding-bottom:6px;margin-top:26px">Postage &amp; Returns</h2>
<p style="font-size:15px">Dispatched from the UK with tracked delivery. If anything is not right, get in touch and we will sort it &mdash; returns are straightforward.</p>

<h2 style="font-size:17px;border-bottom:2px solid #111;padding-bottom:6px;margin-top:26px">Care</h2>
<p style="font-size:15px">Machine wash at 30&deg;C inside out. Do not iron directly on the print. Do not tumble dry on high.</p>

<p style="margin-top:24px;font-size:11px;color:#9a9aa0">{tags}</p>
</div></div>"""


# How many listings apart two designs from the same family must be.
WINDOW = 6


def subject_of(d):
    """oc_bouncer_Nan_6 -> oc_bouncer. The design family, not the variant."""
    return d["design_id"].rsplit("_", 2)[0]


def spread(designs, seed):
    """
    Order the catalogue so no theme arrives in a block.

    A plain shuffle is random, not spread: on this catalogue it left 18.9% of
    listings next to one from the same cluster, with runs of up to 9 in a row.
    A newly-listed feed carrying nine dog breeds and then nine occupations
    reads as one seller flooding a category, which is exactly the impression
    to avoid.

    So each group is dealt out at even intervals across the whole sequence
    instead. An item that is jth of n in its group is placed at position
    (j + 0.5) / n, which spaces that group's items n/total apart no matter how
    big or small the group is. A small jitter - always less than half a slot,
    so the ordering survives - stops the result from looking mechanically
    regular.

    Done twice: first on the design family, so eight Bouncer designs never
    bunch, then on the cluster, so hobby and occupation alternate.
    """
    rnd = random.Random(seed)

    def deal(items, key):
        groups = {}
        for it in items:
            groups.setdefault(key(it), []).append(it)
        placed = []
        for g in groups.values():
            n = len(g)
            for j, it in enumerate(g):
                pos = (j + 0.5) / n + rnd.uniform(-0.3, 0.3) / n
                placed.append((pos, rnd.random(), it))
        placed.sort(key=lambda t: (t[0], t[1]))
        return [it for _, _, it in placed]

    out = []
    by_cluster = {}
    for d in designs:
        by_cluster.setdefault(d.get("cluster", ""), []).append(d)
    for cl, items in by_cluster.items():
        rnd.shuffle(items)
        by_cluster[cl] = deal(items, subject_of)   # spread families within
    for cl, items in by_cluster.items():
        out.extend(items)
    out = deal(out, lambda d: d.get("cluster", ""))   # then spread clusters

    # Dealing by cluster reshuffles the families back together again: it cut
    # cluster runs to 2 but still left 5.6% of listings with another from the
    # same family within five rows - eight Bouncer shirts spread over twenty
    # is still recognisably one seller filling a niche. So walk the sequence
    # once and push any early repeat further down, swapping it with the first
    # later listing that does not clash. Costs a little cluster alternation
    # (1.8% -> 3.7% adjacent, runs of 4 rather than 2, against 18.9% and runs
    # of 9 for a plain shuffle) and takes family repeats to 0.03%.
    for i in range(len(out)):
        recent = {subject_of(x) for x in out[max(0, i - WINDOW):i]}
        if subject_of(out[i]) not in recent:
            continue
        for k in range(i + 1, min(i + 8 * WINDOW, len(out))):
            if subject_of(out[k]) not in recent:
                out[i], out[k] = out[k], out[i]
                break
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalogue", required=True)
    ap.add_argument("--out", default="tshirt_ebay",
                    help="prefix; files are <prefix>_01.csv, _02.csv ...")
    ap.add_argument("--img-base", required=True,
                    help="public bucket URL, e.g. https://pub-XXXX.r2.dev")
    ap.add_argument("--category", default="15687")
    ap.add_argument("--shipping", default="1")
    ap.add_argument("--returns", default="1")
    ap.add_argument("--payment", default="1")
    # City stays, postcode does not. Plenty of sellers are in Manchester, so a
    # shared city is not the signal a shared POSTCODE is - the postcode is
    # specific enough to tie accounts together.
    ap.add_argument("--location", default="Manchester")
    ap.add_argument("--postcode", default="",
                    help="normally blank: eBay falls back to the account's own "
                         "postcode, which is already right per store")
    ap.add_argument("--brand", default="Unbranded")
    ap.add_argument("--sizes", choices=("adult", "all"), default="adult",
                    help="adult = S-2XL at one price (default). all = adds "
                         "the five kids sizes, doubling both the row count "
                         "and the selling limit the catalogue consumes")
    ap.add_argument("--price", type=float, default=11.99,
                    help="the adult price")
    ap.add_argument("--max-mb", type=float, default=70.0,
                    help="max size of one output file. File Exchange takes "
                         "up to about 100 MB, so 70 leaves headroom while "
                         "keeping the number of uploads down. Capping on rows "
                         "is the wrong thing: the rich description dominates")
    ap.add_argument("--rows", type=int, default=1000000,
                    help="secondary cap on data rows per file")
    ap.add_argument("--single", action="store_true",
                    help="one row per design, size typed into the "
                         "personalisation box")
    ap.add_argument("--single-price", type=float, default=11.99)
    ap.add_argument("--personalise-text",
                    default="TYPE SIZE BELOW, CHOOSE: S,M,L,XL,XXL")
    # Sorted output groups the catalogue by subject, because neighbouring
    # design ids share one subject. A sorted upload therefore arrives as a
    # block of birthdays, then a block of dog breeds, which looks like spam in
    # a newly-listed feed and makes any slice taken for another store all one
    # thing.
    ap.add_argument("--no-shuffle", action="store_true",
                    help="upload in catalogue order. Almost never wanted: it "
                         "arrives as a block of one theme at a time")
    ap.add_argument("--seed", type=int, default=20260829,
                    help="use a different seed per store so each gets its "
                         "own mix")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    global SIZES
    SIZES = ([(sz, a.price) for sz, _ in ADULT] if a.sizes == "adult"
             else ALL_SIZES)

    base_url = a.img_base.rstrip("/")
    designs = json.loads(Path(a.catalogue).read_text())

    if not a.no_shuffle:
        designs = spread(designs, a.seed)
    if a.limit:
        designs = designs[:a.limit]

    seen = set()
    dupes = 0

    def row(d, size, price, rel="", reldet="", desc="", pic="",
            child=False):
        """
        One CSV row, built to match the live listings exactly.

        The shape of a variation group is not a matter of taste - File
        Exchange rejects or mangles anything else:
          parent  Action=Add, the CustomLabel, the picture, the description,
                  NO price and NO quantity, C:Size blank
          child   Action BLANK, CustomLabel BLANK, no picture, no description,
                  no profiles, carrying only the size and its price
        Putting Add and a CustomLabel on the children is what turns one
        listing into eleven.
        """
        kids = "Yrs" in size
        r = dict.fromkeys(HEADER, "")
        r[ACTION] = "" if child else "Add"
        r["CustomLabel"] = "" if child else d["design_id"]
        r["*Category"] = a.category
        r["Relationship"] = rel
        r["RelationshipDetails"] = reldet
        r["*Title"] = d["title"]
        r["*Description"] = desc
        r["*ConditionID"] = "1000"
        r["PicURL"] = pic
        r["*Format"] = "" if child else "FixedPrice"
        r["*Duration"] = "" if child else "GTC"
        r["*StartPrice"] = f"{price:.2f}" if price is not None else ""
        r["*Quantity"] = "" if price is None else str(QTY)
        r["*Location"] = "" if child else a.location
        r["PostalCode"] = "" if child else a.postcode
        r["ShippingProfileName"] = "" if child else a.shipping
        r["ReturnProfileName"] = "" if child else a.returns
        r["PaymentProfileName"] = "" if child else a.payment
        r["*C:Size"] = size
        r["*C:Colour"] = "Black"
        r["C:Brand"] = a.brand
        r["*C:Type"] = "T-Shirt"
        r["*C:Style"] = "Graphic Tee"
        r["C:Department"] = "Unisex Kids" if kids else "Unisex Adults"
        r["*C:Material"] = "Cotton"
        r["C:Sleeve Length"] = "Short Sleeve"
        r["C:Neckline"] = "Crew Neck"
        r["C:Fit"] = "Regular"
        r["C:Pattern"] = "No Pattern"
        r["C:Size Type"] = "Regular"
        r["C:Garment Care"] = "Machine Washable"
        r["C:Occasion"] = "Casual"
        r["C:Theme"] = THEME.get(d.get("cluster", ""), "Graphic")
        r["C:Country/Region of Manufacture"] = "United Kingdom"
        r["C:Personalise"] = "No"
        r["C:Features"] = "Breathable"
        return r

    files, buf, n, nbytes = [], [], 1, 0
    cap = int(a.max_mb * 1e6)

    def flush():
        nonlocal buf, n, nbytes
        if not buf:
            return
        fn = f"{a.out}_{n:02d}.csv"
        with open(fn, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=HEADER)
            w.writeheader()
            w.writerows(buf)
        print(f"  {fn}  {len(buf):,} rows  "
              f"{os.path.getsize(fn) / 1e6:.1f} MB")
        files.append(fn)
        buf, nbytes = [], 0
        n += 1

    listings = 0
    for d in designs:
        t = d["title"]
        # A duplicate title is not a near-duplicate that eBay might cluster -
        # it is the SAME listing twice, and it will be rejected or suppressed.
        # Catch it here rather than after a 300,000 row upload.
        if t in seen:
            dupes += 1
            continue
        seen.add(t)

        subject = html.escape(d.get("stem", t))
        tags = html.escape(", ".join(
            x for x in (d.get("cluster", ""), d.get("theme", "")) if x))
        desc = DESC.format(subject=subject, rows=_ROWS, tags=tags)
        pic = f"{base_url}/art/mock/{d['design_id']}.jpg"

        if a.single:
            # Size is "One Size" deliberately: the field is required by the
            # category, and a real size there would contradict the box.
            r = row(d, "One Size", a.single_price, desc=desc, pic=pic)
            r["C:Personalise"] = "Yes"
            r["C:Personalisation Instructions"] = a.personalise_text
            buf.append(r)
        else:
            # The parent carries the picture and the description and no price;
            # the children carry only what differs, which is size and price.
            buf.append(row(d, "", None,
                           reldet="Size=" + ";".join(s for s, _ in SIZES),
                           desc=desc, pic=pic))
            for size, price in SIZES:
                buf.append(row(d, size, price, rel="Variation",
                               reldet=f"Size={size}", child=True))
        listings += 1
        # Estimate rather than measure: the description dominates and is the
        # only field that varies much in size.
        nbytes += len(desc) + 600 * (1 if a.single else len(SIZES))
        if nbytes >= cap or len(buf) >= a.rows:
            flush()
    flush()

    per = 1 if a.single else 1 + len(SIZES)
    items = listings * (1 if a.single else len(SIZES))
    value = (listings * a.single_price if a.single
             else listings * sum(p for _, p in SIZES))
    print(f"  sizes: {', '.join(sz for sz, _ in SIZES)}")
    print(f"\n  {listings:,} listings, {listings * per:,} rows, "
          f"{len(files)} file(s)")
    print("  each file is self-contained: a parent and its size rows are "
          "never split across two")
    if dupes:
        print(f"  {dupes:,} designs skipped for duplicate titles")
    print(f"  selling limit used: {items:,} items, £{value:,.0f} of value")
    if a.single:
        print("\n  NOTE: C:Size = One Size is excluded from every size-filtered")
        print("        eBay search. Drop --single to keep the listing in them.")


if __name__ == "__main__":
    main()
