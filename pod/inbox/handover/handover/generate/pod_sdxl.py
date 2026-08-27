"""
pod_sdxl.py — SDXL generation on a RunPod GPU pod.

The quality pipeline, not a single pass. The earlier attempt failed because it
used base SDXL at 768px with no refiner and no checkpoint — four compounding
mistakes. This fixes all four:

    1024x1024 native      SDXL was trained at this size; 768 degrades output
    community checkpoint  base SDXL is a generalist and looks it
    refiner at 0.25       the pass that sharpens edges and detail
    2x upscale            final files at print resolution

Everything streams to R2 as it is produced and is deleted locally, so the pod
can die at any point without losing work and the disk cannot fill.

    export R2_REMOTE=r2:tshirt-mockups
    python3 pod_sdxl.py --limit 20            # test first, always
    nohup python3 pod_sdxl.py > gen.log 2>&1 &
"""

import argparse, csv, os, subprocess, sys, time

import numpy as np
import torch
from PIL import Image
from diffusers import (StableDiffusionXLPipeline,
                       StableDiffusionXLImg2ImgPipeline)

ap = argparse.ArgumentParser()
ap.add_argument("--queue", default="generation_queue.csv")
ap.add_argument("--model", default="stabilityai/stable-diffusion-xl-base-1.0",
                help="HF id or a local .safetensors from CivitAI")
ap.add_argument("--refiner", default="stabilityai/stable-diffusion-xl-refiner-1.0")
ap.add_argument("--no-refiner", action="store_true")
ap.add_argument("--limit", type=int)
ap.add_argument("--start", type=int, default=0)
ap.add_argument("--tag", default="w0")
ap.add_argument("--batch", type=int, default=4,
                help="images per forward pass. Larger keeps the GPU busier "
                     "and costs nothing in quality — each image is generated "
                     "identically, they are just computed together")
ap.add_argument("--compile", action="store_true",
                help="torch.compile the UNet. Costs 2-4 minutes at startup, "
                     "then runs faster for the rest of the job. Worth it on a "
                     "long run, pointless on a short one")
ap.add_argument("--bench", type=int, default=0,
                help="generate N images, report the rate, and exit. Use this "
                     "to measure settings on the actual GPU before committing")
ap.add_argument("--lightning", action="store_true",
                help="use ByteDance SDXL-Lightning: ~8x faster, and it sets "
                     "steps/cfg/scheduler itself. Ignores --model")
ap.add_argument("--lightning-steps", type=int, default=4, choices=[2, 4, 8],
                help="Lightning variant. 4 is the usual balance; 8 is closer "
                     "to full SDXL if 4 loses detail you care about")
ap.add_argument("--jpeg", action="store_true",
                help="save q95 JPEG instead of PNG. ~5x smaller, invisible at "
                     "print size. The single biggest lever on running cost "
                     "once generation is cheap")
ap.add_argument("--qc", action="store_true",
                help="reject light-background designs ON THE POD, before they "
                     "are uploaded. They would only be discarded later anyway")
ap.add_argument("--qc-max", type=float, default=90,
                help="border brightness above which a design is rejected; "
                     "matches BORDER_MAX in dtf.py")
ap.add_argument("--steps", type=int, default=30)
ap.add_argument("--cfg", type=float, default=7.0)
ap.add_argument("--size", type=int, default=1024,
                help="native generation size — leave at 1024, SDXL is trained there")
ap.add_argument("--hires", type=int, default=1536,
                help="final size via img2img upscale; 0 disables")
ap.add_argument("--hires-denoise", type=float, default=0.35)
args = ap.parse_args()

OUT = f"raw_{args.tag}"
os.makedirs(OUT, exist_ok=True)

# Push finished images to R2 every N designs, then delete locally. Without
# this the disk fills and the run dies — which is exactly what happened before.
R2_REMOTE = os.environ.get("R2_REMOTE", "")
FLUSH_EVERY = int(os.environ.get("R2_FLUSH_EVERY", "200"))
os.environ.setdefault("HF_HOME", "/workspace/hf_cache")


def push_to_r2():
    if not R2_REMOTE or not os.path.isdir(OUT) or not os.listdir(OUT):
        return
    try:
        subprocess.run(
            ["rclone", "move", OUT, f"{R2_REMOTE}/raw",
             "--transfers", "8", "--checkers", "4",
             "--s3-upload-concurrency", "1", "--s3-chunk-size", "5M",
             "--buffer-size", "0", "--no-traverse", "--quiet"],
            check=False, timeout=1800)
    except Exception as e:
        print(f"  [{args.tag}] r2 push failed: {str(e)[:70]}", flush=True)
    os.makedirs(OUT, exist_ok=True)


rows = list(csv.DictReader(open(args.queue, encoding="utf-8")))[args.start:]
rejected = 0
_ext = "jpg" if args.jpeg else "png"
rows = [r for r in rows
        if not os.path.exists(f"{OUT}/{r['index']}.{_ext}")]
if args.limit:
    rows = rows[:args.limit]
if not rows:
    raise SystemExit("nothing to generate")
print(f"{len(rows):,} designs to generate")

# A missing checkpoint produces a confusing "Invalid pretrained_model_name_
# or_path" from diffusers, which reads like a bug rather than a missing file.
if args.model.endswith(".safetensors") and not os.path.exists(args.model):
    raise SystemExit(
        f"checkpoint not found: {args.model}\n"
        "Download a .safetensors from civitai.com (filter: Checkpoint, SDXL "
        "1.0) into /workspace/models/ first.")

# --- SDXL Lightning ------------------------------------------------------
# Base SDXL 1.0 with ByteDance's distilled 4-step UNet swapped in. Everything
# else — VAE, text encoders — stays from base SDXL.
#
# Roughly eight times faster: 476,000 designs go from ~139 GPU-hours to ~17.
#
# It only works with the right settings. Lightning is distilled to reach a
# finished image in 4 steps, so the usual 30 steps and CFG 7 produce burnt,
# over-saturated output. It needs the Euler scheduler on TRAILING timesteps
# and NO classifier-free guidance at all.
if args.lightning:
    from diffusers import UNet2DConditionModel, EulerDiscreteScheduler
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file

    BASE_ID = "stabilityai/stable-diffusion-xl-base-1.0"
    CKPT = f"sdxl_lightning_{args.lightning_steps}step_unet.safetensors"
    print(f"loading SDXL Lightning ({args.lightning_steps}-step): {CKPT}")

    unet = UNet2DConditionModel.from_config(
        BASE_ID, subfolder="unet").to("cuda", torch.float16)
    unet.load_state_dict(
        load_file(hf_hub_download("ByteDance/SDXL-Lightning", CKPT),
                  device="cuda"))

    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE_ID, unet=unet, torch_dtype=torch.float16,
        variant="fp16", use_safetensors=True).to("cuda")
    pipe.scheduler = EulerDiscreteScheduler.from_config(
        pipe.scheduler.config, timestep_spacing="trailing")

    # Lightning replaces the refiner — a polish pass on a 4-step image
    # undoes the distillation and costs most of the speed back.
    args.no_refiner = True
    args.steps = args.lightning_steps
    args.cfg = 0.0
    print(f"  steps={args.steps}  cfg=0  refiner off  scheduler=euler/trailing")

elif args.model.endswith(".safetensors"):
    # a CivitAI checkpoint — this is what makes the output stop looking generic
    pipe = StableDiffusionXLPipeline.from_single_file(
        args.model, torch_dtype=torch.float16, use_safetensors=True)
else:
    pipe = StableDiffusionXLPipeline.from_pretrained(
        args.model, torch_dtype=torch.float16, variant="fp16",
        use_safetensors=True)

if not args.lightning:
    pipe = pipe.to("cuda")
pipe.set_progress_bar_config(disable=True)

# --- speed settings that do not change the image -------------------------
# Every one of these produces bit-identical or visually identical output; they
# only affect how the work is scheduled on the GPU.
try:
    # memory-efficient attention: same maths, less memory traffic
    from diffusers.models.attention_processor import AttnProcessor2_0
    pipe.unet.set_attn_processor(AttnProcessor2_0())
    print("attention: SDPA")
except Exception as e:
    print(f"attention: default ({str(e)[:40]})")

try:
    # frees VRAM so a larger batch fits, which is where the real saving is
    pipe.vae.enable_slicing()
except Exception:
    pass

if args.compile:
    print("compiling UNet (2-4 minutes, then faster for the rest of the run)")
    try:
        pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead",
                                  fullgraph=True)
    except Exception as e:
        print(f"  compile unavailable: {str(e)[:50]}")

refiner = None
if args.hires and args.no_refiner:
    print("note: --hires needs the img2img pipeline, keeping it loaded")
    args.no_refiner = False
if not args.no_refiner:
    print(f"loading refiner: {args.refiner}")
    refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        args.refiner, torch_dtype=torch.float16, variant="fp16",
        use_safetensors=True,
        text_encoder_2=pipe.text_encoder_2, vae=pipe.vae)
    refiner = refiner.to("cuda")
    refiner.set_progress_bar_config(disable=True)
    try:
        from diffusers.models.attention_processor import AttnProcessor2_0
        refiner.unet.set_attn_processor(AttnProcessor2_0())
        refiner.vae.enable_slicing()
    except Exception:
        pass

t0, done, failed = time.time(), 0, 0
for i in range(0, len(rows), args.batch):
    chunk = rows[i:i + args.batch]
    try:
        imgs = pipe(
            prompt=[c["prompt"] for c in chunk],
            negative_prompt=[c["negative"] for c in chunk],
            width=args.size, height=args.size,
            num_inference_steps=args.steps,
            guidance_scale=args.cfg,
        ).images

        if refiner:
            # Low denoise: this is a polish pass, not a regeneration. Higher
            # values throw away the base composition.
            imgs = refiner(
                prompt=[c["prompt"] for c in chunk],
                negative_prompt=[c["negative"] for c in chunk],
                image=imgs, strength=0.25, num_inference_steps=12,
            ).images

        if args.hires and args.hires > args.size:
            # "Hires fix": upscale then re-diffuse at low denoise so the model
            # paints real detail into the larger canvas.
            #
            # Generating at 1536 NATIVELY would be wrong — SDXL is trained at
            # 1024 and larger native sizes produce duplicated features (two
            # heads, repeated limbs). Upscaling then refining avoids that and
            # gives genuinely sharper output.
            big = [im.resize((args.hires, args.hires), Image.LANCZOS)
                   for im in imgs]
            imgs = refiner(
                prompt=[c["prompt"] for c in chunk],
                negative_prompt=[c["negative"] for c in chunk],
                image=big, strength=args.hires_denoise,
                num_inference_steps=18,
            ).images

        for c, im in zip(chunk, imgs):
            # --- reject here, not after uploading ------------------------
            # postrun used to download everything from R2 and then throw 37%
            # away. Those rejects cost storage forever and hours of download
            # for nothing. The check that catches them is a mean over the
            # border — microseconds — so it belongs here, before the file
            # ever leaves the pod.
            if args.qc:
                a = np.asarray(im.convert("RGB")).astype(np.float32)
                lum = a.mean(2)
                b = max(4, int(min(lum.shape) * 0.06))
                edge = np.concatenate([lum[:b, :].ravel(), lum[-b:, :].ravel(),
                                       lum[:, :b].ravel(), lum[:, -b:].ravel()])
                # normalise the pedestal first, exactly as dtf.py does, or a
                # design that is merely lifted gets thrown away as if it were
                # genuinely pale
                black = float(np.clip(np.percentile(edge, 60), 0, 120))
                if float(np.mean(edge) - black) > args.qc_max:
                    rejected += 1
                    continue

            ext = "jpg" if args.jpeg else "png"
            tmp = f"{OUT}/{c['index']}.{ext}.tmp"
            if args.jpeg:
                # q95 on a 24cm print is indistinguishable, and the print
                # pipeline halftones and normalises afterwards anyway — both
                # of which discard far more than JPEG does. Five times
                # smaller, so the same storage budget holds five times the
                # catalogue.
                im.convert("RGB").save(tmp, format="JPEG", quality=95,
                                       subsampling=0, optimize=True)
            else:
                im.save(tmp, format="PNG")
            os.replace(tmp, f"{OUT}/{c['index']}.{ext}")   # atomic
        done += len(chunk)

    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        print(f"  OOM at {i}, retrying singly", flush=True)
        for c in chunk:
            try:
                im = pipe(prompt=c["prompt"], negative_prompt=c["negative"],
                          width=args.size, height=args.size,
                          num_inference_steps=args.steps,
                          guidance_scale=args.cfg).images[0]
                if refiner:
                    im = refiner(prompt=c["prompt"],
                                 negative_prompt=c["negative"],
                                 image=im, strength=0.25,
                                 num_inference_steps=12).images[0]
                im.save(f"{OUT}/{c['index']}.png", format="PNG")
                done += 1
            except Exception as e:
                failed += 1
                print(f"  skip {c['index']}: {str(e)[:60]}", flush=True)
    except Exception as e:
        failed += len(chunk)
        print(f"  batch {i} failed: {str(e)[:80]}", flush=True)

    if R2_REMOTE and done and done % FLUSH_EVERY < args.batch:
        push_to_r2()

    if done and done % 50 < args.batch:
        el = time.time() - t0
        rate = done / max(el, 1)
        left = (len(rows) - done) / max(rate, 0.001) / 3600
        print(f"  [{args.tag}] {done:,}/{len(rows):,}  {rate:.2f}/s  "
              f"~{left:.1f}h left  failed {failed}"
              + (f"  rejected {rejected:,}" if args.qc else ""), flush=True)

if R2_REMOTE:
    push_to_r2()

el = time.time() - t0
print(f"\ndone: {done:,} in {el/3600:.2f}h ({done/max(el,1):.2f}/s), "
      f"failed {failed}, ~${el/3600*0.34:.2f} GPU"
      + (f", rejected {rejected:,} on the pod" if args.qc else ""))
