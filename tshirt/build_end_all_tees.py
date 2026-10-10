#!/usr/bin/env python3
"""End every old t-shirt on the account, from a fresh Active listings export.

The seller's instruction: take all the PREVIOUS t-shirts off, not the new
ones.

Safety. The old catalogue uses GR-####### SKUs and the new catalogue uses
WLT-######. Only GR- rows are ended, so the new listings cannot be touched by
SKU alone, and the export is additionally checked to contain no WLT- rows at
all before anything is written. Two further exclusions match the first end
file (build_end.py): the 22 listings on hb_/oc_/br_ SKUs, which are a separate
batch, and the 40 that carry size variations.

Ordering. The 125,966 already ended on 7 October are still marked active in
this export, so they are included - if those ends did take effect eBay will
simply reject those rows, and if they did not this file finishes the job.
Rows not yet ended are written FIRST so that a partial run does the useful
work.

  python3 build_end_all_tees.py <active_listings_export.csv>
"""
import csv, os, re, sys

csv.field_size_limit(10**9)
OUT = os.path.dirname(os.path.abspath(__file__))
ALREADY = os.path.join(OUT, "EBAY_END_TSHIRTS.csv")
PRICE = 11.99


def main():
    src = sys.argv[1]
    ended = set()
    if os.path.exists(ALREADY):
        with open(ALREADY, newline="", encoding="utf-8") as f:
            r = csv.reader(f); next(r, None)
            for row in r:
                if len(row) >= 2:
                    ended.add(row[1].strip())

    f = open(src, newline="", encoding="utf-8-sig", errors="replace")
    f.readline()                                   # the #INFO line
    r = csv.reader(f)
    hdr = [h.strip() for h in next(r)]
    ix = {h: i for i, h in enumerate(hdr)}
    def g(row, k):
        i = ix.get(k)
        return row[i].strip().strip('"') if i is not None and i < len(row) else ""

    # first pass: collect parents and count variation rows per listing
    parents, varcount, order = {}, {}, []
    cur = None
    for row in r:
        if not row:
            continue
        if g(row, "Relationship") == "Variation":
            if cur:
                varcount[cur] = varcount.get(cur, 0) + 1
            continue
        item = g(row, "Item number")
        if not item:
            continue
        cur = item
        parents[item] = (g(row, "Custom label (SKU)"), g(row, "Title"),
                         g(row, "Category name"))
        order.append(item)

    tees = [i for i in order if "15687" in parents[i][2]]
    wlt = [i for i in tees if parents[i][0].startswith("WLT-")]
    print(f"parent listings in export   {len(order):,}")
    print(f"t-shirts (15687)            {len(tees):,}")
    print(f"  WLT- new catalogue rows   {len(wlt):,}   <- must be 0")
    assert not wlt, "export contains the new catalogue; refusing to build"

    eligible, skip_sku, skip_var = [], 0, 0
    for i in tees:
        sku = parents[i][0]
        if not re.fullmatch(r"GR-\d+", sku):
            skip_sku += 1
            continue
        if varcount.get(i, 0) > 0:
            skip_var += 1
            continue
        eligible.append(i)
    print(f"  held back, non GR- SKU    {skip_sku:,}")
    print(f"  held back, has variations {skip_var:,}")
    print(f"  ELIGIBLE TO END           {len(eligible):,}")

    fresh = [i for i in eligible if i not in ended]
    again = [i for i in eligible if i in ended]
    print(f"\n  not yet ended (written first) {len(fresh):,}")
    print(f"  already ended 7 Oct           {len(again):,}  (included as a safety net)")

    chosen = fresh + again
    assert len(set(chosen)) == len(chosen), "duplicate ItemIDs"

    p = os.path.join(OUT, "EBAY_END_ALL_TEES.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        fh.write("*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193),ItemID,EndCode\n")
        w = csv.writer(fh, lineterminator="\n")
        for i in chosen:
            w.writerow(["End", i, "NotAvailable"])
    print(f"\nwrote {p}")
    print(f"  {len(chosen):,} rows")
    print(f"  value if ending frees it: GBP {len(fresh)*PRICE:,.0f} from the "
          f"{len(fresh):,} still live")


if __name__ == "__main__":
    main()
