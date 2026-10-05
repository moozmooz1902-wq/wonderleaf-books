#!/usr/bin/env python3
"""Rebuild the catalogue so no design repeats.

v5 picked one template per listing by weighted random choice. With 4,441
motorbike listings all drawing from the same distribution, the heaviest
template won most of the time and one slogan ended up on 2,332 shirts -
91.7% of the catalogue was repeats, worse than the 89% the wall-art branch
blames for 424k listings not selling.

Here the subject is a 2-3 word phrase from the title rather than one
collapsed category word, and for the Nth listing sharing a subject the
template and look are chosen by ROTATION, not by chance. So the first
motorbike listing gets template 0 look A, the second template 1 look A, and
so on through every combination before anything repeats.

A subject can only support (compatible templates x 4 looks) distinct
designs. Listings beyond that are dropped rather than duplicated - a
smaller honest catalogue beats a big repetitive one.
"""
import csv, hashlib, sys
from collections import Counter, defaultdict
import vetted, build_replicas_v3 as B

LOOKS = ["A", "B", "C", "D"]
import styles
PALETTES = list(range(len(styles.PALETTES)))   # 10 colourways per look


def subject_of(title, vocab_all, tw):
    """2-3 content words, so 'Cafe Racer Motorcycle' and 'Vintage Motorcycle
    Club' are different subjects instead of both collapsing to MOTORCYCLE."""
    ws = [w.upper() for w in B.keyword_core(title)]
    ws = [w for w in ws if len(w) > 2 and w not in B.BAD_NICHE
          and w not in B.STOPWORDS and w not in tw and w.isalpha()]
    if not ws:
        return None
    return " ".join(ws[:3]) if len(ws) >= 3 else " ".join(ws)


def head_noun(subject, vocab, tw):
    """The word the template slot actually gets filled with."""
    for w in subject.split():
        if any(w in vocab.get(t, ()) for t in vocab):
            return w
    return subject.split()[0]


def main():
    tw = B.template_words()
    vocab = B.harvest_vocab()
    vocab = {k: {v for v in s if not (set(v.split()) & tw)} for k, s in vocab.items()}
    by_type = defaultdict(list)
    for t, typ, u in vetted.TEMPLATES:
        by_type[typ].append(t)

    rows = list(csv.DictReader(open("REPLICA_V5.csv")))
    print(f"{len(rows):,} source rows")

    # how many listings share each subject
    subs = {}
    for r in rows:
        subs[r["source_idx"]] = subject_of(r["original_title"], None, tw)
    counts = Counter(s for s in subs.values() if s)
    print(f"{len(counts):,} distinct subjects")

    seen = Counter()
    out, dropped = [], 0
    used = set()
    for r in rows:
        s = subs[r["source_idx"]]
        if not s:
            dropped += 1; continue
        noun = head_noun(s, vocab, tw)
        typ = B.type_of(noun, vocab)
        pool = by_type.get(typ) or by_type["GENERIC"]
        # strict templates only take vocabulary observed in that slot
        observed = {v for st in vocab.values() for v in st}
        if noun not in observed:
            pool = [p for p in pool if p not in B.STRICT] or by_type["GENERIC"]
        # a slogan can carry many shirts as long as the DESIGN differs, so
        # the variant space is templates x looks x colourways, not just
        # templates x looks
        cap = len(pool) * len(LOOKS) * len(PALETTES)
        i = seen[s]
        if i >= cap:
            dropped += 1; continue
        seen[s] += 1
        tmpl = pool[i % len(pool)]
        look = LOOKS[(i // len(pool)) % len(LOOKS)]
        pal  = PALETTES[(i // (len(pool) * len(LOOKS))) % len(PALETTES)]
        slogan = B.agree(tmpl.replace("{N}", noun))
        key = (slogan, look, pal)
        if key in used:
            dropped += 1; continue
        used.add(key)
        r["slogan"] = slogan; r["look"] = look; r["palette"] = styles.PALETTES[pal][0]
        r["palette_idx"] = pal
        r["template_used"] = tmpl; r["niche"] = noun; r["niche_type"] = typ
        r["subject"] = s
        out.append(r)

    fields = list(rows[0].keys()) + ["subject", "palette", "palette_idx"]
    with open("REPLICA_V6.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in out: w.writerow({k: r.get(k, "") for k in fields})

    n = len(out)
    slog = Counter(r["slogan"] for r in out)
    combo = Counter((r["slogan"], r["look"], r["palette"]) for r in out)
    print(f"\nkept    {n:,}")
    print(f"dropped {dropped:,} (beyond what their subject can support without repeating)")
    print(f"\ndistinct slogans          {len(slog):,}   "
          f"{100*sum(v-1 for v in slog.values() if v>1)/n:.1f}% repeats")
    print(f"distinct designs          {len(combo):,}   "
          f"{100*sum(v-1 for v in combo.values() if v>1)/n:.1f}% repeats   (was 78.1%)")
    print(f"\nmost repeated slogan: {slog.most_common(1)[0][1]}x  (was 2,332x)")
    print("templates in use:", len(Counter(r["template_used"] for r in out)))


main()
