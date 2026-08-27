"""
ebay_graphics.py — eBay UK File Exchange CSV for the GRAPHIC designs.

ebay_csv.py builds titles from slogan text and cannot be used here: the
graphics queue has subjects and art styles, not phrases. Running it against
this queue would produce nonsense titles.

TITLE RULES, carried over from what worked on the text listings:
  * the SUBJECT is always present — "Welsh Dragon", "Labrador" — because that
    is the word a buyer types
  * "T-Shirt" is always present and is never dropped to make room
  * a theme keyword the buyer would search ("Fantasy", "Dog Lover", "Gothic")
  * "Mens" for consistency with the category, the Department field and the
    sizing; a Womens claim against mens sizing invites returns
  * 80 characters hard limit, no duplicates, no numeric padding

STRUCTURE, proven accepted on this account:
    category 15687        Men's Clothing > Shirts & Tops > T-Shirts
    shipping 2, returns 1, payment 1
    RelationshipDetails   "Size=v1;v2;v3"  — one dimension, all values
    variation rows repeat Title + Category, carry "Size=thisvalue"
    CustomLabel, PicURL and Description on the PARENT ONLY
    Size is the only variation dimension; the A4 transfer is a size

    python3 ebay_graphics.py --dir mock_w0 --rows 160000
"""

import argparse, csv, hashlib, html, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--dir", default="mock", help="folder of mockup jpgs")
ap.add_argument("--queue", default="generation_queue.csv")
ap.add_argument("--single", action="store_true",
                help="FLAT listings — one row per design, no variations. The "
                     "buyer types their size in the note at checkout. For a "
                     "smaller account where the variation allowance is tight: "
                     "the same catalogue fits into far fewer listing slots")
ap.add_argument("--personalise-text",
                default="TYPE SIZE BELOW, CHOOSE: S,M,L,XL,XXL",
                help="the instruction shown above the buyer's text box")
ap.add_argument("--single-price", type=float, default=11.99,
                help="the one price used in --single mode")
ap.add_argument("--rows", type=int, default=160000)
ap.add_argument("--out", default="tshirt_ebay")
ap.add_argument("--category", default="15687")
ap.add_argument("--shipping", default="2")
ap.add_argument("--returns", default="1")
ap.add_argument("--payment", default="1")
# City stays. Plenty of sellers are in Manchester, so a shared city is not
# the signal a shared POSTCODE is — the postcode is specific enough to tie
# accounts together, the city is not. Pass --location per store if a
# particular account should say something else.
ap.add_argument("--location", default="Manchester")
# Blank by default. The same postcode repeated across several stores is a
# signal that ties those accounts together, which is the opposite of what
# the multi-store setup is for. eBay falls back to the postcode on the
# account itself, which is already correct per store.
# Pass --postcode "M1 1AE" only if a single store genuinely needs an
# override.
ap.add_argument("--no-shuffle", action="store_true",
                help="keep the sorted-by-design-number order. Rarely wanted: "
                     "it groups the upload by subject")
ap.add_argument("--seed", type=int, default=20260813,
                help="shuffle seed. Change it to get a different order, or "
                     "use a different seed per store so each gets its own mix")
ap.add_argument("--postcode", default="")
ap.add_argument("--prefix", default="GR")
ap.add_argument("--img-base",
                default="https://pub-19fad43c12d848caa97d6d53a8695d03.r2.dev")
args = ap.parse_args()

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# Kids start at 3-4 Yrs and adults stop at 2XL. 10 variations per listing.
SIZES = [
    # Aug 2026: only the smallest kids size is cheaper. The A4 iron-on
    # transfer was dropped entirely — it was folded into the size axis, so
    # removing it takes the listing from 11 variations to 10.
    ("3-4 Yrs", 8.99),
    ("5-6 Yrs", 11.99), ("7-8 Yrs", 11.99),
    ("9-11 Yrs", 11.99), ("12-13 Yrs", 11.99),
    ("S", 11.99), ("M", 11.99), ("L", 11.99), ("XL", 11.99), ("2XL", 11.99),
]
QTY = 1

# The word a buyer searching this family would actually type.
FAMILY_KEYWORD = {
    "dragon": "Fantasy", "mythic": "Fantasy", "norse": "Viking Norse",
    "wild": "Wildlife", "bird": "Bird", "sea": "Sea Ocean",
    "reptile": "Reptile", "cute": "Cute", "nature": "Nature",
    "dino": "Dinosaur", "gothic": "Gothic", "warrior": "Warrior",
    "cosmic": "Space", "machine": "Retro", "botanical": "Nature",
    "breed": "Pet Lover", "academia": "Vintage", "cottage": "Cottagecore",
    "y2k": "Retro Y2K",
    # The "human" family was added later and had no entry here, so it fell
    # through to the default extras of ["Gift"] — which put "Gift" back into
    # 110 titles after it had been deliberately removed.
    "human": "Fantasy",
}
FAMILY_EXTRA = {
    "dragon": ["Dragon", "Mythical", "Gaming", "RPG", "Fantasy Art"],
    "mythic": ["Mythology", "Legend", "Fantasy Art", "Folklore"],
    "norse": ["Odin", "Valhalla", "Nordic", "Runes"],
    "wild": ["Animal", "Nature", "Wild Animal", "Wildlife Art"],
    "bird": ["Birdwatching", "Wildlife", "Nature", "Ornithology"],
    "sea": ["Marine", "Diving", "Nature", "Ocean Life"],
    "reptile": ["Snake", "Exotic", "Animal", "Herpetology"],
    "cute": ["Kawaii", "Cute Animal", "Adorable"],
    "nature": ["Insect", "Wildlife", "Entomology"],
    "dino": ["Jurassic", "Prehistoric", "Kids", "Fossil"],
    "gothic": ["Skull", "Dark", "Alternative", "Halloween", "Occult"],
    "warrior": ["Samurai", "Knight", "Martial Arts", "Battle"],
    "cosmic": ["Astronomy", "Galaxy", "Sci Fi", "Universe"],
    "machine": ["Classic", "Vintage", "Motoring", "Engineering"],
    "botanical": ["Botanical", "Plant", "Garden", "Floral"],
    "breed": ["Owner", "Animal", "Lover"],
    "academia": ["Dark Academia", "Books", "Vintage", "Scholar"],
    "cottage": ["Cottagecore", "Garden", "Rustic", "Countryside"],
    "y2k": ["Y2K", "90s", "Nostalgia", "Retro Vibes"],
    "human": ["Warrior", "Legend", "Mythology", "Folklore", "Fantasy Art"],
}


AUDIENCE = "Mens"
PRODUCT = "T-Shirt"
# "Gift" and "100% Cotton" deliberately excluded — both are generic filler
# that every competitor uses, so they add no search advantage and eat
# characters that a real keyword could use.
# "Idea" was left over from "Gift Idea" and means nothing on its own.
TAIL = ["Novelty", "Present", "Top", "Tee", "Graphic Tee", "Birthday",
        "Christmas", "Xmas", "Cotton", "Unisex", "Adults", "Printed"]
EBAY_MAX = 80
_seen = set()

# eBay's duplicate detection works on the SET of words, not the exact string.
# "Welsh Dragon Airbrush ..." and "Airbrush Welsh Dragon ..." are the same
# listing to eBay even though the strings differ — that is the pattern that
# got 40,000 listings flagged before. Track fingerprints, not just titles.
_fingerprints = set()

# The CORE is the title before optional keywords are appended. Two listings
# whose cores match are near-duplicates even if the trailing word differs:
#   "... 100% Cotton Tee" vs "... 100% Cotton Puppy"
# That is the "Gift 1 / Gift 2" pattern with better manners, and eBay treats
# it the same way.
_cores = set()


def fingerprint(title):
    return " ".join(sorted(w.lower() for w in title.split()))


# --- descriptive title building -------------------------------------------
# Competitors describe the artwork in plain words before stacking keywords:
#   "Greyscale Dragon Mens T-Shirt 100% Cotton"
#   "A Dragon in Nature Fantasy Mens T-Shirt 100% Cotton"
#   "Ferret Watercolour Mens T-Shirt 100% Cotton"
# So the title opens with what the design actually IS, not a keyword dump.

# Style -> a word a buyer would recognise and search.
STYLE_WORD = [
    ("watercolour", "Watercolour"), ("splatter", "Splatter Art"),
    ("dripping", "Drip Art"), ("ink dispersion", "Ink Art"),
    ("neon airbrush", "Neon"), ("iridescent", "Colourful"),
    ("psychedelic", "Psychedelic"), ("greyscale", "Greyscale"),
    ("monochrome charcoal", "Charcoal"), ("neo traditional tattoo", "Tattoo"),
    ("realistic tattoo", "Tattoo"), ("airbrushed", "Airbrush"),
    ("double exposure", "Double Exposure"), ("anime key visual", "Anime"),
    ("bold graphic", "Graphic"), ("dark fantasy digital", "Dark Fantasy"),
    ("epic concept art", "Fantasy Art"), ("hyper detailed", "Detailed"),
    ("lush foliage", "Botanical"), ("dark botanical", "Botanical"),
]

# Scene -> a short setting phrase. These are what turn a bare subject into
# "A Dragon in Nature" rather than "Dragon Graphic".
SCENE_PHRASE = [
    ("wreathed in flames", "in Flames"),
    ("drifting embers", "in Flames"),
    ("swirling smoke", "in Smoke"),
    ("glowing moon", "in Moonlight"),
    ("starry", "Under the Stars"),
    ("constellations", "Under the Stars"),
    ("nebula", "in Space"),
    ("dark foliage", "in Nature"),
    ("leaves and vines", "in Nature"),
    ("wildflowers", "with Flowers"),
    ("thorns and roses", "with Roses"),
    ("autumn leaves", "in Autumn"),
    ("falling snow", "in the Snow"),
    ("frost crystals", "in the Frost"),
    ("water splashing", "in Water"),
    ("waves curling", "in the Waves"),
    ("lightning", "in a Storm"),
    ("storm clouds", "in a Storm"),
    ("runes glowing", "with Runes"),
    ("sacred geometry", "Sacred Geometry"),
    ("shattered glass", "Shattered"),
    ("neon light trails", "Neon Glow"),
    ("radiant light", "Glowing"),
    ("luminous particles", "Glowing"),
    # Every scene needs a phrase. 36 of 60 had none, so designs that differed
    # only by scene produced identical titles and were separated by a trailing
    # keyword instead — the "Gift 1 / Gift 2" pattern in disguise.
    ("paint splatter", "Splash"),
    ("ink splashes", "Ink Splash"),
    ("dripping colour runs", "Dripping"),
    ("geometric light rays", "Geometric"),
    ("glowing halo", "Halo"),
    ("nothing behind", "Portrait"),
    ("torn paper", "Torn Paper"),
    ("swirling water ribbons", "in Water"),
    ("rising bubbles", "Underwater"),
    ("cracked earth", "Desert"),
    ("drifting dust", "Dust"),
    ("scattered feathers", "with Feathers"),
    ("hanging moss", "in the Swamp"),
    ("mushrooms clustered", "with Mushrooms"),
    ("pine branches", "in the Pines"),
    ("burning halo", "Burning"),
    ("sparks scattering", "with Sparks"),
    ("cold blue mist", "in the Mist"),
    ("icicles forming", "Frozen"),
    ("torn cloth", "Torn"),
    ("black feathers falling", "with Feathers"),
    ("fractured moon", "Broken Moon"),
    ("light beams", "Sunbeams"),
    ("an aurora", "Aurora"),
    ("orbiting rings", "Orbit"),
    ("distant planet", "in Orbit"),
    ("triangle framing", "Triangle"),
    ("split circle", "Circle"),
    ("brush stroke", "Brushstroke"),
    ("arch shape", "Arch"),
    ("hexagon outline", "Hexagon"),
    ("alchemical symbols", "Alchemy"),
    ("pentagram", "Occult"),
    ("candle flames", "Candlelit"),
    ("rain streaking", "in the Rain"),
    ("wind swept", "Windswept"),
]


# Cat breeds and farm animals in the "breed" family. Everything else in that
# family is a dog, so the keyword follows the actual animal rather than a
# coin flip.
# Cats, horses and farm animals inside the "breed" family. Everything else in
# that family is a dog.
#
# This used to be a fixed list of names, which broke the moment new cat breeds
# were added: "Russian Blue Cat" was not in the list, so it was labelled
# "Dog Lover" and "Doggo". The name itself is now the primary signal, with a
# list only for breeds whose name does not say what they are.
CAT_NAMED = {
    "Maine Coon", "British Shorthair", "Russian Blue", "Abyssinian",
    "Burmese", "Birman", "Devon Rex", "Cornish Rex", "Scottish Fold",
    "Munchkin", "Turkish Van", "Turkish Angora", "Somali", "Chartreux",
    "Selkirk Rex", "Manx", "Savannah", "Ocicat", "Ragdoll", "Sphynx",
    "Siamese", "Persian", "Bengal", "Tabby", "Calico", "Tortie",
    "Tortoiseshell", "Tuxedo",
}
HORSE_NAMED = {
    "Shire Horse", "Shetland Pony", "Highland Pony", "Arabian Horse",
    "Thoroughbred Horse", "Clydesdale Horse", "Friesian Horse",
    "Appaloosa Horse", "Palomino Horse", "Welsh Cob", "Dartmoor Pony",
    "Exmoor Pony", "New Forest Pony", "Connemara Pony", "Donkey",
}
FARM_NAMED = {
    "Alpaca", "Sheep", "Hereford Bull", "Chicken", "Duck", "Llama",
    "Highland Bull", "Jersey Cow", "Belted Galloway", "Aberdeen Angus",
    "Suffolk Sheep", "Herdwick Sheep", "Jacob Sheep", "Goat", "Pygmy Goat",
    "Pig", "Kunekune Pig", "Rooster",
}


def _is(subject, named):
    """True if the subject IS one of these, by name or by naming convention."""
    if subject in named:
        return True
    low = subject.lower()
    return any(re.search(r"\b" + re.escape(n.lower()) + r"\b", low)
               for n in named)


def breed_terms(subject):
    """
    Keyword and extras that actually match the animal.

    Order matters: a name containing "Cat" as a whole word decides it before
    anything else, so a new cat breed can be added without touching this.
    "Australian Cattle Dog" is safe because the match is word-bounded.
    """
    low = subject.lower()

    if re.search(r"\bcats?\b|\bkitten\b|\bmoggy\b", low) or _is(subject, CAT_NAMED):
        return "Cat Lover", ["Cat", "Kitten", "Owner", "Feline", "Moggy"]

    if re.search(r"\bhorses?\b|\bpony\b|\bponies\b|\bfoal\b|\bcob\b", low) \
            or _is(subject, HORSE_NAMED):
        return "Horse Lover", ["Equestrian", "Pony", "Riding", "Stables"]

    if _is(subject, FARM_NAMED):
        return "Farm Animal", ["Farming", "Countryside", "Rural", "Smallholding"]

    return "Dog Lover", ["Dog", "Puppy", "Owner", "Canine", "Doggo"]


# The generic word a buyer types, for subjects where it is not already in the
# name. Someone searching "dragon t shirt" should find a Wyvern; someone
# searching "bird t shirt" should find a Barn Owl. Without this the listing
# only surfaces for the exact species name.
SUBJECT_WORD = {
    # dragons that are not called dragons
    "Wyvern": "Dragon", "Hydra": "Dragon", "Basilisk": "Dragon",
    # birds
    "Eagle": "Bird", "Golden Eagle": "Bird", "Owl": "Bird",
    "Barn Owl": "Bird", "Snowy Owl": "Bird", "Raven": "Bird",
    "Crow": "Bird", "Falcon": "Bird", "Kingfisher": "Bird",
    "Heron": "Bird", "Puffin": "Bird", "Robin": "Bird", "Swan": "Bird",
    "Peacock": "Bird", "Hummingbird": "Bird",
    # sea life
    "Orca": "Whale", "Humpback Whale": "Sea", "Octopus": "Sea",
    "Jellyfish": "Sea", "Manta Ray": "Sea", "Sea Turtle": "Turtle",
    "Seahorse": "Sea", "Koi Carp": "Fish", "Salmon": "Fish",
    "Pike": "Fish", "Shark": "Sea", "Great White Shark": "Sea",
    # reptiles
    "Cobra": "Snake", "Rattlesnake": "Snake", "Viper": "Snake",
    "Chameleon": "Reptile", "Gecko": "Reptile", "Iguana": "Reptile",
    "Crocodile": "Reptile", "Bearded Dragon": "Reptile",
    # insects
    "Bee": "Insect", "Butterfly": "Insect", "Moth": "Insect",
    "Dragonfly": "Insect", "Beetle": "Insect", "Spider": "Insect",
    # dinosaurs
    "Tyrannosaurus Rex": "Dinosaur", "Triceratops": "Dinosaur",
    "Velociraptor": "Dinosaur", "Stegosaurus": "Dinosaur",
    "Brachiosaurus": "Dinosaur", "Spinosaurus": "Dinosaur",
    "Pterodactyl": "Dinosaur", "Ankylosaurus": "Dinosaur",
    # cat breeds without "Cat" in the name
    "Maine Coon": "Cat", "British Shorthair": "Cat",
    # Baby animals sit in the "cute" family, so they never get a breed
    # keyword — a Kitten design said "Cute Mens T-Shirt" with no "Cat" in it
    # anywhere, and was invisible to the obvious search. The generic word has
    # to come from here instead.
    "Kitten": "Cat", "Puppy": "Dog", "Foal": "Horse", "Lamb": "Sheep",
    "Piglet": "Pig", "Duckling": "Duck", "Chick": "Chicken",
    "Bear Cub": "Bear", "Fox Cub": "Fox", "Fennec Kit": "Fox",
    "Baby Otter": "Otter", "Lop Rabbit": "Rabbit",
    "Netherland Dwarf Rabbit": "Rabbit", "Rex Rabbit": "Rabbit",
    "Angora Rabbit": "Rabbit", "Flemish Giant Rabbit": "Rabbit",
    "Syrian Hamster": "Hamster", "Roborovski Hamster": "Hamster",
    "African Pygmy Hedgehog": "Hedgehog",

    # wolves and big cats
    "Fenrir Wolf": "Wolf", "Panther": "Big Cat", "Lynx": "Wild Cat",
    "Snow Leopard": "Big Cat",
}


def style_word(style):
    low = style.lower()
    for key, word in STYLE_WORD:
        if key in low:
            return word
    return "Graphic"


def scene_phrase(scene):
    low = scene.lower()
    for key, phrase in SCENE_PHRASE:
        if key in low:
            return phrase
    return ""


def describe(subject, scene, style, h):
    """
    A natural opening phrase, alternating between the forms competitors use:
        "Greyscale Dragon"          style then subject
        "Dragon in Flames"          subject then setting
        "Watercolour Wolf in Snow"  both
    """
    sw = style_word(style)
    sp = scene_phrase(scene)
    form = h % 3
    if form == 0 and sw != "Graphic":
        return f"{sw} {subject}" + (f" {sp}" if sp else "")
    if form == 1 and sp:
        return f"{subject} {sp}"
    if sw != "Graphic":
        return f"{subject} {sw}"
    return f"{subject} {sp}".strip() if sp else subject


def make_title(subject, family, style, scene, seed):
    """
    [descriptive phrase] [family keyword] Mens T-Shirt [extras] 100% Cotton

    The subject and "T-Shirt" are never dropped; everything else gives way.
    """
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)

    head = describe(subject, scene, style, h)
    if family == "breed":
        fam, extras_list = breed_terms(subject)
    else:
        fam = FAMILY_KEYWORD.get(family, "Graphic")
        extras_list = FAMILY_EXTRA.get(family, ["Novelty", "Printed"])

    # If the generic word is not already in the subject name, it becomes part
    # of the protected keyword rather than an optional extra — a Wyvern
    # listing is useless if it never says "Dragon".
    generic = SUBJECT_WORD.get(subject)
    if generic and generic.lower() not in subject.lower():
        if generic.lower() not in fam.lower():
            fam = f"{generic} {fam}"

    # Reserve room for the keywords, then trim the DESCRIPTION to fit. The
    # earlier version dropped the family keyword when a title ran long, which
    # cost 837 listings their category word and left 42 groups differing only
    # by a trailing keyword. The description is prose; the keywords are why
    # anyone finds the listing.
    tail_parts = [p for p in (fam, AUDIENCE, PRODUCT) if p]
    seen_w = set()
    keep = []
    for part in tail_parts:
        words = {w.lower() for w in part.split()}
        if words & seen_w:
            continue
        seen_w |= words
        keep.append(part)
    reserved = len(" ".join(keep)) + 1

    budget = EBAY_MAX - reserved
    hw = head.split()
    trimmed = ""
    for w in hw:
        if w.lower() in seen_w:
            continue
        cand = (trimmed + " " + w).strip()
        if len(cand) > budget:
            break
        trimmed = cand
    # the subject must survive whatever else is cut
    if subject.lower() not in trimmed.lower():
        trimmed = subject[:budget].strip()
    seen_w |= {w.lower() for w in trimmed.split()}

    title = " ".join([trimmed] + keep)

    # Check the core BEFORE adding optional keywords, so near-duplicates are
    # caught while there is still room to differentiate.
    if title in _seen or fingerprint(title) in _cores:
        sw2, sp2 = style_word(style), scene_phrase(scene)
        # Try WITH the family keyword first. The earlier version rebuilt the
        # title without it and never added it back, so 11% of dog listings
        # lost "Dog Lover" — the exact term a buyer searches.
        got = False
        for variant in (f"{sw2} {subject} {sp2}".strip(),
                        f"{subject} {sp2} {sw2}".strip(),
                        f"{subject} {sw2} {sp2}".strip()):
            variant = " ".join(variant.split())
            cand = f"{variant} {fam} {AUDIENCE} {PRODUCT}"
            if len(cand) <= EBAY_MAX and fingerprint(cand) not in _cores:
                title = cand
                got = True
                break
        # If the full family keyword will not fit, keep at least the generic
        # category word. Losing "Fantasy" costs a secondary term; losing
        # "Dragon" makes a Wyvern listing invisible to the obvious search.
        must = generic or ""
        if not got:
            for variant in (f"{sw2} {subject} {sp2}".strip(),
                            f"{subject} {sp2} {sw2}".strip(),
                            f"{subject} {sw2} {sp2}".strip()):
                variant = " ".join(variant.split())
                mid = f" {must}" if must and must.lower() not in variant.lower() else ""
                cand = f"{variant}{mid} {AUDIENCE} {PRODUCT}"
                if len(cand) <= EBAY_MAX and fingerprint(cand) not in _cores:
                    title = cand
                    got = True
                    break
        if not got:
            # shortest forms, generic word still protected
            for variant in (f"{sw2} {subject}".strip(),
                            f"{subject} {sp2}".strip(),
                            subject):
                variant = " ".join(variant.split())
                mid = f" {must}" if must and must.lower() not in variant.lower() else ""
                cand = f"{variant}{mid} {AUDIENCE} {PRODUCT}"
                if len(cand) <= EBAY_MAX and fingerprint(cand) not in _cores:
                    title = cand
                    got = True
                    break
    _cores.add(fingerprint(title))

    used = {w.lower() for w in title.split()}
    extras = extras_list
    # "100% Cotton" appears in almost every competitor title, so it goes first
    # in the queue of optional additions.
    # fam first: "Dog Lover" is the search term, "100% Cotton" is a
    # nice-to-have. If only one fits, it must be the search term.
    # The generic word is listed separately as well as inside fam, so that if
    # fam is dropped for length the bare category word still lands. A Wyvern
    # listing that never says "Dragon" is invisible to the obvious search.
    pool = [fam]
    if generic:
        pool.append(generic)
    # "black t shirt" is a high-volume search and the garment is black only,
    # so it ranks above the material and the novelty words.
    pool += ["Black", "100% Cotton", extras[h % len(extras)],
             TAIL[(h >> 4) % len(TAIL)], extras[(h >> 8) % len(extras)]]
    for e in pool:
        if any(w.lower() in used for w in e.split()):
            continue
        cand = f"{title} {e}"
        if len(cand) <= EBAY_MAX:
            title = cand
            used |= {w.lower() for w in e.split()}

    if title in _seen or fingerprint(title) in _fingerprints:
        # A long subject ("Cavalier King Charles Spaniel") crowds out the
        # style word, so two different designs can collapse to one title.
        # Rebuild keeping the words that actually DIFFER between designs —
        # the style and the setting — and drop optional keywords to fit.
        # This is real differentiation, not numeric padding.
        sw, sp = style_word(style), scene_phrase(scene)
        # Try the fullest descriptions first. For a long subject name these
        # only fit once the optional keywords are dropped — which is correct:
        # the scene and style are what make the listing distinct, "100% Cotton"
        # is not. Differentiation outranks the nice-to-have keywords.
        for variant in (f"{sw} {subject} {sp}".strip(),
                        f"{subject} {sp} {sw}".strip(),
                        f"{subject} {sw} {sp}".strip(),
                        f"{sw} {subject}",
                        f"{subject} {sp}"):
            variant = " ".join(variant.split())
            if not variant or variant == head:
                continue
            _must = f" {generic}" if generic and generic.lower() not in variant.lower() else ""
            cand = f"{variant}{_must} {AUDIENCE} {PRODUCT}"
            if len(cand) > EBAY_MAX or cand in _seen:
                continue
            title = cand
            u = {w.lower() for w in title.split()}
            # fam first: "Dog Lover" carries more search weight than "100% Cotton"
            for e in [fam] + extras + TAIL:
                if any(w.lower() in u for w in e.split()):
                    continue
                nxt = f"{title} {e}"
                if len(nxt) <= EBAY_MAX and nxt not in _seen:
                    title = nxt
                    u |= {w.lower() for w in e.split()}
            if fingerprint(title) not in _fingerprints:
                break

    if title in _seen or fingerprint(title) in _fingerprints:
        raise SystemExit(
            f"DUPLICATE TITLE: {title!r}\n"
            "Two designs produced the same title even after using the style "
            "and setting to distinguish them. Check the queue for duplicate "
            "designs — do not pad the title.")
    _seen.add(title)
    _fingerprints.add(fingerprint(title))
    return title


DESC = """<div style="font-family:Arial,Helvetica,sans-serif;max-width:800px;margin:0 auto;color:#222;line-height:1.6">
<div style="background:#111;color:#fff;padding:22px 26px;border-radius:6px 6px 0 0">
<h1 style="margin:0;font-size:24px">{subject}</h1>
<p style="margin:6px 0 0;font-size:14px;opacity:.75">Premium Printed <strong>Black</strong> T-Shirt &middot; Mens (Unisex) &middot; UK Sizing</p>
</div>
<div style="border:1px solid #e3e3e6;border-top:none;padding:26px;border-radius:0 0 6px 6px">

<p style="font-size:15px">A bold, full-colour {subject_l} design printed on a soft heavyweight <strong>black</strong> cotton tee. Printed in the UK using a professional direct-to-film process, so the colours stay rich and the finish stays flexible rather than thick or plasticky &mdash; and it holds up wash after wash.</p>

<h2 style="font-size:17px;border-bottom:2px solid #111;padding-bottom:6px;margin-top:26px">Product Details</h2>
<ul style="padding-left:20px;font-size:15px">
<li>Crew Necked T-Shirt</li><li><strong>Colour: Black</strong></li>
<li>Mens (Unisex)</li><li>Classic Fit</li>
<li>180gsm heavy cotton</li><li>Age 3-4 Yrs to 2XL</li>
<li>100% Cotton</li>
<li>Pre-shrunk jersey knit</li><li>Taped neck and shoulders</li>
<li>Twin needle sleeve and bottom hems</li><li>Seamless twin needle collar</li>
<li>Tear away label</li><li>Hard wearing fabric</li>
</ul>
<p style="font-size:15px;margin-top:14px">Printed with eco-friendly inks, which are safe on skin and suitable for children.</p>

<h2 style="font-size:17px;border-bottom:2px solid #111;padding-bottom:6px;margin-top:26px">Size Guide</h2>
<p style="font-size:15px">Measured flat, in inches. Allow up to one inch tolerance.</p>
<table style="width:100%;border-collapse:collapse;font-size:14px;margin-top:10px">
<tr style="background:#111;color:#fff"><th style="padding:7px 9px;text-align:left">Size</th><th style="padding:7px 9px;text-align:left">To Fit Chest</th><th style="padding:7px 9px;text-align:left">Width</th><th style="padding:7px 9px;text-align:left">Length</th></tr>
{rows}
</table>
<p style="font-size:14px;margin-top:14px"><strong>Kids sizes</strong> &mdash; 3-4 Yrs (chest 14&quot;), 5-6 Yrs (15&quot;), 7-8 Yrs (16&quot;), 9-11 Yrs (17&quot;), 12-13 Yrs (18&quot;).</p>
<p style="font-size:15px"><strong>Fit note:</strong> Mens (Unisex) classic fit. These run a little roomier than high street brands &mdash; if you prefer a slim fit, consider going one size down.</p>

<h2 style="font-size:17px;border-bottom:2px solid #111;padding-bottom:6px;margin-top:26px">Postage &amp; Returns</h2>
<p style="font-size:15px">Dispatched from the UK with tracked delivery. If anything is not right, get in touch and we will sort it &mdash; returns are straightforward.</p>

<h2 style="font-size:17px;border-bottom:2px solid #111;padding-bottom:6px;margin-top:26px">Care</h2>
<p style="font-size:15px">Machine wash at 30&deg;C inside out. Do not iron directly on the print. Do not tumble dry on high.</p>

<p style="margin-top:24px;font-size:11px;color:#9a9aa0">{tags}</p>
</div></div>"""

_SZ = [("S", "34-36", "18", "28"), ("M", "38-40", "20", "29"),
       ("L", "42-44", "22", "30"), ("XL", "46-48", "24", "31"),
       ("2XL", "50-52", "26", "32")]
_cell = 'style="padding:6px 9px;border-bottom:1px solid #e5e5e8"'
# The alternating-row style is built outside the f-string: Python 3.11 does
# not allow a backslash inside an f-string expression, and the pod runs 3.11.
_ALT = ' style="background:#fafafb"'
_rowlist = []
for _i, (_s, _f, _w, _l) in enumerate(_SZ):
    _bg = _ALT if _i % 2 else ""
    _rowlist.append(
        "<tr" + _bg + ">"
        "<td " + _cell + "><strong>" + _s + "</strong></td>"
        "<td " + _cell + ">" + _f + "&quot;</td>"
        "<td " + _cell + ">" + _w + "&quot;</td>"
        "<td " + _cell + ">" + _l + "&quot;</td></tr>")
_ROWS = "\n".join(_rowlist)

ACTION = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=745|CC=UTF-8)"
HEADER = [
    ACTION, "CustomLabel", "*Category", "StoreCategory",
    "Relationship", "RelationshipDetails", "*Title", "Subtitle",
    "*Description", "*ConditionID", "PicURL", "*Format", "*Duration",
    "*StartPrice", "*Quantity", "*Location", "PostalCode",
    "ShippingProfileName", "ReturnProfileName", "PaymentProfileName",
    "*C:Size", "*C:Colour", "C:Brand", "*C:Type", "*C:Style", "C:Department",
    "*C:Material", "C:Sleeve Length", "C:Neckline", "C:Fit", "C:Pattern",
    "C:Size Type", "C:Garment Care", "C:Occasion", "C:Theme",
    "C:Country/Region of Manufacture", "C:Personalise",
    # C:Handmade is sent BLANK deliberately. The personalisation box works
    # without it — it just takes a minute to appear on a new listing — and
    # these are print-on-demand, not handmade.
    "C:Personalisation Instructions", "C:Handmade", "C:Features",
]

# Subjects to skip when building listings. The current run was queued before
# human subjects were gated to faceless compositions, so it contains ~6,689
# open-faced figures. AI faces at this size often have subtle wrongness that
# reads as cheap, and a realistic face also invites a likeness complaint.
# Cheaper to leave them unlisted than to regenerate.
SKIP_SUBJECTS = {
    "Valkyrie", "Berserker", "Norse Warrior", "Shield Maiden", "Ronin",
    "Highland Warrior", "Celtic Warrior", "Archer", "Swordsman",
    "Minotaur", "Centaur",
}

# which designs actually exist as mockups
have = {os.path.splitext(f)[0] for f in os.listdir(args.dir)
        if f.lower().endswith((".jpg", ".png"))}
queue = {r["index"]: r for r in csv.DictReader(open(args.queue, encoding="utf-8"))}
# SHUFFLE, always.
#
# Sorting by design number groups the catalogue by subject: adjacent numbers
# map to the same subject, so a sorted upload arrives as a block of dragons,
# then a block of wolves. That looks like spam in a newly-listed feed, and it
# means a slice taken for another store is all one thing.
#
# shuffle_csv.py did this afterwards, but it is a separate step that gets
# skipped — on this batch finish.sh stopped at the duplicate check and the
# shuffle never ran, which is exactly how the blocks reached the upload.
# Doing it here means it cannot be missed.
#
# The seed is fixed so a rebuild produces the same order — useful when a run
# has to be repeated — but pass --seed to change it, or --no-shuffle for the
# old sorted behaviour.
ids = sorted((i for i in have if i in queue), key=int)
if not args.no_shuffle:
    import random as _r
    _r.Random(args.seed).shuffle(ids)
_before = len(ids)
ids = [i for i in ids if queue[i]["subject"] not in SKIP_SUBJECTS]
if _before != len(ids):
    print(f"skipped {_before - len(ids):,} open-faced human designs")
print(f"{len(ids):,} designs with mockups")
if not ids:
    raise SystemExit("no mockups found")

rel = "Size=" + ";".join(s for s, _ in SIZES)
# flat mode is one row per listing; variation mode is parent + sizes
rows_per = 1 if args.single else 1 + len(SIZES)
per_file = max(1, args.rows // rows_per)

buf, files, n = [], [], 1


def flush():
    global buf, n
    if not buf:
        return
    fn = f"{args.out}_{n:02d}.csv"
    with open(fn, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(buf)
    print(f"  {fn}  {len(buf):,} rows  {os.path.getsize(fn)/1e6:.0f} MB")
    files.append(fn)
    buf = []
    n += 1


count = 0
for did in ids:
    q = queue[did]
    subject, family, style = q["subject"], q["family"], q["style"]
    label = f"{args.prefix}-{int(did):07d}"
    title = make_title(subject, family, style, q["scene"], did)
    _extras = (breed_terms(subject)[1] if family == "breed"
               else FAMILY_EXTRA.get(family, ["novelty"]))
    tags = ", ".join(t.lower() + " t shirt" for t in [subject] + _extras)
    desc = DESC.format(subject=html.escape(subject),
                       subject_l=html.escape(subject.lower()),
                       rows=_ROWS, tags=html.escape(tags))

    if args.single:
        # ONE FLAT LISTING, size collected through eBay's PERSONALISATION
        # field — not variations, not a note at checkout.
        #
        # The columns come from a real listing he set up by hand and
        # exported, rather than being guessed:
        #   C:Personalise                   Yes
        #   C:Personalisation Instructions   the text above the box
        # The buyer then gets a free-text box on the listing page and types
        # their size into it.
        #
        # Size is "One Size" deliberately. The field is required by the
        # category, and a real size there would contradict the box.
        buf.append([
            "Add", label, args.category, "", "", "", title, "", desc,
            "1000", f"{args.img_base}/art/mock/{did}.jpg",
            "FixedPrice", "GTC", f"{args.single_price:.2f}", str(QTY),
            args.location, args.postcode,
            args.shipping, args.returns, args.payment,
            "One Size", "Black", "Unbranded", "T-Shirt",
            "Graphic Tee", "Unisex Adults",
            "Cotton", "Short Sleeve", "Crew Neck", "Regular", "No Pattern",
            "Regular", "Machine Washable", "Casual",
            FAMILY_KEYWORD.get(family, "Graphic"),
            "United Kingdom", "Yes", args.personalise_text, "", "Breathable",
        ])
        count += 1
        if count % per_file == 0:
            flush()
        continue

    buf.append([
        "Add", label, args.category, "", "", rel, title, "", desc,
        "1000", f"{args.img_base}/art/mock/{did}.jpg",
        "FixedPrice", "GTC", "", "",
        args.location, args.postcode,
        args.shipping, args.returns, args.payment,
        "", "Black", "Unbranded", "T-Shirt", "Graphic Tee", "Unisex Adults",
        "Cotton", "Short Sleeve", "Crew Neck", "Regular", "No Pattern",
        "Regular", "Machine Washable", "Casual",
        FAMILY_KEYWORD.get(family, "Graphic"),
        "United Kingdom", "No", "", "", "Breathable",
    ])

    for size, price in SIZES:
        if "Yrs" in size:
            dept, typ = "Unisex Kids", "T-Shirt"
        else:
            dept, typ = "Unisex Adults", "T-Shirt"
        buf.append([
            "", "", args.category, "", "Variation", f"Size={size}",
            title, "", "", "1000", "",
            "", "", f"{price:.2f}", str(QTY), "", "", "", "", "",
            size, "Black", "Unbranded", typ, "Graphic Tee", dept,
            "Cotton", "Short Sleeve", "Crew Neck", "Regular", "No Pattern",
            "Regular", "Machine Washable", "Casual",
            FAMILY_KEYWORD.get(family, "Graphic"),
            "United Kingdom", "No", "", "", "Breathable",
        ])

    count += 1
    if count % per_file == 0:
        flush()

flush()

print(f"\n{count:,} listings | {count*rows_per:,} rows | {len(files)} files")
print(f"titles over 80 chars : {sum(1 for t in _seen if len(t) > 80)}")
print(f"duplicate titles     : {count - len(_seen)}")
print(f"every title has 'T-Shirt': "
      f"{all('t-shirt' in t.lower() for t in _seen)}")
