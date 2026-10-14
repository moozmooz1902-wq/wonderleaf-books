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

### The prompt, which I got wrong

The no-people clause starts at word 62 and runs to word 87; CLIP stops at
about word 55. That part is true. The conclusion drawn from it - that this
was the same bug as the no-text clause and wanted the same fix - was not.

A short form, "unpeopled, empty of people", went in beside `_CLEAN`, one
shard was relaunched onto it, and the other eleven were left on the old
prompt as the control. Marginal, past the retry backlog:

    new prompt  +189 rejections, +112 PEOPLE  = 59.3%
    old prompt  +139 rejections,  +58 PEOPLE  = 41.7%

**It made people MORE common**, and the new arm was carrying the score-bank
fix too, which pushes the other way, so the prompt alone did more than that
17-point gap. Reverted in d9ca0d9 after two and a half hours, before the
other eleven shards could rotate onto it.

schnell runs at guidance_scale 0.0. No classifier-free guidance means
negation is not handled at all: "no people" is not an instruction, it is
the token "people", and moving it into the most attended part of the prompt
asks for exactly what it names. Attacking this from the prompt side at all
means saying what SHOULD be there - "empty streets at dawn" - never what
should not, and that is untested.

**This casts doubt on the no-text fix as well.** `_CLEAN` is eleven
negations sitting inside the window by the same reasoning. The text reject
rate fell after it moved and I credited the move, but no controlled
comparison was ever run, and this result is a reason to suspect it was
neutral or worse. The note is at the top of prompts.py. Measure it the same
way - one shard, eleven controls, marginal rates - before trusting either
direction.

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

## Duplicate audit at 226,992 panels, 13 Oct

    panels            226,992
    distinct hashes   226,990   (exact repeats: 2)
    near duplicates     0.648%  at 24 bits of 256
    per bucket        lunar-kms 0.599  posterleaf-store1 0.627
                      luxvia-art 0.669  mercury-usm 0.682

Against 0.67% at 168,515 and 0.826% at 63,533, so it is still falling as
the catalogue grows, which is what the expanded grid was for. The wall-art
branch blames 89% near-duplication for 424k listings not selling; this is
two orders of magnitude under that.

Full result in `notes/audit_226992.json`, including the closest pairs.

The comparison pass took 95 minutes for 227k panels and the pod ran 2h20m
in all. It is O(n^2) - the code has said since the first audit that it will
not scale to a million - and this run is where that stopped being
theoretical. **Do not simply run it again at 500k**: four times the work, so
roughly six hours and $2, and at 960,000 it is nearer a day. The next audit
needs the LSH bucketing pass the comment describes, or a random sample of
100k rather than the whole catalogue.

The first attempt at this audit crashed and reported success; see the
commit "the duplicate audit crashed at 222k and reported success" for what
was wrong and what was fixed. The fixed version lost zero of 226,992.

## The _CLEAN clause A/B: no detectable effect, and why that is the finding

Ran 13 Oct 08:33-11:20. One shard with the no-text clause at the END of the
prompt, outside CLIP's window, against eleven with it inside - the shipped
behaviour since 12 Oct.

    interval 1 (09:19-10:17)   test 5.73% text/gen   controls 3.67%
    interval 2 (10:17-11:18)   test 2.42% text/gen   controls 3.17%

The two intervals disagree in direction. Interval 1 was contaminated - it
starts at the test shard's 373rd panel and a fresh shard carries its retry
backlog to about its 700th. Interval 2 is clean, and on it the test shard
sits 1.09 standard deviations below the control mean, inside the control
range:

    2.42 TEST | 2.54 2.62 2.81 2.91 2.98 3.02 3.07 3.13 3.14 4.58 4.80
    controls: mean 3.24%, sd 0.75%

**So the answer is no effect this design can see, and the design is the
limitation.** Shards work different slices of the subject grid, and
different subjects and techniques carry very different text propensity -
the controls alone spread from 2.54% to 4.80%, nearly a factor of two. One
shard against eleven detects a large effect (the people experiment was
59.3% against 41.7%, impossible to miss) and cannot resolve a small one.

**Reverted to the shipped prompt and not pursued further, on value.** Text
is about 3.2% of generations. Eliminating it entirely would save roughly
$8 of the remaining GPU budget, and the measurement needed to settle a
difference this small - a paired design running both arms over the same
slice, or many more shard-hours - costs a real fraction of that. The lever
is too small to be worth the instrument.

What this does settle: the 12 Oct move of _CLEAN into the window is not
doing harm, so the doubt raised after the people result can be closed. It
is also not demonstrably doing good. It stays because it is shipped and
there is no evidence to change it, which is a different and weaker reason
than the one I had for it yesterday.

## The 13 Oct afternoon reject spike - transient, and a lesson in reading it

At 14:20 the fleet went from 6.5% rejected to 43%, text-dominated, and it
did NOT come back down. Ten minutes on it read 43.1%. Every shard that
relaunched in the 12:30 rotation is affected; the two that had not rotated
were clean.

                           place share of output    reject rate
    wa-v3-1  (up 8 hrs)        22%, flat                0%
    wa-v3-10 (up 3 hrs)        17-23%, flat             4.5%
    the ten that rotated    40% rising to 61%         42-55%

The pool is 25.4% place. The unaffected shards sit on that baseline; the
affected ones produce double it and climbing. Places are where FLUX writes
shop signs and street names, so the text rejections follow from the
material rather than from anything wrong with the gate - the marks are real
garbled lettering ("CANNON CHASSE", "INETRECLNE"), nearly all in the bottom
signature band.

RULED OUT, each checked rather than assumed:
  * different grid - both broken and healthy log "ip gate: 1,243,137 jobs"
    and "pool: 960,000 of 1,124,581", so subjects.json is the same file;
  * different launch args - identical apart from --part;
  * changed code - no shipped file changed between 11:18 (healthy relaunch)
    and 12:30 (the broken batch);
  * broken resume - every shard logged "resume: 271,217-279,702 panels
    already across 4 bucket(s)", so nothing is being regenerated;
  * a slice effect - striping is jobs[k-1::nparts] over a hash-ordered grid,
    so every stripe is a fair sample;
  * thrashing - 481 distinct SKUs rejected, 122 reaching try 2, 59 using all
    retries and then kept_anyway and uploaded. The retry path works.

HYPOTHESIS, NOT CONFIRMED: --max-hours cuts a run mid-queue, and what is
left unfinished is enriched in the jobs that take three generations instead
of one. Each rotation concentrates that further, so a stripe's remainder
drifts towards places. It fits every number above, including why the two
unrotated shards are clean.

RESOLVED AT 15:20, AND IT WAS TRANSIENT AFTER ALL. The fleet read 28.1%
an hour later and the recovery is per-shard, in the order they rotated:

    wa-v3-5   3.9%   wa-v3-4   7.0%   wa-v3-7  12.5%   wa-v3-9  22.0%
    wa-v3-2  34.5%   wa-v3-8  44.2%   wa-v3-6  46.7%   wa-v3-3  55.2%

That is exactly what the hypothesis predicts and it is now the working
explanation rather than a guess. **The clearing takes about three hours per
shard, not one** - which is the thing I had wrong, in both directions
within an hour.

A LESSON ABOUT THE JUDGEMENT, NOT THE SYSTEM. I called it transient, then
at 14:35 called that wrong on a ten-minute window, and quoted the seller a
$134 overrun computed by treating a transient as permanent. Ten minutes and
forty minutes are both far too short to see a three-hour decay, and I knew
the decay existed - it is documented two sections up. The rule that was
already written down for reject rates applies to everything: a reading
shorter than the process you are watching tells you nothing, and quoting a
cost off one is worse than saying "I do not know yet".

THE COST, on a cycle average rather than on the worst reading:

    baseline 6.5%          88 hr  $208
    cycle average 13.6%    95 hr  $225   <- 3 hr elevated, 7 hr normal
    sustained 43%         144 hr  $342   <- what I wrongly quoted

So about $17 over the standing projection, not $134. The staggered
--max-hours committed at 13:25 should also flatten this, since it stops ten
shards entering the elevated phase at once.

## 14 Oct: a fix that crashed the fleet, and the check that would have caught it

Three shards died overnight on an unhandled EndpointConnectionError from a
single R2 upload, printed GEN_DONE as though they had finished, and billed
idle for forty-five minutes because the watchdog only knew the markers a
tidy finish prints. Three fixes went in: retries around the upload, an exit
status instead of an unconditional echo, and GEN_DONE/GEN_CRASHED added to
the watchdog's kill list.

**The retry loop used the name `attempt`, which is the per-SKU retry
COUNTER** - a dict built at line 519 and read at 575 as attempt[j["sku"]].
The loop rebound it to an int and the next job in the chunk died on 'int'
object is not subscriptable. Every shard crashed within minutes of
starting: 32 kills in 90 minutes, 3,135 panels in the hour instead of
5,700, the whole fleet in a relaunch loop.

IT PARSED. The checks run before shipping it to twelve pods were "does the
file parse" and "does the bundle still fit under the command limit". Both
passed. A name collision two hundred lines apart is exactly what those
cannot see.

**Before changing gen_gated.py again, run the loop, not the parser.** Four
seconds, no pod, no GPU:

    attempt = {j["sku"]: 0 for j in jobs}
    for j in jobs:
        assert attempt[j["sku"]] < retries   # the line that died
        ...the changed block, with a stub that always fails
           and a stub that always succeeds...
    assert isinstance(attempt, dict)

The one good part: GEN_CRASHED worked. It is the only reason the pods were
killed rather than left idling, and the only reason the kill log said what
was happening. The diagnostic was right and the fix beside it was wrong,
which is worth remembering about any commit that does two things at once.

## What is NOT resumable yet

The CPU stage (`pipeline.py`) rebuilds its listings from whatever panels it
is given, so it is cheap to re-run and does not need resuming. The eBay
upload files are not written yet.
