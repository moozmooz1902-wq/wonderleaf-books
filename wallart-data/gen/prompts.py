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
 "G6_poster":    "as a vintage travel poster, the scene inset inside a wide cream margin",
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


def ok(tech, gram, subject=None):
    rule = INCOMPATIBLE.get(gram)
    if rule and rule(tech):
        return False
    if gram == "G3_habitat" and subject and subject not in PERCHING:
        return True          # wording is generic now, so this is fine either way
    return True


RULES = ("flat fill, no gradient, no airbrushing, "
         "the subject sharp and the surroundings flat, "
         "no text, no lettering, no words, no signature, no watermark")


def place_prompt(place, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of {place}, {GRAMMAR_PLACE[gram]}, "
            f"{PALETTE[pal]}, {RULES}")


def creature_prompt(name, tech, gram, pal):
    return (f"{TECHNIQUE[tech]} of a {name}, {GRAMMAR_CREATURE[gram]}, "
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
