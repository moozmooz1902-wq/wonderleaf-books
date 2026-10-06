#!/usr/bin/env python3
"""GPU pod: flat-colour illustrations for BLACK t-shirts, printed by DTF.

Model licence, settled on the wall-art branch and re-checked here: the
artwork goes on goods that are sold, so only an Apache-2.0 model is usable.
FLUX.1-schnell qualifies but is gated on HuggingFace and 401s without an
account that has accepted the licence. segmind/SSD-1B is Apache-2.0, is NOT
gated, and is a distilled SDXL so it is about twice as fast as SDXL base.
SDXL-Turbo and FLUX.1-dev are NON-COMMERCIAL and must never be used here.

What this uploads, and why there are two copies:

    illus/src/   the generated image exactly as the model drew it
    illus/raw/   the printable transparent PNG
    illus/ink/   the same shape as a single flat ink

src/ exists so the flattening can be retuned later without paying for the
GPU again. Generation is the expensive step and the artwork does not change;
how it is reduced for DTF is the part that gets argued over.

    python3 gen_illus.py --limit 24          # sample, then look at it
    python3 gen_illus.py --all --part 1/2
"""
import argparse, io, json, os, time

import dtf

MODEL = os.environ.get("MODEL", "segmind/SSD-1B")
W, H = 1024, 1024
STEPS = int(os.environ.get("STEPS", "26"))
GUIDANCE = float(os.environ.get("GUIDANCE", "8.5"))

# DTF cannot hold a gradient, a soft edge or a 1px line, so the prompt asks
# for none of them. It is still only a request - dtf.flatten() enforces it
# afterwards, because the model complies maybe half the time. The second
# clause is about the garment: these shirts are black, and the model's
# default palette is sepia and charcoal, which on black is invisible.
STYLE = ("flat vector illustration, bold thick black outlines, large simple "
         "shapes, solid blocks of bright saturated colour, screen print "
         "separation, sticker art, cel shaded, three flat colours only, "
         "no gradient, no shading, no texture, no halftone, no crosshatch, "
         "no fine detail, no engraving, high contrast, centred, "
         "die cut, isolated on a plain white background, no background "
         "panel, no frame, no border, no box, no label, "
         "no text, no lettering, no watermark")

# Rotated per subject so 400 designs do not all come back in the same two
# colours. The seller asked for colour; the model will not supply it unasked.
PALETTES = [
    "vivid red, cream and white",
    "electric blue, white and orange",
    "neon green, black and white",
    "hot pink, purple and cream",
    "gold, teal and off-white",
    "orange, turquoise and white",
    "crimson, mustard and ivory",
    "lime, magenta and white",
]

NEG = ("gradient, gradients, shading, shadow, soft shading, airbrush, "
       "halftone, dithering, texture, grain, noise, blurry, soft edges, "
       "photorealistic, photograph, 3d render, depth of field, bokeh, "
       "watercolour, sketch, pencil, crosshatch, engraving, etching, "
       "intricate detail, fine lines, sepia, monochrome, greyscale, dark, "
       "background, backdrop, panel, frame, border, square, rectangle, "
       "poster, label, badge outline, vignette, scenery, landscape, "
       "text, letters, words, watermark, signature")


def prompt_for(subject, i):
    return f"{subject}, {PALETTES[i % len(PALETTES)]}, {STYLE}"


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
    """One flat ink - the cheapest and most reliable thing to print."""
    from PIL import Image
    a = img.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    out = Image.new("RGBA", img.size, ink + (0,))
    out.putalpha(a)
    return out


def usable(img):
    from PIL import ImageStat
    return max(ImageStat.Stat(img.convert("L")).stddev) > 12


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


def s3():
    import boto3
    from botocore.config import Config
    return boto3.client("s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(retries={"max_attempts": 5}), region_name="auto")


def put(cli, bucket, key, img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, fmt, optimize=True)
    buf.seek(0)
    cli.upload_fileobj(buf, bucket, key, ExtraArgs={"ContentType": "image/png"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=24)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--part", default="1/1", help="shard as k/n")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--colours", type=int, default=4)
    ap.add_argument("--prefix", default="illus/")
    a = ap.parse_args()

    subjects = json.load(open("subject_bank.json"))
    if not a.all:
        subjects = subjects[:a.limit]
    k, n = (int(x) for x in a.part.split("/"))
    subjects = [s for i, s in enumerate(subjects) if i % n == k - 1]
    print(f"{len(subjects)} subjects, part {a.part}", flush=True)

    cli = s3(); B = os.environ["R2_BUCKET"]
    gen = Diffuser()
    t0 = time.time(); n_ok = 0; report = []
    for i in range(0, len(subjects), a.batch):
        chunk = subjects[i:i + a.batch]
        imgs = gen([prompt_for(s, i + j) for j, s in enumerate(chunk)],
                   [1000 + i + j for j in range(len(chunk))])
        for s, im in zip(chunk, imgs):
            slug = "".join(c if c.isalnum() else "-" for c in s)[:48].strip("-")
            if not usable(im):
                report.append((slug, False, "model returned a blank frame"))
                print(f"  blank, skipped: {s}", flush=True)
                continue
            # src/ first and unconditionally: it is the only copy that cannot
            # be regenerated for free, so it is saved before anything can fail.
            put(cli, B, f"{a.prefix}src/{slug}.png", im)
            art = dtf.flatten(knockout(im), colours=a.colours)
            ok, why = dtf.printable(art)
            report.append((slug, ok, why))
            if ok:
                put(cli, B, f"{a.prefix}raw/{slug}.png", art)
                put(cli, B, f"{a.prefix}ink/{slug}.png", recolour(art, (242, 240, 234)))
                n_ok += 1
        print(f"  {i+len(chunk)}/{len(subjects)}  {n_ok} printable  "
              f"{(time.time()-t0)/max(1,i+len(chunk)):.1f}s each", flush=True)

    body = "\n".join(f"{'PASS' if o else 'FAIL'}\t{s}\t{w}" for s, o, w in report)
    cli.put_object(Bucket=B, Key=f"{a.prefix}_REPORT_{k}of{n}.tsv",
                   Body=body.encode(), ContentType="text/plain")
    cli.put_object(Bucket=B, Key=f"{a.prefix}_DONE_{k}of{n}.txt",
                   Body=f"printable={n_ok} of {len(subjects)}".encode(),
                   ContentType="text/plain")
    print(f"DONE {n_ok}/{len(subjects)} printable in {(time.time()-t0)/60:.1f} min",
          flush=True)


if __name__ == "__main__":
    main()
