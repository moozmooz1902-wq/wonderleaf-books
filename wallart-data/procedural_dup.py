#!/usr/bin/env python3
"""Can the code-drawn block carry 1,250,000 listings? Measure, don't assume.

`status.py` counts PROCEDURAL = 1_250_000 listings "drawn in code, no GPU"
and `cost_now.py` prices them at nothing. Both are planned numbers: probed
19 Oct, there is no code-drawn block anywhere in R2, and neither
gen_line.py nor gen_geometric.py has ever been run at scale. Before any of
it is built, the question that decides whether it is worth building is not
the compute - that is pennies - but whether the families can supply that
many designs that are DIFFERENT from each other. This repo treats
near-duplication as the main commercial risk (CLAUDE.md), and the
typography line blames 89% near-duplication for 424k unsold listings.

Same instrument as the real audit: 256-bit gradient hash of the ARTWORK
(not the framed mockup, not an average hash - see pipeline.dhash), near is
<= 24 of 256 bits, the threshold r2_audit_stores.py uses.

Two numbers per family set, because they answer different questions:

  SHARE      what fraction of a sample has a near neighbour. This is what
             the catalogue would look like with no duplicate gate, which is
             how the generators are written today.
  KEEP RATE  how many survive a gate applied in seed order - draw, compare
             against everything kept, keep or discard. This is what a gated
             pipeline would actually deliver, and its decline with n is the
             only honest way to extrapolate a ceiling.

Measured 19 Oct on this machine, 4 cores, no GPU and no R2:

  line, no gate      11.2% near at n=500 rising to 38.9% at n=12,000
  line, gated        8,975 of 12,000 survive; keep rate 92% at 1k falling
                     to 75% at 12k, survivor curve still nearly LINEAR
  geometric, no gate 50.8% at n=500 rising to 91.4% at n=6,000
  geometric, gated   1,910 of 6,000 survive; keep rate 63% at 1k falling
                     to 32% by 6k - that grammar is nearly spent, and one
                     pair of its 6,000 hashes was already identical

The geometric figures move a few points with the random stream, because
gen_geometric.design takes an rng rather than a seed and a different worker
split draws a different sequence: the same code read 44.2% at n=500 on a
two-worker split against 50.8% on a four-worker one. The line figures are
seed-addressed and reproduce exactly. Neither changes the conclusion, which
is an order of magnitude, not a few points.

For contrast the diffusion side measured 0.648% near-duplicates at 226,992
panels. So: the geometric grammar cannot be a meaningful part of 1.25M, and
the line families are the only candidate - with a gate, which does not
exist yet.

Drawing cost, measured: 0.168 s per line design and 0.207 s per geometric
one on one core, about 21,000 and 17,000 per core-hour.

  usage: procedural_dup.py [n_line] [n_geo] [procs]
"""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import multiprocessing as mp
import random

NEAR, BITS = 24, 256


def dhash_bits(im, n=16):
    """pipeline.dhash as a bit vector instead of a string, so a sample can go
    into one array and every pairwise distance comes from one matmul."""
    g = np.asarray(im.convert("L").resize((n + 1, n), Image.LANCZOS),
                   dtype=np.int16)
    return (g[:, 1:] > g[:, :-1]).ravel().astype(np.uint8)


def _line_chunk(a):
    import gen_line
    lo, hi, base = a
    return np.array([dhash_bits(gen_line.design(base + i)[0])
                     for i in range(lo, hi)])


def _geo_chunk(a):
    import gen_geometric
    lo, hi, base = a
    rng = random.Random(base + lo)       # disjoint stream per worker
    return np.array([dhash_bits(gen_geometric.design(rng)[0])
                     for _ in range(hi - lo)])


def draw(fn, n, base, procs=4):
    step = (n + procs - 1) // procs
    parts = [(i, min(i + step, n), base) for i in range(0, n, step)]
    with mp.Pool(procs) as p:
        return np.vstack(p.map(fn, parts))


def near_share(V):
    """Share of rows with at least one OTHER row within NEAR bits.

    a.b = BITS - 2*hamming on +/-1 vectors, so one matmul per block gives
    every distance. Blocked, so the full matrix never has to exist, and the
    diagonal is set out of range rather than masked - a row is not its own
    near neighbour, and forgetting that reports 100%.
    """
    S = V.astype(np.float32) * 2 - 1
    n = len(S)
    got = np.zeros(n, bool)
    B = 1024
    for i in range(0, n, B):
        d = (BITS - S[i:i + B] @ S.T) / 2
        for r in range(d.shape[0]):
            d[r, i + r] = BITS
        got[i:i + B] = (d <= NEAR).any(1)
    return got.mean()


def gated(V, report=None):
    """Greedy in seed order: the number a gated pipeline would deliver.

    Greedy is not the maximum independent set, and that is the point - it is
    what you get by drawing in order and keeping what passes, which is how
    the pipeline would run. Reports (drawn, kept) at each checkpoint so the
    keep rate's DECLINE is visible; the single final ratio hides it, and the
    decline is the whole question.
    """
    S = V.astype(np.float32) * 2 - 1
    kept = [0]
    K = S[0:1].copy()
    out, prev = [], 1
    for i in range(1, len(S)):
        if ((BITS - K @ S[i]) / 2 > NEAR).all():
            kept.append(i)
            K = np.vstack([K, S[i:i + 1]])
        if report and (i + 1) % report == 0:
            out.append((i + 1, len(kept), (len(kept) - prev) / report))
            prev = len(kept)
    return kept, out


def run(label, V, report):
    print(f"\n=== {label}  n={len(V):,}")
    n = 500
    while n <= len(V):
        print(f"   no gate   n={n:>8,}   near {near_share(V[:n])*100:7.3f}%")
        n *= 2
    if n // 2 != len(V):
        print(f"   no gate   n={len(V):>8,}   near {near_share(V)*100:7.3f}%")
    kept, marks = gated(V, report)
    for drawn, k, marg in marks:
        print(f"   gated     drawn {drawn:>8,}   kept {k:>8,}   "
              f"marginal {marg*100:5.1f}%")
    print(f"   gated     TOTAL kept {len(kept):,} of {len(V):,} "
          f"({len(kept)/len(V)*100:.1f}%)")
    u = len({v.tobytes() for v in V})
    print(f"   distinct hashes {u:,} of {len(V):,}")


if __name__ == "__main__":
    nl = int(sys.argv[1]) if len(sys.argv) > 1 else 12000
    ng = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
    pr = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if nl:
        t = time.time()
        L = draw(_line_chunk, nl, 1_000_000, pr)
        print(f"line {nl:,} drawn in {time.time()-t:.0f}s on {pr} cores")
        run("line", L, max(1000, nl // 12))
    if ng:
        t = time.time()
        G = draw(_geo_chunk, ng, 90_000, pr)
        print(f"geo  {ng:,} drawn in {time.time()-t:.0f}s on {pr} cores")
        run("geometric", G, max(1000, ng // 6))
