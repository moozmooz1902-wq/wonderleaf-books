#!/usr/bin/env python3
"""The AI image catalogue: subject x proven format x variation -> one listing each.

Formats copy what measurably sells on eBay UK (research/IMAGE_DEMAND.md):
  garland     animal wearing a flower crown/garland, on white      (873, 445, 343 sold)
  toilet      animal sitting on the toilet - bathroom humour        (369, 313 sold)
  bath        animal in a bubble bath - bathroom humour             (259, 178 sold)
  bw          black-and-white animal portrait on white              (309, 244 sold)
  bwpair      two animals together, black and white                 (244 sold)
  nursery     soft watercolour baby animal for nurseries            (241, 232 sold)
  dictionary  vintage engraving printed on an antique dictionary page (489, 392, 342 sold)
  dressed     animal in period clothes, vintage illustration        (342 sold)
  christmas   animal in a festive hat/scarf on white                (194 sold, seasonal)
  mummybaby   mother and baby animal - Mother's Day                 (148, 141 sold)
  plant       tropical leaf / flower photo or watercolour on white  (1,002, 617, 503 sold)

Every image is on a white or near-white background (low ink), and every
listing is a different picture with its own title - no re-rolls.
Images are generated on a GPU pod by pod/gen_ai.py (FLUX.1 schnell, Apache-2.0).

    python3 images_bank.py --stats
    python3 images_bank.py            -> out/<bucket>_ai.csv.gz
"""
import argparse, csv, gzip, hashlib, itertools, json, random, re
from collections import Counter, defaultdict
from pathlib import Path

from compliance import check as ip_check
from generate import fit

HERE = Path(__file__).resolve().parent
BANK = HERE / "banks" / "images"

NO_TEXT = "no text, no letters, no watermark, no signature, no frame"

FORMATS = {
    "garland": dict(
        groups={"safari", "farm", "woodland", "pet_dog", "pet_cat", "pet_small", "horse", "polar", "bird"},
        axes=dict(
            flowers=["pink roses", "white daisies", "sunflowers", "lavender", "blush peonies", "mixed wildflowers",
                     "cherry blossom", "red poppies", "bluebells", "eucalyptus and white roses", "autumn leaves and berries",
                     "yellow buttercups", "pastel hydrangeas", "orange marigolds", "white gypsophila", "lilac wisteria"],
            shot=["head and shoulders portrait", "close-up portrait"],
            style=["photo", "watercolour"]),
        prompt={"photo": "Professional studio photograph of {an_a} wearing a crown and garland of {flowers}, {shot}, looking at the camera, soft natural light, isolated on a pure white background, sharp focus, high detail, minimal, {nt}",
                "watercolour": "Delicate watercolour painting of {an_a} wearing a crown and garland of {flowers}, {shot}, soft washes, fine detail, isolated on a plain white paper background, {nt}"},
        title="{A} Flower Crown Print {Flowers} {Shot} {Style}",
        rooms=["Bedroom", "Living Room", "Nursery", "Hallway"], niche="animals_flowers", store="luxvia-art"),
    "toilet": dict(
        groups={"safari", "farm", "woodland", "pet_dog", "pet_cat", "pet_small", "horse", "polar"},
        axes=dict(prop=["reading a newspaper", "holding a toilet roll", "scrolling on a phone", "reading a book",
                        "wearing reading glasses", "holding a cup of tea", "looking surprised", "with a rubber duck"],
                  style=["photo", "watercolour"]),
        prompt={"photo": "Funny photograph of {an_a} sitting on a white toilet {prop}, bright clean white bathroom, white tiles, soft daylight, centred, high detail, {nt}",
                "watercolour": "Funny watercolour illustration of {an_a} sitting on a white toilet {prop}, light and airy, plain white background, {nt}"},
        title="Funny {A} On Toilet {Prop} {Style} Bathroom Print",
        rooms=["Bathroom", "Toilet", "Cloakroom"], niche="bathroom_animals", store="mercury-usm"),
    "bath": dict(
        groups={"safari", "farm", "woodland", "pet_dog", "pet_cat", "pet_small", "horse", "polar"},
        axes=dict(prop=["with a rubber duck", "wearing a shower cap", "with cucumber slices on its eyes",
                        "with bubbles on its head", "reading a book", "holding a back brush"],
                  style=["photo", "watercolour"]),
        prompt={"photo": "Funny photograph of {an_a} relaxing in a white clawfoot bathtub full of bubbles {prop}, bright white bathroom, soft light, centred, high detail, {nt}",
                "watercolour": "Funny watercolour illustration of {an_a} in a white clawfoot bathtub full of bubbles {prop}, light and airy, plain white background, {nt}"},
        title="Funny {A} In Bath {Prop} {Style} Bathroom Print",
        rooms=["Bathroom", "En Suite"], niche="bathroom_animals", store="mercury-usm"),
    "bw": dict(
        groups=None,
        axes=dict(pose=["close-up face portrait", "side profile portrait", "looking up", "full body portrait",
                        "intense eyes close-up"],
                  style=["photo", "charcoal"]),
        prompt={"photo": "Black and white fine art photograph of {an_a}, {pose}, isolated on a pure white background, high key, detailed texture, dramatic but clean, {nt}",
                "charcoal": "Black and white charcoal drawing of {an_a}, {pose}, expressive realistic sketch on plain white paper, {nt}"},
        title="{A} Black And White {Style} {Pose} Print",
        rooms=["Living Room", "Bedroom", "Office", "Hallway"], niche="animals_bw", store="luxvia-art"),
    "bwpair": dict(
        groups={"safari", "farm", "woodland", "horse", "polar", "pet_dog", "pet_cat", "bird"},
        axes=dict(pose=["nuzzling each other", "side by side", "mother with baby"]),
        prompt={"": "Black and white fine art photograph of two {plural} {pose}, isolated on a pure white background, high key, detailed, tender, {nt}"},
        title="Two {Plural} {Pose} Black And White Print",
        rooms=["Living Room", "Bedroom", "Hallway"], niche="animals_bw", store="luxvia-art"),
    "nursery": dict(
        groups={"safari", "woodland", "farm", "polar", "sea", "bird", "horse"},
        axes=dict(item=["holding a balloon", "in a little hot air balloon", "with stars and a crescent moon",
                        "holding a bunch of flowers", "asleep on a fluffy cloud", "wearing a tiny crown"],
                  tone=["pink", "blue", "sage green", "neutral beige", "lilac", "lemon yellow"]),
        prompt={"": "Cute watercolour illustration of a baby {a} {item}, soft {tone} pastel tones, gentle children's book style, plenty of white space, plain white paper background, {nt}"},
        title="Baby {A} {Item} {Tone} Nursery Print",
        rooms=["Nursery", "Kids Bedroom", "Playroom"], niche="nursery_animals", store="lunar-kms"),
    "dictionary": dict(
        groups=None,
        axes=dict(dress=["as a scientific natural history study", "wearing a Victorian suit and top hat",
                         "wearing steampunk goggles with brass gears", "wearing a golden crown",
                         "wearing a Victorian lace bonnet", "reading an old book"]),
        prompt={"": "Vintage black ink engraving illustration of {an_a} {dress}, fine cross-hatching, antique book plate style, isolated on a plain white background, {nt}"},
        title="{A} {Dress} Vintage Dictionary Page Print",
        rooms=["Living Room", "Study", "Hallway", "Office"], niche="dictionary_art", store="posterleaf-store1",
        page=True),
    "dressed": dict(
        groups={"safari", "farm", "woodland", "pet_dog", "pet_cat", "pet_small", "horse", "polar", "bird", "reptile"},
        axes=dict(outfit=["tweed suit and flat cap", "three piece suit and pocket watch", "red military jacket",
                          "velvet smoking jacket", "Victorian ball gown", "pilot jacket and goggles",
                          "knitted jumper and scarf", "chef's whites and hat", "gardener's apron and wellies",
                          "sailor's striped top"]),
        prompt={"": "Portrait illustration of {an_a} dressed in a {outfit}, vintage storybook painting style, full colour, dignified and charming, isolated on a plain white background, {nt}"},
        title="{A} In {Outfit} Dressed Animal Print",
        rooms=["Living Room", "Study", "Hallway", "Kitchen"], niche="dressed_animals", store="posterleaf-store1"),
    "christmas": dict(
        groups={"pet_dog", "pet_cat", "pet_small", "farm", "woodland", "polar", "safari", "horse", "bird"},
        axes=dict(prop=["wearing a red Santa hat", "wearing a knitted scarf and bobble hat", "wearing reindeer antlers",
                        "tangled in warm fairy lights", "wearing a festive Christmas jumper"],
                  style=["photo", "watercolour"]),
        prompt={"photo": "Festive studio photograph of {an_a} {prop}, cosy and cute, isolated on a pure white background, soft light, high detail, {nt}",
                "watercolour": "Festive watercolour illustration of {an_a} {prop}, cosy and cute, plain white paper background, {nt}"},
        title="Christmas {A} {Prop} {Style} Print",
        rooms=["Living Room", "Hallway", "Kitchen"], niche="christmas_animals", store="luxvia-art"),
    "mummybaby": dict(
        groups={"safari", "farm", "woodland", "polar", "horse", "sea", "bird", "pet_dog", "pet_cat"},
        axes=dict(style=["photo", "watercolour"]),
        prompt={"photo": "Tender photograph of a mother {a} cuddling her baby, isolated on a pure white background, soft light, high detail, {nt}",
                "watercolour": "Tender watercolour painting of a mother {a} cuddling her baby, soft pastel washes, plain white paper background, {nt}"},
        title="Mummy And Baby {A} {Style} Mother's Day Print",
        rooms=["Nursery", "Bedroom", "Living Room"], niche="mummy_baby", store="lunar-kms"),
    "crown": dict(
        groups={"safari", "farm", "woodland", "pet_dog", "pet_cat", "horse", "polar", "bird"},
        axes=dict(crown=["golden crown", "silver tiara", "jewelled crown", "floral crown of gold leaves"],
                  style=["photo", "watercolour"]),
        prompt={"photo": "Regal studio photograph of {an_a} wearing a {crown}, proud pose, isolated on a pure white background, soft light, high detail, {nt}",
                "watercolour": "Regal watercolour painting of {an_a} wearing a {crown}, proud pose, plain white paper background, {nt}"},
        title="{A} With {Crown} King Queen {Style} Print",
        rooms=["Living Room", "Bedroom", "Hallway"], niche="animals_crown", store="luxvia-art"),
    "colourpop": dict(
        groups=None,
        axes=dict(pop=["a red rose", "a yellow sunflower", "a pink bubblegum bubble", "a blue butterfly",
                       "a red balloon", "pink flowers"],
                  pose=["portrait", "close-up"]),
        prompt={"": "Black and white fine art photograph of {an_a}, {pose}, with only {pop} in vivid colour, colour splash, isolated on a pure white background, high key, {nt}"},
        title="{A} Black And White {Pop} Colour Pop {Pose} Print",
        rooms=["Living Room", "Bedroom", "Hallway", "Office"], niche="animals_colourpop", store="posterleaf-store1"),
    "fun": dict(
        groups={"safari", "farm", "woodland", "pet_dog", "pet_cat", "pet_small", "horse", "polar", "bird"},
        axes=dict(fun=["wearing heart-shaped sunglasses", "wearing big headphones", "blowing a pink bubblegum bubble",
                       "wearing a party hat", "wearing a bow tie", "wearing round glasses"],
                  style=["photo", "watercolour"]),
        prompt={"photo": "Fun studio photograph of {an_a} {fun}, playful and cute, isolated on a pure white background, bright soft light, high detail, {nt}",
                "watercolour": "Fun watercolour illustration of {an_a} {fun}, playful and cute, plain white paper background, {nt}"},
        title="Funny {A} {Fun} {Style} Print",
        rooms=["Bedroom", "Living Room", "Kids Bedroom", "Office"], niche="animals_fun", store="mercury-usm"),
}

PLANT_FORMATS = {
    "photo": "Professional botanical photograph of a single {p}, fresh and detailed, isolated on a pure white background, soft shadow, minimal, {nt}",
    "trio": "Professional botanical photograph of three {p}s arranged side by side, isolated on a pure white background, minimal, {nt}",
    "watercolour": "Loose botanical watercolour painting of a {p}, fresh colours, plain white paper background, {nt}",
    "closeup": "Macro close-up photograph of a {p}, fine detail, isolated on a pure white background, {nt}",
    "vintage": "Vintage botanical illustration plate of a {p}, antique hand-coloured engraving, plain white background, {nt}",
    "bw": "Black and white fine art photograph of a {p}, high key, isolated on a pure white background, {nt}",
}
PLANT_TITLE = "{P} {Style} Botanical Print"
TAIL = ["Wall Art", "Picture", "A4 A3 A2", "Gift", "Framed"]
SHORT = {"Head and Shoulders Portrait": "Portrait", "Close-up Portrait": "Close Up", "Close-up Face Portrait": "Face",
         "Side Profile Portrait": "Profile", "Full Body Portrait": "Full Body", "Intense Eyes Close-up": "Eyes",
         "Looking Up": "Looking Up", "Nuzzling Each Other": "Nuzzling", "Side by Side": "Side By Side",
         "Mother with Baby": "Mother And Baby", "A Scientific Natural History Study": "Natural History",
         "A Victorian Suit and Top Hat": "Top Hat", "Steampunk Goggles with Brass Gears": "Steampunk",
         "A Golden Crown": "Crown", "A Victorian Lace Bonnet": "Bonnet", "An Old Book": "Reading",
         "Little Hot Air Balloon": "Hot Air Balloon", "Stars and a Crescent Moon": "Moon And Stars",
         "Bunch of Flowers": "Flowers", "A Fluffy Cloud": "Sleeping Cloud", "Tiny Crown": "Crown",
         "Eucalyptus and White Roses": "Eucalyptus Roses", "Autumn Leaves and Berries": "Autumn Leaves",
         "Knitted Scarf and Bobble Hat": "Scarf And Bobble Hat", "Warm Fairy Lights": "Fairy Lights",
         "Festive Christmas Jumper": "Christmas Jumper", "Cucumber Slices on Its Eyes": "Cucumber Eyes",
         "Bubbles on Its Head": "Bubble Head", "Newspaper": "Newspaper", "Toilet Roll": "Toilet Roll",
         "Cup of Tea": "Cup Of Tea", "Heart-shaped Sunglasses": "Heart Sunglasses", "Big Headphones": "Headphones",
         "A Pink Bubblegum Bubble": "Bubblegum", "A Party Hat": "Party Hat", "A Bow Tie": "Bow Tie",
         "Round Glasses": "Glasses", "Golden Crown": "Gold Crown", "Floral Crown of Gold Leaves": "Leaf Crown",
         "A Red Rose": "Red Rose", "A Yellow Sunflower": "Sunflower", "A Blue Butterfly": "Blue Butterfly",
         "A Red Balloon": "Red Balloon", "Pink Flowers": "Pink Flowers", "Close-up": "Close Up", "Portrait": "Portrait"}
PLANT_STORE = {"tropical": "posterleaf-store1", "green": "posterleaf-store1", "dried": "luxvia-art",
               "flower": "luxvia-art", "fruit": "mercury-usm", "tree": "posterleaf-store1"}
SKU = {"luxvia-art": "LX", "mercury-usm": "MC", "lunar-kms": "LN", "posterleaf-store1": "PL"}


def read(name):
    out = []
    for line in (BANK / name).read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            out.append([x.strip() for x in line.split("|")])
    return out


def titlecase(s):
    small = {"a", "an", "and", "the", "of", "in", "on", "with", "to", "its", "her", "by"}
    return " ".join(w if (i and w.lower() in small) else w[:1].upper() + w[1:] for i, w in enumerate(s.split()))


def short(v):
    """Variant phrase -> short title words ('wearing a red Santa hat' -> 'Red Santa Hat')."""
    t = titlecase(v)
    if t in SHORT:
        return SHORT[t]
    v = re.sub(r"^(wearing|holding|with|in|as|reading|looking|asleep on|tangled in|scrolling on|dressed in)\s+(a |an |the )?", "", v)
    t = titlecase(v)
    return SHORT.get(t, t)


def art(word):
    return ("an " if word[:1].lower() in "aeiou" else "a ") + word


def seed_of(key):
    return int(hashlib.sha1(key.encode()).hexdigest()[:8], 16)


def concepts():
    """Yield dicts: fmt, subject, variant dict, prompt, title, niche, rooms, store, page."""
    animals = read("animals.txt")
    for fid, f in FORMATS.items():
        names = list(f["axes"])
        for name, group, plural in animals:
            if f["groups"] is not None and group not in f["groups"]:
                continue
            for combo in itertools.product(*[f["axes"][k] for k in names]):
                v = dict(zip(names, combo))
                style = v.get("style", "")
                tmpl = f["prompt"][style]
                prompt = tmpl.format(a=name.lower(), an_a=art(name.lower()), plural=plural.lower(), nt=NO_TEXT,
                                     **{k: val for k, val in v.items() if k != "style"})
                words = {"A": name, "Plural": plural, "Style": {"photo": "Photo", "watercolour": "Watercolour",
                                                                "charcoal": "Charcoal", "": ""}[style]}
                for k, val in v.items():
                    if k != "style":
                        words[k.capitalize()] = short(val)
                title = re.sub(r"\s+", " ", f["title"].format(**words)).strip()
                yield dict(fmt=fid, subject=name, variant=v, prompt=prompt, title=title, niche=f["niche"],
                           rooms=f["rooms"], store=f["store"], page=f.get("page", False))
    for name, kind in read("plants.txt"):
        for style, tmpl in PLANT_FORMATS.items():
            yield dict(fmt="plant", subject=name, variant={"style": style},
                       prompt=tmpl.format(p=name.lower(), nt=NO_TEXT),
                       title=PLANT_TITLE.format(P=name, Style={"photo": "Photo", "trio": "Set Trio Photo",
                                                                "watercolour": "Watercolour", "closeup": "Close Up Photo",
                                                                "vintage": "Vintage Botanical", "bw": "Black And White"}[style]),
                       niche="botanical", rooms=["Living Room", "Bedroom", "Bathroom", "Kitchen"],
                       store=PLANT_STORE[kind], page=False)


FIELDS = ["sku", "store", "kind", "niche", "format", "subject", "variant", "prompt", "seed", "page",
          "title", "room", "colour", "img_path"]


def build(write=True):
    by_store = defaultdict(list)
    titles = set()
    dup = blocked = 0
    for c in concepts():
        t = fit([c["title"]] + TAIL)
        if ip_check(t) or ip_check(c["prompt"]):
            blocked += 1
            continue
        if t in titles:            # two concepts collapsing to one title would read as duplicates
            dup += 1
            continue
        titles.add(t)
        by_store[c["store"]].append((c, t))
    stats = {s: Counter(c["fmt"] for c, _ in rows) for s, rows in by_store.items()}
    if write:
        out = HERE / "out"
        out.mkdir(exist_ok=True)
        for store, rows in by_store.items():
            rnd = random.Random(f"ai-{store}")
            rnd.shuffle(rows)        # interleave formats and subjects in upload order
            with gzip.open(out / f"{store}_ai.csv.gz", "wt", encoding="utf-8", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(FIELDS)
                for n, (c, t) in enumerate(rows, 1):
                    sku = f"{SKU[store]}AI{n:07d}"
                    room = random.Random(sku).choice(c["rooms"])
                    w.writerow([sku, store, "ai", c["niche"], c["fmt"], c["subject"], json.dumps(c["variant"]),
                                c["prompt"], seed_of(sku + c["prompt"]), int(c["page"]), t, room, "",
                                f"/art/mock/{sku}.jpg"])
    return stats, dup, blocked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    stats, dup, blocked = build(write=not a.stats)
    total = 0
    for s, c in stats.items():
        n = sum(c.values()); total += n
        print(f"{s:20s} {n:>7,}  " + ", ".join(f"{k} {v:,}" for k, v in c.most_common()))
    print(f"{'TOTAL':20s} {total:>7,}   (duplicate titles dropped {dup}, IP-blocked {blocked})")


if __name__ == "__main__":
    main()
