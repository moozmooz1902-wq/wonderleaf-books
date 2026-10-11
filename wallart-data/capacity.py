#!/usr/bin/env python3
"""How many wall-art designs we can make, and what the GPU actually costs.

The seller's target: 2,000,000 listings on the big store and at least
1,000,000 on each of four others - 6,000,000 in total.

The point of this file is that a listing is NOT a GPU image. Three things
separate the two, and each one divides the bill:

  1. PALETTE IS FREE.      recolour.py maps a finished panel's lightness
                           through a different colour ramp in ~25 ms of CPU.
                           The palette axis is x3 in the catalogue and x1 on
                           the GPU. Inside the four-colourway cap the wall-art
                           branch set after measuring 89% near-duplication.
  2. GEOMETRY IS FREE.     gen_geometric.py draws the hard-edge block in code.
                           That block is 9.12% of the competitor corpus and
                           diffusion is worse at it, not better.
  3. FRAMING IS FREE.      make_sample.py renders the print sheet and all three
                           frame colours in 0.78 s per design on one CPU core.

Run with the measured seconds-per-image from the generation pod:
    python3 capacity.py 2.4
"""
import sys, itertools
sys.path.insert(0, "gen")
from prompts import TECHNIQUE, GRAMMAR_PLACE, GRAMMAR_CREATURE, PALETTE, ok

TARGET = 6_000_000
# Measured on the pod, not quoted: NVIDIA A40 48GB, RunPod secure, $0.59/hr,
# FLUX.1 schnell bf16, 4 steps, 848x1200, batch 4 -> 873 images/hour.
# A 24 GB card is not an option: the transformer alone is 11.9B params =
# 23.8 GB in bfloat16 and a 4090 OOMs in the first attention block.
GPU_HR = 0.59
IMG_HR = 873
CPU_HR = 0.64                 # 16 vCPU cpu3g, measured on this account
PROCEDURAL_SHARE = 0.0912     # hard-edge block, measured in the corpus
# 5 of the 16 sample panels carried lettering or a fake signature - a garbled
# "W ITBEY", an "N2Z1" on a seafront, a scrawled monogram on two paintings.
# guidance_scale is 0 so negative prompts do nothing; the only fix is to read
# the output and generate again. Budget for it.
GATE_REJECT = 5 / 16
N_PAL = len(PALETTE)

# variants per subject, before the palette axis is taken off the GPU
PV = sum(1 for t, g in itertools.product(TECHNIQUE, GRAMMAR_PLACE) if ok(t, g))
CV = sum(1 for t, g in itertools.product(TECHNIQUE, GRAMMAR_CREATURE) if ok(t, g))

HELD = {"UK places": (6155, PV), "creatures": (2908, CV), "botanical": (1500, CV)}


def report(img_hr=IMG_HR):
    sec_per_image = 3600 / img_hr
    print(f"GPU measured at {sec_per_image:.2f} s/image "
          f"({img_hr:,.0f} images/hour/GPU at ${GPU_HR}/hr)\n")

    print("AXES  (designs per subject = techniques x grammars x palettes)")
    print(f"   place-type subject    {PV:>3} GPU bases x {N_PAL} palettes = {PV*N_PAL:>4} designs")
    print(f"   creature-type subject {CV:>3} GPU bases x {N_PAL} palettes = {CV*N_PAL:>4} designs\n")

    print("WHAT THE SUBJECT LISTS WE ALREADY HOLD ARE WORTH")
    tot_d = tot_g = 0
    for name, (n, v) in HELD.items():
        d, g = n * v * N_PAL, n * v
        tot_d += d; tot_g += g
        print(f"   {name:<14}{n:>7,} subjects -> {d:>10,} designs  ({g:>9,} GPU images)")
    print(f"   {'TOTAL':<14}{sum(n for n,_ in HELD.values()):>7,} subjects -> "
          f"{tot_d:>10,} designs  ({tot_g:>9,} GPU images)")
    print(f"   cost of that, with the text-gate retries: "
          f"${tot_g/(1-GATE_REJECT)/img_hr*GPU_HR:,.0f}\n")

    print(f"REACHING THE {TARGET:,} TARGET")
    proc = int(TARGET * PROCEDURAL_SHARE)
    diff = TARGET - proc
    bases = diff / N_PAL
    subs = bases / PV
    gens = bases / (1 - GATE_REJECT)
    gpu_h = gens / img_hr
    cpu_h = TARGET * 0.78 / 3600
    print(f"   drawn in code (free)        {proc:>10,} designs")
    print(f"   needing diffusion           {diff:>10,} designs")
    print(f"   / {N_PAL} palettes, so GPU images   {bases:>10,.0f}")
    print(f"   + {GATE_REJECT:.0%} regenerated for text  {gens:>10,.0f}")
    print(f"   subject atoms needed        {subs:>10,.0f}  "
          f"(we hold {sum(n for n,_ in HELD.values()):,})")
    print(f"   GPU hours                   {gpu_h:>10,.0f}  = ${gpu_h*GPU_HR:,.0f}")
    print(f"   CPU hours to frame all      {cpu_h:>10,.0f}  = ${cpu_h/16*CPU_HR:,.0f}"
          f"  (16 cores)")
    print(f"   TOTAL COMPUTE               {'':>10} = "
          f"${gpu_h*GPU_HR + cpu_h/16*CPU_HR:,.0f}\n")

    print("   wall clock, by how many 48 GB GPUs are rented at once")
    for k in (1, 4, 10, 25, 50):
        print(f"      {k:>2} GPU(s): {gpu_h/k/24:>6.1f} days   "
              f"(same ${gpu_h*GPU_HR:,.0f}, just spent faster)")

    print("\nSTORAGE - Cloudflare R2 at $0.015/GB-month, egress free")
    for label, kb in (("panel, JPEG q92 (MEASURED)", 150),
                      ("+ 3 frame mockups, JPEG q90", 150 + 3 * 190)):
        gb = TARGET * kb / 1024 / 1024
        print(f"   {label:<30}{gb:>8,.0f} GB = ${gb*0.015:>7,.0f}/month")
    print("   -> keep the panel only; render the three mockups on request.")


if __name__ == "__main__":
    report(float(sys.argv[1]) if len(sys.argv) > 1 else IMG_HR)
