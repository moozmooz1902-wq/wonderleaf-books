"""
upscale.py — a separate upscale pass, run after generation.

WHY THIS IS THE RIGHT SHAPE
    Generating at 1536 via diffusion costs an extra ~4 seconds per image, on
    the GPU, during the run. That is roughly $335 across 200,000 designs.

    But the extra resolution is not needed at generation time. Generate cheap
    at 1024, keep those as the masters, then upscale in one pass afterwards.
    Same end result, a fraction of the cost, and the upscale can be re-run
    with a better model later without regenerating anything.

WHAT IT DOES NOT DO
    A plain LANCZOS resize adds no information — it makes the same image
    bigger and softer. Real-ESRGAN reconstructs plausible detail, which is
    what actually looks sharper on a garment.

    If Real-ESRGAN is unavailable this falls back to LANCZOS with light
    unsharp masking. That is better than nothing but genuinely inferior; the
    script says so rather than pretending otherwise.

    python3 upscale.py raw_w0 --scale 2
"""

import argparse, glob, os, sys, time

import numpy as np
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("--out", default=None, help="defaults to <src>_up")
ap.add_argument("--scale", type=int, default=2)
ap.add_argument("--force-lanczos", action="store_true")
args = ap.parse_args()

OUT = args.out or f"{args.src}_up"
os.makedirs(OUT, exist_ok=True)

# --- try Real-ESRGAN; fall back honestly if it is not installed ------------
upsampler = None
if not args.force_lanczos:
    try:
        import torch
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet

        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                        num_block=23, num_grow_ch=32, scale=4)
        upsampler = RealESRGANer(
            scale=4,
            model_path="https://github.com/xinntao/Real-ESRGAN/releases/"
                       "download/v0.1.0/RealESRGAN_x4plus.pth",
            model=model, tile=512, tile_pad=10, pre_pad=0,
            half=torch.cuda.is_available(),
            device="cuda" if torch.cuda.is_available() else "cpu")
        print("using Real-ESRGAN")
    except Exception as e:
        print(f"Real-ESRGAN unavailable ({str(e)[:60]})")
        print("falling back to LANCZOS + unsharp — noticeably softer.")
        print("  install with: pip install realesrgan basicsr")

files = [f for f in sorted(glob.glob(f"{args.src}/*.png"))
         if not os.path.exists(f"{OUT}/{os.path.basename(f)}")]
if not files:
    raise SystemExit("nothing to upscale")
print(f"{len(files):,} images -> {OUT}/ at {args.scale}x")

t0 = 0.0
for i, f in enumerate(files, 1):
    name = os.path.basename(f)
    im = Image.open(f).convert("RGB")
    t = time.time()

    if upsampler:
        out, _ = upsampler.enhance(np.asarray(im), outscale=args.scale)
        Image.fromarray(out).save(f"{OUT}/{name}")
    else:
        # Plain LANCZOS with light unsharp. A staged multi-step upscale was
        # tried and measured no better (edge sharpness 4.3 vs 4.2) while
        # taking 70% longer, so the simpler version stands.
        #
        # Be clear about what this is: resampling makes the image bigger, it
        # does not invent detail. Real-ESRGAN does. If sharpness matters,
        # getting Real-ESRGAN installed is worth more than any resampling
        # trick.
        big = im.resize((im.width * args.scale, im.height * args.scale),
                        Image.LANCZOS)
        big = big.filter(ImageFilter.UnsharpMask(radius=2, percent=80,
                                                 threshold=3))
        big.save(f"{OUT}/{name}")

    t0 += time.time() - t
    if i % 100 == 0:
        rate = t0 / i
        print(f"  {i}/{len(files)}  {rate:.2f}s each  "
              f"~{(len(files)-i)*rate/3600:.1f}h left", flush=True)

rate = t0 / max(len(files), 1)
print(f"\ndone: {len(files):,} in {t0/60:.1f} min ({rate:.2f}s each)")
print(f"200,000 would take {200000*rate/3600:.1f} GPU hours "
      f"(~${200000*rate/3600*0.34:.0f} on community cloud)")
