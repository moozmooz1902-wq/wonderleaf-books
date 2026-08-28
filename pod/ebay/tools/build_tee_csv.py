#!/usr/bin/env python3
"""
Build the eBay File Exchange CSV for the t-shirt catalogue.

Uses Wonderleaf's EXACT live header from ebay_graphics.py / SPEC section 6, so
the file uploads against the account as it is configured today.

Two modes:
  --flat        one row per design, C:Size = One Size, buyer types their size in
                the personalisation box. Matches the store's current setup.
  --variations  parent + one row per size (default S,M,L,XL,2XL). Keeps the
                listing inside eBay's size filter, which the flat format is
                excluded from - that is why the flat store made one sale.
"""

import argparse, csv, html, json
from pathlib import Path

HEADER = ("Action(SiteID=UK|Country=GB|Currency=GBP|Version=745|CC=UTF-8),CustomLabel,"
          "*Category,StoreCategory,Relationship,RelationshipDetails,*Title,Subtitle,"
          "*Description,*ConditionID,PicURL,*Format,*Duration,*StartPrice,*Quantity,"
          "*Location,PostalCode,ShippingProfileName,ReturnProfileName,"
          "PaymentProfileName,*C:Size,*C:Colour,C:Brand,*C:Type,*C:Style,C:Department,"
          "*C:Material,C:Sleeve Length,C:Neckline,C:Fit,C:Pattern,C:Size Type,"
          "C:Garment Care,C:Occasion,C:Theme,C:Country/Region of Manufacture,"
          "C:Personalise,C:Personalisation Instructions,C:Handmade,C:Features").split(",")

SIZES = ["S", "M", "L", "XL", "2XL"]
DESC = (
    '<div style="font-family:Arial,sans-serif;max-width:700px">'
    '<h2>{title}</h2>'
    '<p>Printed in the UK on a black 100% cotton t-shirt, 180gsm, crew neck, '
    'regular fit. Direct-to-garment print - soft handle, no stiff plastisol feel, '
    'machine washable.</p>'
    '<ul><li>Black, 100% cotton, 180gsm</li>'
    '<li>Crew neck, short sleeve, regular fit</li>'
    '<li>Machine washable, wash inside out</li>'
    '<li>Dispatched within one working day from the UK</li></ul>'
    '<p>{sizeline}</p></div>'
)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalogue", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--img-base", default="https://REPLACE-WITH-YOUR-R2-BUCKET/mock")
    ap.add_argument("--category", default="15687")
    ap.add_argument("--shipping", default="2")
    ap.add_argument("--returns", default="1")
    ap.add_argument("--payment", default="1")
    ap.add_argument("--price", default="11.99")
    ap.add_argument("--brand", default="Unbranded")
    ap.add_argument("--location", default="Manchester")
    ap.add_argument("--variations", action="store_true")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    designs = json.loads(Path(a.catalogue).read_text())
    if a.limit:
        designs = designs[:a.limit]

    def base(d, size, rel="", reldet="", title=None, desc=None, pic=None):
        r = dict.fromkeys(HEADER, "")
        r[HEADER[0]] = "Add"
        r["CustomLabel"] = d["design_id"]
        r["*Category"] = a.category
        r["Relationship"] = rel
        r["RelationshipDetails"] = reldet
        r["*Title"] = title if title is not None else d["title"]
        r["*Description"] = desc if desc is not None else ""
        r["*ConditionID"] = "1000"
        r["PicURL"] = pic if pic is not None else f"{a.img_base}/{d['design_id']}.jpg"
        r["*Format"] = "FixedPrice"
        r["*Duration"] = "GTC"
        r["*StartPrice"] = a.price
        r["*Quantity"] = "1"
        r["*Location"] = a.location
        r["PostalCode"] = ""          # blank on purpose - a shared postcode links accounts
        r["ShippingProfileName"] = a.shipping
        r["ReturnProfileName"] = a.returns
        r["PaymentProfileName"] = a.payment
        r["*C:Size"] = size
        r["*C:Colour"] = "Black"
        r["C:Brand"] = a.brand
        r["*C:Type"] = "T-Shirt"
        r["*C:Style"] = "Graphic Tee"
        r["C:Department"] = "Men"
        r["*C:Material"] = "100% Cotton"
        r["C:Sleeve Length"] = "Short Sleeve"
        r["C:Neckline"] = "Crew Neck"
        r["C:Fit"] = "Regular"
        r["C:Pattern"] = "Graphic"
        r["C:Size Type"] = "Regular"
        r["C:Garment Care"] = "Machine Washable"
        r["C:Occasion"] = "Casual"
        r["C:Theme"] = d.get("cluster", "").title()
        r["C:Country/Region of Manufacture"] = "United Kingdom"
        r["C:Handmade"] = ""
        r["C:Features"] = "Breathable"
        return r

    n_parent = n_child = 0
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        for d in designs:
            t = html.escape(d["title"])
            if a.variations:
                desc = DESC.format(title=t, sizeline="Choose your size from the menu above.")
                w.writerow(base(d, "", rel="", reldet="Size=" + ";".join(SIZES),
                                desc=desc))
                n_parent += 1
                for s in SIZES:
                    w.writerow(base(d, s, rel="Variation", reldet=f"Size={s}",
                                    title=d["title"], desc="", pic=""))
                    n_child += 1
            else:
                r = base(d, "One Size",
                         desc=DESC.format(title=t,
                                          sizeline="Type your size in the box at checkout: "
                                                   "S, M, L, XL, XXL."))
                r["C:Personalise"] = "Yes"
                r["C:Personalisation Instructions"] = "TYPE SIZE BELOW, CHOOSE: S,M,L,XL,XXL"
                w.writerow(r)
                n_parent += 1

    print(f"  {n_parent:,} listings" + (f" + {n_child:,} variation rows" if n_child else "")
          + f" -> {a.out}")
    if not a.variations:
        print("  NOTE: C:Size = One Size is excluded from every size-filtered eBay search.")
        print("        --variations keeps the listing in those results.")
    print("  Replace --img-base with your real R2 bucket before uploading.")


if __name__ == "__main__":
    main()
