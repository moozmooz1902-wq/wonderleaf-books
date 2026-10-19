#!/usr/bin/env python3
"""Does the duplicate audit actually find duplicates?

The banded search is an approximation - it only compares panels that agree
exactly on at least one 16-bit slice of the hash - so "it ran and reported
0.6%" is not evidence that it works. This plants pairs whose distance is
known and checks they come back.

Run: python3 test_dup_audit.py
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_audit as D


def planted(n=3000, pairs=40, flips=10, seed=7):
    """Random hashes, with `pairs` of them duplicated and `flips` bits
    changed - well inside the 24-bit threshold, so every one must be found."""
    rng = np.random.default_rng(seed)
    V = rng.integers(0, 2, size=(n, 256), dtype=np.uint8)
    truth = set()
    for i in range(pairs):
        a, b = i * 7, n - 1 - i
        V[b] = V[a].copy()
        V[b][rng.choice(256, flips, replace=False)] ^= 1
        truth.add(a)
        truth.add(b)
    return V, truth


def main():
    V, truth = planted()
    skus = [(f"WA-{i:016x}", "luxvia-art") for i in range(len(V))]
    flags = D.audit(skus, V, None)
    found = {i for i, x in enumerate(flags) if x}
    caught, false = len(truth & found), len(found - truth)
    print(f"\nplanted {len(truth)}, caught {caught}, false alarms {false}")
    assert caught == len(truth), f"missed {len(truth) - caught} planted pairs"
    assert false == 0, f"{false} false alarms on untouched rows"

    # And a set with NO duplicates must come back empty, or the threshold is
    # catching noise rather than copies.
    rng = np.random.default_rng(11)
    clean = rng.integers(0, 2, size=(3000, 256), dtype=np.uint8)
    f2 = D.audit([(f"WA-{i:016x}", "x") for i in range(3000)], clean, None)
    assert f2.sum() == 0, f"{int(f2.sum())} false positives on random hashes"
    print("clean set: 0 flagged")
    print("\nPASS")


if __name__ == "__main__":
    main()
