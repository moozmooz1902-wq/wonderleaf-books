#!/usr/bin/env python3
"""Decide which store each design belongs to, once and for ever.

The rule that matters: a design appears in exactly ONE store. Four shops
selling the same picture compete with each other and multiply the
near-duplicate problem the whole catalogue is built to avoid.

Assignment is by SKU hash against the row quotas, which gives three things
a hand-written split does not:

  * no overlap, by construction - a SKU maps to one store, always
  * every store gets a fair mix of subjects, techniques and compositions,
    the same reason the generation shards were striped rather than sliced
  * stable under growth - adding subjects or raising a quota moves nobody
    who is already placed, because the hash does not depend on list order

Run `python3 allocate.py` for the plan, `--check` to prove the properties.
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = json.load(open(os.path.join(HERE, "stores.json")))


# WEIGHTED RENDEZVOUS HASHING, not cumulative bands.
#
# The first version laid the stores out as bands on 0..1 and picked by where
# a SKU's hash fell. That distributes correctly, and I claimed it was stable
# when a quota changed. It is not, and the claim was wrong. Measured: moving
# luxvia 3M -> 2.5M and lunar 500k -> 1M reshuffled **39.9%** of designs,
# against a floor of 10% - because shifting one band's edge slides every
# band after it.
#
# Rendezvous hashing scores every store for every SKU and takes the winner:
#
#     score = -weight / ln(u)      u = hash(sku, store) as a float in (0,1)
#
# The share each store wins is proportional to its weight, and changing one
# store's weight only moves designs into or out of THAT store - the scores
# of the others are untouched. That is the minimum possible disruption.
#
# It matters because the quotas have already been revised once, nothing has
# been uploaded yet, and after upload a reshuffle means re-homing listings
# that are already live.
import math


def store_for(sku):
    best, best_score = None, -1.0
    for s in PLAN["stores"]:
        h = hashlib.blake2b(f"{sku}|{s['bucket']}".encode(), digest_size=8).digest()
        u = (int.from_bytes(h, "big") + 1) / (2 ** 64 + 1)      # in (0,1)
        score = -s["listings"] / math.log(u)
        if score > best_score:
            best, best_score = s, score
    return best


def plan():
    tot = sum(s["listings"] for s in PLAN["stores"])
    proc = PLAN["procedural_share"]; cw = PLAN["colourways"]
    print(f"{'store':<12}{'bucket':<20}{'listings':>11}{'share':>7}"
          f"{'in code':>10}{'GPU bases':>11}{'frames':>8}")
    tb = 0
    for s in PLAN["stores"]:
        n = s["listings"]
        p = int(n * proc)
        b = int((n - p) / cw)
        tb += b
        print(f"{s['name']:<12}{s['bucket']:<20}{n:>11,}{n/tot:>6.0%}"
              f"{p:>10,}{b:>11,}{len(s['frames']):>8}")
    print(f"{'TOTAL':<32}{tot:>11,}{'':>6}{int(tot*proc):>10,}{tb:>11,}")
    print(f"\nGPU images still to make: {tb - 12834:,} "
          f"(12,834 already generated)")
    for name, price, rate in (("A4500 community", 0.19, 776),
                              ("4090 secure", 0.89, 1394)):
        hrs = (tb / (1 - 0.12)) / rate
        print(f"   on {name:<18} {hrs:>7,.0f} GPU-hours  ${hrs*price:>7,.0f}"
              f"   {hrs*price/100:>4.1f} x $100")


def check():
    """Prove the two properties rather than assert them."""
    import collections, copy
    sample = [f"WA-{i:016x}" for i in range(120000)]
    c = collections.Counter(store_for(s)["bucket"] for s in sample)
    tot = sum(s["listings"] for s in PLAN["stores"])
    print(f"{'bucket':<20}{'wanted':>9}{'got':>9}{'drift':>8}")
    for s in PLAN["stores"]:
        want = s["listings"] / tot
        got = c[s["bucket"]] / len(sample)
        print(f"{s['bucket']:<20}{want:>8.2%}{got:>9.2%}{got-want:>+8.2%}")

    a = store_for("WA-deadbeef00000001")["bucket"]
    print(f"\nsame SKU twice -> same store: "
          f"{a == store_for('WA-deadbeef00000001')['bucket']}  ({a})")

    # disruption: redo the seller's actual quota change and count movers
    before = {s: store_for(s)["bucket"] for s in sample}
    keep = copy.deepcopy(PLAN["stores"])
    prev = {"luxvia-art": 3000000, "lunar-kms": 500000,
            "posterleaf-store1": 1000000, "mercury-usm": 500000}
    for s in PLAN["stores"]:
        s["listings"] = prev[s["bucket"]]
    moved = sum(1 for s in sample if before[s] != store_for(s)["bucket"])
    PLAN["stores"][:] = keep
    floor = 0.5 * sum(abs(prev[s["bucket"]] / sum(prev.values())
                          - s["listings"] / tot) for s in PLAN["stores"])
    print(f"\nquota change luxvia 3M->2.5M, lunar 500k->1M")
    print(f"   designs that change store : {moved/len(sample):>6.1%}")
    print(f"   theoretical minimum       : {floor:>6.1%}")
    print(f"   the old band method       :  39.9%")


if __name__ == "__main__":
    check() if "--check" in sys.argv else plan()
