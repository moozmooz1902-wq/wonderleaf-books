# Access and infrastructure

What a new session needs to know to run this without asking the seller to
set anything up again. Read this before telling them to open a terminal.

## RunPod - WORKING, no setup needed

The API key is stored as an environment credential on the Claude
environment ("poster and t shirt data research"), named `RUNPOD_API_KEY`,
type Bearer, allowed host `rest.runpod.io`.

It is injected by the egress proxy, NOT exposed as a shell variable. So:

- `echo $RUNPOD_API_KEY` prints nothing. That is expected, not a fault.
- `curl https://rest.runpod.io/v1/pods` is already authenticated. Just call it.
- It works in the session it was added to - no need to start a new one.
- **Python's urllib gets 403 through the proxy; curl gets 200.** Fetch with
  curl, parse with Python.

Verified 2026-10-03: `GET /v1/pods` -> HTTP 200.

Useful endpoints (full spec at `GET /v1/openapi.json`):

    GET  /v1/pods                 list
    POST /v1/pods                 create (takes env, templateId, dockerStartCmd,
                                  computeType=CPU, cpuFlavorIds, vcpuCount,
                                  containerDiskInGb, cloudType=COMMUNITY|SECURE)
    POST /v1/pods/{id}/stop       stop (keeps the pod, disk persists if volume)
    DEL  /v1/pods/{id}            delete
    GET  /v1/billing/pods         spend

There is **no secrets endpoint**. Credentials reach a pod either through
`env` on pod creation or through a template's env.

## Cloudflare R2 - NOT connected

Bucket `tshirt-m12k`, account M12K.
Public base `https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev`
(public access is on; a GET of the root returns 404, which is correct for
an empty bucket).

**Do not try to add R2 through the "Create an account for Claude"
credential form.** That form injects a fixed header. R2's storage API signs
every request with a value computed from the secret, so a static
`Authorization: Bearer ...` cannot authenticate however the host is set.
This has already cost several rounds; do not retry it.

### Template already created

    id    vbsgwyibn1
    name  wonderleaf-tshirt-render
    image runpod/base:0.7.0-ubuntu2404, CPU, 60 GB container, 40 GB volume

Created 2026-10-05 via `POST /v1/templates`. It carries `R2_BUCKET` and
`R2_PUBLIC_BASE` already filled, and `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`
and `R2_SECRET_ACCESS_KEY` as `PASTE_..._HERE` placeholders for the seller
to replace in the RunPod UI. Pods created with `templateId: vbsgwyibn1`
inherit all of them, so the pod holds the keys and Claude never does.

Unlike every earlier pod, this one has a 40 GB volume at /workspace, so
work survives a stop.

Before using it, check the three placeholders have been replaced -
`GET /v1/templates` shows the env values.

Two routes that do work:

1. **RunPod template (preferred).** The seller creates a template in the
   RunPod UI carrying `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` and
   `R2_SECRET_ACCESS_KEY` as env vars. Pods are created with that
   `templateId`, so the pod holds the keys and Claude never does.
2. Plain environment variables on the Claude environment under those same
   three names, if an environment-variables section is offered separately
   from the credential form.

Nothing about rendering depends on R2. Only the upload step does.

## Pods seen on the account (2026-10-03)

    v4f4gjeot7i9t0  cpu3g  16 vCPU / 64 GB  50 GB disk  $0.64/hr  EXITED
    hzrsupgjqzlfrg  GPU    36 vCPU / 143 GB 30 GB disk  $0.74/hr  EXITED
    h9bfk4b8x0w4bw  GPU    12 vCPU / 31 GB  30 GB disk  $0.74/hr  EXITED

All three have **volume 0 GB**, so `/workspace` is container disk and is
wiped on stop. Anything uploaded to an earlier pod is gone. Create pods
with a volume if work needs to survive a stop.

The CPU pod ran 11 minutes before the seller stopped it, so the "it takes
forever" complaint is RunPod provisioning time, not the render.

## Costs, measured not estimated

    render      12.3 designs/sec/core, 79 KB per JPEG
                118,360 designs = 2.7 core-hours, 9.5 GB
    cpu3g       $0.64/hr (NOT the $0.20-0.40 quoted earlier - that was wrong)
    whole job   well under an hour, so roughly £0.50

A GPU is needed only for the illustrated 62%: ~10,000 images for 2,517
subjects, ~3h on a 4090, ~$2.50. Not started.

## Boundaries the seller agreed

- Claude starts, runs and stops pods without asking.
- Claude does **not** make payments or top up the card. Report the balance
  and let them do it.
- Anything irreversible or outward-facing - deleting a pod with unsaved
  work, pushing live eBay listings - gets confirmed first.

## Still blocked on the seller

- **Price.** `ebay_file.py` has 9.99 as a placeholder. The export has no
  price column, so it cannot be derived from any data held.
- Confirm eBay category 15687 matches their existing listings.
- Whether listings need S-XXL variations (current file is single-SKU).

## Learned from branch `claude/hopeful-rubin-u14pgu` (the wall-art work)

That branch is the same seller's wall-art pipeline. Things it settled that
apply here:

**eBay business policies are named `1`, not `default`.** `wallart/plan.json`
has `profiles: {shipping: "1", returns: "1", payment: "1"}`, quantity 1,
location United Kingdom. "1, 1, 1" in conversation meant the policy names,
not the quantity. `ebay_file.py` has been corrected. Wall art uses category
360; t-shirts use 15687.

**FLUX.1 [schnell] is the image model**, chosen for its Apache-2.0 licence
(commercial use allowed). FLUX.1-dev is NON-COMMERCIAL and must not be used
on products that are sold. `wallart/pod/gen_ai.py` is a working
implementation: diffusers FluxPipeline, bfloat16, 4 steps, 864x1216,
shardable with `--part k/n`, and a `--dry-run` mode that emits grey
placeholders so the plumbing can be tested without a GPU. Adapt it rather
than writing a new one.

`wallart/research/IMAGE_SOURCES.md` costs fal.ai FLUX.1 schnell at $0.003/MP
if hosting is not worth it.

**Serve-on-demand beats pre-rendering.** `wallart/serve.py` draws the
listing photo, mockup and print file from the URL on request, so nothing is
stored. Worth considering here instead of rendering and uploading 118k JPEGs.

**The duplicate rule, and why it matters.** That branch found store 1's
424k wall-art listings are 89% near-duplicates and treats that as the
likeliest reason they do not sell. Its rules: no two rows share phrase +
venue + colourway; every unique phrase is used before any phrase repeats; a
phrase appears in at most 4 colourways; no template produces more than
40,000 phrases.

### This catalogue fails that test, worse than theirs

Measured on REPLICA_V5.csv, 118,258 listings carrying a slogan:

    distinct slogans            9,761     91.7% of listings are repeats
    distinct slogan+look pairs 25,945     78.1% are repeats
    NEVER UNDERESTIMATE AN OLD MAN WITH A MOTORCYCLE   x2,332
    WEEKEND FORECAST FOOTBALL WITH A CHANCE OF DRINKING x1,540
    niche FOOTBALL x4,579, MOTORCYCLE x4,441, empty x5,117

Cause: the slogan is a function of (niche, template) only, and the niche
vocabulary collapses to 1,913 terms, so thousands of distinct source
listings map onto the same handful of slogans. DO NOT UPLOAD THIS AS IS -
it would reproduce the exact failure the wall-art branch diagnosed.

Fix direction: make the slogan depend on more of the source listing than a
single niche word - the full subject phrase, not the collapsed category -
and enforce a cap so no slogan+look pair repeats.

## Illustrations for DTF - settled 2026-10-06

The seller prints by DTF transfer onto **black** shirts. That rules out
three things the image model produces by default, and no amount of prompting
reliably removes any of them, so `dtf.py` enforces all three after the fact:

- **Gradients and shading.** They band on transfer film. `deshade()`
  mode-filters the artwork into plateaus and then quantises to four flat
  inks with dithering off - dithering is itself a gradient.
- **Hairlines.** A stroke under about 2mm at print size lifts off with the
  carrier sheet. `despeckle()` is a majority vote over a 5px window, so an
  engraved lion's mane becomes either a solid shape or nothing.
- **Dark ink.** The model's default palette is sepia and charcoal, which on
  a black shirt is invisible. `plan_inks()` keeps each ink's hue but floors
  its brightness and saturation, and drops a dark neutral to transparent
  entirely - the shirt is that ink, and the artwork gets its outlines free.

`printable()` then rejects anything still unprintable: too little ink, ink
over the whole shirt, an edge-to-area ratio that means spindly detail, or a
silhouette that is nearly a filled rectangle (a painted background panel the
knockout could not reach).

### Three mistakes worth not repeating

1. **Quantise the artwork, not the canvas.** `knockout()` zeroes the RGB of
   the pixels it removes, so a straight `quantize()` saw a million pixels of
   pure black and spent one of its four inks describing empty space. The
   first flattened sample came out as white blobs because of this.
   `_ink_palette()` builds the palette from the opaque pixels only.
2. **Recolour after matching, never before.** Matching pixels against an
   already-brightened palette sends a black pixel to whichever bright ink
   happens to sit nearest black. The design scrambles. Match against the
   true inks, then `putpalette()` the lifted ones.
3. **Post-processing cannot rescue the wrong prompt.** The first 24
   illustrations were generated as detailed engravings; flattening them just
   produced flat mud. Regenerating 24 with a flat-vector prompt and bright
   palette hints cost about 6p and fixed what hours of filter tuning could
   not.

### CLIP reads 77 tokens and silently drops the rest

The pod log says so plainly - "the following part of your input was
truncated" - and it is easy to miss among the model-loading chatter. The
first prompt ran to about 90 tokens, so every clause after "centred" was
discarded, including the whole instruction not to paint a background panel.
Adding more words to a prompt that is already over the limit changes
nothing at all.

What that cost, and what three samples of 24 settled:

    long prompt, 4 inks     good colour, background panels on 5 of 24
    short prompt, die cut   "die cut" makes the model draw a white sticker
                            border, which eats a palette slot and leaves
                            the subject as a single flat blob - much worse
    reordered, 5 inks       best: the anti-background clause now lands
                            inside the window, 21 of 24 pass, 19 look right

So the order of a prompt matters more than its length: whatever must survive
goes first. Each sample cost about 6p and six minutes, which is far cheaper
than tuning filters against artwork that was wrong to begin with.

Background panels are the one defect still not solved in post. Four
different detectors were measured against a labelled sample and none
separated a painted panel from a design that happens to be solid. It is
handled at the prompt (`no background panel, no frame, no border` plus a
negative prompt) and whatever gets through is rejected by `printable()`.

### Running it

`gen_illus.py` uploads three copies per subject:

    illus/src/   the image exactly as the model drew it
    illus/raw/   the printable transparent PNG
    illus/ink/   the same shape as one flat ink

`src/` exists so the flattening can be retuned without paying for the GPU
again. Generation is the expensive step and the artwork does not change; how
it is reduced for DTF is the part that gets argued over. `try_dtf.py`
re-runs the whole reduction locally against `illus_src/` and renders a
contact sheet on the mockup - that loop is free and is where the tuning
belongs.

### Pod recipe that works

There is still no way to write to R2 from the Claude environment (the
credential form cannot sign SigV4, and the keys live only on template
`vbsgwyibn1`). So the pod pulls the code pack from the bucket's **public**
base and the changed files are carried inline:

    tar czf overlay.tgz gen_illus.py dtf.py && base64 -w0 overlay.tgz

and the dockerStartCmd does `echo '<b64>' | base64 -d > o.tgz && tar xzf
o.tgz` after unpacking `v2/_pack.tgz`. About 9 KB of base64, well inside the
limit. End the command with `sleep <seconds>` rather than `sleep infinity`:
the container then exits on its own, which caps the cost if the pod is not
stopped by hand.

Measured: 24 illustrations on a 4090 in 4.3 minutes end to end, model
download included - $0.06. The 400-subject run is about 25 minutes.

## The 400-subject run, and what it actually yielded

    400 generated          $0.50, 42 minutes on a 4090
    365 physically printable   dtf.py gate: 33 covered the whole shirt, 2 were rectangles
    271 judged good        qwen2.5vl, strict
    259 after the IP filter

Of those 259, eyeballing a 48-design spread, about three in four are
genuinely good and the rest are weak - a blob, or artwork sitting on a
painted panel. So call it 200 solid designs from 400 attempts. That is the
honest number; the mechanical gate's 365 is not.

### The judge, and why it exists

`dtf.py` catches what cannot physically print. It cannot catch the other
failure, which is artwork that prints perfectly and is a magenta blob.

Four different pixel statistics were measured against a labelled sample
looking for one that separates "recognisable motorcycle" from "abstract
smear": dominant-ink share, number of inks above 4% coverage, silhouette
fill, and per-ink block solidity. **None of them separates anything.** The
worst blob in the sample scored better than the best motorcycle on three of
the four. It is not a question about pixels.

So `judge_illus.py` asks qwen2.5vl - the same model that read the seller's
22,437 designs - whether each finished print file is a recognisable,
deliberate illustration of the thing it is meant to be. 365 designs in about
four minutes, $0.09. It composites each design onto black first, because the
judge should see what a buyer sees on the shirt.

It is well calibrated on "is this recognisable" and poorly calibrated on
"is this on a background panel" - it flagged 12 where about 55 were
expected. Panels remain the one unsolved defect, in post and in prompt
alike. Do not claim otherwise.

## Trademark and likeness - 389 listings that must not go up

The subject bank was mined from the collaborator's live catalogue, so
anything they sell arrives looking like a proven seller. 15 of the 400
subjects and 389 of the 116,355 listings (0.33%) name something somebody
else owns:

    banksy 67, king charles 57, che guevara 45, supermarine 45, spitfire 26,
    guinness 15, ducati 14, game of thrones 13, rubik 12, mini cooper 12,
    ghostbusters 9, yamaha 9, xbox 8, land rover 8, delorean 8, scooby 6,
    batman 5, darth 3, the beatles 3, queen elizabeth 3, bob marley 3

eBay runs the VeRO programme: a rights owner reports a listing, it comes
down, and a run of removals puts the account at risk. The M12K account
already carries a selling limit, so it has less room than any of the others
to absorb that. 389 listings out of 116,355 is not worth it.

`ip_risk.py` holds the rules - trademark, character, likeness - and
`strip_ip.py` removes the matching listings from the eBay files, parent row
and all five size variations together. Run it before any upload.

The likeness rule is the one most often got wrong: a portrait of a public
figure is their likeness, not public property, and the estate of a dead one
usually still enforces it.

## Illustrated listings - the composed format

13,313 of the 116,355 listings (11%) now carry a real illustration above the
slogan. The rest stay type-only, because that is what their data says:
type-only averaged 10.53 units per design, type-with-picture 9.66,
picture-only 6.08. The picture is an addition to the best format, not a
replacement for it.

Which listings get one is decided by the catalogue, not by taste: a row's
`illustration` column is matched against the 259 generated subjects, exactly
or by word subset, preferring the closest-sized phrase so "skull" does not
capture "skull with diving gear and stopwatch" when plain "skull" exists.
246 of the 259 found a home.

**The SKUs do not change, so the eBay file does not change.** The artwork at
`art/mock/<SKU>.jpg` and `art/raw/<SKU>.png` is simply replaced.

### Recolouring, and why it is not optional

The illustration is remapped into the listing's own palette before it is
stacked. That does two jobs at once:

- The picture stops clashing with the type under it.
- One drawing of a motorcycle becomes twelve visibly different motorcycles,
  so the 1,466 motorcycle listings do not all carry the same picture.

Checked on the full set: 13,313 listings, 13,313 distinct
picture+layout+palette+slogan combinations. Zero repeats.

Two things had to be got right. The palettes were written for type, where
the deep tone is an outline and never carries a shape on its own - dropped
straight into a drawing, the violet palette's deep (62,46,102) becomes a
hole in the middle of it on a black shirt. So each palette colour goes
through the same brightness floor as `dtf.plan_inks`. And the picture is
sized off the type block's WIDTH: sizing it by height made a one-line slogan
produce a postage stamp and a four-line one produce a poster.

### The print master stays flat

Scaling a composed design up to 2600px interpolates, and an interpolation
between two flat inks is a gradient - the thing DTF cannot hold. So
`dtf.snap()` runs last: every pixel is forced to the nearest ink it is
allowed to be and the alpha is made binary again. Measured on the output:
5 to 7 flat inks per design, **zero semi-transparent pixels**.

The print is 22cm wide unless that would make it taller than 30cm. A picture
over type is a much taller shape than type alone, and an uncapped 36cm print
is both a bigger transfer than it needs to be and lower on the chest than
the placement the seller signed off.

### Cost

Recolouring per listing is a million-pixel remap and the job takes a day.
Cached it is 2,952 remaps in total - 246 pictures in 12 palettes - and the
listings become pastes, at under a second each. The cache only pays off
because the jobs are sorted by picture and palette first, so each worker
gets a contiguous run that shares one tint rather than a random spread that
shares none. 16 cores, about 20 minutes, roughly 20p.
