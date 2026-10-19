#!/usr/bin/env python3
"""Find the near-duplicates across the whole catalogue, and list what to drop.

WHY THIS EXISTS RATHER THAN r2_audit_stores.py. That one downloads every
panel and compares every pair: 95 minutes at 227k panels, about six hours
at this size, and it has to fetch the catalogue to do it. The render pass
already had every panel decoded, so it wrote the 256-bit gradient hash of
the CROPPED artwork to `wallart/hashes/*.jsonl` on the way past. This reads
those and does the rest locally, with nothing to fetch but a few hundred
megabytes of text.

NEAR IS <= 24 OF 256 BITS, the same threshold as every audit before it, so
the numbers are comparable: 0.826% at 63,533 panels, 0.670% at 168,515,
0.648% at 226,992.

ONE HASH PER PANEL, not per listing. The four colourways of a design come
off one panel and share its hash, so they are not in this set at all -
which is the right answer to the trap r2_audit_stores.py had to special
case, where the colourways of one design read as near-duplicates of each
other and the feature counts as the bug.

HOW THE PAIRS ARE FOUND WITHOUT COMPARING EVERY PAIR. 960,000 panels is
4.6e11 pairs; at 24 bits of 256 a pair differs in under a tenth of the
hash, so two panels that are near-duplicates agree exactly on most short
slices of it. Split the hash into 16 slices of 16 bits, group by each
slice in turn, and compare only inside a group. A pair within 24 bits
misses every one of the 16 slices with probability about (1-0.793^16),
i.e. it is found better than 97 times in 100, and the work drops from
4.6e11 comparisons to about 1.2e8.

  usage: dup_audit.py --fetch          pull the hash files from the buckets
         dup_audit.py                  audit what is already pulled
         dup_audit.py --drop drop.txt  also write the SKUs to leave out
"""
import argparse, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
NEAR, BITS, BANDS = 24, 256, 16
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
# Cloudflare answers 403 to the default Python-urllib User-Agent on these
# hostnames - measured 19 Oct, and it looks exactly like the rate limit.


def fetch(dest):
    """Pull wallart/hashes/*.jsonl from every bucket over the public URL.

    Needs no credentials, which is the point: the R2 keys live on the
    RunPod template and must not be anywhere else.
    """
    import urllib.request
    import xml.etree.ElementTree as ET
    os.makedirs(dest, exist_ok=True)
    plan = json.load(open(os.path.join(HERE, "stores.json")))
    got = 0
    for s in plan["stores"]:
        base = s["pic_base"].rstrip("/")
        # r2.dev serves objects, not listings, so the names are DERIVED.
        # render_worker names each file by bucket and range only, and the
        # ranges are the same fixed partition r2_count_stores.py uses, so
        # the whole set is enumerable without a LIST call or a credential.
        pre = s["key_prefix"].strip("/") + "/"
        edges = ["WA-" + c for c in "0123456789abcdef"] + ["WA-g"]
        los = [pre] + [pre + e for e in edges]
        names = [f'{s["bucket"]}-{lo.replace("/", "_")}.jsonl' for lo in los]
        for n in names:
            p = os.path.join(dest, f"{s['bucket']}__{n}")
            if os.path.exists(p) and os.path.getsize(p):
                continue
            u = f"{base}/wallart/hashes/{n}"
            try:
                d = urllib.request.urlopen(
                    urllib.request.Request(u, headers=UA), timeout=120).read()
                open(p, "wb").write(d)
                got += 1
            except Exception as e:
                print(f"  failed {u}: {e}")
    print(f"fetched {got} hash files into {dest}")


def load(src):
    skus, bits = [], []
    for fn in sorted(os.listdir(src)):
        if not fn.endswith(".jsonl"):
            continue
        for line in open(os.path.join(src, fn)):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            skus.append((r["sku"], r["bucket"]))
            bits.append(np.frombuffer(r["h"].encode(), dtype=np.uint8) - 48)
    return skus, np.array(bits, dtype=np.uint8)


def audit(skus, V, drop_path=None):
    n = len(skus)
    print(f"{n:,} panels, {BITS}-bit hashes, near <= {NEAR} bits")
    packed = np.packbits(V, axis=1)                      # n x 32 bytes
    POP = np.unpackbits(np.arange(256, dtype=np.uint8)[:, None],
                        axis=1).sum(1).astype(np.uint16)
    width = BITS // BANDS
    flagged = np.zeros(n, bool)
    pairs = 0
    t0 = time.time()
    for b in range(BANDS):
        col = V[:, b * width:(b + 1) * width]
        key = np.packbits(col, axis=1).view(np.uint16).ravel() \
            if width == 16 else None
        if key is None:
            key = (col * (1 << np.arange(width)[::-1])).sum(1)
        order = np.argsort(key, kind="stable")
        ks = key[order]
        starts = np.flatnonzero(np.r_[True, ks[1:] != ks[:-1]])
        ends = np.r_[starts[1:], n]
        for s, e in zip(starts, ends):
            if e - s < 2:
                continue
            g = order[s:e]
            P = packed[g]
            # BLOCKED, because a group's size is not under our control. The
            # band keys are 16 bits of a hash, so groups average about
            # fifteen - but a flat colour field hashes to the same slice as
            # every other flat colour field, and one such group can hold
            # thousands. P[:, None, :] ^ P[None, :, :] on 4,000 rows is half
            # a gigabyte; on 20,000 it is thirteen. Skipping big groups
            # instead would drop exactly the designs most likely to BE
            # duplicates.
            B = 512
            for i in range(0, len(g), B):
                x = P[i:i + B, None, :] ^ P[None, :, :]
                d = POP[x].sum(2)
                for r in range(d.shape[0]):
                    d[r, i + r] = BITS
                hit = (d <= NEAR).any(1)
                pairs += int((d <= NEAR).sum() // 2)
                flagged[g[i:i + B][hit]] = True
        print(f"  band {b+1}/{BANDS}  flagged so far {flagged.sum():,}"
              f"  {time.time()-t0:.0f}s", flush=True)
    print(f"\nnear-duplicate listings: {flagged.mean():.3%} "
          f"({flagged.sum():,} of {n:,})")
    print(f"   for comparison: 0.826% at 63,533, 0.670% at 168,515, "
          f"0.648% at 226,992")
    if drop_path:
        # Keep the FIRST of every near-duplicate group, drop the rest: the
        # catalogue should lose the copies, not the design.
        drop = []
        for i in np.flatnonzero(flagged):
            sku, bucket = skus[i]
            drop.append(f"{bucket}\t{sku}")
        open(drop_path, "w").write("\n".join(drop) + "\n")
        print(f"   wrote {len(drop):,} SKUs to {drop_path}")
    return flagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(HERE, "hashes"))
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--drop")
    a = ap.parse_args()
    if a.fetch:
        fetch(a.src)
    skus, V = load(a.src)
    if not len(skus):
        sys.exit("no hashes - run the render pass first, or --fetch")
    audit(skus, V, a.drop)


if __name__ == "__main__":
    main()
