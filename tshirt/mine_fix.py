#!/usr/bin/env python3
"""Mine slogan templates, deduped by the DESIGNS they cover.

The first pass counted the same slogan four times because the mask slid
along it ("ORIGINAL PARTS VINTAGE AGED TO {X} ..." vs "... AGED {X} ...").
Word-overlap dedupe misses that. The only honest fix is greedy set cover:
repeatedly take the template that explains the most units NOT already
explained, so every unit is counted exactly once.
"""
import csv, heapq, json, re, sys
from collections import Counter, defaultdict

SRC = sys.argv[1] if len(sys.argv) > 1 else "designs_read.jsonl"
STOP = {"a","an","the","of","and","or","to","in","on","is","it","for","with",
        "my","me","i","you","your","we","our","this","that","at","as","be",
        "but","not","are","was","by","from"}


def norm(s):
    s = re.sub(r"[^A-Z0-9' ]+", " ", str(s).upper())
    return re.sub(r"\s+", " ", s).strip()


def load(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try: r = json.loads(line)
        except Exception: continue
        ls = r.get("text_lines") or []
        if not isinstance(ls, list): ls = [str(ls)]
        r["lines"] = [str(x).strip() for x in ls if str(x).strip()]
        r["slogan"] = " ".join(r["lines"])
        r["sold"] = r.get("sold") or 0
        rows.append(r)
    return rows


def skeletons(toks):
    """Every 1-4 token span masked out, where the rest still says something."""
    for i in range(len(toks)):
        for j in range(i + 1, min(i + 4, len(toks)) + 1):
            span = toks[i:j]
            if all(t in STOP for t in span):
                continue
            skel = tuple(toks[:i]) + ("{X}",) + tuple(toks[j:])
            if sum(1 for t in skel if t != "{X}" and t not in STOP) < 2:
                continue
            yield skel, " ".join(span)


def main():
    rows = load(SRC)
    texted = [r for r in rows if 3 <= len(norm(r["slogan"]).split()) <= 14]
    total_units = sum(r["sold"] for r in rows)
    text_units = sum(r["sold"] for r in texted)
    print(f"{len(rows):,} designs, {total_units:,} units")
    print(f"{len(texted):,} carry a usable slogan (3-14 words), "
          f"{text_units:,} units\n")

    # pass 1 - which skeletons recur at all
    seen = Counter()
    for r in texted:
        for skel, _ in set(skeletons(tuple(norm(r["slogan"]).split()))):
            seen[skel] += 1
    keep = {s for s, n in seen.items() if n >= 4}
    print(f"{len(seen):,} candidate skeletons, {len(keep):,} recur 4+ times")

    # pass 2 - who they cover, and with what fillers
    cover = defaultdict(set); fill = defaultdict(Counter)
    for k, r in enumerate(texted):
        for skel, span in skeletons(tuple(norm(r["slogan"]).split())):
            if skel in keep:
                cover[skel].add(k); fill[skel][span] += 1
    cand = [s for s in cover if len(fill[s]) >= 4]
    print(f"{len(cand):,} of those take 4+ different fillers\n")

    # greedy set cover, lazy-evaluated, by units not yet explained
    sold = [r["sold"] for r in texted]
    claimed = set(); chosen = []
    heap = [(-sum(sold[i] for i in cover[s]), s) for s in cand]
    heapq.heapify(heap)
    while heap and len(chosen) < 300:
        neg, s = heapq.heappop(heap)
        new = cover[s] - claimed
        gain = sum(sold[i] for i in new)
        if not heap or gain >= -heap[0][0]:
            if gain < max(50, text_units * 0.0005):
                break
            claimed |= new
            chosen.append({
                "template": " ".join(s),
                "distinct_fillers": len(fill[s]),
                "designs": len(new),
                "units_explained": gain,
                "top_fillers": " | ".join(f for f, _ in fill[s].most_common(15)),
            })
        else:
            heapq.heappush(heap, (-gain, s))

    exp = sum(c["units_explained"] for c in chosen)
    print(f"{len(chosen)} NON-OVERLAPPING templates")
    print(f"  {exp:,} of {text_units:,} slogan units  "
          f"({100*exp/text_units:.1f}% of slogan sales)")
    print(f"  {exp:,} of {total_units:,} total units  "
          f"({100*exp/total_units:.1f}% of all sales)\n")
    print("top 30, each counted once:")
    for c in chosen[:30]:
        print(f"  {c['units_explained']:>6,}u {c['designs']:>4}d "
              f"{c['distinct_fillers']:>4}f  {c['template'][:64]}")

    with open("MINED_TEMPLATES.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(chosen[0].keys()))
        w.writeheader(); w.writerows(chosen)
    print(f"\nwrote MINED_TEMPLATES.csv ({len(chosen)} rows)")


if __name__ == "__main__":
    main()
