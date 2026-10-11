# Scaling to millions: how it is structured

11 October 2026. The wall art goes on an unlimited store, so the listing
ceiling that governs the t-shirt account does not apply. The target is **2M+
designs on the main store and millions more across the others**.

## The one structural fact that makes this affordable

**Only the artwork costs money. Everything after it is free.**

    FLUX generation      GPU   - the only real cost
    frame compositing    CPU   - PIL, milliseconds, 3 frames per design
    size variants        none  - the same mockup serves A4/A3/A2; only the
                                 print file is rendered per size, and only on sale
    titles, CSV          CPU   - free

So the plan is: **generate each artwork once, composite everything else.**
A design becomes 9 eBay variations (3 frames x 3 sizes) for the price of one
image. That is the whole leverage.

## The subject mix is weighted to the décor leader, not to what we happen to hold

The seller asked for "similar stuff" to what already sells there. Rather than
guess, the mix follows Fy!'s **measured** block shares from
`subject_blocks_corrected.md` — Fy! being the décor leader, where the seller's
own source data was found to be close to the inverse shape.

| block | Fy! share | designs at 5M | atoms needed |
|---|---|---|---|
| animals | 20.6% | 1,030,000 | 7,803 |
| vintage register | 17.3% | 865,000 | 6,553 |
| botanical | 16.9% | 845,000 | 6,402 |
| abstract | 14.0% | 700,000 | 5,303 |
| landscape | 8.5% | 425,000 | 3,220 |
| city / place | 7.9% | 395,000 | 2,992 |
| figure | 3.4% | 170,000 | 1,288 |
| food / drink | 2.9% | 145,000 | 1,098 |
| space | 1.4% | 70,000 | 530 |
| sport | 1.1% | 55,000 | 417 |
| vehicle | 0.8% | 40,000 | 303 |
| typography | 0.5% | 25,000 | 189 |
| | | **5,000,000** | **36,098** |

Note `vintage` is a **register applied across the other blocks**, not a block
of its own — a vintage botanical and a vintage place poster both count there.
And typography stays at 0.5%, deliberately: it is 6.2% of the seller's own
source and the worst performer in their watcher data.

## Atoms: 10,563 held, 36,098 needed

At 132 designs per atom (11 techniques x 4 valid grammars x 3 palettes), 5M
designs needs about 36,000 subject atoms. All of the gap is enumerable and
IP-free:

| source | atoms |
|---|---|
| UK moths — already listed in `enumerable_subject_lists.md` | 2,500 |
| world birds, commercially viable subset | 5,000 |
| world cities and landmarks | 10,000 |
| garden and wild plants, flowers, trees | 8,000 |
| butterflies and moths, world | 4,000 |
| minerals, shells, fungi, feathers | 3,000 |
| constellations, moon phases, celestial | 500 |
| dog, cat, horse, cattle and poultry breeds | 900 |
| **new atoms** | **33,900** |

Added to the 10,563 held, that is 44,463 — comfortably past the 36,098 needed,
with headroom to drop any atom that generates badly.

## Pipeline

    1  atoms      enumerable lists -> subjects.jsonl        (CPU, free)
    2  prompts    subject x technique x grammar x palette   (CPU, free)
                  incompatible combinations dropped
    3  generate   FLUX.1 schnell, 4 steps, 848x1200         (GPU - the cost)
                  sharded by atom range, resumable, streams straight to R2
    4  gate       OCR reject (any legible text) + pHash/CLIP near-dup reject
    5  frame      3 mockups per design on the 2000x2000 contract   (CPU, free)
    6  build      titles as keyword stacks, eBay CSV               (CPU, free)

**Sharding.** Pods take disjoint atom ranges, so they never collide and no
coordination is needed. Every image written is recorded, so a pod that is
stopped — or runs out of balance — restarts exactly where it left off. That
was a hard requirement from the start and it is what makes a run safe to
interrupt.

**Nothing is held on the pod.** Images stream to R2 as they are made. A pod's
disk is wiped when it stops, so anything kept locally is lost.

## Storage, which is now the real constraint rather than GPU

At 5M designs:

    print master   1200x1697 JPEG q92   ~300 KB   ->  1.5 TB
    3 mockups      2000x2000 JPEG q90   ~250 KB   ->  3.8 TB
                                                      -------
                                                      5.3 TB

Cloudflare R2 is $0.015/GB/month with **no egress charge**, so that is about
**$80/month**, and egress being free is why R2 rather than S3 — eBay will be
serving those images constantly.

The wall-art bucket still does not exist: `wallart/plan.json` has
`pic_base: ""`. **This is the blocker for the full run.** The first batch can
live on the pod; 5M images cannot.

## What is still to be measured

GPU cost per image, from the batch running now. The estimate spans $85 to $345
for 1.8M depending on card and throughput, which is too wide to plan on. The
measured rate replaces it.
