#!/usr/bin/env python3
"""The job grid, extracted verbatim from gen/gen_gated.py.

Not a reimplementation: `sku_for`, `_thin` and `expand` are copied
character for character, because a SKU is a hash of the job and the
slightest difference in how the grid is built gives different SKUs, which
would point every listing at a picture that does not exist.

It exists so a pod can rebuild the grid without carrying gen_gated.py's
thirty-six kilobytes of generation machinery - a pod's whole start command
has to fit in about sixty thousand characters, bundle included.

  python3 grid.py gen/subjects.json   # prints the job count
"""
import hashlib, itertools, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def sku_for(job, prefix="WA"):
    """A SKU derived from WHAT the job is, never from where it sits in a list.

    This is what makes the run resumable. The first version numbered jobs by
    position after a seeded shuffle, which is reproducible only while the
    subject list never changes - add one flower and every SKU after it moves,
    so everything already generated looks unfinished and gets made again.
    Hashing the job content instead means a SKU is the same for ever, lists
    can be extended at any time, and "what is already done" is simply "what
    is already in the bucket".

    CRC32 IS NOT WIDE ENOUGH. It collided on the very first run of 12,834
    jobs - 2^32 means a collision is likely past about 65,000, and 937,500
    jobs would collide roughly a hundred thousand times, each one silently
    dropping a design. 64 bits puts that at effectively never.
    """
    key = "|".join(str(job[k]) for k in ("kind", "subject", "tech", "gram", "pal"))
    return f"{prefix}-{hashlib.blake2b(key.encode(), digest_size=8).hexdigest()}"


# Measured on the finished 12,834-panel block: 1.5% of designs have a near
# twin from a DIFFERENT design, and every one of the closest pairs is a
# minimal composition - a red fox and a whippet, cow parsley and a curlew,
# a kingfisher and a barn owl. Different subjects, but "small and centred on
# a vast expanse of plain paper" looks the same at thumbnail size whatever
# is in the middle, which is exactly how a buyer sees an eBay search grid.
# The hash is not being fooled; it is reporting something true.
#
# So these compositions are capped. They sell, and they are cheap to make,
# but at an equal share of the grid they would be a sixth of five million
# listings all looking alike. The cap is applied by SKU hash, so which ones
# survive is deterministic and a resumed run makes the same choices.
# C2_disc joined these on 11 Oct. The audit found every near-twin in the
# first block was a minimal composition - a small subject on an empty
# sheet - and "one large disc centred on a plain flat ground" is that
# same picture for all 155 celestial subjects: a circle. Capped like the
# other two rather than dropped, because the composition does sell.
# G10_abstract joined on 12 Oct. Even reworded to build the abstraction
# FROM the place, an all-over field with no focal point is the
# composition least able to tell one subject from another, and it was
# 8 of the 28 panels in the audit's closest-pair list.
THIN_GRAMMARS = {"G8_minimal": 0.35, "B1_specimen": 0.45, "C2_disc": 0.30,
                 "G10_abstract": 0.50}


def _thin(jobs):
    kept = []
    for j in jobs:
        keep = THIN_GRAMMARS.get(j["gram"])
        if keep is None:
            kept.append(j); continue
        h = int(hashlib.blake2b(j["sku"].encode(), digest_size=4).hexdigest(), 16)
        if (h % 1000) / 1000.0 < keep:
            kept.append(j)
    return kept


def expand(subjects, thin=True):
    """Build the full grid from the subject lists, exactly as the planner does,
    so a pod and this machine always agree on which SKU is which job."""
    import itertools, random, prompts as P
    jobs = []
    for s_, t, g, c in itertools.product(subjects.get("place", []),
                                         P.TECHNIQUE, P.GRAMMAR_PLACE, P.PALETTE):
        if P.ok(t, g, s_, c):
            jobs.append(dict(kind="place", subject=s_, tech=t, gram=g, pal=c,
                             prompt=P.place_prompt(s_, t, g, c)))
    for s_, t, g, c in itertools.product(subjects.get("creature", []),
                                         P.TECHNIQUE, P.GRAMMAR_CREATURE, P.PALETTE):
        if P.ok(t, g, s_, c):
            jobs.append(dict(kind="creature", subject=s_, tech=t, gram=g, pal=c,
                             prompt=P.creature_prompt(s_, t, g, c)))
    for s_, t, g, c in itertools.product(subjects.get("botanical", []),
                                         P.TECHNIQUE, P.GRAMMAR_BOTANICAL, P.PALETTE):
        if P.ok(t, g, s_, c):
            jobs.append(dict(kind="botanical", subject=s_, tech=t, gram=g, pal=c,
                             prompt=P.botanical_prompt(s_, t, g, c)))
    # The three kinds added 11 Oct 2026. Each carries its own grammars, which
    # is the point: more compositions that are genuinely different beats more
    # subjects the model renders the same way.
    for kind, grams, fn in (("celestial", P.GRAMMAR_CELESTIAL, P.celestial_prompt),
                            ("stilllife", P.GRAMMAR_STILLLIFE, P.stilllife_prompt),
                            ("architecture", P.GRAMMAR_ARCH, P.architecture_prompt)):
        for s_, t, g, c in itertools.product(subjects.get(kind, []),
                                             P.TECHNIQUE, grams, P.PALETTE):
            if P.ok(t, g, s_, c):
                jobs.append(dict(kind=kind, subject=s_, tech=t, gram=g, pal=c,
                                 prompt=fn(s_, t, g, c)))
    # The copyright gate, enforced here rather than reported somewhere else.
    # A blocked subject must never reach a prompt, let alone a listing.
    try:
        # the bundle unpacks flat, so ip_check.py lands beside this file
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import ip_check
        bad = ip_check.check_subjects(subjects)
        if bad:
            raise SystemExit(f"IP BLOCKLIST: refusing to generate {bad}")
        print(f"ip gate: {len(jobs):,} jobs, no blocked subject", flush=True)
    except ImportError:
        print("ip gate: ip_check.py not shipped to this pod - REFUSING", flush=True)
        raise SystemExit(2)

    pre = subjects.get("prefix", "WA")
    for j in jobs:
        j["sku"] = sku_for(j, pre)
    # ordered by the SKU hash: a stable pseudo-random shuffle, so any prefix
    # of the work is a fair mix of subjects, and adding subjects later
    # interleaves them instead of renumbering anything
    jobs.sort(key=lambda j: j["sku"])
    if thin:
        before = len(jobs)
        jobs = _thin(jobs)
        print(f"minimal-composition cap: {before - len(jobs):,} of {before:,} dropped",
              flush=True)
    seen = {}
    for j in jobs:                       # a collision would silently drop work
        seen.setdefault(j["sku"], []).append(j)
    dup = {k: v for k, v in seen.items() if len(v) > 1}
    if dup:
        raise SystemExit(f"SKU collision on {len(dup)} jobs: {list(dup)[:3]}")
    return jobs


if __name__ == "__main__":
    jobs = expand(json.load(open(sys.argv[1])))
    print(f"{len(jobs):,} jobs; first {jobs[0]['sku']}")
