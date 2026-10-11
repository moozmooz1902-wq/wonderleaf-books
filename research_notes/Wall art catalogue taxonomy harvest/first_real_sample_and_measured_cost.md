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

---

# Update, same night: the numbers that got it under $500

The target changed to 5,000,000 listings - 3,000,000 on the main store and
500,000 on each of four others - with a ceiling of $500. It fits, at
**$244 to $361**. `wallart-samples/PLAN.md` is the costed plan;
`wallart-data/capacity.py` is the model. What changed:

## 1. A 24 GB card, via NF4

Measured on an RTX 4090 with the transformer and T5 quantised to NF4:

    704x1008 batch 4   1,782 gen/hr   16.1 GB peak
    848x1200 batch 4   1,295 gen/hr   18.4 GB peak
    batch 8            no faster than batch 4 at either size, just fatter

Against the A40's 873 gen/hr that is only 1.5x, because NF4 dequantises on
the fly and gives back about 30% of the speed. The win is not the card, it is
the **hourly price**: a 4090 rents at $0.34 community against the A40's $0.59
secure, so the cost per image falls from $0.00068 to $0.00019.

704x1008 is 38% faster than 848x1200 and, inside the mockup, indistinguishable
(`wallart-samples/06_resolution.jpg`). The art is only ever shown 1,106 px
wide in the listing photo; the print file is upscaled on order anyway.

## 2. The text defect went from 31% to 7.7%

Two changes, and the second is the one that matters:

- **G6_poster deleted.** "As a vintage travel poster" asks for typography by
  definition. It produced the two worst defects in the first sixteen.
- **`gen/gen_gated.py` reads its own output.** EasyOCR on the same GPU, with
  a confidence and area floor so faint marks do not cause thrashing; anything
  carrying text is regenerated with a new seed, twice before it is let
  through. On 48 designs it caught four and all four came back clean:

      WA-0000003   "SKYE" x2 at conf 1.00 / 0.91
      WA-0000018   "LALE", "LOND", "MAW CITT H.16, 2013"
      WA-0000013   "Ma2,2018"          a fake dated signature
      WA-0000002   "2195 4"            a fake inventory number

  Throughput with the gate on was 1,863 gen/hr, slightly *better* than the
  ungated bench, so the gate is free in practice. The budget still uses the
  conservative 1,549.

Cost of the gate at 7.7%: 656 GPU-hours instead of 606. Cost of not having
it: one listing in thirteen with a garbled word printed across it.

## 3. A million designs that cost no GPU at all

`gen_line.py` - thirteen families of minimal line work, 0.156 s each on one
CPU core, 19,000 per core-hour. This is the block the seller picked out, and
it carries 20% of the catalogue for nothing.

Two things it does that matter, both in service of the full-bleed request:

- **Terminating vs spanning.** Anything that ends - a sun, a closed contour,
  the end of an arc - stays inside a 7% safe box. Anything that continues - a
  horizon, a dune ridge, a wave - is drawn 6% *past* the edge. The moulding
  eats 1.06% of each side, so a spanning line reads as going behind the frame
  and a terminating one is never clipped.
- **An ink-coverage guard.** The random draw can produce a near-blank sheet.
  Anything under 1.5% or over 93% ink is redrawn with a new seed.

Four families needed fixing after the first look: contour varied only its
phase and produced three identical designs in thirteen; botanical drew
chevrons for leaves; arch swept its crown 0 to pi and joined the left foot to
the right shoulder, drawing an hourglass; one-line used up to six lobes and
read as a test pattern.

## 4. Margin or full bleed, decided per design

`layout.py`. Margin is 8.5%. Drawn and painted techniques take the margin,
flat and graphic ones go edge to edge, and 28% of each group takes the other
treatment so neither look is a rule. Then `edge_risk()` measures the strip the
moulding will cover against the whole image and overrides to a margin above
1.05 - calibrated as centred subject 0.09, landscape to the edge 0.95, drawn
dark border 1.21, subject against the edge 1.45. A false positive costs a
margin print; a false negative ships a sliced subject.

One thing that only showed up on screen: a code-drawn design on bone paper
inside a pure white margin reads as a grey rectangle floating in a white one.
`paper_of()` samples the panel's own border and, if it is near-uniform, prints
the margin in that colour instead.

## 5. Two more things learned about RunPod

- **Community hosts can be dead on arrival, repeatably.** Two of two tried
  tonight answered `nvidia-smi`, exposed every `/dev/nvidia*` node, and never
  gave torch a usable device. The launcher now gives up after 200 s with
  `CUDA_DEAD_ON_THIS_HOST` instead of going on to download 24 GB of weights
  first. Production needs a supervisor that recreates the pod elsewhere; the
  75/25 column in the plan is what it costs if a quarter has to fall back to
  secure.
- **`interruptible: true` and `networkVolumeId` both exist on `POST /pods`.**
  Spot pricing and a shared model cache are the two obvious further savings
  and neither has been tried yet.

---

# Update: no people, and eyes that are not wrong

The seller's conditions for going ahead: no human figures, animal eyes that
are actually eyes, and nothing that reads as generated. 129 panels were made
specifically to test those, weighted toward the cells most likely to fail -
66 close-up animal portraits across every technique, and 30 townscapes and
seafronts, which are the places that invite figures.

## The eyes are mostly fine, and the failures have a pattern

Seven of 93 creature panels came out with the eyes wrong - 7.5%. Four of the
seven were ROBINS and five of the seven were WET techniques (oil impasto,
watercolour, ink wash, palette knife). A small bird's face is a few dozen
pixels across and a wet-on-wet wash will not hold an eye at that size.

That combination is now simply not generated. `prompts.ok()` refuses a
close-up portrait of a small-faced bird in a wet technique - a tiny slice of
the grid that accounted for five of the seven failures. The same birds still
appear in habitat and minimal grammars, and in flat techniques, where they
came out clean every time.

`EYES = "exactly two eyes, both eyes clear and correctly placed"` is now in
every creature prompt.

**Resolution does not fix eyes.** 24 high-risk bird portraits were generated
at 704x1120 and at 848x1328 from the same seeds. 848 costs 43% more per image
(1,118/hour against 1,601) and did not correct a single face. The whole
catalogue is generated at 704.

## People: measured, not assumed

Of 30 townscapes deliberately prompted at places that invite figures, 11 had
some figure and only 2 had one big enough to read as a person. Not one panel
in 129 produced a human face. `NO_PEOPLE` is in every place prompt;
creature prompts get a variant that does not say "no faces", because the
animal's face is the subject.

## CLIP zero-shot does not work as a gate, and is not being shipped

It was the obvious tool and it failed both tests on labelled data:

    EYES   catching 71% of the bad ones means regenerating 34% of
           everything, at 12.8% precision. Useless.
    HUMAN  the failure score is LOWER on the panels with figures
           (0.362) than on the ones without (0.593). Inverted - the
           captions fire on townscapes in general, not on figures.

`quality_gate.py` is kept because `calibrate()` is how the thresholds in this
pipeline get set, but no CLIP gate is in the production path. A gate that
does not separate is worse than no gate: it costs money and gives false
confidence.

## The real defect was the fake signature, and the fix is a crop

Looking at the panels rather than the OCR log: EasyOCR catches printed
lettering and does not catch a cursive signature, because a scribble is not
characters. Roughly one panel in four carried one - a scrawled name, a
"(C) T.S.1013", a fake date. It is the clearest tell that the work is
generated, and it credits a painter who does not exist.

Two approaches were tried. **Painting them out** (`declutter.py`) works on
flat ground and fails on busy ground, and measuring why is the useful part:

    mark density    flat background   signature 0.13-0.83  clean 0.001-0.29
                    busy artwork      signature 0.49-0.52  clean 0.45-0.85

On a splattered or linocut ground the whole band reads as marks, so density
cannot separate them. Adding a neighbourhood test - a signature is a busy
little patch in quiet space, fur is a busy patch among more fur - helped, but
only cleared about half.

**Cropping works.** The vertical position of every detected mark was
measured across the labelled set:

    p10 0.972   p50 0.972   p75 1.000   p90 1.000

    cropping the bottom  6% removes  91%
    cropping the bottom 10% removes  96%
    cropping the bottom 12% removes 100%

So the worker now generates 704x1120 and throws the bottom tenth away. It
costs 11% more pixels - measured at 1,601 generations/hour against 1,782 -
and it is deterministic, with no risk of smearing the artwork. `declutter.py`
stays as a second pass for the residual on quiet grounds.

An hour was spent trying to be clever before measuring where the marks
actually were. The measurement took two minutes and answered it.

## Where the budget landed

    5,000,000 listings
      937,500 base images
    1,065,341 generations at 12% rejection
          665 GPU-hours
         $226 community + $22 CPU  =  $249
         $333 at a 75/25 community/secure mix + $22  =  $355
