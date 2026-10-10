#!/usr/bin/env python3
"""Measured colour/composition profile for any group of titles matching a regex.

Used to get an exact generation target for the two products we intend to build,
rather than borrowing a generic technique profile.
"""
import collections, glob, gzip, json, math, os, re, sys

D = sys.argv[1]
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

GROUPS = {
 "ALL (baseline)": r".",
 "UK place":       r"\b(cornwall|devon|yorkshire|scotland|wales|snowdonia|cotswolds|"
                   r"whitby|lake district|cumbria|northumberland|pembrokeshire|"
                   r"brecon|dorset|norfolk|suffolk|sussex|kent|somerset|london|"
                   r"edinburgh|glasgow|manchester|liverpool|brighton|bath|york)\b",
 "travel poster":  r"travel poster|vintage travel|affiche",
 "charcoal/sketch":r"\b(charcoal|sketch|graphite|pencil drawing)\b",
 "linocut":        r"\blinocut\b",
 "botanical":      r"\b(botanical|flower|floral|leaf|leaves|fern|herbarium)\b",
 "dog/cat breed":  r"\b(terrier|retriever|spaniel|collie|dachshund|poodle|bulldog|"
                   r"labrador|shepherd|breed|siamese|persian cat)\b",
}
HUE = ["red","orange","yellow","ylw-grn","green","spring","cyan","azure","blue","violet","magenta","rose"]

def hue_entropy(h):
    return -sum(v*math.log(v,2) for v in h if v>0)

def strategy(r):
    h = r.get("hue12") or [0]*12
    sat, cf = r.get("sat",0), r.get("colourful",0)
    if sat < 0.10 or cf < 0.06: return "monochrome"
    e = hue_entropy(h)
    o = sorted(range(12), key=lambda i: -h[i]); a,b = o[0],o[1]
    top2, sep = h[a]+h[b], min((a-b)%12,(b-a)%12)
    if e >= 2.6: return "full_spectrum"
    if top2 >= 0.70 and sep >= 4: return "complementary"
    if top2 >= 0.80 and sep <= 2: return "duotone_analogous"
    if cf < 0.30 and sat < 0.30: return "neutral_accent"
    return "full_spectrum"

print(f"{len(rows):,} measured images\n")
print(f"{'group':<17} {'n':>6}  {'lum':>5} {'sat':>5} {'edge':>6} {'b-c':>7} "
      f"{'mono%':>6}  strategy mix")
print("-"*108)
for name, pat in GROUPS.items():
    rx = re.compile(pat, re.I)
    rs = [r for r in rows if rx.search(r.get("t") or "")] if pat != r"." else rows
    if len(rs) < 25:
        print(f"{name:<17} {len(rs):>6}  (too few)"); continue
    def m(f):
        v=[x[f] for x in rs if f in x]; return sum(v)/len(v) if v else 0
    st = collections.Counter(strategy(x) for x in rs)
    n = len(rs)
    agg=[0.0]*12
    for x in rs:
        for i,v in enumerate(x.get("hue12") or [0]*12): agg[i]+=v
    tot=sum(agg) or 1
    hues=sorted(range(12), key=lambda i:-agg[i])[:3]
    mix = " ".join(f"{k.split('_')[0]}{v/n*100:.0f}%" for k,v in st.most_common(3))
    print(f"{name:<17} {n:>6,}  {m('lum'):.3f} {m('sat'):.3f} {m('edge'):.4f} "
          f"{m('border_lum')-m('centre_lum'):+7.3f} {st['monochrome']/n*100:5.1f}%  {mix}"
          f"   | " + " ".join(f"{HUE[i]}{agg[i]/tot*100:.0f}%" for i in hues))
