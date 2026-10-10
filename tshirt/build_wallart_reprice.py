#!/usr/bin/env python3
"""Wall-art reprice file: A3 unframed £14.99 -> £8.99, framed £29.95 -> £19.99.

Written in the same eBay-active-revise-price-quantity template the export
arrives in, so it uploads straight back with no conversion.

Price only. `Available quantity` is deliberately left BLANK on every row:
File Exchange leaves a blank field unchanged, so this cannot reset stock
levels on anything that has sold since the export was taken. Writing the
exported quantity back would risk exactly that.

Only listings whose two variation prices are exactly {29.95, 14.99} are
touched. Anything already repriced, or on a different structure, is skipped
and counted so the skip is visible rather than silent.

  python3 build_wallart_reprice.py <active_listings_export.csv>
"""
import csv, collections, os, sys

csv.field_size_limit(10**9)
OUT = os.path.dirname(os.path.abspath(__file__))
NEW = {"29.95": "19.99", "14.99": "8.99"}


def main():
    src = sys.argv[1]
    f = open(src, newline="", encoding="utf-8-sig", errors="replace")
    info = f.readline().rstrip("\r\n")
    r = csv.reader(f)
    hdr = [h.strip() for h in next(r)]
    ix = {h: i for i, h in enumerate(hdr)}
    QTY, PRICE, REL, CAT = (ix["Available quantity"], ix["Start price"],
                            ix["Relationship"], ix["Category name"])

    groups, cur = [], None
    for row in r:
        if not row:
            continue
        if len(row) > REL and row[REL].strip().strip('"') == "Variation":
            if cur:
                cur[1].append(row)
            continue
        if cur:
            groups.append(cur)
        cur = (row, [])
    if cur:
        groups.append(cur)

    out, skipped = [], collections.Counter()
    for parent, vars_ in groups:
        cat = parent[CAT].strip().strip('"') if len(parent) > CAT else ""
        if "360" not in cat:
            skipped["not wall art"] += 1
            continue
        if len(vars_) != 2:
            skipped[f"{len(vars_)} variations, not 2"] += 1
            continue
        prices = [v[PRICE].strip().strip('"') for v in vars_]
        if sorted(prices) != sorted(NEW):
            skipped[f"prices {sorted(prices)}"] += 1
            continue
        p = list(parent)
        p[QTY] = ""                      # never revise quantity
        p[PRICE] = ""
        nv = []
        for v in vars_:
            v = list(v)
            v[PRICE] = NEW[v[PRICE].strip().strip('"')]
            v[QTY] = ""                  # never revise quantity
            nv.append(v)
        out.append((p, nv))

    path = os.path.join(OUT, "WALLART_REPRICE.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        fh.write(info + "\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(hdr)
        for p, nv in out:
            w.writerow(p)
            for v in nv:
                w.writerow(v)

    before = len(out) * (29.95 + 14.99)
    after = len(out) * (19.99 + 8.99)
    print(f"wrote {path}")
    print(f"  listings repriced   {len(out):,}")
    print(f"  price rows changed  {len(out)*2:,}")
    print(f"  quantity rows       0   (left blank on purpose)")
    print(f"  listed value   GBP {before:,.0f} -> GBP {after:,.0f}")
    print(f"  FREES          GBP {before-after:,.0f}")
    print(f"\n  skipped: {dict(skipped.most_common(6))}")


if __name__ == "__main__":
    main()
