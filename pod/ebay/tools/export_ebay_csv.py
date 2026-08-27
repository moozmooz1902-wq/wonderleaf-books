#!/usr/bin/env python3
"""
Flatten generated listings into an upload CSV.

Column names follow eBay File Exchange conventions for a multi-variation
fixed-price listing. THIS IS A PLACEHOLDER SCHEMA - swap it for Wonderleaf's
real export the moment that file is available; only `COLUMNS` and `row()` need
to change.

Size and colour are emitted as VARIATION rows under a parent listing, never as
separate listings. That distinction is what keeps a large catalogue inside
eBay's duplicate-listing policy.

Usage:
    python3 export_ebay_csv.py --listings listings.jsonl --out upload.csv
    python3 export_ebay_csv.py --listings listings.jsonl --out upload.csv --variations
    python3 export_ebay_csv.py --listings listings.jsonl --out upload.csv --store 0 --limit 50000
"""

import argparse, csv, json, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
MATRIX = json.loads((DATA / "product_matrix.json").read_text())
SUFFIX_TO_PRODUCT = {p["id"]: p for p in MATRIX["apparel_products"]}

COLUMNS = [
    "Action", "CustomLabel", "Category", "StoreCategory", "Title", "ConditionID",
    "PicURL", "Quantity", "Format", "Duration", "StartPrice", "Currency",
    "Location", "DispatchTimeMax", "ReturnsAcceptedOption", "ShippingProfileName",
    "ReturnProfileName", "PaymentProfileName",
    "C:Brand", "C:Size", "C:Colour", "C:Material", "C:Style", "C:Department",
    "C:Type", "C:Sleeve Length", "C:Fit", "C:Neckline", "C:Occasion",
    "Relationship", "RelationshipDetails", "Description",
]

DEFAULTS = {
    "Action": "Add",
    "Category": "15687",           # Men's T-Shirts (UK). Verify before upload.
    "ConditionID": "1000",         # New with tags
    "Format": "FixedPrice",
    "Duration": "GTC",
    "Currency": "GBP",
    "Location": "United Kingdom",
    "DispatchTimeMax": "1",
    "ReturnsAcceptedOption": "ReturnsAccepted",
    "C:Material": "100% Cotton",
    "C:Department": "Men",
    "C:Type": "T-Shirt",
    "C:Occasion": "Casual",
}

DESCRIPTION = (
    "<h2>{title}</h2>"
    "<p>Printed in the UK on a quality {colour_word} garment. "
    "Direct-to-garment print, machine washable, built to last wash after wash.</p>"
    "<ul><li>Available in a full range of sizes</li>"
    "<li>Soft handle, no stiff plastisol feel</li>"
    "<li>Dispatched within one working day</li></ul>"
    "<p>Choose your size and colour from the drop-down above.</p>"
)


def row(listing, brand, size=None, colour=None, parent=False, child=False):
    p = SUFFIX_TO_PRODUCT.get(listing["product_id"], {})
    r = dict.fromkeys(COLUMNS, "")
    r.update(DEFAULTS)
    r["CustomLabel"] = listing["sku"] + (f"-{size or ''}{colour or ''}".replace(" ", "") if child else "")
    r["Title"] = listing["title"]
    r["StartPrice"] = f'{listing["price"]["from_gbp"]:.2f}'
    r["Quantity"] = "10"
    r["C:Brand"] = brand
    r["C:Style"] = "Graphic Tee"
    r["PicURL"] = f'https://REPLACE-WITH-YOUR-CDN/{listing["design_id"]}.jpg'
    r["Description"] = DESCRIPTION.format(title=listing["title"], colour_word="black")
    if parent:
        r["Relationship"] = ""
        r["RelationshipDetails"] = ""
    if child:
        r["Relationship"] = "Variation"
        details = []
        if size:
            r["C:Size"] = size
            details.append(f"Size={size}")
        if colour:
            r["C:Colour"] = colour
            details.append(f"Colour={colour}")
        r["RelationshipDetails"] = "|".join(details)
        r["Title"] = ""
        r["Description"] = ""
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listings", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--brand", default="Wonderleaf")
    ap.add_argument("--store", type=int, default=None, help="only this store index")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--variations", action="store_true",
                    help="emit variation child rows for size/colour under each parent")
    a = ap.parse_args()

    n_parent = n_child = 0
    with open(a.listings) as fh, open(a.out, "w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=COLUMNS)
        w.writeheader()
        for line in fh:
            L = json.loads(line)
            if a.store is not None and L["store_ix"] != a.store:
                continue
            if a.limit and n_parent >= a.limit:
                break
            w.writerow(row(L, a.brand, parent=True))
            n_parent += 1
            if a.variations:
                axes = L.get("variation_axes") or {}
                sizes = axes.get("size") or [None]
                colours = axes.get("colour") or [None]
                for s in sizes:
                    for c in colours:
                        w.writerow(row(L, a.brand, size=s, colour=c, child=True))
                        n_child += 1

    print(f"{n_parent:,} parent listings" + (f" + {n_child:,} variation rows" if n_child else "")
          + f" -> {a.out}")
    print("  NOTE: Category, PicURL and the shipping/return/payment profile names are "
          "placeholders. Replace with Wonderleaf's real values before uploading.")


if __name__ == "__main__":
    main()
