#!/usr/bin/env python3
"""What five million listings costs, priced on what this run is ACTUALLY doing.

capacity.py prices the plan against a community RTX 4090 at 1,601
generations an hour. We have never once been given a community 4090 - all
seven probed went CUDA_DEAD, and the fleet that is really running is RTX
A4000 and RTX 4000 Ada. So this file prices the same plan against the
measured fleet instead, and is the number to quote.

Measured 13 Oct 2026, 07:25 UTC, twelve live shards:
    burn            $2.20/hour
    output          7,672 kept panels/hour (unchanged, remeasured)
    so              $0.000287 a kept panel
    spent to date   $254.06   (includes the t-shirt work and the failed
                              experiments, not just this run)
    done            604,938 base images of the 960,000 pool, counted

SPENT was last anchored by hand at $126.00 / 242,174 panels on 13 Oct. It is
carried forward, not remeasured: 604,938 - 242,174 = 362,764 panels since, at
the gated $0.000353 each, is $128.06, so $254.06 on 15 Oct 18:20 UTC. That
unit cost is not a guess - the fleet put 6,517 panels into R2 in the hour to
18:20 at $2.32/hour, which is $0.000356 a panel, within 1% of it.

RunPod has no balance endpoint on either API - every path checked, and the
GraphQL myself{} query returns null for this key. So spend is carried here
by hand and is only as fresh as the last edit. It is a floor, not a balance:
it does not know about the $100 the seller added on 13 Oct.
"""
BURN, RATE = 2.20, 7672          # $/hour and kept panels/hour, measured
SPENT, DONE = 254.06, 604_938
POOL = 960_000
COLOURWAYS, PROCEDURAL = 4, 1_250_000

# The full gate stack, measured on 219 generations through an RTX A4500,
# twice, with identical results both times because the seeds are derived
# from the SKU:
#
#     TEXT     7   3.2%    the only gate the twelve pods carry today
#     EMPTY    7   3.2%
#     PEOPLE   4   1.8%
#     EYES     1   0.5%
#     total   19   8.7%
#
# So the fleet's measured rate, which already nets out text rejections at
# about 3.2%, has to lose a further 5.5 points of keep rate AND some
# throughput: the same card does 0.216 img/s with no gates and 0.18 to 0.19
# with all four. Batching the CLIP call across the chunk did not help - the
# cost is the model's forward pass, not the per-call overhead - so it is
# taken as real.
# 0.087 was the bench figure on 219 panels of OLD material. Measured on
# the live fleet after the 12 Oct fixes, over 476 generations of the work
# that is actually LEFT: 19%, of which TEXT 12.0, EMPTY 4.4, PEOPLE 2.5.
# Text is the one still above where it should be.
# Read from done.txt and rejects.jsonl, NOT from the "reject X%" line in
# boot.log. That line is unreliable for the same reason the progress
# counter was: the log is too big to fetch whole, curl cuts it off, and the
# last line that arrives is pinned near the truncation point. It read
# 11-14% for three hours while the real figure fell. Both of these files
# are small and the division is exact:
#
#     kept 2,725  rejected 239   8.1%
#     kept 2,798  rejected 254   8.3%
#     kept 2,826  rejected 254   8.2%
GATE_KEEP = 1 - 0.082           # keep rate with all four gates, measured live
OLD_KEEP = 1 - 0.032             # keep rate already inside the measured rate
GATE_SPEED = 0.185 / 0.216       # throughput, gated against ungated

PANEL_KB = 157                   # measured over 189 real panels
R2_PER_GB_MONTH = 0.015
CPU_CORE_HOURS, CPU_CORES, CPU_PER_HR = 557, 16, 0.64
SWEEP_GPU_HOURS = 14             # the owed text sweep over the finished set


def main():
    per = BURN / RATE
    per_gated = per / GATE_SPEED / (GATE_KEEP / OLD_KEEP)
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
    print(f"   with all four gates    ${per_gated:.6f} a panel  "
          f"({(1-GATE_SPEED):.0%} slower, keep {GATE_KEEP:.1%} not {OLD_KEEP:.1%})\n")
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
        p = price / rate / GATE_SPEED / (GATE_KEEP / OLD_KEEP)
        print(f"      {name:<36} ${SPENT + left * p + cpu + sweep:>7.0f}")


if __name__ == "__main__":
    main()
