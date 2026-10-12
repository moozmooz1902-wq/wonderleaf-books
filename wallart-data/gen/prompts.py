#!/usr/bin/env python3
"""Build generation prompts from the measured spec.

Every element traces to research_notes/Wall art catalogue taxonomy harvest/:
  - techniques name the physical artefact, not the style, per the_grammar_of_what_sells
  - the grammars are the eleven composition kinds from the same note
  - charcoal and sketch lead because they are the only techniques beating the
    seller's 1.05% base watch rate (first_party_demand_watchers)
  - palettes are the measured strategy mix, not the eleven-image guess the
    early grammar note made (measured_colour_and_style)
  - "no text, no lettering" sits in the POSITIVE prompt because FLUX schnell at
    guidance_scale 0 ignores negative prompts; the OCR gate is what enforces it
"""
import itertools, json, random

TECHNIQUE = {
 "charcoal":      "charcoal and graphite drawing, visible paper grain, loose open hatching",
 "sketch":        "loose pencil sketch, visible construction lines, soft graphite shading",
 "linocut":       "two-tone linocut print, white gouge marks cutting through flat ink, chatter and speckle",
 "watercolour":   "wet-on-wet watercolour, soft bleeds and blooms, pigment pooling at the edge of the wash",
 "gouache":       "flat gouache illustration, every shape outlined with a dark contour line",
 "oil_impasto":   "thick oil painting, visible impasto ridges and brush drag",
 "palette_knife": "palette knife painting, angular facets with hard straight edges, no outlines",
 "ink_wash":      "black ink wash painting, hard dry edges, deliberate splatter dots",
 "pastel":        "soft pastel drawing, visible grain, scribbly open fill",
 "collage":       "cut paper collage, flat torn-edge shapes layered in planes",
 "screenprint":   "flat screen-printed poster, simplified geometric shapes, bold flat colour",
 # Added 11 Oct 2026 to widen the grid without leaning harder on any one
 # subject. Each names a physical artefact nobody else in the measured
 # competitor corpus is printing much of, and each looks unmistakably unlike
 # the eleven above - which is the point, since the duplicate audit showed
 # near-twins come from shared COMPOSITION, not from shared subject.
 "risograph":     "two-colour risograph print, layers slightly misregistered, coarse halftone dot grain, flat ink",
 "monotype":      "monotype print pulled from an inked plate, the plate wiped back, soft blurred edges and plate tone",
 "cyanotype":     "cyanotype photogram, Prussian blue ground with white silhouettes, uneven brushed edges",
}
GRAMMAR_PLACE = {
 "G2_terrain":   "seen across open land, the horizon pushed to the top of the picture",
 "G1_window":    "seen through a window or terrace arch framing the left and right edges",
 "G9_naive":     "as a naive flattened townscape in horizontal bands with no vanishing point",
 # Reworded 12 Oct. The old wording was "as an all-over painterly
 # abstraction, marks edge to edge, no focal point", which removes the
 # subject from the picture by instruction - so the subject axis contributed
 # nothing and every place collapsed to the same beige field. The audit found
 # Topsham, Split, Bidean nam Bian, Fowey, Curbar Edge, Dungeness and Saltash
 # all within 8 bits of each other, three of them IDENTICAL. The abstraction
 # now has to be derived from the place rather than replace it.
 "G10_abstract": "as an all-over painterly abstraction built from the colours and shapes of the place itself, marks edge to edge, no focal point",
 "G11_hardedge": "as a hard-edge composition of circles, arcs and a horizon split in three flat colours",
}
GRAMMAR_CREATURE = {
 "G4_portrait": "head and shoulders, centred, cropped by the lower edge, direct gaze, on one flat ground",
 "G3_habitat":  "set among a dense foreground of seedheads and flowers running off every edge",
 "G8_minimal":  "small and centred on a vast expanse of plain paper",
 "G7_chart":    "as a specimen chart of nine simplified studies on one flat warm ground",
}
# Botanical is not a minor block. In the mined competitor titles the single
# biggest group of subject atoms after people is flowers - anemone, daisies,
# dahlia, tulips, orchid, rose, peony, hydrangea, ranunculus, sunflower - and
# people are ruled out, so this is the largest block available.
GRAMMAR_BOTANICAL = {
 "B1_specimen":  "a single stem laid flat and centred like a pressed herbarium specimen, on plain paper",
 "B2_vase":      "arranged loosely in a simple ceramic vase on a plain ground, the vase cropped by the lower edge",
 "B3_scatter":   "several cuttings scattered evenly across the sheet with space between them",
 "B4_meadow":    "growing in a dense band across the lower half, stems running off both edges",
 "B5_single":    "one bloom, very large, filling most of the sheet, cropped by the edges",
}
# Three blocks added 11 Oct 2026. The three kinds above are 2,238 subjects and
# 284,665 base images; five million listings needs about a million bases, and
# padding the place list with obscure towns is the wrong way to get there
# because FLUX has no idea what Tipton looks like and renders a generic
# British town - three hundred of which would be three hundred near-twins.
# Celestial, still life and architecture are things the model genuinely
# knows apart, they are enumerable and IP-free, and each is a block the
# measured competitor corpus sells and this catalogue had none of.
GRAMMAR_CELESTIAL = {
 "C1_vast":     "a vast empty night sky filling the sheet, the land a thin dark band at the foot",
 "C2_disc":     "one large disc centred on a plain flat ground, nothing else in the picture",
 "C3_row":      "as a row of three simplified studies across the middle of the sheet",
 "C4_overland": "above a simplified dark landscape silhouette along the lower third",
}
GRAMMAR_STILLLIFE = {
 "S1_table":   "arranged on a plain table top seen from slightly above, cropped by the lower edge",
 "S2_single":  "one object, very large and centred, on a flat plain ground",
 "S3_flatlay": "laid out flat and seen from directly above on a plain ground",
 "S4_shelf":   "lined up along a single shelf running the full width of the sheet",
}
GRAMMAR_ARCH = {
 "A1_elevation": "drawn flat as a straight-on elevation, centred on plain paper",
 "A2_street":    "in a row of simplified facades across the lower half, no vanishing point",
 "A3_detail":    "one architectural detail very large and cropped by every edge",
 "A4_wide":      "small in a wide empty landscape with the horizon low",
}
# measured_colour_and_style.md counted the colour strategy of thousands of
# competitor images, and the first three here were built from it: duotone or
# analogous 33%, complementary 14%, warm neutral plus accent 2.5%.
#
# The two added on 11 Oct close the gap that count exposed. MONOCHROME is
# 21-23% of the market - one competitor image in five is essentially
# colourless - and it was missing from this grid entirely, which is a strange
# thing to leave out when charcoal and sketch are also the only two
# techniques beating the seller's own base watch rate. FULL SPECTRUM is 30%
# and was also absent. Between them they were 51% of what sells and 0% of
# what we were making.
PALETTE = {
 "duotone":       "two adjacent colours only",
 "complementary": "burnt orange against petrol blue",
 "neutral":       "cream, bone and oatmeal with one small rust accent",
 "monochrome":    "no colour at all, warm charcoal black on cream paper",
 "spectrum":      "a full spectrum of saturated colour, many hues at once",
}
# Not every technique suits every grammar. A hard-edge composition of flat
# colour cannot be a wet-on-wet watercolour, and a specimen chart of nine
# studies is a drawing convention, not an impasto one. Generating the
# contradictions wastes GPU and produces mush, so they are excluded.
FLAT = {"screenprint", "collage", "gouache", "palette_knife", "linocut",
        "risograph", "cyanotype"}
DRAWN = {"charcoal", "sketch", "linocut", "ink_wash", "pastel", "monotype"}
# A technique can contradict a palette as flatly as it contradicts a
# composition, and generating the contradiction wastes a GPU-second and
# produces mush. A cyanotype is Prussian blue by chemistry - that is what
# the process IS - so it is only asked for in the two palettes that can
# hold it. Nothing that is black ink or bare graphite by definition is
# asked for in full spectrum.
# Cyanotype is Prussian blue and white by chemistry, so it is only asked
# for in the one palette that does not argue with it. The monochrome
# palette says "warm charcoal black on cream paper", which is a
# different process entirely.
PAL_ONLY = {"cyanotype": {"duotone"}}
# Compositions that must not meet the neutral palette. Measured on 63,533
# live panels: the near-duplicate cluster was almost entirely
# G10_abstract and G8_minimal in "cream, bone and oatmeal", and the reason
# is plain once seen. Both compositions deliberately suppress detail, and
# the neutral palette suppresses contrast, so what is left is a pale sheet
# with very little in it - and a 256-bit gradient hash cannot tell two pale
# sheets apart, which is also the point: neither can a buyer scrolling eBay.
# The compositions still run in the other four palettes.
GRAM_NOT_PAL = {("G10_abstract", "neutral"), ("G8_minimal", "neutral"),
                ("B1_specimen", "neutral")}
NO_SPECTRUM = {"charcoal", "sketch", "ink_wash", "cyanotype"}
INCOMPATIBLE = {
    "G11_hardedge": lambda t: t not in FLAT,       # needs flat hard-edged colour
    "G10_abstract": lambda t: t in {"charcoal", "sketch"},   # abstraction needs mass
    "G7_chart":     lambda t: t not in DRAWN,      # a chart is a drawing convention
    "B1_specimen":  lambda t: t not in DRAWN,      # a herbarium sheet is drawn
}
# a few grammars read oddly on large animals
PERCHING = {"barn owl", "european robin", "kingfisher", "puffin", "goldfinch",
            "wren", "blue tit", "bullfinch", "swallow", "kestrel"}

# Measured on 93 creature panels, 11 Oct 2026: 7 came out with the eyes wrong.
# Four of the seven were robins and five of the seven were wet painterly
# techniques. A small bird's face is only a few dozen pixels across, and a
# wet-on-wet wash is exactly the technique that will not hold an eye at that
# size. The combination is a tiny slice of the catalogue, so it is simply not
# generated: no close-up portrait of a small-faced bird in a wet technique.
SMALL_FACED = {"european robin", "wren", "blue tit", "goldfinch", "bullfinch",
               "chaffinch", "swallow", "kingfisher", "great tit", "nuthatch",
               "long-tailed tit", "sparrow", "dunnock", "siskin", "linnet"}
WET = {"oil_impasto", "watercolour", "ink_wash", "palette_knife", "pastel"}


def pal_ok(tech, pal):
    allow = PAL_ONLY.get(tech)
    if allow is not None and pal not in allow:
        return False
    if pal == "spectrum" and tech in NO_SPECTRUM:
        return False
    return True


def ok(tech, gram, subject=None, pal=None):
    if pal is not None and not pal_ok(tech, pal):
        return False
    if pal is not None and (gram, pal) in GRAM_NOT_PAL:
        return False
    rule = INCOMPATIBLE.get(gram)
    if rule and rule(tech):
        return False
    if gram == "G4_portrait" and tech in WET and subject in SMALL_FACED:
        return False
    if gram == "G3_habitat" and subject and subject not in PERCHING:
        return True          # wording is generic now, so this is fine either way
    return True


# G6_poster, "as a vintage travel poster", was removed on 11 Oct 2026. It was
# the single biggest source of lettering - a vintage travel poster IS a piece
# of typography, so the model put a place name across it however the rules
# were worded. Of the five defective panels in the first sample of sixteen,
# the worst two came from it.
#
# These words sit in the POSITIVE prompt because schnell runs at
# guidance_scale 0 and ignores the negative prompt entirely. They help a
# little and are not a gate; gen_gated.py reading the output is the gate.
# NO PEOPLE. The seller's rule, 11 Oct 2026: human figures and human faces
# are where generated work looks generated, and a half-formed face in a
# harbour scene is worse than no figure at all. Nothing in the subject lists
# is a person, but villages, seafronts and terraces invite staffage, so it is
# said explicitly and quality_gate.py checks the output as well.
NO_PEOPLE = ("no people, no person, no human figures, no faces, "
             "no crowds, deserted and empty of people")
# A creature portrait must NOT be told "no faces" - that is the subject. The
# animal variant names humans only.
NO_PEOPLE_CREATURE = "no people, no human figures, no hands, animal only"

_CLEAN = ("no text, no lettering, no words, no letters, no numbers, "
         "no signature, no handwriting, no monogram, no watermark, "
          "unsigned, clean empty corners")

RULES = ("flat fill, no gradient, no airbrushing, "
         "the subject sharp and the surroundings flat, "
         + NO_PEOPLE + ", " + _CLEAN)
RULES_CREATURE = ("flat fill, no gradient, no airbrushing, "
                  "the subject sharp and the surroundings flat, "
                  + NO_PEOPLE_CREATURE + ", " + _CLEAN)

# Eyes are the other giveaway, and only creatures have them. Asking for them
# plainly and once beats any amount of negative wording, which schnell
# ignores at guidance_scale 0.
EYES = ("exactly two eyes, both eyes clear and correctly placed, "
        "clean simple eyes")

# Creatures that HAVE NO FACE, and what asking for eyes anyway produced.
#
# The eyes clause was being applied to every creature, and FLUX did as it
# was told: a sea anemone with two human eyes, a fan coral with two eyes, a
# limpet with cartoon eyes, a chambered nautilus with two big ones, krill
# and an aphid colony as geometric blobs with eyes. Measured on 1,609
# creature panels, these were most of the worst-scoring ones. Nothing was
# wrong with the model; the prompt asked for eyes on an animal that has
# none.
#
# Matched on words rather than listed by name, because the subject lists
# will keep growing and a name list would quietly stop covering them.
NO_FACE_WORDS = (
    "coral", "anemone", "sponge", "jellyfish", "man o war", "comb jelly",
    "salp", "krill", "plankton", "barnacle", "urchin", "sand dollar",
    "starfish", "sea star", "brittle star", "basket star", "feather star",
    "sea cucumber", "sea squirt", "tube worm", "tube worms",
    "barnacles", "christmas tree worm",
    "earthworm", "aphid colony", "limpet", "periwinkle", "mussel", "scallop",
    "oyster", "cockle", "razor clam", "whelk", "snail shell", "nautilus",
    "sea slug", "nudibranch", "sea hare", "mermaid's purse", "egg case",
    "kelp", "sea grass", "seagrass", "stonewort", "maerl", "slime mould",
    "lichen", "wasp nest", "honeycomb", "bird's nest", "fossil", "ammonite",
    "trilobite", "shell",
)


# Things that CONTAIN one of those words and plainly do have a face. Plain
# substring matching put the no-eyes wording on an oystercatcher, a
# tortoiseshell cat, a barnacle goose and an australian kelpie. Word
# boundaries fix three of those on their own - "oyster" does not end a word
# inside "oystercatcher", nor "shell" inside "tortoiseshell", nor "kelp"
# inside "kelpie" - and the goose needs saying.
FACE_ANYWAY = ("barnacle goose", "oystercatcher", "shellduck", "shelduck",
               "coral snake")   # a snake, and it has a face
_NO_FACE_RX = None


def has_face(subject):
    global _NO_FACE_RX
    s = (subject or "").lower()
    if any(x in s for x in FACE_ANYWAY):
        return True
    if _NO_FACE_RX is None:
        import re as _re
        _NO_FACE_RX = _re.compile(
            r"\b(" + "|".join(_re.escape(w) for w in NO_FACE_WORDS) + r")\b")
    return not _NO_FACE_RX.search(s)


# What to say instead. Saying nothing is not enough - "animal only" and a
# portrait grammar still invite a face - so it is said plainly.
NO_EYES = ("no face, no eyes, no features added, "
           "the natural form only")


def place_prompt(place, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of {place}, {GRAMMAR_PLACE[gram]}, "
            f"{PALETTE[pal]}, {RULES}")


def botanical_prompt(name, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of {name}, {GRAMMAR_BOTANICAL[gram]}, "
            f"{PALETTE[pal]}, {RULES}")


def creature_prompt(name, tech, gram, pal):
    eyes = EYES if has_face(name) else NO_EYES
    return (f"{TECHNIQUE[tech]} of a {name}, {GRAMMAR_CREATURE[gram]}, "
            f"{PALETTE[pal]}, {eyes}, {RULES_CREATURE}")


def celestial_prompt(name, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of {name}, {GRAMMAR_CELESTIAL[gram]}, "
            f"{PALETTE[pal]}, {RULES}")


def stilllife_prompt(name, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of {name}, {GRAMMAR_STILLLIFE[gram]}, "
            f"{PALETTE[pal]}, {RULES}")


def architecture_prompt(name, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of {name}, {GRAMMAR_ARCH[gram]}, "
            f"{PALETTE[pal]}, {RULES}")


def build(places, creatures, limit=None, seed=11):
    """Deterministic, and shuffled so any prefix is a fair sample of the whole."""
    jobs = []
    dropped = 0
    for p, t, g, c in itertools.product(places, TECHNIQUE, GRAMMAR_PLACE, PALETTE):
        if not ok(t, g, p):
            dropped += 1; continue
        jobs.append({"kind": "place", "subject": p, "tech": t, "gram": g, "pal": c,
                     "prompt": place_prompt(p, t, g, c)})
    for s, t, g, c in itertools.product(creatures, TECHNIQUE, GRAMMAR_CREATURE, PALETTE):
        if not ok(t, g, s):
            dropped += 1; continue
        jobs.append({"kind": "creature", "subject": s, "tech": t, "gram": g, "pal": c,
                     "prompt": creature_prompt(s, t, g, c)})
    build.dropped = dropped
    random.Random(seed).shuffle(jobs)
    for i, j in enumerate(jobs):
        j["sku"] = "WA-%07d" % i
    return jobs[:limit] if limit else jobs


if __name__ == "__main__":
    import sys
    PL = ["Snowdonia", "the Lake District", "Whitby harbour", "Sheffield",
          "the Cotswolds", "Hope Cove Devon", "Loch Lomond", "Pembrokeshire coast"]
    CR = ["border collie", "red fox", "barn owl", "highland cow",
          "puffin", "european robin", "brown hare", "kingfisher"]
    jobs = build(PL, CR, limit=int(sys.argv[1]) if len(sys.argv) > 1 else 12)
    json.dump(jobs, open(sys.argv[2], "w"), indent=1) if len(sys.argv) > 2 else None
    for j in jobs[:6]:
        print(f"[{j['sku']}] {j['kind']:<8} {j['tech']:<13} {j['gram']}")
        print(f"    {j['prompt'][:150]}")
