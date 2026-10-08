#!/usr/bin/env python3
"""What generating N wall-art images actually costs on rented GPUs.

Throughput is the weak number in all of this: published FLUX.1 schnell figures
conflict badly (community reports ~1.8 s/image on a 4090 against JarvisLabs'
"6-10 seconds"), so three scenarios are given rather than one, and the cheap and
dear ends are both shown. Everything else - rental price, storage price - is
quoted from a published price list.
"""
RATES = {                      # USD per GPU-hour, RunPod published pricing
    "RTX 4090 (community)": 0.34,
    "RTX 4090 (secure)":    0.69,
    "L40S":                 0.86,
    "A100 80GB":            1.64,
}
# seconds per 1-megapixel image at 4 steps, the three plausible cases
SPEED = {"optimistic (2 s)": 2.0, "middle (4 s)": 4.0, "pessimistic (8 s)": 8.0}
SCALES = [100_000, 500_000, 1_000_000, 2_500_000]

print("GENERATION COST - FLUX.1 schnell, 4 steps, ~1 MP, one GPU-second each\n")
print(f"{'designs':>10} {'speed':<18} {'GPU-hours':>10} "
      + " ".join(f"{k:>22}" for k in RATES))
for n in SCALES:
    for sname, sec in SPEED.items():
        gh = n * sec / 3600
        row = " ".join(f"{'$%.0f' % (gh*r):>22}" for r in RATES.values())
        print(f"{n:>10,} {sname:<18} {gh:>10,.0f} {row}")
    print()

print("WALL-CLOCK on the cheap option (RTX 4090 community, middle speed)")
for n in SCALES:
    gh = n * 4.0 / 3600
    for gpus in (1, 5, 20):
        print(f"   {n:>9,} designs on {gpus:>2} GPU(s): {gh/gpus/24:>6.1f} days  "
              f"(${gh*0.34:,.0f} of GPU time)")
    print()

print("STORAGE - Cloudflare R2, $0.015/GB-month, no egress fee")
for n in SCALES:
    listing = n * 0.4 / 1024          # ~400 KB listing JPEG at 2000x2000
    master  = n * 45  / 1024          # ~45 MB print master at A2 300dpi
    print(f"   {n:>9,}: listing images {listing:>7,.0f} GB = ${listing*0.015:>8,.0f}/mo"
          f" | pre-rendered masters {master:>8,.0f} GB = ${master*0.015:>9,.0f}/mo")
print("\n   -> store the recipe plus a compressed master and render the print file")
print("      on order; pre-rendering masters costs ~100x more for files that are")
print("      almost never fetched.")

print("\nUPSCALING (needed for A2 at 300 dpi = 4961 x 7015)")
for n in SCALES:
    gh = n * 6.0 / 3600               # ~6 s/image for a 4x ESRGAN-class pass
    print(f"   {n:>9,}: {gh:>8,.0f} GPU-hours = ${gh*0.34:>7,.0f} on a 4090")
print("\n   -> only upscale a design once it SELLS. Upscaling the whole catalogue")
print("      up front doubles the bill for files nobody has ordered.")
