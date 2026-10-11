#!/usr/bin/env python3
"""Food, drink and objects. Added 11 Oct 2026 as a fifth subject kind.

Kitchen and dining is one of the blocks the mined competitor titles show and
this catalogue had none of, and a still life is the one grammar where a flat
plain ground is normal rather than a near-duplicate risk.

The IP line in this block is BRAND NAMES, and it is drawn here rather than
left to the gate. A negroni, a daiquiri and a margarita are generic drink
names. Aperol, Campari, Pimm's, Hendrick's, Guinness, Chartreuse, Angostura
and Dark 'n' Stormy are trade marks and are not in this file - nor is any
bottle label, which is why every bottle below is described by what it is and
never by whose it is. ip_check.py carries the same names as a backstop.
"""

HOT_DRINKS = [
 "a flat white in a stoneware cup","an espresso in a small white cup",
 "a cafetiere of coffee","a stovetop coffee pot","a pour over coffee cone",
 "a cup of black coffee and a spoon","coffee beans in a bowl",
 "a hand grinder and beans","a teapot and two cups","a cup of tea with milk",
 "a glass cup of green tea","a loose leaf tea caddy","a tea strainer",
 "a mug of hot chocolate","a cup of matcha","a thermos flask and cup",
 "a samovar","a tin of biscuits and a mug",
]

COLD_DRINKS = [
 "a glass of red wine","a glass of white wine","a glass of rose wine",
 "a decanter of red wine","two wine glasses and a cork",
 "a wine bottle with no label","a champagne flute","a coupe glass",
 "a pint of stout settling","a pint of pale ale","a wheat beer in a tall glass",
 "a bottle of beer with no label","a whisky glass with one large cube",
 "a whisky decanter","a copita glass of whisky","a gin and tonic with lime",
 "a highball with cucumber","a negroni in a rocks glass",
 "a daiquiri in a coupe","a margarita with a salt rim",
 "an old fashioned with an orange twist","a martini with an olive",
 "a manhattan with a cherry","a whisky sour","a mojito with mint",
 "a mai tai","a bloody mary with celery","an espresso martini",
 "a pina colada","a cosmopolitan","a french 75","a sidecar","a boulevardier",
 "a dark rum punch","a glass of cider with ice","a jug of lemonade",
 "a glass of iced tea","a bottle of sparkling water and a glass",
 "a milk bottle and a glass","a smoothie in a tall glass",
]

FRUIT_VEG = [
 "a lemon cut in half","a bowl of lemons","a single ripe fig",
 "figs split open","a pomegranate cut open","a bunch of black grapes",
 "a bunch of green grapes","a pear on a plate","three pears in a row",
 "an apple with a leaf","a bowl of red apples","a quince",
 "a persimmon","a blood orange cut in half","a bowl of clementines",
 "a melon wedge","a watermelon slice","a pineapple",
 "a bowl of cherries","a punnet of strawberries","a punnet of raspberries",
 "a bowl of blueberries","a bunch of bananas","a mango cut open",
 "a papaya half","a passion fruit cut open","a kiwi cut in half",
 "an avocado cut in half","a bulb of garlic","a red onion cut in half",
 "a bunch of spring onions","a head of radicchio","a savoy cabbage",
 "a romanesco cauliflower","a bunch of carrots with tops",
 "a bunch of beetroot with leaves","a bowl of new potatoes",
 "a plate of asparagus","a globe artichoke","a bunch of radishes",
 "a string of chillies","a pumpkin on a table","a butternut squash",
 "a basket of tomatoes","a tomato on the vine","an aubergine",
 "a courgette with its flower","a corn cob with husk","a bowl of broad beans",
 "a bowl of peas in the pod","a wedge of celeriac","a bunch of leeks",
 "a head of fennel","a bowl of olives","a jar of preserved lemons",
]

KITCHEN_TABLE = [
 "a wedge of hard cheese","a round of soft cheese","a cheese board",
 "a loaf of sourdough","a sliced rye loaf","a baguette",
 "a croissant on a plate","a stack of pancakes","a bowl of ramen",
 "a plate of spaghetti","fresh pasta sheets","a bowl of noodles",
 "a wheel of parmesan","a jar of honey with a dipper","a honeycomb",
 "an egg in a cup","three brown eggs in a bowl","a jug of milk",
 "a pat of butter on a dish","a bowl of flour and a whisk",
 "a dusted bundt cake","a slice of lemon tart","a plate of macarons",
 "a chocolate cake with one slice cut","a bowl of soup and bread",
 "a roast chicken on a platter","a plate of oysters on ice",
 "a whole fish on a board","a crab on a board","a bowl of mussels",
 "a loaf of brioche","a jar of jam and a spoon","a tin of sardines",
 "a bowl of rice","a bowl of lentils","a bowl of sea salt",
 "a pepper mill","a mortar and pestle with spices",
 "a bundle of cinnamon sticks","a bowl of star anise",
 "a bowl of dried chillies","a saffron dish","a vanilla pod",
]

OBJECTS = [
 "a cast iron pan","a copper saucepan","a stack of enamel plates",
 "a stoneware jug","a hand thrown bowl","a stack of three bowls",
 "a wooden chopping board and knife","a balance scale with weights",
 "a pair of scissors on paper","a ball of string","a brass candlestick",
 "a lit beeswax candle","a hurricane lamp","an oil lamp",
 "a watering can","a terracotta plant pot","a pair of secateurs",
 "a trowel and fork","a wicker basket","a trug of cut flowers",
 "a straw hat on a hook","a pair of walking boots","a tin bath",
 "a stack of old books","an open book face down","a fountain pen and ink",
 "a pot of paintbrushes","a palette with mixed paint","a wooden ruler",
 "a pair of spectacles on a book","a pocket watch","a mantel clock",
 "a brass compass","a sextant","a ship in a bottle","a glass float",
 "a vinyl record out of its sleeve","a record player arm","a metronome",
 "a violin on a chair","a cello against a wall","a trumpet",
 "a piano keyboard close up","a sheet of music with no notes",
 "a typewriter","a rotary telephone","a film camera","a darkroom tray",
 "a sewing machine","a basket of yarn","a pair of knitting needles",
 "a thimble and thread","a pin cushion","a folded linen cloth",
 "a bar of soap and a brush","a hairbrush and comb","a perfume bottle",
 "a hand mirror","a key on a ring","a brass door knocker",
]

NATURAL_OBJECTS = [
 "a scallop shell","a nautilus shell","a group of cowrie shells",
 "a razor shell","a whelk shell","a sea urchin test","a starfish",
 "a piece of coral","a mermaid's purse","a beach pebble with a hole",
 "three smooth pebbles stacked","a piece of driftwood","a sea glass piece",
 "a feather, barred","a single long tail feather","a down feather",
 "a bird's nest with three eggs","a speckled egg","an acorn and cup",
 "a conker in its case","a sweet chestnut husk","a pine cone",
 "a sycamore seed pair","an ash key cluster","a beech nut",
 "a walnut cracked open","a hazelnut cluster","a seed head skeleton",
 "an ammonite fossil","a trilobite fossil","a fossil fern frond",
 "a quartz crystal","an amethyst geode","a piece of fool's gold",
 "a lump of coal","a flint hand axe","a piece of amber",
 "a honeycomb fragment","a wasp nest fragment","a snail shell",
]

ALL = (HOT_DRINKS + COLD_DRINKS + FRUIT_VEG + KITCHEN_TABLE + OBJECTS
       + NATURAL_OBJECTS)

if __name__ == "__main__":
    import collections
    for k, v in list(globals().items()):
        if isinstance(v, list) and k.isupper() and k != "ALL":
            print(f"{k:<20}{len(v):>6}")
    d = [x for x, c in collections.Counter(ALL).items() if c > 1]
    print(f"{'TOTAL':<20}{len(ALL):>6}   unique {len(set(ALL))}   dupes {d}")
