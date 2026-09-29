#!/usr/bin/env python3
"""Build an eBay File Exchange upload from the replica catalogue.

Business policies are all named "default" per the seller. Price, location
and quantity are set at the top so one edit changes every row.

Usage:
    python3 ebay_file.py 20            # small file to test the format
    python3 ebay_file.py               # everything
"""
import csv, html, sys

# ---- the only things that need changing -------------------------------
PRICE     = "9.99"          # <-- CONFIRM: placeholder
QUANTITY  = "1"
LOCATION  = "United Kingdom"
CATEGORY  = "15687"         # eBay UK > Men's Clothing > T-Shirts
CONDITION = "1000"          # New with tags
POLICY    = "default"       # payment / postage / returns profile name
IMG_BASE  = "https://IMAGES-NOT-UPLOADED-YET/"   # becomes the r2.dev URL
# -----------------------------------------------------------------------

HEADER = ("*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193)",
          "CustomLabel", "*Category", "*Title", "*Description", "*ConditionID",
          "PicURL", "*Quantity", "*StartPrice", "*Format", "*Duration",
          "*Location", "ShippingProfileName", "ReturnProfileName",
          "PaymentProfileName", "C:Brand", "C:Colour", "C:Material",
          "C:Size Type", "C:Style", "C:Department")


def description(r):
    slogan = r.get("slogan") or ""
    niche  = (r.get("niche") or "").title()
    printed = (f'<p style="font-size:1.1em"><b>&ldquo;{html.escape(slogan)}&rdquo;</b></p>'
               if slogan else "")
    return (
      '<div style="font-family:Arial,Helvetica,sans-serif;max-width:700px">'
      f'<h2>{html.escape(r["new_title"])}</h2>'
      + printed +
      f'<p>Printed on a heavyweight black cotton t-shirt. '
      f'{"A funny " + html.escape(niche) + " design, ideal as a gift." if niche else ""}</p>'
      '<h3>Details</h3><ul>'
      '<li>Black, 100% cotton, heavyweight</li>'
      '<li>Print centred on the chest</li>'
      '<li>Machine washable &mdash; wash inside out at 30&deg;C</li>'
      '<li>Unisex fit &mdash; see the size guide before ordering</li>'
      '</ul>'
      '<h3>Sizes</h3><p>S / M / L / XL / XXL</p>'
      '<p>Dispatched from the UK. Message us if you need a different size '
      'or colour and we will do our best to help.</p></div>')


def main(limit=None):
    rows = list(csv.DictReader(open("REPLICA_V5.csv")))
    if limit: rows = rows[:limit]
    out = "EBAY_UPLOAD_TEST.csv" if limit else "EBAY_UPLOAD.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(HEADER)
        for r in rows:
            sku = f"WLT-{int(r['source_idx']):06d}"
            w.writerow(("Add", sku, CATEGORY, r["new_title"], description(r),
                        CONDITION, IMG_BASE + sku + ".jpg", QUANTITY, PRICE,
                        "FixedPrice", "GTC", LOCATION, POLICY, POLICY, POLICY,
                        "Unbranded", "Black", "Cotton", "Regular",
                        "Graphic Tee", "Men"))
    print(f"wrote {out}  ({len(rows):,} listings)")
    print(f"  price {PRICE}  qty {QUANTITY}  policies '{POLICY}'  category {CATEGORY}")


main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
