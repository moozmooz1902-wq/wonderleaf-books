#!/usr/bin/env python3
"""Measured colour profile per technique, supervised by the seller's own labels.

Better than asking CLIP what technique a picture is: it agreed with the title
only 37.8% of the time. But Fy! *states* its technique in the title - 142.6% of
its titles carry a technique word - so the title is the label and the pixels
are the measurement. No model, no guessing.

Output per technique: the colour strategy mix, mean lightness/saturation/edge
density, the border-vs-centre lightness that distinguishes a margined print
from a full-bleed panel, and the dominant hues. That is directly usable as a
generation spec.
"""
import collections, glob, gzip, json, math, os, sys

D = sys.argv[1]
MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 60

TECH = ["watercolour", "watercolor", "linocut", "woodcut", "etching", "engraving",
        "lithograph", "screenprint", "risograph", "gouache", "acrylic", "oil",
        "pastel", "charcoal", "pencil", "graphite", "ink", "collage",
        "photograph", "photography", "illustration", "painting", "drawing",
        "sketch", "impasto", "silhouette", "line art", "vector", "digital"]
ALIAS = {"watercolor": "watercolour", "photography": "photograph",
         "graphite": "pencil"}

rows = []
for p in sorted(glob.glob(os.path.join(D, "*.jsonl.gz"))):
    try:
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    except (EOFError, OSError):
        pass
print(f"{len(rows):,} measured images")

def hue_entropy(h):
    return -sum(v * math.log(v, 2) for v in h if v > 0)

def strategy(r):
    h = r.get("hue12") or [0] * 12
    sat, cf = r.get("sat", 0), r.get("colourful", 0)
    if sat < 0.10 or cf < 0.06:
        return "monochrome"
    e = hue_entropy(h)
    order = sorted(range(12), key=lambda i: -h[i])
    a, b = order[0], order[1]
    top2, sep = h[a] + h[b], min((a - b) % 12, (b - a) % 12)
    if e >= 2.6:
        return "full_spectrum"
    if top2 >= 0.70 and sep >= 4:
        return "complementary"
    if top2 >= 0.80 and sep <= 2:
        return "duotone_analogous"
    if cf < 0.30 and sat < 0.30:
        return "neutral_accent"
    return "full_spectrum"

HUE = ["red", "orange", "yellow", "ylw-grn", "green", "spring",
       "cyan", "azure", "blue", "violet", "magenta", "rose"]

groups = collections.defaultdict(list)
for r in rows:
    t = (r.get("t") or "").lower()
    if not t:
        continue
    for w in TECH:
        if w in t:
            groups[ALIAS.get(w, w)].append(r)

print(f"\n{'technique':<14} {'n':>6}  {'lum':>5} {'sat':>5} {'edge':>6} "
      f"{'bord-cen':>8}  dominant strategy        top hues")
print("-" * 104)
out = {}
for k, rs in sorted(groups.items(), key=lambda x: -len(x[1])):
    if len(rs) < MIN:
        continue
    n = len(rs)
    def m(f):
        v = [x[f] for x in rs if f in x]
        return sum(v) / len(v) if v else 0
    st = collections.Counter(strategy(x) for x in rs)
    agg = [0.0] * 12
    for x in rs:
        for i, v in enumerate(x.get("hue12") or [0] * 12):
            agg[i] += v
    tot = sum(agg) or 1
    hues = sorted(range(12), key=lambda i: -agg[i])[:3]
    s1, c1 = st.most_common(1)[0]
    print(f"{k:<14} {n:>6,}  {m('lum'):.3f} {m('sat'):.3f} {m('edge'):.4f} "
          f"{m('border_lum')-m('centre_lum'):+8.3f}  {s1:<16}{c1/n*100:4.0f}%  "
          + " ".join(f"{HUE[i]}{agg[i]/tot*100:.0f}%" for i in hues))
    out[k] = {"n": n, "lum": round(m("lum"), 4), "sat": round(m("sat"), 4),
              "edge": round(m("edge"), 5),
              "border_minus_centre": round(m("border_lum") - m("centre_lum"), 4),
              "strategy": {a: round(b / n, 4) for a, b in st.most_common()},
              "hue": {HUE[i]: round(agg[i] / tot, 4) for i in range(12)}}
json.dump(out, open(os.path.join(D, "technique_profiles.json"), "w"), indent=1)
print(f"\n-> {os.path.join(D, 'technique_profiles.json')}")
