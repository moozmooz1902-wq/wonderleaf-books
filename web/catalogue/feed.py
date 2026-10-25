#!/usr/bin/env python3
"""The Google Merchant Center product feed.

Serialised from catalogue.json, which product.build_all() wrote and which
the website's database was built from. Nothing here computes a price, a
title or a URL - see the long note at the top of product.py for why that
matters more than anything else in this directory.

ATTRIBUTE CHOICES, and the reasoning where it is not obvious. Checked
against Google's published product data specification, 25 Oct 2026:

* [id] - the variant id, under the 50-character limit, stable for ever
  because it is built from the design's content hash. Google warns that
  changing ids loses a product's history.
* [item_group_id] - REQUIRED for variants in the UK and required for ALL
  variants in free listings, which is the whole point of this exercise.
  Nine variants of a design share one group id.
* [brand] + [mpn] - no GTIN exists for a made-to-order print and inventing
  one is worse than omitting it ("submit only if you're sure it's
  correct"). With a brand and an MPN present, [identifier_exists] must NOT
  be set to no, so it is omitted and Google's default of yes applies.
* [price] - VAT INCLUSIVE. Google requires tax-inclusive prices outside the
  US and Canada, and the seller is VAT registered.
* [color] and [size] - the two axes that distinguish the variants, so both
  are required here rather than optional.
* [google_product_category] - 500044, Posters, Prints & Visual Artwork.
  Taken from Google's own taxonomy file, not from memory: 500045 is
  Decorative Tapestries and would be wrong.
* handling and transit times - submitted so the feed states the same
  delivery promise the delivery page makes. A feed that implies faster
  delivery than the site is "hiding processing delays behind a stated
  delivery time".

WHAT IS DELIBERATELY ABSENT: [sale_price], any promotion, and anything
resembling a strikethrough "was" price. A reference price the product was
never actually sold at is the clearest possible misrepresentation finding,
and a new shop has no price history to refer back to.
"""
import argparse, json, os, re, sys, xml.sax.saxutils as SAX

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
sys.path.insert(0, HERE)

MAX_ITEMS_PER_FILE = 100_000   # keeps each file comfortably fetchable


def esc(s):
    return SAX.escape(str(s))


def load():
    cat = json.load(open(os.path.join(HERE, "catalogue.json")))
    cfg = json.load(open(os.path.join(WEB, "business.config.json")))
    return cat, cfg


def required_missing(cfg):
    """The identity a feed cannot honestly be built without."""
    need = ["brand", "domain", "legal_name", "company_number", "vat_number",
            "registered_address", "email", "phone"]
    missing = [k for k in need if not cfg.get(k)]
    if cfg["fulfilment"]["delivery"][0].get("price") is None:
        missing.append("fulfilment.delivery[0].price")
    return missing


def items(cat, cfg):
    """One dict per purchasable variant - exactly what the feed submits."""
    base = f"https://{cfg['domain']}"
    d = cfg["fulfilment"]["delivery"][0]
    cur = cfg["currency"]
    out = []
    for p in cat["products"]:
        for v in p["variants"]:
            out.append({
                "id": v["id"],
                "item_group_id": p["item_group_id"],
                "title": v["title"],
                "description": v["description"],
                # The variant URL. The page reads these parameters on the
                # server and answers with THIS variant's price.
                "link": f'{base}/art/{p["slug"]}?frame={v["frame"]}&size={v["size"]}',
                # Our own image host, not r2.dev - see wrangler.toml.
                "image_link": f'{base}/img/{v["image_path"]}',
                "availability": v["availability"],
                "price": f'{v["price"]:.2f} {cur}',
                "brand": p["brand"],
                "mpn": v["id"],
                "condition": "new",
                "google_product_category": cat["google_product_category"],
                "product_type": p["product_type"],
                "color": v["frame_label"],
                "size": v["size_label"],
                "material": v["material"],
                "item_group_title": p["title"],
                "shipping_country": "GB",
                "shipping_service": d["name"],
                "shipping_price": f'{d["price"]:.2f} {cur}',
                "min_handling_time": 1,
                "max_handling_time": cfg["fulfilment"]["dispatch_working_days"],
                "min_transit_time": d["min_days"],
                "max_transit_time": d["max_days"],
            })
    return out


def validate(rows, cfg):
    """Check the feed against the spec BEFORE Google does.

    Every rule here is one Google enforces. Finding a breach locally costs
    nothing; finding it after submission costs a disapproval on the account's
    record, and a new account's record is the thing we are protecting.
    """
    bad, seen = [], {}
    for r in rows:
        i = r["id"]
        if i in seen:
            bad.append(f"{i}: duplicate id")
        seen[i] = 1
        if len(i) > 50:
            bad.append(f"{i}: id over 50 chars ({len(i)})")
        if not (0 < len(r["title"]) <= 150):
            bad.append(f"{i}: title length {len(r['title'])}")
        if not (0 < len(r["description"]) <= 5000):
            bad.append(f"{i}: description length {len(r['description'])}")
        if len(r["item_group_id"]) > 50:
            bad.append(f"{i}: item_group_id over 50 chars")
        if len(r["brand"] or "") > 70:
            bad.append(f"{i}: brand over 70 chars")
        if not re.match(r"^\d+\.\d{2} [A-Z]{3}$", r["price"]):
            bad.append(f"{i}: price {r['price']!r} not 'N.NN CCC'")
        if float(r["price"].split()[0]) <= 0:
            bad.append(f"{i}: price must be greater than zero")
        if r["availability"] not in ("in_stock", "out_of_stock", "preorder",
                                     "backorder"):
            bad.append(f"{i}: availability {r['availability']!r}")
        for f in ("link", "image_link"):
            if not r[f].startswith("https://"):
                bad.append(f"{i}: {f} is not https")
            if " " in r[f]:
                bad.append(f"{i}: {f} contains a space")
        if cfg.get("domain") and f"//{cfg['domain']}" not in r["link"]:
            bad.append(f"{i}: link is not on the verified domain")
        if len(r["color"]) > 100 or not r["color"]:
            bad.append(f"{i}: color {r['color']!r}")
        if r["color"].lower() in ("multicolor", "multicoloured", "n/a"):
            bad.append(f"{i}: color {r['color']!r} is not allowed by Google")
        if len(r["size"]) > 100 or not r["size"]:
            bad.append(f"{i}: size {r['size']!r}")
        if (r["brand"] or "").strip().lower() in ("n/a", "generic", "none",
                                                  "unbranded"):
            bad.append(f"{i}: brand {r['brand']!r} is explicitly disallowed")
        # Promotional text in a title is a disapproval in its own right.
        for word in ("sale", "free delivery", "best price", "cheap", "%",
                     "!!!", "discount", "offer", "bestseller", "best seller"):
            if word in r["title"].lower():
                bad.append(f"{i}: title contains promotional text {word!r}")
        if r["title"].isupper():
            bad.append(f"{i}: title is all capitals")
    return bad


FIELD_ORDER = [
    ("id", "g:id"), ("item_group_id", "g:item_group_id"),
    ("title", "title"), ("description", "description"),
    ("link", "link"), ("image_link", "g:image_link"),
    ("availability", "g:availability"), ("price", "g:price"),
    ("brand", "g:brand"), ("mpn", "g:mpn"), ("condition", "g:condition"),
    ("google_product_category", "g:google_product_category"),
    ("product_type", "g:product_type"),
    ("color", "g:color"), ("size", "g:size"), ("material", "g:material"),
    ("item_group_title", "g:item_group_title"),
]


def to_xml(rows, cfg, title):
    """RSS 2.0 with Google's namespace - the format Merchant Center has
    accepted longest and the one least likely to be misparsed."""
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">',
           '<channel>',
           f'<title>{esc(title)}</title>',
           f'<link>https://{esc(cfg["domain"])}</link>',
           f'<description>{esc(cfg["brand"])} framed art prints</description>']
    for r in rows:
        out.append("<item>")
        for key, tag in FIELD_ORDER:
            out.append(f"<{tag}>{esc(r[key])}</{tag}>")
        out.append("<g:shipping>"
                   f"<g:country>{esc(r['shipping_country'])}</g:country>"
                   f"<g:service>{esc(r['shipping_service'])}</g:service>"
                   f"<g:price>{esc(r['shipping_price'])}</g:price>"
                   "</g:shipping>")
        for k in ("min_handling_time", "max_handling_time",
                  "min_transit_time", "max_transit_time"):
            out.append(f"<g:{k}>{r[k]}</g:{k}>")
        out.append("</item>")
    out += ["</channel>", "</rss>", ""]
    return "\n".join(out)


def to_tsv(rows):
    """A tab-separated copy. Useful for eyeballing in a spreadsheet and for
    Merchant Center's own file upload, which some accounts prefer."""
    cols = [k for k, _ in FIELD_ORDER] + [
        "shipping_country", "shipping_service", "shipping_price",
        "min_handling_time", "max_handling_time",
        "min_transit_time", "max_transit_time"]
    head = {"id": "id", "item_group_id": "item group id", "title": "title",
            "description": "description", "link": "link",
            "image_link": "image link", "availability": "availability",
            "price": "price", "brand": "brand", "mpn": "mpn",
            "condition": "condition",
            "google_product_category": "google product category",
            "product_type": "product type", "color": "color", "size": "size",
            "material": "material", "item_group_title": "item group title",
            "shipping_country": "shipping(country)",
            "shipping_service": "shipping(service)",
            "shipping_price": "shipping(price)",
            "min_handling_time": "min handling time",
            "max_handling_time": "max handling time",
            "min_transit_time": "min transit time",
            "max_transit_time": "max transit time"}
    lines = ["\t".join(head[c] for c in cols)]
    for r in rows:
        lines.append("\t".join(
            str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(WEB, "feed"))
    ap.add_argument("--tsv", action="store_true")
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="build anyway with the identity fields unset. For "
                         "inspecting the shape of the feed only - the result "
                         "must never be submitted.")
    a = ap.parse_args()

    cat, cfg = load()
    missing = required_missing(cfg)
    if missing and not a.allow_incomplete:
        print("REFUSING to build the feed. These are unset in "
              "business.config.json:")
        for m in missing:
            print("  -", m)
        print("\nA feed built with blanks in the business identity is a feed "
              "that misrepresents who is selling, which is the exact finding "
              "we are avoiding. Fill them in, or pass --allow-incomplete to "
              "inspect the shape without submitting it.")
        return 2
    if missing:
        cfg = dict(cfg)
        cfg.setdefault("domain", "example-not-for-submission.invalid")
        for k in ("brand", "legal_name"):
            cfg[k] = cfg.get(k) or "NOT SET"
        if cfg["fulfilment"]["delivery"][0].get("price") is None:
            cfg["fulfilment"]["delivery"][0]["price"] = 0.0

    rows = items(cat, cfg)
    problems = validate(rows, cfg)
    print(f"feed items: {len(rows):,} "
          f"({len(cat['products']):,} designs x "
          f"{len(rows)//max(1,len(cat['products']))} variants)")
    if problems:
        print(f"\nSPEC PROBLEMS ({len(problems)}) - not writing the feed:")
        for p in problems[:40]:
            print("  -", p)
        return 1
    print("spec check: 0 problems")

    os.makedirs(a.out, exist_ok=True)
    shards = [rows[i:i + MAX_ITEMS_PER_FILE]
              for i in range(0, len(rows), MAX_ITEMS_PER_FILE)] or [[]]
    written = []
    for n, shard in enumerate(shards, 1):
        name = "feed.xml" if len(shards) == 1 else f"feed-{n:02d}.xml"
        path = os.path.join(a.out, name)
        open(path, "w").write(
            to_xml(shard, cfg, f"{cfg['brand']} products"
                   + (f" ({n} of {len(shards)})" if len(shards) > 1 else "")))
        written.append((path, len(shard)))
    if a.tsv:
        path = os.path.join(a.out, "feed.tsv")
        open(path, "w").write(to_tsv(rows))
        written.append((path, len(rows)))

    for path, n in written:
        print(f"wrote {path}  ({n:,} items, "
              f"{os.path.getsize(path)/1e6:.1f} MB)")
    if missing:
        print("\nDO NOT SUBMIT THIS FILE. It was built with "
              "--allow-incomplete and the business identity is not filled "
              "in.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
