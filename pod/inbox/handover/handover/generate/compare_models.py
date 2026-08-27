"""
compare_models.py — is Lightning actually good enough for shirts?

Generates the SAME designs twice, once with the current setup and once with
SDXL Lightning, puts both on shirts, and lays them out in pairs so the
question can be settled by looking rather than by argument.

    ./venv/bin/python compare_models.py --n 12

Writes compare.jpg — left column current, right column Lightning, same
design on each row. Also reports the reject rate for each, since a model
that renders backgrounds differently can quietly change how many designs
survive QC.

Takes about 15 minutes and a few pence of GPU. Worth it before committing
476,000 designs either way.
"""

import argparse, csv, gc, math, os, subprocess, sys, time

import numpy as np
import torch
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=12, help="designs to compare")
ap.add_argument("--queue", default="generation_queue.csv")
ap.add_argument("--model", default="Lykon/dreamshaper-xl-1-0")
ap.add_argument("--lightning-steps", type=int, default=4)
ap.add_argument("--size", type=int, default=1024)
args = ap.parse_args()

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

rows = []
with open(args.queue, encoding="utf-8") as fh:
    for i, r in enumerate(csv.DictReader(fh)):
        rows.append(r)
        if len(rows) >= args.n:
            break
if not rows:
    raise SystemExit("no prompts in the queue")

print(f"comparing {len(rows)} designs\n")


def run(tag, build):
    """Generate every prompt with one pipeline, return paths and timing."""
    pipe = build()
    pipe.set_progress_bar_config(disable=True)
    os.makedirs(tag, exist_ok=True)
    out = []
    t0 = time.time()
    for i, r in enumerate(rows):
        kw = dict(prompt=r["prompt"], negative_prompt=r["negative"],
                  width=args.size, height=args.size)
        if tag == "lightning":
            kw.update(num_inference_steps=args.lightning_steps,
                      guidance_scale=0.0)
        else:
            kw.update(num_inference_steps=30, guidance_scale=7.0)
        img = pipe(**kw).images[0]
        p = os.path.join(tag, f"{i:02d}.png")
        img.save(p)
        out.append(p)
        print(f"  {tag}: {i+1}/{len(rows)}", flush=True)
    el = time.time() - t0
    del pipe
    gc.collect()
    torch.cuda.empty_cache()
    return out, el


def build_current():
    from diffusers import StableDiffusionXLPipeline
    print(f"loading {args.model}")
    return StableDiffusionXLPipeline.from_pretrained(
        args.model, torch_dtype=torch.float16, variant="fp16",
        use_safetensors=True).to("cuda")


def build_lightning():
    from diffusers import (StableDiffusionXLPipeline, UNet2DConditionModel,
                           EulerDiscreteScheduler)
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file
    B = "stabilityai/stable-diffusion-xl-base-1.0"
    ckpt = f"sdxl_lightning_{args.lightning_steps}step_unet.safetensors"
    print(f"loading SDXL Lightning {args.lightning_steps}-step")
    unet = UNet2DConditionModel.from_config(B, subfolder="unet").to(
        "cuda", torch.float16)
    unet.load_state_dict(
        load_file(hf_hub_download("ByteDance/SDXL-Lightning", ckpt),
                  device="cuda"))
    p = StableDiffusionXLPipeline.from_pretrained(
        B, unet=unet, torch_dtype=torch.float16, variant="fp16",
        use_safetensors=True).to("cuda")
    p.scheduler = EulerDiscreteScheduler.from_config(
        p.scheduler.config, timestep_spacing="trailing")
    return p


cur, t_cur = run("current", build_current)
lit, t_lit = run("lightning", build_lightning)

# --- put both through the real print pipeline ----------------------------
import dtf
import photo_mockup as PM

def shirts(paths, tag):
    made, flagged = [], 0
    os.makedirs(f"{tag}_mock", exist_ok=True)
    for p in paths:
        pr = p.replace(".png", "_print.png")
        try:
            st = dtf.to_dtf(p, pr)
        except Exception as e:
            print(f"  {p}: {str(e)[:50]}")
            continue
        if st.get("border", 0) > dtf.BORDER_MAX:
            flagged += 1
        m = os.path.join(f"{tag}_mock", os.path.basename(p).replace(".png", ".jpg"))
        PM.build(pr, m)
        made.append(m)
    return made, flagged


m_cur, f_cur = shirts(cur, "current")
m_lit, f_lit = shirts(lit, "lightning")

# --- the sheet ------------------------------------------------------------
n = min(len(m_cur), len(m_lit))
CELL = 420
sheet = Image.new("RGB", (CELL * 2 + 30, CELL * n + 60), (255, 255, 255))
for i in range(n):
    sheet.paste(Image.open(m_cur[i]).resize((CELL, CELL)), (0, 60 + CELL * i))
    sheet.paste(Image.open(m_lit[i]).resize((CELL, CELL)),
                (CELL + 30, 60 + CELL * i))
sheet.save("compare.jpg", quality=93)

print()
print("=" * 60)
print(f"  LEFT  column: current   {t_cur/len(rows):.1f}s each   "
      f"{f_cur}/{len(cur)} flagged")
print(f"  RIGHT column: lightning {t_lit/len(rows):.1f}s each   "
      f"{f_lit}/{len(lit)} flagged")
print(f"  speed: {t_cur/max(t_lit,0.01):.1f}x faster")
print("=" * 60)
print()
print("  Open compare.jpg. Same design on each row.")
print("  If the right column is as good, Lightning saves about $200 on this")
print("  batch. If it is not, say so and we keep the current setup — the")
print("  saving is not worth designs that sell less.")
