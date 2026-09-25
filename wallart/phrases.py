#!/usr/bin/env python3
"""The phrase universe: every unique piece of wall-art text we can print.

Sources
  banks/niches/*.txt  hand-written phrases and {slot} templates, one niche per file
  banks/slots/*.txt   values that fill the slots (names, towns, breeds, ...)
  assets/eng-webbe_vpl.txt  public-domain scripture, filtered to short uplifting verses

Bank syntax
  header lines `key: value` until a line `---`
  then one phrase per line:
      " / "   a line break the layout must respect
      *word*  the accent word, set in the script face
      {slot}  first field of a slot value, {slot.1} its second field, ...

A template expands to the full cross product of its slots, but lazily and in a
scrambled, deterministic order - `{girl} & {boy} est. {year}` alone is 4.4M
phrases, so nothing is ever materialised that the generator does not ask for.

    python3 phrases.py --stats          supply per niche
    python3 phrases.py --sample 30      random phrases from every niche
"""
import argparse, math, random, re
from itertools import islice
from pathlib import Path

HERE = Path(__file__).resolve().parent
NICHES = HERE / "banks" / "niches"
AI_NICHES = HERE / "banks" / "niches_ai"          # written by expand_phrases.py
SLOTS = HERE / "banks" / "slots"
SCRIPTURE = HERE / "assets" / "eng-webbe_vpl.txt"

SLOT_RE = re.compile(r"\{(\w+)(?:\.(\d|PL))?\}")


def _read_slot(name):
    return [l.split("|") for l in (SLOTS / f"{name}.txt").read_text().splitlines() if l.strip()]


def load_slots():
    s = {n: _read_slot(n) for n in ["girl_names", "boy_names", "surnames", "towns",
                                     "counties", "drinks", "dog_breeds", "relations",
                                     "professions", "hobbies", "ages", "anniversaries"]}
    return {
        "girl": s["girl_names"], "boy": s["boy_names"],
        "name": s["girl_names"] + s["boy_names"],
        "surname": s["surnames"], "town": s["towns"], "county": s["counties"],
        "drink": s["drinks"], "breed": s["dog_breeds"], "rel": s["relations"],
        "job": s["professions"], "hobby": s["hobbies"], "age": s["ages"],
        "anniv": s["anniversaries"],
        "year": [[str(y)] for y in range(2026, 1949, -1)],
        "ryear": [[str(y)] for y in range(2027, 2019, -1)],
        "num": [[str(n)] for n in range(1, 201)],
    }


MAX_PER_TEMPLATE = 40_000     # no single pattern may flood the catalogue


class Template:
    """A phrase with slots, expanded on demand in a scrambled order."""

    def __init__(self, text, slots):
        text = re.sub(r"\{(\w+)\}s\b", r"{\1.PL}", text)   # "{surname}s" -> proper plural
        self.text = text
        self.names = list(dict.fromkeys(m.group(1) for m in SLOT_RE.finditer(text)))
        self.pools = [slots[n] for n in self.names]
        self.full = math.prod(len(p) for p in self.pools)
        self.size = min(self.full, MAX_PER_TEMPLATE)

    def __iter__(self):
        n = self.full
        # multiplicative scramble: visits every index once, but neighbours differ in
        # every slot, so the first few thousand are not all "Aaron", "Abigail", ...
        stride = next(p for p in range(int(n * 0.618) | 1, 10 * n + 3, 2)
                      if math.gcd(p, n) == 1) if n > 1 else 1
        for i in range(self.size):
            k = (i * stride) % n
            pick = {}
            for name, pool in zip(self.names, self.pools):
                k, r = divmod(k, len(pool))
                pick[name] = pool[r]
            out = SLOT_RE.sub(lambda m: _field(pick[m.group(1)], m.group(2)), self.text)
            out = re.sub(r"(\w)s's\b", r"\1s'", out)          # "Rogers's" -> "Rogers'"
            yield out[:1].upper() + out[1:]


def plural(name):
    """Family-name plural: Smith -> Smiths, Peters -> Peterses, Fox -> Foxes."""
    return name + ("es" if re.search(r"(s|x|z|ch|sh)$", name) else "s")


def _field(vals, idx):
    if idx == "PL":
        return plural(vals[0])
    i = int(idx or 0)
    return vals[i] if i < len(vals) else vals[0]


def load_niches():
    slots = load_slots()
    niches = {}
    for f in sorted(NICHES.glob("*.txt")) + sorted(AI_NICHES.glob("*.txt")):
        head, _, body = f.read_text().partition("\n---\n")
        meta = {}
        for line in head.splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
        lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#")]
        meta["id"] = f.stem
        meta["parent"] = meta.get("parent", f.stem)
        meta["noun"] = [x.strip() for x in meta.get("noun", "Wall Art Print").split("|")]
        meta["rooms"] = [x.strip() for x in meta.get("rooms", "Living Room").split("|")]
        meta["mood"] = [x.strip() for x in meta.get("mood", "minimal").split(",")]
        meta["occasion"] = [x.strip() for x in meta.get("occasion", "").split("|") if x.strip()]
        meta["fixed"] = [l for l in lines if not SLOT_RE.search(l)]
        meta["templates"] = [Template(l, slots) for l in lines if SLOT_RE.search(l)]
        niches[f.stem] = meta
    niches["scripture"] = scripture_niche()
    return niches


# ------------------------------------------------------------------- scripture

BOOKS = {
    "GEN": "Genesis", "EXO": "Exodus", "NUM": "Numbers", "DEU": "Deuteronomy",
    "JOS": "Joshua", "RUT": "Ruth", "1SA": "1 Samuel", "2SA": "2 Samuel",
    "1CH": "1 Chronicles", "2CH": "2 Chronicles", "NEH": "Nehemiah", "JOB": "Job",
    "PSA": "Psalm", "PRO": "Proverbs", "ECC": "Ecclesiastes", "SNG": "Song of Songs",
    "ISA": "Isaiah", "JER": "Jeremiah", "LAM": "Lamentations", "EZK": "Ezekiel",
    "DAN": "Daniel", "HOS": "Hosea", "JOL": "Joel", "MIC": "Micah", "NAM": "Nahum",
    "HAB": "Habakkuk", "ZEP": "Zephaniah", "ZEC": "Zechariah", "MAL": "Malachi",
    "MAT": "Matthew", "MRK": "Mark", "LUK": "Luke", "JHN": "John", "ACT": "Acts",
    "ROM": "Romans", "1CO": "1 Corinthians", "2CO": "2 Corinthians",
    "GAL": "Galatians", "EPH": "Ephesians", "PHP": "Philippians",
    "COL": "Colossians", "1TH": "1 Thessalonians", "2TH": "2 Thessalonians",
    "1TI": "1 Timothy", "2TI": "2 Timothy", "HEB": "Hebrews", "JAS": "James",
    "1PE": "1 Peter", "2PE": "2 Peter", "1JN": "1 John", "REV": "Revelation",
}
# books people actually hang on walls; narrative books produce odd picks
DEVOTIONAL = {"NUM", "DEU", "JOS", "RUT", "NEH", "PSA", "PRO", "ECC", "SNG", "ISA", "JER",
              "LAM", "MIC", "NAM", "ZEP", "MAT", "JHN", "ROM", "1CO", "2CO", "GAL", "EPH",
              "PHP", "COL", "1TH", "2TI", "HEB", "JAS", "1PE", "1JN"}
PERSONAL = re.compile(r"\b(you|your|I|my|me|we|us|our|LORD|God|Christ|Jesus)\b")
GOOD = re.compile(r"\b(love|loves|loved|joy|peace|hope|strength|strong|light|bless|blessed|"
                  r"trust|faith|grace|merciful|mercy|rejoice|shepherd|refuge|praise|thanks|"
                  r"good|kind|kindness|courage|comfort|rest|delight|fear not|don.t be afraid|"
                  r"heart|glory|lovingkindness|faithful|salvation|forever|shine|beautiful|"
                  r"wisdom|gentle|patient|pray|prayer|gladness|song|sing)\b", re.I)
BAD = re.compile(r"\b(kill|killed|slay|slain|blood|wrath|destroy|destroyed|enemies|enemy|"
                 r"death|die|died|dead|sin|sins|sinners|wicked|evil|curse|cursed|burn|"
                 r"sword|war|harlot|prostitute|adultery|vengeance|punish|anger|angry|"
                 r"hate|hated|fool|fools|lazy|sluggard|wine|drunk|beat|smite|struck|"
                 r"idol|idols|abomination|terror|trouble|weep|grave|Sheol|slave|slaves|"
                 r"Egypt|Babylon|Israel|Judah|Jerusalem|Zion|Pharaoh|circumcis\w*|flesh|"
                 r"offerings?|sacrifices?|vows?|calamity|darkness|priest|priests|king|Levites|Satan|devil|crush|breasts?|womb|"
                 r"disciplines?|suffer\w*|afflict\w*|shame|mourn\w*|tears|wept|rebuke\w*|"
                 r"judgement|judgment|condemn\w*|perish\w*|servant|servants)\b", re.I)


def scripture_niche():
    meta = {"id": "scripture", "name": "Bible Verse Prints",
            "noun": ["Bible Verse Print", "Scripture Wall Art", "Christian Verse Print"],
            "rooms": ["Living Room", "Bedroom", "Hallway", "Church"],
            "mood": ["sacred", "elegant", "script", "minimal"],
            "occasion": ["Easter", "Christening", "Confirmation"], "templates": [], "fixed": []}
    if not SCRIPTURE.exists():
        return meta
    for line in SCRIPTURE.read_text(encoding="utf-8").splitlines():
        code, _, rest = line.partition(" ")
        if code not in DEVOTIONAL:
            continue
        ref, _, text = rest.partition(" ")
        text = text.strip().replace("“", "").replace("”", "").replace("‘", "'").replace("’", "'")
        text = re.sub(r"^(A Psalm by David|A Psalm of David|A Prayer by [^.]*|A Song[^.]*|For the Chief Musician[^.]*)\.\s*", "", text)
        text = text.rstrip(",;:—-").strip()
        words = len(text.split())
        if not text[:1].isupper() or text.startswith(("And ", "But ", "For ", "Therefore", "So ")):
            continue
        if not (5 <= words <= 22) or not GOOD.search(text) or BAD.search(text) or not PERSONAL.search(text):
            continue
        if not text.endswith((".", "!", "?")):
            text += "."
        meta["fixed"].append(f"{text} ~ {BOOKS[code]} {ref}")
    return meta


# ------------------------------------------------------------------- iteration

def norm(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def iter_niche(meta, seen, seed=0):
    """Yield unique phrases for one niche: hand-written first, then templates
    round-robin so the output mixes every template rather than exhausting one."""
    fixed = list(meta["fixed"])
    random.Random(f"{seed}-{meta['id']}").shuffle(fixed)
    for t in fixed:
        k = norm(t)
        if k not in seen:
            seen.add(k)
            yield t
    gens = [iter(t) for t in meta["templates"]]
    while gens:
        alive = []
        for g in gens:
            for t in g:
                k = norm(t)
                if k not in seen:
                    seen.add(k)
                    yield t
                    alive.append(g)
                    break
        gens = alive


def supply(meta):
    return len(meta["fixed"]) + sum(t.size for t in meta["templates"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--sample", type=int, default=0)
    a = ap.parse_args()
    niches = load_niches()
    if a.stats or not a.sample:
        tot = 0
        for nid, m in sorted(niches.items(), key=lambda kv: -supply(kv[1])):
            s = supply(m); tot += s
            print(f"{nid:22s} fixed {len(m['fixed']):>6,}  templates {len(m['templates']):>3}  supply {s:>12,}")
        print(f"{'TOTAL':22s} {tot:>52,}")
    if a.sample:
        for nid, m in niches.items():
            got = list(islice(iter_niche(m, set(), seed=7), 400))
            print(f"\n== {nid}")
            for t in random.Random(1).sample(got, min(a.sample, len(got))):
                print("  ", t)


if __name__ == "__main__":
    main()
