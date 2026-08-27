"""
retitle_art.py — rewrite wall art titles around what buyers actually search.

WHY
    424,118 live wall art listings, no sales. Their titles read

        Sea Turtle Watercolour Loose Muted Pastels A4 Wall Art Print

    Half of that is aesthetic vocabulary from the generator — Watercolour,
    Loose, Muted Pastels, Kraft, Terracotta, Ochre. It describes the picture
    to someone already looking at it. Nobody types it into search.

    Measured across all 424,118 titles:
        gift                0%
        home decor          0%
        picture             0%
        framed / unframed   0%
        bedroom, kitchen, living room, office   ~0%
        poster             14%
    and the average title used 64 of the 80 characters eBay allows.

    So: drop the dead words, keep the subject, and spend the space on terms
    people search — the wall art equivalent of "Dog Lover" on a t-shirt.

WHAT IT WRITES
    An eBay File Exchange REVISE file: Action, ItemID, Title. Nothing else.
    Titles change in place — listings keep their age, their watchers and
    their search history. No ending, no relisting, no risk to the images.

USE
    python3 retitle_art.py export.csv --out revise
"""

import argparse, csv, os, re, sys

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

MAX = 80

# ---------------------------------------------------------------------------
# The generator's own vocabulary. These are the words to reclaim: they are
# style and palette names, not search terms.
# ---------------------------------------------------------------------------
STYLES = [
    "Vintage Travel Poster", "Scandinavian Minimal", "Line Art Continuous",
    "Cute Watercolour Loose", "Watercolour Loose", "Antique Botanical",
    "Farmhouse Rustic", "Kraft Poster", "Retro 70s", "Art Deco",
    "Mid Century Modern", "Japandi", "Bauhaus", "Risograph", "Linocut",
    "Block Print", "Pressed Flower", "Chalkboard", "Blueprint",
    "Botanical Illustration", "Vintage Poster", "Minimal Line",
]
PALETTES = [
    "Warm Neutral Beige", "Black And White", "Muted Pastels", "Mustard Yellow",
    "Forest Green", "Dusty Pink", "Navy Blue", "Sage Green", "Burnt Orange",
    "Deep Teal", "Terracotta", "Burgundy", "Ochre", "Cream", "Charcoal",
    "Blush", "Olive", "Rust", "Indigo", "Mauve", "Slate", "Sand",
]
TAIL = ["A4 Wall Art Print", "A3 Wall Art Print", "Wall Art Print"]

# ---------------------------------------------------------------------------
# Buyer intent by subject. The wall art equivalent of "Dog Lover" — the words
# someone types when they are shopping rather than describing.
#
# Order matters: the first match wins, so the specific sits above the general.
# ---------------------------------------------------------------------------
INTENT = [
    # pets — the strongest gifting intent on the whole site
    (r"\b(terrier|retriever|spaniel|collie|poodle|dachshund|labrador|beagle|"
     r"bulldog|pug|husky|corgi|shepherd|doberman|rottweiler|whippet|greyhound|"
     r"chihuahua|shih tzu|pomeranian|schnauzer|setter|pointer|mastiff|"
     r"cockapoo|cavapoo|labradoodle|puppy|dog)\b", "Dog Lover Pet Gift"),
    (r"\b(cat|kitten|persian|siamese|ragdoll|maine coon|bengal|tabby)\b",
     "Cat Lover Pet Gift"),
    (r"\b(horse|pony|stallion|mare|foal)\b", "Horse Lover Equestrian Gift"),
    (r"\b(rabbit|hamster|guinea pig|budgie|parrot|ferret)\b",
     "Pet Lover Gift"),

    # farm and countryside
    (r"\b(cow|bull|calf|sheep|lamb|goat|pig|hen|chick|rooster|duck|goose|"
     r"turkey|donkey|tractor|barn|farm)\b", "Farmhouse Country Kitchen Gift"),

    # wildlife
    (r"\b(lion|tiger|leopard|cheetah|elephant|giraffe|zebra|rhino|"
     r"hippo|monkey|gorilla|panda|koala|kangaroo|safari)\b",
     "Wildlife Animal Gift"),
    (r"\b(fox|badger|deer|stag|hare|hedgehog|otter|squirrel|wolf|bear|"
     r"moose|elk|lynx|highland)\b", "Wildlife Woodland Gift"),

    # birds
    (r"\b(owl|eagle|hawk|falcon|robin|wren|finch|tit|kingfisher|heron|"
     r"puffin|swan|peacock|pheasant|crow|raven|hummingbird|bird)\b",
     "Bird Wildlife Gift"),

    # sea
    (r"\b(whale|dolphin|shark|turtle|octopus|jellyfish|seahorse|crab|"
     r"lobster|starfish|coral|clownfish|fish|seaside|coastal|beach|ocean|"
     r"wave|lighthouse|nautical)\b", "Coastal Nautical Bathroom Gift"),

    # botanical and kitchen
    (r"\b(herb|sage|rosemary|thyme|basil|mint|lavender|garlic|lemon|"
     r"tomato|mushroom|vegetable|fruit|seed catalogue)\b",
     "Botanical Kitchen Decor Gift"),
    (r"\b(flower|floral|rose|peony|tulip|sunflower|daisy|poppy|orchid|"
     r"botanical|leaf|fern|palm|monstera|eucalyptus|plant|cactus|"
     r"succulent|bouquet)\b", "Botanical Floral Decor Gift"),

    # food and drink
    (r"\b(coffee|espresso|tea|wine|gin|cocktail|beer|whisky|bread|cake|"
     r"pizza|kitchen)\b", "Kitchen Cafe Bar Decor Gift"),

    # places
    (r"\b(london|paris|new york|rome|venice|tokyo|liverpool|manchester|"
     r"edinburgh|dublin|barcelona|amsterdam|skyline|city|map)\b",
     "City Travel Poster Gift"),
    (r"\b(lake district|cornwall|yorkshire|snowdonia|highlands|mountain|"
     r"forest|coast|national park|landscape|countryside)\b",
     "Landscape Travel Poster Gift"),

    # nursery
    (r"\b(baby|nursery|bunny|teddy|balloon|rainbow|unicorn|dinosaur|"
     r"alphabet|nursery rhyme)\b", "Nursery Kids Bedroom Decor Gift"),

    # celestial and abstract
    (r"\b(moon|star|sun|planet|galaxy|constellation|zodiac|celestial|"
     r"astronomy|aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|"
     r"sagittarius|capricorn|aquarius|pisces)\b",
     "Celestial Astrology Decor Gift"),
    (r"\b(quote|motivational|inspirational|typography|but first|"
     r"home sweet|love|family)\b", "Quote Typography Decor Gift"),
    (r"\b(abstract|geometric|shape|line art|minimal)\b",
     "Abstract Modern Decor Gift"),
    (r"\b(car|motorcycle|train|plane|boat|ship|bike|vintage advert)\b",
     "Vintage Retro Decor Gift"),
    (r"\b(football|rugby|cricket|tennis|golf|boxing|cycling|climbing)\b",
     "Sports Decor Gift"),
]

# what every wall art title should carry, in priority order
BASE = "Wall Art Print"
FILLERS = ["Poster", "Home Decor", "Unframed", "Picture", "A4"]


def strip_known(title):
    """Pull the SUBJECT out by removing the generator's own vocabulary."""
    t = title
    for phrase in TAIL + sorted(STYLES, key=len, reverse=True) + \
            sorted(PALETTES, key=len, reverse=True):
        t = re.sub(re.escape(phrase), " ", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip(" -|,")


def intent_for(subject):
    s = subject.lower()
    for pattern, words in INTENT:
        if re.search(pattern, s):
            return words
    return "Home Decor Gift"


def build(subject, intent):
    """Fill 80 characters, most valuable words first, never truncating a word."""
    parts = [subject, intent, BASE]
    title = " ".join(p for p in parts if p)

    # drop a repeated word rather than saying Gift twice
    seen, words = set(), []
    for w in title.split():
        k = w.lower()
        if k in seen:
            continue
        seen.add(k)
        words.append(w)
    title = " ".join(words)

    if len(title) > MAX:                      # subject itself is long
        while len(title) > MAX and " " in title:
            title = title.rsplit(" ", 1)[0]
        return title

    for extra in FILLERS:                     # spend what is left
        if extra.lower() in title.lower():
            continue
        if len(title) + 1 + len(extra) <= MAX:
            title += " " + extra
    return title


ap = argparse.ArgumentParser()
ap.add_argument("export")
ap.add_argument("--out", default="revise")
ap.add_argument("--rows", type=int, default=30000)
ap.add_argument("--category", default="Art Prints")
ap.add_argument("--preview", type=int, default=0,
                help="print N before/after pairs and write nothing")
args = ap.parse_args()

rows = list(csv.reader(open(args.export, encoding="utf-8-sig", errors="ignore")))
head = next(i for i, r in enumerate(rows) if r and r[0] == "Action")
h = rows[head]
iC, iT, iN = (h.index("Category name"), h.index("Title"),
              h.index("Item number"))

out, unchanged, generic = [], 0, 0
for r in rows[head + 1:]:
    if len(r) <= max(iC, iT, iN) or not r[iN].strip():
        continue
    if args.category and not r[iC].startswith(args.category):
        continue
    subject = strip_known(r[iT])
    if not subject:
        continue
    intent = intent_for(subject)
    if intent == "Home Decor Gift":
        generic += 1
    new = build(subject, intent)
    if new == r[iT]:
        unchanged += 1
        continue
    out.append((r[iN].strip("\"' "), new))

if args.preview:
    for item, new in out[:args.preview]:
        print(new)
    print()
    print("%s titles would change, %s fell back to the generic keywords"
          % (format(len(out), ","), format(generic, ",")))
    sys.exit()

n = 0
for i in range(0, len(out), args.rows):
    n += 1
    dst = "%s_%02d.csv" % (args.out, n)
    with open(dst, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Action(SiteID=UK|Country=GB|Currency=GBP|Version=745"
                    "|CC=UTF-8)", "ItemID", "*Title"])
        for item, title in out[i:i + args.rows]:
            w.writerow(["Revise", item, title])
    print("  %s  %s listings" % (dst, format(len(out[i:i + args.rows]), ",")))

print()
print("%s titles rewritten across %d files" % (format(len(out), ","), n))
print("%s already matched and were skipped" % format(unchanged, ","))
print("%s used the generic keywords — worth adding rules for these"
      % format(generic, ","))
