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

## The 12 Oct gate incident, and what each fix was worth

Three shards relaunched with the full gate stack came up rejecting 100%.
It was three separate faults wearing one coat, and the measurements are
worth keeping because each was found the same way: regenerate the rejected
panels with the gates off and LOOK at them.

    1. BUSY_FLOOR fitted to the wrong material. 0.10/0.18 was measured on
       141 old-grid panels at 52% median busyness. The work left is the new
       kinds and the flat techniques - screenprint's own median is 28.9% -
       so the floor rejected 46% of generations, including every minimal
       poster in the catalogue. Now 0.035/0.055, which rejects 4 of the 80
       it was shown and they are the right 4.

    2. The crop-line fix over-correcting. Reading the whole panel is right,
       but rejecting on a mark's FULL size threw a panel away for a 2%
       sliver that the crop removes anyway. The box is now clipped to what
       survives.

    3. CLIP NEVER SAW "no text". FLUX reads with T5 at 256 tokens and CLIP
       at 77. The clause started at word 60 of an 82-word prompt, and every
       batch printed that it had been truncated. Moving it to word 14, and
       taking the word "poster" out of the screenprint description, took
       text rejection from 60% to 28% on the same jobs.

Still above the 8-12% a healthy shard runs at, so text is not finished.

## The people gate, settled 13 Oct

The gate was rejecting panels for PEOPLE at roughly 2.5% of everything
generated, which on one shard read as 39% of all rejections against a
measured 2.3% people rate - a gap big enough that it was either the gate
misfiring or real figures, and guessing either way was expensive.

So: 60 people-rejected panels regenerated with every gate off, written to
`wallart/pplaudit/`, downloaded through the public r2.dev URL, laid out
three to a contact sheet and LOOKED AT. The pod was deleted straight after;
it bills until deleted.

**36 of the 60 genuinely had people in them.** Three had a whole person
where the subject should have been - "shaggy ink cap" came back a boy's
portrait, "lily asiatic" a dozen human silhouettes, "Helmsley" a man in a
checked shirt. The other 33 were pedestrians in townscapes. Turning the
gate off would have shipped all of them.

**24 were false alarms** - a bowl of cherries, a cup of coffee, a moth, the
moon. The score bank in quality_gate.py had no label for "an object on a
table", so a still life matched nothing on the pass side and "a person
standing in the scene" won by default.

Two things came out of it, and they are very different sizes.

### The prompt, which is the big one

The no-people clause started at word 62 and ran to word 87. CLIP stops at
about word 55. **This is the same bug as the no-text clause, in the same
place, found a day later** - I moved `_CLEAN` into the window, watched the
text rejects fall, and did not think to look at the clause sitting next to
it. For the whole run so far FLUX has been drawing streets having never
been told to leave them empty.

Fixed by putting a short form - "unpeopled, empty of people" - beside
`_CLEAN`, keeping the long one at the end for T5. Verified against the real
CLIP tokeniser for all six builders. SKUs hash kind|subject|tech|gram|pal
and never the prompt text, so nothing already made is remade - checked
against all 60 manifest rows, zero SKUs move.

### The score bank, which is the small one

SHIPPED, commit b89a04c. Four object labels added to the pass side:
false alarms 18 -> 9, true catches 34 -> 33. The one catch lost is a
risograph of ligularia with a five-pixel figure in it, 0.875 -> 0.333. The
three catastrophic panels are untouched - 0.927 -> 0.907, 0.992, 0.993.
Freed: a champagne flute, a flat white, a gargoyle spout, a bowl of
cherries, a lappet moth, dried chillies, a cup of matcha, a bee-eater, and
Dartmouth harbour at 0.829, which is close enough to the line to be worth
a second look if harbour scenes start showing figures.

The first draft was wrong in a way worth recording: adding "a building or
architectural detail with nobody in it" to the pass side halved the false
alarms AND cut true catches from 34 to 19, because that label describes
exactly the townscapes that DO have pedestrians and hands every one of them
a strong pass match. It was the most plausible label in the set and the only
harmful one. The comment in quality_gate.py says so at the point of
temptation.

**That test set cannot measure the miss rate.** Every panel in it was
chosen because the live gate rejected it, so it is selected for high
scores. It can say which rejections a changed bank would stop making, and
whether the three catastrophic panels still fail. It cannot say what a
changed bank would start letting through, and nothing here should be read
as if it could.

The 60 panels, the labels I read off them by eye, and the calibration
scripts are in the scratchpad, not the repo - they are a 11 MB test set
that costs about $0.02 of GPU to rebuild from `wallart/pplaudit/`.

### What is NOT fixed

Thirteen of the 24 false alarms are townscapes with no visible figures -
Vilnius, Hong Kong, the Norfolk coast. The gate cannot tell those from a
street with three-pixel pedestrians, and neither could I at a glance.
Leave them rejected: the cost of being wrong is shipping people.

Also noted while measuring, neither acted on: `_CLEAN` spends 24 of CLIP's
77 tokens on eleven ways of saying "no text", and the palette clause does
not reach CLIP at all - T5 carries the colour on its own. Both measurable
with the offline bench, both one-change-at-a-time jobs for later.

## What is NOT resumable yet

The CPU stage (`pipeline.py`) rebuilds its listings from whatever panels it
is given, so it is cheap to re-run and does not need resuming. The eBay
upload files are not written yet.
