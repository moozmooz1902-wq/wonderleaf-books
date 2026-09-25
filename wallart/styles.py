"""Visual building blocks: named colourways, font pairings, layouts, ornaments.

Every design is phrase + palette + fonts + layout + ornament. The palette NAME goes
into the listing title, because decor buyers search by colour ("sage green kitchen
print") - so each palette carries the words a buyer would type.
"""

# id: (title words, background, ink, accent)
PALETTES = {
    "bw":        ("Black and White", "#FFFFFF", "#111111", "#111111"),
    "wb":        ("Black",           "#141414", "#F4F1EA", "#D8C79A"),
    "sage":      ("Sage Green",      "#E4E9DF", "#3F5446", "#7E9A82"),
    "sagedeep":  ("Sage",            "#8FA58D", "#FBFAF5", "#2F3F33"),
    "terracotta":("Terracotta",      "#F3E7DC", "#9B4A2E", "#C9724F"),
    "rust":      ("Burnt Orange",    "#C0582F", "#FFF6EC", "#3A1F12"),
    "blush":     ("Blush Pink",      "#F6E3DF", "#5B3A3A", "#C98C8C"),
    "dustypink": ("Dusty Pink",      "#D9A8A5", "#FFFFFF", "#6B3F3D"),
    "navy":      ("Navy Blue",       "#1F2A44", "#F5F1E8", "#C9A96E"),
    "navylight": ("Navy",            "#F4F1EA", "#1F2A44", "#9C7C45"),
    "cream":     ("Cream",           "#F5EFE3", "#2B2622", "#A88B5E"),
    "beige":     ("Beige",           "#E8DCCB", "#4A3C30", "#8C6E52"),
    "charcoal":  ("Charcoal Grey",   "#3A3B3D", "#F2F0EB", "#BFB6A5"),
    "grey":      ("Grey",            "#E6E6E3", "#333333", "#7A7A76"),
    "forest":    ("Forest Green",    "#23392D", "#F1EDE2", "#C2A76A"),
    "mustard":   ("Mustard Yellow",  "#E1AD2F", "#2A2419", "#FFFFFF"),
    "teal":      ("Teal",            "#1E5E5E", "#F4F0E6", "#E3B85B"),
    "duckegg":   ("Duck Egg Blue",   "#D5E4E1", "#2E4A4E", "#6C9A99"),
    "lilac":     ("Lilac",           "#E4DCEC", "#4A3D5C", "#8B77A6"),
    "burgundy":  ("Burgundy",        "#5E1F2B", "#F7EEE6", "#D9B48F"),
    "olive":     ("Olive Green",     "#6B6B3E", "#F7F3E6", "#2B2B18"),
    "kraft":     ("Kraft Brown",     "#C8A57A", "#2A1E14", "#FFFFFF"),
    "chalk":     ("Chalkboard",      "#2E3432", "#F4F4F0", "#E8D9A8"),
    "gold":      ("Black and Gold",  "#101010", "#D4B26A", "#D4B26A"),
    "pastel":    ("Pastel",          "#FBF4EE", "#5E5A7A", "#E9A6A6"),
    "rainbow":   ("Rainbow",         "#FFFFFF", "#3C3C58", "#E07A5F"),
}
RAINBOW = ["#E07A5F", "#F2CC8F", "#81B29A", "#3D85C6", "#9B72CF"]

# which palettes suit which niche mood - the generator draws from these
PALETTE_MOODS = {
    "rustic":  ["cream", "beige", "kraft", "sage", "terracotta", "chalk", "forest", "bw", "olive"],
    "bold":    ["bw", "wb", "mustard", "navy", "rust", "teal", "charcoal", "forest", "gold"],
    "retro":   ["mustard", "rust", "teal", "cream", "terracotta", "navy", "olive", "burgundy"],
    "script":  ["blush", "sage", "cream", "navylight", "bw", "dustypink", "lilac", "duckegg"],
    "elegant": ["bw", "wb", "navy", "gold", "cream", "sage", "forest", "burgundy", "charcoal"],
    "minimal": ["bw", "wb", "beige", "grey", "sage", "cream", "charcoal", "blush"],
    "modern":  ["bw", "wb", "charcoal", "sagedeep", "terracotta", "navy", "mustard", "grey"],
    "vintage": ["cream", "kraft", "navy", "forest", "burgundy", "beige", "chalk", "olive"],
    "playful": ["mustard", "blush", "teal", "pastel", "rainbow", "duckegg", "rust", "bw"],
    "kids":    ["pastel", "rainbow", "duckegg", "blush", "sage", "mustard", "lilac", "bw"],
    "sacred":  ["cream", "bw", "wb", "navy", "gold", "sage", "blush", "beige", "forest"],
    "celtic":  ["forest", "cream", "sage", "bw", "navy", "kraft"],
    "geometric": ["navy", "gold", "wb", "teal", "cream", "forest", "bw", "sage"],
    "industrial": ["charcoal", "wb", "kraft", "rust", "bw", "chalk"],
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

LAYOUTS = ["stack", "subway", "left", "frame", "rules", "arch", "badge", "block", "ribbon", "corner"]

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
