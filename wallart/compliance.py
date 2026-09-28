#!/usr/bin/env python3
"""IP / VeRO safety gate. Every phrase, title and AI-written phrase passes here.

eBay's VeRO programme lets rights owners have listings removed, and repeat
removals restrict the account. This blocks the things that trigger it:

  brand      company and product names (drinks, food, fashion, cars, retail, toys)
  franchise  films, TV, games, books, characters, catchphrases
  sport      clubs, leagues, teams, governing bodies
  origin     protected drink/food names (PDO/GI) enforced by trade bodies
  phrase     short phrases that are registered trade marks, song lyrics/titles,
             film lines, or copyrighted poems/hymns
  artist     artists whose work is still in copyright (died after 1955) or
             whose name is itself a trade mark; museum names (implied endorsement)
  person     celebrities and royals (personality/likeness rights, trade marks)

    python3 compliance.py            audit every bank, slot and the built catalogue
    python3 compliance.py "text"     check one phrase

The list is deliberately cautious: a false positive costs one phrase; a false
negative can cost a store. It cannot catch every song lyric - AI-written
phrases are additionally screened by the model (see expand_phrases.py), and
the list should grow whenever eBay removes a listing.
"""
import re, sys

W = lambda words: r"\b(?:" + "|".join(words) + r")\b"

RULES = {
    "brand": W([
        # drinks
        "aperol", "campari", "pimm'?s", "baileys", "guinness", "smirnoff", "gordon'?s", "hendrick'?s",
        "bombay sapphire", "tanqueray", "jack daniel'?s", "jameson", "johnnie walker", "glenfiddich",
        "bacardi", "captain morgan", "malibu", "kahlua", "jagermeister", "j[aä]germeister", "corona beer",
        "heineken", "carlsberg", "stella artois", "budweiser", "peroni", "birra moretti", "strongbow",
        "kopparberg", "magners", "thatchers", "brewdog", "red bull", "monster energy", "coca[- ]?cola",
        "coke", "pepsi", "fanta", "sprite", "irn[- ]?bru", "tango drink", "lucozade", "ribena", "vimto",
        "starbucks", "costa coffee", "nespresso", "nescaf[eé]", "tassimo", "yorkshire tea", "pg tips",
        "tetley", "twinings", "typhoo", "bovril", "horlicks", "ovaltine",
        # food & retail
        "nutella", "marmite", "cadbury", "galaxy chocolate", "maltesers", "kitkat", "kit kat", "mars bar",
        "twix", "snickers", "haribo", "walkers crisps", "pringles", "doritos", "heinz", "hp sauce", "oxo",
        "hovis", "warburtons", "kellogg'?s", "weetabix", "greggs", "mcdonald'?s", "burger king",
        "kfc", "nando'?s", "domino'?s", "pizza hut", "subway", "wetherspoons?", "tesco", "sainsbury'?s",
        "asda", "morrisons", "waitrose", "aldi", "lidl", "m&s", "marks (?:and|&) spencer", "primark",
        "ikea", "amazon", "ebay", "etsy", "argos", "boots the chemist", "boots pharmacy", "harrods", "selfridges", "john lewis",
        # fashion & beauty
        "vogue", "chanel", "gucci", "prada", "dior", "louis vuitton", "hermes", "herm[eè]s",
        "burberry", "tiffany'?s?", "versace", "armani", "balenciaga", "yves saint laurent", "ysl",
        "fendi", "valentino", "givenchy", "rolex", "cartier", "barbour", "nike", "adidas", "puma",
        "reebok", "vans", "converse", "dr\\.? martens", "ugg", "lush cosmetics", "mac cosmetics", "benefit cosmetics",
        "l'or[eé]al", "maybelline", "dove soap", "olaplex", "ghd", "dyson",
        # cars & vehicles
        "ford", "vauxhall", "volkswagen", "vw", "bmw", "mercedes", "audi", "porsche", "ferrari",
        "lamborghini", "maserati", "bentley", "rolls[- ]royce", "aston martin", "jaguar", "land rover",
        "range rover", "land rover defender", "mini cooper", "tesla motors", "toyota", "honda", "nissan", "kia",
        "hyundai", "volvo", "fiat", "vespa", "harley[- ]davidson", "ducati", "triumph motorcycles?", "kawasaki",
        "yamaha", "suzuki", "jcb", "john deere", "massey ferguson", "caterpillar", "michelin",
        # toys, games, tech
        "lego", "barbie", "hot wheels", "monopoly", "scrabble", "cluedo", "jenga", "rubik'?s?",
        "tetris", "nintendo", "playstation", "xbox", "minecraft", "fortnite", "roblox", "pok[eé]mon",
        "apple (?:inc|store|watch|mac)", "iphone", "google", "facebook", "instagram", "tiktok", "netflix", "spotify", "youtube",
    ]),
    "franchise": W([
        "disney", "pixar", "marvel", "dc comics", "star wars", "jedi", "yoda", "darth", "harry potter",
        "hogwarts", "gryffindor", "slytherin", "muggle", "mischief managed", "lord of the rings",
        "hobbit", "middle[- ]earth", "game of thrones", "winter is coming", "peaky blinders",
        "by order of", "friends tv", "how you doin", "central perk", "the office", "doctor who",
        "tardis", "dalek", "star trek", "beam me up", "disney frozen", "let it go", "hakuna matata",
        "lion king", "mickey", "minnie", "winnie the pooh", "paddington", "peppa", "bluey",
        "gruffalo", "hungry caterpillar", "peter rabbit", "thomas the tank", "paw patrol",
        "sesame street", "muppets?", "snoopy", "peanuts", "hello kitty", "moomins?", "tintin",
        "asterix", "shrek", "minions?", "despicable me", "toy story", "buzz lightyear",
        "to infinity and beyond", "spider[- ]?man", "batman", "superman", "wonder woman", "avengers",
        "gotham", "only fools", "lovely jubbly", "del boy", "gavin and stacey", "what's occurring",
        "downton", "bridgerton", "coronation street", "eastenders", "love island", "bake off",
        "strictly come dancing", "top gear", "james bond", "007", "shaken,? not stirred", "i'll be back",
        "may the force", "you had me at hello", "keep calm", "hot girl walk", "live laugh love",
        "the dash", "footprints in the sand", "do it anyway", "desiderata", "if you can keep your head",
        "the gruffalo", "oh,? the places you'll go", "dr\\.? seuss", "roald dahl", "willy wonka",
        "oompa", "mr\\.? men", "little miss", "wallace (?:and|&) gromit", "shaun the sheep",
        "wizard of oz", "somewhere over the rainbow", "there's no place like home",
    ]),
    "sport": W([
        "premier league", "fa cup", "uefa", "fifa", "champions league", "world cup", "wimbledon",
        "formula (?:1|one)", "f1", "wembley", "six nations", "manchester united", "man united",
        "man utd", "manchester city", "man city", "liverpool fc", "the kop", "you'll never walk alone",
        "arsenal", "gunners", "chelsea fc", "tottenham", "tottenham hotspur", "coyg", "coys", "everton",
        "newcastle united", "toon army", "west ham", "aston villa", "leeds united", "celtic fc",
        "rangers fc", "real madrid", "barcelona fc", "juventus", "mcfc", "mufc", "lfc", "afc bournemouth", "ynwa",
        "nfl", "nba", "mlb", "ufc", "wwe",
    ]),
    "origin": W([
        "champagne", "prosecco", "cava", "cognac", "armagnac", "tequila", "mezcal", "scotch whisky",
        "parmigiano", "parmesan", "feta", "roquefort", "stilton", "melton mowbray pork pies?", "cornish pasty",
        "cornish pasties", "arbroath smokie",
    ]),
    "phrase": "|".join(PHRASE_LIST := [
        r"\b(?:gin|wine|prosecco|rum|beer|cider|cocktail|martini|fizz|bubbly|vodka|whisky|mulled wine)\b[^.]*\bo'?clock\b",
        r"\bo'?clock\b[^.]*\b(?:gin|wine|prosecco|rum|beer|cocktail)\b",
        r"\bfive o'?clock somewhere\b", r"\beat,? sleep,? .{1,25},? repeat\b", r"\bros[eé],? all day\b",
        r"\bsip,? sip,? hooray\b", r"\bbeast mode\b", r"\btrain insane\b", r"\bjust dance\b",
        r"\bstrong is the new\b", r"\bblonde ambition\b", r"\bgirl ?boss\b", r"\bboss babe\b",
        r"\bstarted from the bottom\b", r"^let it be$", r"^let it go$", r"\bbang tidy\b",
        r"\bgert lush\b", r"\brawr means\b", r"\bhow great thou art\b", r"\bmorning has broken\b",
        r"\bgreat is thy faithfulness\b", r"\bgood times (?:and|&) tan lines\b", r"\bjust do it\b",
        r"\bimpossible is nothing\b", r"\bbecause you'?re worth it\b", r"\bi'?m lovin'? it\b",
        r"\bevery little helps\b", r"\bprobably the best\b", r"\bhave a break\b",
        r"\bfinger lickin'?\b", r"\bthink different\b", r"\bi (?:♥|❤|heart|love) ny\b",
        r"\bi love new york\b", r"\bgood vibes only\b", r"\bnot all (?:those )?who wander\b",
        r"\bsweet caroline\b", r"\bhere comes the sun\b", r"\ball you need is love\b",
        r"\bdon'?t worry,? be happy\b", r"\bdon'?t stop believin\b", r"\bsummer lovin\b",
        r"\bbaby,? it'?s cold outside\b", r"\bhave yourself a merry little\b",
        r"\blet it snow\b", r"\bit'?s the most wonderful time\b", r"\ball i want for christmas\b",
        r"\blast christmas\b", r"\brockin'? around\b", r"\bjingle bell rock\b", r"\bfeliz navidad\b",
        r"\bhakuna\b", r"\bmind the gap\b", r"\bthe dash\b", r"\bsomewhere over\b",
        r"\bdancing queen\b", r"\bmamma mia\b", r"\bbohemian rhapsody\b", r"\bwonderwall\b",
        r"\bthree little birds\b", r"\bevery little thing\b", r"\bstairway to heaven\b",
        r"\bhotel california\b", r"\bpiano man\b", r"\bperfect day\b", r"\bgod'?s own country\b",
        r"\bwhat would jesus do\b", r"\bwwjd\b",
    ]),
    "artist": W([
        "banksy", "picasso", "dal[ií]", "warhol", "edward hopper", "magritte", "haring", "basquiat",
        "lichtenstein", "hockney", "lowry", "vettriano", "frida kahlo", "kahlo", "chagall", "mir[oó]",
        "rothko", "pollock", "de kooning", "francis bacon", "lucian freud", "hirst", "tracey emin", "kusama", "koons",
        "kaws", "o'keeffe", "escher", "dr seuss", "beatrix potter", "quentin blake",
        # museum names imply endorsement - never in a title
        "met museum", "metropolitan museum", "smithsonian", "rijksmuseum", "national gallery",
        "tate modern", "tate britain", "tate gallery", "british museum", "louvre", "moma", "v&a", "victoria and albert", "van gogh museum",
    ]),
    "person": W([
        "beatles", "lennon", "mccartney", "elvis", "presley", "marilyn", "monroe", "audrey hepburn",
        "james dean", "bob marley", "muhammad ali", "princess diana", "lady di", "king charles",
        "queen elizabeth", "hm the queen", "prince william", "kate middleton", "royal family",
        "taylor swift", "beyonc[eé]", "rihanna", "adele", "ed sheeran", "harry styles",
        "one direction", "oasis", "noel gallagher", "liam gallagher", "david bowie", "freddie mercury", "madonna",
        "michael jackson", "dolly parton", "keith lemon", "gordon ramsay", "jamie oliver",
        "mary berry", "david attenborough", "churchill", "einstein", "mandela", "gandhi", "obama",
        "trump", "messi", "ronaldo", "beckham", "harry kane", "rashford", "lewis hamilton", "senna",
        "shakira", "drake", "kanye", "eminem", "nirvana", "cobain", "stormzy",
    ]),
}
META = re.compile(r"[\\?()\[\]|*+{}^$.]")


def _split(rule):
    """Word-list rules -> (set of plain phrases, regex for the few with patterns).
    Set lookups keep the check fast enough for millions of titles."""
    inner = rule[len(r"\b(?:"):-len(r")\b")]
    plain, pats = set(), []
    for w in inner.split("|"):
        if META.search(w.replace("\\.", "")) or "\\" in w:
            pats.append(w)
        else:
            plain.add(w.lower())
    return plain, (re.compile(r"\b(?:" + "|".join(pats) + r")\b", re.I) if pats else None)


WORDLISTS = {k: _split(v) for k, v in RULES.items() if k != "phrase"}
def _triggered(pattern):
    """Each phrase pattern runs only when its key word is in the text - a cheap
    substring test that skips ~all of them for ordinary titles."""
    words = re.findall(r"[a-z]{3,}", pattern.replace("\\b", " ").lower())
    trig = "clock" if "clock" in pattern else max(words, key=len) if words else ""
    return trig, re.compile(pattern, re.I)


PHRASES = [_triggered(p) for p in PHRASE_LIST]
TOKEN = re.compile(r"[a-z0-9àâäçéèêëîïôöùûüñ&'\u2019]+")


def check(text):
    """-> (rule, matched text) for the first rule hit, or None if clean."""
    t = text.replace("*", "").replace(" / ", " ")
    low = t.lower().replace("\u2019", "'")
    toks = TOKEN.findall(low)
    grams = set()
    for n in (1, 2, 3, 4):
        for i in range(len(toks) - n + 1):
            g = " ".join(toks[i:i + n])
            grams.add(g)
            if g.endswith("'s"):
                grams.add(g[:-2])
    for rule, (plain, rx) in WORDLISTS.items():
        hit = grams & plain
        if hit:
            return rule, hit.pop()
        if rx:
            m = rx.search(t)
            if m:
                return rule, m.group(0)
    for trig, rx in PHRASES:
        if trig in low:
            m = rx.search(t)
            if m:
                return "phrase", m.group(0)
    return None


def ok(text):
    return check(text) is None


def audit():
    from pathlib import Path
    here = Path(__file__).resolve().parent
    hits = []
    for f in sorted((here / "banks").rglob("*.txt")):
        body = f.read_text().partition("\n---\n")[2] if "niches" in f.parts[-2] else f.read_text()
        for n, line in enumerate(body.splitlines(), 1):
            if line.strip() and not line.startswith("#"):
                h = check(line.split("|")[0])
                if h:
                    hits.append((f.relative_to(here), n, line.strip(), *h))
    for h in hits:
        print(f"{h[0]}:{h[1]}  [{h[3]}: {h[4]}]  {h[2]}")
    print(f"\n{len(hits)} bank lines would be blocked")
    return hits


if __name__ == "__main__":
    if len(sys.argv) > 1:
        r = check(" ".join(sys.argv[1:]))
        print("BLOCKED" if r else "ok", r or "")
    else:
        audit()
