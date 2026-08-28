#!/usr/bin/env python3
"""
Build the laser-focused UK t-shirt catalogue for the limited-limit store.

THE VARIATION RULE
    A variation counts only if it changes WHO IS SEARCHING.
    Recipient, occasion, age, nationality and sub-type do. Restyling does not.

    Critically, the recipient/occasion is carried IN THE DESIGN TEXT, not just
    the title - so the artwork differs too. Same image with a different title is
    the near-duplicate trap that buried the wall art.

Every design maps to a phrase a UK buyer types:
    "50th Birthday Gift For Grandad"     "Cockapoo Dad"
    "Electrician Grandad"                "Carp Fishing Legend"

Output: designs.json - one record per design, carrying the artwork lines and
the eBay title, ready for render_designs.py and generate_listings.py.
"""

import argparse, hashlib, json, random, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data"))
from banks import (RECIPIENTS, GRANDPARENT_NAMES, OCCASIONS, ALL_AGES,
                   MILESTONE_AGES, OCCUPATIONS, DOG_BREEDS, CAT_BREEDS,
                   HOBBIES, NATIONS, UK_PLACES, pretty,
                   BIKER_SUBJECTS, NORSE_SUBJECTS, GOTHIC_SUBJECTS, MUSIC_SCENES,
                   MILITARY_SUBJECTS, FOOD_DRINK, UK_PLACES_EXTRA, HOBBIES_EXTRA,
                   MOTIF_FRAMES)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose_slogans import art_lines, fix_articles

MAX = 80


def ordinal(n):
    """52 -> 52nd. The 11/12/13 exception included."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }".replace(" ", "")

# ---------------------------------------------------------------- title tail
# Measured from the competitor corpus: they spend >50% of the title on product
# and buyer language. "Mens Womens" makes the listing findable by both.
TAILS = [
    "Mens Womens T-Shirt Funny Novelty Gift Tee Top",
    "Mens Womens T-Shirt Novelty Gift Tee Top",
    "Mens Womens T-Shirt Funny Gift Tee",
    "Mens Womens T-Shirt Gift Tee",
    "Mens Womens T-Shirt Tee",
]


def pack_title(head, extras=()):
    """Fill 70-80 chars: head, then the longest tail that fits, then extras."""
    head = re.sub(r"\s+", " ", head).strip()
    for tail in TAILS:
        if len(head) + 1 + len(tail) <= MAX:
            title = f"{head} {tail}"
            used = {w.lower() for w in title.split()}
            for e in extras:
                if not e or e.lower() in title.lower():
                    continue
                if all(w.lower() in used for w in e.split()):
                    continue
                if len(title) + 1 + len(e) <= MAX:
                    title += " " + e
                    used.update(e.lower().split())
            return title
    return f"{head} {TAILS[-1]}"[:MAX].strip()


# ------------------------------------------------------------------ frames
# {s} = subject, {r} = recipient/role
OCCUPATION_FRAMES = [
    "{s} {r}", "World's Best {s} {r}", "{s} {r} The Legend", "Trust Me I'm A {s}",
    "Never Underestimate A {s}", "{s} Because Superhero Isn't A Job Title",
    "Grumpy Old {s}", "{s} By Day Legend By Night", "Off Duty {s}",
    "{s} Dictionary Definition", "Retired {s}", "Proud {s} {r}",
    "{s} Hourly Rate Watching Me Extra", "Don't Tell Me How To Do My Job {s}",
    "Evolution Of A {s}", "{s} Fuelled By Tea", "Certified {s}",
    "Apprentice {s} In Training", "It's A {s} Thing You Wouldn't Understand",
    "{s} Because Money Doesn't Grow On Trees", "Legend {s} Since Day One",
]
HOBBY_FRAMES = [
    "{s} {r}", "{s} Legend", "I'd Rather Be {s}", "Eat Sleep {s} Repeat",
    "{s} Is Cheaper Than Therapy", "Weekend Forecast {s}", "Addicted To {s}",
    "{s} Obsessed", "Born To {s}", "{s} Club Member", "Talk {s} To Me",
    "My Retirement Plan Is {s}", "Warning May Talk About {s}",
    "{s} Because Murder Is Wrong", "Powered By {s} And Tea", "Certified {s} Addict",
    "Life Is Better {s}", "{s} And Chill", "Professional {s} Enthusiast",
    "There's No Such Thing As Too Much {s}",
]
BREED_FRAMES = [
    "{s} {r}", "Proud {s} {r}", "{s} Lover", "Crazy {s} Person",
    "My {s} Thinks I'm Cool", "Easily Distracted By {s}", "{s} Squad",
    "I Work Hard So My {s} Can Live Better", "{s} Hair Don't Care",
    "Life Is Better With A {s}", "{s} Because People Are Rubbish",
    "Just A {r} Who Loves {s}", "{s} Mum And Dad Of The Year",
    "All You Need Is Love And A {s}", "{s} Whisperer", "Home Is Where My {s} Is",
    "Sorry I'm Late My {s} Needed Me", "{s} Rescue Squad",
]
BIRTHDAY_FRAMES = [
    "{o} Birthday {r}", "{a} Year Old Legend {r}", "Vintage {y} {o} Birthday",
    "Aged {a} Years To Perfection", "{a} Year Old Banger", "Made In {y} {a} Years",
    "Level {a} Complete", "{a} And Still Fabulous", "Limited Edition {y}",
    "{a} Years Young {r}", "Born In {y} {o} Birthday", "{o} Birthday Legend",
]
NATION_FRAMES = [
    "British Grown {s} Roots", "{s} Flag Pride", "Half {s} Half British",
    "Made In {s}", "{s} Blood British Heart", "Proud {s} Heritage",
    "{s} Roots Forever", "You Can Take The Person Out Of {s}",
    "{s} And Proud", "Born In {s} Living In Britain", "{s} Mum", "{s} Dad",
]
PLACE_FRAMES = [
    "{s} Born And Bred", "Proud To Be From {s}", "{s} Til I Die",
    "Made In {s}", "{s} Lass", "{s} Lad", "You Can't Beat {s}",
    "Home Is {s}", "{s} Legend", "{s} Roots",
]
GRANDPARENT_FRAMES = [
    "Best {s} Ever", "{s} Est {y}", "World's Greatest {s}", "Promoted To {s}",
    "{s} The Legend", "Like A Normal {s} Only Cooler", "{s} Of The Year",
    "Proud {s}", "Never Underestimate A {s}", "{s} And Proud Of It",
]

# Frames written to TAKE a recipient. Only these are crossed with roles.
ROLE_FRAMES_OCC = [
    "{s} {r}", "World's Best {s} {r}", "{s} {r} The Legend", "Proud {s} {r}",
    "Best {s} {r} Ever", "{s} {r} Of The Year", "My {r} Is A {s}",
    "Never Underestimate A {s} {r}",
]
ROLE_FRAMES_HOB = [
    "{s} {r}", "Best {s} {r} Ever", "World's Greatest {s} {r}",
    "Just A {r} Who Loves {s}", "{s} {r} Of The Year", "Proud {s} {r}",
]
ROLE_FRAMES_BREED = [
    "{s} {r}", "Proud {s} {r}", "Best {s} {r} Ever", "World's Greatest {s} {r}",
    "Just A {r} Who Loves {s}", "{s} {r} Of The Year",
]

ROLES = ["Dad", "Mum", "Grandad", "Nan", "Uncle", "Auntie", "Lover", "Owner"]
GIFT_ROLES = ["Dad", "Mum", "Grandad", "Nan", "Uncle", "Auntie", "Brother", "Sister"]


def rec(did, text, theme, cluster, extras=()):
    """One design record: artwork lines + packed eBay title."""
    text = fix_articles(re.sub(r"\s+", " ", text).strip())
    lines, emph = art_lines(text)
    return {
        "design_id": did,
        "stem": text,
        "theme": theme,
        "cluster": cluster,
        "ip_tier": "R0",
        "title": pack_title(text, extras),
        "art": {"lines": lines, "emphasis_line": emph,
                "ink": "light_on_dark", "garment": "black"},
        "tone": "flat",
    }


GIFT_OCCASIONS = ["Christmas", "Fathers Day", "Mothers Day", "Birthday",
                  "Retirement", "Anniversary"]


def build(year, limit=None, with_occasions=False):
    out, seen = [], set()

    def add(r):
        k = r["stem"].lower()
        if k in seen or len(r["stem"]) > 52:
            return
        seen.add(k)
        out.append(r)

    # 1. BIRTHDAY - every age is separately searched
    for age in ALL_AGES:
        frames = BIRTHDAY_FRAMES
        recips = RECIPIENTS if age in MILESTONE_AGES else RECIPIENTS[:14]
        for r_label, _ in recips:
            for i, f in enumerate(frames):
                add(rec(f"bd_{age}_{r_label.replace(' ','')}_{i}",
                        f.format(a=age, o=ordinal(age), y=year - age,
                                 r=f"For {r_label}"),
                        "uk_birthday", "birthday", (str(year - age), "Birthday")))

    # 2. OCCUPATIONS - solo frames once, role frames crossed with recipients
    for occ in OCCUPATIONS:
        s = pretty(occ)
        for i, f in enumerate(OCCUPATION_FRAMES):
            if "{r}" in f:
                continue
            add(rec(f"oc_{occ}_{i}", f.format(s=s, r=""), "uk_trades",
                    "occupation", (s, "Gift")))
        for role in GIFT_ROLES:
            for i, f in enumerate(ROLE_FRAMES_OCC):
                add(rec(f"oc_{occ}_{role}_{i}", f.format(s=s, r=role),
                        "uk_trades", "occupation", (s, role)))

    # 3. DOG AND CAT BREEDS
    for breed in DOG_BREEDS + CAT_BREEDS:
        s = pretty(breed)
        for i, f in enumerate(BREED_FRAMES):
            if "{r}" in f:
                continue
            add(rec(f"br_{breed}_{i}", f.format(s=s, r=""), "uk_animals", "breed", (s,)))
        for role in ROLES:
            for i, f in enumerate(ROLE_FRAMES_BREED):
                add(rec(f"br_{breed}_{role}_{i}", f.format(s=s, r=role),
                        "uk_animals", "breed", (s, role)))

    # 4. HOBBIES
    for hob in HOBBIES + HOBBIES_EXTRA:
        s = pretty(hob)
        for i, f in enumerate(HOBBY_FRAMES):
            if "{r}" in f:
                continue
            add(rec(f"hb_{hob}_{i}", f.format(s=s, r=""), "uk_outdoors", "hobby", (s,)))
        for role in GIFT_ROLES:
            for i, f in enumerate(ROLE_FRAMES_HOB):
                add(rec(f"hb_{hob}_{role}_{i}", f.format(s=s, r=role),
                        "uk_outdoors", "hobby", (s, role)))

    # 5. NATIONS / HERITAGE - the frames already read as standalone statements
    for nat in NATIONS:
        s = pretty(nat)
        for i, f in enumerate(NATION_FRAMES):
            add(rec(f"nt_{nat}_{i}", f.format(s=s), "uk_flags", "heritage", (s, "Flag")))
        for role in ["Dad", "Mum", "Grandad", "Nan"]:
            add(rec(f"nt_{nat}_{role}", f"Proud {s} {role}", "uk_flags",
                    "heritage", (s, role)))

    # 6. UK PLACES
    for pl in UK_PLACES + UK_PLACES_EXTRA:
        s = pretty(pl)
        for i, f in enumerate(PLACE_FRAMES):
            add(rec(f"pl_{pl}_{i}", f.format(s=s), "uk_flags", "place", (s,)))

    # 7. GRANDPARENT NAMES x OCCASION
    for gp in GRANDPARENT_NAMES:
        for i, f in enumerate(GRANDPARENT_FRAMES):
            add(rec(f"gp_{gp}_{i}", f.format(s=gp, y=year), "uk_family", "grandparent",
                    (gp, "Gift")))
        for occ_label, occ_kw in OCCASIONS[:6]:
            add(rec(f"gp_{gp}_o_{occ_label.replace(' ','')}",
                    f"Best {gp} Ever {occ_label}", "uk_family", "grandparent",
                    (occ_kw,)))

    # 8. IDENTITY MOTIFS - biker, Norse, gothic, music scene, military, food.
    # 40%+ of competitor catalogues, ~5% of the current one. These take
    # STATEMENT frames; nobody searches "Valknut Nan".
    MOTIF_BANKS = [
        (BIKER_SUBJECTS, "uk_biker", "biker", True),
        (NORSE_SUBJECTS, "uk_viking", "norse", False),
        (GOTHIC_SUBJECTS, "uk_skull_gothic", "gothic", False),
        (MUSIC_SCENES, "uk_music", "music", True),
        (MILITARY_SUBJECTS, "uk_military", "military", False),
        (FOOD_DRINK, "uk_funny_slogan", "food_drink", True),
    ]
    for bank, theme, cluster, takes_role in MOTIF_BANKS:
        for tok in bank:
            s_ = pretty(tok)
            for i, f in enumerate(MOTIF_FRAMES):
                add(rec(f"mo_{cluster}_{tok}_{i}", f.format(s=s_), theme, cluster, (s_,)))
            if takes_role:
                # "Biker Dad" and "Metalhead Grandad" are real searches;
                # "Valknut Nan" is not - hence the flag.
                for role in ["Dad", "Mum", "Grandad", "Nan", "Uncle"]:
                    for tpl in ("{s} {r}", "Best {s} {r} Ever", "World's Greatest {s} {r}"):
                        add(rec(f"mo_{cluster}_{tok}_{role}_{abs(hash(tpl))%97}",
                                tpl.format(s=s_, r=role), theme, cluster, (s_, role)))

    # 9. merge the measured slogan grid (50 joke frames x 93 subjects)
    try:
        slog = Path(__file__).resolve().parent.parent / "data" / "slogan_designs.json"
        if slog.exists():
            for d in json.loads(slog.read_text()):
                add(rec(d["design_id"], d["stem"], d.get("theme", "uk_funny_slogan"),
                        "slogan", ("Funny",)))
    except Exception as e:
        print(f"  (slogan grid not merged: {e})", file=sys.stderr)

    # 10. OPTIONAL occasion crossing.
    # "Christmas gift for a samoyed owner" is a genuine search, and the occasion
    # goes into the ARTWORK so the image differs too - not a title-only variant.
    # But these are thinner than the base set: turn on deliberately, not by
    # default.
    if with_occasions:
        base = [d for d in out if d["cluster"] in
                ("occupation", "hobby", "breed", "grandparent")
                and d["stem"].lower().startswith(("best ", "world's greatest "))]
        for d in base:
            for occ in GIFT_OCCASIONS:
                add(rec(f"{d['design_id']}_o{occ.replace(' ','')}",
                        f"{d['stem']} {occ}", d["theme"], d["cluster"], (occ, "Gift")))

    if limit:
        out = out[:limit]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="catalogue.json")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--with-occasions", action="store_true",
                    help="cross gift frames with Christmas / Fathers Day / etc. "
                         "Roughly 3x the catalogue, but thinner than the base set.")
    a = ap.parse_args()

    designs = build(a.year, a.limit, a.with_occasions)
    Path(a.out).write_text(json.dumps(designs, ensure_ascii=False))
    print(f"  {len(designs):,} designs -> {a.out}")

    if a.stats:
        import collections
        c = collections.Counter(d["cluster"] for d in designs)
        for k, v in c.most_common():
            print(f"    {v:7,}  {k}")
        L = [len(d["title"]) for d in designs]
        band = sum(1 for x in L if 70 <= x <= 80)
        print(f"\n  title length mean {sum(L)/len(L):.1f}   in 70-80 band "
              f"{band:,} ({band/len(L):.0%})   over 80: {sum(1 for x in L if x > 80)}")
        print(f"  distinct titles: {len({d['title'] for d in designs}):,} of {len(designs):,}")
        print("\n  samples:")
        for d in designs[::max(1, len(designs)//12)][:12]:
            print(f"    {d['title']}")


if __name__ == "__main__":
    main()
