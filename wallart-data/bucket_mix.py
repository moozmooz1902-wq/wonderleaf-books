#!/usr/bin/env python3
"""Is every store bucket getting the same MIX, or is one getting all the cats?

The seller's rule: "mix data gets uploaded and mix data throughout all
buckets, I want so all has variation of data." This is the check.

Nothing is sorted into buckets afterwards. A panel is routed the instant it
is made - gen_gated.py asks allocate.store_for(sku) and PUTs it straight
into that store's bucket, then deletes it from the pod. There is no staging
area and no sorting pass, so there is no moment where one bucket is holding
a run of one subject.

Two separate mechanisms do the work, and they are worth keeping distinct:

  WHICH BUCKET      weighted rendezvous hashing on the SKU (allocate.py).
                    Deterministic, and weighted so the four buckets fill in
                    proportion to their quotas: 50 / 20 / 20 / 10.
  WHAT ORDER        the grid is sorted by SKU hash, which is a stable
                    pseudo-random shuffle, so consecutive jobs are unrelated
                    subjects. Measured on the pool: 476 distinct subjects in
                    the first 500 jobs, longest same-subject run 2.

Because the order is shuffled and the routing is a hash of the same SKU,
every bucket receives the same mixture continuously, from the first hour.

    python3 bucket_mix.py            # reads the pods' done.txt lists
"""
import collections, glob, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "gen"))


def pods():
    out = subprocess.run(["curl", "-sS", "--max-time", "60",
                          "https://rest.runpod.io/v1/pods"],
                         capture_output=True, text=True).stdout
    d = json.loads(out)
    d = d if isinstance(d, list) else d.get("pods", [])
    return [p for p in d if p.get("desiredStatus") == "RUNNING"
            and str(p.get("name", "")).startswith("wa-v3-")]


def skus_from_pods():
    out = set()
    for p in pods():
        t = subprocess.run(["curl", "-sS", "--max-time", "90",
                            f"https://{p['id']}-8000.proxy.runpod.net/art/done.txt"],
                           capture_output=True, text=True).stdout
        out |= {l.strip() for l in t.splitlines() if l.strip()}
    return out


def report(skus):
    import allocate
    import gen_gated as G
    want = set(skus)
    meta = {}
    subs = json.load(open(os.path.join(HERE, "gen", "subjects.json")))
    for j in G.expand(subs):
        if j["sku"] in want:
            meta[j["sku"]] = j
    rows = [(allocate.store_for(s)["bucket"], j["kind"], j["tech"], j["pal"],
             j["subject"]) for s, j in meta.items()]
    bk = sorted({r[0] for r in rows})
    n = len(rows)
    plan = {x["bucket"]: x["listings"] for x in allocate.PLAN["stores"]}
    tot = sum(plan.values())

    print(f"{n:,} panels resolved\n")
    print(f"{'bucket':<20}{'made':>9}{'share':>8}{'quota':>8}")
    for b in sorted(bk, key=lambda x: -plan[x]):
        c = sum(1 for r in rows if r[0] == b)
        print(f"{b:<20}{c:>9,}{c/n:>7.1%}{plan[b]/tot:>8.1%}")

    for idx, title in ((1, "SUBJECT KIND"), (2, "TECHNIQUE"), (3, "PALETTE")):
        print(f"\n{title}, share within each bucket")
        print(f"  {'':<16}" + "".join(f"{b.split('-')[0][:9]:>11}" for b in bk))
        for k in sorted({r[idx] for r in rows}):
            line = f"  {k:<16}"
            for b in bk:
                sub = [r for r in rows if r[0] == b]
                line += f"{sum(1 for r in sub if r[idx] == k)/len(sub):>10.1%} "
            print(line)

    print("\nDISTINCT SUBJECTS in each bucket")
    for b in bk:
        sub = [r for r in rows if r[0] == b]
        print(f"  {b:<20}{len({r[4] for r in sub}):>6,} over {len(sub):,} panels")


if __name__ == "__main__":
    report(skus_from_pods())
