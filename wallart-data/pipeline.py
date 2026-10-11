#!/usr/bin/env python3
"""Base panel -> listings. Everything after the GPU, and none of it costs much.

For each generated panel:
    1. declutter  - paint out any signature the 10% crop did not already remove
    2. colourways - the original plus three recolours, 4 listings from 1 image
    3. layout     - 8.5% white margin or full bleed, decided per design, with
                    the edge check overriding a bleed that would clip a subject
    4. mockup     - the black frame listing photo (white and oak on request)
    5. manifest   - one row per listing, ready for the eBay file

Measured: about 0.37 s of one core per listing, so 5,000,000 listings is
roughly 515 core-hours, or 32 hours on a 16-core pod - about $21.

The duplicate audit is the part that matters commercially. The wall-art
branch measured store 1 at 89% near-duplicates and blamed that for 424,000
listings not selling. Every block generated here gets measured the same way
before it goes anywhere near eBay.
"""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from declutter import strip_marks
from recolour import recolour, RAMPS
from layout import compose, choose
from frames import mockup

COLOURWAYS = ["as-generated"] + list(RAMPS)[:3]
LISTING_PX = 1400


def dhash(im, n=16):
    """Gradient hash of the ARTWORK, 256 bits.

    Two earlier mistakes, both of which made the duplicate audit lie:

    * hashing the framed mockup. The wall, the moulding and the white margin
      are identical in every listing and swamp the artwork, so everything
      looks alike.
    * an average hash. It asks "is this pixel brighter than the mean", which
      for minimal line work on pale paper is "no" almost everywhere. A group
      of 26 visibly different designs - rings, dunes, contour, an arch, a
      hatch - came out with the same hash.

    A difference hash compares each pixel to its right-hand neighbour, so it
    encodes where the edges are, which is what actually distinguishes one
    design from another.
    """
    g = np.asarray(im.convert("L").resize((n + 1, n), Image.LANCZOS), dtype=np.int16)
    return "".join("1" if v else "0" for v in (g[:, 1:] > g[:, :-1]).ravel())


def one(args):
    src, job, outdir, want_mockup = args
    im = Image.open(src)
    # the code-drawn designs never carry a signature and are already in a
    # chosen palette, so they skip both the declutter pass and the recolours -
    # a fresh seed gives a genuinely new design, which a recolour does not
    if job.get("kind") == "line":
        panel, ways = im, ["as-drawn"]
    else:
        panel, _ = strip_marks(im)
        ways = COLOURWAYS
    rows = []
    for ci, cw in enumerate(ways):
        art = panel if ci == 0 else recolour(panel, cw)
        sku = f'{job["sku"]}-{ci}'
        sheet, used = compose(art, choose(job["tech"], sku))
        rec = {**{k: job[k] for k in ("subject", "tech", "gram", "pal", "kind")},
               "sku": sku, "base": job["sku"], "colourway": cw, "layout": used}
        rec["hash"] = dhash(art)        # the artwork, never the frame
        if want_mockup:
            p = os.path.join(outdir, sku + ".jpg")
            mockup(sheet, "black").resize((LISTING_PX, LISTING_PX),
                                          Image.LANCZOS).save(p, "JPEG", quality=90)
            rec["listing"] = os.path.basename(p)
        rows.append(rec)
    return rows


def audit(rows, near=24):
    """The test store 1 failed, which it failed at 89% near-duplicate.

    Two things this has to get right, and the first version got both wrong:

    * it must count LISTINGS that have a near neighbour, not pairs. Summing
      pairs reported 135% of the catalogue as duplicated, which is not a
      number that can exist.
    * the four colourways of one design ARE near-identical in structure, by
      design - that is the whole point of the colourway trick and it sits
      inside the four-per-design cap. Counting them is counting the feature
      as the bug. Only neighbours from a DIFFERENT base image count.
    """
    from collections import Counter
    n = len(rows)
    bits = np.array([[int(c) for c in r["hash"]] for r in rows], dtype=np.uint8)
    base = np.array([r["base"] for r in rows])
    exact = n - len(set(r["hash"] for r in rows))

    flagged = np.zeros(n, dtype=bool)
    B = 512
    for i0 in range(0, n, B):
        blk = bits[i0:i0 + B]
        d = (blk[:, None, :] != bits[None, :, :]).sum(axis=2)
        same = base[i0:i0 + B][:, None] == base[None, :]
        d[same] = 999                                   # ignore own colourways
        flagged[i0:i0 + B] = (d <= near).any(axis=1)

    trio = Counter((r["subject"], r["tech"], r["gram"]) for r in rows)
    print(f"\nDUPLICATE AUDIT on {n:,} listings  (256-bit gradient hash of the artwork,"
          f" colourways of the same design excluded)")
    print(f"   distinct images            {len(set(r['hash'] for r in rows)):,}")
    print(f"   exact repeats              {exact/n:>7.2%}")
    print(f"   listings with a near twin from another design "
          f"(<={near}/256 bits)  {flagged.mean():>7.2%}")
    print(f"   distinct subject+technique+composition  {len(trio):,}")
    print(f"   most repeated combination  {trio.most_common(1)[0][1]}x")
    print(f"   store 1, which did not sell:  89% near-duplicate")
    return float(flagged.mean())


if __name__ == "__main__":
    panels, manifest, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    want_mockup = "--no-mockups" not in sys.argv
    os.makedirs(outdir, exist_ok=True)
    jobs = {j["sku"]: j for j in (json.loads(l) for l in open(manifest))}
    tasks = []
    for sku, j in sorted(jobs.items()):
        for ext in (".jpg", ".png"):      # diffusion panels are jpg, code-drawn are png
            p = os.path.join(panels, sku + ext)
            if os.path.exists(p):
                tasks.append((p, j, outdir, want_mockup))
                break
    print(f"{len(tasks):,} panels -> {len(tasks)*len(COLOURWAYS):,} listings", flush=True)

    import time
    t0 = time.time()
    rows = []
    with ProcessPoolExecutor() as ex:
        for i, got in enumerate(ex.map(one, tasks, chunksize=4), 1):
            rows += got
            if i % 100 == 0:
                print(f"  {i:,}/{len(tasks):,}  {(time.time()-t0)/ (i*len(COLOURWAYS))*1000:.0f} ms/listing",
                      flush=True)
    el = time.time() - t0
    with open(os.path.join(outdir, "listings.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n{len(rows):,} listings in {el/60:.1f} min = "
          f"{el/len(rows)*1000:.0f} ms each (on {os.cpu_count()} cores)")
    from collections import Counter
    print("   layout mix:", dict(Counter(r["layout"] for r in rows)))
    audit(rows)
