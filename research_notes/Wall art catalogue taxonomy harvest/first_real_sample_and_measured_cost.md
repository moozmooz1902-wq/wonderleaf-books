# The first real sample, and what a million actually costs

11 Oct 2026. Everything below is measured on a rented GPU, not quoted from a
price list or a forum post.

## What was generated

16 designs, FLUX.1 [schnell], 4 steps, guidance_scale 0, 848x1200, bfloat16,
batch 4. One per technique/grammar pairing so the spread is visible rather
than sixteen versions of the same thing. Composited through
`art_border.py` (6% white paper margin, printed into the design, no mount)
and `frames.py` style A (plain moulding) in black, white and oak.

Sheets are in `wallart-samples/`.

## The measured rate

    NVIDIA A40 48GB, RunPod secure, $0.59/hr
    16 images in 1.1 min = 873 images/hour = $0.00068 per image

A 24 GB card is not an option and this cost three failed pods to establish.
The FLUX transformer is 11.9B parameters, which is 23.8 GB in bfloat16, so an
RTX 4090 runs out of memory inside the first attention block even with
`enable_model_cpu_offload`. 48 GB is the floor.

## Four things that cost 50 minutes, so they are not repeated

1. **Never override `dockerStartCmd` without re-running the image's own
   `/start.sh`.** It is what starts RunPod's in-container agent. Without it
   the pod reports `runtime: null` for ever and the HTTP proxy has no route,
   so every request to the pod's port returns 404 while the pod says RUNNING.
   Two pods, two machines, two clouds, identical silence. Run the job with
   `nohup ... &` and then `exec /start.sh`.
2. **`black-forest-labs/FLUX.1-schnell` is now a GATED repo.** It returns 401
   without a Hugging Face token. `lzyvegetable/FLUX.1-schnell` is an ungated
   diffusers-format mirror of the same weights and is what the worker uses by
   default. The licence is unaffected - schnell is Apache-2.0 whoever hosts
   it - but it is a third party, so switch back to the official repo once the
   seller has an HF token (free, it is just a licence click-through).
3. **Pin diffusers.** 0.33+ calls `torch.accelerator`, which arrived in torch
   2.6; the RunPod images ship 2.4. `diffusers==0.31.0` with
   `transformers==4.46.3` works.
4. **Community hosts can have a broken CUDA runtime.** One answered
   `nvidia-smi` correctly, exposed every `/dev/nvidia*` node, and still gave
   `CUDA unknown error` from `torch.cuda.init()` for 200 seconds of retries.
   The secure host was ready on the first try. `launch_gen.py` waits for
   `torch.cuda.is_available()` rather than trusting `nvidia-smi`.

## The honest defect rate: 5 of 16

- `SAMPLE-01` Whitby screenprint: large garbled lettering, "W ITBEY".
- `SAMPLE-06` Brighton collage: "N2Z1" across the seafront.
- `SAMPLE-15` kingfisher linocut: a fake artist's monogram, bottom left.
- `SAMPLE-00`, `SAMPLE-05`: scrawled signature marks in the lower corner.

guidance_scale is 0, so negative prompts do nothing - "no text" sits in the
positive prompt and is plainly not enough. 31% must be read and regenerated,
and the budget below carries that factor. Two cheap reductions worth trying
before the full run: drop or reword the G6 vintage-travel-poster grammar,
which is the grammar that invites lettering, and crop the bottom 4% of every
panel, which is where the fake signatures land.

`SAMPLE-13` also shows the G7 specimen-chart grammar failing - one kingfisher
instead of nine studies. Worth a prompt rewrite, not a blocker.

## What a listing costs, and why it is not one GPU image

Three multipliers are free, and they are the whole argument:

- **Palette.** `recolour.py` maps a finished panel's lightness through a
  different ramp in about 25 ms of CPU. Three colourways from one generation.
  This sits inside the four-colourway cap the wall-art branch set after
  measuring store 1 at 89% near-duplicates.
- **Geometry.** `gen_geometric.py` draws the hard-edge block in code. That
  block is 9.12% of the competitor corpus and diffusion is worse at it.
- **Framing.** Print sheet plus all three frame colours renders in 0.78 s on
  one CPU core. 6M designs is 1,300 core-hours, about $52.

Run `python3 wallart-data/capacity.py` for the table. At the measured rate:

    6,000,000 listings
      547,200 drawn in code, free
    1,817,600 GPU base images
    2,643,782 generations once the 31% text gate is paid for
        3,028 GPU-hours = $1,787
                          + $52 CPU = $1,839 all in
          858 GB of panels on R2 = $13/month

Ten 48 GB GPUs at once finishes it in 12.6 days; twenty-five in 5 days. The
bill is the same either way, only the calendar changes.

## Capacity, in subjects not dollars

Each place subject yields 58 GPU bases (11 techniques x 6 grammars, minus the
contradictions) and so 174 designs. Each creature subject yields 38 bases and
114 designs.

    held today     10,563 subjects -> 1,573,482 designs
    6M target      31,338 subjects needed

So 1.57M is reachable with the lists already in the repo, and the gap to 6M
is a subject-sourcing job, not a model limit - 33,900 further IP-free atoms
were already identified in `scale_plan_millions.md`.

## Not yet measured, and worth measuring before the full run

- A 4090 with the transformer quantised to NF4 fits in about 12 GB and rents
  at $0.34/hr community. If it reaches 1,900 images/hour the bill drops by
  roughly three quarters. This is the single biggest open lever.
- 640x896 instead of 848x1200: about 1.75x faster, and the listing photo only
  ever shows the panel at 1188px wide inside the mockup.
- Batch 8 rather than 4 on a 48 GB card.

## Still blocking a scaled run

`wallart/plan.json` has `pic_base: ""`. There is no R2 bucket for wall art
yet, so generated panels have nowhere to live. One bucket per eBay account is
the established rule; t-shirts for M12K go to `tshirt-m12k`.
