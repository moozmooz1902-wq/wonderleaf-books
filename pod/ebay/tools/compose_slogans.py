#!/usr/bin/env python3
"""
Compose the slogan grid: JOKE TEMPLATE x SUBJECT -> design records.

The overnight eBay research found that UK slogan tees are not written one at a
time. A small bank of reusable joke frames is applied across every hobby, trade
and role - the SAME frames turn up in unrelated searches:

    "Fishing Cheaper Than Therapy"  /  "Gardening is Cheaper than Therapy"
    "The Rodfather" / "The Gardenfather" / "THE DOGFATHER" / "The Cat Father"
    "Warning May Start Talking About Fishing" / "...About Gardening"

So the slogan catalogue is a grid, exactly like the garment catalogue:

    50 templates x 93 subjects = 4,561 slogans
    x 17 garments x 7 stores   = 542,759 listings, all pure typography

A template declares `requires`; a subject supplies word FORMS. Composition only
happens when every required slot exists - that is what prevents the grammatical
garbage ("Grumpy Old Fishings Club") a naive cross-product produces.

Stdlib only.

Usage:
    python3 compose_slogans.py --out designs.json
    python3 compose_slogans.py --out designs.json --themes uk_outdoors,uk_biker
    python3 compose_slogans.py --out designs.json --max-len 46 --stats
"""

import argparse, json, re, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
TEMPLATES = json.loads((DATA / "slogan_templates.json").read_text())["templates"]
SUBJECTS = json.loads((DATA / "subjects.json").read_text())["subjects"]
THEME_BANK = {t["id"]: t for t in json.loads((DATA / "uk_theme_bank.json").read_text())["themes"]}

SLOT_RE = re.compile(r"\{(\w+)\}")

# "If A Electrician Can't Fix It" is the kind of thing that makes a catalogue look
# machine-made. Fix the article to match the SOUND of the next word, not its letter.
_VOWEL_SOUND = re.compile(r"^[aeiou]", re.I)
_YOU_WORDS = re.compile(r"^(uni|use|usu|ufo|euro|eul|ewe|one|once)", re.I)
_H_SILENT = re.compile(r"^(hour|honest|honour|heir)", re.I)
# single letters whose NAME starts with a vowel sound: F L M N R S X (and A E I O)
_ACRONYM_VOWEL = re.compile(r"^[AEFHILMNORSX](?:[A-Z0-9]|$)")
_ARTICLE_RE = re.compile(r"\b([Aa]n?)\s+(\S+)")


def _needs_an(word):
    w = word.strip("\"'([")
    if not w:
        return False
    if _ACRONYM_VOWEL.match(w) and w.upper() == w and len(w) > 1:
        return True          # "an MMA fighter", "an HGV driver"
    if _H_SILENT.match(w):
        return True          # "an hour"
    if _YOU_WORDS.match(w):
        return False         # "a uniform", "a European", "a one-off"
    return bool(_VOWEL_SOUND.match(w))


def fix_articles(text):
    def repl(m):
        art, nxt = m.group(1), m.group(2)
        want = "an" if _needs_an(nxt) else "a"
        want = want.capitalize() if art[0].isupper() else want
        return f"{want} {nxt}"
    return _ARTICLE_RE.sub(repl, text)


def compose(template, subject):
    """Fill a template's slots from a subject. Returns None if any slot is missing."""
    if not all(subject.get(r) for r in template["requires"]):
        return None
    text = template["pattern"]
    for slot in SLOT_RE.findall(text):
        val = subject.get(slot)
        if not val:
            return None
        text = text.replace("{" + slot + "}", val)
    return fix_articles(text)


def art_lines(slogan):
    """Break a slogan into a BALANCED stacked lockup.

    Greedy wrapping produced awkward breaks ("I DON'T NEED / THERAPY I JUST /
    NEED FISHING"). Instead, try every legal partition into 2-4 lines and pick
    the one whose lines are most even in length - even lines make the block read
    as one solid shape at thumbnail size, which is the whole point of the lockup.

    Emphasis goes on the LAST line, not the longest: the payoff word is the one
    that should carry the accent colour.
    """
    words = slogan.split()
    n_words = len(words)
    if n_words == 1:
        return [slogan], 0

    # Lines are scaled to fill the print width, so a line with MORE characters
    # gets a SMALLER font. Left alone that makes long slogans render as thin
    # strips while short ones fill the chest. Targeting ~13 characters per line
    # keeps type size - and therefore design scale - consistent across the
    # whole catalogue.
    target_n = max(2, min(4, round(len(slogan) / 13) or 2))

    candidates = []
    for n in range(2, min(4, n_words) + 1):
        best, best_score = None, None
        # partition indices
        def walk(start, remaining, acc):
            nonlocal best, best_score
            if remaining == 1:
                parts = acc + [" ".join(words[start:])]
                if any(not p for p in parts):
                    return
                lens = [len(p) for p in parts]
                spread = max(lens) - min(lens)
                # Even lines are good, but not at the cost of orphan words:
                # "Fishing / Is Cheaper / Than / Therapy" scores well on spread
                # and reads terribly. Penalise short lines and extra lines.
                runts = sum(max(0, 7 - L) ** 2 for L in lens)
                score = (spread * 2 + runts * 3
                         + abs(len(parts) - target_n) * 10)
                if best_score is None or score < best_score:
                    best, best_score = parts, score
                return
            for cut in range(start + 1, n_words - remaining + 2):
                walk(cut, remaining - 1, acc + [" ".join(words[start:cut])])
        walk(0, n, [])
        if best:
            candidates.append((best_score, best))

    if not candidates:
        return [slogan], 0
    # prefer the partition with the best balance overall
    _, lines = min(candidates, key=lambda c: c[0])
    return lines, len(lines) - 1


def build(themes=None, max_len=None):
    designs, seen = [], set()
    for subj in SUBJECTS:
        if themes and subj["theme"] not in themes:
            continue
        for tpl in TEMPLATES:
            if subj.get("kind", "activity") not in tpl.get("suits", ["activity"]):
                continue
            slogan = compose(tpl, subj)
            if not slogan:
                continue
            if max_len and len(slogan) > max_len:
                continue
            key = slogan.lower()
            if key in seen:
                continue
            seen.add(key)
            lines, emph = art_lines(slogan)
            theme = THEME_BANK.get(subj["theme"], {})
            designs.append({
                "design_id": f"slg_{tpl['id'][2:]}_{subj['id']}",
                "stem": slogan,
                "theme": subj["theme"],
                "ip_tier": tpl["ip_tier"],
                "template_id": tpl["id"],
                "subject_id": subj["id"],
                "tone": tpl["tone"],
                # black-tee only: light ink on transparent
                "art": {
                    "lines": lines,
                    "emphasis_line": emph,
                    "ink": "light_on_dark",
                    "garment": "black",
                },
                "extra_keywords": (theme.get("keyword_bank") or [])[:6],
                "adult_only": subj["theme"] == "uk_funny_slogan" and tpl["tone"] == "dark",
            })
    return designs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="designs.json")
    ap.add_argument("--themes", help="comma-separated theme ids to restrict to")
    ap.add_argument("--max-len", type=int, default=None,
                    help="drop slogans longer than this (keeps eBay titles inside 80 chars)")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    themes = set(a.themes.split(",")) if a.themes else None
    designs = build(themes, a.max_len)
    Path(a.out).write_text(json.dumps(designs, indent=1, ensure_ascii=False))
    print(f"{len(designs):,} slogan designs -> {a.out}")

    if a.stats:
        import collections
        by_theme = collections.Counter(d["theme"] for d in designs)
        by_tier = collections.Counter(d["ip_tier"] for d in designs)
        lens = [len(d["stem"]) for d in designs]
        print(f"  slogan length: mean {sum(lens)/len(lens):.0f}, max {max(lens)}")
        print(f"  ip tiers: {dict(by_tier)}")
        for t, c in by_theme.most_common():
            print(f"    {c:5d}  {t}")
        print("\n  samples:")
        for d in designs[::max(1, len(designs)//10)][:10]:
            print(f"    [{d['theme']:16s}] {d['stem']}")


if __name__ == "__main__":
    main()
