#!/usr/bin/env python3
"""A Google Shopping XML feed of the OnBuy catalogue, for OnBuy's own
"Product Creation" feed import.

WHY THIS EXISTS. OnBuy's Seller Control Panel has an Integrations screen
with two Available Imports - a CSV one and a **Google XML** one, both
labelled Product Creation. That is a far better route than the Product
Create Template, which is a spreadsheet a person reviews over about five
days:

  * it is a FEED, pulled on a schedule, so a price change here reaches
    OnBuy on the next fetch instead of in another ticket;
  * the format is Google Shopping XML, which is published, stable, and
    already produced and validated elsewhere in this repo by
    web/catalogue/feed.py;
  * it needs no template and no column guessing, which is the whole of
    README_ONBUY.md section 2.

THE TRAP THIS FILE EXISTS TO AVOID. walryvo.com ALREADY SERVES A GOOGLE
SHOPPING FEED at /feed.xml, and it is the WRONG ONE to give OnBuy. That
feed is the WEBSITE's: 209 designs, website prices of 24.99/29.99/34.99,
<link> pointing at walryvo.com product pages and images served from
walryvo.com. Pointing OnBuy's import at it would create 209 products at the
old prices rather than 10,000 at 19.99, and every one of them would carry a
link to a competing shop. The two feeds must never be confused, which is
why this writes a differently named file and why check() refuses a feed
carrying website prices.

WHAT IS STILL UNKNOWN, and the Integrations setup screen answers all three:

  1. ONE ITEM PER VARIANT, OR PER PRODUCT? This emits one <item> per
     variant with g:item_group_id tying the nine together, which is how
     Google Shopping works and how web/catalogue/feed.py already does it.
     If OnBuy wants one item per product, --one-per-product does that.
  2. IS <link> REQUIRED? These 10,000 designs are NOT on walryvo.com - the
     website deliberately carries 209, because a new domain hosting
     millions of near-identical pages is the shape of a feed farm. So
     there is no honest per-item landing page. <link> is omitted unless
     --link-base is given, rather than pointed at a page that does not
     exist.
  3. IS g:gtin REQUIRED? If it is, the barcode exemption in
     README_ONBUY.md section 1 blocks this route exactly as it blocks the
     template route. A feed changes the transport, not the policy.

DESCRIPTIONS ARE PLAIN TEXT HERE, not the HTML that goes in the CSV.
Google's specification wants plain text in [description] and the website's
own feed already obeys that. It also matters for size: the HTML
description is about 1.3 KB and ninety thousand of them is a file no
Worker will serve.

  usage: build_onbuy_feed.py --rows out/onbuy/luxvia-art_onbuy_10k_rows.jsonl
         build_onbuy_feed.py --rows ... --limit 5 --tag first
         build_onbuy_feed.py --check out/onbuy/feed
"""
import argparse, json, os, re, sys, xml.sax.saxutils as SAX

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import listing_text as LT

P = json.load(open(os.path.join(HERE, "onbuy_plan.json")))

# Posters, Prints & Visual Artwork, from Google's own taxonomy file. The
# same id web/catalogue/feed.py uses, and checked there rather than
# remembered: 500045 is Decorative Tapestries and would be wrong.
GOOGLE_CATEGORY = "500044"

# A size budget, not a row count. Cloudflare Workers Assets refuses a file
# over 25 MiB and the website serves this, so shards are kept well under.
MAX_BYTES = 18_000_000

# The website's prices. A feed carrying these is the website's feed, not
# this one, and check() says so rather than letting 209 products at 24.99
# reach OnBuy under this file's name.
WEBSITE_PRICES = {"24.99", "29.99", "34.99", "8.99", "12.99", "18.99"}


def esc(s):
    return SAX.escape(str(s))


def plain_description(r):
    """Plain text, and only what the website already claims.

    Same discipline as the HTML description in build_onbuy.py: no gsm, no
    'archival', no glazing material, nothing hand-painted or signed. Short,
    because ninety thousand copies of it is the file.
    """
    tech = LT.TECH.get(r["_tech"], r["_tech"])
    pal = LT.PAL.get(r["_pal"], "")
    gram = LT.GRAM.get(r["_gram"], "")
    bits = [
        f'{r["_subject"]} as {tech.lower()} wall art, framed and ready to '
        f'hang.',
        f'Printed to order in the United Kingdom on premium satin art '
        f'paper with pigment inks, then framed behind glazing with the '
        f'hanging fixture fitted.',
    ]
    spec = [("Theme", r["_theme"]), ("Style", tech),
            ("Composition", gram), ("Palette", pal)]
    bits.append(" ".join(f"{k}: {v}." for k, v in spec if v))
    bits.append("This is a printed reproduction of digitally created "
                "artwork. It is not a painting, it is not an original, and "
                "it is not signed.")
    return " ".join(bits)


def items(rows, one_per_product, link_base):
    """One <item> per variant, or per product with --one-per-product.

    The variant rows carry the price, the size, the frame colour and the
    photograph of that frame; the product row carries the name, the
    description and the brand. Both halves are needed for a complete item,
    so the product rows are indexed first and joined on group_sku - the
    same join the CSV expresses by putting them next to each other.
    """
    # KEYED ON THE PRODUCT'S OWN SKU, not on its group_sku. A parent row
    # leaves Parent_Group EMPTY - that is the template's rule and it is how
    # a parent is recognised - so keying on group_sku put every product
    # under "" and no variant ever found its parent. The feed came out with
    # zero items and, worse, check() passed it.
    prod = {r["sku"]: r for r in rows if r["_row"] == "product"}
    out = []
    if one_per_product:
        # The cheapest variant stands for the product, because a feed that
        # quotes a price has to quote one a buyer can actually pay, and the
        # lowest is the one the listing leads with everywhere else.
        kids_by = {}
        for r in rows:
            if r["_row"] == "variant":
                kids_by.setdefault(r["group_sku"], []).append(r)
        for g, p in prod.items():
            kids = kids_by.get(g, [])
            if not kids:
                continue
            cheap = min(kids, key=lambda k: float(k["price"]))
            out.append(_item(p, cheap, g, link_base, group=False))
        return out
    for r in rows:
        if r["_row"] != "variant":
            continue
        p = prod.get(r["group_sku"])
        if p:
            out.append(_item(p, r, r["group_sku"], link_base, group=True))
    return out


def _item(p, v, group_id, link_base, group=True):
    group_on = group
    d = {
        "g:id": v["sku"],
        "title": p["product_name"],
        "description": plain_description(p),
        "g:image_link": v["image_1"],
        "g:availability": "in_stock",
        "g:price": f'{float(v["price"]):.2f} GBP',
        "g:brand": p["brand"],
        "g:mpn": v["sku"],
        "g:condition": "new",
        "g:google_product_category": GOOGLE_CATEGORY,
        # The OnBuy category, not an invented one: the same path the CSV
        # submits, resolved from the template's Categories tab.
        "g:product_type": P["category_path"],
        # g:color, the AMERICAN spelling. That is what Google's
        # specification names the attribute and what
        # web/catalogue/feed.py already emits, so a parser that reads
        # Google Shopping XML will look for exactly this. OnBuy's own
        # variant axis is displayed as "Colour" - the display name and the
        # feed attribute are different things and only one of them is
        # ours to choose.
        "g:color": v["variant_one_value"],
        "g:size": v["variant_two_value"],
        "g:shipping_weight": f'{float(v["delivery_weight"]):.2f} kg',
    }
    if group_on:
        d["g:item_group_id"] = group_id
    if link_base:
        d["link"] = f'{link_base.rstrip("/")}/{group_id}'
    # The two photographs this variant does not lead with, so a buyer sees
    # the other frame colours without them being mistaken for the variant.
    extra = [u for u in (p["image_1"], p["image_2"], p["image_3"])
             if u != v["image_1"]]
    d["_additional"] = extra
    return d


def item_xml(r):
    """One item, serialised. Sharding measures THIS rather than estimating
    it: the first version guessed at the size from the field lengths plus a
    constant, undershot by a quarter because XML tags are most of the bytes,
    and produced 23.1 MB shards against an 18 MB budget - close enough to
    Workers' 25 MiB refusal to matter."""
    out = ["<item>"]
    for k, v in r.items():
        if k == "_additional":
            for u in v:
                out.append(f"<g:additional_image_link>{esc(u)}"
                           f"</g:additional_image_link>")
            continue
        out.append(f"<{k}>{esc(v)}</{k}>")
    out.append("</item>")
    return "\n".join(out)


def to_xml(chunks, title):
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">',
           '<channel>', f'<title>{esc(title)}</title>',
           '<link>https://walryvo.com</link>',
           f'<description>{esc(title)}</description>']
    out += chunks
    out += ["</channel>", "</rss>", ""]
    return "\n".join(out)


def write(rows, out_dir, tag, title):
    os.makedirs(out_dir, exist_ok=True)
    # Shard on a SIZE budget and on whole items. Workers Assets refuses a
    # file over 25 MiB, and the whole point of this route is that the
    # website serves the feed.
    shards, cur, n = [], [], 0
    for r in rows:
        x = item_xml(r)
        if cur and n + len(x.encode()) > MAX_BYTES:
            shards.append(cur)
            cur, n = [], 0
        cur.append(x)
        n += len(x.encode()) + 1
    if cur or not shards:
        shards.append(cur)

    written = []
    for i, shard in enumerate(shards, 1):
        name = (f"onbuy_{tag}.xml" if len(shards) == 1
                else f"onbuy_{tag}_{i:02d}.xml")
        path = os.path.join(out_dir, name)
        t = title + (f" ({i} of {len(shards)})" if len(shards) > 1 else "")
        open(path, "w", encoding="utf-8").write(to_xml(shard, t))
        written.append((path, len(shard)))
    for p_, k in written:
        print(f"wrote {p_}  ({k:,} items, {os.path.getsize(p_)/1e6:.1f} MB)")
    return written


def check(out_dir):
    bad = {}
    def note(k, n=1):
        bad[k] = bad.get(k, 0) + n
    files = [f for f in sorted(os.listdir(out_dir)) if f.endswith(".xml")]
    if not files:
        print("no XML in", out_dir)
        return 1
    ok_prices = {f'{s["framed"]:.2f}' for s in P["sizes"]}
    ids, items_n = set(), 0
    for fn in files:
        path = os.path.join(out_dir, fn)
        body = open(path, encoding="utf-8").read()
        if os.path.getsize(path) > MAX_BYTES * 1.05:
            note("files over the shard budget")
        if os.path.getsize(path) > 25 * 1024 * 1024:
            note("files over the 25 MiB Workers asset limit")
        items_n += body.count("<item>")
        for m in re.finditer(r"<item>(.*?)</item>", body, re.S):
            it = m.group(1)
            def f(tag):
                g = re.search(rf"<{tag}>(.*?)</{tag}>", it, re.S)
                return g.group(1) if g else ""
            i = f("g:id")
            if not i:
                note("items with no id")
            if i in ids:
                note("duplicate ids")
            ids.add(i)
            price = f("g:price").split()[0] if f("g:price") else ""
            if price not in ok_prices:
                note("prices that are not an OnBuy framed price")
            if price in WEBSITE_PRICES - ok_prices:
                # The loud one. See the note at the top of this file.
                note("WEBSITE prices in the OnBuy feed")
            img = f("g:image_link")
            if "r2.dev" not in img:
                note("images not served from the bucket")
            if "walryvo.com" in img:
                note("images pointing at the website instead of the bucket")
            # esc(), because the category path contains an ampersand and
            # the file holds it as &amp;. Comparing the raw path against
            # the escaped text failed on every one of 90,000 items, which
            # is the sort of all-or-nothing result that means the CHECK is
            # wrong rather than the data.
            if f("g:product_type") != esc(P["category_path"]):
                note("items not in the OnBuy wall-art category")
            if "<g:colour>" in it:
                note("g:colour, which Google's spec spells g:color")
            if not f("g:color") or not f("g:size"):
                note("items missing a variant axis")
            if not f("title") or not f("description"):
                note("items with no title or description")
            if "<" in f("description"):
                note("HTML in a description that must be plain text")
    # AN EMPTY FEED IS A FAILURE, NOT A CLEAN RESULT. This is how the
    # parent-key bug above got as far as "no problems": the builder emitted
    # zero items and every per-item assertion below vacuously held. A check
    # whose strongest statement is about rows it never saw has to say so.
    if items_n == 0:
        note("an EMPTY feed - nothing was written")
    print(f"checked {len(files)} file(s), {items_n:,} items, "
          f"{len(ids):,} distinct ids")
    for k in sorted(bad):
        print(f"  [BLOCK] {k}: {bad[k]:,}")
    if not bad:
        print("  no problems.")
    return len(bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", default=os.path.join(
        HERE, "out", "onbuy", "luxvia-art_onbuy_10k_rows.jsonl"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "onbuy", "feed"))
    ap.add_argument("--tag", default="10k")
    ap.add_argument("--limit", type=int, default=0,
                    help="listings, not items. OnBuy reportedly asks new "
                         "accounts to start product creation with 5-10.")
    ap.add_argument("--one-per-product", action="store_true")
    ap.add_argument("--link-base", default="",
                    help="only if the setup screen says <link> is required")
    ap.add_argument("--check", metavar="DIR")
    a = ap.parse_args()
    if a.check:
        sys.exit(1 if check(a.check) else 0)

    rows = [json.loads(l) for l in open(a.rows)]
    if a.limit:
        # On the PRODUCT's own sku, for the same reason items() is: a
        # parent leaves Parent_Group empty, so collecting group_sku here
        # collected "" and the limited feed came out with parents and no
        # variants at all.
        keep, n = set(), 0
        for r in rows:
            if r["_row"] == "product":
                if n >= a.limit:
                    break
                keep.add(r["sku"])
                n += 1
        rows = [r for r in rows
                if (r["sku"] if r["_row"] == "product" else r["group_sku"])
                in keep]
    print(f"{sum(1 for r in rows if r['_row'] == 'product'):,} listings in")

    it = items(rows, a.one_per_product, a.link_base)
    print(f"{len(it):,} feed items "
          f"({'one per product' if a.one_per_product else 'one per variant'})")
    write(it, a.out, a.tag, f'{P["brand"]} products for OnBuy')
    print()
    check(a.out)


if __name__ == "__main__":
    main()
