#!/usr/bin/env python3
"""
Turn harvested museum records into a listable catalogue.

    python3 build_art_catalogue.py --raw met_raw.jsonl --out art_catalogue.json

The harvest is indiscriminate - it returns andirons, sherds and snuffboxes
alongside the Van Goghs, because the only way to tell is to read the record.
This filters to things somebody would hang on a wall, scores what is likely
to sell, and writes the keyword-stacked title.

TITLES follow the grammar the research found working, with one change. This
is what canvasartshop sells:

    HOKUSAI, THE GREAT WAVE OFF KANAGAWA -FRAMED ART POSTER PAINTING PRINT 4 SIZES

We print unframed A4 on paper, so Framed, Canvas and Ready to Hang are
claims we cannot make - see CLAUDE.md. Everything else about the shape is
kept: artist first because that is what people search, then the work, then
a stack of the words a buyer might type.
"""

import argparse
import collections
import html
import json
import re
from pathlib import Path

# --------------------------------------------------------------------------
# what belongs on a wall
# --------------------------------------------------------------------------
# Matched against classification and objectName. The Met's classification is
# often blank, so objectName has to carry it.
WALL = re.compile(
    r"paint|print|drawing|watercolo|woodblock|woodcut|etching|engraving|"
    r"lithograph|poster|map|photograph|album|screen|scroll|fresco|"
    r"illustration|plate|panel|miniature|pastel|charcoal|sketch",
    re.I)

# Things that match WALL by accident, or that simply do not sell as a print.
# This list earned every entry: a first pass matched "paint" and "print"
# inside the MEDIUM field and cheerfully offered painted chests of drawers
# and transfer-printed dinner plates as wall art.
NOT_WALL = re.compile(
    r"andiron|vase|coin|medal|sword|armor|armour|helmet|dagger|rifle|"
    r"pistol|furniture|chair|table|cabinet|desk|chest|drawer|bureau|"
    r"snuffbox|teapot|bowl|dish|plate\b|platter|saucer|tureen|"
    r"cup\b|mug\b|jug|jar\b|bottle|flask|decanter|goblet|tankard|"
    r"figurine|statuette|sculpture|bust\b|relief|plaque|medallion|"
    r"textile|dress|coat|shoe|hat\b|fan\b|glove|apron|"
    r"jewel|ring\b|necklace|bracelet|brooch|pendant|earring|"
    r"watch|clock|instrument|violin|piano|flute|drum|"
    r"fragment|sherd|shard|tile\b|brick|pot\b|pottery|porcelain|"
    r"button|buckle|spoon|fork|knife|candlestick|lamp|mirror|"
    r"box\b|case\b|binding|sampler|quilt|carpet|rug\b|coverlet|"
    r"certificate|indenture|bookplate|trade card|invitation|"
    r"stove|kettle|basket|tray|screen\b|stand\b|frame\b",
    re.I)

# Artists a British print buyer searches for by name. Presence here is a
# strong score, because the demand already exists - the whole reason this
# catalogue beats anything we could generate.
FAMOUS = {
    "vincent van gogh": 100, "claude monet": 95, "katsushika hokusai": 95,
    "utagawa hiroshige": 85, "gustav klimt": 90, "rembrandt": 85,
    "johannes vermeer": 90, "pierre-auguste renoir": 80, "edgar degas": 80,
    "paul cezanne": 75, "paul gauguin": 75, "edouard manet": 75,
    "j. m. w. turner": 85, "joseph mallord william turner": 85,
    "john constable": 75, "thomas gainsborough": 70, "william blake": 70,
    "john william waterhouse": 85, "john everett millais": 75,
    "dante gabriel rossetti": 70, "edward burne-jones": 70,
    "william morris": 80, "alphonse mucha": 80, "henri de toulouse-lautrec": 80,
    "edvard munch": 80, "gustave dore": 70, "caspar david friedrich": 75,
    "hieronymus bosch": 80, "pieter bruegel the elder": 80,
    "sandro botticelli": 80, "leonardo da vinci": 85, "michelangelo": 80,
    "raphael": 75, "caravaggio": 80, "francisco goya": 80,
    "diego velazquez": 75, "el greco": 70, "peter paul rubens": 70,
    "albrecht durer": 80, "john singer sargent": 75, "winslow homer": 70,
    "mary cassatt": 70, "james mcneill whistler": 70, "camille pissarro": 70,
    "georges seurat": 75, "henri rousseau": 70, "amedeo modigliani": 75,
    "egon schiele": 75, "wassily kandinsky": 70, "piet mondrian": 70,
    "kitagawa utamaro": 70, "utagawa kuniyoshi": 75, "ando hiroshige": 85,
    "maria sibylla merian": 70, "pierre-joseph redoute": 75,
    "john james audubon": 85, "ernst haeckel": 80,
}

# Subject tags a print buyer actually shops for, and what each is worth.
GOOD_TAGS = {
    "Flowers": 30, "Birds": 30, "Landscapes": 30, "Cats": 25, "Dogs": 25,
    "Trees": 20, "Gardens": 20, "Horses": 20, "Ships": 20, "Boats": 18,
    "Mountains": 20, "Rivers": 18, "Seascapes": 25, "Butterflies": 25,
    "Fruit": 18, "Women": 12, "Men": 6, "Children": 10, "Portraits": 15,
    "Sunsets": 20, "Moon": 20, "Stars": 18, "Snow": 15, "Autumn": 15,
    "Fish": 15, "Insects": 12, "Shells": 15, "Maps": 25, "Castles": 20,
    "Bridges": 15, "Cities": 15, "Windmills": 15, "Waterfalls": 18,
    "Lions": 20, "Tigers": 20, "Elephants": 18, "Owls": 22, "Deer": 20,
    "Rabbits": 18, "Foxes": 20, "Bears": 15, "Wolves": 20, "Whales": 18,
}

# Words that make a title unsellable however good the picture is.
BAD_TITLE = re.compile(
    r"^untitled|^\[|fragment|sherd|study for|verso|recto|"
    r"^plate \d+$|^page \d+|^no\. ?\d+$|unidentified|album leaf",
    re.I)

# Title tail candidates, best keyword first. Nothing here claims a frame,
# a canvas or ready to hang - see CLAUDE.md, we sell unframed A4 paper.
TAIL = ["Art Print", "Poster", "Wall Art", "Fine Art", "Home Decor",
        "Picture", "Gift", "A4", "A3", "Unframed"]

MAX_TITLE = 80


def surname(name):
    """'Vincent van Gogh' -> 'Van Gogh'. What a buyer types."""
    if not name:
        return ""
    name = re.sub(r"\s*\(.*?\)", "", name).strip()
    parts = name.split()
    if len(parts) < 2:
        return name
    # Keep the nobiliary particle: people search "Van Gogh", not "Gogh".
    for i, p in enumerate(parts):
        if p.lower() in ("van", "de", "der", "del", "di", "da", "le", "la"):
            return " ".join(parts[i:]).title()
    return parts[-1]


def clean_title(t):
    t = re.sub(r"\s*\(.*?\)\s*$", "", t or "").strip()
    t = re.sub(r"\s+", " ", t)
    return t.strip(" ,;:-")


def tag_list(rec):
    out = []
    for t in rec.get("tags") or []:
        term = t.get("term") if isinstance(t, dict) else t
        if term:
            out.append(term)
    return out


def wall_suitable(rec):
    """
    Is this a picture, or a thing with a picture on it?

    MEDIUM is deliberately not searched for the positive match. "Painted
    pine" and "transfer-printed earthenware" both contain the words, and
    matching them let a chest of drawers and a dinner plate through as
    bestselling wall art.
    """
    name = str(rec.get("objectName") or "")
    cls = str(rec.get("classification") or "")
    if NOT_WALL.search(name) or NOT_WALL.search(cls):
        return False
    return bool(WALL.search(name) or WALL.search(cls))


def score(rec, tags):
    s = 0
    artist = (rec.get("artistDisplayName") or "").lower()
    for name, pts in FAMOUS.items():
        if name in artist:
            s += pts
            break
    for t in tags:
        s += GOOD_TAGS.get(t, 0)
    cls = (rec.get("classification") or "") + (rec.get("objectName") or "")
    if re.search(r"paint", cls, re.I):
        s += 25
    elif re.search(r"woodblock|woodcut", cls, re.I):
        s += 20
    elif re.search(r"drawing|watercolo", cls, re.I):
        s += 10
    if rec.get("artistDisplayName"):
        s += 5
    # A dated work reads as a real piece rather than an anonymous fragment.
    if (rec.get("objectBeginDate") or 0) > 1400:
        s += 5
    return s


def build_title(rec, tags):
    """
    Artist first, then the work, then a stack of buyer words.

    The tee catalogue put the same 46-character tail on all 50,740 listings,
    which is 46 characters of nothing. Here the middle of the title is made
    of THIS picture's own subject words, and only the generic tail fills
    whatever is left.
    """
    art = surname(rec.get("artistDisplayName"))
    work = clean_title(rec.get("title"))
    head = f"{art} {work}" if art else work
    head = head[:52].strip(" ,-")

    parts = [head]
    used = len(head)
    # This picture's own subject words first - they are the ones a buyer
    # searching for a subject rather than an artist will type.
    for t in tags[:3]:
        if t in GOOD_TAGS and used + len(t) + 1 <= MAX_TITLE - 22:
            parts.append(t)
            used += len(t) + 1
    for word in TAIL:
        if used + len(word) + 1 <= MAX_TITLE:
            parts.append(word)
            used += len(word) + 1
    return " ".join(parts)[:MAX_TITLE].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-score", type=int, default=25)
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    kept, seen_titles = [], set()
    counts = collections.Counter()
    for line in open(a.raw, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        counts["read"] += 1
        if not rec.get("primaryImage"):
            counts["no image"] += 1
            continue
        if not wall_suitable(rec):
            counts["not wall art"] += 1
            continue
        work = clean_title(rec.get("title"))
        if not work or BAD_TITLE.search(work):
            counts["unusable title"] += 1
            continue
        tags = tag_list(rec)
        s = score(rec, tags)
        if s < a.min_score:
            counts["scored too low"] += 1
            continue
        title = build_title(rec, tags)
        key = title.lower()
        if key in seen_titles:
            counts["duplicate title"] += 1
            continue
        seen_titles.add(key)
        kept.append({
            "design_id": f"met{rec['objectID']}",
            "title": title,
            "stem": work,
            "artist": rec.get("artistDisplayName") or "",
            "date": rec.get("objectDate") or "",
            "medium": rec.get("medium") or "",
            "department": rec.get("department") or "",
            "tags": tags[:6],
            "score": s,
            "image": rec["primaryImage"],
            "image_small": rec.get("primaryImageSmall") or "",
            "source": "Metropolitan Museum of Art, CC0",
        })

    kept.sort(key=lambda d: -d["score"])
    Path(a.out).write_text(json.dumps(kept, indent=1))

    print(f"  {counts['read']:,} records read")
    for k in ("no image", "not wall art", "unusable title",
              "scored too low", "duplicate title"):
        if counts[k]:
            print(f"    dropped {counts[k]:>7,}  {k}")
    print(f"  {len(kept):,} listable -> {a.out}")
    if kept and a.stats:
        print("\n  best scoring:")
        for d in kept[:12]:
            print(f"    {d['score']:>4}  {d['title']}")
        print("\n  a slice from the middle:")
        for d in kept[len(kept) // 2:len(kept) // 2 + 6]:
            print(f"    {d['score']:>4}  {d['title']}")
        over = [d for d in kept if len(d["title"]) > MAX_TITLE]
        print(f"\n  titles over {MAX_TITLE} characters: {len(over)}")
        print(f"  median title length: "
              f"{sorted(len(d['title']) for d in kept)[len(kept)//2]}")


if __name__ == "__main__":
    main()
