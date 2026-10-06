#!/usr/bin/env python3
"""GPU pod: FLUX.1-schnell illustrations for black t-shirts.

Adapted from wallart/pod/gen_ai.py on the poster branch, which already
settled the model choice: FLUX.1 [schnell], Apache-2.0, commercial use
allowed. FLUX.1-dev is non-commercial and must never be used on goods that
are sold.

Difference from the wall-art version: those prints go on white paper, these
go on a BLACK shirt. So the model draws on a plain white ground, and the
white is knocked out to transparency and the artwork reduced to the
design's own inks. What gets uploaded is a transparent PNG that screen
prints cleanly.

    python3 gen_illus.py --limit 24          # sample, then look at it
    python3 gen_illus.py --all --part 1/2
"""
import argparse, io, json, os, sys, time

# FLUX.1-schnell is Apache-2.0 but GATED on HuggingFace - it 401s without an
# account that has accepted the licence, which is a setup step the seller
# should not need. SSD-1B is also Apache-2.0, is NOT gated, and is a distilled
# SDXL so it is roughly twice as fast as SDXL base. Both permit commercial use;
# SDXL-Turbo and FLUX.1-dev do not, and must never be used on goods that sell.
MODEL = os.environ.get("MODEL", "segmind/SSD-1B")
W, H = 1024, 1024
STEPS = int(os.environ.get("STEPS", "22"))
GUIDANCE = float(os.environ.get("GUIDANCE", "7.0"))

STYLE = ("bold screen-print t-shirt graphic, thick confident linework, flat "
         "solid shapes, strong silhouette, high contrast, centred composition, "
         "plain pure white background, no text, no lettering, no watermark, "
         "vector poster art")


def prompt_for(subject):
    return f"{subject}, {STYLE}"


NEG = ("text, letters, words, watermark, signature, photo, photograph, "
       "realistic, 3d render, gradient, blurry, grey background, noise")


class Diffuser:
    def __init__(self):
        import torch
        from diffusers import StableDiffusionXLPipeline
        self.torch = torch
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            MODEL, torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
        free = torch.cuda.mem_get_info()[0] / 2**30 if torch.cuda.is_available() else 0
        print(f"{MODEL}  free VRAM {free:.0f} GB", flush=True)
        self.pipe.to("cuda") if free >= 14 else self.pipe.enable_model_cpu_offload()
        self.pipe.set_progress_bar_config(disable=True)

    def __call__(self, prompts, seeds):
        gens = [self.torch.Generator("cuda").manual_seed(int(s)) for s in seeds]
        return self.pipe(prompt=prompts, negative_prompt=[NEG] * len(prompts),
                         num_inference_steps=STEPS, guidance_scale=GUIDANCE,
                         width=W, height=H, generator=gens).images


SENTINEL = (255, 0, 255)


def knockout(img, thresh=52):
    """Remove the background, whatever colour the model actually painted it.

    The first version assumed white and tested every channel against 238. The
    model does not paint white: real backgrounds came out (249,239,222),
    (231,199,152), (223,216,210) - cream, beige, warm grey. All of those
    survived the test and would print as a visible square on a black shirt.

    So the background is found by flooding inward from the edges with a
    tolerance, which removes whatever is contiguous with the border and
    leaves a similar tone INSIDE the artwork alone.
    """
    from PIL import Image, ImageDraw
    im = img.convert("RGB")
    w, h = im.size
    work = im.copy()
    d = ImageDraw.Draw(work)
    seeds = [(1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2),
             (w // 2, 1), (w // 2, h - 2), (1, h // 2), (w - 2, h // 2)]
    for sx, sy in seeds:
        try:
            ImageDraw.floodfill(work, (sx, sy), SENTINEL, thresh=thresh)
        except Exception:
            pass
    out = im.convert("RGBA")
    px_w, px_o = work.load(), out.load()
    for y in range(h):
        for x in range(w):
            if px_w[x, y] == SENTINEL:
                px_o[x, y] = (0, 0, 0, 0)
    return out


def recolour(img, ink):
    """One flat ink, so it reads as a screen print rather than a photo."""
    from PIL import Image
    a = img.getchannel("A").point(lambda v: 255 if v > 110 else 0)
    out = Image.new("RGBA", img.size, ink + (0,))
    out.putalpha(a)
    return out


def usable(img):
    from PIL import ImageStat
    return max(ImageStat.Stat(img.convert("L")).stddev) > 12


def s3():
    import boto3
    from botocore.config import Config
    return boto3.client("s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(retries={"max_attempts": 5}), region_name="auto")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=24)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--prefix", default="illus/")
    a = ap.parse_args()

    subjects = json.load(open("subject_bank.json"))[:a.limit]
    print(f"{len(subjects)} subjects", flush=True)
    cli = s3(); B = os.environ["R2_BUCKET"]
    flux = Diffuser()
    t0 = time.time(); n = 0
    for i in range(0, len(subjects), a.batch):
        chunk = subjects[i:i + a.batch]
        imgs = flux([prompt_for(s) for s in chunk], [1000 + i + k for k in range(len(chunk))])
        for s, im in zip(chunk, imgs):
            if not usable(im):
                print(f"  blank, skipped: {s}", flush=True); continue
            art = knockout(im)
            slug = "".join(c if c.isalnum() else "-" for c in s)[:48].strip("-")
            for name, obj in (("raw", art), ("ink", recolour(art, (242, 240, 234)))):
                buf = io.BytesIO(); obj.save(buf, "PNG", optimize=True); buf.seek(0)
                cli.upload_fileobj(buf, B, f"{a.prefix}{name}/{slug}.png",
                                   ExtraArgs={"ContentType": "image/png"})
            n += 1
        print(f"  {n}/{len(subjects)}  {(time.time()-t0)/max(1,n):.1f}s each", flush=True)
    cli.put_object(Bucket=B, Key=f"{a.prefix}_DONE.txt",
                   Body=f"illustrations={n}".encode(), ContentType="text/plain")
    print(f"DONE {n} illustrations in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
