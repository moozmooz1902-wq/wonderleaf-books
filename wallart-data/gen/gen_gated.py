#!/usr/bin/env python3
"""Production worker: generate, read the output, and reject what has writing on it.

Five of the first sixteen panels came back with lettering or a fake artist's
signature - "W ITBEY" across a harbour, "N2Z1" on a seafront, a monogram in
the corner of a linocut. guidance_scale is 0 for schnell, so negative prompts
are inert and there is no prompt wording that fixes it. The only thing that
works is looking at the result.

EasyOCR runs on the same GPU in about 50 ms, against roughly 2,000 ms for a
generation, so the gate costs about 2.5% and saves a listing that would have
gone up with a garbled word printed across it.

A rejected job is retried with a different seed, up to --retries times. The
rejection rate is reported at the end, because that number is what the
catalogue budget is built on.

Resumable: every finished SKU is appended to done.txt.
"""
import argparse, json, os, time, zlib

# A detection has to be reasonably confident AND reasonably large before it
# counts. FLUX leaves faint marks everywhere that OCR will happily read as a
# letter; rejecting on those throws away good work.
MIN_CONF = 0.35
MIN_AREA = 0.0012          # share of the panel
MIN_CHARS = 2


def text_marks(reader, img):
    import numpy as np
    a = np.asarray(img.convert("RGB"))
    H, W = a.shape[:2]
    out = []
    for box, txt, conf in reader.readtext(a):
        t = "".join(c for c in txt if c.isalnum())
        if len(t) < MIN_CHARS or conf < MIN_CONF:
            continue
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        area = (max(xs) - min(xs)) * (max(ys) - min(ys)) / (W * H)
        if area >= MIN_AREA:
            out.append((txt, round(float(conf), 2), round(area, 4)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--width", type=int, default=704)
    ap.add_argument("--height", type=int, default=1008)
    ap.add_argument("--retries", type=int, default=2)
    # Generate taller than needed and throw the bottom away. Measured on 129
    # panels: 96% of the fake signatures and stray marks sit below 90% of the
    # panel height, so a 10% crop removes almost all of them for the cost of
    # generating 11% more pixels. Trying to paint them out instead was tried
    # first and only half worked - see declutter.py.
    ap.add_argument("--crop-bottom", type=float, default=0.10)
    ap.add_argument("--tag", default="")
    ap.add_argument("--quant", default="nf4", choices=["none", "nf4"])
    ap.add_argument("--model", default="lzyvegetable/FLUX.1-schnell")
    ap.add_argument("--no-gate", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    donep = os.path.join(a.out, "done.txt")
    done = {l.strip() for l in open(donep)} if os.path.exists(donep) else set()
    a.crop_bottom = max(0.0, min(0.25, a.crop_bottom))

    jobs = [j for j in json.load(open(a.jobs)) if j["sku"] not in done]
    if a.limit:
        jobs = jobs[:a.limit]
    gen_h = int(round(a.height / (1 - a.crop_bottom) / 16)) * 16
    print(f"generating {a.width}x{gen_h}, cropping the bottom "
          f"{a.crop_bottom:.0%} down to {a.width}x{a.height}", flush=True)
    print(f"{len(jobs):,} to generate at {a.width}x{a.height} "
          f"quant={a.quant} gate={'off' if a.no_gate else 'on'}", flush=True)

    import torch
    from diffusers import FluxPipeline
    kw = {"torch_dtype": torch.bfloat16}
    if a.quant == "nf4":
        from diffusers.quantizers import PipelineQuantizationConfig
        kw["quantization_config"] = PipelineQuantizationConfig(
            quant_backend="bitsandbytes_4bit",
            quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4",
                          "bnb_4bit_compute_dtype": torch.bfloat16},
            components_to_quantize=["transformer", "text_encoder_2"])
    pipe = FluxPipeline.from_pretrained(a.model, **kw)
    free = torch.cuda.mem_get_info()[0] / 2**30
    print(f"free vram {free:.0f} GB", flush=True)
    pipe.to("cuda") if (a.quant == "nf4" or free >= 40) else pipe.enable_model_cpu_offload()

    reader = None
    if not a.no_gate:
        import easyocr
        reader = easyocr.Reader(["en"], gpu=True, verbose=False)
        print("ocr gate ready", flush=True)

    t0 = time.time()
    kept = rejected = gens = 0
    df = open(donep, "a")
    mf = open(os.path.join(a.out, "manifest.jsonl"), "a", encoding="utf-8")
    rf = open(os.path.join(a.out, "rejects.jsonl"), "a", encoding="utf-8")

    queue = list(jobs)
    attempt = {j["sku"]: 0 for j in jobs}
    while queue:
        chunk, queue = queue[:a.batch], queue[a.batch:]
        gens_seed = [zlib.crc32(f"{j['sku']}#{attempt[j['sku']]}".encode()) % 2**31
                     for j in chunk]
        imgs = pipe(prompt=[j["prompt"] for j in chunk],
                    num_inference_steps=a.steps, guidance_scale=0.0,
                    width=a.width, height=gen_h, max_sequence_length=256,
                    generator=[torch.Generator("cpu").manual_seed(s) for s in gens_seed]
                    ).images
        gens += len(chunk)
        if a.crop_bottom > 0:
            imgs = [im.crop((0, 0, im.width, int(im.height * (1 - a.crop_bottom))))
                    for im in imgs]
        for (j, im, sd) in zip(chunk, imgs, gens_seed):
            marks = text_marks(reader, im) if reader else []
            if marks and attempt[j["sku"]] < a.retries:
                attempt[j["sku"]] += 1
                queue.append(j)
                rejected += 1
                rf.write(json.dumps({"sku": j["sku"], "try": attempt[j["sku"]],
                                     "marks": marks}) + "\n")
                continue
            if marks:
                rejected += 1
                rf.write(json.dumps({"sku": j["sku"], "try": "final", "kept_anyway": True,
                                     "marks": marks}) + "\n")
            im.save(os.path.join(a.out, j["sku"] + a.tag + ".jpg"), "JPEG", quality=92)
            df.write(j["sku"] + "\n")
            mf.write(json.dumps({**j, "seed": sd, "marks": marks},
                                 ensure_ascii=False) + "\n")
            kept += 1
        df.flush(); mf.flush(); rf.flush()
        el = time.time() - t0
        print(f"  kept {kept:,} / {gens:,} generated  {gens/el:.2f} img/s  "
              f"reject {rejected/max(gens,1):.0%}  {el/60:.1f} min", flush=True)

    el = time.time() - t0
    print(f"DONE kept {kept:,} from {gens:,} generations in {el/60:.1f} min", flush=True)
    print(f"RATE: {3600*gens/el:,.0f} generations/hour", flush=True)
    print(f"REJECT_RATE: {rejected/max(gens,1):.4f}", flush=True)


if __name__ == "__main__":
    main()
