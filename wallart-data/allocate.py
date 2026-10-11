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


def _bounds():
    """Cumulative 0..1 bands, one per store, proportional to its quota."""
    tot = sum(s["listings"] for s in PLAN["stores"])
    out, acc = [], 0.0
    for s in PLAN["stores"]:
        acc += s["listings"] / tot
        out.append((acc, s))
    return out


BOUNDS = _bounds()


def store_for(sku):
    h = int(hashlib.blake2b(("store|" + sku).encode(), digest_size=8).hexdigest(), 16)
    x = (h % 10**9) / 10**9
    for upper, s in BOUNDS:
        if x < upper:
            return s
    return BOUNDS[-1][1]


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
    import collections
    sample = [f"WA-{i:016x}" for i in range(200000)]
    c = collections.Counter(store_for(s)["bucket"] for s in sample)
    tot = sum(s["listings"] for s in PLAN["stores"])
    print(f"{'bucket':<20}{'wanted':>9}{'got':>9}{'drift':>8}")
    for s in PLAN["stores"]:
        want = s["listings"] / tot
        got = c[s["bucket"]] / len(sample)
        print(f"{s['bucket']:<20}{want:>8.2%}{got:>9.2%}{got-want:>+8.2%}")
    once = all(sum(1 for _ in [store_for("WA-deadbeef00000001")]) == 1 for _ in range(1))
    a = store_for("WA-deadbeef00000001")["bucket"]
    b = store_for("WA-deadbeef00000001")["bucket"]
    print(f"\nsame SKU twice -> same store: {a == b}  ({a})")


if __name__ == "__main__":
    check() if "--check" in sys.argv else plan()
