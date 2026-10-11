#!/usr/bin/env python3
"""GPU pod: generate wall art with FLUX.1 [schnell].

schnell, not dev: Apache-2.0, so commercial use is allowed. FLUX.1-dev is
non-commercial and must never be used on goods that are sold.

Settings are the ones the wall-art branch already proved: 4 steps,
guidance_scale 0.0, max_sequence_length 256 (schnell's T5 window is 256, not
the 512 people quote from dev), bfloat16, 848x1200 for the A-series ratio.

Resumable: every image written is appended to done.txt, so a pod that is
stopped - or runs out of balance - restarts where it left off.

  python3 gen_worker.py --jobs jobs.json --out /workspace/art --batch 4
"""
import argparse, json, os, time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--steps", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    donep = os.path.join(a.out, "done.txt")
    done = {l.strip() for l in open(donep)} if os.path.exists(donep) else set()

    jobs = [j for j in json.load(open(a.jobs)) if j["sku"] not in done]
    if a.limit:
        jobs = jobs[:a.limit]
    print(f"{len(jobs):,} to generate ({len(done):,} already done)", flush=True)

    import torch
    from diffusers import FluxPipeline
    pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell",
                                        torch_dtype=torch.bfloat16)
    free = torch.cuda.mem_get_info()[0] / 2**30 if torch.cuda.is_available() else 0
    print(f"free vram {free:.0f} GB", flush=True)
    if free >= 40:
        pipe.to("cuda")
    else:
        pipe.enable_model_cpu_offload()      # 24 GB cards: slower but fits

    t0 = time.time(); n = 0
    df = open(donep, "a")
    mf = open(os.path.join(a.out, "manifest.jsonl"), "a", encoding="utf-8")
    for i in range(0, len(jobs), a.batch):
        chunk = jobs[i:i + a.batch]
        gens = [torch.Generator("cpu").manual_seed(abs(hash(j["sku"])) % 2**31)
                for j in chunk]
        imgs = pipe(prompt=[j["prompt"] for j in chunk],
                    num_inference_steps=a.steps, guidance_scale=0.0,
                    width=848, height=1200, max_sequence_length=256,
                    generator=gens).images
        for j, im in zip(chunk, imgs):
            p = os.path.join(a.out, j["sku"] + ".jpg")
            im.save(p, "JPEG", quality=92)
            df.write(j["sku"] + "\n")
            mf.write(json.dumps(j, ensure_ascii=False) + "\n")
            n += 1
        df.flush(); mf.flush()
        el = time.time() - t0
        print(f"  {n:,}/{len(jobs):,}  {n/el:.2f} img/s  {el/60:.1f} min", flush=True)
    el = time.time() - t0
    print(f"DONE {n:,} images in {el/60:.1f} min = {n/max(el,1):.2f} img/s", flush=True)
    if n:
        print(f"RATE: {3600*n/el:,.0f} images/hour", flush=True)


if __name__ == "__main__":
    main()
