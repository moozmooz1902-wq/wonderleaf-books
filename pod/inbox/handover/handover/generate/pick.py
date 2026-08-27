"""
select.py — choose which designs to build, weighted by market research.

The engine holds 1.57M designs. Building them in index order would give you
whatever the first subjects happen to be. This picks a balanced, niche-weighted
set so a 50,000 run covers the categories that actually convert.

WEIGHTS come from 2026 market research:
  * pet breeds and occupation-intent niches earn most across every platform,
    because buyers search with intent rather than browsing
  * dragons, gothic and Norse are proven high-volume sellers on eBay UK
  * dark academia, cottagecore and Y2K are climbing rather than saturated
  * broad "funny" and generic cottagecore are heavily saturated — avoided

CAPS stop any one subject sprawling. No subject exceeds its share, so the
catalogue never looks like one idea repeated.
"""

import argparse, os, csv, random, subprocess
from collections import Counter, defaultdict

from graphics import SUBJECTS, design, TOTAL_SPACE, _OFFSETS

# family -> share of the run. Sums to 1.0.
WEIGHTS = {
    "breed":     0.24,   # highest intent, highest earning
    "dragon":    0.10,   # proven eBay UK seller
    "wild":      0.12,
    "gothic":    0.08,
    "norse":     0.06,
    "bird":      0.05,
    "sea":       0.05,
    "warrior":   0.05,
    "mythic":    0.05,
    "academia":  0.04,   # climbing, low saturation
    "cottage":   0.03,
    "y2k":       0.03,
    "dino":      0.03,
    "reptile":   0.02,
    "cute":      0.02,
    "cosmic":    0.02,
    "botanical": 0.01,
    "machine":   0.01,
    "nature":    0.01,
}

# index range for each subject, so we can sample within one subject
_RANGES = {}
for _i, (_name, _fam) in enumerate(SUBJECTS):
    _start = _OFFSETS[_i]
    _end = _OFFSETS[_i + 1] if _i + 1 < len(_OFFSETS) else TOTAL_SPACE
    _RANGES[_name] = (_start, _end, _fam)

BY_FAMILY = defaultdict(list)
for _name, (_s, _e, _f) in _RANGES.items():
    BY_FAMILY[_f].append(_name)


# Roughly what share of the run should be black-and-white. Monochrome done
# well is high impact and prints beautifully in single-colour DTF, but the
# catalogue should read colourful overall.
MONO_TARGET = 0.12


# Hard caps on how often the same CONCEPT may recur, whatever the art style.
# Without these, one subject+scene+pose ("a Vizsla with luminous particles,
# two subjects") appeared 18 times with only the style differing — which is
# the same failure as the text run, in a different costume.
MAX_PER_SUBJECT_SCENE_COMP = 2    # same concept, at most 2 art styles
MAX_PER_SUBJECT_SCENE = 20        # same subject+setting, but different poses

# BREADTH CAP. Batch 1 was the wrong shape: 290 subjects averaging 486
# listings each, so 820 Welsh Dragon listings mostly competed with each other
# for a fixed amount of search traffic. With ~1,000 subjects the same total
# spreads across ten times the search surface. This caps how deep any one
# subject can go, so volume has to come from MORE NICHES rather than more of
# the same one.
#
# Set to 0 to disable. Otherwise a run of N designs allows roughly
# N / subjects * SPREAD_SLACK per subject.
SPREAD_SLACK = 1.6


def select(n, seed=42, exclude=None):
    """
    Return n design indices, niche-weighted, with concept caps applied.

    Builds the capped set DIRECTLY rather than over-selecting and filtering:
    for each subject, walk its (scene, composition) pairs and take at most
    MAX_PER_SUBJECT_SCENE_COMP styles from each. Filtering after the fact
    wasted most of what it picked and could not reach the true ceiling.
    """
    # Must use _COMP_BY_SUBJECT, not _COMP_BY_FAM: human subjects have their
    # compositions filtered per-subject (no helmet on a mermaid), and the
    # offsets in graphics.py are computed from that. Using the family list
    # here produced indices that decoded to the wrong design.
    from graphics import (SUBJECTS, _STYLE_BY_FAM, _SCENE_BY_SUBJECT,
                          _COMP_BY_SUBJECT, _OFFSETS, TOTAL_SPACE)
    rng = random.Random(seed)
    exclude = exclude or set()

    # candidate pool per subject, already respecting the caps
    by_subject = {}
    for si, (name, fam) in enumerate(SUBJECTS):
        styles = _STYLE_BY_FAM[fam]
        scenes = _SCENE_BY_SUBJECT[si]
        comps = _COMP_BY_SUBJECT[si]
        base = _OFFSETS[si]
        ns, nc = len(scenes), len(comps)

        picks, per_scene = [], {}
        order = [(sc, cp) for sc in range(ns) for cp in range(nc)]
        rng.shuffle(order)
        for sc, cp in order:
            if per_scene.get(sc, 0) >= MAX_PER_SUBJECT_SCENE:
                continue
            # which styles to use for this exact concept
            st_order = list(range(len(styles)))
            rng.shuffle(st_order)
            taken = 0
            for st in st_order:
                if taken >= MAX_PER_SUBJECT_SCENE_COMP:
                    break
                if per_scene.get(sc, 0) >= MAX_PER_SUBJECT_SCENE:
                    break
                # mixed-radix: comp is the fastest axis, then scene, then style
                idx = base + cp + nc * (sc + ns * st)
                if idx in exclude:
                    continue
                picks.append(idx)
                per_scene[sc] = per_scene.get(sc, 0) + 1
                taken += 1
        rng.shuffle(picks)
        by_subject[name] = picks

    # Per-subject ceiling for this run, so no single niche dominates.
    if SPREAD_SLACK:
        cap = max(4, int(n / max(len(SUBJECTS), 1) * SPREAD_SLACK))
        for k in by_subject:
            by_subject[k] = by_subject[k][:cap]

    # take proportionally from each family, then round-robin across subjects
    out = []
    for fam, share in WEIGHTS.items():
        subjects = BY_FAMILY.get(fam, [])
        if not subjects:
            continue
        want = int(n * share)
        pools = [by_subject[s] for s in subjects if by_subject.get(s)]
        if not pools:
            continue
        taken, pos = 0, 0
        while taken < want and any(pos < len(p) for p in pools):
            for p in pools:
                if pos < len(p):
                    out.append(p[pos])
                    taken += 1
                    if taken >= want:
                        break
            pos += 1

    # Any family that cannot fill its weighted share under the caps leaves a
    # shortfall. Top up from whatever is left rather than returning short —
    # the caps are the hard rule, the weights are a preference.
    if len(out) < n:
        chosen = set(out)
        spare = [i for s in by_subject.values() for i in s if i not in chosen]
        rng.shuffle(spare)
        out.extend(spare[:n - len(out)])

    # Spread every subject EVENLY across the whole queue.
    #
    # A plain round-robin looks mixed at the start but is not: subjects with
    # few available designs run out first, so the tail fills up with whichever
    # subjects had the most. Split seven ways, the first store saw 988 subjects
    # and the last only 529, with one subject appearing 41 times. Since each
    # store takes a contiguous slice, that matters — every store must get the
    # full spread.
    #
    # Instead give each design a position in 0..1 based on how far through its
    # OWN subject it is, then order by that. A subject with 4 designs lands at
    # roughly 0.12, 0.37, 0.62, 0.87; one with 40 lands every 0.025. Both end
    # up evenly distributed no matter how many they have.
    from collections import defaultdict as _dd
    buckets = _dd(list)
    for idx in out:
        buckets[design(idx)["subject"]].append(idx)

    placed = []
    for name, items in buckets.items():
        rng.shuffle(items)
        k = len(items)
        # random offset so subjects do not all line up at the same points
        jitter = rng.random()
        for i, idx in enumerate(items):
            phase = ((i + 0.5) / k + jitter) % 1.0
            placed.append((phase, idx))

    placed.sort(key=lambda t: t[0])
    return [idx for _, idx in placed][:n]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=50000)
    ap.add_argument("--out", default="generation_queue.csv")
    ap.add_argument("--exclude", nargs="*", default=[],
                    help="previous queue CSVs — their designs are never "
                         "reused, so a later batch cannot overlap an earlier one")
    ap.add_argument("--ledger", default="used_designs.txt",
                    help="running record of every design index ever queued. "
                         "Read before selecting and appended after, so batches "
                         "months apart still cannot collide. Set to '' to skip")
    args = ap.parse_args()

    # Indices already used by earlier batches. Without this, a second run
    # would re-pick from the same weighted pool and duplicate designs that are
    # already listed.
    used = set()

    # The LEDGER is the durable record. Passing --exclude with the right CSV
    # every time is easy to get wrong months later, and one slip means
    # duplicate listings — the failure that had to be reversed with eBay End
    # files once already. The ledger accumulates automatically instead.
    # A missing ledger is the one way duplicates get through. It is not an
    # error — the first ever batch has none — but it must never pass silently,
    # because the second batch missing it would relist designs already on
    # eBay. That failure took End files to undo once.
    if args.ledger and not os.path.exists(args.ledger) and not args.exclude:
        print()
        print("=" * 68)
        print(" NO LEDGER FOUND — nothing will be excluded")
        print("=" * 68)
        print(f" Expected: {args.ledger}")
        print()
        print(" This is correct ONLY for the very first batch.")
        print(" If anything has been generated before, stop and run:")
        print()
        print("     python3 rebuild_ledger.py r2:BUCKET/raw [r2:BUCKET2/raw ...]")
        print()
        print(" That reads what is already in R2, so it works even when the")
        print(" old queue files are gone with a terminated pod.")
        print("=" * 68)
        try:
            if input(" Type FIRST to confirm this is the first batch: ").strip() != "FIRST":
                raise SystemExit("stopped — build the ledger first")
        except EOFError:
            raise SystemExit("stopped — no ledger and not confirmed")

    if args.ledger and os.path.exists(args.ledger):
        with open(args.ledger, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.isdigit():
                    used.add(int(line))
        print(f"ledger: {len(used):,} designs already used")

    for prev in args.exclude:
        with open(prev, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                used.add(int(r["index"]))
    if used:
        print(f"excluding {len(used):,} designs from earlier batches")

    # over-select, then drop the used ones and trim
    idxs = select(args.count, exclude=used)
    if len(idxs) < args.count:
        raise SystemExit(
            f"only {len(idxs):,} unused designs available for the requested "
            f"{args.count:,} — widen the vocabulary in graphics.py")
    idxs = idxs[:args.count]
    rows = [design(i) for i in idxs]

    # uniqueness guard — prompts must all differ
    prompts = [r["prompt"] for r in rows]
    dupes = len(prompts) - len(set(prompts))
    if dupes:
        raise SystemExit(f"ABORT: {dupes} duplicate prompts. Fix before building.")

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    if args.ledger:
        with open(args.ledger, "a", encoding="utf-8") as f:
            for i in idxs:
                f.write(f"{i}\n")
        print(f"ledger updated  : {args.ledger}")

        # Push a copy to R2. The pod this runs on will be terminated, and the
        # ledger is the record of what must never be reused.
        #
        # This REPORTS the outcome either way. A backup that fails quietly is
        # worse than none, because it invites terminating a pod that still
        # holds the only copy.
        remote = os.environ.get("R2_REMOTE", "")
        if not remote:
            print()
            print("  NOTE: R2_REMOTE is not set, so the ledger was NOT backed")
            print("        up. It exists only on this pod. Before terminating:")
            print("          export R2_REMOTE=r2:YOUR-BUCKET/art")
            print("          python3 state.py backup $R2_REMOTE")
        else:
            base = remote.rsplit("/", 1)[0] if "/" in remote else remote
            failed = []
            for name, src in ((os.path.basename(args.ledger), args.ledger),
                              ("generation_queue.csv", args.out)):
                r = subprocess.run(
                    f"rclone copyto '{src}' '{base}/state/{name}'",
                    shell=True, capture_output=True, text=True)
                if r.returncode == 0:
                    print(f"backed up       : {base}/state/{name}")
                else:
                    failed.append(name)
            if failed:
                print()
                print("  BACKUP FAILED for: " + ", ".join(failed))
                print("  These files exist ONLY on this pod. Fix rclone and run")
                print(f"  python3 state.py backup {base} before terminating it.")

    print(f"selected        : {len(rows):,} designs")
    print(f"duplicate prompts: {dupes}")
    print(f"unique subjects : {len(set(r['subject'] for r in rows))}")
    print(f"unique scenes   : {len(set(r['scene'] for r in rows))}")
    print(f"unique styles   : {len(set(r['style'] for r in rows))}")

    fam = Counter(r["family"] for r in rows)
    print("\nfamily mix:")
    for f_, c in fam.most_common():
        print(f"  {f_:<10} {c:>6,}  ({c/len(rows)*100:4.1f}%)")

    top = Counter(r["subject"] for r in rows).most_common(1)[0]
    print(f"\nlargest subject : {top[0]} at {top[1]} "
          f"({top[1]/len(rows)*100:.2f}% of the run)")
    print(f"written to      : {args.out}")
