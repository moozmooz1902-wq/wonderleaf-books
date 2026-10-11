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

    `near` is the Hamming distance within the 256-bit hash at which two
    designs count as the same thing to a browsing buyer. 24/256 is under 10%
    of the bits.
    """
    from collections import Counter
    h = Counter(r["hash"] for r in rows)
    exact = sum(c - 1 for c in h.values() if c > 1)
    keys = list(h)
    bits = np.array([[int(c) for c in k] for k in keys], dtype=np.int8)
    counts = np.array([h[k] for k in keys])
    nd = 0
    for i in range(len(keys)):
        d = (bits[i] != bits[i + 1:]).sum(axis=1)
        nd += int((counts[i + 1:][d <= near]).sum())
    trio = Counter((r["subject"], r["tech"], r["gram"]) for r in rows)
    print(f"\nDUPLICATE AUDIT on {len(rows):,} listings  (256-bit gradient hash "
          f"of the artwork)")
    print(f"   distinct images            {len(h):,}")
    print(f"   exact repeats              {exact/len(rows):>7.2%}")
    print(f"   near-duplicates (<={near}/256 bits apart)  "
          f"{nd/len(rows):>7.2%}")
    print(f"   distinct subject+technique+composition  {len(trio):,}")
    print(f"   most repeated combination  {trio.most_common(1)[0][1]}x")
    print(f"   store 1, which did not sell:  89% near-duplicate")
    return exact / len(rows)


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
