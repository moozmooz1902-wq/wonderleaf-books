#!/usr/bin/env python3
"""Pick the opening catalogue: the best N designs, not the first N.

THE POINT OF THIS FILE. The eBay catalogue is 3.77M listings and it goes up
whole. The website is the opposite: a small curated range where every page a
buyer lands on is worth looking at. Two reasons, and the second is the one
that actually pays.

1. A buyer who opens a category and sees forty variations of the same idea
   leaves. Forty genuinely different pictures sells.
2. Google will not index, and may not approve, a brand-new domain carrying
   millions of near-identical pages. A small coherent shop reads as a real
   business. A huge thin one reads as a feed farm. Scale comes AFTER the
   account is healthy, and scale_plan() below says in what steps.

WHAT "BEST" MEANS HERE, AND WHERE EACH NUMBER COMES FROM. Nothing in the
weights is a hunch; each one is traceable:

* TECHNIQUE - from the seller's own eBay watchers, 168,819 listings against a
  1.05% base rate (research_notes/.../what_to_generate.md, mine_unsold.py).
  charcoal z=+5.9 (5.96%), sketch z=+4.4 (5.26%). NOTHING else in a 27-word
  technique vocabulary cleared significance - not watercolour, not linocut.
  So charcoal and sketch lead, the rest of the monochrome family follows as
  the nearest untested thing, and the painterly techniques are present in a
  minority because they are unproven, not disproven.
* PALETTE - the same finding read through colour: the winners are a hand-made
  monochrome mark, so monochrome and neutral lead.
* NICHE - UK places scored z=+12.6 as an aggregate (354 listings, 7.91%), the
  single strongest result in the project, and the moon z=+4.1. Those niches
  are boosted. Everything else sits at 1.0 - present, not pushed.
* COMPOSITION - the minimal/abstract/disc compositions are DOWN-weighted, not
  because they sell badly but because the duplicate audit found every
  near-twin in the first block was one of them. On a small range they are the
  fastest way to look repetitive.

AND THREE HARD FILTERS, which are refusals rather than weights:

* One colourway per design. A design exists in four recolours. Showing all
  four next to each other is the near-duplicate problem in its purest form,
  so the opening range takes colourway 0 only - the actual generated panel,
  not a recolour.
* A minimum Hamming distance of MIN_DISTANCE bits between the gradient hashes
  of any two chosen designs. "Near" is 24 of 256 bits in the eBay audit; this
  asks for far more than not-near.
* Framed only. See FRAMES_ONLY below - this one is a Google policy decision
  and it is the most important line in the file.
"""
import argparse, glob, json, os, random, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
WALLART = os.environ.get(
    "WALLART_DIR", "/home/user/wonderleaf-books/wallart-data")
sys.path.insert(0, HERE)
sys.path.insert(0, WALLART)
sys.path.insert(0, os.path.join(WALLART, "gen"))
import taxonomy as T

# FRAMED ONLY, AND WHY. The eBay listings sell an "Unframed Print Only"
# option whose variation carries no picture, so eBay falls back to the
# listing's main photo - which shows a black frame. The seller decided that,
# their existing listings have always worked that way, and on eBay it is
# their call to make.
#
# It cannot carry over to Google. In a Merchant Center feed every variant is
# its own product with its own [image_link], so an unframed print would be
# submitted with a photograph of a framed one. That is not a formatting
# quibble - it is the first line of the misrepresentation policy, "offers
# that represent you or your products in a way that isn't accurate", and it
# is exactly the kind of image/offer mismatch that gets an account actioned.
#
# There is no unframed photograph to use instead: the only images in the
# buckets are the three framed mockups, and cropping the artwork back out of
# them and uploading it needs the R2 write key, which lives on the RunPod
# template and deliberately not here.
#
# So the website launches framed only - three frame colours, three sizes,
# nine honest variants. Unframed can be added the day a real unframed
# photograph exists for every design in the range. Do not add it before.
FRAMES_ONLY = True

TECH_WEIGHT = {
    "charcoal": 1.00, "sketch": 0.90,          # measured winners
    "ink_wash": 0.55, "monotype": 0.50,        # nearest untested monochrome
    "cyanotype": 0.42, "linocut": 0.40,
    "screenprint": 0.34, "watercolour": 0.32,  # unproven on this audience
    "gouache": 0.28, "pastel": 0.26, "collage": 0.24,
    "risograph": 0.24, "oil_impasto": 0.22, "palette_knife": 0.22,
}
PAL_WEIGHT = {"monochrome": 1.00, "neutral": 0.85, "duotone": 0.72,
              "complementary": 0.45, "spectrum": 0.36}

# Niche boosts. Only where there is a measurement behind it.
NICHE_WEIGHT = collections.defaultdict(lambda: 1.0, {
    # UK places, aggregate z=+12.6
    "british-coast": 1.60, "mountains-hills": 1.45, "national-parks": 1.45,
    "british-countryside": 1.35, "lakes-rivers": 1.35, "islands": 1.30,
    "natural-landmarks": 1.30, "british-cities": 1.25,
    # the moon, z=+4.1
    "the-moon": 1.55, "constellations": 1.20, "sky-and-aurora": 1.15,
})

# Compositions that made up every near-twin in the duplicate audit. A small
# centred subject on an empty sheet, an all-over abstract field, and one big
# disc all look the same at thumbnail size whatever the subject is.
GRAM_PENALTY = {"G8_minimal": 0.35, "G10_abstract": 0.30, "C2_disc": 0.45,
                "B5_single": 0.70, "S2_single": 0.75}

# A proxy, not a detector: 17% of panels carry a small distant human figure
# (the for-scale kind), which breaks the seller's own no-figures rule, and
# the sweep that would find them needs a GPU pod. Street and wide townscape
# compositions are where a figure is most likely, so they are held back in
# the opening range. The contact sheet is what actually catches them - see
# sheet.py. Not a substitute for the sweep, and not pretending to be.
FIGURE_RISK = {"A2_street": 0.45, "A4_wide": 0.70, "G1_window": 0.85}

MIN_DISTANCE = 48       # of 256 bits. The eBay audit calls <=24 "near".
PER_NICHE_MIN = 12      # every category page must be worth opening
PER_NICHE_MAX = 28      # and none may dominate the range

# THE OPENING RANGE IS NARROW AND DEEP, NOT SMALL AND SPARSE.
#
# The seller's instruction on 25 Oct was to launch with very few products
# and add more once the account is accepted. Right call - but "fewer
# products" must not become "the same 53 categories with two prints in
# each". Google's editorial requirements make a site that looks unfinished
# a violation in its own right: placeholders, empty pages and links that do
# not "point to relevant content" are all listed under website quality. A
# category holding two items reads as exactly that.
#
# So a small launch narrows the RANGE rather than thinning the shelves.
# These twelve niches are the ones the measured demand actually points at -
# UK places (aggregate z=+12.6, the strongest result in the project) and the
# moon (z=+4.1) - plus the animal and botanical niches with the broadest
# general appeal. Twenty designs each is a shop that looks stocked.
#
# Deliberately absent: Still Life (which is where the alcohol subjects live,
# see RESTRICTED below) and Architecture. They come back at the next stage.
LAUNCH_NICHES = [
    "british-coast", "mountains-hills", "national-parks", "lakes-rivers",
    "the-moon", "constellations",
    "british-birds", "british-wildlife", "dogs",
    "garden-flowers", "wildflowers", "trees",
]

# RESTRICTED SUBJECTS - never submitted to Google, at any catalogue size.
#
# A print DEPICTING a negroni is not an alcoholic drink, and a human being
# would never confuse the two. Shopping's restricted-products screening is
# automated and reads the title and description, where the words "negroni",
# "whisky" and "champagne" sit in plain text. The downside of a wrong call
# is a restricted-product action on a young account; the upside of keeping
# eleven cocktail prints is nothing. So they are excluded by rule rather
# than by luck, and the rule survives the catalogue growing.
RESTRICTED = (
    r"\b(negroni|martini|old[- ]fashioned|whisky|whiskey|gin|rum|vodka|"
    r"tequila|mezcal|brandy|cognac|wine|champagne|prosecco|beer|ale|lager|"
    r"stout|cider|cocktail|aperol|campari|absinthe|sherry|vermouth|liqueur|"
    r"bourbon|sake|spritz|margarita|mojito|daiquiri|highball|negroni|"
    r"tobacco|cigar|cigarette|pipe smoke|vape)\b"
)

# TARGET MIX, AND WHY THE WINNERS DO NOT GET THE WHOLE SHOP.
#
# Scored on weights alone, the selection came out 99% charcoal and 100%
# monochrome. The weights were right and the result was still wrong, for
# three reasons:
#
# 1. The research that produced those weights says so itself: the winners
#    rest on single-digit watched counts and are "leads to test at modest
#    volume first, not licences to generate a million of anything". It also
#    says saturation is a real risk - charcoal won among the 151 charcoal
#    listings that existed, which cannot tell us how it does at 1,000.
# 2. A shop where every picture is a black-and-white charcoal drawing is a
#    shop a buyer cannot browse. The point of the range is that a category
#    page holds forty things that look different from each other.
# 3. It would teach us nothing. With no painterly or colour work in the
#    range there is no contrast to measure, so the first month of real
#    traffic could not confirm or overturn the watcher finding.
#
# So the winners get the largest share by a wide margin - charcoal and
# sketch together are 37% of the range against 14% of the grid, a 2.7x tilt -
# and everything else is present in enough volume to be judged. These are
# shares of the range, normalised; they are not probabilities.
TECH_MIX = {
    "charcoal": 22, "sketch": 15,              # measured winners, 37% total
    "ink_wash": 10, "monotype": 8,             # rest of the monochrome family
    "linocut": 8, "cyanotype": 5,
    "watercolour": 8, "screenprint": 6,        # unproven, present to test
    "gouache": 4, "pastel": 4, "collage": 3,
    "risograph": 3, "oil_impasto": 2, "palette_knife": 2,
}
PAL_MIX = {"monochrome": 30, "neutral": 25, "duotone": 20,
           "complementary": 15, "spectrum": 10}


def load_panels():
    """Every design that has a rendered, hashed panel, with its job metadata
    and its bucket. The hash files are the authority on what exists: a panel
    in R2 is done, a panel not in R2 is not."""
    import grid
    subjects = json.load(open(os.path.join(WALLART, "gen/subjects.json")))
    jobs = {j["sku"]: j for j in grid.expand(subjects)}
    # DEDUPE BY SKU. The same design is hashed into both hashes/ and
    # hashes_<bucket>/, so globbing hashes*/ and appending gave 1,428,569
    # rows for 960,516 designs - and the duplicates were landing in the
    # candidate list as if they were separate products. A design belongs to
    # exactly one store (allocate.py), so a second row for the same SKU is a
    # repeat of the same fact, not a second product.
    seen = {}
    for p in sorted(glob.glob(os.path.join(WALLART, "hashes*/*.jsonl"))):
        for line in open(p):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r["sku"] in seen:
                if seen[r["sku"]]["bucket"] != r["bucket"]:
                    raise SystemExit(
                        f"select: {r['sku']} hashed under two buckets "
                        f"({seen[r['sku']]['bucket']} and {r['bucket']}) - "
                        f"one design must live in one store, so the pictures "
                        f"for this SKU are ambiguous. Fix before building.")
                continue
            j = jobs.get(r["sku"])
            if not j:
                continue
            seen[r["sku"]] = dict(j, bucket=r["bucket"], h=int(r["h"], 2))
    return list(seen.values())


_RESTRICTED_RE = re.compile(RESTRICTED, re.I)


def restricted(p):
    """True if this design must never be submitted. Checked on the subject,
    which is what the title and description are built from."""
    return bool(_RESTRICTED_RE.search(str(p.get("subject", ""))))


def score(p, allow=None):
    hit = T.niche_for(p)
    if not hit:
        return 0.0, None
    _section, niche = hit
    if allow is not None and niche not in allow:
        return 0.0, None
    if restricted(p):
        return 0.0, None
    s = (TECH_WEIGHT.get(p["tech"], 0.2)
         * PAL_WEIGHT.get(p["pal"], 0.4)
         * NICHE_WEIGHT[niche]
         * GRAM_PENALTY.get(p["gram"], 1.0)
         * FIGURE_RISK.get(p["gram"], 1.0))
    return s, niche


def pick(panels, want, min_distance=MIN_DISTANCE,
         per_min=PER_NICHE_MIN, per_max=PER_NICHE_MAX, allow=None):
    """Highest-scoring designs, spread across niches, no two visually close.

    Two passes. The first guarantees every niche reaches per_min so no
    category page is a dead end. The second fills the rest by score. Both
    passes enforce the distance rule, which is what stops the top of the
    score list being forty charcoal coastlines that look alike.
    """
    scored = []
    for p in panels:
        s, niche = score(p, allow)
        if s > 0:
            scored.append((s, niche, p))
    scored.sort(key=lambda t: (-t[0], t[2]["sku"]))

    # Quotas. Niche keeps the shop browsable, technique and palette keep it
    # from collapsing onto the measured winner. A candidate is taken only if
    # it has room in all three.
    tech_cap = {k: max(1, round(want * v / sum(TECH_MIX.values())))
                for k, v in TECH_MIX.items()}
    pal_cap = {k: max(1, round(want * v / sum(PAL_MIX.values())))
               for k, v in PAL_MIX.items()}

    chosen, chosen_h = [], []
    n_niche = collections.Counter()
    n_tech = collections.Counter()
    n_pal = collections.Counter()
    taken = set()
    rejected_close = rejected_quota = 0

    def far_enough(h):
        nonlocal rejected_close
        for g in chosen_h:
            if bin(h ^ g).count("1") < min_distance:
                rejected_close += 1
                return False
        return True

    def take(s, niche, p):
        chosen.append(dict(p, _score=round(s, 4), _niche=niche))
        chosen_h.append(p["h"])
        taken.add(p["sku"])
        n_niche[niche] += 1
        n_tech[p["tech"]] += 1
        n_pal[p["pal"]] += 1

    def room(niche, p, niche_ceiling):
        nonlocal rejected_quota
        if (n_niche[niche] >= niche_ceiling
                or n_tech[p["tech"]] >= tech_cap.get(p["tech"], 0)
                or n_pal[p["pal"]] >= pal_cap.get(p["pal"], 0)):
            rejected_quota += 1
            return False
        return True

    by_niche = collections.defaultdict(list)
    for s, niche, p in scored:
        by_niche[niche].append((s, p))

    # pass 1 - floor every niche, so no category page is a dead end.
    #
    # This pass used to ignore the technique and palette caps, on the
    # reasoning that an empty category is worse than a skewed mix. That was
    # a mistake with a measurable size: 53 niches x 12 is 636 slots, this
    # pass runs before any other, and it takes each niche's highest scorer -
    # so it spent all 636 on charcoal monochrome and the mix caps never got
    # a say. The shop came out 64% one technique.
    #
    # So the floor is filled in two scans. The first respects the caps, which
    # is enough for almost every niche. The second runs only for a niche
    # still short afterwards and ignores the caps for that niche alone, which
    # keeps the original intent - no dead-end category - without letting it
    # decide the whole range.
    order = sorted(by_niche, key=lambda n: -NICHE_WEIGHT[n])
    for niche in order:
        for s, p in by_niche[niche]:
            if n_niche[niche] >= per_min or len(chosen) >= want:
                break
            if p["sku"] in taken or not room(niche, p, per_min):
                continue
            if far_enough(p["h"]):
                take(s, niche, p)
    relaxed = []
    for niche in order:
        if n_niche[niche] >= per_min:
            continue
        for s, p in by_niche[niche]:
            if n_niche[niche] >= per_min or len(chosen) >= want:
                break
            if p["sku"] in taken or not far_enough(p["h"]):
                continue
            take(s, niche, p)
            relaxed.append(niche)

    # pass 2 - fill by score under all three quotas
    for s, niche, p in scored:
        if len(chosen) >= want:
            break
        if p["sku"] in taken or not room(niche, p, per_max):
            continue
        if far_enough(p["h"]):
            take(s, niche, p)

    # pass 3 - if the quotas left the range short of `want`, relax the niche
    # ceiling (never the distance rule, and never the framed-only rule).
    if len(chosen) < want:
        for s, niche, p in scored:
            if len(chosen) >= want:
                break
            if p["sku"] in taken or not room(niche, p, per_max * 3):
                continue
            if far_enough(p["h"]):
                take(s, niche, p)

    return chosen, dict(candidates=len(scored), rejected_close=rejected_close,
                        rejected_quota=rejected_quota,
                        floor_relaxed=sorted(set(relaxed)),
                        short_by=max(0, want - len(chosen)))


def scale_plan():
    """The staged scale-up. Deliberately slow at the start: the point of the
    first stage is a clean account, not reach."""
    return [
        (1_000,     "Launch. Submit the feed, get the account and the site "
                    "verified, watch for disapprovals. Change nothing else."),
        (5_000,     "Only once free listings are serving and there are zero "
                    "policy issues for 14 straight days."),
        (25_000,    "Only once the first stage has held for another 30 days "
                    "and Search is indexing category pages."),
        (100_000,   "Add colourways 1-3 here, as a Colourway variant inside "
                    "the existing products, not as new products."),
        (500_000,   "Only with unframed photographs rendered, if unframed is "
                    "wanted by then."),
    ]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--want", type=int, default=240)
    ap.add_argument("--min-distance", type=int, default=MIN_DISTANCE)
    ap.add_argument("--out", default=os.path.join(HERE, "selection.json"))
    ap.add_argument("--niches", default=",".join(LAUNCH_NICHES),
                    help="comma-separated niche slugs to draw from, or "
                         "'all' to use the whole taxonomy")
    ap.add_argument("--per-min", type=int, default=PER_NICHE_MIN)
    ap.add_argument("--per-max", type=int, default=PER_NICHE_MAX)
    a = ap.parse_args()

    allow = None
    if a.niches and a.niches != "all":
        allow = [s.strip() for s in a.niches.split(",") if s.strip()]
        unknown = [n for n in allow if n not in T.NICHES]
        if unknown:
            raise SystemExit(f"select: unknown niche(s) {unknown}. "
                             f"Run `python3 taxonomy.py` for the list.")
        allow = set(allow)
        print(f"drawing from {len(allow)} niche(s): {', '.join(sorted(allow))}")

    panels = load_panels()
    print(f"rendered panels available: {len(panels):,}")
    n_restricted = sum(1 for p in panels if restricted(p))
    print(f"excluded as restricted subjects (alcohol/tobacco): "
          f"{n_restricted:,}")
    chosen, stats = pick(panels, a.want, a.min_distance,
                         a.per_min, a.per_max, allow)
    print(f"candidates scored: {stats['candidates']:,}   "
          f"rejected as visually close: {stats['rejected_close']:,}")
    print(f"chosen: {len(chosen):,}")

    print("\nby section / niche:")
    bysec = collections.defaultdict(collections.Counter)
    for c in chosen:
        bysec[T.NICHES[c["_niche"]]["section"]][c["_niche"]] += 1
    for s, t, _ in T.SECTIONS:
        tot = sum(bysec[s].values())
        print(f"  {t:<22} {tot:>5}   "
              + ", ".join(f"{n}:{v}" for n, v in bysec[s].most_common()))
    print("\nby technique:")
    for t, n in collections.Counter(c["tech"] for c in chosen).most_common():
        print(f"  {t:<15} {n:>5}  ({n/len(chosen):.0%})")
    print("\nby palette:")
    for t, n in collections.Counter(c["pal"] for c in chosen).most_common():
        print(f"  {t:<15} {n:>5}  ({n/len(chosen):.0%})")
    print("\nby bucket (where the pictures live):")
    for t, n in collections.Counter(c["bucket"] for c in chosen).most_common():
        print(f"  {t:<20} {n:>5}")

    # closest pair actually present, as a check on the distance rule
    worst, pair = 999, None
    hs = [(c["sku"], c["h"]) for c in chosen]
    for i in range(len(hs)):
        for k in range(i + 1, len(hs)):
            d = bin(hs[i][1] ^ hs[k][1]).count("1")
            if d < worst:
                worst, pair = d, (hs[i][0], hs[k][0])
    print(f"\nclosest pair in the chosen set: {worst} bits apart {pair}")
    print(f"(the eBay duplicate audit calls 24 or fewer 'near')")

    out = [{k: v for k, v in c.items() if k != "h"} for c in chosen]
    json.dump(dict(generated=len(out), framed_only=FRAMES_ONLY,
                   min_distance=a.min_distance, designs=out),
              open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
