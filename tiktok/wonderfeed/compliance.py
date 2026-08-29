"""Automated IP screening for catalogue concepts.

Why this is strict: on TikTok Shop an IP complaint costs violation points,
listing removal and withheld balance, and a pattern of them suspends the shop.
A suspension takes all 100 slots at once, so the expected cost of one risky
listing is far higher than the revenue it could ever earn.

The screen runs in two passes:

1. A deterministic blocklist - fast, free, catches the obvious. Marques, bands,
   clubs, franchises, brands. No model call needed.
2. An optional Claude review for what a word list cannot catch: a concept that
   describes a protected design without naming it ("the wedge-shaped 80s
   supercar with pop-up headlights").

Neither pass is legal advice, and neither replaces looking at the concept
yourself before you list it.
"""

import re
import sys

# Whole-word terms that make a concept unsellable without a licence.
BLOCKLIST = {
    "car marques": [
        "bmw", "mercedes", "porsche", "ferrari", "lamborghini", "audi",
        "volkswagen", "vw", "golf gti", "gti", "mustang", "ford", "toyota",
        "supra", "skyline", "nissan", "subaru", "impreza", "mini cooper",
        "land rover", "defender", "jaguar", "aston martin", "bentley",
        "rolls royce", "tesla", "honda", "civic", "type r", "escort", "capri",
        "delorean", "corvette", "camaro", "beetle", "fiat", "vespa", "ducati",
        "harley", "davidson", "triumph", "kawasaki", "yamaha", "peugeot",
        "renault", "citroen", "vauxhall", "opel", "mazda", "rx7", "lotus",
    ],
    "bands and artists": [
        "beatles", "oasis", "nirvana", "queen", "pink floyd", "led zeppelin",
        "rolling stones", "arctic monkeys", "taylor swift", "beyonce", "adele",
        "bowie", "david bowie", "elvis", "michael jackson", "amy winehouse",
        "fleetwood mac", "radiohead", "the clash", "joy division", "blur",
        "stone roses", "smiths", "eminem", "tupac", "biggie", "bob marley",
        "jimi hendrix", "kurt cobain", "abbey road", "dark side of the moon",
    ],
    "clubs and teams": [
        "manchester united", "man utd", "liverpool fc", "arsenal", "chelsea",
        "tottenham", "man city", "manchester city", "everton", "newcastle united",
        "rangers", "celtic", "premier league", "uefa", "fifa", "wimbledon",
        "six nations", "formula 1", "formula one", "f1", "nba", "nfl",
    ],
    "franchises and characters": [
        "disney", "marvel", "star wars", "harry potter", "hogwarts", "pokemon",
        "pikachu", "mario", "nintendo", "sonic", "batman", "superman",
        "spider-man", "spiderman", "mickey mouse", "winnie the pooh", "peppa pig",
        "bluey", "paw patrol", "lego", "minecraft", "stranger things",
        "game of thrones", "friends", "the office", "barbie", "hello kitty",
        "studio ghibli", "totoro", "peanuts", "snoopy", "moomin",
    ],
    "brands": [
        "nike", "adidas", "coca cola", "coca-cola", "pepsi", "mcdonalds",
        "starbucks", "chanel", "gucci", "louis vuitton", "prada", "versace",
        "supreme", "apple inc", "playstation", "xbox", "spotify", "netflix",
        "guinness", "jack daniels", "cadbury", "penguin books",
    ],
    "living people": [
        "ronaldo", "messi", "beckham", "lewis hamilton", "verstappen",
        "king charles", "kate middleton", "meghan markle", "banksy",
    ],
}

# Patterns that usually mean a specific protected design is being described.
RISKY_PATTERNS = [
    (r"\bmk\s?[ivx0-9]+\b", "a specific vehicle generation (Mk-number)"),
    (r"\balbum cover\b", "album cover artwork is copyrighted"),
    (r"\bmovie poster\b|\bfilm poster\b", "film posters are copyrighted"),
    (r"\bsong lyrics?\b|\blyrics?\b", "song lyrics are copyrighted"),
    (r"\bin the style of ([A-Z][a-z]+ ){1,2}[A-Z][a-z]+", "style-of a named artist"),
    (r"\bofficial\b|\blicen[cs]ed\b", "implies an authorisation you do not have"),
    (r"\bdupe\b|\breplica\b|\binspired by ([A-Z])", "counterfeit-adjacent wording"),
    (r"\bjersey\b|\bkit\b.*\bclub\b", "club kit designs are protected"),
]

# Niche-level risk. Drives whether a concept needs a hard look before listing.
NICHE_RISK = {
    "botanical": "low",
    "affirmation": "low",
    "kids": "low",
    "food": "low",
    "pets": "low",
    "humour": "medium",      # jokes drift into catchphrases and memes
    "family": "low",
    "identity": "low",
    "travel": "medium",      # landmarks are fine; city crests and logos are not
    "sport": "high",         # clubs, badges, players
    "music": "high",         # covers, logos, likenesses
    "cars": "high",          # the design itself is protected, not just the badge
}

SAFE_HARBOURS = """Safest sources, in order:
1. Your own original artwork, or AI-generated work you prompted yourself
   without naming a living artist or a protected design.
2. Verified public-domain archives (Biodiversity Heritage Library, Rijksmuseum,
   the Met, Smithsonian Open Access, Library of Congress). Check the licence on
   each item - a museum can restrict commercial use by its terms of service even
   where the scan carries no copyright of its own.
3. Stock you hold a commercial licence for, with the licence saved.

Factual and geometric subjects are usually safe even in risky niches: circuit
layouts, coastlines, star charts, tube-style diagrams of your own design,
elevation profiles, tide tables."""


class Verdict:
    BLOCK = "BLOCK"
    REVIEW = "REVIEW"
    PASS = "PASS"


def _fields(concept):
    parts = [concept.get("name", ""), concept.get("description", ""),
             concept.get("id", "")]
    parts.extend(concept.get("angles") or [])
    parts.extend(concept.get("rooms") or [])
    return " ".join(str(p) for p in parts)


def screen(concept):
    """Deterministic pass. Returns (verdict, [reasons])."""
    text = _fields(concept)
    lowered = text.lower()
    reasons = []

    for category, terms in BLOCKLIST.items():
        for term in terms:
            if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lowered):
                reasons.append(f"{category}: '{term}'")

    if reasons:
        return Verdict.BLOCK, reasons

    for pattern, why in RISKY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            reasons.append(why)

    risk = NICHE_RISK.get(concept.get("niche", ""), "medium")
    if risk == "high":
        reasons.append(f"'{concept.get('niche')}' is a high-risk niche - "
                       f"confirm the subject is original or factual")

    return (Verdict.REVIEW if reasons else Verdict.PASS), reasons


REVIEW_PROMPT = """You are screening wall-art product concepts for intellectual \
property risk before they are listed on TikTok Shop UK.

Block anything that would need a licence:
- A specific protected product design, even when the brand is not named. Car and \
motorbike designs are protected by copyright, design right and trademark - \
describing a recognisable model without naming it is still infringing.
- Album covers, film or TV properties, book covers, video game assets.
- Band names, logos, club badges, brand marks, or their close imitations.
- Living people's names or likenesses.
- Song lyrics, poems or quotations still in copyright (author died within 70 years).
- Characters, whether named or clearly recognisable.

Allow:
- Original subjects and generic ones: plants, landscapes, abstract shapes, \
typography you wrote, animals, food, everyday objects.
- Factual or geometric subjects: circuit layouts, coastlines, star charts, \
elevation profiles, maps of your own drawing.
- Public-domain works where the author died over 70 years ago.

CONCEPTS:
{concepts}

For each, return an object with:
- "id": the concept id
- "verdict": "BLOCK" or "PASS"
- "reason": one short sentence. For BLOCK, name what is protected.
- "fix": for BLOCK only, a one-line rewrite that keeps the same buyer but drops \
the protected element. Otherwise "".

Return ONLY a JSON array. No preamble, no code fence."""


def review_with_claude(concepts, api_key, settings, log=print):
    """Second pass for what a word list cannot catch. Returns {id: dict}."""
    import json

    import anthropic

    if not concepts:
        return {}
    listing = "\n".join(
        f"- id: {c['id']}\n  name: {c.get('name', '')}\n  "
        f"description: {c.get('description', '')}"
        for c in concepts
    )
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=settings["models"]["script_model"],
        max_tokens=4000,
        messages=[{"role": "user", "content": REVIEW_PROMPT.format(concepts=listing)}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        rows = json.loads(text)
    except json.JSONDecodeError:
        log("  ! Claude review returned unparseable output; keeping pass-1 verdicts")
        return {}
    return {r["id"]: r for r in rows if isinstance(r, dict) and r.get("id")}


def screen_all(concepts, api_key=None, settings=None, log=print):
    """Both passes. Returns (passed, blocked, needs_review)."""
    passed, blocked, review = [], [], []
    for c in concepts:
        verdict, reasons = screen(c)
        c["_ip"] = {"verdict": verdict, "reasons": reasons}
        (blocked if verdict == Verdict.BLOCK
         else review if verdict == Verdict.REVIEW else passed).append(c)

    if api_key and (passed or review):
        rows = review_with_claude(passed + review, api_key, settings, log=log)
        still_passed, still_review = [], []
        for c in passed + review:
            row = rows.get(c["id"])
            if row and row.get("verdict") == "BLOCK":
                c["_ip"]["verdict"] = Verdict.BLOCK
                c["_ip"]["reasons"].append(f"AI review: {row.get('reason', '')}")
                c["_ip"]["fix"] = row.get("fix", "")
                blocked.append(c)
            elif c["_ip"]["verdict"] == Verdict.REVIEW:
                still_review.append(c)
            else:
                still_passed.append(c)
        passed, review = still_passed, still_review

    return passed, blocked, review


def main(argv=None):
    import argparse

    import yaml

    from .config import ConfigError, ROOT, load_settings, secret

    ap = argparse.ArgumentParser(description="Screen products for IP risk.")
    ap.add_argument("--file", default=str(ROOT / "config" / "products.yaml"))
    ap.add_argument("--deep", action="store_true",
                    help="also run the Claude review pass (costs a few pence)")
    ap.add_argument("--safe-harbours", action="store_true",
                    help="print where to source artwork safely")
    args = ap.parse_args(argv)

    if args.safe_harbours:
        print(SAFE_HARBOURS)
        return 0

    with open(args.file, encoding="utf-8") as fh:
        products = (yaml.safe_load(fh) or {}).get("products", [])
    if not products:
        print(f"No products in {args.file}")
        return 0

    api_key, settings = None, None
    if args.deep:
        try:
            settings = load_settings()
            api_key = secret("ANTHROPIC_API_KEY")
        except ConfigError as exc:
            print(f"Config error: {exc}", file=sys.stderr)
            return 2

    print(f"Screening {len(products)} product(s)"
          f"{' with Claude review' if args.deep else ''}...\n")
    passed, blocked, review = screen_all(products, api_key, settings)

    for label, group in (("BLOCK", blocked), ("REVIEW", review)):
        if not group:
            continue
        print(f"{label}  ({len(group)})")
        print("-" * 66)
        for c in group:
            print(f"  {c['id']}")
            for r in c["_ip"]["reasons"]:
                print(f"      - {r}")
            if c["_ip"].get("fix"):
                print(f"      fix: {c['_ip']['fix']}")
        print()

    print(f"PASS: {len(passed)}   REVIEW: {len(review)}   BLOCK: {len(blocked)}")
    if blocked:
        print("\nRemove or rewrite everything under BLOCK before listing it.")
    print("\nThis is a screen, not legal advice. Look at each concept yourself.")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
