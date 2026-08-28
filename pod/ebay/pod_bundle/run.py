#!/usr/bin/env python3
"""
Render the t-shirt catalogue: two files per design.

    <design_id>.png   4500x5400 transparent  -> print/  (goes to the printer)
    <design_id>.jpg   2000x2000              -> mock/   (the eBay image)

CPU ONLY. These are typography on black - no GPU, no model, no image API.
Resumable: anything already on disk is skipped, so it is safe to re-run.

    python3 run.py --workers 32
    python3 run.py --workers 32 --limit 200      # smoke test first
"""
import argparse, json, multiprocessing as mp, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("BLANK_TEE", os.path.join(HERE, "blank.png"))

import render_designs as rd
import photo_mockup as pm

ART = os.path.join(HERE, "print")
MOCK = os.path.join(HERE, "mock")
FONTS = os.path.join(HERE, "fonts")


def one(d):
    png = os.path.join(ART, d["design_id"] + ".png")
    jpg = os.path.join(MOCK, d["design_id"] + ".jpg")
    if os.path.exists(png) and os.path.exists(jpg):
        return "skip"
    try:
        art = None
        if not os.path.exists(png):
            art = rd.render(d, FONTS)
            art.save(png, compress_level=6)
        if not os.path.exists(jpg):
            pm.build(art if art is not None else png, jpg)
        return "ok"
    except Exception as e:
        return f"FAIL {d['design_id']}: {type(e).__name__} {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", default=os.path.join(HERE, "catalogue.json"))
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    os.makedirs(ART, exist_ok=True)
    os.makedirs(MOCK, exist_ok=True)
    designs = json.load(open(a.catalogue))
    if a.limit:
        designs = designs[:a.limit]

    print(f"  {len(designs):,} designs, {a.workers} workers")
    t0, ok, skip, fail = time.time(), 0, 0, []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(one, designs, chunksize=16), 1):
            if r == "ok":
                ok += 1
            elif r == "skip":
                skip += 1
            else:
                fail.append(r)
            if i % 1000 == 0:
                el = time.time() - t0
                print(f"  {i:,}/{len(designs):,}  {el/60:.1f} min  "
                      f"eta {(len(designs)-i)*el/i/60:.0f} min", flush=True)

    print(f"\n  rendered {ok:,}  skipped {skip:,}  failed {len(fail)}")
    for f in fail[:10]:
        print("   ", f)
    print(f"  total {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
