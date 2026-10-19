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
the offending SKUs back through gen_gated.py with --jobs.

**SIZED 15 Oct, and it is 28x smaller than this note used to say.** The old
figure here was "at roughly 50 ms a panel, a million panels is about 14
GPU-hours, so it is worth doing once at the end rather than repeatedly" -
which priced sweeping the WHOLE catalogue. Only panels written before the
cutoff need it; everything after was gated on the full generation. Nobody had
counted them, and the deferral rested on the wrong number.

`r2_age_histogram.py` counts them from LastModified in one listing pass, no
GETs, nothing downloaded. At 621,532 panels listed:

      before 11 Oct 22:00      35,925     <- the whole job
        luxvia-art             17,946
        posterleaf-store1       7,280
        lunar-kms               7,062
        mercury-usm             3,637

      by day   11 Oct    49,801
               12 Oct   148,546
               13 Oct   139,046
               14 Oct   147,216
               15 Oct   136,923

35,925 panels at 50 ms is **0.50 GPU-hours, about $0.09** - not 14 hours and
not $2.57. It does not need to wait for the end of the run, and it never did;
the set it covers stopped growing on 11 Oct and cannot grow again.

The lesson is the arithmetic, not the OCR: a job was deferred for days on an
estimate of the wrong population, and the right population was one listing
pass away. cost_now.py still carries $2.57 for this and is now overstating
the total by about $2.50.

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

## 15 Oct: an upstream release stopped every new pod, and it looked like one bad shard

`transformers 5.20.0` was published to PyPI at 18:01:01 UTC. The pod start
command's `pip install` was unpinned, so every pod created after that minute
installed it, and 5.20.0 imports `torch.distributed.checkpoint.hf_storage`,
which this image's `torch 2.8.0.dev20250319` does not have. It surfaces
several frames deep, under `from diffusers import FluxPipeline`:

    ModuleNotFoundError: No module named
    'torch.distributed.checkpoint.hf_storage'

The worker exits non-zero before generating anything and `run.sh` prints
GEN_CRASHED. wa-v3-9 came off its ten-hour clock at 18:28 and four
replacements died inside ten minutes: 65y3lillu5qg2l, t0btjelg789u06,
sqoahq1rgkfl6p, brew9anhay8y0s.

**It presented as one bad shard and it was the whole fleet.** The eleven
shards still producing had all been launched between 06:33 and 17:39, before
the upload, on 5.19.0; nothing was wrong with them, the cards, the account or
the repo. Each would have died the same way at its own staggered expiry over
the following hours, one at a time, several hours apart - which is the most
misleading shape a fleet-wide fault can take. Twelve shards failing at once
gets diagnosed in minutes. One failing every forty minutes gets diagnosed as
a flaky host, and the stagger that was added on 13 Oct to smooth the warm-up
cost is what spreads it out.

The pin is in `relaunch.sh`: `diffusers==0.41.0 transformers==5.19.0`. 5.19.0
is not a guess - it is the version the producing fleet was measured on, since
those pods were launched after 5.19.0 went up on 6 Oct and before 5.20.0. The
rest of the list is deliberately left unpinned: no version of it is known to
be good, so pin each one the same way the first time it breaks.

Two things made this slower to find than it should have been.

`launch_gen.py` carried the comment "Pinned, because the unpinned install
broke twice" directly above a `pip install` that was being handed bare
package names. The note had been true of an intention and never of the
command; it read as a guarantee, so the dependency list was the last place
looked. A comment that claims a property nothing enforces is worse than no
comment.

And the watchdog deleted the first three pods with their logs, so the only
copy of the traceback was gone. It now keeps the last 40 KB of the log under
`notes/crashlogs/` before killing on GEN_CRASHED or a dead-host marker - the
text is already in memory when the marker matches, so it costs one local
write and no extra request. The fourth pod's log was only readable because it
was being downloaded every twelve seconds by hand at the time.

One wrong turn on the way, left here because the correction is the useful
part. Those first three kills happened when the pods were 76, 170 and 170
seconds old, and that looked impossible - the fourth pod took two full
minutes just to reach `nvidia-smi` - so the conclusion was that the watchdog
had matched GEN_CRASHED in something that was not the pod's own log, and a
guard was written on that basis. The timing was real and the explanation was
wrong: on a host that already has the container image cached, a pod can boot,
pip install and fail the diffusers import inside 76 seconds. One slow pod is
not the floor for all of them. The guard was kept, because requiring the
worker's own invocation line in the body before honouring a DONE marker means
a DELETE needs positive evidence from this run rather than a substring
anywhere in whatever the proxy returned - but CUDA_DEAD is exempt, since
`run.sh` prints it before the worker is ever invoked and that pod bills with
no usable device.

## The duplicate audit, rewritten 15 Oct, and one wrong shortcut ruled out

The audit compared every panel against every other through a popcount lookup
table. That was 95 minutes at 226,992 panels and it is O(n^2), so at the
current 609,478 it would be about eleven hours and at 960,000 about a day.
The open-work note said it needed "the LSH bucketing pass or a 100k random
sample". Neither is what it got, and the sample idea is actively wrong.

**Distances now come from a matrix product.** Write each 256-bit code as
+-1 and a.b = BITS - 2*hamming, so hamming = (BITS - a.b)/2. Every value is
an integer within +-256 and float32 holds those exactly, so this is the
Hamming distance and not an approximation of it - checked against the lookup
table on 256 x 40,000 pairs, maximum difference 0. BLAS does the work
instead of a fancy-indexed intermediate, which is 13x faster. np.bitwise_count
was tried first and is only 1.3x, because the cost was never the popcount,
it was materialising a probes x panels x 32 array.

That alone puts the EXACT audit at about two hours at 609k, so it stays as
`--full` rather than being abandoned.

**The default samples one side.** 40,000 random probes, each compared against
the WHOLE catalogue: about sixteen minutes, with a Wilson interval of roughly
+-0.08 points at the rates being tracked. This is unbiased, because each
probe's answer is exactly the answer the full scan would give that panel.

**Sampling BOTH sides does not work, and "100k random sample" meant that.**
Hashing a subsample and looking for twins inside it understates the rate by
an order of magnitude, because a panel whose only twin was not sampled looks
unique. On a planted set whose true rate was 0.800%:

    12% subsample, both sides   0.000%    0.00x the truth
    25% subsample, both sides   0.000%    0.00x
    50% subsample, both sides   0.167%    0.21x
    probes against full set     0.800%    unbiased

It would have reported a clean catalogue and the number would have looked
like good news, which is the worst kind of wrong for a figure the whole
no-duplicates control rests on. The hourly routine still carries that
suggestion; the script's docstring now says not to follow it.

Exact repeats are counted over the whole catalogue in both modes - identical
codes are identical bytes, so there is nothing to estimate and no reason to.

The download is the slow stage now, not the comparison: 609k GETs. Threads
went 48 -> 160, which is about how many R2 will serve at once, since the work
per object is one 16x16 resize.

Tested by slicing the comparison stage out of the SCRIPT string the pod
actually receives and executing THAT - exact mode reproduces brute force to
the digit, probe mode over every panel reproduces exact mode, and both find
the planted exact repeat. Parsing is not running; that is the 14 Oct lesson
and it cost twelve shards.

**The structural fix is not done.** Every audit still downloads the entire
catalogue to hash it, which is the hour. The worker already has each panel in
memory when it gates it, so it could write the gradient hash into the
manifest and an audit would never download anything again. That is a change
to the production worker and was not worth making during a run; it only helps
panels made after it ships, so the sooner it ships the more it covers.

## Duplicate audit at 611,441 panels, 15 Oct - and why the rise is not a rise

    0.758% of panels have a near twin, 95% CI [0.677, 0.847]
    40,000 probes against the whole catalogue, threshold 24 bits of 256
    4 exact repeats in 611,441
    per bucket 0.719% to 0.837%, every interval overlapping every other
    notes/audit_611441.json

The series now reads 0.826% (63,533) -> 0.670% (168,515) -> 0.648%
(226,992) -> 0.758% (611,441), and the last step is a genuine rise in the
headline number: the interval does not include 0.648%.

**It is not a rise in duplication.** "Percentage of panels with a near twin"
is not comparable across catalogue sizes. If near pairs arise at roughly
constant probability q per PAIR, the rate is about q*n, so it grows linearly
with the catalogue even when the generator has not changed at all. Dividing
it out:

      panels     rate   per-pair q   vs previous
      63,533   0.826%    1.300e-07        -
     168,515   0.670%    3.976e-08      0.31x
     226,992   0.648%    2.855e-08      0.72x
     611,441   0.758%    1.240e-08      0.43x

q has fallen at every step, including this one. Had it stayed where it was at
226,992, the rate at 611,441 would be 1.75%, and had it stayed at its
63,533 value it would be 7.95%. The generator is getting more diverse faster
than the catalogue is growing; the headline barely moved because the two
effects nearly cancel.

Both numbers are now reported - `per_pair_q` alongside `near_dupe_pct` - and
`--ref-size N` compares each probe against a random N-panel reference instead
of the whole catalogue, which takes n out of it directly. `--ref-size 226992`
reproduces the conditions of the 13 Oct audit. Checked empirically, not just
argued: on a planted set, halving the reference halves the rate (ratio 0.48)
while per_pair_q moves 4% (0.96x).

For scale, the typography branch blames 89% near-duplication for 424,000
listings not selling. 0.758% is two orders of magnitude below that. The
closest pairs are 3 to 9 bits apart and a handful of SKUs appear as the twin
of several others, so what exists is small clusters rather than isolated
pairs - worth a look if the figure ever climbs, not now.

**The hashes were thrown away, and that was the real mistake of this run.**
Downloading and hashing 611,441 panels is the entire cost of the audit -
about seventy minutes - and the script printed a percentage and discarded
them. Every question asked afterwards needed them and none could be answered
without paying the seventy minutes again. They are 32 bytes a panel, 19.6 MB
at this size, against the 154 GB of panels they describe. The audit now
writes them to R2 under `audit/hashes_<n>.npy` before comparing, outside the
`luxvia/gen/` prefix it lists so a later run cannot mistake one for a panel.

## The crop lever is closed, on arithmetic, without spending a shard-hour

Open work carried "--crop-bottom 0.14 instead of 0.10 - one shard, never the
fleet" for days. It does not need running. The cost side settles it before
the benefit side is even measured.

A deeper crop does not shrink the panel - the stored panel stays 704x1008
and the GENERATION grows, because gen height is height/(1-crop) rounded to
16:

      crop 10%   generate 704x1120  for a 704x1008 panel
      crop 14%   generate 704x1168  for a 704x1008 panel

That is 4.3% more pixels on every single generation, and since attention is
superlinear in sequence length, 4.3% is a floor on the extra cost, not an
estimate. On the $119.49 of GPU left it is **+$5.12, certain**.

The benefit is a share of the text rejects, which are wasted generations. The
text rate averages 4.60% of generations across 561 shard-hour readings in
notes/ab_snapshots.jsonl. So:

      halve the text rejects    saves $2.75   <- the best case
      cut them by 30%           saves $1.65

**The best imaginable outcome saves half what the lever certainly costs.**
There is no version of this experiment that pays, so there is no reason to
run it.

And had it been worth running, it was barely measurable. The spread between
shard-hour readings is 4.05 points against a 4.60 point mean, so detecting
even a halving takes about 26 shard-hours on one treated shard, a 30% cut
about 73, and a 20% cut 165. That spread is inflated by freshly rotated
shards, which read 40-55% for about three hours - but the verdict does not
rest on it. The cost exceeds the maximum benefit whatever the variance is.

Same shape as the _CLEAN A/B, one step earlier: there the instrument cost
more than the lever was worth, here the lever costs more than it can return.
Both were worth an hour of arithmetic before any GPU time.

## Fake signatures are a LIVE gap, not a historical one - 15 Oct

The owed sweep was supposed to be a tidy-up of 35,925 old panels. It found
something still happening.

Two samples of 1,500 panels each, same detector, 0 missed either time:

                        before 11 Oct 22:00     after it (current panels)
      detector hits        34  (2.27%)             33  (2.20%)
      old gate re-run       3  (0.20%)             14  (0.93%)

**The rate is the same on panels being made now.** Every candidate in both
samples was looked at by eye, not counted and trusted -
notes/sweep/precutoff_sheet.jpg and postcutoff_sheet.jpg - and most are
real: cursive artist signatures along the bottom edge (Naughie, Saltlord,
Mathilson, Sidby Saffron 1974, Dykeasm, Angfresen and a dozen more), edition
marks, a red seal, one panel carrying the word Copyright. A minority are
text inside the depicted scene - a SLIGACHAN road sign, a RECORDS shopfront -
which is a legitimate part of an illustrated street and not a false claim of
authorship. The rest is texture the threshold was too fine to exclude.

Reading the sheets, roughly 19 of 33 post-cutoff hits are fake signatures or
edition marks: about **1.27% of panels, so around 7,900 of 622,226, about
31,600 listings.**

**Why the gate misses them, precisely.** It is not the crop-line case
777dae2 fixed, and the signatures sit ABOVE the crop line, so a deeper crop
would not reach them either. A small cursive signature fails the gate twice
over:

  * MIN_CONF 0.35 - cursive does not read, which is the whole reason
    detection finds these and recognition does not;
  * MIN_AREA 0.0012 - that is 852 px of a 704x1008 panel, about 106x8 px.
    Anything smaller is admitted deliberately, because FLUX leaves faint
    marks everywhere and rejecting on them throws away good work.

The floor is not wrong. It was set against speckle, and a signature is
simply smaller than it while being perfectly visible to a buyer. CLAUDE.md
makes both of these legal controls - nothing may claim to be hand-painted or
artist-signed, and the fake signatures are meant to be cropped off.

**The cheap remedy, and why it does not slow the run.** Regenerating a SKU
reproduces the same image, because seeds are derived from the SKU - so a
regeneration pass only helps if the gate it runs under catches the defect.
That gate does NOT have to go on the fleet:

      detection pass over the whole catalogue   2.1 GPU-hours   $0.39
      regenerate the ~7,900 flagged             $2.79
      ------------------------------------------------------------
      under $4, and no throughput cost at all

Tightening the live gate instead would raise the reject rate on all twelve
shards for the whole remaining run, to catch panels a single end-of-run pass
catches for three dollars. The sweep is the right shape; it just has to be
the detector and not the reader.

NOT DONE, and deliberately not started: this is a legal control and the
decision is the seller's, so it is written up here and reported rather than
acted on.

## Data check, 17 Oct 00:50 UTC - verified from outside RunPod entirely

Asked to confirm the panels are safe on Cloudflare and the run can continue
at any time. Both checked rather than assumed, and checked WITHOUT RunPod,
which matters: the account is empty, so the usual route (spin a pod that
holds the R2 keys) was not available. The keys live only on template
vbsgwyibn1 and never in this environment.

The way round it is that each store bucket has a public read base in
stores.json. Eight real SKUs taken from the 611,441-panel audit were
requested over plain HTTPS:

    luxvia-art          3 of 8 present
    posterleaf-store1   2 of 8
    lunar-kms           2 of 8
    mercury-usm         1 of 8
                        8 of 8 total, each in exactly one bucket

Each panel appearing in one bucket and only one is the right answer - a SKU
is allocated to a single store - so this is a check of the allocation as
well as of the storage. Two were downloaded in full: both 704x1008 JPEG,
RGB, the correct panel dimensions, real artwork rather than an error page.

CONTINUING IS SAFE AND NEEDS NOTHING KEPT HERE. gen_gated.py --resume lists
the four buckets and drops every SKU already present (gen/gen_gated.py:479).
It reads no local state at all; done.txt is per-pod scratch that dies with
the pod. The code's own comment anticipated exactly this: "If the balance
runs out mid-run, the pods stop, and the next pod picks up exactly here."

WHAT THIS IS NOT. The panels are ON Cloudflare, durably, in one place. That
is storage, not a backup: there is a single copy, so it does not protect
against a bucket being deleted, a bad script, a leaked key, or the
Cloudflare account lapsing. Nothing here can make a second copy - 154 GB,
no credentials in this environment, and no pod to run it on.

THE RISK WORTH NAMING. RunPod went to zero on 16 Oct and took twelve
running shards with it inside two minutes. The same thing happening to the
Cloudflare account would take the entire catalogue, not an afternoon of
compute. Storage is about $2.32 a month for the 154 GB. It is by far the
cheapest thing in this project and the only one that is irreplaceable.
Claude cannot see Cloudflare billing from here - there is no CF token in
this environment - so that one has to be checked by the seller.

WORTH DOING WHEN THERE IS CREDIT AGAIN, cheapest first:
  * keep the Cloudflare account funded - this is the whole ballgame
  * a second R2 bucket as a copy. CLAUDE.md records that a copy within R2
    is server side and free, so this costs only the extra storage
  * object versioning or a delete lifecycle rule on the four buckets, which
    turns an accidental delete into something recoverable
  * the hashes the audit now keeps (audit/hashes_<n>.npy) are a cheap
    integrity record: 32 bytes a panel against 154 GB of panels, enough to
    tell later whether anything changed or went missing

## What is NOT resumable yet

The CPU stage (`pipeline.py`) rebuilds its listings from whatever panels it
is given, so it is cheap to re-run and does not need resuming. The eBay
upload files are not written yet.

## 17 Oct, 11:20 UTC - the count stopped answering, and it was our own data

Three consecutive non-answers from `r2_count_stores.py` at 16 minutes, after
three successes the same morning at 10, 11 and 14. Two wrong explanations
were reached for first and both are written down here so neither is tried
again:

1. "RunPod's CPU hosts have slowed." Plausible, and it would have been
   answered by raising the window - a parameter already changed twice that
   day, once wrongly. No measurement supported it.
2. "`pip install boto3` is unpinned, so this is `transformers 5.20.0`
   again." A good hypothesis on shape - the shards pin `boto3==1.43.114` and
   survive, the count pod does not pin and started failing - and wrong.

What settled it was reading `boot.log` instead of only `count.json`.
`wait()` polls `count.json` alone, so a crashed pod and a slow pod are the
same event: nothing arrives. A diagnostic that printed `boot.log` each poll
showed `status=RUNNING`, pip **finished**, the Python body running, and at
7.8 minutes not one of the four buckets listed. `count.json` reading 335
bytes was `http.server`'s 404 page, not output.

The cause is that the listing was serial: each bucket walked end to end,
one after another, 1,000 keys per LIST call. At 790k panels that is about
790 sequential round trips at ~0.75s, and it grows with the catalogue. It
was always going to cross 16 minutes; it crossed it that morning.

The fix is a partition, not a bigger timeout. Eighteen contiguous half-open
ranges `(lo, hi]` per bucket, boundaries at `WA-0`..`WA-f` plus one range
below the first and one above the last, all four buckets at once: 72 ranges,
72 threads, one boto3 client each. 72 LIST calls replaced ~790 serial ones
and it answered in under a minute.

The ranges partition the LEXICOGRAPHIC keyspace and do not assume the key
shape. Sharding on "the SKU is a hash so the prefixes are even" would have
been shorter and would silently miss any key of another form, reading the
total LOW - and the total is the one number the seller reads. The boundaries
are covered by a test that runs the shipped heredoc body unedited against a
fake R2 honouring Prefix/StartAfter/ContinuationToken, with keys sitting
exactly on a boundary, keys sorting before `WA-0` and after `WA-g`, a
non-`.jpg`, and an empty bucket. All four buckets exact.

Two independent checks on the first real run, 790,956 panels: it is +10,681
on the 09:34 figure over about two hours, ~5,340/hr, inside the healthy
band; and the bucket split is 50.0 / 20.0 / 20.0 / 10.0 percent against a
configured 50 / 20 / 20 / 10. A broken partition does not reproduce the
allocation.

Note `cost_now.py` models spend from the panel count and read $319.73 while
the RunPod API read $338.90 - about $19 low. SPEND IS REPORTED FROM THE API.
The modelled figure is for projecting what is LEFT, not for what is gone.

## 17 Oct, 13:20 UTC - rotation did NOT spike, and the 13 Oct hypothesis fails

Between 11:53 and 12:40 seven shards rotated, and by 13:17 two more, nine of
twelve inside ninety minutes. All of them stopped the same way: `UNFINISHED`,
which is `--max-hours 10` expiring with jobs still in the block. None crashed,
nothing was archived to crashlogs, no pod failed to boot and no API read came
back unreadable.

I TOLD THE SELLER TO EXPECT A BAD READING AND IT DID NOT COME. The four
earliest rotations, 1.1 to 1.4 hours old at 13:17, read:

    wa-v3-1  7.9%    wa-v3-2  9.6%    wa-v3-3  7.2%    wa-v3-4  8.2%

That is indistinguishable from the shards that never rotated, and the fleet
sat at 8.0% - the same figure as 12:18 and 11:18.

So the hypothesis recorded for the 13 Oct spike is CONTRADICTED by this run:

    "--max-hours cuts a run mid-queue, and what is left unfinished is
     enriched in the jobs that take three generations instead of one.
     Each rotation concentrates that further."

Today's nine rotations were all exactly that cut, and there was no
enrichment visible at all. A second prediction of the same hypothesis also
fails: the pool is now 83% consumed (796,704 of 960,000 base images), so a
remainder drifting towards hard jobs should show up as a rising fleet reject
rate across the whole day. It has not moved off 8%.

WHAT THIS ESTABLISHES: `--max-hours` rotation on its own does not produce
the 40-55% break-in. WHAT IT DOES NOT: the cause of 13 Oct. Ten shards
rotated simultaneously that day against nine staggered over ninety minutes
here, and that difference is untested. Nothing is being changed on the
strength of one clean run.

THE OPERATIONAL CONSEQUENCE IS THE POINT. The standing hourly guidance says
a rotated shard reads 40-55% for about three hours, with "do not diagnose,
do not change anything". Read as a blanket rule it is a licence to excuse
any high reading for three hours after any rotation - which is exactly how a
real fault would get waved through. It is a reason to WITHHOLD JUDGEMENT and
re-read, not a reason to expect a spike: nine rotations today produced none.
Judge a high reading on the gate split in rejects.jsonl, not on whether a
rotation happens to be in the window.

## 17 Oct, 14:33 UTC - launch BOTH loops with nohup setsid, not as a plain job

The container restarted at about 14:30. The watchdog survived it; the
filler loop did not, and it has died on every restart today while the
watchdog has not. The difference is only how they were started:

    nohup python3 watchdog.py 7000 > watch80.log 2>&1 &   survived
    bash fill_shards.sh 12 110 auto > fill_new65.log 2>&1  died

A plain background job stays in the session's process group and goes down
with it. So the filler is now started the same way as the watchdog:

    CLIP_GATE=1 nohup setsid bash /home/user/wonderleaf-books/wallart-data/\
        fill_shards.sh 12 110 auto > .../fill_new66.log 2>&1 < /dev/null &

`setsid` puts it in its own session, `< /dev/null` stops it dying on a
closed stdin. The shell prints "Done" for the nohup wrapper immediately -
that is the wrapper exiting, not the loop; check the real pid with
`ps -eo pid,args | grep fill_shards`.

THE PODS ARE NEVER AFFECTED BY A RESTART. Twelve were still running and
generating throughout, and the stray sweep found nothing to reap. Only the
two local loops need restarting, and the only cost of the gap is that an
expired shard waits for the filler to come back before it is replaced.

Note the hourly routine still prints the old plain-`bash` form for the
filler. It works, but it will die on the next restart; use the form above.

CORRECTION, 15:20 - THAT ONLY SURVIVES THE LIGHTER RESTART. There are two
different events and nohup/setsid only helps with one:

  * agent/session restart (14:30): the nohup'd watchdog lived, the plain
    background filler died. This is the case the form above fixes.
  * full container replacement (about 14:55): everything local died,
    setsid included. The new loops came up as pid 230 and 236 - pids that
    low only happen in a fresh container.

So do not treat the detached form as restart-proof. It narrows the window;
it does not close it. The only durable record is still R2, and the only
real protection is checking both loops every hour, which the routine does.

WHAT THE 14:35-14:53 BLACKOUT SHOWED. Before that container died it lost
outbound network for eighteen minutes: watch80.log has 37 consecutive
"pod list unreadable, retrying" lines from 14:35:29 to 14:53:29 and then
stops mid-window. The watchdog killed NOTHING across all 37. That is the
pods()-returns-None fix working as intended - an unreadable read is not an
empty fleet, and EMPTY_PASSES_BEFORE_STOP never armed. All twelve pods
were still RUNNING and generating when the new container came up. Had the
old code been in place it would have exited on the first failure, or read
[] and begun stopping healthy shards during a network outage.

wa-v3-9 ALSO BURNED THREE HOSTS ON CUDA. It expired at 13:19 and then hit
CUDA_DEAD_ON_THIS_HOST on three consecutive replacements - 13:30, 13:37,
13:44 - before the fourth host held. The watchdog caught each one and the
filler replaced it; total lost time about 25 minutes on one twelfth of the
fleet. CUDA_DEAD is deliberately ungated in the DONE markers because
run.sh prints it before the worker starts, and that is why it was caught
at all. Worth watching if one shard starts doing this repeatedly, but
three bad community hosts in a row is a capacity-quality problem, not a
bug here.

## 17 Oct, 17:20 UTC - the container is now recycled between every check

Measured window lifetimes, from the first and last timestamped line of each
watchdog log:

    watch79   10:55:21 -> 12:44:14    109 min   full window, ended normally
    watch80   12:58:03 -> 14:53:29    115 min   full window (blackout at end)
    watch81   15:18:38 -> 15:24:19      6 min   container replaced
    watch82   16:18:27 -> 16:24:02      6 min   container replaced

So this is NOT how it has always behaved. The container lived continuously
from 10:55 to 14:53, across two hourly checks. Since about 15:00 it has been
replaced between every check, about six minutes after the check finishes and
the session goes idle - which matches a container reclaimed on inactivity.

CONSEQUENCE: the loops cannot be kept alive, by any launch method. nohup and
setsid are irrelevant to a container replacement. The hourly check IS the
supervisor, and there is a blind window of roughly 54 minutes after each one.

WHAT THE BLIND WINDOW ACTUALLY COSTS, measured rather than feared:

  * Nothing while all twelve shards are healthy. The pods do not depend on
    this container at all. The two blind hours delivered +6,488 and +6,264
    panels, at or above the 6,500/hr healthy figure.
  * When a shard expires or dies inside the window it idles and bills until
    the next check kills it. One event so far: wa-v3-11, killed 45 seconds
    after the 16:18 restart, upper bound $0.17.
  * Worst realistic case is a whole rotation burst landing in a blind window:
    twelve pods idling under an hour, about $2.40, once per ten-hour cycle.

NOT CHANGING --max-hours TO AVOID IT. Raising it so the shards never rotate
again would remove the exposure, and it is the wrong trade: the whole
exposure is about $2.40 at worst against $353 spent, the system self-heals
within one hour unaided, and --max-hours is also the bound that stops a bad
pod running forever. Same arithmetic that closed the crop lever and the
_CLEAN clause - the fix costs more risk than the fault costs money. Revisit
only if a burst actually lands in a blind window and the real figure comes
in far above the estimate above.

## 18 Oct, 04:20 UTC - the run starts ENDING, one stripe at a time

wa-v3-1 came up at 03:19, ran 53 minutes and printed:

    pool: 960,000 of 1,124,581 grid jobs
    part 1 of 12
    resume: 888,026 panels already across 4 bucket(s)
    SHARD COMPLETE
    DONE kept 0 from 0 generations in 0.0 min

That is not an expiry and not a fault. Stripe 1 of 12 is EXHAUSTED. This is
how the run ends: `--part k/12` slices the pool, the slices drain at
different rates because the shards rotate onto different cards at different
times, and they finish one by one rather than together.

WITHOUT HANDLING IT THIS COSTS MONEY FOR NOTHING. The watchdog kills a
SHARD COMPLETE pod (it is in the DONE markers) and the filler, maintaining
twelve, immediately launches another, which boots, downloads FLUX, reads the
buckets, finds nothing and exits. Forever, for the rest of the run.

SO fill_shards.sh NOW TAKES `DONE_SHARDS`, a space-separated list of
finished stripes, and never launches them. Started as:

    DONE_SHARDS="1" CLIP_GATE=1 ... fill_shards.sh 12 110 auto

EVERY HOURLY CHECK MUST NOW READ EACH POD'S MARKER AND ADD ANY NEW
`SHARD COMPLETE` TO THAT LIST. A stripe that finishes and is not added
churns pods until someone notices.

WHY DROP THE SHARD RATHER THAN RE-PARTITION THE REMAINDER. Running eleven
shards instead of twelve costs NO extra money - the GPU-hours for the jobs
that remain are the same however many shards share them out, only the
wall-clock stretches. Re-striping the remainder across a new `--part`
count would keep twelve busy, but two live shards could then pick the same
job; that is merely idempotent rather than harmful, because the SKU and the
seed are both hashes of the job, and it still pays for the same panel
twice. Churn costs money for zero panels, so churn is what gets removed.

The exclusion is covered by test_done_shards.sh, which runs the shipped
stripe_done and TODO-loop text against a faked pod list. It includes the
substring traps that matter: skipping "1" must not also skip 11 and 12, and
skipping "2" must not skip 12.

Remaining at this point: 960,000 - 888,026 = 71,974 jobs across eleven
live stripes, about 6,500 each, roughly eleven hours on eleven shards.

## 18 Oct, 08:18 UTC - the stagger is PARTIAL, read ages as a multiset

At 01:18 I wrote in a commit message that "THE STAGGER IS FULLY RESTORED",
counting pod ages running 0.94h to 11.58h in eight distinct steps. Too
kind, and this morning proved it: shards 2, 3, 4 and 5 were all launched
at 22:19 in the burst and all four read UNFINISHED together at 09.97h -
a four-pod mini-burst, $0.63 worst case for the window.

The dispersal is real but it only separates shards that expired
SEPARATELY. Shards replaced in the same minute come back to the limit in
the same minute ten hours later, forever, until something separates them.

SO READ THE AGES AS A MULTISET, NOT A RANGE. "Eight distinct steps across
eleven hours" sounds dispersed and is not: at 01:18 four shards shared the
2.97h step and that was the group that fired this morning. The question to
ask of an age list is how many shards share each value, not how wide the
spread is.

Nothing in the pipeline changes for this. $0.63 is the same order as every
other window, the replacement path cleared the last four-pod group in 63
seconds, and --max-hours stays as it is for the reasons in the 17:20 entry.
The correction is to how the numbers are read.

(Also recorded for honesty: the commit that first described this
correction, 04e44f3, says "RESUME.md now says to read the ages as a
multiset". It did not - the edit it describes failed on a bad match and
the commit went through anyway. This section is that text, added properly.)

## 19 Oct, 00:30 UTC - the 5,000,000 is NOT a panel shortfall. Retraction.

Two things I said yesterday were wrong and both need to stand corrected
here, not only in the chat, because the chat is not the memory.

**First retraction.** Through the evening I projected "five million by
about 23:30". Then at 23:18, with 958,549 panels counted, I said the
opposite - "3.83-3.84M rather than 5M, roughly 96% of target". Both are
wrong, and they are wrong in opposite directions, which means neither was
read off the plan.

The plan is in `status.py:10-13` and `cost_now.py:49`:

    TARGET_LISTINGS = 5_000_000
    PROCEDURAL      = 1_250_000      # drawn in code, no GPU
    BASES_NEEDED    = (5_000_000 - 1_250_000) / 4 = 937,500 panels

So the five million was never 5,000,000 diffusion panels. It is
**3,750,000 listings from 937,500 FLUX panels at four colourways, PLUS
1,250,000 drawn in code.** Against that, the image side at 958,549 panels
is not 96% of anything - it is 102% of its own share, 3,834,196 listings
against 3,750,000 asked for. The image pipeline has OVERSHOT and is
finishing.

**Second retraction, and the real finding.** The gap to five million is
therefore the 1,250,000 code-drawn listings - and those are **not built.**
I probed the buckets rather than trusting the number:

- `<store>/gen/` holds this run's FLUX output, in all four buckets.
- Alongside it is the seller's PRE-EXISTING content: `luxvia/abstract/`,
  `luxvia/birds/`, `luxvia/boho/`, `luxvia/botanical/`, `luxvia/cats/`,
  `luxvia/celestial/`, and loose sequential files like
  `store1/0000000_framed.jpg`, `store2/0000000_raw.jpg`,
  `store7/0000001_framed.jpg`.
- There is **no code-drawn block anywhere in R2.** Not under a prefix of
  its own, not mixed into `gen/`.

`PROCEDURAL = 1_250_000` is a planned number in a costing script. Nothing
has ever generated it. `gen_line.py` (twelve line families) and
`gen_geometric.py` (grammar G11) are both written and both standalone -
they draw to disk - but there is no bulk runner, no SKU scheme, no R2
upload path and no quality or duplicate gate wired to either. The block is
designed, not made.

What it would take, so the seller can decide rather than be told:

- GPU cost: none. It is PIL on a CPU, about 0.2 s per design per core.
  1,250,000 designs is roughly 70 core-hours - a few wall-clock hours on
  one many-core CPU pod, for well under a dollar of compute.
- R2 cost is the part that is not free: 1.25M new objects is about
  $5.60 of Class A writes at $4.50/million, plus storage.
- The real risk is NOT cost, it is **near-duplication**, which this repo
  already treats as the main commercial danger (CLAUDE.md; 89% blamed for
  424k unsold listings on the typography line). Twelve line families and
  one geometric grammar asked for 1.25M distinct designs is exactly the
  shape that produces it. The last measured figure on the image side is
  0.648% near-duplicates at 226,992 panels. A code-drawn block would have
  to be audited the same way - gradient hash of the artwork, excluding a
  design's own colourways - BEFORE any of it is uploaded, and the family
  parameter spaces widened until it passes.

So the honest position: the images are done and slightly over target; the
remaining 1.25M is a separate build that costs almost nothing in compute
and needs a duplication answer first. It is not a shortfall to be fixed by
running more GPU.

## 19 Oct, 00:25 UTC - an empty boot.log is not a leaked pod. Check ps.

Picking the run back up I found `wallart-count` RUNNING with an empty
boot.log after a 90-second fetch, and the 00:17 count log holding only its
pod line. I read that as a pod the orchestrator had leaked when the
container was replaced, and deleted it.

It was not leaked. The orchestrating `r2_count_stores.py` was still alive -
`ps` showed it at 9m56s, waiting for that pod to answer. I deleted a pod
that was still in use and killed my own in-flight count.

The mistake is the same shape as the two already recorded here: an empty
network read is not evidence. `pods()` returning None rather than [] fixed
it for the pod list; the snapshot printing UNREADABLE rather than
"running" fixed it for boot.log. This one is the orchestrator side of it.

**Rule: before deleting a pod as leaked, check whether a local process
still owns it.** `ps -eo pid,etime,args | grep r2_count_stores` is the
whole test, and the grep that misled me only looked for
`fill_shards|health|monitor`. Cost here was a few cents and one lost
count, but the same reflex aimed at a generating shard would throw away
hours of panels.
