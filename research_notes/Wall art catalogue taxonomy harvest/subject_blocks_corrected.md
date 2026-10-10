# Subject blocks, recomputed on the corrected extraction

10 October 2026. `competitor_data_analysis.md` was written from an extraction
that took two columns and flattened tabs but not newlines, and its subject
ranking had already been corrected once. This recomputes from scratch on the
verified extraction — 93 files, no double counting, 13,727,739 rows,
**1,372,755 titled listings** — and counts **distinct titles per set**, so the
three builders can be compared instead of merged.

Script: `wallart-data/subjects_clean.py`.

| block | Fy! (282,475) | Displate (442,729) | raw800k (171,424) |
|---|---|---|---|
| **animals** | **58,084 — 20.6%** | 43,076 — 9.7% | 10,497 — 6.1% |
| **vintage / advertising** | **48,877 — 17.3%** | 8,377 — 1.9% | 3,589 — 2.1% |
| botanical | 47,696 — 16.9% | 20,407 — 4.6% | 21,236 — 12.4% |
| abstract | 39,512 — 14.0% | 11,695 — 2.6% | 15,684 — 9.1% |
| landscape | 24,036 — 8.5% | 21,029 — 4.7% | 14,329 — 8.4% |
| city / place | 22,360 — 7.9% | 27,281 — 6.2% | 9,673 — 5.6% |
| figure | 9,635 — 3.4% | 17,591 — 4.0% | 11,763 — 6.9% |
| food / drink | 8,178 — 2.9% | 5,323 — 1.2% | 2,516 — 1.5% |
| space | 3,885 — 1.4% | 9,415 — 2.1% | 3,465 — 2.0% |
| sport | 3,185 — 1.1% | 6,355 — 1.4% | 1,117 — 0.7% |
| vehicle | 2,349 — 0.8% | 7,782 — 1.8% | 1,575 — 0.9% |
| **typography** | **1,515 — 0.5%** | 10,330 — 2.3% | **10,590 — 6.2%** |

*(Blocks are not exclusive — a title can match more than one — and Displate's
percentages are low across the board because most of its titles are franchise
and character names that match no décor block at all, consistent with its
search queries being 91.2% named entities.)*

## The finding: the seller's source data is the wrong shape

Compare the décor leader with the set the seller's own catalogue was built
from:

| | Fy! | raw800k | |
|---|---|---|---|
| animals | **20.6%** | 6.1% | **3.4× under** |
| vintage / advertising | **17.3%** | 2.1% | **8.2× under** |
| typography | 0.5% | **6.2%** | **12× over** |
| figure | 3.4% | 6.9% | 2× over |

**raw800k under-indexes by a wide margin on the two blocks that matter most,
and over-indexes on the one that performs worst.**

- **Animals** is the single largest block for the décor leader at one title in
  five, and the seller's source has it at 6.1%.
- **Vintage** is 17.3% of Fy! against 2.1% of raw800k — and `vintage` is the
  strongest register in the seller's own watcher data at z = +6.6.
- **Typography** is 6.2% of raw800k against 0.5% of Fy! — and typography is
  where the slogan block lives, the 12,731 listings running at 0.39% against a
  1.05% base.

So the shape of the seller's catalogue is close to the inverse of the shape
that works. That is not a subtle optimisation; it is the top-line explanation
for why a 168,819-listing catalogue gets 2,142 watchers.

## What it implies for the build

The first build already picked vintage UK place posters and charcoal breed
portraits. This independently supports both and suggests the weighting:

- **Animals deserve more weight than one product.** 20.6% of the décor
  leader's catalogue, and we hold 221 Kennel Club breeds, 636 BOU birds, 107
  mammals and 59 butterflies — 1,023 enumerable animal subjects before any
  treatment axis.
- **Vintage is a register, not a block**, and it can be applied across
  animals, places and botanicals alike. Fy! runs it at 17.3%; we should too.
- **Typography should be cut hard, not grown.** It is 0.5% of the leader.

Botanical at 16.9% of Fy! and 12.4% of raw800k is the one block where the
seller is already roughly in line with the leader, and it has 1,916 measured
images in the colour pass — the largest single group — so the material to
match it exists.
