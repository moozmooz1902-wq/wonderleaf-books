# Where the work lives

One chat per product line was getting confusing, so this is the map. Read
it first in any new session.

## The decision

**T-shirts are worked on in this branch, `claude/dreamy-hopper-cgp4p4`.**
Everything else about t-shirts - the catalogue, the mockup, the eBay
builder, the RunPod and R2 access - is here. Start with
`tshirt/ACCESS.md`, then `tshirt/RESUME.md`.

**Wall art and posters live on `claude/hopeful-rubin-u14pgu`**, under
`wallart/`. That is a separate pipeline with its own stores, buckets and
compliance rules. It is not duplicated here; read it on that branch.

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
  go to `tshirt-m12k`.
- FLUX.1 **schnell** is the image model, for its Apache-2.0 licence.
  FLUX.1-dev is non-commercial and must never be used on goods that are
  sold.
- Near-duplicate listings are treated as the main commercial risk. The
  wall-art branch blames 89% near-duplication for 424k listings not
  selling. Any catalogue generated here gets measured against that before
  it is uploaded.

## Access

RunPod and Cloudflare R2 are both connected and verified from the
environment "poster and t shirt data research". No terminal work is needed
from the seller. See `tshirt/ACCESS.md` for how each one is wired, what
does not work and why, so the failed routes are not retried.
