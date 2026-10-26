# The 240 reviewed by eye, 26 Oct 2026

The seller asked for anything doubtful to be dropped rather than queried.
All 240 designs were looked at, not the 48 that had been sampled before.
**30 removed, 210 kept**, every niche still carrying 14 or more.

The earlier note in CLAUDE.md put the defect rate at "about 4%". On the
full range it is **12.5%**. The sample of 48 happened to miss the two
worst pockets - the cyanotype wildflowers and the bird portraits.

## Removed, and why

**Human figures (10).** The seller's rule, 11 Oct. Three of these are not
the small for-scale walker the rule was written for; they are pages
covered in people.

| # | Design | What is in it |
|---|---|---|
| 5 | Formby beach | two figures walking on the sand |
| 8 | Durdle Door | a figure in the foreground, another under the arch |
| 13 | Fistral beach | several figures on the beach |
| 26 | a strawberry moon in June | two figures on the ridge |
| 64 | the Peak District | a figure in the foreground |
| 65 | Bannau Brycheiniog | a street scene with a figure |
| 79 | Wastwater | a figure on the shore |
| 87 | the River Avon at Bath | figures on the path |
| 93 | the constellation Leo | a figure silhouetted on the horizon |
| 134 | corn marigold | **covered** in child-shaped silhouettes |
| 135 | wood sage | **entirely** people, including a family group and a dog walker |
| 143 | hemp agrimony | **covered** in floating human figures |

**Fake signatures (4).** The site states in writing that nothing is signed.
A scrawl in the corner contradicts that on the page itself, which is the
exact shape of a misrepresentation finding.

- 48 Ben Lomond, 77 the River Tweed, 86 Loch Broom, 175 old english sheepdog

**Wrong subject entirely (4).** Not stylistic licence - the picture is of
another thing.

- **116 "hobby"** - a hobby is a falcon. The picture is a dog. Filed under British Birds.
- **123 "whinchat"** - a bird. The picture is cats. Also under British Birds.
- **44 "Haystacks"** - a Lake District fell. The picture is literal haystacks in a field.
- **160 sorbus cashmiriana** - a rowan. The picture is a dead stick in a green field.

**Animal eyes wrong (3).** The seller's other standing rule.

- 202 grey squirrel - red-rimmed eyes, unsettling
- 208 texel sheep - human-looking blue eyes, plus disembodied sheep heads floating around it
- 170 xoloitzcuintli - doubled markings that read as a second pair of eyes

**Failed or malformed renders (5).**

- 128 great willowherb - a blank page with four dots
- 149 lilac panicle - near-blank
- 196 gomphrena - orange blobs that read as torn paper
- 148 raspberry cane - reads as candy canes
- 32 a crescent moon and the evening star - a muddy unresolved mass at the foot

**Doubtful, dropped on the seller's instruction (2).**

- 1 Bamburgh beach - a mark on the groyne that could be a person; could not resolve it
- 192 gaura - an abstract splash that does not read as the flower named

## NOT dropped, but worth knowing

**Named places often do not look like the place.** Glastonbury Tor (#40),
Haytor (#36, #46), Thorpe Cloud (#47), Stac Pollaidh (#53) and Blea Tarn
(#81) are all drawn as flat-topped American-style mesas. Stanage Edge and
Hen Cloud do not resemble their real forms either. Nobody is misled about
what they are buying - it is a stylised print and the photograph shows
exactly what arrives - but a buyer who knows Glastonbury Tor will not
recognise it, and that is a refund rather than a policy problem. Left in
because removing them would take out most of two niches, and that is the
seller's call rather than mine.

The same applies to several birds: the curlew (#113) has no downcurved
bill, the crossbill (#120) no crossed bill, the goldeneye (#125) is a
passerine rather than a duck. Dropped only the two that are not birds at
all.

**Repetition inside niches.** Sheet 16 is twelve consecutive watercolours
of orange flowers on pale blue. The constellation ink-washes repeat
subjects - Andromeda, Cassiopeia and Leo each appear twice - and a large
run of the moon designs are a disc above a dark horizon. The gradient-hash
distance rule passed all of them, because it measures pixels and not
whether a shopper scrolling a category sees the same picture four times.
Near-duplication is the stated commercial risk on this project; at 210
designs it is cosmetic, at scale it is the whole problem.

## Strongest of the range

The risograph and collage work (#216-#239) is the most distinctive: strong
colour, no defects found, and nothing that repeats. If the range is ever
cut further, cut toward those.

---

# Round two, same day: the colour fix and a second eye-review

The seller looked at the range and said it needed more colour and more
variety, and that a shopper scrolling a category should not see the same
look twice. Both were right, and the second one turned out to be a bug
rather than a matter of taste.

## What was wrong

Every category page was a single colour. Measured: british-birds 100%
neutral, british-wildlife 100% complementary, dogs 100% duotone,
garden-flowers 100% complementary, trees 100% duotone, nine of twelve
niches at 78% or more. The overall mix read 30/25/19/15/11 and hid it
completely.

Panels are generated in batches that share a palette, so a niche's highest
scorers are siblings and a quota applied across the whole range cannot see
it. Fixed by capping palette and technique **per niche** at 30%, and by
rebalancing the mix toward colour.

Checked the pool first, since the other explanation was that the artwork
is simply drab. It is not: across 952,439 panels the palettes run duotone
22.6%, complementary 21.1%, monochrome 21.0%, neutral 19.3%, spectrum
16.0%. The skew was entirely in the selection code.

| | Before | After |
|---|---|---|
| Worst single-palette niche | 100% (five of them) | **43%** |
| Palettes per niche | 1-2 | **3-5** |
| Colour vs mono/neutral | 45 / 55 | **67 / 33** |

## Ordering on the page

Fixing the mix was not enough. A category page is `ORDER BY rank`, rank is
selection order, selection order is score order, and score order clusters -
so a niche could hold five palettes and still open with six charcoals.

Products are now dealt out round-robin across palettes within each niche
before rank is assigned, with the lane order reshuffled every cycle, seeded
from the niche name. A strict rotation would have replaced clustering with
a metronome, which is just as visible. A second pass separates neighbours
sharing a technique.

Result across all 209: **6 same-technique neighbours, 5 same-colour
neighbours.** Seeded, so the order is identical on every build - a
catalogue that reshuffles itself cannot be checked against yesterday's.

## Second eye-review: 31 more dropped

A fresh selection is a different 240, so the first review did not carry
over. All 240 looked at again; 31 removed, **209 kept**.

- **9 human figures or probable ones** - Dartmoor (a figure on the
  clifftop), the Peak District, Stanage Edge, Shanklin Chine, Perranporth,
  and "turkey oak", which is an American desert roadside with a figure
  walking across it.
- **5 fake signatures** - Catbells, the South Downs, reed warbler, rough
  collie (a monogram stamp), Ben Lomond.
- **6 animal eyes wrong** - the shrew worst of all, huge and cartoonish on
  an animal with famously tiny eyes.
- **6 failed renders** - the constellation Centaurus is an empty
  rectangle; the Plough is two dots where seven stars should be;
  bupleurum is a gradient with five dots on it.
- **5 wrong subject** - "bracco italiano" is a dog breed and the picture is
  an abstract bird; "wildcat" is a spotted African cat rather than a
  Scottish one; "a red deer hind" has antlers, which a hind does not.
- **1 stray object** - a wine glass floating in Haweswater.

`catalogue/rejected.json` now holds **61 SKUs** with reasons, and
`select.py` drops them before scoring, so no future re-selection can bring
them back.

## Pattern worth knowing

**oil_impasto and palette_knife do not work for botanical subjects.** Four
of the five "abstract texture that does not read as the plant" rejects came
from those two techniques on flowers - cerinthe, red campion, broom. They
are fine on animals and landscapes. If the share of those techniques is
raised later, exclude them from the botanical niches rather than
discovering it one contact sheet at a time.
