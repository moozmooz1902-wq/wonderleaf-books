#!/usr/bin/env python3
"""Subjects that must not be printed, whatever the artwork looks like.

These came out of the collaborator's own catalogue, which is where the
subject bank was mined from, so they arrive looking like proven sellers.
They are not. eBay runs the VeRO programme: a rights owner reports a listing
and it is removed, and a run of removals puts the account itself at risk.
The M12K account already carries a selling limit, so it has the least room
of any of them to absorb that.

Three kinds, all of them live:

    trademark   a brand, a marque, a model name
    character   a film, game or television character
    likeness    a real person, living or dead, including the royal family

The last one is the least obvious and the most often got wrong: a portrait
of a public figure is their likeness, not public property, and the estate of
a dead one usually still enforces it.
"""
import re

PATTERNS = [
    # film, television, games
    r"ghostbuster|ecto.?1|scooby|mystery\s*machine|freddy\s*krueger|spock|"
    r"star\s*wars|yoda|darth|jedi|batman|superman|spider.?man|marvel|disney|"
    r"pokemon|pikachu|super\s*mario|sonic\s*the|minecraft|fortnite|"
    r"harry\s*potter|hogwarts|mickey\s*mouse|simpsons|rick\s*and\s*morty|"
    r"game\s*of\s*thrones|iron\s*throne|delorean|rubik",
    # real people
    r"che\s*guevara|bob\s*marley|elvis|the\s*beatles|banksy|einstein|"
    r"marilyn\s*monroe|queen\s*elizabeth|king\s*charles|royal\s*family|"
    r"princess\s*diana",
    # marques and models
    r"ferrari|porsche|lamborghini|\bbmw\b|mercedes|\baudi\b|volkswagen|\bvw\b|"
    r"mini\s*cooper|land\s*rover|range\s*rover|harley|davidson|ducati|yamaha|"
    r"kawasaki|\bhonda\b|suzuki|triumph\s*motor|interceptor\s*car|"
    r"supermarine|spitfire|eurofighter|typhoon\s*aircraft|lancaster\s*bomber",
    # brands
    r"\bnike\b|adidas|\bpuma\b|gucci|rolex|playstation|\bxbox\b|nintendo|"
    r"jack\s*daniel|guinness|coca.?cola|\bpepsi\b|\blego\b|barbie|"
    r"\bapple\b\s*(logo|computer)",
]
RISK = re.compile("|".join(PATTERNS), re.I)


def risky(text):
    """True if this subject or phrase names something someone else owns."""
    return bool(RISK.search(text or ""))


def clean(items, key=None):
    """Drop the risky ones. Returns (kept, dropped)."""
    kept, dropped = [], []
    for it in items:
        (dropped if risky(key(it) if key else it) else kept).append(it)
    return kept, dropped


if __name__ == "__main__":
    import json, sys
    src = sys.argv[1] if len(sys.argv) > 1 else "subject_bank.json"
    kept, dropped = clean(json.load(open(src)))
    print(f"{len(dropped)} dropped of {len(kept) + len(dropped)}")
    for d in dropped:
        print("  ", d)
    json.dump(kept, open("subject_bank_clean.json", "w"), indent=1)
