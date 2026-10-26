#!/usr/bin/env python3
"""ONE function builds a product. The page and the feed are both rendered
from its output, and that is the whole anti-misrepresentation design.

WHY THIS FILE EXISTS AT ALL. The seller's previous shop was suspended for
misrepresentation and Google never said which rule. The failure modes that
produce that verdict are, overwhelmingly, DISAGREEMENTS - the feed says
GBP 29.99 and the page says GBP 24.99; the feed says in stock and the page
says sold out; the feed's title mentions a frame colour the page does not
offer; the page shows a framed photograph for an unframed product. Google's
own wording is "offers that represent you or your products in a way that
isn't accurate", and a feed that disagrees with its own landing page is
inaccurate by definition.

Those disagreements are nearly always structural: two code paths, written at
different times, both deciding what a product costs. The fix is not to check
them against each other afterwards - it is to make a second code path
impossible. `build()` returns the product. The Astro page renders that dict.
The feed serialises that dict. Neither computes a price, a title, an
availability or an image URL of its own.

The checker in preflight.py then proves the deployed page and the submitted
feed still agree, because a design that cannot drift is not the same thing
as a design that has been shown not to have drifted.

THE VARIANT URL RULE, which is the other half of it. Every variant is its
own product in the feed with its own [link], and that link carries ?frame=
and ?size=. The page MUST read those server-side and render that variant's
price, title and JSON-LD. If the page ignores them and always shows the
cheapest variant, then eight of every nine feed rows point at a page showing
a different price - which is the exact "price mismatch" disapproval that
turns into a misrepresentation suspension when it happens at scale.
"""
import hashlib, json, os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
WALLART = os.environ.get(
    "WALLART_DIR", "/home/user/wonderleaf-books/wallart-data")
sys.path.insert(0, HERE)
import taxonomy as T

# The seller's go-to prices, 22 Oct 2026, VAT inclusive, and the same two
# ladders their eBay listings use.
SIZES = [
    {"code": "a4", "label": "A4", "cm": "21 x 29.7 cm"},
    {"code": "a3", "label": "A3", "cm": "29.7 x 42 cm"},
    {"code": "a2", "label": "A2", "cm": "42 x 59.4 cm"},
]
FRAMED_PRICE = {"a4": 24.99, "a3": 29.99, "a2": 34.99}
UNFRAMED_PRICE = {"a4": 8.99, "a3": 12.99, "a2": 18.99}

# UNFRAMED IS A REAL TIER NOW, AND ONLY BECAUSE IT HAS ITS OWN PHOTOGRAPH.
#
# It was left out at first for a specific reason, not an oversight: every
# picture in the buckets is a framed mockup. build_ebay.py puts it plainly -
# "no unframed photograph was ever rendered" - and on eBay the unframed rows
# carry no PicURL, so eBay falls back to the main image. That is fine on
# eBay. In a Merchant Center feed every variant carries its own image, and
# selling an unframed print against a photograph of a framed one is an
# image/product mismatch: a disapproval on its own, and a misrepresentation
# pattern when it is every ninth row.
#
# catalogue/unframed.py removes that objection. It takes the generated panel
# that sits beside the mockups in R2, crops the same 11% off the bottom that
# render_worker.py crops (the fake-signature fix - the site states in writing
# that nothing is signed), and lays it on the cream wall with a paper shadow.
# So the unframed tier now shows an unframed print. Do not re-add it on top
# of the framed photographs if those files ever go missing; rebuild them.
FRAMES = [
    {"code": "black", "label": "Black", "wood": "black-painted wood",
     "framed": True},
    {"code": "white", "label": "White", "wood": "white-painted wood",
     "framed": True},
    {"code": "oak",   "label": "Oak",   "wood": "natural oak",
     "framed": True},
    {"code": "none",  "label": "Unframed", "wood": None, "framed": False},
]


def price_of(frame, size):
    return (FRAMED_PRICE if frame["framed"] else UNFRAMED_PRICE)[size["code"]]
COLOURWAY = 0   # one colourway per design in the opening range

_STORES = {s["bucket"]: s for s in json.load(
    open(os.path.join(WALLART, "stores.json")))["stores"]}


def config():
    return json.load(open(os.path.join(WEB, "business.config.json")))


def _slugify(s):
    s = re.sub(r"[''`]", "", str(s).lower())
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def slug(design):
    """The product page path. Stable, readable, and unique: the subject and
    style read well in a search result, and the SKU tail guarantees two
    'robin charcoal' designs cannot collide on one URL."""
    style = T.STYLE_BY_TECH.get(design["tech"], (None, design["tech"], None))[1]
    tail = design["sku"].split("-")[-1][:8]
    return f"{_slugify(design['subject'])}-{_slugify(style)}-{tail}"


def image(design, frame_code, base=""):
    """The photograph for one variant, absolute, for the feed.

    Framed variants come from the mockups in R2. The unframed one comes from
    catalogue/unframed.py and is served off the shop's own domain as a static
    asset, because it is rendered here rather than by the GPU run."""
    if frame_code == "none":
        return f'{base}/unframed/{design["sku"]}.jpg'
    st = _STORES[design["bucket"]]
    return (f'{st["pic_base"].rstrip("/")}/'
            f'{st["key_prefix"].strip("/")}/listing/'
            f'{design["sku"]}-{COLOURWAY}-{frame_code}.jpg')


def image_path(design, frame_code):
    """The same object's key, for serving through the shop's own image
    domain instead of the rate-limited r2.dev hostname."""
    if frame_code == "none":
        return f'unframed/{design["sku"]}.jpg'
    st = _STORES[design["bucket"]]
    return (f'{st["bucket"]}/{st["key_prefix"].strip("/")}/listing/'
            f'{design["sku"]}-{COLOURWAY}-{frame_code}.jpg')


def _sub(s):
    small = {"a", "an", "and", "of", "the", "in", "on", "with", "at", "yr"}
    w = re.sub(r"\s+", " ", str(s)).strip().split()
    return " ".join(x if x in small and i else x[:1].upper() + x[1:]
                    for i, x in enumerate(w))


# The style's name as an ADJECTIVE, which is not the same word as its
# navigation label. "Charcoal Drawings" is right at the top of a category
# page and wrong in the middle of a title: "St Abbs Charcoal Drawings -
# Framed Landscape Print" is not English. Two separate jobs, two separate
# vocabularies.
STYLE_ADJ = {
    "charcoal": "Charcoal", "sketch": "Pencil Sketch", "ink_wash": "Ink Wash",
    "linocut": "Linocut", "screenprint": "Screen Print",
    "watercolour": "Watercolour", "gouache": "Gouache", "pastel": "Pastel",
    "monotype": "Monotype", "cyanotype": "Cyanotype", "collage": "Collage",
    "risograph": "Riso Print", "oil_impasto": "Impasto",
    "palette_knife": "Palette Knife",
}
KIND_WORD = {"creature": "Animal", "botanical": "Botanical",
             "place": "Landscape", "celestial": "Celestial",
             "stilllife": "Still Life", "architecture": "Architectural"}

# SEVERAL TITLE SHAPES, PICKED BY THE SKU. One template across a thousand
# products is the same near-duplicate problem as one composition across a
# thousand pictures, in text instead of pixels - and the repo already
# learned that lesson on eBay, where near-identical titles get suppressed in
# search before a buyer ever sees them. Picking by SKU hash rather than at
# random means a product's title never changes between builds, which matters
# because the feed and the page both have to keep saying the same thing.
# The colour is in every template on purpose. It earns its place twice: it
# is what buyers actually type ("black and white moon print"), and it makes
# the title unique. Without it, two designs of the same subject in the same
# technique differing only in palette produced the SAME title - 10 collisions
# in a 1,000-design range, and the rate would climb as the range grows.
TITLE_TEMPLATES = [
    "{s} {a} Print - Framed {c} {k} Wall Art",
    "{s} - Framed {a} {k} Print in {c}",
    "Framed {a} Print of {s} - {c} {k} Wall Art",
    "{s} {k} Wall Art - Framed {c} {a} Print",
    "{s} {a} Wall Art - Framed {c} Print",
]


def _pick(options, design, salt):
    h = int(hashlib.blake2b(f"{salt}|{design['sku']}".encode(),
                            digest_size=4).hexdigest(), 16)
    return options[h % len(options)]


def group_title(design):
    """The design's name - the page <h1> and the feed's [item_group_title]."""
    adj = STYLE_ADJ.get(design["tech"], _sub(design["tech"]))
    kind = KIND_WORD.get(design["kind"], "")
    col = T.COLOUR_BY_PAL.get(design["pal"], (None, design["pal"], ""))[1]
    tpl = _pick(TITLE_TEMPLATES, design, "title")
    t = tpl.format(s=_sub(design["subject"]), a=adj, k=kind, c=col)
    # "Screen Print" and "Riso Print" already end in the word the template
    # then adds again: "Framed Screen Print Print of The Quantock Hills".
    t = re.sub(r"\bPrint Print\b", "Print", t)
    return re.sub(r"\s+", " ", t).replace(" - - ", " - ").strip()[:150]


def variant_title(design, frame, size):
    """Feed [title] for one variant. Says exactly what the buyer gets, which
    is the point: an accurate title is the cheapest compliance there is."""
    base = group_title(design)
    if not frame["framed"]:
        # THE GROUP TITLE SAYS "FRAMED". THE UNFRAMED ONE MUST NOT.
        #
        # Every TITLE_TEMPLATE contains the word Framed, because until this
        # tier existed every product was. Left alone, an unframed variant
        # came out as "St Abbs - Framed Charcoal Print - Unframed Print, A4",
        # which contradicts itself inside one line and is a disapproval on
        # the title alone, never mind what the picture shows.
        base = re.sub(r"\bFramed\s+", "", base)
        base = re.sub(r"\s+-\s+-\s+", " - ", base).strip(" -")
        return f"{base} - Unframed Print, {size['label']}"[:150]
    return f"{base} - {frame['label']} Frame, {size['label']}"[:150]


def _make_lines(cfg, framed=True):
    """How the print is made, said three ways so 2,508 feed rows are not
    2,508 copies of one sentence - and read from business.config.json rather
    than typed here, because the paper and the inks are also stated on the
    FAQ, the how-its-made page and the product page. Twelve hardcoded copies
    of 'heavyweight matte art paper' is how a feed and a page come to
    disagree, which is the whole failure this build exists to avoid."""
    f = cfg["fulfilment"]
    paper, inks, where = f["paper"], f["inks"], f["made_in"]
    if framed:
        return [
            f"Each print is made to order in {where}, printed with {inks} "
            f"on {paper}, then framed behind glazing with the hanging "
            f"fixture already fitted, so it arrives ready for the wall.",
            f"We print to order in {where} with {inks} on {paper}, and "
            f"frame it behind glazing with the hanging fixture fitted "
            f"before it is packed.",
            f"Printed to order in {where} with {inks} on {paper}, framed "
            f"behind glazing and fitted with its hanging fixture, so there "
            f"is nothing to assemble.",
        ]
    return [
        f"Each print is made to order in {where}, printed with {inks} on "
        f"{paper} and posted flat, so you can frame it yourself.",
        f"We print to order in {where} with {inks} on {paper}. The unframed "
        f"option is the sheet on its own, posted flat and board-backed.",
        f"Printed to order in {where} with {inks} on {paper}, unframed and "
        f"posted flat in a board-backed envelope.",
    ]


def description(design, frame=None, size=None, cfg=None):
    """Honest prose, generated per design so no two pages read alike.

    Every clause here is either a fact about the product or a statement of
    what it is NOT. The negative sentences are deliberate: 'printed
    reproduction of digitally created artwork', 'not a painting', 'not
    signed'. They cost nothing, they are true, and they close off the
    unreliable-claims and false-identity routes to a suspension before
    anyone can walk down them.
    """
    style = T.STYLE_BY_TECH.get(design["tech"], (None, design["tech"], ""))
    colour = T.COLOUR_BY_PAL.get(design["pal"], (None, "", ""))
    niche = T.NICHES[T.niche_for(design)[1]]
    subj = _sub(design["subject"])
    adj = STYLE_ADJ.get(design["tech"], _sub(design["tech"])).lower()
    comp = {"G1_window": "framed as a view through a window",
            "G2_terrain": "looking out across open land",
            "G3_habitat": "set in its own habitat",
            "G4_portrait": "as a close portrait",
            "G6_poster": "in the manner of a travel poster",
            "G7_chart": "laid out as a chart",
            "G9_naive": "drawn plainly, without fuss",
            "G11_hardedge": "reduced to hard-edged shapes",
            "B1_specimen": "as a botanical specimen",
            "B2_vase": "arranged in a vase",
            "B3_scatter": "scattered across the sheet",
            "B4_meadow": "massed as a meadow",
            "C1_vast": "under a vast sky",
            "C3_row": "shown as a row of phases",
            "C4_overland": "sitting low over the land",
            "S1_table": "arranged on a table",
            "S3_flatlay": "laid out flat from above",
            "S4_shelf": "resting on a shelf",
            "A1_elevation": "drawn square on, as an elevation",
            "A2_street": "seen along the street",
            "A3_detail": "closed right in on the detail",
            "A4_wide": "set in a wide view",
            }.get(design["gram"])

    # Four opening shapes, picked by SKU. Without this, every one of the 71
    # charcoal products in a 1,000-design range opened with the same two
    # sentences - about 1,500 identical words spread across the site, which
    # is the thin-content pattern that stops a new domain being indexed.
    # Mid-sentence, use the subject EXACTLY as the subject lists store it.
    # They are already cased correctly for what each thing is - "Bamburgh
    # Beach" and "Glen Coe" are proper nouns, "field spaniel" and "cow
    # parsley" are not - and lower-casing everything turned the places into
    # "a charcoal study of bamburgh beach", which reads as a typo on a page
    # asking someone for GBP 30.
    raw = re.sub(r"\s+", " ", str(design["subject"])).strip()
    openers = [
        f"{subj}, drawn in {adj} and printed as framed wall art"
        f"{', ' + comp if comp else ''}.",
        f"A {adj} study of {raw}{', ' + comp if comp else ''}, "
        f"printed and framed ready to hang.",
        f"Framed {adj} wall art: {raw}{', ' + comp if comp else ''}.",
        f"{subj} in {adj}{', ' + comp if comp else ''} - one of our "
        f"{niche['title'].lower()} prints.",
    ]
    bits = [
        _pick(openers, design, "open"),
        style[2],
        colour[2],
        "",
        _pick(_make_lines(cfg or config(),
                          framed=(frame is None or frame["framed"])),
              design, "make"),
    ]
    if frame and size:
        bits.append(
            f"This option is the {size['label']} size ({size['cm']}) in a "
            f"{frame['wood']} frame."
            if frame["framed"] else
            f"This option is the {size['label']} size ({size['cm']}) as an "
            f"unframed print - the sheet on its own, with no frame or mount, "
            f"posted flat in a board-backed envelope.")
    bits += [
        "",
        # Said on every product on purpose. These three sentences are the
        # cheapest compliance on the site: they are true, they cost nothing,
        # and they close off the false-claim routes to a suspension.
        "This is a printed reproduction of digitally created artwork. It is "
        "not a painting, it is not an original, and it is not signed or "
        "numbered. Colours can vary a little between a screen and a print.",
    ]
    return "\n".join(b for b in bits if b).strip()[:5000]


def build(design, cfg=None):
    """THE product record. Everything downstream reads this and only this."""
    cfg = cfg or config()
    section, niche = T.niche_for(design)
    base = f"https://{cfg['domain']}" if cfg.get("domain") else ""
    sl = slug(design)
    variants = []
    for frame in FRAMES:
        for size in SIZES:
            vid = f"{design['sku']}-{COLOURWAY}-{frame['code'][:3].upper()}-{size['label']}"
            if len(vid) > 50:                      # Google's [id] limit
                raise ValueError(f"variant id too long: {vid}")
            variants.append({
                "id": vid,
                "frame": frame["code"],
                "frame_label": frame["label"],
                "size": size["code"],
                "size_label": size["label"],
                "size_cm": size["cm"],
                "price": price_of(frame, size),
                "price_feed": f"{price_of(frame, size):.2f} {cfg['currency']}",
                "title": variant_title(design, frame, size),
                "description": description(design, frame, size, cfg),
                "link": f"{base}/art/{sl}?frame={frame['code']}&size={size['code']}",
                "image": image(design, frame["code"], base),
                "image_path": image_path(design, frame["code"]),
                "availability": "in_stock",
                "condition": "new",
                "colour": frame["label"],
                "material": (f'Wood frame, {cfg["fulfilment"]["paper"]}'
                             if frame["framed"] else
                             f'{cfg["fulfilment"]["paper"]}, unframed'),
            })
    return {
        "sku": design["sku"],
        "colourway": COLOURWAY,
        "slug": sl,
        "url": f"{base}/art/{sl}",
        "item_group_id": f"{design['sku']}-{COLOURWAY}",
        "title": group_title(design),
        "description": description(design, cfg=cfg),
        "section": section,
        "section_title": next(t for s, t, _ in T.SECTIONS if s == section),
        "niche": niche,
        "niche_title": T.NICHES[niche]["title"],
        "style": T.STYLE_BY_TECH.get(design["tech"],
                                     (design["tech"], design["tech"], ""))[0],
        "style_title": T.STYLE_BY_TECH.get(design["tech"],
                                           (None, design["tech"], ""))[1],
        "colour": T.COLOUR_BY_PAL.get(design["pal"], (design["pal"],
                                                      design["pal"], ""))[0],
        "colour_title": T.COLOUR_BY_PAL.get(design["pal"],
                                            (None, design["pal"], ""))[1],
        "rooms": T.NICHE_ROOMS.get(niche, []),
        "subject": _sub(design["subject"]),
        "product_type": T.product_type(design),
        "google_product_category": T.GOOGLE_PRODUCT_CATEGORY,
        "brand": cfg["brand"],
        "mpn": f"{design['sku']}-{COLOURWAY}",
        "bucket": design["bucket"],
        "default_frame": "black",
        "default_size": "a3",
        "price_from": min(v["price"] for v in variants),
        "variants": variants,
    }


GRAM_SHORT = {
    "G1_window": "Window View", "G2_terrain": "Open Land",
    "G3_habitat": "In Habitat", "G4_portrait": "Portrait",
    "G6_poster": "Poster Style", "G7_chart": "Chart", "G8_minimal": "Minimal",
    "G9_naive": "Naive", "G10_abstract": "Abstract",
    "G11_hardedge": "Hard Edge", "B1_specimen": "Specimen",
    "B2_vase": "In A Vase", "B3_scatter": "Scattered", "B4_meadow": "Meadow",
    "B5_single": "Single Stem", "C1_vast": "Vast Sky", "C2_disc": "Disc",
    "C3_row": "Phases", "C4_overland": "Over The Land", "S1_table": "On A Table",
    "S2_single": "Single Object", "S3_flatlay": "Flat Lay", "S4_shelf": "On A Shelf",
    "A1_elevation": "Elevation", "A2_street": "Street View",
    "A3_detail": "Detail", "A4_wide": "Wide View",
}


def build_all(designs, cfg=None):
    """THE ONLY SANCTIONED WAY TO BUILD THE CATALOGUE.

    `build()` is stateless, which is what makes it trustworthy - but it also
    means it cannot see that another design produced the same title. Two
    designs of the same subject in the same technique and palette, differing
    only in composition, collided 10 times in 1,000. Adding the colour to
    every title fixed the palette collisions and not these.

    So titles are made unique here, where the whole range is in view, by
    adding the composition to every member of a colliding group. It is done
    once, in one place, and the result is what both the page and the feed
    read - the database is built from this list and the feed is serialised
    from the same list, so there is still exactly one answer to "what is this
    product called".

    Deterministic: the groups are keyed on content and sorted by SKU, so the
    same selection always produces the same titles. A title that changed
    between builds would make the feed disagree with the cached page.
    """
    cfg = cfg or config()
    products = [build(d, cfg) for d in designs]
    by_title = {}
    for p, d in zip(products, designs):
        by_title.setdefault(p["title"], []).append((p, d))
    for title, group in by_title.items():
        if len(group) < 2:
            continue
        for p, d in sorted(group, key=lambda t: t[0]["sku"]):
            hint = GRAM_SHORT.get(d["gram"])
            if not hint:
                continue
            p["title"] = f"{title} ({hint})"[:150]
            for v in p["variants"]:
                v["title"] = (f'{p["title"]} - {v["frame_label"]} Frame, '
                              f'{v["size_label"]}')[:150]
    # Prove it, rather than trust it. A duplicate title left in the
    # catalogue is a duplicate <h1> and <title> on two indexable URLs, which
    # is the thin-content signal we are specifically trying not to send.
    seen = {}
    for p in products:
        if p["title"] in seen:
            raise SystemExit(
                f"build_all: duplicate title after dedupe:\n  {p['title']!r}\n"
                f"  {seen[p['title']]} and {p['sku']}\n"
                f"Add a distinguishing axis to TITLE_TEMPLATES or GRAM_SHORT.")
        seen[p["title"]] = p["sku"]
    slugs = {}
    for p in products:
        if p["slug"] in slugs:
            raise SystemExit(f"build_all: duplicate slug {p['slug']!r}")
        slugs[p["slug"]] = 1
    return products


def variant_of(product, frame=None, size=None):
    """Resolve ?frame=&size= to one variant, falling back to the defaults.

    The page uses this server-side. If it did not, the feed's links would
    point at pages showing a different price - the mismatch that this whole
    file exists to prevent."""
    f = frame or product["default_frame"]
    s = size or product["default_size"]
    for v in product["variants"]:
        if v["frame"] == f and v["size"] == s:
            return v
    for v in product["variants"]:
        if (v["frame"] == product["default_frame"]
                and v["size"] == product["default_size"]):
            return v
    return product["variants"][0]


def json_ld(product, variant, cfg=None):
    """schema.org Product for the page head.

    Google reads this as well as the feed, so it is generated from the same
    variant the page is showing and the same numbers the feed carries. A
    JSON-LD price that disagrees with the feed is a price mismatch even when
    the visible page is right."""
    cfg = cfg or config()
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": variant["title"],
        "description": variant["description"],
        "sku": variant["id"],
        "mpn": product["mpn"],
        "brand": {"@type": "Brand", "name": product["brand"]},
        "image": [variant["image"]],
        "category": product["product_type"],
        "material": variant["material"],
        "color": variant["colour"],
        "size": f'{variant["size_label"]} ({variant["size_cm"]})',
        "offers": {
            "@type": "Offer",
            "url": variant["link"],
            "priceCurrency": cfg["currency"],
            "price": f'{variant["price"]:.2f}',
            "itemCondition": "https://schema.org/NewCondition",
            "availability": "https://schema.org/InStock",
            "seller": {"@type": "Organization", "name": cfg["legal_name"]},
            "hasMerchantReturnPolicy": {
                "@type": "MerchantReturnPolicy",
                "applicableCountry": "GB",
                "returnPolicyCategory":
                    "https://schema.org/MerchantReturnFiniteReturnWindow",
                "merchantReturnDays": cfg["returns"]["window_days"],
                "returnMethod": "https://schema.org/ReturnByMail",
                "returnFees": (
                    "https://schema.org/ReturnShippingFees"
                    if cfg["returns"]["who_pays_return_postage"] == "customer"
                    else "https://schema.org/FreeReturn"),
            },
            "shippingDetails": {
                "@type": "OfferShippingDetails",
                "shippingRate": {
                    "@type": "MonetaryAmount",
                    "value": f'{cfg["fulfilment"]["delivery"][0]["price"]:.2f}',
                    "currency": cfg["currency"],
                },
                "shippingDestination": {
                    "@type": "DefinedRegion", "addressCountry": "GB"},
                "deliveryTime": {
                    "@type": "ShippingDeliveryTime",
                    "handlingTime": {
                        "@type": "QuantitativeValue", "minValue": 1,
                        "maxValue": cfg["fulfilment"]["dispatch_working_days"],
                        "unitCode": "DAY"},
                    "transitTime": {
                        "@type": "QuantitativeValue",
                        "minValue": cfg["fulfilment"]["delivery"][0]["min_days"],
                        "maxValue": cfg["fulfilment"]["delivery"][0]["max_days"],
                        "unitCode": "DAY"},
                },
            },
        },
    }


if __name__ == "__main__":
    sel = json.load(open(os.path.join(HERE, "selection.json")))
    cfg = config()
    # A product can be built before the identity fields are filled in; what
    # must not happen is a DEPLOY before then, which preflight.py enforces.
    cfg.setdefault("brand", None)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for d in sel["designs"][:n]:
        p = build(d, cfg)
        v = variant_of(p, "oak", "a2")
        print("=" * 70)
        print("slug     ", p["slug"])
        print("group    ", p["title"], f"({len(p['title'])} chars)")
        print("niche    ", p["section_title"], "/", p["niche_title"],
              "/", p["style_title"], "/", p["colour_title"])
        print("prodtype ", p["product_type"])
        print("variants ", len(p["variants"]))
        print("variant  ", v["id"], "|", v["price_feed"])
        print("vtitle   ", v["title"], f"({len(v['title'])} chars)")
        print("link     ", v["link"])
        print("image    ", v["image"])
        print("desc     ", p["description"][:220].replace("\n", " ") + " ...")
    longest = 0
    for d in sel["designs"]:
        p = build(d, cfg)
        longest = max(longest, max(len(x["title"]) for x in p["variants"]))
    print("=" * 70)
    print(f"{len(sel['designs']):,} designs x {len(FRAMES) * len(SIZES)} "
          f"variants = {len(sel['designs']) * len(FRAMES) * len(SIZES):,} "
          f"feed items")
    print(f"longest variant title: {longest} chars (Google limit 150)")
