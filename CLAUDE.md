# Wonderleaf — standing rules

## Artwork must be DTF-printable. This is not negotiable.

Everything Wonderleaf sells is printed direct-to-film. DTF cannot print
semi-transparent ink: wherever alpha sits between 0 and 255 the RIP lays down
a dithered white underbase and the colour comes out weak and patchy. The
adhesive powder also needs a dot of roughly half a millimetre to grip —
anything finer sheds in the shaker or lifts off in the wash.

So every print file, for every product, now and in future:

| | |
|---|---|
| **At least 90% of inked pixels fully opaque** | target is ~98%; only the anti-aliased edge of a shape should be partial |
| **No feature below 0.5 mm** | 6 px at 300 dpi |
| **RGBA, transparent background** | never a matte, never flattened onto black |
| **300 dpi** | 4500 × 5400 for tees |

Verify before committing to a batch — a full run is hours of pod time:

    python3 pod/ebay/tools/check_print_files.py 'print/*.png'

`check.py` in the pod bundle asserts the same thing on one design before the
run starts, so a renderer that has regressed cannot burn a whole run.

### What this rules out

- **Distressed / worn textures made by fading alpha.** This is what caught us:
  the tee renderer multiplied glyph alpha by a blurred noise mask and only 42%
  of the ink came out solid. `--distress` still exists and is binary now, but
  it is OFF by default and should stay off — holes in the ink are exactly
  where powder has nothing to hold.
- **Soft glows, drop shadows, feathered edges, smoke, gradients to nothing.**
  All of these are partial alpha by definition.
- **Hairlines and fine detail** below 0.5 mm at final print size.

### The one exception

Artwork that genuinely cannot be made solid — the older painterly SDXL
designs, where the fade *is* the picture — goes through `halftone.py`
instead. It converts the fade into solid dots big enough to hold powder,
which reads as a smooth gradient at arm's length.

**One universal setting: 28 LPI, 0.5 mm smallest dot.** Those are the
defaults, so it is just:

    python3 pod/ebay/fulfilment/halftone.py in.png out.png

Do not tune per design. A single setting is what makes this printable without
thinking about it.

## Other standing rules

- **eBay changes go through File Exchange CSV.** No API, no software
  authorised against the accounts.
- **`PostalCode` stays blank.** A shared postcode ties the stores together.
  eBay falls back to each account's own, which is already right.
- **Titles must not claim Canvas, Framed or Ready to Hang** on unframed A4
  paper.
- **This repository is public.** No credentials, ever — rclone reads its keys
  from the pod's environment.
