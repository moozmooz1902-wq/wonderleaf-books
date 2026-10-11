# How to pause and continue

The seller funds this in $100 blocks, so the run has to survive stopping
dead at any moment - including RunPod simply switching the pods off when the
balance hits zero - and pick up from exactly the same place.

## It already does. The bucket is the bookmark.

There is no separate progress file to lose. A panel that exists in R2 is
done; a panel that does not is not. On start, every pod lists the prefix and
drops the jobs it finds, then generates only the rest.

    python3 gen_gated.py --subjects subjects.json --r2-prefix wallart/v1 --resume ...

Two things make that safe, and the first one took a rewrite to get right.

**A SKU says what a design IS, not where it sat in a list.** The first
version numbered jobs by position after a seeded shuffle. That is
reproducible only while the subject list never changes - add one flower and
every SKU after it shifts, so a half-finished run would regenerate
everything it had already paid for. The SKU is now
`WA-<64-bit blake2b of kind|subject|technique|composition|palette>`.

Proven: adding two subjects to a 12,834-job list produced 288 new SKUs and
lost **zero** old ones.

**64 bits, not 32.** The first attempt used crc32 and collided on the very
first run of 12,834 jobs. 2^32 collides past about 65,000, and 937,500 jobs
would collide roughly a hundred thousand times, each one quietly throwing
away a design. There is a collision check in `expand()` that refuses to run
rather than lose work; that check is what caught it.

## Stopping on purpose

    for p in <pod ids>; do curl -X DELETE https://rest.runpod.io/v1/pods/$p; done

Deleting a pod loses nothing: every panel was uploaded as it was made and
the container disk holds nothing that matters. `--max-hours N` also makes a
pod stop itself, so a forgotten pod cannot run all night.

## Starting again after a top-up

Exactly the same command. The pods list the bucket, see what is there, and
carry on. Run `python3 status.py <panels in bucket>` first to see where
things stand and what the next $100 buys.

## The grid, the pool, and why they are different numbers

`gen/subjects.json` holds 5,204 subjects in six kinds. Expanded against 14
techniques, 26 compositions and 5 palettes, with the contradictions dropped
and the minimal compositions capped, that is a **grid of 1,176,784 base
images** - 4,707,136 listings at four colourways.

The catalogue only needs 937,500 bases (5,000,000 listings less the
1,250,000 drawn in code, over four colourways). So every pod runs with

    --pool 960000

which takes the first 960,000 of the grid in SKU order. That order is a
stable pseudo-random shuffle, so the pool is a fair mix of every kind,
technique, composition and palette - checked: 476 distinct subjects in the
first 500 jobs, longest same-subject run 2, monochrome 20.6% of the pool
against 21-23% measured in the market.

The 216,784 jobs outside the pool are **spare capacity, not waste.** Raising
`--pool` is the only change needed to use them, and nothing already
generated is regenerated, because a SKU is a hash of what a job is.

Rebuild `gen/subjects.json` after editing any subject list:

    python3 build_subjects.py

It refuses to write a list with a repeated subject, because the same subject
twice inside one kind is the same SKU twice and `expand()` stops the run on
a collision.

## Adding subjects later is safe, and this was verified

Today's change took the grid from 284,665 to 1,176,784 base images - 2,966
new subjects, three new kinds, three new techniques, two new palettes - and
**all 284,665 old SKUs are still jobs in the new grid. Zero lost.** The
12,834 panels already sitting in the store buckets stay done, and `--resume`
still sees them.

## Owed: a text sweep over what was made before 11 Oct 22:00

Panels generated before that time were gated on the CROPPED image, so a
title straddling the crop line could get through - GUATEMALA across the
foot of an Antigua screenprint is the one that was caught by eye. The gate
now reads the full generation, but the panels already in the buckets were
not checked that way.

The sweep is cheap and has not been run yet: on one pod, list the four
store prefixes, run EasyOCR over the bottom fifth of each panel, and feed
the offending SKUs back through gen_gated.py with --jobs. At roughly 50 ms
a panel, a million panels is about 14 GPU-hours, so it is worth doing once
at the end rather than repeatedly.

## What is NOT resumable yet

The CPU stage (`pipeline.py`) rebuilds its listings from whatever panels it
is given, so it is cheap to re-run and does not need resuming. The eBay
upload files are not written yet.
