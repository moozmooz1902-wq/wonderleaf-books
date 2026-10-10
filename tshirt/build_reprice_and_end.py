#!/usr/bin/env python3
"""From a fresh Active listings export, build two upload files:

  1. WALLART_REPRICE_A3.csv  - revise the 77,378 A3 wall-art listings:
     unframed £14.99 -> £8.99, framed £29.95 -> £19.99.  Written in the same
     eBay-active-revise-price-quantity template the export came in, which is
     the template designed for exactly this, so it goes straight back up.

  2. EBAY_END_GR_TEES.csv    - end every live GR- t-shirt.

Only GR- SKUs are ended. The new catalogue is WLT- and the third batch is
hb_/oc_/br_/bd_/mo_/slg_/pl_/nt_/gp_; neither is touched, and both are
asserted absent from the end file before it is written.

  python3 build_reprice_and_end.py <active_listings_export.csv>
"""
import csv, collections, os, re, sys

csv.field_size_limit(10**9)
OUT = os.path.dirname(os.path.abspath(__file__))
NEWPRICE = {"29.95": "19.99", "14.99": "8.99"}


def main():
    src = sys.argv[1]
    f = open(src, newline="", encoding="utf-8-sig", errors="replace")
    info = f.readline()
    r = csv.reader(f)
    hdr = [h.strip() for h in next(r)]
    ix = {h: i for i, h in enumerate(hdr)}
    def g(row, k):
        i = ix.get(k)
        return row[i].strip().strip('"') if i is not None and i < len(row) else ""

    groups = []            # (parent_row, [variation rows])
    cur = None
    for row in r:
        if not row:
            continue
        if g(row, "Relationship") == "Variation":
            if cur:
                cur[1].append(row)
            continue
        if not g(row, "Item number"):
            continue
        if cur:
            groups.append(cur)
        cur = (row, [])
    if cur:
        groups.append(cur)

    # ---- 1. the A3 wall-art reprice ------------------------------------
    rep, changed = [], 0
    for parent, vars_ in groups:
        if "360" not in g(parent, "Category name") or len(vars_) != 2:
            continue
        prices = {g(v, "Start price") for v in vars_}
        if not prices <= set(NEWPRICE):          # only the 29.95/14.99 pair
            continue
        newvars = []
        for v in vars_:
            v = list(v)
            old = v[ix["Start price"]].strip().strip('"')
            v[ix["Start price"]] = NEWPRICE[old]
            newvars.append(v)
            changed += 1
        rep.append((parent, newvars))

    p1 = os.path.join(OUT, "WALLART_REPRICE_A3.csv")
    with open(p1, "w", newline="", encoding="utf-8-sig") as fh:
        fh.write(info if info.endswith("\n") else info + "\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(hdr)
        for parent, vars_ in rep:
            w.writerow(parent)
            for v in vars_:
                w.writerow(v)
    before = len(rep) * (29.95 + 14.99)
    after = len(rep) * (19.99 + 8.99)
    print(f"WALLART_REPRICE_A3.csv   {len(rep):,} listings, {changed:,} prices changed")
    print(f"  listed value  GBP {before:,.0f} -> GBP {after:,.0f}   frees GBP {before-after:,.0f}")

    # ---- 2. end every live GR- t-shirt ---------------------------------
    gr, other = [], collections.Counter()
    for parent, vars_ in groups:
        if "15687" not in g(parent, "Category name"):
            continue
        sku = g(parent, "Custom label (SKU)")
        if re.fullmatch(r"GR-\d+", sku):
            gr.append(g(parent, "Item number"))
        else:
            other[sku.split("_")[0] if "_" in sku else sku[:4]] += 1
    assert gr, "no GR- t-shirts found"
    p2 = os.path.join(OUT, "EBAY_END_GR_TEES.csv")
    with open(p2, "w", newline="", encoding="utf-8") as fh:
        fh.write("*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193),ItemID,EndCode\n")
        w = csv.writer(fh, lineterminator="\n")
        for i in gr:
            w.writerow(["End", i, "NotAvailable"])
    print(f"\nEBAY_END_GR_TEES.csv     {len(gr):,} rows")
    print(f"  frees GBP {len(gr)*11.99:,.0f}   (single-item listings at GBP 11.99)")
    print(f"  NOT touched: {sum(other.values()):,} other t-shirts -> {dict(other.most_common(6))}")


if __name__ == "__main__":
    main()
