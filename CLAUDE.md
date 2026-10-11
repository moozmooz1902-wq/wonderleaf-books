# Where the work lives

One chat per product line was getting confusing, so this is the map. Read
it first in any new session.

## The decision

**T-shirts are worked on in this branch, `claude/dreamy-hopper-cgp4p4`.**
Everything else about t-shirts - the catalogue, the mockup, the eBay
builder, the RunPod and R2 access - is here. Start with
`tshirt/ACCESS.md`, then `tshirt/RESUME.md`.

**The IMAGE-BASED wall-art pipeline is also on this branch now**, under
`wallart-data/`, built 10-11 Oct 2026. That is the generated-artwork line:
FLUX panels, the code-drawn line families, frames, colourways, the
copyright gate and the RunPod/R2 run. Start with `wallart-data/RESUME.md`
for how to pause and continue, `wallart-samples/PLAN.md` for the costed
plan, and
`research_notes/Wall art catalogue taxonomy harvest/first_real_sample_and_measured_cost.md`
for everything that was measured and everything that failed first.

**The older typography wall-art pipeline stays on
`claude/hopeful-rubin-u14pgu`**, under `wallart/`, with its own stores and
buckets. The two are not duplicated; read that one on that branch. If you
are looking for generated IMAGES, you are in the right place here; if you
are looking for the 2.3M typography catalogue, you are not.

## Why it is split this way

Different product lines, different buckets, different eBay categories
(t-shirts 15687, wall art 360). Merging them would mean one branch where
most of the files are irrelevant to whatever is being worked on.

The cost is that a session on one branch cannot see the other's chat. That
does not matter, because neither can any session: **the repo is the memory,
not the conversation.** Anything worth carrying across gets committed.
`tshirt/ACCESS.md` has a section recording what was carried over from the
wall-art branch, including corrections it forced.

## Shared facts, true for both lines

- eBay business policies on every account are named `1` - shipping, returns
  and payment. Not `default`.
- Quantity 1, location United Kingdom.
- One Cloudflare R2 bucket per eBay account. T-shirts for the M12K account
  go to `tshirt-m12k`. **There is no wall-art bucket yet**: the stored R2
  token can write to `tshirt-m12k` but cannot list or create buckets
  (probed 11 Oct), so generated panels currently live under the prefix
  `tshirt-m12k/wallart/v1/`. A copy within R2 is server side and free, so
  moving them once a bucket exists costs nothing.
- FLUX.1 **schnell** is the image model, for its Apache-2.0 licence.
  FLUX.1-dev is non-commercial and must never be used on goods that are
  sold.
- Near-duplicate listings are treated as the main commercial risk. The
  wall-art branch blames 89% near-duplication for 424k listings not
  selling. Any catalogue generated here gets measured against that before
  it is uploaded - `wallart-data/pipeline.py audit()` is that measurement.
  Measure it on a gradient hash of the ARTWORK, excluding a design's own
  colourways; hashing the framed mockup or using an average hash both give
  answers that are badly wrong, in opposite directions.
- No human figures, and animal eyes must be right. The seller's rule,
  11 Oct. Enforced in `gen/prompts.py`, not left to chance.
- Nothing claims to be hand-painted, original or artist-signed, and the
  fake signatures FLUX scrawls on the artwork are cropped off. Both are
  legal controls, not just quality ones - see `wallart-data/ip_check.py`.

## Access

RunPod and Cloudflare R2 are both connected and verified from the
environment "poster and t shirt data research". No terminal work is needed
from the seller. See `tshirt/ACCESS.md` for how each one is wired, what
does not work and why, so the failed routes are not retried.
