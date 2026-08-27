#!/usr/bin/env python3
"""
Rewrite wall art titles for buyer search, and emit an eBay Revise file.

WHY
    424,117 live wall art listings. Measured on the real export:
        mean title length   67.4 of 80
        under 70 chars      59%
        wasted characters   5,343,432
        home decor           8%      picture         0%
        gift                25%      room word      27%
    Only 24% ever received an intent phrase from the earlier retitle_art.py -
    the other 76% still read as generator vocabulary:

        "Donkey Watercolour Loose Dusty Pink A4 Wall Art Print"
        "Kingfisher Farmhouse Rustic Black And White A4 Wall Art Print"

    "Watercolour Loose", "Dusty Pink" and "Farmhouse Rustic" describe the
    picture to someone already looking at it. Nobody types them.

HONESTY CONSTRAINT
    These are UNFRAMED A4 PAPER PRINTS. The title never claims Canvas, Framed,
    or Ready to Hang, however much search volume those words carry. A false
    product claim buys one sale and a defect. Competitors selling real canvas
    may use them; we may not.

WHAT IT WRITES
    An eBay File Exchange REVISE file - Action, ItemID, Title. Titles change in
    place, so listings keep their age, watchers and search history. Nothing
    ends, nothing relists, images untouched.

USE
    python3 retitle_wallart.py export.csv --out revise_wallart.csv
    python3 retitle_wallart.py export.csv --out revise.csv --sample 40
"""

import argparse, csv, hashlib, re, sys
from collections import Counter

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

MAX, TARGET_MIN = 80, 70

# --------------------------------------------------------------- vocabulary to strip

STYLES = [
    "Vintage Ad Illustration", "Vintage Botanical Plate", "Vintage Travel Poster",
    "Scandinavian Minimal", "Line Art Continuous", "Cute Watercolour Loose",
    "Botanical Illustration", "Ink Wash Japanese", "Bauhaus Geometric",
    "Whimsical Nursery", "Mid Century Modern", "Mid-Century Modern",
    "Coastal Grandmother", "Watercolour Loose", "Farmhouse Rustic",
    "Antique Botanical", "Quiet Luxury", "Modern Organic", "Country Club",
    "Grandmillennial", "Sacred Geometry", "French Country", "English Country",
    "Mediterranean Sun", "Industrial Loft", "Dark Academia", "Maximalist Pattern",
    "Boho Desert", "Art Deco Luxury", "Nordic Folk", "Kraft Poster", "Japandi Zen",
    "Pressed Flower", "Vintage Poster", "Minimal Line", "Retro 70s", "Art Deco",
    "Cottagecore", "Chalkboard", "Blueprint", "Risograph", "Block Print",
    "Linocut", "Japandi", "Bauhaus", "Tachisme", "Colour Field",
]
PALETTES = [
    "Warm Neutral Beige", "Cream And Cream", "Black And White", "Muted Pastels",
    "Mustard Yellow", "Burnt Orange", "Forest Green", "Dusty Pink", "Navy Blue",
    "Sage Green", "Deep Teal", "Terracotta", "Burgundy", "Charcoal", "Indigo",
    "Blush", "Olive", "Rust", "Mauve", "Slate", "Sand", "Ochre", "Cream",
]
# phrases the previous retitle already injected - strip so we can rebuild cleanly
OLD_INTENT = [
    "Farmhouse Country Kitchen Gift", "Nursery Kids Bedroom Decor Gift",
    "Coastal Nautical Bathroom Gift", "Celestial Astrology Decor Gift",
    "Horse Lover Equestrian Gift", "Botanical Kitchen Decor Gift",
    "Botanical Floral Decor Gift", "Kitchen Cafe Bar Decor Gift",
    "Quote Typography Decor Gift", "Landscape Travel Poster Gift",
    "Wildlife Woodland Gift", "Abstract Modern Decor Gift",
    "Vintage Retro Decor Gift", "City Travel Poster Gift", "Wildlife Animal Gift",
    "Dog Lover Pet Gift", "Cat Lover Pet Gift", "Bird Wildlife Gift",
    "Home Decor Gift", "Sports Decor Gift", "Pet Lover Gift",
]
ROOMS_STRIP = ["Living Room Bedroom", "Living Room", "Bedroom", "Kitchen",
               "Bathroom", "Nursery", "Hallway", "Home Office", "Dining Room"]
TAILS_STRIP = ["A4 Wall Art Print", "A3 Wall Art Print", "Wall Art Poster Print",
               "Wall Art Print", "Wall Art Poster", "A4 ART PRINT", "ART PRINT",
               "Wall Art", "Poster Print", "Poster", "Print", "A4", "A3"]

# ------------------------------------------------------------------- buyer intent
# (subject regex, keyword phrase, room word). First match wins, specific first.

INTENT = [
    (r"\b(terrier|retriever|spaniel|collie|poodle|dachshund|labrador|beagle|bulldog|"
     r"pug|husky|corgi|shepherd|doberman|rottweiler|whippet|greyhound|chihuahua|"
     r"shih tzu|pomeranian|schnauzer|setter|pointer|mastiff|cockapoo|cavapoo|"
     r"labradoodle|jack russell|puppy|dog)\b", "Dog Lover Gift", "Living Room"),
    (r"\b(cat|kitten|persian|siamese|ragdoll|maine coon|bengal|tabby|shorthair)\b",
     "Cat Lover Gift", "Living Room"),
    (r"\b(horse|pony|stallion|mare|foal|equestrian)\b", "Horse Lover Gift", "Bedroom"),
    (r"\b(rabbit|hamster|guinea pig|budgie|parrot|ferret|hedgehog)\b", "Pet Lover Gift", "Nursery"),
    (r"\b(cow|bull|calf|sheep|lamb|goat|pig|hen|chick|rooster|duck|goose|turkey|"
     r"donkey|tractor|barn|farm|highland)\b", "Farmhouse Country Gift", "Kitchen"),
    (r"\b(lion|tiger|leopard|cheetah|elephant|giraffe|zebra|rhino|hippo|monkey|"
     r"gorilla|panda|koala|kangaroo|safari)\b", "Wildlife Animal Gift", "Nursery"),
    (r"\b(fox|badger|deer|stag|hare|otter|squirrel|wolf|bear|moose|elk|lynx)\b",
     "Woodland Wildlife Gift", "Living Room"),
    (r"\b(owl|eagle|hawk|falcon|robin|wren|finch|kingfisher|heron|puffin|swan|"
     r"peacock|pheasant|crow|raven|hummingbird|cardinal|butterfly|bee|dragonfly|bird)\b",
     "Bird Wildlife Gift", "Living Room"),
    (r"\b(whale|dolphin|shark|turtle|octopus|jellyfish|seahorse|crab|lobster|"
     r"starfish|coral|clownfish|fish|mermaid|seaside|coastal|beach|ocean|wave|"
     r"lighthouse|nautical|sail)\b", "Coastal Nautical Gift", "Bathroom"),
    (r"\b(herb|sage|rosemary|thyme|basil|mint|lavender|garlic|lemon|tomato|"
     r"mushroom|vegetable|fruit|pumpkin|cheese|apple|pear|olive)\b",
     "Kitchen Decor Gift", "Kitchen"),
    (r"\b(coffee|espresso|tea|wine|gin|cocktail|beer|whisky|bread|cake|pizza|bar)\b",
     "Kitchen Cafe Bar Gift", "Kitchen"),
    (r"\b(flower|floral|rose|peony|tulip|sunflower|daisy|poppy|orchid|botanical|"
     r"leaf|fern|palm|monstera|eucalyptus|plant|cactus|succulent|bouquet|"
     r"birth flower|wildflower)\b", "Botanical Floral Gift", "Living Room"),
    (r"\b(baby|nursery|bunny|teddy|balloon|rainbow|unicorn|dinosaur|alphabet|"
     r"little one|hello little)\b", "Nursery Kids Gift", "Nursery"),
    (r"\b(london|paris|new york|rome|venice|tokyo|liverpool|manchester|edinburgh|"
     r"dublin|barcelona|amsterdam|lisbon|skyline|city|map|tram|battersea|hampstead)\b",
     "City Travel Gift", "Living Room"),
    (r"\b(lake district|cornwall|yorkshire|snowdonia|highlands|mountain|forest|"
     r"coast|national park|landscape|countryside|valley|river)\b",
     "Landscape Travel Gift", "Living Room"),
    (r"\b(moon|star|sun|planet|galaxy|constellation|zodiac|celestial|astronomy|"
     r"aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|"
     r"aquarius|pisces)\b", "Celestial Astrology Gift", "Bedroom"),
    (r"\b(quote|motivational|inspirational|typography|but first|home sweet|love|"
     r"family|magic|you are)\b", "Quote Typography Gift", "Home Office"),
    (r"\b(car|motorcycle|train|plane|boat|ship|bike|saloon|scooter|vintage advert)\b",
     "Vintage Retro Gift", "Home Office"),
    (r"\b(football|rugby|cricket|tennis|golf|boxing|cycling|climbing|sport)\b",
     "Sports Fan Gift", "Home Office"),
    (r"\b(abstract|geometric|shape|line art|minimal|pattern|tile|colours chart|"
     r"mandala|sacred)\b", "Abstract Modern Gift", "Living Room"),
]
DEFAULT_INTENT = ("Home Decor Gift", "Living Room")

# ---------------------------------------------------------------- relabelling
# Only 3,122 distinct subjects exist across 424,117 listings - each repeated
# ~136 times, differing ONLY by style and palette. So style and palette cannot
# be stripped: they are the sole differentiator, and removing them collapses the
# catalogue into 3,122 duplicate titles.
#
# Keep both. Relabel them into words buyers actually search. The rendering
# recipe is unchanged - only the label moves.
STYLE_MAP = {
    "Watercolour Loose": "Watercolour", "Cute Watercolour Loose": "Watercolour",
    "Farmhouse Rustic": "Farmhouse", "Scandinavian Minimal": "Scandinavian",
    "Nordic Folk": "Scandinavian", "Whimsical Nursery": "Nursery",
    "Antique Botanical": "Vintage Botanical", "Botanical Illustration": "Botanical",
    "Vintage Botanical Plate": "Vintage Botanical", "Kraft Poster": "Vintage",
    "Vintage Ad Illustration": "Retro Advert", "Vintage Travel Poster": "Vintage Travel",
    "Vintage Poster": "Vintage", "Mid Century Modern": "Mid Century",
    "Mid-Century Modern": "Mid Century", "Line Art Continuous": "Line Art",
    "Minimal Line": "Line Art", "Modern Organic": "Modern", "Japandi Zen": "Japandi",
    "Ink Wash Japanese": "Japanese", "Bauhaus Geometric": "Bauhaus",
    "Sacred Geometry": "Geometric", "Colour Field": "Abstract",
    "Tachisme": "Abstract", "Maximalist Pattern": "Maximalist",
    "Industrial Loft": "Industrial", "Art Deco Luxury": "Art Deco",
    "Coastal Grandmother": "Coastal", "Boho Desert": "Boho",
    "English Country": "Country", "French Country": "French",
    "Mediterranean Sun": "Mediterranean", "Quiet Luxury": "Luxury",
    "Grandmillennial": "Traditional", "Dark Academia": "Dark Academia",
    "Country Club": "Preppy", "Pressed Flower": "Pressed Flower",
    "Block Print": "Block Print", "Cottagecore": "Cottagecore",
    "Chalkboard": "Chalkboard", "Blueprint": "Blueprint", "Risograph": "Retro",
    "Linocut": "Linocut", "Japandi": "Japandi", "Bauhaus": "Bauhaus",
    "Art Deco": "Art Deco", "Retro 70s": "Retro",
}
# Colour IS searched in decor ("sage green wall art"). Keep it - only normalise
# the ones that read as a paint chart rather than a search term.
PALETTE_MAP = {
    "Warm Neutral Beige": "Beige", "Cream And Cream": "Cream",
    "Muted Pastels": "Pastel", "Black And White": "Black And White",
    "Mustard Yellow": "Mustard", "Burnt Orange": "Burnt Orange",
    "Forest Green": "Forest Green", "Dusty Pink": "Dusty Pink",
    "Navy Blue": "Navy", "Sage Green": "Sage Green", "Deep Teal": "Teal",
    "Terracotta": "Terracotta", "Burgundy": "Burgundy", "Charcoal": "Charcoal",
    "Indigo": "Indigo", "Blush": "Blush", "Olive": "Olive", "Rust": "Rust",
    "Mauve": "Mauve", "Slate": "Slate", "Sand": "Sand", "Ochre": "Ochre",
    "Cream": "Cream",
}
_STYLE_FIND = re.compile(r"(?i)\b(" + "|".join(
    re.escape(k) for k in sorted(STYLE_MAP, key=len, reverse=True)) + r")\b")
_PAL_FIND = re.compile(r"(?i)\b(" + "|".join(
    re.escape(k) for k in sorted(PALETTE_MAP, key=len, reverse=True)) + r")\b")


def extract_style_colour(title):
    """Pull the style and palette OUT of the original, mapped to search terms."""
    sm = _STYLE_FIND.search(title)
    pm = _PAL_FIND.search(title)
    style = STYLE_MAP.get(sm.group(1).title(), "") if sm else ""
    if sm and not style:
        for k, v in STYLE_MAP.items():
            if k.lower() == sm.group(1).lower():
                style = v
                break
    colour = ""
    if pm:
        for k, v in PALETTE_MAP.items():
            if k.lower() == pm.group(1).lower():
                colour = v
                break
    return style, colour


# Honest product nouns for UNFRAMED A4 PAPER. No Canvas, no Framed, no Ready to Hang.
TAIL_VARIANTS = [
    "Wall Art Print Poster Picture Home Decor Unframed A4",
    "Wall Art Poster Print Picture Home Decor A4 Unframed",
    "Wall Art Print Picture Poster Home Decor A4",
    "Wall Art Poster Print Picture Decor A4",
    "Wall Art Print Poster Picture A4",
    "Wall Art Print Poster A4",
    "Wall Art Print A4",
]


# One compiled alternation, longest phrase first, instead of ~120 separate
# passes per title. Over 424k rows that is the difference between minutes and
# hours.
_STRIP_RE = re.compile(
    r"(?i)(?<=\s)(?:" + "|".join(
        re.escape(p) for p in sorted(
            set(OLD_INTENT + TAILS_STRIP + ROOMS_STRIP + STYLES + PALETTES),
            key=len, reverse=True)
    ) + r")(?=\s)")
_TRAIL_RE = re.compile(r"(?i)\b(gift|decor|home|and|the|with)\b\s*$")
_WS_RE = re.compile(r"\s+")


def strip_vocab(title):
    """Recover the SUBJECT by removing everything the generator added."""
    t = " " + title + " "
    prev = None
    while prev != t:                 # phrases can sit adjacent
        prev = t
        t = _STRIP_RE.sub(" ", t)
    return _WS_RE.sub(" ", _TRAIL_RE.sub(" ", t)).strip(" -|,")


_INTENT_C = [(re.compile(p), kw, room) for p, kw, room in INTENT]


def classify(subject, original):
    hay = f"{subject} {original}".lower()
    for rx, kw, room in _INTENT_C:
        if rx.search(hay):
            return kw, room
    return DEFAULT_INTENT


CORE = "Wall Art Print"          # never dropped - the product identity
SIZE = "A4"                      # never dropped
EXTRA_NOUNS = ["Poster", "Picture", "Home Decor", "Unframed", "Gift Idea"]


def build(subject, colour, style, keywords, room):
    """Pack the title to 70-80 chars in strict priority order.

    Subject, "Wall Art Print" and "A4" are protected. Everything else is added
    only while it fits, most valuable first:
        colour and style  - searched, AND the only thing distinguishing the ~136
                            listings that share each subject
        gift phrase       - buyer intent
        room              - a sidebar filter
        extra nouns       - fill the remaining characters
    """
    subject = " ".join(subject.split()[:6]) or "Wall Art"
    used = {w.lower() for w in subject.split()}
    used.update({"wall", "art", "print", "a4"})

    parts = [subject]
    reserved = len(CORE) + len(SIZE) + 2      # both plus their spaces

    def try_add(phrase):
        nonlocal parts
        if not phrase:
            return
        words = [w for w in phrase.split() if w.lower() not in used]
        if not words:
            return
        cand = " ".join(words)
        if len(" ".join(parts)) + 1 + len(cand) + reserved <= MAX:
            parts.append(cand)
            used.update(w.lower() for w in words)

    for phrase in (colour, style, keywords, room, *EXTRA_NOUNS):
        try_add(phrase)

    return re.sub(r"\s+", " ", f"{' '.join(parts)} {CORE} {SIZE}").strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export")
    ap.add_argument("--out", default="revise_wallart.csv")
    ap.add_argument("--category", default="360")
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--cull-out", help="also write an End file for seed re-rolls: "
                    "keep the OLDEST listing per (subject, colour, style) group, end the rest")
    ap.add_argument("--version", default="745")
    a = ap.parse_args()

    with open(a.export, encoding="utf-8-sig", newline="") as fh:
        first = fh.readline()
        if not first.startswith("#INFO"):
            fh.seek(0)
        rows = list(csv.DictReader(fh))

    art = [r for r in rows
           if a.category in (r.get("Category name") or "") and (r.get("Title") or "").strip()]
    print(f"  wall art rows: {len(art):,}")

    seen, out, stats = set(), [], Counter()
    for r in art:
        item, old = r.get("Item number", "").strip(), r["Title"].strip()
        subject = strip_vocab(old)
        if not subject:                       # 1,766 titles strip to nothing
            subject = " ".join(old.split()[:4])
        style, colour = extract_style_colour(old)
        kw, room = classify(subject, old)
        new = build(subject, colour, style, kw, room)

        # never ship two identical titles
        if new.lower() in seen:
            for alt in ("Picture", "Poster", "Home Decor", "Gift Idea",
                        "Unframed", "Decor", "Wall Decor"):
                if alt.lower() in new.lower() or len(new) + len(alt) + 1 > MAX:
                    continue
                cand = f"{new} {alt}"
                if cand.lower() not in seen:
                    new = cand
                    break
        seen.add(new.lower())

        stats["changed"] += (new != old)
        stats["in_band"] += (TARGET_MIN <= len(new) <= MAX)
        stats["over"] += (len(new) > MAX)
        out.append((item, new, old))
        if a.sample and len(out) <= a.sample:
            print(f"    [{len(old):2d}] {old}\n    [{len(new):2d}] {new}\n")

    # ---- optional cull -------------------------------------------------
    # 424,117 listings describe only 43,483 distinct (subject, colour, style)
    # products - a mean of 9.8 listings per description, up to 234. Those are
    # re-rolls of one prompt with a different seed. No title can separate them
    # because there is nothing to separate. Keep the OLDEST of each group (most
    # listing age = most accumulated ranking equity) and end the rest.
    if a.cull_out:
        groups = {}
        for r in art:
            subject = strip_vocab(r["Title"]) or " ".join(r["Title"].split()[:4])
            style, colour = extract_style_colour(r["Title"])
            key = (subject.lower(), colour.lower(), style.lower())
            item = r.get("Item number", "").strip()
            if key not in groups or item < groups[key]:
                groups[key] = item
        keep = set(groups.values())
        ending = [r.get("Item number", "").strip() for r in art
                  if r.get("Item number", "").strip() not in keep]
        with open(a.cull_out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow([f"Action(SiteID=UK|Country=GB|Currency=GBP|Version={a.version}|CC=UTF-8)",
                        "ItemID", "EndCode"])
            for item in ending:
                w.writerow(["End", item, "NotAvailable"])
        print(f"\n  CULL: {len(keep):,} distinct products kept, "
              f"{len(ending):,} seed re-rolls to end -> {a.cull_out}")

    header = f"Action(SiteID=UK|Country=GB|Currency=GBP|Version={a.version}|CC=UTF-8)"
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([header, "ItemID", "*Title"])
        for item, new, _ in out:
            w.writerow(["Revise", item, new])

    n = len(out)
    lens = [len(t) for _, t, _ in out]
    print(f"\n  written: {n:,} revise rows -> {a.out}")
    print(f"  titles changed        {stats['changed']:,} ({stats['changed']/n:.0%})")
    print(f"  in the 70-80 band     {stats['in_band']:,} ({stats['in_band']/n:.0%})")
    print(f"  over 80 chars         {stats['over']}   <- must be 0")
    print(f"  duplicate titles      {n - len(seen)}   <- must be 0")
    print(f"  mean length           {sum(lens)/n:.1f}  (was 67.4)")
    print(f"  characters reclaimed  {sum(lens) - sum(len(o) for _,_,o in out):,}")


if __name__ == "__main__":
    main()
