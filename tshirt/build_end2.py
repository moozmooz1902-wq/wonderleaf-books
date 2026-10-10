#!/usr/bin/env python3
"""Build the NEXT tranche of t-shirt ends, from a fresh active-listings export.

Run after the first 125,966 ends (EBAY_END_TSHIRTS.csv, uploaded 2026-10-07).

Why a fresh export is required and the old one will not do: the container no
longer holds the active t-shirt export the first end file was built from, and
more importantly the account has changed twice since - 125,966 listings ended
and about 20,000 new ones went live. Ending from a stale list would at best
re-end listings that are already gone and at worst END THE NEW UPLOADS, which
are the whole point of the exercise.

Two independent guards against that:
  * every ItemID already in EBAY_END_TSHIRTS.csv is skipped;
  * every listing whose SKU matches the new catalogue's WLT- pattern, or whose
    ItemID is newer than the newest already-ended one, is skipped.

Selection order is the same as the first file, worst-first:
  1. duplicate titles live against each other - keep one, end the rest;
  2. then longest-listed (lowest ItemID) until the target is met.

  python3 build_end2.py <active_listings_export.csv> <how_many>
"""
import csv, collections, re, sys, os

csv.field_size_limit(10**9)
OUT = os.path.dirname(os.path.abspath(__file__))
ALREADY = os.path.join(OUT, "EBAY_END_TSHIRTS.csv")


def norm(t):
    t = re.sub(r"[^a-z0-9 ]", " ", t.lower())
    return " ".join(t.split())


def find_header(path):
    """eBay exports carry one to three #INFO lines before the real header."""
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        for n, line in enumerate(f):
            if line.lstrip().startswith("#INFO"):
                continue
            if "Item number" in line or "ItemID" in line:
                return n
            if n > 12:
                break
    return 0


def main():
    src, want = sys.argv[1], int(sys.argv[2])

    ended = set()
    if os.path.exists(ALREADY):
        with open(ALREADY, newline="", encoding="utf-8") as f:
            r = csv.reader(f); next(r, None)
            for row in r:
                if len(row) >= 2:
                    ended.add(row[1].strip())
    newest_ended = max((int(x) for x in ended if x.isdigit()), default=0)
    print(f"already ended      {len(ended):,}   newest ItemID {newest_ended}")

    skip = find_header(src)
    f = open(src, newline="", encoding="utf-8-sig", errors="replace")
    for _ in range(skip):
        f.readline()
    r = csv.reader(f)
    hdr = [h.strip() for h in next(r)]
    ix = {h: i for i, h in enumerate(hdr)}
    def g(row, *names):
        for k in names:
            i = ix.get(k)
            if i is not None and i < len(row):
                v = row[i].strip().strip('"')
                if v:
                    return v
        return ""

    live, skipped_new, skipped_done, not_tee = [], 0, 0, 0
    for row in r:
        if not row:
            continue
        if g(row, "Relationship", "Relationship ") == "Variation":
            continue
        item = g(row, "Item number", "ItemID")
        title = g(row, "Title")
        if not item or not title:
            continue
        sku = g(row, "Custom label (SKU)", "CustomLabel")
        cat = g(row, "eBay category 1 number", "*Category", "Category name")
        if cat and "15687" not in cat and "shirt" not in cat.lower():
            not_tee += 1
            continue
        if item in ended:
            skipped_done += 1
            continue
        # never touch the new catalogue
        if sku.startswith("WLT-") or (item.isdigit() and int(item) > newest_ended):
            skipped_new += 1
            continue
        if not re.fullmatch(r"GR-\d+", sku):      # same eligibility as before
            continue
        live.append((item, sku, title))

    print(f"not t-shirts       {not_tee:,}")
    print(f"skipped, already ended {skipped_done:,}")
    print(f"skipped, new catalogue {skipped_new:,}  <- protected")
    print(f"eligible to end    {len(live):,}")

    bytitle = collections.defaultdict(list)
    for it, sku, t in live:
        bytitle[norm(t)].append((it, sku, t))
    dupes = []
    for grp in bytitle.values():
        if len(grp) > 1:
            grp.sort(key=lambda x: int(x[0]))
            dupes.extend(grp[:-1])          # keep the newest copy
    dupe_items = {d[0] for d in dupes}
    rest = sorted((e for e in live if e[0] not in dupe_items), key=lambda x: int(x[0]))

    chosen = (dupes + rest)[:want]
    print(f"\nduplicate titles   {len(dupes):,}")
    print(f"longest-listed used {max(0, want - len(dupes)):,}")
    print(f"TOTAL to end       {len(chosen):,}")
    print(f"left live after    {len(live) - len(chosen):,}")
    assert len({c[0] for c in chosen}) == len(chosen)
    assert not (set(c[0] for c in chosen) & ended)

    HDR = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193),ItemID,EndCode\n"
    p = os.path.join(OUT, "EBAY_END_TSHIRTS_2.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        fh.write(HDR)
        w = csv.writer(fh, lineterminator="\n")
        for item, sku, title in chosen:
            w.writerow(["End", item, "NotAvailable"])
    print(f"\nwrote {p}  ({len(chosen):,} rows)")

    m = os.path.join(OUT, "EBAY_END_MANIFEST_2.csv")
    with open(m, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["ItemID", "SKU", "Title", "Reason"])
        for item, sku, title in chosen:
            w.writerow([item, sku, title,
                        "duplicate title already live" if item in dupe_items
                        else "longest-listed, not converting"])
    print(f"wrote {m}")


if __name__ == "__main__":
    main()
