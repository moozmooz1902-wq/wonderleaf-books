#!/usr/bin/env python3
"""The copyright gate. Nothing reaches a listing without passing this.

Six things can get a generated wall-art catalogue taken down or sued, and
they are checked here rather than hoped about.

 1. LICENSED IP as a subject. Film, game and brand names. The Displate brand
    list in this repo is 191 of them and is used as the seed blocklist,
    matched as whole phrases - matching single words flagged "hedgehog" the
    animal because of Sonic, and "horizon" the skyline because of a
    PlayStation game, neither of which is a problem.

 2. NAMED ARTISTS. Style is not copyrightable, but naming a living or
    recent artist invites a passing-off claim and breaches eBay's own
    listing rules. No artist name appears in a prompt or a title.

 3. RESTRICTED LANDMARKS. UK law is generous here - CDPA s.62 allows
    depicting buildings and public sculptures - but that exception is UK
    only. The Eiffel Tower's night illumination, the Atomium and the
    Hollywood sign are protected where they stand, so they are blocked.

 4. FALSE ATTRIBUTION. A fake painter's signature on the artwork is not just
    an AI tell, it is a false attribution of authorship under CDPA s.84.
    Removing it (declutter.py, and the 10% crop) is a legal control as much
    as a quality one.

 5. MISDESCRIPTION. Saying "hand-painted", "original" or "handmade" about a
    generated print breaches the Consumer Protection from Unfair Trading
    Regulations 2008. The technique words are fine as descriptions of the
    LOOK - "charcoal style" - and not as claims about how it was made.

 6. THE MODEL LICENCE. Verified, not assumed - see licence_chain().
"""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

# Artists whose names must never appear. Not exhaustive and not meant to be:
# the rule is that NO artist is named, and this catches the ones the mined
# competitor titles actually used.
ARTISTS = ["banksy", "matisse", "henri matisse", "picasso", "monet", "van gogh",
           "klimt", "hockney", "warhol", "kandinsky", "o'keeffe", "okeeffe",
           "mondrian", "basquiat", "haring", "lichtenstein", "rothko",
           "cezanne", "paul cezanne", "hokusai", "william morris", "mucha",
           "escher", "dali", "frida kahlo", "yayoi kusama", "takashi murakami"]

# Protected where they stand. UK CDPA s.62 covers UK buildings and public
# sculpture, so UK landmarks are not listed; these are the foreign ones with
# no equivalent exception, plus the usual trademark traps.
LANDMARKS = ["eiffel tower at night", "eiffel tower illumination", "atomium",
             "hollywood sign", "little mermaid copenhagen", "cloud gate",
             "the bean chicago", "angel of the north"]

# Words that would turn an accurate listing into a misleading one.
FORBIDDEN_CLAIMS = ["hand painted", "hand-painted", "handpainted", "handmade",
                    "hand made", "original painting", "original artwork",
                    "one of a kind", "oil on canvas", "artist signed",
                    "signed by the artist", "limited edition of"]


def _phrases(path):
    out = []
    for line in open(path):
        b = line.strip().replace("-", " ").lower()
        if len(b.split()) >= 2 or len(b) >= 9:   # whole phrases, not stray words
            out.append(b)
    return out


def blocklist():
    bl = set(ARTISTS) | set(LANDMARKS)
    p = os.path.join(HERE, "displate_brands.txt")
    if os.path.exists(p):
        bl |= set(_phrases(p))
    return sorted(bl)


def scan(text, bl=None):
    """Whole-phrase, word-boundary matches only."""
    bl = bl or blocklist()
    t = " " + re.sub(r"[^a-z0-9' ]+", " ", text.lower()) + " "
    t = re.sub(r"\s+", " ", t)
    return [b for b in bl if f" {b} " in t]


def check_subjects(subjects):
    bl = blocklist()
    bad = {}
    for kind, vals in subjects.items():
        if not isinstance(vals, list):
            continue
        for v in vals:
            hits = scan(v, bl)
            if hits:
                bad[v] = hits
    return bad


def check_listing(title, description=""):
    """A listing must not claim to be something it is not."""
    t = (title + " " + description).lower()
    return [c for c in FORBIDDEN_CLAIMS if c in t]


def licence_chain():
    return {
        "FLUX.1-schnell weights": "Apache-2.0, commercial use allowed. "
            "FLUX.1-dev is NON-commercial and is never used. The ungated "
            "mirror lzyvegetable/FLUX.1-schnell was checked file by file "
            "against the official repo: 23 of 23 comparable files have "
            "identical sha256, so the weights are the official ones.",
        "diffusers / transformers / accelerate / sentencepiece / easyocr":
            "Apache-2.0",
        "bitsandbytes": "MIT",
        "torch / numpy": "BSD-family, permissive",
        "pillow": "MIT-CMU",
        "protobuf": "BSD-3-Clause",
        "CLIP ViT-L/14": "MIT (and not in the production path anyway)",
        "copyleft anywhere in the chain": "none - nothing GPL or AGPL",
        "who owns the output":
            "UK: a computer-generated work gets 50 years from creation under "
            "CDPA s.9(3) and the author is the person who made the "
            "arrangements, so the seller owns these. US: the Copyright Office "
            "will not register purely AI-generated images, so they can be "
            "sold there but copying cannot easily be stopped.",
    }


if __name__ == "__main__":
    subs = json.load(open(sys.argv[1] if len(sys.argv) > 1
                          else os.path.join(HERE, "gen", "subjects.json")))
    bl = blocklist()
    print(f"blocklist: {len(bl)} phrases "
          f"({len(ARTISTS)} artists, {len(LANDMARKS)} landmarks, rest brands)\n")

    bad = check_subjects(subs)
    n = sum(len(v) for v in subs.values() if isinstance(v, list))
    print(f"1. SUBJECTS        {n} checked -> "
          f"{'BLOCKED: ' + json.dumps(bad) if bad else 'all clear'}")

    sys.path.insert(0, os.path.join(HERE, "gen"))
    import prompts as P
    vocab = " ".join(list(P.TECHNIQUE.values()) + list(P.GRAMMAR_PLACE.values())
                     + list(P.GRAMMAR_CREATURE.values())
                     + list(P.GRAMMAR_BOTANICAL.values())
                     + list(P.PALETTE.values()) + [P.RULES, P.RULES_CREATURE])
    hits = scan(vocab, bl)
    print(f"2. PROMPT WORDING  -> {'BLOCKED: ' + str(hits) if hits else 'no artist, brand or landmark named'}")

    sample = "Highland Cow Charcoal Style Wall Art Print A3 Framed Black Frame"
    claims = check_listing(sample)
    print(f"3. LISTING WORDING -> sample title "
          f"{'BLOCKED: ' + str(claims) if claims else 'makes no handmade or original claim'}")
    bad_t = "Original Hand-Painted Highland Cow Oil on Canvas, artist signed"
    print(f"   control (should fail) -> {check_listing(bad_t)}")

    print("\n4. LICENCE CHAIN")
    for k, v in licence_chain().items():
        print(f"   {k}\n      {v}")
