#!/usr/bin/env python3
"""Rebuild the eBay file from the freshly joined parts, in one pass.

Titles follow the formula of the HOT SELLERS in the source catalogue - the
file the designs were replicated from, weighted by units actually sold - not
the seller's own GR- catalogue, which is the one being ended.

Measured on 156,687 units sold across 15,604 selling titles:

    T-Shirt 88.7%   Mens 89.2%   Funny 40.2%   Top 28.6%   Tee 14.9%
    Womens   2.2%   Unisex 3.3%  Novelty 0.0%  Gift  4.6%

So the shape is  {subject} T-Shirt Mens [Funny] [theme] Tee Top  and Womens,
Unisex and Novelty are deliberately absent. Hot titles average 60 characters,
so the builder does not pad to 80 for its own sake.

Also applied: quantity 1 per size, price 11.99, shipping policy 2, a
"This design" block in every description, and the drops the seller asked for.
"""
import csv, re, html, json, collections, os

csv.field_size_limit(20 << 20)
SRC  = "/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv"
TMP  = SRC + ".new"
LIMIT = 80

THEME = {"humour": "Funny", "football": "Football", "music": "Music",
         "birthday": "Birthday", "seasonal": "Christmas", "pets": "Pet",
         "biker": "Biker", "nerd": "Geek", "fishing2": "Fishing",
         "fishing": "Fishing", "family": "Family", "gym": "Gym",
         "patriotic": "Flag", "trades": "Work", "drinking": "Beer",
         "gaming": "Gaming", "veteran": "Veteran", "awareness": "Awareness",
         "farming": "Farming", "faith": "Faith", "rude": "Rude",
         "memorial": "Memorial"}
FUNNY_THEMES = {"humour", "rude"}
TAILS = ["Tee Top", "Tee", "Top", ""]        # "tee top" is the commonest ending

# garment and gift padding stripped from the head; the formula puts back only
# the words the hot sellers actually use
STOP = {"mens", "men", "men's", "mens'", "womens", "women", "women's", "unisex",
        "t-shirt", "tshirt", "t", "shirt", "shirts", "tee", "tees", "top", "tops",
        "novelty", "gift", "gifts", "present", "presents", "idea", "ideas",
        "joke", "jokes", "funny", "adult", "adults", "humour", "humor",
        "ladies", "boys", "girls", "clothing", "apparel", "gents", "cotton"}

STYLE = {"line_art": "Line art", "distressed": "Distressed vintage print",
         "typography_only": "Typography", "cartoon": "Cartoon illustration",
         "flat_vector": "Flat vector artwork", "photographic": "Photographic"}
LAYOUT = {"text_only": "wording only, no illustration",
          "text_above_image": "wording above the illustration",
          "image_only": "illustration only, no wording",
          "text_below_image": "wording below the illustration",
          "two_panel": "a two-panel layout"}
ANCHOR = "<p>Printed on a heavyweight black cotton t-shirt, chest centred.</p>"

def clean(words):
    out, seen = [], set()
    for w in words:
        k = re.sub(r"[^a-z0-9'-]", "", w.lower())
        if not k or k in STOP or k in seen:
            continue
        seen.add(k); out.append(w)
    return out

# Function words that read as litter at the end of a head, once the slogan has
# been chopped: "... Drifting Drift On The T-Shirt Mens".
FUNC = {"a", "an", "the", "of", "on", "in", "at", "to", "by", "for", "with",
        "and", "or", "but", "is", "are", "was", "be", "am", "it", "its", "this",
        "that", "my", "your", "our", "i", "you", "we", "me", "him", "her",
        "no", "not", "so", "up", "out", "as", "if", "all", "any", "than",
        "then", "there", "here", "just", "very", "too", "own", "do", "does",
        "did", "has", "have", "had", "will", "would", "can", "could"}

def tidy(head):
    """Drop function words dangling at either end of the head."""
    h = head[:]
    while h and re.sub(r"[^a-z0-9'-]", "", h[-1].lower()) in FUNC:
        h.pop()
    while h and re.sub(r"[^a-z0-9'-]", "", h[0].lower()) in FUNC:
        h.pop(0)
    return h

def assemble(head, mids, tail):
    parts = [" ".join(head), "T-Shirt", "Mens"] + mids + ([tail] if tail else [])
    return " ".join(p for p in parts if p)

def norm(t):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", t.lower()).split())

def design_block(s):
    style  = STYLE.get(s.get("style", ""), "Original artwork")
    layout = LAYOUT.get(s.get("layout", ""), "a centred layout")
    pal    = (s.get("palette", "") or "").replace("-", " ").strip()
    sent = f"{style}, {layout}"
    if pal:
        sent += f' in a <b>{html.escape(pal)}</b> colourway'
    illus = (s.get("illustration", "") or "").strip()
    extra = f" Illustration: {html.escape(illus)}." if illus else ""
    return ("<h3>This design</h3><p>" + sent + "." + extra +
            " Printed for this listing only &mdash; each of our designs is drawn "
            "separately, so the artwork, wording and colours differ from listing "
            "to listing.</p>")

# ---- source ----------------------------------------------------------------
src = {}
for r in csv.DictReader(open("v7.csv", newline="", encoding="utf-8")):
    if r["slogan"]:
        src[f"WLT-{int(r['source_idx']):06d}"] = r

old = []
with open(SRC, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if not (row.get("Relationship") or "").strip():
            old.append((row["CustomLabel"].strip(), row["*Title"].strip()))
print(f"listings {len(old):,}", flush=True)

# the 545 pairs that differed only by "T-Shirt" vs "T Shirt": drop one each
g = collections.defaultdict(list)
for s, t in old: g[norm(t)].append(s)
dupe_drop = {s for v in g.values() if len(v) > 1 for s in sorted(v)[1:]}
print(f"old near-duplicate copies to drop: {len(dupe_drop):,}", flush=True)

# ---- titles ----------------------------------------------------------------
seen, titles, unplaceable = set(), {}, []
for sku, oldt in old:
    if sku in dupe_drop:
        continue
    s = src.get(sku) or {}
    th = s.get("theme", "")
    # Funny where the theme is humour or rude (hot sellers: 40.2% of units),
    # otherwise the theme's own search word.
    mids_pref = ["Funny"] if th in FUNNY_THEMES else []
    tw = THEME.get(th)
    if tw and tw not in mids_pref:
        mids_pref.append(tw)
    pool = clean(oldt.split()
                 + s.get("slogan", "").title().split()
                 + s.get("subject", "").title().split())
    if not pool:
        unplaceable.append(sku); continue
    placed = False
    for mids in (mids_pref, mids_pref[:1], []):
        for tail in TAILS:
            n = len(pool)
            while n > 0 and len(assemble(pool[:n], mids, tail)) > LIMIT:
                n -= 1
            for k in range(n, 0, -1):
                head = tidy(pool[:k])
                if not head:
                    continue
                t = assemble(head, mids, tail)
                if len(t) <= LIMIT and norm(t) not in seen:
                    seen.add(norm(t)); titles[sku] = t; placed = True; break
            if placed: break
        if placed: break
    if not placed:
        unplaceable.append(sku)

print(f"titles built {len(titles):,} | unplaceable {len(unplaceable):,}", flush=True)
DROP = dupe_drop | set(unplaceable)

# ---- write -----------------------------------------------------------------
kept = dropped_rows = 0
cur_dropped = False
H2 = re.compile(r"(<h2[^>]*>)(.*?)(</h2>)", re.S)
with open(SRC, newline="", encoding="utf-8") as f, \
     open(TMP, "w", newline="", encoding="utf-8") as o:
    r = csv.reader(f); w = csv.writer(o, lineterminator="\r\n")
    hdr = next(r); w.writerow(hdr)
    IREL = hdr.index("Relationship")
    I_QTY = hdr.index("*Quantity"); I_PRICE = hdr.index("*StartPrice")
    I_SHIP = hdr.index("ShippingProfileName")
    for row in r:
        if (row[IREL] or "").strip() == "Variation":
            if cur_dropped:
                dropped_rows += 1; continue
            row[I_QTY] = "1"; row[I_PRICE] = "11.99"
            w.writerow(row); continue
        sku = row[1].strip()
        if sku in DROP:
            cur_dropped = True; dropped_rows += 1; continue
        cur_dropped = False
        row[3] = titles[sku]
        row[I_SHIP] = "2"
        s = src.get(sku)
        d = row[4]
        d = H2.sub(lambda m: m.group(1) + html.escape(row[3], quote=True) + m.group(3), d, count=1)
        if s and ANCHOR in d:
            d = d.replace(ANCHOR, ANCHOR + design_block(s), 1)
        row[4] = d
        kept += 1
        w.writerow(row)
os.replace(TMP, SRC)
print(f"\nkept {kept:,} listings | dropped {len(DROP):,} listings ({dropped_rows:,} rows)")
json.dump({"dropped": sorted(DROP)}, open("dropped_skus.json", "w"))
