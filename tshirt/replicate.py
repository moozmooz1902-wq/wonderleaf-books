"""Build a parallel listing for each existing design.

One row in, one row out: same niche, same search keywords, a reworded title
and a design brief that is close but deliberately not a copy.

Titles are rewritten by reordering the keyword blocks and swapping synonyms -
eBay titles are keyword lists, so the search coverage survives while the
string itself changes. Nothing is copied verbatim.
"""
import csv, json, random, re, sys
from collections import Counter

random.seed(11)
GARMENT_WORDS = re.compile(r"\b(t.?shirts?|tshirts?|tees?|tops?|hoodies?|vests?|aprons?|"
 r"sweat ?shirts?|jumpers?|ringer|v.?neck|petite|fotl|fruit of the loom|organic|"
 r"baseball|raglan|long.?sleeve|tank tops?)\b", re.I)
AUDIENCE = re.compile(r"\b(mens?|men's|womens?|ladies|unisex|adults?|kids?|childrens?|boys?|girls?)\b", re.I)
# Only strip words that carry no search value. Birthday/gift/funny/xmas are
# high-volume search terms - dropping them was destroying the whole point.
FILLER = re.compile(r"\b(100%?|cotton|size|sizes|top|tee|printed|quality|brand)\b", re.I)

SYN = {
 "funny":["humorous","comedy","joke","witty"],
 "mens":["men's","for men","gents"],
 "t-shirt":["tee","t shirt","shirt"],
 "gift":["present","gift idea"],
 "biker":["motorcyclist","rider"],
 "motorbike":["motorcycle","bike"],
 "motorcycle":["motorbike","bike"],
 "awesome":["legendary","top class","first class"],
 "vintage":["retro","classic","old school"],
 "birthday":["bday","birthday gift"],
 "dad":["father","daddy"],
 "grandad":["grandpa","grandfather"],
 "lover":["fan","enthusiast","addict"],
 "cool":["ace","brilliant"],
}


def keyword_core(title):
    """Strip garment/audience/filler to find the words that carry the niche."""
    t = GARMENT_WORDS.sub(" ", title)
    t = AUDIENCE.sub(" ", t)
    words = [w for w in re.findall(r"[A-Za-z0-9'&-]+", t) if len(w) > 1]
    words = [w for w in words if not FILLER.fullmatch(w)]
    seen = set(); out = []
    for w in words:                      # drop repeats, keep first occurrence
        if w.lower() in seen: continue
        seen.add(w.lower()); out.append(w)
    return out


def rewrite(title, rng):
    """Same keywords, different string."""
    core = keyword_core(title)
    if len(core) < 2:
        return None
    # swap a couple of words for synonyms
    out = []
    for w in core:
        lw = w.lower()
        if lw in SYN and rng.random() < 0.18:
            out.append(rng.choice(SYN[lw]).title() if w[0].isupper() else rng.choice(SYN[lw]))
        else:
            out.append(w)
    # rebuild: subject block, then garment, then audience, then keyword tail
    head = out[:max(3, len(out)//2)]
    tail = out[max(3, len(out)//2):]
    garment = rng.choice(["T-Shirt", "Tee", "T Shirt"])
    aud = rng.choice(["Mens", "Men's", "Unisex"])
    extra = rng.choice(["Funny", "Novelty", "Gift", ""])
    def build(with_extra=True):
        parts = [" ".join(head), garment, aud, extra if with_extra else "", " ".join(tail)]
        return re.sub(r"\s{2,}", " ", " ".join(p for p in parts if p)).strip()
    new = build()
    if len(new) > 80: new = build(False)          # drop the optional word first
    if len(new) > 80: new = new[:80].rsplit(" ", 1)[0]
    return new


def brief(cv, title):
    """Design brief: same concept, different execution, built to the house spec."""
    subject = " ".join(keyword_core(title)[:6])
    inks = cv.get("ink_colours") or 4
    inks = min(max(inks, 4), 5)          # house spec, whatever the original used
    layout = cv.get("placement", "centre_chest")
    return (f"Same subject and audience as the original: {subject}. "
            f"NOT a copy - change the composition, the pose or angle, and the palette. "
            f"House spec: BLACK garment, {inks} flat spot colours, artwork covering "
            f"10-25% of the chest ({layout}), bold flat vector, thick linework, strong "
            f"silhouette. One condensed grotesk for any text.")


def main(limit=None):
    rows = json.load(open("all.json"))
    cv = {}
    try:
        for line in open("cv_features.jsonl"):
            r = json.loads(line); cv[r["idx"]] = r
    except FileNotFoundError:
        pass
    rng = random.Random(11)
    out = []; skipped = 0; seen = set()
    for i, r in enumerate(rows):
        if limit and len(out) >= limit: break
        new = rewrite(r["title"], rng)
        if not new or new.lower() == r["title"].lower() or new.lower() in seen:
            skipped += 1; continue
        seen.add(new.lower())
        f = cv.get(i, {})
        out.append([i, r["title"], new, r["sold"], f.get("garment", "?"),
                    f.get("ink_colours", ""), brief(f, r["title"]),
                    f.get("hash", "")])
    with open("REPLICA_CATALOGUE.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(("source_idx", "original_title", "new_title", "original_sold",
                    "original_garment", "original_inks", "design_brief", "image_hash"))
        w.writerows(out)
    print(f"source listings     : {len(rows):,}")
    print(f"replicas generated  : {len(out):,}  ({100*len(out)/len(rows):.1f}%)")
    print(f"skipped             : {skipped:,}  (too few keywords, or collided)")


main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
