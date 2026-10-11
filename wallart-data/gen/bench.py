#!/usr/bin/env python3
"""Measure images/hour for FLUX.1 schnell under several configurations.

The whole budget turns on this number, so it is measured rather than quoted.
A 24 GB card cannot hold the 11.9B transformer in bfloat16 (23.8 GB), so the
cheap cards are only usable quantised. bitsandbytes NF4 puts the transformer
at about 7 GB and the T5 at about 5 GB, which leaves room on a 4090.

    python3 bench.py --quant nf4 --sizes 848x1200,832x1200,704x1008 --batches 4,8
"""
import argparse, json, time, os, zlib

PROMPTS = [
 "charcoal and graphite drawing, visible paper grain, loose open hatching of Snowdonia, seen across open land, the horizon pushed to the top of the picture, two adjacent colours only, flat fill, no gradient, no text, no lettering, no signature",
 "flat screen-printed poster of a puffin, head and shoulders, centred, direct gaze, on one flat ground, burnt orange against petrol blue, flat fill, no gradient, no text, no lettering, no signature",
 "wet-on-wet watercolour, soft bleeds and blooms of the Lake District, seen across open land, cream bone and oatmeal with one small rust accent, no text, no lettering, no signature",
 "two-tone linocut print, white gouge marks cutting through flat ink of the Cotswolds, as a naive flattened townscape in horizontal bands, burnt orange against petrol blue, no text, no lettering, no signature",
]


def build(quant, model):
    import torch
    from diffusers import FluxPipeline
    kw = {"torch_dtype": torch.bfloat16}
    if quant == "nf4":
        from diffusers import FluxTransformer2DModel
        from diffusers.quantizers import PipelineQuantizationConfig
        qc = PipelineQuantizationConfig(
            quant_backend="bitsandbytes_4bit",
            quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4",
                          "bnb_4bit_compute_dtype": torch.bfloat16},
            components_to_quantize=["transformer", "text_encoder_2"])
        kw["quantization_config"] = qc
    pipe = FluxPipeline.from_pretrained(model, **kw)
    if quant == "nf4":
        pipe.to("cuda")                      # already small enough
    else:
        free = torch.cuda.mem_get_info()[0] / 2**30
        print(f"free vram {free:.0f} GB", flush=True)
        pipe.to("cuda") if free >= 40 else pipe.enable_model_cpu_offload()
    return pipe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quant", default="none", choices=["none", "nf4"])
    ap.add_argument("--model", default="lzyvegetable/FLUX.1-schnell")
    ap.add_argument("--sizes", default="848x1200")
    ap.add_argument("--batches", default="4")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--out", default="/workspace/art")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    import torch
    print(f"torch {torch.__version__} quant={a.quant}", flush=True)
    print(torch.cuda.get_device_name(0), flush=True)
    pipe = build(a.quant, a.model)

    results = []
    for size in a.sizes.split(","):
        w, h = (int(x) for x in size.split("x"))
        for bs in (int(x) for x in a.batches.split(",")):
            prompts = [PROMPTS[i % len(PROMPTS)] for i in range(bs)]
            gens = [torch.Generator("cpu").manual_seed(zlib.crc32(f"{size}{bs}{i}".encode()) % 2**31)
                    for i in range(bs)]
            try:
                pipe(prompt=prompts, num_inference_steps=4, guidance_scale=0.0,
                     width=w, height=h, max_sequence_length=256, generator=gens)   # warm up
                torch.cuda.synchronize()
                t0 = time.time()
                for r in range(a.reps):
                    imgs = pipe(prompt=prompts, num_inference_steps=4, guidance_scale=0.0,
                                width=w, height=h, max_sequence_length=256,
                                generator=gens).images
                torch.cuda.synchronize()
                el = time.time() - t0
                n = a.reps * bs
                rate = 3600 * n / el
                peak = torch.cuda.max_memory_allocated() / 2**30
                results.append({"size": size, "batch": bs, "img_per_hour": round(rate),
                                "sec_per_img": round(el / n, 3), "peak_vram_gb": round(peak, 1)})
                print(f"  {size} batch {bs}: {rate:,.0f} img/hr "
                      f"({el/n:.2f} s each), peak {peak:.1f} GB", flush=True)
                for i, im in enumerate(imgs):
                    im.save(f"{a.out}/bench_{a.quant}_{size}_b{bs}_{i}.jpg", "JPEG", quality=92)
            except torch.OutOfMemoryError:
                print(f"  {size} batch {bs}: OOM", flush=True)
                results.append({"size": size, "batch": bs, "oom": True})
            torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    json.dump(results, open(f"{a.out}/bench.json", "w"), indent=1)
    print("BENCH " + json.dumps(results), flush=True)


if __name__ == "__main__":
    main()
