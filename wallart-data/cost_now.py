#!/usr/bin/env python3
"""What five million listings costs, priced on what this run is ACTUALLY doing.

capacity.py prices the plan against a community RTX 4090 at 1,601
generations an hour. We have never once been given a community 4090 - all
seven probed went CUDA_DEAD, and the fleet that is really running is RTX
A4000 and RTX 4000 Ada. So this file prices the same plan against the
measured fleet instead, and is the number to quote.

Measured 11 Oct 2026, 22:50 UTC, twelve live shards:
    burn            $2.12/hour
    output          7,672 kept panels/hour
    so              $0.000276 a kept panel
    spent to date   $52.64   (includes the t-shirt work and the failed
                              experiments, not just this run)
    done            41,599 base images of the 960,000 pool
"""
BURN, RATE = 2.12, 7672          # $/hour and kept panels/hour, measured
SPENT, DONE = 52.64, 41_599
POOL = 960_000
COLOURWAYS, PROCEDURAL = 4, 1_250_000

# Two gates were added after these twelve pods started, so they are not in
# the measured rate. Both throw work away on purpose and both are worth it.
EMPTINESS = 0.050                # measured on the 141-panel eval: 7 of 141
CLIPPED_TEXT = 0.010             # the straddling-title class, estimated

PANEL_KB = 157                   # measured over 189 real panels
R2_PER_GB_MONTH = 0.015
CPU_CORE_HOURS, CPU_CORES, CPU_PER_HR = 557, 16, 0.64
SWEEP_GPU_HOURS = 14             # the owed text sweep over the finished set


def main():
    per = BURN / RATE
    per_gated = per * (1 + EMPTINESS + CLIPPED_TEXT)
    left = POOL - DONE
    gpu_left = left * per_gated
    cpu = CPU_CORE_HOURS / CPU_CORES * CPU_PER_HR
    sweep = SWEEP_GPU_HOURS * (BURN / 12)
    storage = POOL * PANEL_KB * 1024 / 1e9 * R2_PER_GB_MONTH
    total = SPENT + gpu_left + cpu + sweep

    print(f"TARGET {POOL * COLOURWAYS + PROCEDURAL:,} listings")
    print(f"   {PROCEDURAL:,} drawn in code, {POOL * COLOURWAYS:,} from "
          f"{POOL:,} base images at {COLOURWAYS} colourways\n")
    print(f"   measured now          ${per:.6f} a panel  "
          f"({BURN:.2f}/hr over {RATE:,}/hr)")
    print(f"   with the two new gates ${per_gated:.6f} a panel  "
          f"(+{EMPTINESS:.0%} empty, +{CLIPPED_TEXT:.0%} clipped text)\n")
    print(f"   already spent                       ${SPENT:>7.2f}")
    print(f"   GPU for the remaining {left:,}     ${gpu_left:>7.2f}")
    print(f"   CPU stage, {CPU_CORE_HOURS} core-hours           ${cpu:>7.2f}")
    print(f"   the owed text sweep                 ${sweep:>7.2f}")
    print(f"   {'-' * 44}")
    print(f"   TOTAL TO FINISH FIVE MILLION        ${total:>7.2f}")
    print(f"\n   storage, {POOL * PANEL_KB * 1024 / 1e9:.0f} GB of panels        "
          f"${storage:>7.2f}/month (not in the total)")
    print(f"\n   what is left to spend          ${total - SPENT:>7.2f}"
          f"  = {(total - SPENT) / 100:.1f} top-ups of $100")
    print(f"   at the current rate            "
          f"{left / RATE / 24:.1f} days on twelve shards")
    print("\n   if the cards change")
    for name, price, rate in (("community 4090 $0.34, 1,601/hr", 0.34, 1601),
                              ("RTX A4500 $0.19, 776/hr", 0.19, 776),
                              ("RTX A4000 $0.17, 576/hr  <- today", 0.17, 576),
                              ("secure 4090 $0.89, 1,394/hr", 0.89, 1394)):
        p = price / rate * (1 + EMPTINESS + CLIPPED_TEXT)
        print(f"      {name:<36} ${SPENT + left * p + cpu + sweep:>7.0f}")


if __name__ == "__main__":
    main()
