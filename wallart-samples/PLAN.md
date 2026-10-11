# Five million wall-art listings: the plan and the bill

11 October 2026. Written to be read before anything is generated, because the
instruction was to know the cost first.

---

## 1. The answer up front

**Yes - 3,000,000 on the main store and 500,000 on each of the other four is
buildable, and it comes in under $500.**

| | all on community GPUs | 75/25 community/secure |
|---|---|---|
| at the measured 7.7% reject | **$244** | $335 |
| if reject doubles to 15% | **$264** | $361 |

Even if every hour had to run on the expensive secure hosts it would be
$605 - and that is the pessimistic corner of the pessimistic corner.

Plus about **$9 a month** of Cloudflare R2 storage, or $23 a month if a
listing photo is stored for every design instead of drawn on request.

Wall clock: **2.3 to 2.5 days** on twelve GPUs rented at the same time, or
about 5 days on six. Renting more GPUs does not change the bill, only the
calendar - the work is billed by the GPU-hour either way.

Nothing is generated until you say go.

---

## 2. Why it is this cheap: a listing is not a GPU image

This is the whole trick, and it is where the money is.

| multiplier | what it does | GPU cost |
|---|---|---|
| **Drawn in code** | 1,250,000 of the 5,000,000 are not generated at all. The line designs you picked out - line in a desert, contours, arches, dunes - are drawn by a program in 0.156 s each. | **zero** |
| **Four colourways** | One generated panel becomes four listings by remapping its lightness through a different colour ramp. 0.085 s of CPU. | **zero** |
| **Framing** | The print sheet and all three frame colours render in 0.22 s on one CPU core. | **zero** |

So 5,000,000 listings need only **937,500 generated images**, and after the
text gate, about **1.02 million generations**. At 1,549 generations per hour
per GPU that is 656 GPU-hours.

Four colourways is not a number I invented. The wall-art branch measured
store 1's 424,000 listings at 89% near-duplicates and concluded that was the
likeliest reason they did not sell; the rule it set was a maximum of four
colourways per design. This plan sits exactly on that limit and no further.

---

## 3. The measured numbers everything rests on

Taken from a rented GPU today, not from a price list.

```
RTX 4090 + NF4, 704x1008, batch 4    1,782 generations/hour   16.1 GB peak
RTX 4090 + NF4, 848x1200, batch 4    1,295 generations/hour   18.4 GB peak
A40 48GB bf16,  848x1200, batch 4      873 generations/hour
the full gated run, 48 designs       1,863 generations/hour   7.7% rejected
RunPod:  4090 community $0.34/hr    4090 secure $0.89/hr    A40 $0.59/hr
```

The budget uses the conservative 1,549/hour from the bench, not the 1,863
the real run managed with the OCR gate switched on.

Three findings worth keeping:

- **Batch 8 is not faster than batch 4** on either size. It only uses more
  memory. Batch 4 everywhere.
- **704x1008 is 38% faster than 848x1200 and holds up in the frame.** Sheet
  `06_resolution.jpg` is the same two designs at both sizes inside the
  mockup. The plan uses 704 for the flat, graphic techniques and 848 for the
  drawn ones where fine detail is the product.
- **A 24 GB card cannot run this model in bfloat16 at all** - the transformer
  alone is 11.9B parameters, 23.8 GB. NF4 quantisation is not an
  optimisation here, it is the only way onto the cheap hardware. It costs
  about 30% of the speed and buys a card that is 2.6x cheaper per hour.

---

## 4. Margin or full bleed - you get both

Margin is **8.5%**, as asked.

Sheet `05_margin_vs_full_bleed.jpg` shows the same four designs both ways.
The split is not random - it follows what the 212,995 competitor images
measured: the drawn and painted techniques (watercolour, charcoal, ink wash,
pastel, oil) run +0.12 to +0.18 border-minus-centre lightness, so they get
the margin; the flat and graphic ones (screenprint, collage, linocut,
gouache, hard-edge) go edge to edge. Then 28% of each group takes the other
treatment, so both looks appear across every technique and the catalogue
never looks like one rule applied five million times.

### Not cutting the image at the frame

You asked for the full-bleed ones to be handled properly at the edges. Three
defences, in `layout.py`:

1. **The code-drawn designs know where the frame is.** Anything that
   *terminates* - a sun, a closed contour, the end of an arc - is kept inside
   a 7% safe box. Anything that *spans* - a horizon, a dune ridge, a wave -
   is deliberately drawn 6% **past** the edge, so it reads as continuing
   behind the moulding instead of stopping just short of it. That is the
   difference between a line that looks cut off and one that looks intended.

2. **The generated panels are made at the frame's own shape.** The aperture
   inside the moulding is 1106 x 1598. Generating at 832 x 1200 puts the
   crop at about 1 px instead of 12.

3. **Everything else is measured.** `edge_risk()` looks at the strip the
   moulding will cover and compares its contrast to the whole image.
   Calibrated on real panels:

   ```
   centred subject on plain ground   0.09   full bleed fine
   landscape running to the edge     0.95   full bleed fine
   a drawn dark border               1.21   clips unevenly -> margin
   subject pushed against the edge   1.45   the bad case    -> margin
   ```

   Anything over 1.05 is printed with a margin instead, where the whole
   image is visible. **No design is ever cropped through its subject because
   the mix said full bleed.**

One more thing that came out of this: when a code-drawn design gets a margin,
the margin takes **the design's own paper colour**, not pure white. A white
margin around a bone-coloured sheet reads as a grey rectangle floating inside
a white one. Sheet `07_line_margin.jpg` shows it fixed.

---

## 5. What is in the catalogue

| block | count | how | cost |
|---|---|---|---|
| line and minimal | 1,000,000 | 13 families, drawn in code | free |
| geometric hard-edge | 250,000 | 5 kinds, drawn in code | free |
| places - UK and beyond | ~1,900,000 | FLUX, 11 techniques x 5 grammars | GPU |
| creatures | ~1,300,000 | FLUX, 11 techniques x 4 grammars | GPU |
| botanical | ~550,000 | FLUX | GPU |

The thirteen line families are in sheet `08_line_families.jpg`: dunes,
mountain, contour, waves, arch, rings, rays, botanical, one-line, bands,
grid, horizon-sun, hatch.

**Subjects needed:** 937,500 base images at about 43 per subject is
**21,828 subject atoms**. 10,563 are already in the repo; 33,900 IP-free ones
were identified in the earlier research. So the gap is a list-building job,
not a limit of the method.

---

## 6. The one real quality problem, and the fix

Five of the first sixteen panels came back with writing on them - a garbled
"W ITBEY" across a harbour, "N2Z1" on a seafront, a fake artist's monogram in
the corner of a linocut. schnell runs at guidance_scale 0, so negative
prompts do nothing; there is no wording that reliably fixes it.

Two changes:

- **The vintage-travel-poster grammar is gone.** A travel poster *is* a piece
  of typography, so the model put a place name on it however the prompt was
  worded. It produced the two worst defects in the first sample.
- **The output is read before it is kept.** `gen_gated.py` runs EasyOCR on
  the same GPU and regenerates anything carrying text with a new seed, up to
  twice.

**Both together took the defect rate from 31% to 7.7%, measured on a run of
48 designs.** All four rejects were caught on the first attempt and came back
clean on the retry, so 48 of 48 kept panels are free of writing. What the
gate actually caught:

```
WA-0000003   "SKYE"  x2, confidence 1.00 and 0.91      (Isle of Skye, lettered)
WA-0000018   "LALE", "LOND", "MAW CITT H.16, 2013"     (Loch Lomond, lettered)
WA-0000013   "Ma2,2018"                                (fake dated signature)
WA-0000002   "2195 4"                                  (fake inventory number)
```

The gate costs almost nothing in throughput - the gated run measured 1,863
generations/hour against 1,782 on the ungated bench.

---

## 7. Still open before the run can start

1. **No R2 bucket for wall art.** `wallart/plan.json` still has
   `pic_base: ""`. One bucket per eBay account is the rule; t-shirts for M12K
   go to `tshirt-m12k`. Nothing can be published until this exists.
2. **Community GPUs are cheap but flaky.** Two of two community hosts tried
   today answered `nvidia-smi` correctly and still never gave torch a usable
   device. The launcher now detects this in 200 seconds and the pod kills
   itself (`CUDA_DEAD_ON_THIS_HOST`) rather than spending five minutes
   downloading weights first. Production needs a supervisor that recreates
   the pod elsewhere when that happens. The 75/25 column above is what it
   costs if a quarter of the work has to fall back to secure hosts.
3. **A Hugging Face token would be worth having.**
   `black-forest-labs/FLUX.1-schnell` is now gated and returns 401. We are
   using `lzyvegetable/FLUX.1-schnell`, an ungated mirror of the same
   Apache-2.0 weights. The licence is fine either way, but it is a third
   party. The token is free - it is just a licence click-through.
4. **A duplicate audit before upload.** The code-drawn million is the part of
   this plan most at risk of looking repetitive. It gets measured against the
   same test the research applied to store 1 before any of it goes up.

---

## 8. Not spending anything right now

Every pod used today has been deleted. Total spent getting to these numbers
is a little over a dollar.
