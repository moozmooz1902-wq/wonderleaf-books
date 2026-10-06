#!/usr/bin/env python3
"""Final catalogue: varied titles, shuffled so it does not read as a dump.

Two things the seller asked for that the earlier build got wrong:

1. Every title said "Funny" in the same position and the same shape. Funny
   measures at 2.12x the catalogue average so it stays on most listings, but
   it is also the single most spammed word in this category, so the modifier
   and the title SHAPE both rotate. Nine shapes x several modifiers means
   two listings in the same niche do not look like the same template.

2. The file was in source order, so thousands of motorbike listings sat
   together. eBay sellers get flagged for exactly that. Rows are now
   interleaved by subject so consecutive listings are from different niches.
"""
import csv, random, re
from collections import defaultdict
import titles

RNG = random.Random(20261006)

# measured: funny 2.12x, tee 2.70x, top 2.51x, mens 1.29x. The rest are
# shape variation, not claimed lifts - they stop every title looking alike.
MODIFIER = (["Funny"] * 6) + ["Novelty", "Humour", "Joke", "Sarcastic",
                              "Slogan", "Graphic", "Rude", "Cheeky"]
GARMENT  = ["T-Shirt", "Tee", "T Shirt", "Tshirt"]
AUDIENCE = ["Mens", "Men's", "Unisex", "Adults"]
TAIL     = ["Tee", "Top", "Gift", "Present", "Gift Idea", ""]


def dedupe_words(s):
    """The source title often already contains Funny or Tee, so the shapes
    doubled them: "Funny T-Shirt Mens Funny", "... Tee Tee". Keep the first
    occurrence of each word, drop later ones."""
    out, seen = [], set()
    for w in s.split():
        k = re.sub(r"[^a-z0-9]", "", w.lower())
        if k and k in seen:
            continue
        if k: seen.add(k)
        out.append(w)
    return " ".join(out)


def build_title(row, i):
    """Nine shapes, rotated by index so neighbours differ."""
    subj = titles.subject_words(row["original_title"])[:7]
    if len(subj) < 2:
        return None
    core = " ".join(subj[:5])
    extra = " ".join(subj[5:7])
    m = MODIFIER[i % len(MODIFIER)]
    g = GARMENT[(i // 3) % len(GARMENT)]
    a = AUDIENCE[(i // 5) % len(AUDIENCE)]
    t = TAIL[(i // 7) % len(TAIL)]
    shapes = [
        f"{core} {g} {a} {m} {extra} {t}",
        f"{m} {core} {g} {a} {extra} {t}",
        f"{core} {m} {g} {a} {extra} {t}",
        f"{core} {g} {m} {a} {t} {extra}",
        f"{m} {core} {a} {g} {t} {extra}",
        f"{core} {a} {g} {m} {extra} {t}",
        f"{core} {g} {a} {extra} {m} {t}",
        f"{m} {g} {core} {a} {extra} {t}",
        f"{core} {extra} {g} {a} {m} {t}",
    ]
    s = dedupe_words(re.sub(r"\s{2,}", " ", shapes[i % len(shapes)]).strip())
    if len(s) > 80:
        s = dedupe_words(re.sub(r"\s{2,}", " ",
                shapes[i % len(shapes)].replace(extra, "")).strip())
    if len(s) > 80:
        s = s[:80].rsplit(" ", 1)[0]
    return s


def interleave(rows):
    """Round-robin across subjects so no two neighbours share a niche."""
    buckets = defaultdict(list)
    for r in rows:
        buckets[r.get("subject") or r.get("niche") or "?"].append(r)
    for b in buckets.values():
        RNG.shuffle(b)
    order = list(buckets)
    RNG.shuffle(order)
    out, live = [], [buckets[k] for k in order]
    while live:
        nxt = []
        for b in live:
            out.append(b.pop())
            if b:
                nxt.append(b)
        RNG.shuffle(nxt)
        live = nxt
    return out


def main():
    rows = list(csv.DictReader(open("REPLICA_V6.csv")))
    print(f"{len(rows):,} distinct designs in")
    rows = interleave(rows)
    kept, seen = [], set()
    for i, r in enumerate(rows):
        t = build_title(r, i)
        if not t or t.lower() in seen:
            continue
        seen.add(t.lower())
        r["new_title"] = t
        kept.append(r)
    fields = list(rows[0].keys())
    with open("FINAL_V7.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in kept: w.writerow({k: r.get(k, "") for k in fields})

    from collections import Counter
    n = len(kept)
    print(f"{n:,} listings out ({len(rows)-n:,} dropped on duplicate titles)")
    print(f"distinct titles  {len(set(r['new_title'] for r in kept)):,}")
    fy = sum(1 for r in kept if "funny" in r["new_title"].lower())
    print(f"titles with Funny {fy:,} ({100*fy/n:.0f}%) - was 100%")
    print(f"max title length {max(len(r['new_title']) for r in kept)}")
    nb = sum(1 for a, b in zip(kept, kept[1:])
             if (a.get('subject') or '') == (b.get('subject') or ''))
    print(f"neighbouring rows sharing a subject: {nb} ({100*nb/n:.2f}%)")
    print("\nfirst 8 titles, to show the spread:")
    for r in kept[:8]: print("  ", r["new_title"])


main()
