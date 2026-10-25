#!/usr/bin/env python3
"""The browsable niche tree for the website.

WHY THIS IS NOT A KEYWORD CLASSIFIER. The first version of this file matched
words against subject strings - "terrier" means dog, "poppy" means flower.
That was wrong twice over: it mislabels ("dog violet" is a flower, "dog
lichen" is a fungus, "dog whelk" is a sea snail) and it silently drops
whatever no rule happens to cover, which on 5,204 subjects is a long tail
nobody would ever notice was missing.

The subject lists in wallart-data/subjects/*.py are ALREADY grouped - DOGS,
BRITISH_BIRDS, FUNGI_MORE, COAST, CONSTELLATIONS and forty more. Those groups
were written by hand when the catalogue was planned, so they are editorial
judgements, not inferences. This file reads them and maps each group to a
niche a buyer would browse. Every subject therefore lands in exactly one
niche, by construction, and `check()` proves it rather than assuming it.

A subject that appears in no group is a hard error. It means someone extended
a subject module without extending its ALL tuple, and the right outcome is a
refusal, not a product quietly filed under "Other".
"""
import json, os, sys

WALLART = os.environ.get(
    "WALLART_DIR", "/home/user/wonderleaf-books/wallart-data")

# Top-level sections. Order is the order of the site navigation.
SECTIONS = [
    ("animals",      "Animals & Wildlife", "creature"),
    ("botanical",    "Flowers & Botanical", "botanical"),
    ("landscapes",   "Landscapes & Places", "place"),
    ("night-sky",    "Space & Night Sky",   "celestial"),
    ("still-life",   "Still Life",          "stilllife"),
    ("architecture", "Architecture",        "architecture"),
]

# (module, LIST NAME) -> (section, niche slug, niche title, blurb)
#
# The blurb is shown on the niche page and is also what makes each category
# page genuinely different from the next, which matters for Google: 43 near
# identical category pages is the thin-content pattern that stops a new shop
# being indexed at all.
GROUPS = [
    # --- creatures ----------------------------------------------------------
    ("creatures", "BRITISH_MAMMALS", "animals", "british-wildlife",
     "British Wildlife",
     "Foxes, badgers, otters, deer and hares - the mammals of these islands, "
     "drawn as studies rather than as cartoons."),
    ("creatures", "BRITISH_BIRDS", "animals", "british-birds",
     "British Birds",
     "Robins, wrens, kingfishers, owls and waders, taken from the British "
     "list and drawn one species at a time."),
    ("creatures", "DOGS", "animals", "dogs", "Dogs",
     "Breed studies, from working terriers to gundogs and hounds. Generic "
     "breed names only - no named dogs, no mascots."),
    ("creatures", "DOGS_MORE", "animals", "dogs", "Dogs", ""),
    ("creatures", "CATS", "animals", "cats", "Cats",
     "Breed and coat studies of domestic cats, drawn with the eyes right - "
     "which is the one thing that makes or breaks an animal print."),
    ("creatures", "SMALL_PETS", "animals", "small-pets", "Small Pets",
     "Rabbits, guinea pigs, rats and the rest of the hutch and cage animals."),
    ("creatures", "HORSE_BREEDS", "animals", "horses", "Horses & Ponies",
     "Native ponies and heavy breeds - Shires, Highlands, Exmoors - as well "
     "as the riding types."),
    ("creatures", "FARM_BREEDS", "animals", "farm-animals", "Farm Animals",
     "Rare and commercial breeds of sheep, cattle, pigs, goats and poultry, "
     "named by breed."),
    ("creatures", "WORLD_WILDLIFE", "animals", "world-wildlife",
     "World Wildlife",
     "Big cats, elephants, primates and the large mammals of Africa, Asia "
     "and the Americas."),
    ("creatures", "MAMMALS_WORLD_MORE", "animals", "world-wildlife",
     "World Wildlife", ""),
    ("creatures", "BIRDS_WORLD", "animals", "world-birds", "Birds of the World",
     "Parrots, hornbills, hummingbirds, cranes and the rest of the world "
     "list, beyond the British birds."),
    ("creatures", "BUTTERFLIES_MOTHS_MORE", "animals", "butterflies",
     "Butterflies & Moths",
     "Wing studies of British and European butterflies and moths, named by "
     "species."),
    ("creatures", "INSECTS_SMALL", "animals", "insects", "Insects & Bugs",
     "Bees, beetles, dragonflies and the smaller invertebrates, drawn large "
     "enough to see."),
    ("creatures", "BEETLES_BUGS_MORE", "animals", "insects",
     "Insects & Bugs", ""),
    ("creatures", "FISH_FRESHWATER", "animals", "freshwater-fish",
     "Freshwater Fish",
     "Coarse and game fish of British rivers and lakes - trout, pike, perch, "
     "barbel and the rest."),
    ("creatures", "MARINE_LIFE_MORE", "animals", "sea-life", "Sea Life",
     "Whales, seals, sharks, rays, shells and sea fish, plus the "
     "rockpool animals."),
    ("creatures", "REPTILES_AMPHIBIANS_MORE", "animals", "reptiles",
     "Reptiles & Amphibians",
     "Frogs, newts, lizards, geckos and snakes, named by species."),

    # --- botanical ----------------------------------------------------------
    ("botanical", "GARDEN_FLOWERS", "botanical", "garden-flowers",
     "Garden Flowers",
     "Roses, peonies, dahlias, tulips and the rest of the border, drawn as "
     "single specimens and small arrangements."),
    ("botanical", "PERENNIALS_MORE", "botanical", "garden-flowers",
     "Garden Flowers", ""),
    ("botanical", "WILDFLOWERS", "botanical", "wildflowers", "Wildflowers",
     "Meadow and hedgerow flowers - poppies, cow parsley, foxgloves, "
     "harebells - named by common name."),
    ("botanical", "BULBS_ALPINES", "botanical", "bulbs-alpines",
     "Bulbs & Alpines",
     "Snowdrops, crocuses, irises, alliums and the rock-garden plants."),
    ("botanical", "FOLIAGE_TREES", "botanical", "leaves", "Leaves & Foliage",
     "Single leaves and leaf studies - oak, maple, ivy, fern - where the "
     "shape is the whole subject."),
    ("botanical", "TREES_SHRUBS_MORE", "botanical", "trees", "Trees & Shrubs",
     "Whole trees and shrubs by species, from English oak to monkey puzzle."),
    ("botanical", "FERNS_GRASSES_MOSSES", "botanical", "ferns-grasses",
     "Ferns, Grasses & Moss",
     "Fronds, seed heads, sedges and mosses - the quiet green end of the "
     "botanical range."),
    ("botanical", "FUNGI_MORE", "botanical", "mushrooms-fungi",
     "Mushrooms & Fungi",
     "Field mushrooms, brackets, waxcaps and lichens, named by species. "
     "Illustrations, not a foraging guide."),
    ("botanical", "TROPICAL_HOUSEPLANTS", "botanical", "houseplants",
     "Houseplants & Tropical",
     "Monstera, palms, orchids and the glasshouse plants, including cacti "
     "and succulents."),
    ("botanical", "HERBS_EDIBLE_FUNGI", "botanical", "herbs-edibles",
     "Herbs & Edibles",
     "Kitchen herbs, salad leaves and edible plants, drawn as botanical "
     "specimens."),
    ("botanical", "AQUATIC_SEAWEED", "botanical", "seaweed-water-plants",
     "Seaweed & Water Plants",
     "Wracks, kelps and pond plants - the coastal and freshwater botanicals."),

    # --- places -------------------------------------------------------------
    ("places_uk", "COAST", "landscapes", "british-coast", "British Coast",
     "Bays, coves, harbours and headlands of the British coastline, named "
     "place by named place."),
    ("places_uk", "MOUNTAINS_HILLS", "landscapes", "mountains-hills",
     "Mountains & Hills",
     "Munros, Welsh peaks, Lakeland fells and the ridges in between."),
    ("places_uk", "NATIONAL_PARKS", "landscapes", "national-parks",
     "National Parks",
     "The fifteen national parks of Great Britain, drawn as landscapes "
     "rather than maps."),
    ("places_uk", "AONB", "landscapes", "british-countryside",
     "British Countryside",
     "Downs, dales, broads and the designated landscapes - the gentler "
     "country between the parks."),
    ("places_uk", "LOCHS_LAKES_RIVERS", "landscapes", "lakes-rivers",
     "Lochs, Lakes & Rivers",
     "Still water and running water, from Highland lochs to chalk streams."),
    ("places_uk", "ISLANDS", "landscapes", "islands", "Islands",
     "Orkney, Skye, Scilly, Lundy and the rest of the offshore places."),
    ("places_uk", "LANDMARKS_NATURAL", "landscapes", "natural-landmarks",
     "Natural Landmarks",
     "Sea stacks, waterfalls, caves and gorges - the named natural features."),
    ("places_uk", "CITIES_TOWNS", "landscapes", "british-cities",
     "British Cities & Towns",
     "City and town views, drawn as skylines, streets and rooftops."),
    ("places_world", "CITIES_EUROPE", "landscapes", "european-cities",
     "European Cities",
     "Paris, Lisbon, Venice, Prague and the rest of the European list."),
    ("places_world", "CITIES_ASIA_PACIFIC", "landscapes", "asia-pacific",
     "Asia & Pacific",
     "Tokyo, Kyoto, Singapore, Sydney and the cities of the Pacific rim."),
    ("places_world", "CITIES_AMERICAS", "landscapes", "americas",
     "The Americas",
     "New York, New Orleans, Rio, Vancouver and the cities of the Americas."),
    ("places_world", "CITIES_AFRICA", "landscapes", "africa", "Africa",
     "Marrakesh, Cairo, Cape Town and the African cities."),
    ("places_world", "LANDSCAPE_TYPES", "landscapes", "world-landscapes",
     "World Landscapes",
     "Deserts, salt flats, hot springs and the landscape types that belong "
     "to no single country."),

    # --- celestial ----------------------------------------------------------
    ("celestial", "MOON", "night-sky", "the-moon", "The Moon",
     "Phases, supermoons and the named full moons of the year. The strongest "
     "single subject in this whole range."),
    ("celestial", "CONSTELLATIONS", "night-sky", "constellations",
     "Constellations",
     "The twenty-four shapes a buyer can actually name, drawn as star maps."),
    ("celestial", "PLANETS", "night-sky", "planets", "Planets",
     "The planets and dwarf planets, as discs and as crescents."),
    ("celestial", "DEEP_SKY", "night-sky", "deep-sky", "Deep Sky",
     "Nebulae, clusters and galaxies - the faint objects, drawn bold."),
    ("celestial", "ATMOSPHERE", "night-sky", "sky-and-aurora",
     "Sky & Aurora",
     "Aurorae, eclipses, meteor showers and haloes - what happens between "
     "the ground and the stars."),

    # --- still life ---------------------------------------------------------
    ("stilllife", "HOT_DRINKS", "still-life", "coffee-and-tea",
     "Coffee & Tea",
     "Pots, cups and the apparatus of a hot drink - kitchen prints that earn "
     "their wall."),
    ("stilllife", "COLD_DRINKS", "still-life", "drinks", "Drinks",
     "Glassware and cold drinks, drawn as still life."),
    ("stilllife", "FRUIT_VEG", "still-life", "fruit-and-vegetables",
     "Fruit & Vegetables",
     "Cut fruit, bowls and single specimens - the kitchen still life."),
    ("stilllife", "KITCHEN_TABLE", "still-life", "kitchen-and-table",
     "Kitchen & Table",
     "Boards, cloths, pots and pans, arranged flat or on a table."),
    ("stilllife", "OBJECTS", "still-life", "objects-and-curios",
     "Objects & Curios",
     "Books, lamps, baskets and made things, drawn one at a time."),
    ("stilllife", "NATURAL_OBJECTS", "still-life", "natural-objects",
     "Natural Objects",
     "Pebbles, shells, nests, cones and feathers - what you bring home from "
     "a walk."),

    # --- architecture -------------------------------------------------------
    ("architecture", "VERNACULAR", "architecture", "cottages-and-vernacular",
     "Cottages & Vernacular",
     "Flint cottages, pantile roofs, long houses and the local building "
     "traditions."),
    ("architecture", "BRITISH_STYLES", "architecture", "british-architecture",
     "British Architecture",
     "Georgian terraces, Victorian brick, Arts and Crafts, Brutalist "
     "concrete - by period and style."),
    ("architecture", "DETAILS", "architecture", "architectural-details",
     "Architectural Details",
     "Doors, windows, letter plates, gargoyles and ironwork, drawn close."),
    ("architecture", "STRUCTURES", "architecture", "bridges-and-structures",
     "Bridges & Structures",
     "Bridges, cranes, mills, weirs and lighthouses - the working "
     "structures."),
    ("architecture", "TOWNSCAPE", "architecture", "townscapes", "Townscapes",
     "Streets, mews, pier pavilions and the shape of a town."),
]

# Style axis - the techniques, in plain words a buyer searches for.
# The first two are the measured winners on the seller's own audience
# (charcoal z=+5.9, sketch z=+4.4 against a 1.05% base rate, mine_unsold.py),
# so they lead the navigation rather than sitting in alphabetical order.
STYLES = [
    ("charcoal-drawings", "Charcoal Drawings", "charcoal",
     "Soft black charcoal on paper - smudged, worked, unmistakably hand made."),
    ("pencil-sketches", "Pencil Sketches", "sketch",
     "Graphite line and hatching, left as a drawing rather than finished flat."),
    ("ink-wash", "Ink Wash", "ink_wash",
     "Diluted black ink in washes - the monochrome end of painting."),
    ("linocut-prints", "Linocut Prints", "linocut",
     "Cut-block printing: bold shapes, visible carve marks, limited colour."),
    ("screen-prints", "Screen Prints", "screenprint",
     "Flat printed colour in layers, in the poster tradition."),
    ("watercolours", "Watercolours", "watercolour",
     "Wet-on-wet washes, soft bleeds and pigment pooling at the edges."),
    ("gouache", "Gouache", "gouache",
     "Opaque matte paint - flat, chalky and saturated."),
    ("pastel", "Pastel", "pastel",
     "Dry pigment, grainy and soft-edged on toothed paper."),
    ("monotype", "Monotype", "monotype",
     "One-off press prints: inky, textured, never quite repeatable."),
    ("cyanotype", "Cyanotype", "cyanotype",
     "The Prussian-blue photographic process - white silhouettes on deep blue."),
    ("collage", "Collage", "collage",
     "Torn and cut paper, assembled in layers."),
    ("riso-prints", "Riso Prints", "risograph",
     "Duplicator printing - grainy, slightly misregistered, bright flat inks."),
    ("impasto", "Impasto", "oil_impasto",
     "Thick raised paint, built up so the surface holds the light."),
    ("palette-knife", "Palette Knife", "palette_knife",
     "Paint laid in flat blades rather than brushed."),
]

# Colour axis.
COLOURS = [
    ("black-and-white", "Black & White", "monochrome",
     "One colour and its tones. The quietest option and the easiest to hang."),
    ("neutral-and-beige", "Neutral & Beige", "neutral",
     "Cream, bone, oatmeal and stone, with at most one small warm accent."),
    ("two-tone", "Two Tone", "duotone",
     "Two colours doing all the work - graphic and calm at once."),
    ("bold-colour", "Bold Colour", "complementary",
     "Opposed colours at full strength, for a wall that needs an anchor."),
    ("colourful", "Colourful", "spectrum",
     "The full range, used across the whole picture."),
]

# Room axis. Advisory only - a suggestion of where a thing suits, never a
# claim about the product.
ROOMS = [
    ("living-room", "Living Room",
     ["british-coast", "mountains-hills", "national-parks", "british-cities",
      "british-countryside", "lakes-rivers", "trees", "world-landscapes",
      "british-architecture", "townscapes"]),
    ("bedroom", "Bedroom",
     ["the-moon", "constellations", "deep-sky", "sky-and-aurora", "planets",
      "british-wildlife", "leaves", "ferns-grasses", "butterflies"]),
    ("kitchen", "Kitchen",
     ["coffee-and-tea", "fruit-and-vegetables", "kitchen-and-table",
      "herbs-edibles", "drinks", "mushrooms-fungi"]),
    ("hallway", "Hallway",
     ["architectural-details", "cottages-and-vernacular",
      "bridges-and-structures", "islands", "natural-landmarks",
      "objects-and-curios"]),
    ("study", "Study & Office",
     ["world-birds", "freshwater-fish", "insects", "reptiles",
      "european-cities", "asia-pacific", "americas", "africa",
      "natural-objects"]),
    ("nursery", "Nursery & Child's Room",
     ["small-pets", "farm-animals", "dogs", "cats", "horses", "sea-life",
      "world-wildlife"]),
]

GOOGLE_PRODUCT_CATEGORY = "500044"  # Home & Garden > Decor > Artwork >
                                    # Posters, Prints & Visual Artwork.
                                    # Verified against Google's published
                                    # taxonomy-with-ids.en-GB.txt, 25 Oct 2026.
                                    # NOT 500045, which is Decorative
                                    # Tapestries.


def _load_groups():
    """Read the subject modules and return {subject: (section, niche)} plus
    the niche metadata, with every group named in GROUPS resolved."""
    sys.path.insert(0, os.path.join(WALLART, "subjects"))
    mods, missing = {}, []
    for name in ("creatures", "botanical", "places_uk", "places_world",
                 "celestial", "stilllife", "architecture"):
        mods[name] = __import__(name)

    subject_niche, niches = {}, {}
    for mod, listname, section, slug, title, blurb in GROUPS:
        lst = getattr(mods[mod], listname, None)
        if lst is None:
            missing.append(f"{mod}.{listname}")
            continue
        if slug not in niches:
            niches[slug] = dict(slug=slug, title=title, section=section,
                                blurb=blurb, groups=[])
        elif blurb and not niches[slug]["blurb"]:
            niches[slug]["blurb"] = blurb
        niches[slug]["groups"].append(f"{mod}.{listname}")
        for s in lst:
            # First group wins. The subject modules dedupe within themselves,
            # so a repeat here would be a cross-module repeat and is worth
            # knowing about rather than silently relabelling.
            subject_niche.setdefault(s, (section, slug))
    if missing:
        raise SystemExit(f"taxonomy: group(s) not found in subject modules: "
                         f"{missing}")
    return subject_niche, niches


SUBJECT_NICHE, NICHES = _load_groups()
STYLE_BY_TECH = {t: (s, n, b) for s, n, t, b in STYLES}
COLOUR_BY_PAL = {p: (s, n, b) for s, n, p, b in COLOURS}
NICHE_ROOMS = {}
for _slug, _title, _niches in ROOMS:
    for _n in _niches:
        NICHE_ROOMS.setdefault(_n, []).append(_slug)


def niche_for(job):
    """(section, niche slug) for a job, or None if its subject is unknown."""
    return SUBJECT_NICHE.get(job["subject"])


def product_type(job):
    """Our own category path, for the feed's [product_type]."""
    hit = niche_for(job)
    if not hit:
        return None
    section, slug = hit
    sect_title = next(t for s, t, _ in SECTIONS if s == section)
    style = STYLE_BY_TECH.get(job["tech"], (None, job["tech"], None))[1]
    return f"Wall Art > {sect_title} > {NICHES[slug]['title']} > {style}"


def check():
    """Prove every subject in every module lands in a niche. A subject that
    does not is a module extended without extending GROUPS, and that must
    stop a build rather than produce products filed nowhere."""
    sys.path.insert(0, os.path.join(WALLART, "subjects"))
    problems, total = [], 0
    for name in ("creatures", "botanical", "places_uk", "places_world",
                 "celestial", "stilllife", "architecture"):
        mod = __import__(name)
        for s in getattr(mod, "ALL", []):
            total += 1
            if s not in SUBJECT_NICHE:
                problems.append(f"{name}: {s!r} is in ALL but in no group "
                                f"named by GROUPS")
    # Every niche must be reachable from a section, and every style/colour
    # must map to a real axis value used by the generator.
    for slug, n in NICHES.items():
        if n["section"] not in [s for s, _, _ in SECTIONS]:
            problems.append(f"niche {slug}: unknown section {n['section']}")
        if not n["blurb"]:
            problems.append(f"niche {slug}: no blurb - category page would be "
                            f"thin content")
    return total, problems


if __name__ == "__main__":
    total, problems = check()
    print(f"sections {len(SECTIONS)}  niches {len(NICHES)}  "
          f"styles {len(STYLES)}  colours {len(COLOURS)}  rooms {len(ROOMS)}")
    print(f"subjects mapped: {len(SUBJECT_NICHE):,} of {total:,} in ALL")
    by_section = {}
    for n in NICHES.values():
        by_section.setdefault(n["section"], []).append(n["title"])
    for s, t, _ in SECTIONS:
        print(f"\n{t}  ({len(by_section.get(s, []))} niches)")
        print("   " + ", ".join(sorted(by_section.get(s, []))))
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems[:40]:
            print("  -", p)
        sys.exit(1)
    print("\nOK - every subject lands in exactly one niche")
    if "--json" in sys.argv:
        out = dict(sections=[dict(slug=s, title=t, kind=k)
                             for s, t, k in SECTIONS],
                   niches=NICHES,
                   styles=[dict(slug=s, title=t, tech=c, blurb=b)
                           for s, t, c, b in STYLES],
                   colours=[dict(slug=s, title=t, pal=p, blurb=b)
                            for s, t, p, b in COLOURS],
                   rooms=[dict(slug=s, title=t, niches=n) for s, t, n in ROOMS],
                   google_product_category=GOOGLE_PRODUCT_CATEGORY)
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "taxonomy.json")
        json.dump(out, open(path, "w"), indent=1)
        print(f"wrote {path}")
