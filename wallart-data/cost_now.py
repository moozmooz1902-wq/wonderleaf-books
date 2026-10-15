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
    spent to date   anchored, then carried forward - see below
    done            pass --panels from r2_count_stores.py

SPEND IS NO LONGER EDITED BY HAND, because editing it by hand is how it went
wrong. The anchor below was verified once; everything after it is computed
from the panel count you pass in:

    spent = ANCHOR_SPENT + (panels - ANCHOR_DONE) * gated cost per panel

Run it as `cost_now.py --panels 615809`, taking the number from
r2_count_stores.py. With no --panels it reports the anchor itself and says
so, rather than quietly presenting a stale figure as current.

Why: the anchor sat at $126.00 / 242,174 panels from 13 Oct until 15 Oct
18:20, by which time 604,938 panels were done. It therefore reported $278
left to spend when the real figure was $150 - a $128 error, in the direction
of looking cheaper, in the one number used to tell the seller how much a
top-up needs to be. Re-anchoring by hand every hour is not a fix; a file
that cannot go stale is.

The unit cost is not a guess. In the hour to 18:20 the fleet put 6,517
panels into R2 at $2.32/hour, which is $0.000356 a panel, within 1% of the
gated $0.000353 used here.

RunPod has no balance endpoint on either API - every path checked, and the
GraphQL myself{} query returns null for this key. This is SPEND, a floor,
never a balance: it does not know about the $100 the seller added on 13 Oct,
and the balance is theirs to read.
"""
BURN, RATE = 2.20, 7672          # $/hour and kept panels/hour, measured
# Verified once, by hand, and not to be edited to "catch up" - that is what
# --panels is for. ANCHOR_SPENT includes the t-shirt work and the failed
# experiments, not just this run.
ANCHOR_SPENT, ANCHOR_DONE = 254.06, 604_938
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
# The owed text sweep. This was 14, which priced sweeping the whole finished
# catalogue. It only has to cover panels written before 11 Oct 22:00, when the
# text gate still read the cropped image - 35,925 of them, counted from
# LastModified by r2_age_histogram.py on 15 Oct, and that set cannot grow.
# 35,925 at 50 ms is 0.50 GPU-hours, so this line was overstating the total by
# about $2.50 for days on a population nobody had counted.
SWEEP_GPU_HOURS = 0.5


def main():
    import sys
    per = BURN / RATE
    per_gated = per / GATE_SPEED / (GATE_KEEP / OLD_KEEP)

    if "--panels" in sys.argv:
        DONE = int(sys.argv[sys.argv.index("--panels") + 1].replace(",", ""))
    else:
        DONE = ANCHOR_DONE
    since = DONE - ANCHOR_DONE
    SPENT = ANCHOR_SPENT + since * per_gated
    if since:
        print(f"spend: ${ANCHOR_SPENT:.2f} anchored at {ANCHOR_DONE:,} panels, "
              f"plus {since:,} since at ${per_gated:.6f} = ${SPENT:.2f}")
    else:
        print(f"spend: ${ANCHOR_SPENT:.2f} at the anchor, {ANCHOR_DONE:,} "
              f"panels. Pass --panels from r2_count_stores.py for today's.")
    if since < 0:
        print(f"  NOTE: {-since:,} FEWER panels than the anchor. The anchor is "
              f"wrong, or this is a different catalogue - check before quoting.")
    print()

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
