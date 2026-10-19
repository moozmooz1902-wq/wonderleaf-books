#!/usr/bin/env python3
"""Titles and descriptions for the wall-art listings.

Three things this has to get right, and they pull against each other.

1. EBAY'S 80-CHARACTER TITLE LIMIT is hard. A title one character over is
   rejected at upload, and finding that out on a 3.8M-row file is finding it
   out too late. So every title is built, measured and TRIMMED here, and
   build_ebay.py asserts the limit on every row it writes.

2. THE TITLES MUST NOT ALL BE THE SAME SHAPE. 3.8M listings off one template
   is the near-duplicate problem again, in text instead of pixels - and eBay
   suppresses near-identical titles in search long before a buyer sees them.
   So there are several templates and the SKU picks one, which gives a stable
   spread without a random seed: the same SKU always gets the same title.

3. NOTHING MAY CLAIM WHAT THIS IS NOT. These are prints of generated
   artwork. Not hand-painted, not original, not signed, not limited. That is
   a legal control, not a quality preference, and ip_check.FORBIDDEN_CLAIMS
   is the list. check() below runs it on every title and description, and
   build_ebay.py refuses to write a row that fails.
"""
import json, os, re, sys
import hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ip_check

MAX_TITLE = 80

# How each technique reads in a title. The prompt vocabulary is snake_case
# and some of it would be wrong in a listing: "oil_impasto" is a LOOK, and
# saying "oil" alone edges towards "oil on canvas", which is a forbidden
# claim and also untrue - this is printed on paper.
TECH = {
    "charcoal": "Charcoal", "sketch": "Sketch", "linocut": "Linocut",
    "watercolour": "Watercolour", "gouache": "Gouache",
    "oil_impasto": "Impasto Style", "palette_knife": "Palette Knife Style",
    "ink_wash": "Ink Wash", "pastel": "Pastel", "collage": "Collage",
    "screenprint": "Screen Print Style", "risograph": "Riso Style",
    "monotype": "Monotype Style", "cyanotype": "Cyanotype Style",
}

KIND = {"place": "Landscape", "creature": "Animal", "botanical": "Botanical",
        "celestial": "Celestial", "stilllife": "Still Life",
        "architecture": "Architectural"}

# Composition, in words a buyer searches for rather than grammar codes.
GRAM = {
    "G1_window": "Window View", "G2_terrain": "Terrain", "G9_naive": "Naive",
    "G10_abstract": "Abstract", "G11_hardedge": "Geometric",
    "G3_habitat": "Habitat", "G4_portrait": "Portrait", "G7_chart": "Chart",
    "G8_minimal": "Minimal",
    "B1_specimen": "Specimen", "B2_vase": "In A Vase", "B3_scatter": "Scattered",
    "B4_meadow": "Meadow", "B5_single": "Single Stem",
    "C1_vast": "Vast Sky", "C2_disc": "Disc", "C3_row": "Phases",
    "C4_overland": "Over The Land",
    "S1_table": "On A Table", "S2_single": "Single Object",
    "S3_flatlay": "Flat Lay", "S4_shelf": "On A Shelf",
    "A1_elevation": "Elevation", "A2_street": "Street", "A3_detail": "Detail",
    "A4_wide": "Wide View",
}

PAL = {"duotone": "Duotone", "complementary": "Bold Colour",
       "neutral": "Neutral Tones", "monochrome": "Monochrome",
       "spectrum": "Colourful"}

# Each template is (parts...) joined with spaces; {s} subject, {t} technique,
# {k} kind, {g} composition, {p} palette. The tail carries the keywords a
# buyer actually types.
TEMPLATES = [
    "{s} {t} {k} Print - Framed Wall Art Picture",
    "{s} Wall Art Print - {t} {k} Framed Picture",
    "Framed {t} Print - {s} {k} Wall Art Picture",
    "{s} {g} {t} Print - Framed Wall Art",
    "{s} {k} Wall Art - {p} {t} Framed Print",
    "{t} {s} Print - {k} Framed Wall Art Picture",
]


def _sub(s):
    """Subject, title-cased, with the small words left alone."""
    small = {"a", "an", "and", "of", "the", "in", "on", "with", "at"}
    w = re.sub(r"\s+", " ", str(s)).strip().split()
    return " ".join(x if x in small and i else x[:1].upper() + x[1:]
                    for i, x in enumerate(w))


def title(job):
    """Build a title, then make it FIT. Trimming drops the optional middle
    before it touches the subject or the keyword tail: a buyer searches for
    the subject and for "framed wall art print", and neither may be the
    thing that falls off the end."""
    f = dict(s=_sub(job["subject"]), t=TECH.get(job["tech"], _sub(job["tech"])),
             k=KIND.get(job["kind"], ""), g=GRAM.get(job["gram"], ""),
             p=PAL.get(job["pal"], ""))
    h = int(hashlib.blake2b(job["sku"].encode(), digest_size=4).hexdigest(), 16)
    order = [TEMPLATES[h % len(TEMPLATES)]] + TEMPLATES
    for tpl in order:
        t = re.sub(r"\s+", " ", tpl.format(**f)).strip()
        t = re.sub(r"\s+-\s+-", " -", t).replace(" - - ", " - ")
        if len(t) <= MAX_TITLE:
            return t
    # Every template too long: keep the subject and the keywords, drop the
    # rest. Still measured, never assumed.
    t = f"{f['s']} Framed Wall Art Print"
    return t[:MAX_TITLE].rstrip(" -")


# THE SIZE THE LISTING ACTUALLY SELLS, read from the same place the
# variation rows get it. The first version listed all three A sizes in the
# description while the listing offered only A3 as a variation - a listing
# that advertises three sizes and sells one is a dispute waiting to happen,
# and it was caught by reading the finished file rather than by any check,
# because no check knows what the prose is claiming.
SIZE = json.load(open(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "ebay_plan.json")))["size"]


def description(job, t):
    """Plain HTML, no external assets, no claims that are not true."""
    kind = KIND.get(job["kind"], "").lower()
    tech = TECH.get(job["tech"], job["tech"]).lower()
    pal = PAL.get(job["pal"], "").lower()
    comp = GRAM.get(job["gram"], "")
    import html as H
    return (
      '<div style="font-family:Arial,Helvetica,sans-serif;max-width:720px">'
      f'<h2>{H.escape(t)}</h2>'
      f'<p>A {kind} wall art print in a {tech} style, '
      f'{"composed as " + H.escape(comp.lower()) + ", " if comp else ""}'
      f'in {pal}. Printed to order on heavyweight art paper and supplied '
      f'framed and ready to hang.</p>'
      '<h3>Frame</h3>'
      '<p>Choose <b>black</b>, <b>white</b> or <b>oak</b> at checkout. '
      'The main photograph shows the black frame.</p>'
      '<h3>Details</h3><ul>'
      '<li>Giclee-style print on heavyweight matte art paper</li>'
      '<li>Wooden moulding, glazed front, hanging fixture fitted</li>'
      f'<li>Size: {SIZE}</li>'
      '<li>Printed and framed in the United Kingdom</li>'
      '<li>Dispatched carefully packed in protective board</li>'
      '</ul>'
      '<h3>Please note</h3>'
      '<p>This is a printed reproduction of digitally created artwork. '
      'It is not a painting and it is not signed. Colours can vary slightly '
      'between screens and print.</p>'
      '<p>Message us before ordering if you need a different size and we '
      'will do our best to help.</p></div>')


def check(t, d=""):
    """Returns a list of problems; empty means the row may be written."""
    bad = []
    if not t or len(t) > MAX_TITLE:
        bad.append(f"title length {len(t)}")
    bad += [f"forbidden claim: {c}" for c in ip_check.check_listing(t, d)]
    return bad


if __name__ == "__main__":
    import json
    jobs = json.load(open(sys.argv[1]))
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    worst, bad = 0, 0
    for j in jobs[:n]:
        t = title(j); d = description(j, t)
        p = check(t, d)
        worst = max(worst, len(t))
        if p: bad += 1; print("PROBLEM", p, t)
    for j in jobs[:8]:
        t = title(j)
        print(f"{len(t):>3}  {t}")
    print(f"\nchecked {min(n,len(jobs)):,}  longest title {worst}  problems {bad}")
