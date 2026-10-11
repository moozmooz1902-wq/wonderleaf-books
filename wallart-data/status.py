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
RATE = 1601                            # measured generations/hour/GPU
REJECT = 0.12


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
    for label, rate in (("community $0.34", 0.34), ("secure $0.89", 0.89)):
        print(f"      on {label:<16} ${hours_total*rate:,.0f}"
              f"   = {hours_total*rate/100:.1f} x $100 top-ups")

    print(f"\nRIGHT NOW")
    print(f"   base images in the bucket {done:,}  "
          f"({done/BASES_NEEDED:.2%} of the GPU work)")
    print(f"   listings that is          {done*COLOURWAYS:,}")
    print(f"   spent TODAY               ${sp:,.2f}")
    print(f"   spent all time on RunPod  ${sum(byday.values()):,.2f}")
    print(f"   pods running              {len(on)}  burning ${burn:.2f}/hour")
    if on:
        print("      " + ", ".join(f"{p['id']} ({p.get('name')})" for p in on))

    print(f"\nWHAT THE NEXT $100 BUYS")
    for label, rate in (("community $0.34/hr", 0.34), ("secure $0.89/hr", 0.89)):
        h = 100 / rate
        b = h * RATE * (1 - REJECT)
        print(f"   {label:<20} {h:,.0f} GPU-hours -> {b:,.0f} base images "
              f"-> {b*COLOURWAYS:,.0f} listings")
