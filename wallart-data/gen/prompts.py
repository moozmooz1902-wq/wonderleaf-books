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
}
GRAMMAR_PLACE = {
 "G2_terrain":   "seen across open land, the horizon pushed to the top of the picture",
 "G1_window":    "seen through a window or terrace arch framing the left and right edges",
 "G9_naive":     "as a naive flattened townscape in horizontal bands with no vanishing point",
 "G10_abstract": "as an all-over painterly abstraction, marks edge to edge, no focal point",
 "G11_hardedge": "as a hard-edge composition of circles, arcs and a horizon split in three flat colours",
}
GRAMMAR_CREATURE = {
 "G4_portrait": "head and shoulders, centred, cropped by the lower edge, direct gaze, on one flat ground",
 "G3_habitat":  "set among a dense foreground of seedheads and flowers running off every edge",
 "G8_minimal":  "small and centred on a vast expanse of plain paper",
 "G7_chart":    "as a specimen chart of nine simplified studies on one flat warm ground",
}
PALETTE = {
 "duotone":       "two adjacent colours only",
 "complementary": "burnt orange against petrol blue",
 "neutral":       "cream, bone and oatmeal with one small rust accent",
}
# Not every technique suits every grammar. A hard-edge composition of flat
# colour cannot be a wet-on-wet watercolour, and a specimen chart of nine
# studies is a drawing convention, not an impasto one. Generating the
# contradictions wastes GPU and produces mush, so they are excluded.
FLAT = {"screenprint", "collage", "gouache", "palette_knife", "linocut"}
DRAWN = {"charcoal", "sketch", "linocut", "ink_wash", "pastel"}
INCOMPATIBLE = {
    "G11_hardedge": lambda t: t not in FLAT,       # needs flat hard-edged colour
    "G10_abstract": lambda t: t in {"charcoal", "sketch"},   # abstraction needs mass
    "G7_chart":     lambda t: t not in DRAWN,      # a chart is a drawing convention
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


def ok(tech, gram, subject=None):
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


def place_prompt(place, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of {place}, {GRAMMAR_PLACE[gram]}, "
            f"{PALETTE[pal]}, {RULES}")


def creature_prompt(name, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of a {name}, {GRAMMAR_CREATURE[gram]}, "
            f"{PALETTE[pal]}, {EYES}, {RULES_CREATURE}")


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
