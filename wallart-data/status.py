#!/usr/bin/env python3
"""Where the money and the work have got to. Run this before every top-up.

The seller funds this in $100 blocks, so the only numbers that matter are:
how much of the catalogue is built, what it cost, and how far the next $100
goes. Spend comes from RunPod's own billing, not from an estimate.
"""
import json, subprocess, sys

TARGET_LISTINGS = 5_000_000
COLOURWAYS = 4
PROCEDURAL = 1_250_000                 # drawn in code, no GPU
BASES_NEEDED = (TARGET_LISTINGS - PROCEDURAL) / COLOURWAYS
REJECT = 0.12

# Measured per card on the real job, not quoted. What matters is dollars per
# image, and the cheap slow card wins: an A4500 is less than half the speed
# of a secure 4090 and still 2.2x cheaper per image.
#   card                        $/hr    gen/hr   $/image
CARDS = {
    "RTX A4500 20GB community": (0.19,    720),
    "RTX 4090 24GB secure":     (0.89,   1512),
    "RTX 4090 24GB community":  (0.34,   1601),   # when any is available
    "A40 48GB secure":          (0.59,    873),
}
RATE = CARDS["RTX 4090 24GB secure"][1]


def curl(path):
    out = subprocess.run(["curl", "-sS", "--max-time", "60",
                          f"https://rest.runpod.io/v1{path}"],
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return []


def spend(since=None):
    """RunPod ignores startDate on this endpoint - it returned every day back
    to September - so the filtering is done here instead."""
    import datetime
    since = since or datetime.datetime.utcnow().strftime("%Y-%m-%d")
    rows = curl("/billing/pods")
    if not isinstance(rows, list):
        return 0.0, {}
    byday = {}
    for r in rows:
        byday[r.get("time", "")[:10]] = byday.get(r.get("time", "")[:10], 0) + r.get("amount", 0)
    return sum(v for d, v in byday.items() if d >= since), byday


def live():
    pods = curl("/pods")
    if not isinstance(pods, list):
        return [], 0.0
    on = [p for p in pods if p.get("desiredStatus") == "RUNNING"]
    return on, sum(p.get("costPerHr", 0) for p in on)


if __name__ == "__main__":
    done = int(sys.argv[1]) if len(sys.argv) > 1 else 0   # panels in the bucket
    sp, byday = spend()
    on, burn = live()

    gens_total = BASES_NEEDED / (1 - REJECT)
    hours_total = gens_total / RATE
    print(f"TARGET {TARGET_LISTINGS:,} listings")
    print(f"   drawn in code, free      {PROCEDURAL:,}")
    print(f"   base images needed       {BASES_NEEDED:,.0f}")
    print(f"   generations (with retries){gens_total:,.0f}")
    print(f"   GPU-hours                {hours_total:,.0f}")
    print(f"\n   {'card':<28}{'$/hr':>6}{'gen/hr':>8}{'$/image':>10}"
          f"{'GPU-hrs':>9}{'TOTAL':>8}{'x $100':>8}")
    for name, (price, rate) in sorted(CARDS.items(), key=lambda kv: kv[1][0] / kv[1][1]):
        h = gens_total / rate
        print(f"   {name:<28}{price:>6.2f}{rate:>8,}{price/rate:>10.6f}"
              f"{h:>9,.0f}{'$%.0f' % (h*price):>8}{h*price/100:>8.1f}")

    print(f"\nRIGHT NOW")
    print(f"   base images in the bucket {done:,}  "
          f"({done/BASES_NEEDED:.2%} of the GPU work)")
    print(f"   listings that is          {done*COLOURWAYS:,}")
    print(f"   spent TODAY               ${sp:,.2f}")
    print(f"   spent all time on RunPod  ${sum(byday.values()):,.2f}")
    print(f"   pods running              {len(on)}  burning ${burn:.2f}/hour")
    if on:
        print("      " + ", ".join(f"{p['id']} ({p.get('name')})" for p in on))

    print(f"\nWHAT ONE $100 TOP-UP BUYS")
    for name, (price, rate) in sorted(CARDS.items(), key=lambda kv: kv[1][0] / kv[1][1]):
        h = 100 / price
        b = h * rate * (1 - REJECT)
        print(f"   {name:<28}{h:>7,.0f} GPU-hours  {b:>9,.0f} base images"
              f"  {b*COLOURWAYS:>11,.0f} listings")
