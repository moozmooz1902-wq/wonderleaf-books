"""Build eBay titles around the keywords that measurably carry sales.

Measured across all 167,695 of the seller's listings, units per listing
against the 1.30 catalogue average, with the share of units coming from
each word's top 3 listings checked so a couple of blockbusters cannot
masquerade as a keyword effect:

  KEEP                          DROP
  funny   35,074 listings 2.12x   cotton  68,723 listings 0.40x
  tee      8,768          2.70x   womens  17,810          0.18x
  top     21,209          2.51x   ringer  12,752          0.05x
  mens   114,876          1.29x   fotl     8,651          0.04x
  retro    1,702          6.52x   organic  8,662          0.05x
  dad      2,305          1.61x   petite   8,559          0.06x

Not used, and why: racer 18.10x, cafe 17.57x and chopper 15.22x look
enormous but 56-78% of their units come from three listings each - that is
the biker niche selling, not the word. novelty 3.13x is 88% one listing.
gift 15.24x and unisex 36.50x are real but sit on 597 and 144 listings, so
they are kept for search coverage rather than claimed as a lift.

birthday 0.81x, christmas 0.57x and vintage 0.83x all sit BELOW the
catalogue average on large samples, so they go in only when the design is
actually about that occasion, never as filler.
"""
import re

LIMIT = 80          # eBay's title limit

GARMENT = re.compile(r"\b(t.?shirts?|tshirts?|tees?|tops?|hoodies?|vests?|aprons?|"
    r"sweat ?shirts?|jumpers?|ringer|v.?neck|petite|fotl|fruit of the loom|organic|"
    r"baseball|raglan|long.?sleeve|tank tops?)\b", re.I)
AUDIENCE = re.compile(r"\b(mens?|men's|womens?|ladies|unisex|adults?|kids?|"
    r"childrens?|boys?|girls?)\b", re.I)
# measured dead weight - these cost characters and return nothing
DEAD = re.compile(r"(\b\d{1,3}\s*%|\b(100|cotton|size|sizes|printed|quality|brand|"
    r"ringer|fotl|fruit|loom|organic|petite|charcoal|qualified|neck|sleeve|"
    r"unisex|adult|adults)\b)", re.I)


def subject_words(title):
    """What the listing is actually about, minus garment and dead weight."""
    t = DEAD.sub(" ", AUDIENCE.sub(" ", GARMENT.sub(" ", title)))
    out, seen = [], set()
    for w in re.findall(r"[A-Za-z0-9'&-]{2,}", t):
        if w.lower() in seen: continue
        seen.add(w.lower()); out.append(w)
    return out


def niche_words(row):
    """The niche, if the subject words missed it. Template boilerplate is NOT
    a search term - nobody types "warning may spontaneously start", and it
    was eating 30 characters that the subject needs."""
    n = (row.get("niche") or "").strip()
    return [w.title() for w in n.split()] if n else []


def build(row, rng):
    """Assemble to 80 chars, most valuable keywords first."""
    subj = subject_words(row["original_title"])
    typ  = (row.get("niche_type") or "").upper()
    occasion = ["Birthday"] if typ in ("AGE", "YEAR") else []

    # order matters: everything after the cut is what gets dropped at 80 chars
    blocks = [
        subj[:6],                     # the niche - without this nothing is found
        ["T-Shirt"],                  # the product
        ["Mens"],                     # 1.29x, and this store is a mens store
        ["Funny"],                    # 2.12x on 35,074 listings - the big one
        occasion,                     # only when the design really is one
        niche_words(row),             # in case the subject words missed it
        ["Gift"],
        subj[6:11],                   # more of the subject, not slogan filler
        [rng.choice(["Tee", "Top"])],   # 2.70x / 2.51x as a tail keyword
    ]
    out, seen = [], set()
    for b in blocks:
        for w in b:
            k = w.lower()
            if k in seen: continue
            cand = " ".join(out + [w])
            if len(cand) > LIMIT: continue
            seen.add(k); out.append(w)
    return " ".join(out)
