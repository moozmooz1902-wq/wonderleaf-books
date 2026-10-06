#!/usr/bin/env python3
"""eBay File Exchange upload with S-XXL adult size variations.

One parent row per design carrying the title, category, description,
picture and policies, then five variation rows carrying the size, price and
quantity. That is how a buyer picks a size on one listing rather than
seeing five separate ones.

The seller's business policies are all named "1". Adult sizes only.
"""
import csv, html, sys
import r2_config

PRICE     = "12.99"
QUANTITY  = "5"              # per size
SIZES     = ["S", "M", "L", "XL", "XXL"]
SIZE_NAME = {"S": "Small", "M": "Medium", "L": "Large",
             "XL": "X-Large", "XXL": "XX-Large"}
LOCATION  = "United Kingdom"
CATEGORY  = "15687"
CONDITION = "1000"
POLICY    = "1"
PREFIX    = "v2/"

HEADER = ("*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193)",
          "CustomLabel", "*Category", "*Title", "*Description", "*ConditionID",
          "PicURL", "*Quantity", "*StartPrice", "*Format", "*Duration",
          "*Location", "ShippingProfileName", "ReturnProfileName",
          "PaymentProfileName", "Relationship", "RelationshipDetails",
          "C:Brand", "C:Colour", "C:Material", "C:Size", "C:Size Type",
          "C:Style", "C:Department", "C:Type", "C:Fit", "C:Sleeve Length",
          "C:Neckline", "C:Pattern", "C:Occasion")


def description(r):
    slogan = r.get("slogan") or ""
    printed = (f'<p style="font-size:1.15em;margin:18px 0"><b>&ldquo;'
               f'{html.escape(slogan)}&rdquo;</b></p>' if slogan else "")
    return (
      '<div style="font-family:Arial,Helvetica,sans-serif;max-width:720px;line-height:1.5">'
      f'<h2 style="margin:0 0 6px">{html.escape(r["new_title"])}</h2>'
      + printed +
      '<p>Printed on a heavyweight black cotton t-shirt, chest centred.</p>'
      '<h3>Details</h3><ul>'
      '<li>Black, 100% ringspun cotton, heavyweight</li>'
      '<li>Unisex adult fit, S to XXL</li>'
      '<li>Print centred on the chest, approx 22cm wide</li>'
      '<li>Machine washable &mdash; wash inside out at 30&deg;C, do not iron the print</li>'
      '</ul>'
      '<h3>Size guide (chest, to fit)</h3>'
      '<table cellpadding="6" style="border-collapse:collapse">'
      '<tr><th align="left">Size</th><th align="left">Chest</th></tr>'
      '<tr><td>S</td><td>34-36"</td></tr><tr><td>M</td><td>38-40"</td></tr>'
      '<tr><td>L</td><td>42-44"</td></tr><tr><td>XL</td><td>46-48"</td></tr>'
      '<tr><td>XXL</td><td>50-52"</td></tr></table>'
      '<p>Dispatched from the UK. Message us if you need a different size and '
      'we will do our best to help.</p></div>')


def main(limit=None):
    rows = [r for r in csv.DictReader(open("FINAL_V7.csv")) if r.get("slogan")]
    if limit: rows = rows[:limit]
    out = "EBAY_VARIATIONS_TEST.csv" if limit else "EBAY_VARIATIONS.csv"
    n = 0
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(HEADER)
        for r in rows:
            sku = f"WLT-{int(r['source_idx']):06d}"
            pic = f"{r2_config.PUBLIC_BASE}/{PREFIX}{sku}.jpg"
            # parent: everything about the listing except price and size
            w.writerow(("Add", sku, CATEGORY, r["new_title"], description(r),
                        CONDITION, pic, "", "", "FixedPrice", "GTC", LOCATION,
                        POLICY, POLICY, POLICY, "", "",
                        "Unbranded", "Black", "Cotton", "", "Regular",
                        "Graphic Tee", "Men", "T-Shirt", "Regular",
                        "Short Sleeve", "Crew Neck", "Graphic Print", "Casual"))
            # children: one per size
            for s in SIZES:
                w.writerow(("", f"{sku}-{s}", "", "", "", "", "", QUANTITY,
                            PRICE, "", "", "", "", "", "",
                            "Variation", f"Size={SIZE_NAME[s]}",
                            "", "", "", SIZE_NAME[s], "", "", "", "", "", "",
                            "", "", ""))
            n += 1
    print(f"wrote {out}")
    print(f"  {n:,} designs x {len(SIZES)} sizes = {n*len(SIZES):,} variations")
    print(f"  {n*(1+len(SIZES)):,} rows total")
    print(f"  price {PRICE}, qty {QUANTITY}/size, policies '{POLICY}', category {CATEGORY}")


main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
