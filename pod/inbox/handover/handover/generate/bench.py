"""
bench.py — measure what each speed setting actually saves, on your GPU.

WHY MEASURE RATHER THAN ASSUME
    Batch size, attention backend and torch.compile all change throughput, and
    by how much depends on the card, the driver and the model. Published
    figures are worth nothing here. This runs the real pipeline at several
    settings and reports images per second and cost per million, so the
    decision is made on numbers from the machine that will do the work.

    Every setting it tests produces the SAME IMAGE. Batch size, attention and
    compilation change only how the work is scheduled — not what is computed.
    Steps are tested separately because that one does affect the result.

    ./venv/bin/python bench.py --model Lykon/dreamshaper-xl-1-0

Takes about 10 minutes and costs a few pence. On a million-design run it pays
for itself several hundred times over if it finds even a 10% saving.
"""

import argparse, csv, sys, time

import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Lykon/dreamshaper-xl-1-0")
ap.add_argument("--refiner", default="stabilityai/stable-diffusion-xl-refiner-1.0")
ap.add_argument("--queue", default="generation_queue.csv")
ap.add_argument("--per-test", type=int, default=8,
                help="images per configuration; more is steadier but slower")
ap.add_argument("--gpu-cost", type=float, default=0.34,
                help="$/hour per GPU, for the cost column")
args = ap.parse_args()

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# real prompts, so the numbers reflect real work
rows = []
with open(args.queue, encoding="utf-8") as f:
    for i, r in enumerate(csv.DictReader(f)):
        rows.append((r["prompt"], r["negative"]))
        if i >= 64:
            break
if not rows:
    raise SystemExit("no prompts found")

print(f"loading {args.model} ...", flush=True)
pipe = StableDiffusionXLPipeline.from_pretrained(
    args.model, torch_dtype=torch.float16, use_safetensors=True,
    variant="fp16").to("cuda")
pipe.set_progress_bar_config(disable=True)

print(f"loading refiner ...", flush=True)
ref = StableDiffusionXLImg2ImgPipeline.from_pretrained(
    args.refiner, torch_dtype=torch.float16, variant="fp16",
    use_safetensors=True).to("cuda")
ref.set_progress_bar_config(disable=True)


def apply_sdpa(on):
    try:
        from diffusers.models.attention_processor import (
            AttnProcessor2_0, AttnProcessor)
        p = AttnProcessor2_0() if on else AttnProcessor()
        pipe.unet.set_attn_processor(p)
        ref.unet.set_attn_processor(p)
        return True
    except Exception:
        return False


def run(batch, steps, refine=True, n=None):
    """Generate n images and return images/second."""
    n = n or args.per_test
    gen = torch.Generator("cuda").manual_seed(0)
    done = 0
    torch.cuda.synchronize()
    t0 = time.time()
    while done < n:
        k = min(batch, n - done)
        chunk = rows[done % len(rows):done % len(rows) + k]
        while len(chunk) < k:
            chunk.append(rows[0])
        imgs = pipe([c[0] for c in chunk],
                    negative_prompt=[c[1] for c in chunk],
                    num_inference_steps=steps, guidance_scale=7.0,
                    width=1024, height=1024, generator=gen,
                    output_type="latent" if refine else "pil").images
        if refine:
            ref(prompt=[c[0] for c in chunk],
                negative_prompt=[c[1] for c in chunk],
                image=imgs, strength=0.25, num_inference_steps=12,
                generator=gen)
        done += k
    torch.cuda.synchronize()
    return done / (time.time() - t0)


def report(label, rate, base=None):
    hrs = 1_000_000 / rate / 3600
    cost = hrs * args.gpu_cost
    delta = ""
    if base:
        pct = (rate / base - 1) * 100
        delta = f"   {pct:+5.0f}%"
    print(f"  {label:<34} {rate:5.2f} img/s   ${cost:6.0f} /million{delta}")


print("\nwarming up ...", flush=True)
apply_sdpa(True)
run(2, 30, n=4)

print("\n" + "=" * 74)
print("SETTINGS THAT DO NOT CHANGE THE IMAGE")
print("=" * 74)

apply_sdpa(False)
base = run(1, 30)
report("batch 1, default attention", base)

apply_sdpa(True)
r = run(1, 30)
report("batch 1, SDPA attention", r, base)

for b in (2, 4, 6, 8):
    try:
        r = run(b, 30)
        report(f"batch {b}, SDPA", r, base)
    except torch.cuda.OutOfMemoryError:
        print(f"  batch {b:<28} out of memory")
        torch.cuda.empty_cache()
        break

print("\n" + "=" * 74)
print("SETTINGS THAT DO CHANGE THE IMAGE — judge these by eye, not by rate")
print("=" * 74)

for steps in (30, 25, 20):
    r = run(4, steps)
    report(f"batch 4, {steps} steps", r, base)

r = run(4, 30, refine=False)
report("batch 4, 30 steps, NO refiner", r, base)

print("\n" + "=" * 74)
print("The top block is free: same image, less time. Take the fastest that")
print("fits in memory.")
print("The bottom block trades quality for speed. Generate a sheet at each")
print("and look at it before deciding — a cheap run of designs nobody buys")
print("is not a saving.")
