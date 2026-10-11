#!/usr/bin/env python3
"""What 5,000,000 wall-art listings cost to build. Every rate is measured.

The seller's target, 11 Oct 2026:
    main store      3,000,000
    four others       500,000 each
    total           5,000,000      under $500

MEASURED, not quoted (see first_real_sample_and_measured_cost.md and
the bench run of 11 Oct):

    RTX 4090 + NF4, 704x1008, batch 4   1,782 generations/hour   16.1 GB peak
    with the gate AND the 10% crop      1,601 generations/hour   measured
    848x1328 -> 848x1200, same config   1,118 generations/hour   43% dearer
    text rejection, clean subject mix    7.7%  (was 31% before the fixes)
    text rejection, adversarial mix     15.8%  (peopled towns, portraits)
    RTX 4090 + NF4, 848x1200, batch 4   1,295 generations/hour   18.4 GB peak
    A40 48GB bf16,  848x1200, batch 4     873 generations/hour
    RunPod price    4090 community $0.34/hr   4090 secure $0.89/hr

    procedural line design  0.156 s   recolour a panel   0.085 s
    compose + edge check    0.062 s   listing mockup     0.221 s

Batch 8 is not faster than batch 4 on either size; it only uses more memory.
A 24 GB card cannot run bf16 at all - the transformer alone is 23.8 GB - so
NF4 is not an optimisation here, it is the only way onto the cheap hardware.
"""
TARGET = {"main store": 3_000_000, "store 2": 500_000, "store 3": 500_000,
          "store 4": 500_000, "store 5": 500_000}
TOTAL = sum(TARGET.values())

# Everything is generated 11% taller than needed and the bottom tenth is
# thrown away: measured over 129 panels, 96% of the fake signatures sit below
# 90% of the panel height. These rates are WITH that overhead and with the
# OCR gate running, so they are the real production rates.
RATE = {"704x1120 -> 704x1008": 1601, "848x1328 -> 848x1200": 1118}
# 848 was tested head to head against 704 on 24 high-risk bird portraits at
# the same seeds. It costs 43% more per image and did not fix a single eye,
# so the whole catalogue is generated at 704.
SHARE_704 = 1.00
PRICE = {"community 4090": 0.34, "secure 4090": 0.89, "mixed 75/25": 0.4775}
CPU_HR, CPU_CORES = 0.64, 16

PROC_LINE, PROC_GEO = 1_000_000, 250_000      # drawn in code, no GPU at all
COLOURWAYS = 4                 # the cap the wall-art branch set after measuring
                               # store 1 at 89% near-duplicates
SEC = {"line": 0.156, "recolour": 0.085, "compose": 0.062, "mockup": 0.221,
       "declutter": 0.080}      # per BASE image, not per listing
KB = {"panel": 120, "proc_panel": 150, "listing": 190}
R2 = 0.015                     # $/GB/month, egress free

EFF_RATE = 1 / (SHARE_704 / RATE["704x1120 -> 704x1008"]
                + (1 - SHARE_704) / RATE["848x1328 -> 848x1200"])


def report(reject):
    proc = PROC_LINE + PROC_GEO
    diff = TOTAL - proc
    bases = diff / COLOURWAYS
    gens = bases / (1 - reject)
    gpu_h = gens / EFF_RATE

    cpu_s = (proc * SEC["line"] + diff * SEC["recolour"]
             + bases * SEC["declutter"]
             + TOTAL * (SEC["compose"] + SEC["mockup"]))
    cpu_h = cpu_s / 3600
    cpu_cost = cpu_h / CPU_CORES * CPU_HR

    print(f"\n=== text-gate rejection {reject:.1%} "
          f"(effective {EFF_RATE:,.0f} generations/hour/GPU) ===")
    print(f"  drawn in code, free        {proc:>10,}  "
          f"({PROC_LINE:,} line + {PROC_GEO:,} geometric)")
    print(f"  from diffusion             {diff:>10,}")
    print(f"  / {COLOURWAYS} colourways (free)      {bases:>10,.0f}  base images")
    print(f"  + regenerated for text     {gens:>10,.0f}  generations")
    print(f"  GPU-hours                  {gpu_h:>10,.0f}")
    for name, p in PRICE.items():
        print(f"      on {name:<16} ${gpu_h*p:>8,.0f}"
              f"   + ${cpu_cost:,.0f} CPU  =  ${gpu_h*p + cpu_cost:>8,.0f}")
    print(f"  CPU-hours (1 core)         {cpu_h:>10,.0f}  "
          f"= {cpu_h/CPU_CORES:,.0f} h on a {CPU_CORES}-core pod")
    for k in (6, 12, 25):
        print(f"      wall clock on {k:>2} GPUs:  {gpu_h/k/24:>5.1f} days")
    return gpu_h


print(f"TARGET {TOTAL:,} listings across {len(TARGET)} stores")
for k, v in TARGET.items():
    print(f"   {k:<12}{v:>10,}")
for r in (0.12, 0.16):
    report(r)

print("\n=== storage, Cloudflare R2 ===")
proc, diff = PROC_LINE + PROC_GEO, TOTAL - (PROC_LINE + PROC_GEO)
g_panel = (diff * KB["panel"] + proc * KB["proc_panel"]) / 1024 / 1024
g_list = TOTAL * KB["listing"] / 1024 / 1024
print(f"   panels only                 {g_panel:>8,.0f} GB = ${g_panel*R2:>6,.0f}/month")
print(f"   + a listing photo each      {g_list:>8,.0f} GB = ${g_list*R2:>6,.0f}/month")
print(f"   -> keep the panels, draw the three frame colours on request: "
      f"${g_panel*R2:,.0f}/month")

print("\n=== subject atoms needed ===")
PV, CV = 47, 38                # bases per subject, after dropping G6_poster
bases = (TOTAL - proc) / COLOURWAYS
avg = 0.55 * PV + 0.45 * CV
print(f"   {bases:,.0f} base images / {avg:.0f} per subject = "
      f"{bases/avg:,.0f} subjects")
print(f"   held today 10,563;  identified and IP-free 33,900")
