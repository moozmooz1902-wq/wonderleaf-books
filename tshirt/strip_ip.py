#!/usr/bin/env python3
"""Remove listings that name something somebody else owns, before they go up.

0.33% of the catalogue - 389 listings - carries a trademark, a model name or
a real person's likeness. They are there because the subject bank was mined
from the collaborator's live catalogue, so they arrive looking like proven
sellers: Banksy, King Charles, Che Guevara, Spitfire, Ducati, Land Rover.

eBay runs the VeRO programme. A rights owner reports a listing, it comes
down, and a run of removals puts the account itself at risk. The M12K
account already carries a selling limit, which means it has less room than
any of the others to absorb that. 389 listings is not worth it.

A listing is a parent row plus its five size variations, so a match on the
parent drops the whole block.

A match on the eBay row alone is not enough. 52 of the 389 name the brand
only in the design brief - the title says "Classic British Off Roader" and
the artwork is a Land Rover. The picture infringes exactly as the words
would, so the SKUs are worked out from the catalogue and dropped by label as
well as by text.

    python3 strip_ip.py --skus risky_skus.txt EBAY_part*.csv
"""
import csv, sys, os
from collections import Counter
import ip_risk

csv.field_size_limit(10 ** 7)


def strip(path, outdir="clean", skus=frozenset()):
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, os.path.basename(path))
    kept = dropped = 0
    hits = Counter()
    with open(path, newline="", encoding="utf-8") as f, \
         open(out, "w", newline="", encoding="utf-8") as g:
        r, w = csv.reader(f), csv.writer(g)
        w.writerow(next(r))
        skipping = False
        for row in r:
            if row and row[0] == "Add":            # a new listing starts here
                m = ip_risk.RISK.search(" ".join(row))
                by_sku = len(row) > 1 and row[1] in skus
                skipping = bool(m) or by_sku
                if skipping:
                    hits[m.group(0).lower() if m else "artwork only"] += 1
                    dropped += 1
                else:
                    kept += 1
            if not skipping:
                w.writerow(row)
    return kept, dropped, hits, out


if __name__ == "__main__":
    args = sys.argv[1:]
    skus = frozenset()
    if args and args[0] == "--skus":
        skus = frozenset(l.strip() for l in open(args[1]) if l.strip())
        args = args[2:]
        print(f"{len(skus)} SKUs listed as risky")
    tot_k = tot_d = 0
    all_hits = Counter()
    for p in args:
        k, d, h, out = strip(p, skus=skus)
        all_hits += h
        tot_k += k; tot_d += d
        print(f"{os.path.basename(p)}  kept {k:>6}  dropped {d:>4}  -> {out}")
    print(f"\n{tot_k} listings kept, {tot_d} dropped ({tot_d/(tot_k+tot_d):.2%})")
    for k, v in all_hits.most_common():
        print(f"  {v:>4}  {k}")
