#!/usr/bin/env python3
"""Wall-art reprice: every wall-art listing on the account, in one file.

  A3, two variations   framed  £29.95 -> £19.99
                       unframed £14.99 ->  £8.99
  A4, single print              £8.99 ->  £6.99

Written in the same eBay-active-revise-price-quantity template the export
arrives in, so it uploads straight back with no conversion.

Price only. `Available quantity` is left BLANK on every row: File Exchange
leaves a blank field unchanged, so this cannot reset stock on anything that
sold between the export and the upload.

Only listings matching an expected starting price are touched, so running it
twice is a no-op rather than a second discount. Anything else is skipped and
counted, so the skip is visible rather than silent.

  python3 build_wallart_reprice.py <active_listings_export.csv>
"""
import csv, collections, os, sys

csv.field_size_limit(10**9)
OUT = os.path.dirname(os.path.abspath(__file__))
VAR_NEW = {"29.95": "19.99", "14.99": "8.99"}     # the A3 pair
SINGLE_NEW = {"8.99": "6.99"}                     # the A4 singles


def main():
    src = sys.argv[1]
    f = open(src, newline="", encoding="utf-8-sig", errors="replace")
    info = f.readline().rstrip("\r\n")
    r = csv.reader(f)
    hdr = [h.strip() for h in next(r)]
    ix = {h: i for i, h in enumerate(hdr)}
    QTY, PRICE, REL, CAT = (ix["Available quantity"], ix["Start price"],
                            ix["Relationship"], ix["Category name"])
    def c(row, i):
        return row[i].strip().strip('"') if i < len(row) else ""

    groups, cur = [], None
    for row in r:
        if not row:
            continue
        if c(row, REL) == "Variation":
            if cur:
                cur[1].append(row)
            continue
        if cur:
            groups.append(cur)
        cur = (row, [])
    if cur:
        groups.append(cur)

    out, skipped = [], collections.Counter()
    n_var = n_single = 0
    before = after = 0.0
    for parent, vars_ in groups:
        if "360" not in c(parent, CAT):
            skipped["not wall art"] += 1
            continue
        p = list(parent)
        p[QTY] = ""                                   # never revise quantity
        if vars_:
            prices = sorted(c(v, PRICE) for v in vars_)
            if prices != sorted(VAR_NEW):
                skipped["variation prices %s" % prices] += 1
                continue
            p[PRICE] = ""
            nv = []
            for v in vars_:
                v = list(v)
                old = c(v, PRICE)
                before += float(old); after += float(VAR_NEW[old])
                v[PRICE] = VAR_NEW[old]
                v[QTY] = ""
                nv.append(v)
            out.append((p, nv)); n_var += 1
        else:
            old = c(parent, PRICE)
            if old not in SINGLE_NEW:
                skipped["single price %s" % old] += 1
                continue
            before += float(old); after += float(SINGLE_NEW[old])
            p[PRICE] = SINGLE_NEW[old]
            out.append((p, [])); n_single += 1

    path = os.path.join(OUT, "WALLART_REPRICE.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        fh.write(info + "\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(hdr)
        for p, nv in out:
            w.writerow(p)
            for v in nv:
                w.writerow(v)

    print("wrote %s" % path)
    print("  A3, two variations   %7s listings   29.95->19.99 and 14.99->8.99" % f"{n_var:,}")
    print("  A4, single print     %7s listings    8.99->6.99" % f"{n_single:,}")
    print("  TOTAL                %7s listings" % f"{len(out):,}")
    print("  quantity rows written: 0  (blank on purpose)")
    print("\n  listed value  GBP %s -> GBP %s" % (f"{before:,.0f}", f"{after:,.0f}"))
    print("  FREES         GBP %s" % f"{before-after:,.0f}")
    if skipped:
        print("\n  skipped: %s" % dict(skipped.most_common(5)))


if __name__ == "__main__":
    main()
