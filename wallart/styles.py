"""Visual building blocks: named colourways, font pairings, layouts, ornaments.

Every design is phrase + palette + fonts + layout + ornament. The palette NAME goes
into the listing title, because decor buyers search by colour ("sage green kitchen
print") - so each palette carries the words a buyer would type.
"""

# id: (title words, background, ink, accent)
# INK SAVING: every design prints on a WHITE background with black or one dark
# text colour. Dark or coloured backgrounds are gone - full-bleed colour costs
# far more ink than text does. The accent colour is only used for small
# ornaments and the script accent word.
PALETTES = {
    "bw":         ("Black and White", "#FFFFFF", "#111111", "#111111"),
    "bwgrey":     ("Black and Grey",  "#FFFFFF", "#111111", "#8C8C8C"),
    "gold":       ("Black and Gold",  "#FFFFFF", "#111111", "#B08D3C"),
    "sage":       ("Sage Green",      "#FFFFFF", "#3F5446", "#7E9A82"),
    "forest":     ("Forest Green",    "#FFFFFF", "#23392D", "#5E7F63"),
    "olive":      ("Olive Green",     "#FFFFFF", "#4F4F2A", "#8A8A55"),
    "navy":       ("Navy Blue",       "#FFFFFF", "#1F2A44", "#5C6F93"),
    "teal":       ("Teal",            "#FFFFFF", "#1E5E5E", "#4E9A96"),
    "duckegg":    ("Duck Egg Blue",   "#FFFFFF", "#2E4A4E", "#7FAAA9"),
    "terracotta": ("Terracotta",      "#FFFFFF", "#9B4A2E", "#C9724F"),
    "rust":       ("Burnt Orange",    "#FFFFFF", "#A7461F", "#D9824F"),
    "mustard":    ("Mustard Yellow",  "#FFFFFF", "#2A2419", "#D9A21E"),
    "blush":      ("Blush Pink",      "#FFFFFF", "#5B3A3A", "#C98C8C"),
    "burgundy":   ("Burgundy",        "#FFFFFF", "#5E1F2B", "#A0525F"),
    "plum":       ("Plum",            "#FFFFFF", "#4B2142", "#8E5A84"),
    "lilac":      ("Lilac",           "#FFFFFF", "#4A3D5C", "#9B87B5"),
    "charcoal":   ("Charcoal Grey",   "#FFFFFF", "#3A3B3D", "#8A8A8A"),
    "cocoa":      ("Brown",           "#FFFFFF", "#4A3527", "#9C7A5B"),
    "pastel":     ("Pastel",          "#FFFFFF", "#5E5A7A", "#E9A6A6"),
    "rainbow":    ("Rainbow",         "#FFFFFF", "#3C3C58", "#E07A5F"),
}
RAINBOW = ["#E07A5F", "#F2CC8F", "#81B29A", "#3D85C6", "#9B72CF"]

# which palettes suit which niche mood - the generator draws from these.
# Black comes first everywhere: it is the cheapest to print and the most searched.
PALETTE_MOODS = {
    "rustic":  ["bw", "cocoa", "sage", "forest", "terracotta", "olive", "charcoal"],
    "bold":    ["bw", "navy", "charcoal", "rust", "teal", "forest", "gold"],
    "retro":   ["bw", "rust", "mustard", "teal", "terracotta", "navy", "olive", "burgundy"],
    "script":  ["bw", "blush", "sage", "navy", "plum", "lilac", "duckegg", "gold"],
    "elegant": ["bw", "gold", "navy", "sage", "forest", "burgundy", "charcoal", "bwgrey"],
    "minimal": ["bw", "bwgrey", "charcoal", "sage", "cocoa", "blush"],
    "modern":  ["bw", "charcoal", "terracotta", "navy", "sage", "bwgrey"],
    "vintage": ["bw", "cocoa", "navy", "forest", "burgundy", "olive", "gold"],
    "playful": ["bw", "rainbow", "teal", "blush", "mustard", "rust", "pastel"],
    "kids":    ["bw", "pastel", "rainbow", "duckegg", "blush", "sage", "lilac"],
    "sacred":  ["bw", "gold", "navy", "sage", "blush", "forest", "cocoa"],
    "celtic":  ["bw", "forest", "sage", "navy", "cocoa"],
    "geometric": ["bw", "gold", "navy", "teal", "forest", "sage"],
    "industrial": ["bw", "charcoal", "rust", "cocoa", "bwgrey"],
}

# (main face, main variation, accent script face, small face, small variation)
FONTSETS = {
    "classic_serif": ("PlayfairDisplay.ttf", "Bold", "GreatVibes.ttf", "Montserrat.ttf", "Medium"),
    "didone":        ("DMSerifDisplay.ttf", None, "Allura.ttf", "Raleway.ttf", "Medium"),
    "fat_face":      ("AbrilFatface.ttf", None, "Sacramento.ttf", "JosefinSans.ttf", "SemiBold"),
    "roman":         ("Cinzel.ttf", "Bold", "GreatVibes.ttf", "CormorantGaramond.ttf", "SemiBold"),
    "garamond":      ("CormorantGaramond.ttf", "Bold", "DancingScript.ttf", "CormorantGaramond.ttf", "Medium"),
    "yeseva":        ("YesevaOne.ttf", None, "Satisfy.ttf", "Montserrat.ttf", "Regular"),
    "condensed":     ("BebasNeue.ttf", None, "Pacifico.ttf", "Oswald.ttf", "Regular"),
    "anton":         ("Anton.ttf", None, "Satisfy.ttf", "Oswald.ttf", "Light"),
    "oswald":        ("Oswald.ttf", "Bold", "DancingScript.ttf", "Oswald.ttf", "Light"),
    "geometric":     ("Montserrat.ttf", "ExtraBold", "Sacramento.ttf", "Montserrat.ttf", "Light"),
    "spartan":       ("LeagueSpartan.ttf", "Bold", "Allura.ttf", "LeagueSpartan.ttf", "Light"),
    "josefin":       ("JosefinSans.ttf", "Bold", "GreatVibes.ttf", "JosefinSans.ttf", "Light"),
    "raleway":       ("Raleway.ttf", "Black", "DancingScript.ttf", "Raleway.ttf", "Light"),
    "slab":          ("AlfaSlabOne.ttf", None, "Pacifico.ttf", "Oswald.ttf", "Regular"),
    "western":       ("Rye.ttf", None, "Satisfy.ttf", "SpecialElite.ttf", None),
    "typewriter":    ("SpecialElite.ttf", None, "Caveat.ttf", "SpecialElite.ttf", None),
    "deco":          ("Limelight.ttf", None, "GreatVibes.ttf", "PoiretOne.ttf", None),
    "poiret":        ("PoiretOne.ttf", None, "Allura.ttf", "PoiretOne.ttf", None),
    "script_lead":   ("Pacifico.ttf", None, "Pacifico.ttf", "Montserrat.ttf", "Medium"),
    "lobster":       ("Lobster.ttf", None, "Lobster.ttf", "Raleway.ttf", "Medium"),
    "dancing":       ("DancingScript.ttf", "Bold", "DancingScript.ttf", "JosefinSans.ttf", "Regular"),
    "handwritten":   ("AmaticSC.ttf", None, "Caveat.ttf", "AmaticSC.ttf", None),
    "marker":        ("PermanentMarker.ttf", None, "Caveat.ttf", "Caveat.ttf", "Bold"),
    "kids_round":    ("Fredoka.ttf", "Bold", "Chewy.ttf", "Fredoka.ttf", "Medium"),
    "kids_chewy":    ("Chewy.ttf", None, "Pacifico.ttf", "Fredoka.ttf", "Medium"),
    "kids_lucky":    ("LuckiestGuy.ttf", None, "Chewy.ttf", "Fredoka.ttf", "Medium"),
    "blackletter":   ("UnifrakturMaguntia.ttf", None, "GreatVibes.ttf", "CormorantGaramond.ttf", "SemiBold"),
    "italic_serif":  ("PlayfairDisplayItalic.ttf", "Bold Italic", "Allura.ttf", "Montserrat.ttf", "Regular"),
}

FONT_MOODS = {
    "rustic":  ["handwritten", "slab", "typewriter", "classic_serif", "condensed", "dancing", "western"],
    "bold":    ["condensed", "anton", "geometric", "slab", "spartan", "fat_face", "oswald"],
    "retro":   ["slab", "lobster", "script_lead", "western", "fat_face", "deco", "condensed"],
    "script":  ["dancing", "script_lead", "classic_serif", "didone", "italic_serif", "lobster"],
    "elegant": ["classic_serif", "didone", "roman", "garamond", "yeseva", "poiret", "italic_serif"],
    "minimal": ["josefin", "raleway", "geometric", "poiret", "garamond", "spartan"],
    "modern":  ["geometric", "spartan", "josefin", "anton", "raleway", "condensed"],
    "vintage": ["roman", "typewriter", "deco", "western", "classic_serif", "slab"],
    "playful": ["kids_round", "marker", "lobster", "script_lead", "kids_chewy", "handwritten"],
    "kids":    ["kids_round", "kids_chewy", "kids_lucky", "script_lead", "marker"],
    "sacred":  ["roman", "garamond", "classic_serif", "didone", "italic_serif", "dancing"],
    "celtic":  ["roman", "garamond", "blackletter", "classic_serif"],
    "geometric": ["roman", "poiret", "josefin", "garamond", "didone"],
    "industrial": ["condensed", "anton", "slab", "typewriter", "oswald"],
}

# "block" (solid colour half-page) was removed to save ink
LAYOUTS = ["stack", "subway", "left", "frame", "rules", "arch", "badge", "ribbon", "corner"]

# ornaments suited to each niche; "none" keeps pure type in the mix
ORNAMENTS = {
    "coffee_cafe": ["cup", "beans", "stars", "lines", "none"],
    "kitchen": ["whisk", "heart", "leaf", "lines", "none"],
    "bar_pub": ["glass", "stars", "lines", "sun", "none"],
    "motivation": ["arrow", "sparkle", "lines", "sun", "none"],
    "proverbs_classics": ["laurel", "lines", "diamond", "none"],
    "faith_christian": ["cross", "dove", "laurel", "sun", "heart", "none"],
    "scripture": ["cross", "laurel", "leaf", "lines", "none"],
    "faith_blessings": ["knot", "laurel", "heart", "leaf", "none"],
    "faith_islamic": ["crescent", "star8", "lantern", "diamond", "none"],
    "faith_dharmic": ["lotus", "sun", "dots", "diamond", "none"],
    "home_family": ["heart", "house", "leaf", "laurel", "none"],
    "personalised_family": ["heart", "laurel", "house", "lines", "none"],
    "wedding_love": ["heart", "rings", "laurel", "sparkle", "none"],
    "nursery_kids": ["stars", "moon", "rainbow", "cloud", "heart"],
    "classroom": ["pencil", "stars", "rainbow", "heart", "sparkle"],
    "bathroom": ["bubbles", "drop", "lines", "stars", "none"],
    "laundry_utility": ["sock", "bubbles", "lines", "none"],
    "garden_outdoor": ["leaf", "flower", "sun", "bee", "none"],
    "man_cave": ["stars", "lines", "wrench", "bolt", "none"],
    "hobbies": ["stars", "lines", "sun", "none"],
    "pets": ["paw", "heart", "bone", "none"],
    "office_work": ["arrow", "lines", "sparkle", "none"],
    "fitness_selfcare": ["sun", "leaf", "heart", "sparkle", "none"],
    "memorial": ["feather", "heart", "dove", "leaf", "robin"],
    "milestones": ["stars", "sparkle", "laurel", "heart", "none"],
    "new_home": ["house", "key", "heart", "laurel", "none"],
    "thank_you_jobs": ["heart", "stars", "apple", "sparkle", "none"],
    "places_towns": ["pin", "stars", "lines", "sun", "none"],
    "heritage_dialect": ["stars", "lines", "diamond", "none"],
    "christmas_seasonal": ["tree", "snow", "star", "holly", "heart"],
    "funny_sarcasm": ["stars", "sparkle", "lines", "none"],
    "travel_coastal": ["waves", "sun", "anchor", "palm", "none"],
    "words_aesthetic": ["sparkle", "moon", "sun", "leaf", "none"],
}
