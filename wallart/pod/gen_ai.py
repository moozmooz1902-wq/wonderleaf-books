#!/usr/bin/env python3
"""GPU pod: generate the AI image catalogue and upload it to R2.

For every row of out/<bucket>_ai.csv.gz (built by images_bank.py):
    FLUX.1 [schnell] (Apache-2.0, commercial use allowed), 4 steps, 864x1216
    -> dictionary-page composite where the format needs it (ai_compose.py)
    -> art/raw/<SKU>.png   the picture itself, for printing (upscale as usual)
    -> art/mock/<SKU>.jpg  the listing photo: the picture in a black frame

Resumable (skips SKUs whose listing photo is already in the bucket) and
shardable across GPUs/pods with --part k/n.

    export R2_ACCOUNT_ID=... R2_ACCESS_KEY_ID=... R2_SECRET_ACCESS_KEY=...
    python3 pod/gen_ai.py --bucket luxvia-art --limit 20        # try a few, then look at them
    python3 pod/gen_ai.py --all --part 1/2                      # GPU 1 of 2
    python3 pod/gen_ai.py --all --dry-run --limit 8             # no GPU: grey placeholders, tests the plumbing
"""
import argparse, csv, gzip, io, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
BUCKETS = ["luxvia-art", "mercury-usm", "lunar-kms", "posterleaf-store1"]
MODEL = "black-forest-labs/FLUX.1-schnell"


def load_rows(buckets, part, limit, done_by_bucket):
    k, n = map(int, part.split("/"))
    rows = []
    for b in buckets:
        with gzip.open(HERE / "out" / f"{b}_ai.csv.gz", "rt", encoding="utf-8") as fh:
            for i, r in enumerate(csv.DictReader(fh)):
                if i % n != k - 1 or f"art/mock/{r['sku']}.jpg" in done_by_bucket.get(b, ()):
                    continue
                rows.append(r)
                if limit and len(rows) >= limit:
                    return rows
    return rows


class Flux:
    def __init__(self, steps, width, height):
        import torch
        from diffusers import FluxPipeline
        self.torch = torch
        self.pipe = FluxPipeline.from_pretrained(MODEL, torch_dtype=torch.bfloat16)
        free = torch.cuda.mem_get_info()[0] / 2**30 if torch.cuda.is_available() else 0
        if free >= 40:
            self.pipe.to("cuda")
        else:                                 # 24 GB cards: slower, but fits
            self.pipe.enable_model_cpu_offload()
        self.steps, self.w, self.h = steps, width, height

    def __call__(self, prompts, seeds):
        gens = [self.torch.Generator("cpu").manual_seed(int(s)) for s in seeds]
        out = self.pipe(prompt=prompts, num_inference_steps=self.steps, guidance_scale=0.0,
                        width=self.w, height=self.h, max_sequence_length=256, generator=gens)
        return out.images


class Placeholder:
    """--dry-run: no GPU, no model download; grey cards with the SKU, to test the pipeline."""
    def __init__(self, *a):
        pass

    def __call__(self, prompts, seeds):
        from PIL import Image, ImageDraw
        ims = []
        for p in prompts:
            im = Image.new("RGB", (864, 1216), "white")
            ImageDraw.Draw(im).rectangle([150, 250, 714, 966], outline=(120, 120, 120), width=6)
            ims.append(im)
        return ims


def usable(img):
    """Reject blank or near-uniform outputs (a failed generation)."""
    from PIL import ImageStat
    return max(ImageStat.Stat(img.convert("L")).stddev) > 12


def finish(row, img):
    from ai_compose import dictionary_page, pure_white
    from render import mockup
    if row["page"] == "1":
        img = dictionary_page(img, int(row["seed"]), width=1728)
    else:
        img = pure_white(img)                  # background exactly #FFFFFF, not the model's 245-grey
    raw = io.BytesIO(); img.save(raw, "PNG", optimize=False, compress_level=6)
    mock = io.BytesIO(); mockup(img, 1600, framed=True).save(mock, "JPEG", quality=88, optimize=True)
    return raw.getvalue(), mock.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", choices=BUCKETS)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--part", default="1/1")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="placeholders, and write to out/ai_preview/ instead of R2")
    a = ap.parse_args()
    buckets = BUCKETS if a.all else [a.bucket]

    if a.dry_run:
        client, done = None, {}
        preview = HERE / "out" / "ai_preview"; preview.mkdir(parents=True, exist_ok=True)
    else:
        from publish import s3, existing
        client = s3()
        done = {b: existing(client, b, "art/mock/") for b in buckets}
    rows = load_rows(buckets, a.part, a.limit, done)
    print(f"{len(rows):,} images to make", flush=True)
    if not rows:
        return
    gen = (Placeholder if a.dry_run else Flux)(a.steps, 864, 1216)
    up = ThreadPoolExecutor(max_workers=16)
    futs, t0, made, redo = [], time.time(), 0, 0

    def put(bucket, key, body, ctype):
        client.put_object(Bucket=bucket, Key=key, Body=body, ContentType=ctype,
                          CacheControl="public, max-age=31536000, immutable")

    for i in range(0, len(rows), a.batch):
        chunk = rows[i:i + a.batch]
        imgs = gen([r["prompt"] for r in chunk], [r["seed"] for r in chunk])
        for r, img in zip(chunk, imgs):
            if not usable(img):                  # one retry with a new seed
                redo += 1
                img = gen([r["prompt"]], [int(r["seed"]) + 1])[0]
            raw, mock = finish(r, img)
            if a.dry_run:
                (preview / f"{r['sku']}.jpg").write_bytes(mock)
            else:
                futs.append(up.submit(put, r["store"], f"art/raw/{r['sku']}.png", raw, "image/png"))
                futs.append(up.submit(put, r["store"], f"art/mock/{r['sku']}.jpg", mock, "image/jpeg"))
            made += 1
        if made % 200 < a.batch:
            rate = made / (time.time() - t0)
            print(f"  {made:,}/{len(rows):,}  {rate * 3600:,.0f}/hour  eta {(len(rows) - made) / rate / 3600:.1f} h"
                  f"  retries {redo}", flush=True)
    for f in futs:
        f.result()
    up.shutdown()
    print(f"done: {made:,} images in {(time.time() - t0) / 3600:.1f} h")


if __name__ == "__main__":
    main()
