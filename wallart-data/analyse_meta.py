#!/usr/bin/env python3
"""Turn the per-image records into the things we actually need to decide.

Six outputs:
 1. how the labels check out against titles that state their own technique
    (an accuracy number, so nothing downstream is trusted blindly)
 2. what techniques, grammars and colour strategies each competitor uses
 3. the real colour of the catalogue - palettes and hue, measured not described
 4. subject x technique lift: which pairing is over-represented
 5. the gap table: cells with volume in the market but little supply
 6. what the two catalogues do differently

  python3 analyse_meta.py <dir with meta_*.jsonl.gz>
"""
import collections, glob, gzip, json, math, os, sys

D = sys.argv[1]
rows = []
for p in sorted(glob.glob(os.path.join(D, "meta_*.jsonl.gz"))) or \
         sorted(glob.glob(os.path.join(D, "meta_*.jsonl"))):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
print(f"{len(rows):,} image records from {D}\n")
if not rows:
    sys.exit(0)

bysrc = collections.Counter(r.get("s", "?") for r in rows)
print("by source:", dict(bysrc), "\n")

# ---- 1. do the labels agree with titles that name their own technique? -----
STATED = {"linocut": "linocut", "watercolour": "watercolour", "watercolor": "watercolour",
          "collage": "paper_collage", "pencil": "pencil_graphite",
          "photograph": "photograph", "photography": "photograph",
          "risograph": "risograph", "pastel": "crayon_pastel",
          "impasto": "oil_impasto", "line art": "line_art"}
hit = collections.Counter(); tot = collections.Counter()
for r in rows:
    t = (r.get("t") or "").lower()
    if not t:
        continue
    for word, want in STATED.items():
        if word in t:
            tot[want] += 1
            if r.get("tech") == want:
                hit[want] += 1
            break
if tot:
    print("LABEL CHECK - titles that name their own technique vs what CLIP said")
    gt = gh = 0
    for k in sorted(tot, key=lambda x: -tot[x]):
        gt += tot[k]; gh += hit[k]
        print(f"  {k:<16} {hit[k]:>6,}/{tot[k]:>6,}  {hit[k]/tot[k]*100:5.1f}%")
    print(f"  {'OVERALL':<16} {gh:>6,}/{gt:>6,}  {gh/gt*100:5.1f}%\n")

# ---- 2. label distributions, per source --------------------------------
def dist(axis, topn=14):
    print(f"{axis.upper()}")
    for s in bysrc:
        c = collections.Counter(r.get(axis) for r in rows if r.get("s") == s)
        n = sum(c.values()) or 1
        print(f"  {s}: " + "  ".join(f"{k}={v/n*100:.1f}%" for k, v in c.most_common(topn)))
    print()

for ax in ("tech", "gram", "colo", "subj", "text", "grou", "regi"):
    dist(ax)

# ---- 3. measured colour -------------------------------------------------
print("MEASURED COLOUR (means per source)")
for s in bysrc:
    rs = [r for r in rows if r.get("s") == s]
    def m(k):
        v = [r[k] for r in rs if k in r]
        return sum(v) / len(v) if v else 0
    print(f"  {s}: lum={m('lum'):.3f} sat={m('sat'):.3f} colourful={m('colourful'):.3f} "
          f"edge={m('edge'):.4f} border_lum={m('border_lum'):.3f} centre_lum={m('centre_lum'):.3f}")
print()
HUE = ["red", "orange", "yellow", "yellow-green", "green", "spring",
       "cyan", "azure", "blue", "violet", "magenta", "rose"]
print("HUE SHARE across colourful pixels")
for s in bysrc:
    rs = [r for r in rows if r.get("s") == s and r.get("hue12")]
    if not rs: continue
    agg = [0.0] * 12
    for r in rs:
        for i, v in enumerate(r["hue12"]):
            agg[i] += v
    tot12 = sum(agg) or 1
    print(f"  {s}: " + "  ".join(f"{HUE[i]}={agg[i]/tot12*100:.1f}%" for i in range(12)))
print()

# ---- 4. subject x technique lift ---------------------------------------
print("SUBJECT x TECHNIQUE - top lifts (observed / expected), min 150 pairs")
N = len(rows)
cs = collections.Counter(r.get("subj") for r in rows)
ct = collections.Counter(r.get("tech") for r in rows)
cp = collections.Counter((r.get("subj"), r.get("tech")) for r in rows)
lifts = []
for (s_, t_), n in cp.items():
    if n < 150 or not s_ or not t_:
        continue
    exp = cs[s_] * ct[t_] / N
    if exp > 0:
        lifts.append((n / exp, n, s_, t_))
for lift, n, s_, t_ in sorted(lifts, reverse=True)[:30]:
    print(f"  x{lift:5.1f}  {n:>7,}  {s_:<22} {t_}")
print()

# ---- 5. the gap: big subjects with thin technique coverage -------------
print("GAP TABLE - subjects by volume, with how concentrated their technique is")
for s_, n in cs.most_common(24):
    if not s_: continue
    tc = collections.Counter(r.get("tech") for r in rows if r.get("subj") == s_)
    top, topn = tc.most_common(1)[0]
    share = topn / n
    print(f"  {s_:<22} {n:>8,}  top technique {top:<22} {share*100:5.1f}%"
          + ("   <- concentrated, room to differentiate" if share > 0.45 else ""))
