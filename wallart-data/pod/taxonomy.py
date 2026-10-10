#!/usr/bin/env python3
"""Zero-shot label axes for scoring competitor art with CLIP.

Each axis is scored independently with a softmax inside the axis, so an image
gets a technique AND a grammar AND a colour strategy, rather than one label
from a flat list of two hundred.

The technique prompts name the physical artefact, not the style name. That is
straight out of our own research finding: "naming the style is useless to a
diffusion model, naming the physical artefact is what works, because the
artefact is what the model has seen." The same holds for reading images back.
"""

AXES = {
 # the eleven techniques from the grammar notes, plus the non-painting ones
 # that a real catalogue is full of and the notes had no name for
 "technique": {
  "contour_hatching": "a drawing filled with dense parallel hatching lines running along the slope of each form",
  "palette_knife":    "a palette knife painting of angular facets with hard straight edges and no outlines",
  "art_nouveau_gouache": "a flat gouache illustration where every shape is outlined with a dark contour line",
  "fauvist_gouache":  "a fauvist painting with unmixed colour, visible separate strokes and coloured violet shadows",
  "watercolour":      "a wet-on-wet watercolour with soft bleeds, blooms and pigment pooling at the edge of the wash",
  "linocut":          "a two-tone linocut print where white gouge marks cut through flat black ink",
  "paper_collage":    "a cut paper collage of flat torn-edge shapes layered in planes",
  "oil_impasto":      "a thick oil painting with visible impasto ridges and brush drag",
  "crayon_pastel":    "a soft pastel or crayon drawing with visible grain and scribbly open fill",
  "ink_wash":         "a black ink wash painting with hard dry edges and splatter dots",
  "photochrom":       "a hand-tinted vintage photograph with faded colour, grain and an aged cream border",
  "photograph":       "a colour photograph",
  "vector_flat":      "a flat vector graphic with perfectly clean hard edges and no texture",
  "digital_3d":       "a glossy three-dimensional computer rendering",
  "pencil_graphite":  "a detailed graphite pencil drawing in grey tones",
  "oil_classical":    "an old master oil painting on canvas with varnish and craquelure",
  "line_art":         "a single continuous thin black line drawing on a plain ground",
  "risograph":        "a risograph print with misregistered flat ink layers and visible halftone dots",
 },
 # the eleven composition grammars, each a kind of picture rather than a subject
 "grammar": {
  "G1_framed_view":    "a view looking out through a window or terrace arch, the opening framing the left and right edges",
  "G2_pure_terrain":   "a landscape of nothing but land, the horizon pushed right to the top of the picture",
  "G3_hero_habitat":   "one animal perched high on a dense foreground of flowers and seedheads running off every edge",
  "G4_portrait_bust":  "a single creature centred, cropped by the bottom edge, looking straight at the viewer, on one flat colour",
  "G5_flat_lay":       "an overhead flat lay of a few objects on a patterned tablecloth, no horizon and no depth",
  "G6_poster_margin":  "an art panel inset inside a wide cream margin with text set in the margin",
  "G7_specimen_chart": "a grid chart of nine or twelve small simplified specimens on one flat warm background",
  "G8_minimal_object": "one small object in ink on a vast expanse of white paper with a line of spaced capitals beneath",
  "G9_naive_cityscape":"a naive flattened city of horizontal bands with no vanishing point and flowers floating in the sky",
  "G10_allover_abstract":"an all-over painterly abstraction with marks edge to edge and no focal point or horizon",
  "G11_hardedge_geometric":"a hard-edge geometric composition of circles arcs and half discs in three flat colours",
 },
 "colour_strategy": {
  "C1_complementary":  "a picture carried by one complementary pair, burnt orange against petrol blue",
  "C2_neutral_accent": "a warm neutral picture of cream bone and oatmeal with one small hot rust accent",
  "C3_full_spectrum":  "a picture using every hue at the same saturation over one pale dominant ground",
  "C4_monochrome":     "a black and white picture with no colour at all",
  "C5_duotone":        "a picture printed in only two flat ink colours",
 },
 "subject": {
  "bird": "a bird", "cat": "a cat", "dog": "a dog", "horse": "a horse",
  "wild_mammal": "a wild mammal such as a bear fox deer or lion",
  "sea_creature": "a whale, fish or other sea creature",
  "insect_butterfly": "a butterfly, bee or other insect",
  "flower_botanical": "flowers or a botanical plant specimen",
  "tree_forest": "trees or a forest",
  "mountain_landscape": "a mountain landscape", "coast_sea": "a coastline or the sea",
  "field_countryside": "fields and open countryside", "desert": "a desert",
  "city_skyline": "a city skyline or cityscape", "building_architecture": "a single building or piece of architecture",
  "street_scene": "a street scene", "interior_room": "the inside of a room",
  "map": "a map", "person_portrait": "a portrait of a person", "figure_body": "a human figure or body",
  "nude": "a nude figure", "food": "food", "drink_cocktail": "a cocktail, wine or other drink",
  "vehicle_car": "a car or motorcycle", "aircraft": "an aeroplane", "boat_ship": "a boat or ship",
  "space_astronomy": "space, planets or the night sky", "moon_phases": "phases of the moon",
  "abstract_shapes": "abstract shapes with no subject", "pattern_repeat": "a repeating pattern",
  "typography_only": "nothing but words and letters", "sport": "a sport being played",
  "music_instrument": "a musical instrument", "fashion_clothing": "clothing or fashion",
  "still_life_objects": "a still life of household objects", "anatomy": "an anatomical diagram",
  "mythology_fantasy": "a mythological or fantasy scene", "religious": "a religious image",
  "dinosaur": "a dinosaur", "zodiac_celestial": "a zodiac or celestial chart",
 },
 "text": {
  "no_text":      "a picture with no words anywhere in it",
  "small_caption":"a picture with one small line of text underneath",
  "text_led":     "a design that is mostly large words",
 },
 "ground": {
  "white_paper":  "a subject on plain white paper with a wide empty margin",
  "flat_colour":  "a subject on a single flat colour background",
  "full_bleed":   "an image that fills the whole area edge to edge with no margin",
  "textured":     "a subject on a visibly textured or patterned background",
 },
 "register": {
  "calm_neutral": "a calm, quiet, muted picture for a tasteful interior",
  "bold_graphic": "a bold loud high-contrast graphic poster",
  "cute_childlike":"a cute childlike illustration for a nursery",
  "vintage_aged": "an aged vintage print with faded ink and foxed paper",
  "luxury_gold":  "an opulent picture with gold and marble",
  "dark_moody":   "a dark moody picture with deep shadow",
 },
}

def prompts():
    """Flat (axis, key, text) in a stable order."""
    out = []
    for axis, d in AXES.items():
        for k, v in d.items():
            out.append((axis, k, v))
    return out
