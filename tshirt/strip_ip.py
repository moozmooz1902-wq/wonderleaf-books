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

    python3 strip_ip.py EBAY_part*.csv
"""
import csv, sys, os
from collections import Counter
import ip_risk

csv.field_size_limit(10 ** 7)


def strip(path, outdir="clean"):
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
                skipping = bool(m)
                if skipping:
                    hits[m.group(0).lower()] += 1
                    dropped += 1
                else:
                    kept += 1
            if not skipping:
                w.writerow(row)
    return kept, dropped, hits, out


if __name__ == "__main__":
    tot_k = tot_d = 0
    all_hits = Counter()
    for p in sys.argv[1:]:
        k, d, h, out = strip(p)
        all_hits += h
        tot_k += k; tot_d += d
        print(f"{os.path.basename(p)}  kept {k:>6}  dropped {d:>4}  -> {out}")
    print(f"\n{tot_k} listings kept, {tot_d} dropped ({tot_d/(tot_k+tot_d):.2%})")
    for k, v in all_hits.most_common():
        print(f"  {v:>4}  {k}")
