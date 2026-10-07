#!/usr/bin/env python3
"""One pass: build the whole eBay file from the freshly joined parts.

TITLE RULE - what is printed on the shirt leads, and nothing describes it.

    {slogan, in full} T-Shirt Mens [Funny|theme] [Tee] [Top]

The slogan is what render_illus.py draws, so it is the product, and a buyer
reads it off the title. No subject, illustration or palette words go in - they
describe the design rather than name it, they ate the 80 characters, and they
produced titles like "...Husband Looks Like T-Shirt Mens Raising Light Woman
Tee". Those words move to the description instead.

Everything else matches the seller's known-good upload: the variation set on
the parent's RelationshipDetails, S/M/L/XL/2XL, variations repeating category,
condition and title and carrying no SKU, Location Manchester, quantity 1,
price 11.99, postage policy 2.
"""
import csv, re, html, collections, os, json

csv.field_size_limit(20 << 20)
SRC  = "/home/user/wonderleaf-books/tshirt/EBAY_ONE_FILE.csv"
TMP  = SRC + ".new"
LIMIT = 80
SIZES, SETSTR = ["S", "M", "L", "XL", "2XL"], "Size=S;M;L;XL;2XL"
OLD2NEW = {"Small": "S", "Medium": "M", "Large": "L",
           "X-Large": "XL", "XX-Large": "2XL"}
LOCATION, PRICE, QTY, SHIP = "Manchester", "11.99", "1", "2"

THEME = {"humour": "Funny", "football": "Football", "music": "Music",
         "birthday": "Birthday", "seasonal": "Christmas", "pets": "Pet",
         "biker": "Biker", "nerd": "Geek", "fishing2": "Fishing",
         "fishing": "Fishing", "family": "Family", "gym": "Gym",
         "patriotic": "Flag", "trades": "Work", "drinking": "Beer",
         "gaming": "Gaming", "veteran": "Veteran", "awareness": "Awareness",
         "farming": "Farming", "faith": "Faith", "rude": "Rude",
         "memorial": "Memorial"}
FUNNY = {"humour", "rude"}
FUNC = {"a","an","the","of","on","in","at","to","by","for","with","and","or",
        "but","is","are","was","be","am","it","its","this","that","my","your",
        "our","i","you","we","me","no","not","so","up","out","as","if"}
STYLE = {"line_art": "Line art", "distressed": "Distressed vintage print",
         "typography_only": "Typography", "cartoon": "Cartoon illustration",
         "flat_vector": "Flat vector artwork", "photographic": "Photographic"}
LAYOUT = {"text_only": "wording only, no illustration",
          "text_above_image": "wording above the illustration",
          "image_only": "illustration only, no wording",
          "text_below_image": "wording below the illustration",
          "two_panel": "a two-panel layout"}
ANCHOR = "<p>Printed on a heavyweight black cotton t-shirt, chest centred.</p>"

def norm(t): return " ".join(re.sub(r"[^a-z0-9 ]", " ", t.lower()).split())
taken = set()

def wsp(s):  return [w for w in re.split(r"\s+", (s or "").strip()) if w]
def key(w):  return re.sub(r"[^a-z0-9]", "", w.lower())
def tc(s):   return [w.capitalize() for w in wsp(s)]

def make_title(slog, niche, mids, extra, taken):
    """Full slogan first, clean. Extra words are added ONLY to break a clash.

    A title that is already unique stays as the printed wording plus garment
    keywords and nothing else. Only where another listing already holds that
    exact title does a distinguishing noun get appended, and the fewest
    possible - so the clutter lands on the duplicates, not on everything.
    """
    def build(sl, nm, tail, ne=0):
        return " ".join(sl + ["T-Shirt", "Mens"] + extra[:ne] + mids[:nm]
                        + (tail.split() if tail else []))
    # pass 1: clean, no extras
    for nm in range(len(mids), -1, -1):
        for tail in ("Tee Top", "Tee", "Top", ""):
            t = build(slog, nm, tail)
            if len(t) <= LIMIT and norm(t) not in taken:
                return t
    # pass 2: add the fewest distinguishing nouns that make it unique
    for ne in range(1, len(extra) + 1):
        for nm in range(len(mids), -1, -1):
            for tail in ("Tee Top", "Tee", "Top", ""):
                t = build(slog, nm, tail, ne)
                if len(t) <= LIMIT and norm(t) not in taken:
                    return t
    # pass 3: whatever fits, unique or not
    for nm in range(len(mids), -1, -1):
        for tail in ("Tee Top", "Tee", "Top", ""):
            t = build(slog, nm, tail)
            if len(t) <= LIMIT:
                return t
    for n in range(len(slog) - 1, 0, -1):
        sl = slog[:n]
        while sl and key(sl[-1]) in FUNC:
            sl.pop()
        if not sl:
            continue
        if niche and key(niche) not in {key(x) for x in sl}:
            sl = sl + [niche.capitalize()]
        for nm in range(len(mids), -1, -1):
            for tail in ("Tee Top", "Tee", "Top", ""):
                t = build(sl, nm, tail)
                if len(t) <= LIMIT:
                    return t
    return None

def design_block(s, slogan):
    style  = STYLE.get(s.get("style", ""), "Original artwork")
    layout = LAYOUT.get(s.get("layout", ""), "a centred layout")
    pal    = (s.get("palette", "") or "").replace("-", " ").strip()
    out = ["<h3>This design</h3><p>Printed wording: <b>&ldquo;"
           + html.escape(slogan) + "&rdquo;</b>.</p><p>" + style + ", " + layout]
    if pal:
        out.append(f' in a <b>{html.escape(pal)}</b> colourway')
    out.append(".")
    illus = (s.get("illustration", "") or "").strip()
    if illus:
        out.append(" Illustration: " + html.escape(illus) + ".")
    # the describing keywords that used to clutter the title live here now
    kws, seen = [], set()
    for f in ("niche", "subject"):
        for w in wsp(s.get(f, "").replace("-", " ")):
            k = key(w)
            if k and len(k) > 2 and k not in seen and k not in FUNC:
                seen.add(k); kws.append(w.capitalize())
    if kws:
        out.append(" Theme: " + html.escape(", ".join(kws[:8])) + ".")
    out.append(" Printed for this listing only &mdash; each of our designs is "
               "drawn separately, so the artwork, wording and colours differ "
               "from listing to listing.</p>")
    return "".join(out)

src = {}
for r in csv.DictReader(open("v7.csv", newline="", encoding="utf-8")):
    if r["slogan"]:
        src[f"WLT-{int(r['source_idx']):06d}"] = r

hdr = open(SRC, newline="", encoding="utf-8").readline().rstrip("\r\n").split(",")
I = {n: i for i, n in enumerate(hdr)}
SPEC = [i for n, i in I.items() if n.startswith("C:") and n != "C:Size"]
H2 = re.compile(r"(<h2[^>]*>)(.*?)(</h2>)", re.S)

parents = variations = nosrc = notitle = 0
titles = {}
cur = None
with open(SRC, newline="", encoding="utf-8") as f, \
     open(TMP, "w", newline="", encoding="utf-8") as o:
    r = csv.reader(f); w = csv.writer(o, lineterminator="\r\n")
    next(r); w.writerow(hdr)
    skip = False
    for row in r:
        if (row[I["Relationship"]] or "").strip() == "Variation":
            if skip:
                continue
            new = OLD2NEW.get((row[I["C:Size"]] or "").strip(), row[I["C:Size"]])
            row[0] = ""; row[I["CustomLabel"]] = ""
            row[I["*Category"]] = cur[I["*Category"]]
            row[I["*Title"]] = cur[I["*Title"]]
            row[I["*ConditionID"]] = cur[I["*ConditionID"]]
            row[I["Relationship"]] = "Variation"
            row[I["RelationshipDetails"]] = f"Size={new}"
            row[I["C:Size"]] = new
            row[I["*Location"]] = ""
            row[I["*StartPrice"]] = PRICE
            row[I["*Quantity"]] = QTY
            for i in SPEC:
                row[i] = cur[i]
            variations += 1
            w.writerow(row); continue

        sku = row[I["CustomLabel"]].strip()
        s = src.get(sku)
        if s is None:
            skip = True; nosrc += 1; continue
        slogan = s["slogan"]
        th = s.get("theme", "")
        mids = ["Funny"] if th in FUNNY else []
        tw = THEME.get(th)
        if tw and tw not in mids:
            mids.append(tw)
        have = {key(x) for x in tc(slogan)}
        extra, eseen = [], set()
        for fld in ("niche", "subject", "illustration"):
            for ww in wsp(s.get(fld, "").replace("-", " ")):
                k = key(ww)
                if k and len(k) > 2 and k not in have and k not in eseen and k not in FUNC:
                    eseen.add(k); extra.append(ww.capitalize())
        t = make_title(tc(slogan), s.get("niche", ""), mids, extra, taken)
        if t:
            taken.add(norm(t))
        if not t:
            skip = True; notitle += 1; continue
        skip = False
        titles[sku] = t
        row[I["*Title"]] = t
        row[I["RelationshipDetails"]] = SETSTR
        row[I["C:Size"]] = ""
        row[I["*Location"]] = LOCATION
        row[I["ShippingProfileName"]] = SHIP
        d = H2.sub(lambda m: m.group(1) + html.escape(t, quote=True) + m.group(3),
                   row[I["*Description"]], count=1)
        if ANCHOR in d:
            d = d.replace(ANCHOR, ANCHOR + design_block(s, slogan), 1)
        row[I["*Description"]] = d
        cur = row
        parents += 1
        w.writerow(row)
os.replace(TMP, SRC)

ts = list(titles.values())
print(f"listings {parents:,} | variations {variations:,}")
print(f"no source row {nosrc} | no title buildable {notitle}")
print(f"distinct titles {len(set(ts)):,} | EXACT duplicates {len(ts)-len(set(ts)):,}")
print(f"normalised duplicates {len(ts)-len(set(norm(t) for t in ts)):,}")
L = [len(t) for t in ts]
print(f"length min {min(L)} mean {sum(L)/len(L):.1f} max {max(L)}")
full = sum(1 for sku, t in titles.items() if norm(t).startswith(norm(src[sku]['slogan'])))
print(f"opens with the COMPLETE printed slogan: {full:,} ({100*full/len(ts):.1f}%)")
json.dump(titles, open("final_titles.json", "w"))
