# Wall art: what is actually there, measured

Read on branch `claude/hopeful-rubin-u14pgu`, where the pipeline lives. This
folder is a review written from the t-shirt branch, because that is the
branch this session is allowed to push to. **Nothing here changes the
wall-art code.** The one code change it proposes is described below and
needs to land on that branch.

## The headline

The pipeline is in better shape than expected. It is not a rebuild job. The
renderer is clean, the compliance gate is thorough, and the thing the seller
asked for - black ink on a white background, to save ink - **is already how
it works**, and has been since the commit "Plain white inside the black
frame".

What it needs is not better drawing. It needs more things to say.

## The numbers

`generate.py --plan-only`, run 2026-10-06:

    2,784,923 listings
      957,516 unique phrases
         2.91 versions of each phrase on average

That average hides the problem. The catalogue is two very different things
stuck together.

### 95% of it is slot-filled personalisation

    personalised_family   649,577 listings   216,525 phrases
    wedding_love          360,876            180,438
    milestones            296,737             98,873
    nursery_kids          271,562             89,862
    new_home              233,626             77,818
    hobbies               204,298             68,099
    man_cave              184,881             60,934
    places_towns          140,638             46,876
    pets                  107,654             35,401
    bar_pub                99,742             32,655
    kitchen                89,428             29,045

Those are real unique strings - "The Patel Family Est. 2004", "Home is
Bishopton" - produced by crossing a handful of templates with 516 first
names, 369 surnames, 2,326 towns and 60 dog breeds. Each one is a different
search, and each one is a design a buyer has to find by typing their own
name into eBay.

### The other 5% is the same few sentences over and over

    niche              phrases   listings   versions each
    motivation             131      7,859          60.0
    biz_hospitality         70      4,757          68.0
    biz_retail_shop         61      3,658          60.0
    words_aesthetic        114      5,013          44.0
    biz_office_pro          71      3,550          50.7
    biz_health              54      3,022          56.0
    biz_fitness_venues      59      2,830          48.0
    coffee_cafe            190      4,529          24.0
    scripture              691     11,054          16.0
    laundry_utility         37        738          20.0

**Motivation is 131 sentences turned into 7,859 listings.** Hospitality is
70 sentences turned into 4,757. These are the generic, high-search niches -
the ones a buyer finds without knowing a name - and they are the thinnest
part of the catalogue by a wide margin.

This is the exact failure this branch already diagnosed in the seller's
existing store: 424k wall-art listings, 89% near-duplicates, and the
branch's own note says that is the likeliest reason they do not sell. The
rules in the README ("a phrase appears in at most 4 colourways") are
written for colourways, but the venue multiplier runs on top of them and
takes the real figure to 60.

## Quality of the drawing, measured not eyeballed

432 designs rendered across all 9 layouts and 28 font sets, ink measured
against the sheet:

    ink fills 77% of the width, 43% of the height
    centring is correct on stack, subway, frame, rules and badge
    left and corner are deliberately off-centre, which is a layout not a bug

I tested whether a tighter margin would help at the size an eBay thumbnail
is actually seen (`THUMBNAIL_TEST.png`, three margins at 190px). It barely
moves: all three read fine. **The drawing is not the problem.** I had
expected to find one and did not.

One small fix is worth making: `build_block` says it sizes a block to fill
its box, but it only ever shrinks to fit, never grows. A short phrase is
laid out at the size its width needs and then left sitting small. The fix is
four lines and is bounded by the width each line can still take, so nothing
can overflow the margin. Measured effect is small (43% to 43%) because width
is usually the binding edge, but it is correct, and it matters for the badge
layout where the cap is looser.

## Ink colour: already right, with one question

Every one of the 20 palettes has a `#FFFFFF` background. The dark-background
designs were removed. `bw` is first in all 14 mood lists, so black is the
most-used ink by a distance.

But 16 of the 20 palettes use a dark **colour** rather than black:

    pure black   bw, bwgrey, gold, mustard
    coloured     navy, forest, plum, burgundy, cocoa, charcoal, sage,
                 teal, olive, duckegg, blush, lilac, rust, terracotta,
                 pastel, rainbow

A dark colour covers the same area as black, so it is the same amount of
ink - but it is CMY rather than K, which costs more per page on most
printers. Against that, the palette name goes into the listing title because
decor buyers search by colour: "sage green kitchen print" is a real search
and a black-and-white listing does not answer it.

So this is a trade the seller should make, not me. Three options, in the
order I would pick them:

1. **Keep the colours.** They are already dark and sparing, and they earn
   their place in search.
2. **Keep the colours but shift the mix** so black takes a larger share -
   say 60% of listings black, the rest spread over colours.
3. **Black only.** Cheapest to print, loses the colour searches, and cuts
   the catalogue because colourway is one of the levers that makes a phrase
   into more than one listing.

## The public-domain artworks are the weakest thing here

142,904 listings (5%) are harvested museum scans. Looking at
`wallart/samples/pd_samples.jpg`: faded mezzotints, yellowed paper, visible
plate marks, low contrast, and some landscape scans sitting in portrait
frames. They are legally clean and commercially poor - not what a UK eBay
wall-art buyer is searching for.

I would cut them or curate them down hard rather than list 143k of them.

## What is blocking an upload today

- `plan.json` has `pic_base: ""` for all four stores. Nothing can point at an
  image until each bucket's public URL is in there.
- The four buckets (`luxvia-art`, `mercury-usm`, `lunar-kms`,
  `posterleaf-store1`) have not been confirmed as reachable from here. The
  t-shirt R2 credentials in RunPod template `vbsgwyibn1` are for
  `tshirt-m12k` only.
- No images have been rendered or uploaded. `serve.py` draws them on demand
  instead, which avoids storage entirely but needs a host and a domain.
  Pre-rendering to R2 is the same shape as the t-shirt job and is known to
  work.
- `expand_phrases.py` needs `ANTHROPIC_API_KEY` in the environment. This is
  the fix for the thin generic niches and it is already written.

## What I would do, in order

1. **Fill the generic niches.** Run the phrase expansion that is already
   built. It takes motivation from 131 sentences to thousands and drops the
   duplication from 60 versions each to single figures. Costs about $5-26
   depending on model, needs an API key in the environment.
2. **Cut or curate the museum scans.**
3. **Decide the ink-colour question above.**
4. **Fill in `pic_base` and confirm the four buckets.**
5. **Render and upload**, the same way the t-shirt catalogue was done.
6. Apply the `build_block` fix on the wall-art branch.

`CURRENT_OUTPUT.png` in this folder is 12 designs across all 9 layouts, as
the code draws them today.

---

# What was decided, and what is now written

The seller answered three questions on 2026-10-06.

## Buckets: unchanged, already correct

    luxvia-art          1,000,000
    mercury-usm           500,000
    lunar-kms             500,000
    posterleaf-store1     500,000

Four accounts, 2.5M base listings. That is what `plan.json` already says and
it matches what the seller described. Nothing to change.

## Ink: mostly black, some colour - DONE and measured

`CHANGES.patch` adds `black_first()` to `generate.py`. Only two palettes
print on the black cartridge alone - `bw` and `bwgrey`, both ink `#111111`
with a black or grey accent. Every other palette is a dark colour: the same
coverage on the page, but CMY rather than K.

A phrase gets its versions by walking down the palette list and most phrases
take only two or three, so the ORDER of that list is what decides the ink
bill, not how many colours exist. `black_first()` interleaves black and
colour so the share holds at roughly 60% at **every** prefix length, instead
of depending on where a phrase happened to stop:

    first 1: 100%   first 4: 50%
    first 2:  50%   first 5: 60%
    first 3:  67%   first 8: 62%

Regenerated all four stores and counted the result:

    2,500,000 listings
    1,581,769 on the black cartridge alone = 63.3%

      bw          Black and White     924,512   37.0%
      bwgrey      Black and Grey      657,257   26.3%
      navy        Navy Blue           159,490    6.4%
      sage        Sage Green          154,921    6.2%
      forest      Forest Green        121,525    4.9%
      gold        Black and Gold      101,855    4.1%

`gold` and `mustard` are black ink too - `#111111` and `#2A2419` - with a
coloured accent used only on the small ornament and the script word, so the
share of pages that are essentially K-only is nearer 69%.

The 37% that stays coloured is led by navy, sage and forest, which are the
three colour words UK decor buyers actually search.

## Museum scans: curate down hard - the filter is written, not yet run

`pd_quality.py` (goes to `wallart/pd/quality.py`).

`curate.py` already filters on what the museums SAY about a work - licence,
UK copyright, theme, demand, duplicates - and takes 1,090,421 records down
to 153,178. What it cannot see is what the scan looks like, which is the
entire problem with this product line. A faded mezzotint on yellowed paper
passes every metadata test.

Unlike the t-shirt illustrations, where "is this a recognisable motorcycle"
defeated four different pixel statistics and needed a vision model, this
defect **is** photometric, so it gets measured:

    contrast  spread between the 5th and 95th percentile of luminance. A
              crisp engraving uses the range; a faded one sits in a band.
    ink       share darker than mid grey - real blacks, not a grey wash.
    sat       mean saturation - a colour woodblock against a sepia one.
    cast      distance from neutral towards yellow, which is what aged
              paper does.

Shortlist first, so nothing is paid for that could not print anyway:

    153,178 curated
     55,360 are >= 3508px on the long side (A3 at 300dpi) and score >= 40

Then fetch a 400px thumbnail of each, measure, and keep the best with a
quota per theme - landscapes and city views are half the shortlist by count
and the least distinctive by eye, and without a quota the survivors would be
mostly those, which is how a catalogue ends up looking like a job lot.

**Not run yet.** The museum IIIF hosts are not on this environment's
outbound allowlist - `artic.edu` returns 403 through the proxy - so the
fetch is a pod job. 55,360 thumbnails, 32 workers, roughly 30 minutes and
about 30p. Target after measuring: 15,000-20,000 kept of 153,178.

## Also in the patch: build_block grows as well as shrinks

`build_block` says it sizes a block to fill its box and only ever shrinks to
fit it. A short phrase is laid out at the size its width needs and left
sitting small. The fix is bounded by the width each line can still take, so
no line can overflow the margin. Measured effect is small because width is
usually the binding edge, but it is correct and it matters for the badge
layout, where the cap is looser.

## Where this code has to go

`CHANGES.patch` applies to `claude/hopeful-rubin-u14pgu`. This session can
only push to `claude/dreamy-hopper-cgp4p4`, so it is carried here as a patch
rather than committed there. One word of permission and it goes to the
wall-art branch properly, where it belongs.
