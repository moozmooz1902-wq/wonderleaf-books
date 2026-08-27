#!/usr/bin/env python3
"""
eBay UK listing-grid generator.

    LISTINGS = DESIGNS x PRODUCTS x STORES
               (size and colour are VARIATIONS INSIDE a listing, never rows)

This is the mechanic reverse-engineered from t-shirt-junky, love_tshirts and
canvasartshop: they do not invent a million ideas, they invent a design library
and multiply it across a product grid. 20,000 designs x 17 garments x 3 stores
is 1,020,000 listings.

Titles are ASSEMBLED, not written - packed into eBay's 70-80 character band by
greedily adding theme keywords until the next one would break 80. Not one of the
600 competitor titles sampled exceeded 80 characters.

Stdlib only. Streams to JSONL/CSV so it does not hold the grid in memory.

Usage
-----
  # built-in pure-grid themes (no artwork needed beyond one treatment)
  python3 generate_listings.py flags     --stores 3 --out flags.jsonl
  python3 generate_listings.py birthdays --stores 3 --year 2026 --out bdays.jsonl

  # your own design library
  python3 generate_listings.py designs --library designs.json --stores 3 --out all.jsonl

  # wall art
  python3 generate_listings.py art --library artworks.json --stores 2 --out art.jsonl

  # how big would the grid be?
  python3 generate_listings.py estimate --designs 20000 --stores 3

Design library format (JSON list):
  [{"design_id":"blk_cafe_racer_01","stem":"Cafe Racer Biker Motorbike Motorcycle",
    "theme":"uk_biker","ip_tier":"R0","extra_keywords":["Custom Bike","Enthusiast"]}]
"""

import argparse, csv, hashlib, itertools, json, re, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
MATRIX = json.loads((DATA / "product_matrix.json").read_text())
THEMES = {t["id"]: t for t in json.loads((DATA / "uk_theme_bank.json").read_text())["themes"]}

TITLE_MAX = MATRIX["_meta"]["ebay_title_limit"]          # 80
TITLE_MIN, TITLE_HI = MATRIX["_meta"]["title_target_band"]  # 70, 80
APPAREL = MATRIX["apparel_products"]
WALL_ART = MATRIX["wall_art_products"]

# Per-store keyword bias so the same design+product in two stores is not byte-identical.
STORE_BIAS = [
    ["Gift", "Present", "Unisex"],
    ["Top", "Tee", "Novelty"],
    ["Mens", "Quality", "New"],
    ["Ladies", "Cotton", "Casual"],
    ["Birthday", "Xmas", "Idea"],
    ["UK", "Fast Post", "Premium"],
    ["Adult", "Classic", "Fit"],
]


# --------------------------------------------------------------- title packing

def pack_title(stem, suffix, keywords, limit=TITLE_MAX):
    """Greedily fill the gap between stem and suffix with keywords, never exceeding limit.

    Competitor titles are `{design stem} {padding} {product suffix}` sized to the
    70-80 band. Duplicate tokens are dropped - eBay does not reward repetition and
    the space is better spent on a new term.
    """
    base = f"{stem} {suffix}".strip()
    if len(base) > limit:
        # stem itself is too long: trim stem words from the right until it fits
        words = stem.split()
        while words and len(" ".join(words) + " " + suffix) > limit:
            words.pop()
        return " ".join(words + suffix.split())[:limit].strip()

    seen = {w.lower().strip(",") for w in base.split()}
    head = stem
    for kw in keywords:
        if kw.lower() in seen:
            continue
        candidate = f"{head} {kw} {suffix}".strip()
        if len(candidate) <= limit:
            head = f"{head} {kw}"
            seen.update(w.lower() for w in kw.split())
    return f"{head} {suffix}".strip()


def price_for(product, store_ix):
    lo, hi = product["price_gbp"]
    # tiny per-store spread so stores are not price-identical, kept inside the band
    bump = round(store_ix * 0.30, 2)
    return {"from_gbp": round(lo + bump, 2), "to_gbp": round(hi + bump, 2)}


def variations_for(product):
    """Size/colour become VARIATIONS INSIDE the listing - this is the policy-critical bit."""
    axes = {}
    for axis in product.get("variation_axes", []):
        vals = product.get(axis if axis != "colour" else "colours") or product.get(axis)
        if axis == "colour":
            vals = product.get("colours")
        if axis == "size":
            vals = product.get("sizes")
        if axis == "frame_colour":
            vals = product.get("frame_colour")
        if vals:
            axes[axis] = vals
    count = 1
    for v in axes.values():
        count *= len(v)
    return axes, count


def sku(*parts):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:12]


# ----------------------------------------------------- compatibility gating

KIDS_PRODUCTS = {"kids_tee", "kids_tee_bg", "kids_sweat", "kids_hoodie"}
WOMENS_PRODUCTS = {"womens_wide", "womens_petite"}
NON_GARMENT = {"apron"}

# A naive cartesian product emits "73rd Birthday ... Kids Sweatshirt Jumper" and
# "Rude Slogan ... Kids T-Shirt". Those rows are what make a big catalogue read as
# spam. Gate the grid instead of shipping the noise.
def compatible(design, product):
    pid = product["id"]
    theme = design.get("theme")

    # Never put adult-humour or offensive content on childrenswear.
    if pid in KIDS_PRODUCTS and (theme in {"uk_funny_slogan"} or design.get("adult_only")):
        return False

    # Birthday grids: match the age to the garment's wearer.
    age = design.get("age")
    if age is not None:
        if pid in KIDS_PRODUCTS and not (3 <= age <= 15):
            return False
        if pid not in KIDS_PRODUCTS and age < 16:
            return False
        if pid in NON_GARMENT and age < 18:
            return False

    # "Mens ..." copy on a womens cut reads wrong; the padding is gendered.
    if pid in WOMENS_PRODUCTS and design.get("mens_only"):
        return False

    # Explicit per-design opt-outs.
    if pid in set(design.get("exclude_products", [])):
        return False
    return True


# --------------------------------------------------------------- row emitters

def apparel_rows(designs, stores):
    """designs: iterable of dicts with design_id, stem, theme, ip_tier, extra_keywords."""
    seen = set()
    for d in designs:
        theme = THEMES.get(d.get("theme"), {})
        kw = list(d.get("extra_keywords", [])) + list(theme.get("keyword_bank", []))
        for product in APPAREL:
            if not compatible(d, product):
                continue
            for s in range(stores):
                key = (d["design_id"], product["id"], s)
                if key in seen:
                    continue
                seen.add(key)
                title = pack_title(d["stem"], product["suffix"], STORE_BIAS[s % len(STORE_BIAS)] + kw)
                axes, n = variations_for(product)
                yield {
                    "sku": sku(*key),
                    "store_ix": s,
                    "design_id": d["design_id"],
                    "product_id": product["id"],
                    "theme": d.get("theme"),
                    "ip_tier": d.get("ip_tier", "R0"),
                    "title": title,
                    "title_len": len(title),
                    "price": price_for(product, s),
                    "variation_axes": axes,
                    "variation_count": n,
                }


def art_rows(artworks, stores):
    """artworks: dicts with design_id, stem (e.g. 'HOKUSAI, THE GREAT WAVE OFF KANAGAWA')."""
    seen = set()
    for a in artworks:
        kw = list(a.get("extra_keywords", []))
        for product in WALL_ART:
            for fi, suffix in enumerate(product["suffix_pool"]):
                for s in range(stores):
                    key = (a["design_id"], product["id"], fi, s)
                    if key in seen:
                        continue
                    seen.add(key)
                    title = pack_title(a["stem"], suffix, STORE_BIAS[s % len(STORE_BIAS)] + kw)
                    axes, n = variations_for(product)
                    yield {
                        "sku": sku(*key),
                        "store_ix": s,
                        "design_id": a["design_id"],
                        "product_id": product["id"],
                        "format_variant": fi,
                        "theme": a.get("theme", "wall_art"),
                        "ip_tier": a.get("ip_tier", "R0"),
                        "title": title,
                        "title_len": len(title),
                        "price": price_for(product, s),
                        "variation_axes": axes,
                        "variation_count": n,
                    }


# --------------------------------------------------- built-in pure-grid themes

COUNTRIES = """Albania Algeria Angola Antigua Argentina Armenia Australia Austria Bangladesh Barbados
Belarus Belgium Belize Bolivia Bosnia Botswana Brazil Bulgaria Cameroon Canada Chile China Colombia
Congo Croatia Cuba Cyprus Czechia Denmark Dominica Ecuador Egypt Estonia Ethiopia Fiji Finland France
Gambia Georgia Germany Ghana Greece Grenada Guyana Haiti Honduras Hungary Iceland India Indonesia Iran
Iraq Ireland Israel Italy Jamaica Japan Jordan Kenya Kosovo Kuwait Latvia Lebanon Liberia Libya
Lithuania Luxembourg Malawi Malaysia Maldives Malta Mauritius Mexico Moldova Montenegro Morocco
Mozambique Namibia Nepal Netherlands Nigeria Norway Pakistan Panama Paraguay Peru Philippines Poland
Portugal Romania Russia Rwanda Samoa Senegal Serbia Seychelles Singapore Slovakia Slovenia Somalia
Spain Sudan Sweden Switzerland Syria Taiwan Tanzania Thailand Trinidad Tunisia Turkey Uganda Ukraine
Uruguay Venezuela Vietnam Wales Scotland England Yemen Zambia Zimbabwe""".split()

FLAG_TREATMENTS = ["Torn", "Curled", "Distressed", "Love"]

# Competitor titles use the DEMONYM on second mention ("Torn Morocco Flag Moroccan Day
# Football"). Irregulars are listed; the rest fall back to a suffix rule, and anything
# we cannot form confidently simply omits the demonym rather than inventing a wrong one.
DEMONYM = {
    "Albania":"Albanian","Argentina":"Argentine","Australia":"Australian","Austria":"Austrian",
    "Bangladesh":"Bangladeshi","Barbados":"Barbadian","Belarus":"Belarusian","Belgium":"Belgian",
    "Brazil":"Brazilian","Bulgaria":"Bulgarian","Cameroon":"Cameroonian","Canada":"Canadian",
    "Chile":"Chilean","China":"Chinese","Colombia":"Colombian","Croatia":"Croatian","Cuba":"Cuban",
    "Cyprus":"Cypriot","Czechia":"Czech","Denmark":"Danish","Dominica":"Dominican","Ecuador":"Ecuadorian",
    "Egypt":"Egyptian","England":"English","Estonia":"Estonian","Ethiopia":"Ethiopian","Fiji":"Fijian",
    "Finland":"Finnish","France":"French","Georgia":"Georgian","Germany":"German","Ghana":"Ghanaian",
    "Greece":"Greek","Grenada":"Grenadian","Guyana":"Guyanese","Haiti":"Haitian","Honduras":"Honduran",
    "Hungary":"Hungarian","Iceland":"Icelandic","India":"Indian","Indonesia":"Indonesian","Iran":"Iranian",
    "Iraq":"Iraqi","Ireland":"Irish","Israel":"Israeli","Italy":"Italian","Jamaica":"Jamaican",
    "Japan":"Japanese","Jordan":"Jordanian","Kenya":"Kenyan","Kosovo":"Kosovan","Kuwait":"Kuwaiti",
    "Latvia":"Latvian","Lebanon":"Lebanese","Liberia":"Liberian","Libya":"Libyan","Lithuania":"Lithuanian",
    "Luxembourg":"Luxembourgish","Malawi":"Malawian","Malaysia":"Malaysian","Maldives":"Maldivian",
    "Malta":"Maltese","Mauritius":"Mauritian","Mexico":"Mexican","Moldova":"Moldovan",
    "Montenegro":"Montenegrin","Morocco":"Moroccan","Mozambique":"Mozambican","Namibia":"Namibian",
    "Nepal":"Nepalese","Netherlands":"Dutch","Nigeria":"Nigerian","Norway":"Norwegian",
    "Pakistan":"Pakistani","Panama":"Panamanian","Paraguay":"Paraguayan","Peru":"Peruvian",
    "Philippines":"Filipino","Poland":"Polish","Portugal":"Portuguese","Romania":"Romanian",
    "Russia":"Russian","Rwanda":"Rwandan","Samoa":"Samoan","Scotland":"Scottish","Senegal":"Senegalese",
    "Serbia":"Serbian","Seychelles":"Seychellois","Singapore":"Singaporean","Slovakia":"Slovak",
    "Slovenia":"Slovenian","Somalia":"Somali","Spain":"Spanish","Sudan":"Sudanese","Sweden":"Swedish",
    "Switzerland":"Swiss","Syria":"Syrian","Taiwan":"Taiwanese","Tanzania":"Tanzanian","Thailand":"Thai",
    "Trinidad":"Trinidadian","Tunisia":"Tunisian","Turkey":"Turkish","Uganda":"Ugandan",
    "Ukraine":"Ukrainian","Uruguay":"Uruguayan","Venezuela":"Venezuelan","Vietnam":"Vietnamese",
    "Wales":"Welsh","Yemen":"Yemeni","Zambia":"Zambian","Zimbabwe":"Zimbabwean",
    "Algeria":"Algerian","Angola":"Angolan","Antigua":"Antiguan","Armenia":"Armenian",
    "Belize":"Belizean","Bolivia":"Bolivian","Bosnia":"Bosnian","Botswana":"Botswanan",
    "Congo":"Congolese","Gambia":"Gambian","Sri Lanka":"Sri Lankan",
}


def ordinal(n):
    """18 -> 18th, 21 -> 21st, 71 -> 71st, 43 -> 43rd. The 11/12/13 exception included."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }".replace(" ", "")

BIRTHDAY_TEMPLATES = [
    "{ord} Birthday {age} Year Old",
    "Vintage Year {ord} Birthday {year}",
    "Birth of Legends {ord} Birthday {year}",
    "Premium Vintage {ord} Birthday {year}",
    "Aged to Perfection {ord} Birthday {year}",
    "{age} Year Old Banger Birthday {ord} Year Old",
    "{ord} Birthday {age} Year Old Level Up Gaming",
    "Limited Edition {year} {ord} Birthday",
]


def flag_designs():
    for t in FLAG_TREATMENTS:
        for c in COUNTRIES:
            dem = DEMONYM.get(c)
            stem = f"{t} {c} Flag {dem} Day Football" if dem else f"{t} {c} Flag Day Football"
            yield {
                "design_id": f"flag_{t.lower()}_{c.lower()}",
                "stem": stem,
                "theme": "uk_flags",
                "ip_tier": "R0",
                "extra_keywords": ["Patriotic", "National", "Supporter", "World Cup"],
            }


def birthday_designs(current_year):
    for ti, tpl in enumerate(BIRTHDAY_TEMPLATES):
        for age in range(3, 99):
            yield {
                "design_id": f"bday_t{ti}_{age}",
                "stem": tpl.format(age=age, ord=ordinal(age), year=current_year - age),
                "theme": "uk_birthday",
                "ip_tier": "R0",
                "age": age,
                "extra_keywords": [str(current_year - age), "Funny", "Gift"],
            }


# --------------------------------------------------------------------- output

def write(rows, out_path, fmt, report_every=250_000):
    n = 0
    band = 0
    over = 0
    p = Path(out_path)
    if fmt == "jsonl":
        with p.open("w") as fh:
            for r in rows:
                n += 1
                if TITLE_MIN <= r["title_len"] <= TITLE_HI: band += 1
                if r["title_len"] > TITLE_MAX: over += 1
                fh.write(json.dumps(r, separators=(",", ":")) + "\n")
                if n % report_every == 0:
                    print(f"  ... {n:,} rows", file=sys.stderr)
    else:
        with p.open("w", newline="") as fh:
            w = None
            for r in rows:
                n += 1
                if TITLE_MIN <= r["title_len"] <= TITLE_HI: band += 1
                if r["title_len"] > TITLE_MAX: over += 1
                flat = {**r,
                        "price_from": r["price"]["from_gbp"], "price_to": r["price"]["to_gbp"],
                        "variation_axes": json.dumps(r["variation_axes"])}
                flat.pop("price")
                if w is None:
                    w = csv.DictWriter(fh, fieldnames=list(flat))
                    w.writeheader()
                w.writerow(flat)
                if n % report_every == 0:
                    print(f"  ... {n:,} rows", file=sys.stderr)
    return n, band, over


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("flags", "birthdays", "designs", "art"):
        s = sub.add_parser(name)
        s.add_argument("--stores", type=int, default=3)
        s.add_argument("--out", default=f"{name}.jsonl")
        s.add_argument("--format", choices=["jsonl", "csv"], default="jsonl")
        if name in ("designs", "art"):
            s.add_argument("--library", required=True)
        if name == "birthdays":
            s.add_argument("--year", type=int, default=2026)

    e = sub.add_parser("estimate")
    e.add_argument("--designs", type=int, required=True)
    e.add_argument("--stores", type=int, default=3)
    e.add_argument("--kind", choices=["apparel", "art"], default="apparel")

    a = ap.parse_args()

    if a.cmd == "estimate":
        if a.kind == "apparel":
            prods = len(APPAREL)
            var = sum(variations_for(p)[1] for p in APPAREL) / prods
        else:
            prods = sum(len(p["suffix_pool"]) for p in WALL_ART)
            var = sum(variations_for(p)[1] * len(p["suffix_pool"]) for p in WALL_ART) / prods
        listings = a.designs * prods * a.stores
        print(f"  designs            {a.designs:,}")
        print(f"  product slots      {prods}")
        print(f"  stores             {a.stores}")
        print(f"  -> LISTINGS        {listings:,}")
        print(f"  mean variations    {var:.0f} per listing")
        print(f"  -> SKUs            {int(listings * var):,}")
        return

    stores = a.stores
    if a.cmd == "flags":
        rows = apparel_rows(flag_designs(), stores)
    elif a.cmd == "birthdays":
        rows = apparel_rows(birthday_designs(a.year), stores)
    elif a.cmd == "designs":
        rows = apparel_rows(json.loads(Path(a.library).read_text()), stores)
    else:
        rows = art_rows(json.loads(Path(a.library).read_text()), stores)

    n, band, over = write(rows, a.out, a.format)
    print(f"{n:,} listings -> {a.out}")
    print(f"  titles in the 70-80 band: {band:,} ({band/max(1,n):.0%})")
    print(f"  titles over 80 chars:     {over}  <- must be 0")


if __name__ == "__main__":
    main()
