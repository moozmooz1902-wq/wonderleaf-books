#!/usr/bin/env python3
"""Turn the selection into the two artefacts the shop runs on.

  catalogue.json  - the whole built catalogue, for the feed builder and the
                    preflight checker to read. Never served to a browser.
  seed.sql        - D1 (SQLite) inserts, for the site to query.

D1 RATHER THAN A BUNDLED JSON FILE, and the reason is the seller's own plan.
At 1,000 products a JSON import would be simpler and would work. At the
500,000 the scale plan ends on it would not: a Cloudflare Worker has a hard
bundle-size limit and a multi-hundred-megabyte catalogue cannot be imported
into one at any price. Choosing the database now means the scale-up is a
bigger seed file and nothing else, instead of a rewrite of the site at the
exact moment the shop starts working.

Everything written here comes from product.build_all(). This file computes no
titles, no prices and no URLs of its own - if it did, there would be two
answers to what a product costs, and that is the whole failure mode.
"""
import collections, json, os, random, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import product as P
import taxonomy as T

OUT_JSON = os.path.join(HERE, "catalogue.json")
OUT_SQL = os.path.join(HERE, "seed.sql")
OUT_DB = os.path.join(HERE, "catalogue.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
  slug TEXT PRIMARY KEY,
  sku TEXT NOT NULL,
  item_group_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  section TEXT NOT NULL,
  section_title TEXT NOT NULL,
  niche TEXT NOT NULL,
  niche_title TEXT NOT NULL,
  style TEXT NOT NULL,
  style_title TEXT NOT NULL,
  colour TEXT NOT NULL,
  colour_title TEXT NOT NULL,
  subject TEXT NOT NULL,
  product_type TEXT NOT NULL,
  brand TEXT,
  mpn TEXT NOT NULL,
  bucket TEXT NOT NULL,
  price_from REAL NOT NULL,
  default_frame TEXT NOT NULL,
  default_size TEXT NOT NULL,
  rank INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_products_niche ON products(niche, rank);
CREATE INDEX IF NOT EXISTS idx_products_section ON products(section, rank);
CREATE INDEX IF NOT EXISTS idx_products_style ON products(style, rank);
CREATE INDEX IF NOT EXISTS idx_products_colour ON products(colour, rank);

CREATE TABLE IF NOT EXISTS variants (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  frame TEXT NOT NULL,
  frame_label TEXT NOT NULL,
  size TEXT NOT NULL,
  size_label TEXT NOT NULL,
  size_cm TEXT NOT NULL,
  price REAL NOT NULL,
  title TEXT NOT NULL,
  image_path TEXT NOT NULL,
  availability TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_variants_slug ON variants(slug);

-- PRECOMPUTED FACET COUNTS.
--
-- The navigation shows a count beside every niche, section, style and
-- colour, on the home page and on every category page. Computed live that
-- is "SELECT niche, COUNT(*) FROM products GROUP BY niche", which reads
-- EVERY row in the table on EVERY page view. At 240 products that is
-- nothing. At a million it is a full scan per request, and D1 bills rows
-- read, so it would be simultaneously the slowest query on the site and the
-- largest line on the bill - for a number that only changes when the
-- catalogue is rebuilt.
--
-- So it is written here at build time instead. One row per facet value,
-- read by primary key. ~70 rows today, and it does not grow with the
-- catalogue: a million products still have 53 niches.
CREATE TABLE IF NOT EXISTS facet_counts (
  kind TEXT NOT NULL,          -- niche | section | style | colour | room
  key TEXT NOT NULL,
  title TEXT NOT NULL,
  parent TEXT,                 -- section slug, for niches
  parent_title TEXT,
  n INTEGER NOT NULL,
  PRIMARY KEY (kind, key)
);

CREATE TABLE IF NOT EXISTS product_rooms (
  slug TEXT NOT NULL, room TEXT NOT NULL,
  PRIMARY KEY (slug, room)
);
CREATE INDEX IF NOT EXISTS idx_rooms_room ON product_rooms(room);

-- Orders are written by the Stripe webhook. Kept because a shop that cannot
-- say what it sold cannot honour the returns policy it publishes, and
-- "denying return and refund despite having a clear policy" is the one
-- misrepresentation finding that carries no warning.
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  created TEXT NOT NULL,
  email TEXT,
  total REAL NOT NULL,
  currency TEXT NOT NULL,
  status TEXT NOT NULL,
  items TEXT NOT NULL,
  shipping TEXT
);

-- THE THREE ANALYTICS TABLES. Written by site/src/lib/analytics.ts and read
-- only by /admin. None of them is in the DELETE list below, because a
-- catalogue rebuild must not erase the record of who visited - the
-- catalogue changes weekly and the traffic history is the one thing that
-- cannot be regenerated.
--
-- `hits` is one row per human page view. `crawls` is a daily counter per
-- bot, never a row each, because Googlebot fetching every product and
-- photograph is tens of thousands of requests. See the long note at the
-- top of analytics.ts for why the two are shaped differently.
CREATE TABLE IF NOT EXISTS hits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  day TEXT NOT NULL,
  visitor TEXT NOT NULL,   -- salted daily hash. No IP is stored anywhere.
  path TEXT NOT NULL,
  ref TEXT,
  src TEXT,                -- google-shopping | google-search | direct | host
  country TEXT
);
CREATE INDEX IF NOT EXISTS idx_hits_ts ON hits(ts);
CREATE INDEX IF NOT EXISTS idx_hits_day ON hits(day);

CREATE TABLE IF NOT EXISTS crawls (
  day TEXT NOT NULL,
  bot TEXT NOT NULL,
  kind TEXT NOT NULL,
  n INTEGER NOT NULL,
  PRIMARY KEY (day, bot, kind)
);

-- One row each time a basket reaches Stripe. Orders divided by checkouts is
-- the conversion rate, and a checkout with no matching order is an
-- abandoned basket - the number that says whether the problem is traffic or
-- the shop.
CREATE TABLE IF NOT EXISTS checkouts (
  id TEXT PRIMARY KEY,
  ts INTEGER NOT NULL,
  day TEXT NOT NULL,
  total REAL NOT NULL,
  items INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_checkouts_ts ON checkouts(ts);
"""


def _q(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    sel = json.load(open(os.path.join(HERE, "selection.json")))
    cfg = P.config()
    products = P.build_all(sel["designs"], cfg)

    json.dump(dict(
        generated_from="selection.json",
        framed_only=sel.get("framed_only", True),
        colourway=P.COLOURWAY,
        frames=P.FRAMES, sizes=P.SIZES,
        google_product_category=T.GOOGLE_PRODUCT_CATEGORY,
        taxonomy=dict(
            sections=[dict(slug=s, title=t) for s, t, _ in T.SECTIONS],
            niches=T.NICHES,
            styles=[dict(slug=s, title=t, blurb=b) for s, t, _, b in T.STYLES],
            colours=[dict(slug=s, title=t, blurb=b) for s, t, _, b in T.COLOURS],
            rooms=[dict(slug=s, title=t) for s, t, _ in T.ROOMS],
        ),
        products=products,
    ), open(OUT_JSON, "w"), indent=1)

    # The site reads its own copies under src/data rather than importing
    # across the project root (Vite refuses that, and more importantly a
    # second hand-maintained copy of the business details is exactly the
    # kind of drift Google's verification cross-check punishes). Written
    # here so there is one writer and the site is never edited by hand.
    data_dir = os.path.join(os.path.dirname(HERE), "site", "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    public = {k: v for k, v in cfg.items() if not k.startswith("_")}
    for key in ("fulfilment", "returns", "social_proof"):
        if isinstance(public.get(key), dict):
            public[key] = {k: v for k, v in public[key].items()
                           if not k.startswith("_")}
    if isinstance(public.get("fulfilment", {}).get("delivery"), list):
        public["fulfilment"]["delivery"] = [
            {k: v for k, v in d.items() if not k.startswith("_")}
            for d in public["fulfilment"]["delivery"]]
    json.dump(public, open(os.path.join(data_dir, "business.json"), "w"),
              indent=1)
    # THE PALETTE, WRITTEN OUT AS CSS.
    #
    # The colours used to live in global.css, which meant changing the shop's
    # look was an edit in a stylesheet and a hunt for every literal that had
    # escaped the tokens. The seller changes them often, so they are data
    # now: themes.json holds the named presets, business.config.json picks
    # one by name, and this writes the :root block that global.css imports.
    # Switching the whole shop is one word and a rebuild.
    themes = json.load(open(os.path.join(os.path.dirname(HERE),
                                         "themes.json")))
    want = cfg.get("theme", "paper-white")
    if want not in themes:
        raise SystemExit(f"build_db: no theme {want!r} in themes.json. "
                         f"Have: {[k for k in themes if not k.startswith('_')]}")
    th = themes[want]
    css = [f"/* GENERATED by build_db.py from themes.json: {want} */",
           f"/* {th['label']} */",
           "/* Do not edit. Change \"theme\" in business.config.json and",
           "   rebuild, or add a preset to themes.json. */",
           ":root {",
           f"  color-scheme: {th['scheme']};"]
    for k, v in th.items():
        if k in ("label", "scheme"):
            continue
        css.append(f"  --{k}: {v};")
    css += ["}", ""]
    open(os.path.join(os.path.dirname(HERE), "site", "src", "styles",
                      "theme.css"), "w").write("\n".join(css))
    # THE BROWSER NEEDS TO BE TOLD, NOT JUST THE STYLESHEET.
    #
    # The seller reported the shop's colours looking "completely different
    # on a phone". It was not our CSS - there is no prefers-color-scheme
    # rule anywhere in this site. It is that Chrome on Android AUTO-DARKENS
    # pages, and the one thing that stops it is the page declaring the
    # scheme it was designed in. theme.css already sets color-scheme on
    # :root; these two carry the same fact into the <head>, where the
    # browser reads it before any stylesheet has loaded.
    #
    # theme-color was ALSO hardcoded to #edeae3, the cream, so the phone's
    # browser bar stayed cream whatever theme the shop was wearing. It is
    # the theme's own page colour now, so it cannot fall out of step again.
    cfg["theme_scheme"] = th["scheme"]
    cfg["theme_color"] = th["paper"]
    print(f"theme: {want} ({th['scheme']}, {th['paper']})")

    # THE SITE'S TAXONOMY IS WHAT ACTUALLY HAS STOCK, not the whole tree.
    #
    # The full taxonomy has 53 niches in 6 sections. A narrow launch draws
    # from 12 of them, and if the navigation still carried all six sections
    # then four of its links would open a category with nothing in it.
    # Google's editorial requirements make that a violation twice over -
    # links must "point to relevant content", and a site with empty pages is
    # one that "needs improvement". So the menus are built from the
    # products, and shrink and grow with the range on their own.
    live_niches = {p["niche"] for p in products}
    live_sections = {p["section"] for p in products}
    live_styles = {p["style"] for p in products}
    live_colours = {p["colour"] for p in products}
    live_rooms = {r for p in products for r in p["rooms"]}
    json.dump(dict(
        sections=[dict(slug=s, title=t) for s, t, _ in T.SECTIONS
                  if s in live_sections],
        niches={k: v for k, v in T.NICHES.items() if k in live_niches},
        styles=[dict(slug=s, title=t, blurb=b) for s, t, _, b in T.STYLES
                if s in live_styles],
        colours=[dict(slug=s, title=t, blurb=b) for s, t, _, b in T.COLOURS
                 if s in live_colours],
        rooms=[dict(slug=s, title=t) for s, t, _ in T.ROOMS
               if s in live_rooms],
    ), open(os.path.join(data_dir, "taxonomy.json"), "w"), indent=1)
    print(f"live taxonomy: {len(live_sections)} sections, "
          f"{len(live_niches)} niches, {len(live_styles)} styles, "
          f"{len(live_colours)} colours, {len(live_rooms)} rooms")

    # INTERLEAVE THE PALETTES WITHIN EACH NICHE.
    #
    # A category page is `WHERE niche = ? ORDER BY rank`, and rank is just
    # the order products come out of selection - which is score order, and
    # score order clusters, because panels that share a palette were
    # generated together and score alike. So a niche could hold five
    # palettes and still open with six charcoal drawings in a row, which
    # looks exactly like the single-palette problem it was meant to fix.
    #
    # So within each niche the products are dealt out round-robin across
    # palettes before rank is assigned: first the best of each palette, then
    # the second best of each, and so on. Score order survives inside each
    # palette, the niches keep their relative order, and the top of every
    # category page is as varied as the niche itself.
    seen, order_of_niche = {}, []
    for pr in products:
        if pr["niche"] not in seen:
            seen[pr["niche"]] = True
            order_of_niche.append(pr["niche"])
    bucket = collections.defaultdict(lambda: collections.defaultdict(list))
    for pr in products:
        bucket[pr["niche"]][pr["colour"]].append(pr)
    # The lane order is reshuffled every cycle. A strict round robin fixes
    # the clustering and replaces it with a metronome - two-tone, bold,
    # colourful, two-tone, bold, colourful - which is just as obviously a
    # pattern to anyone scrolling. Seeded from the niche name so the order
    # is varied but identical on every build; a catalogue that reshuffles
    # itself each time it is built cannot be checked against yesterday's.
    woven = []
    for niche in order_of_niche:
        lanes = [l for l in bucket[niche].values() if l]
        rng = random.Random(f"walryvo:{niche}")
        last = None
        while lanes:
            cycle = lanes[:]
            rng.shuffle(cycle)
            # A shuffle can end one cycle and start the next on the same
            # lane, which puts two of a colour together and undoes the point.
            if len(cycle) > 1 and cycle[0] is last:
                cycle[0], cycle[1] = cycle[1], cycle[0]
            for lane in cycle:
                if lane:
                    woven.append(lane.pop(0))
                    last = lane
            lanes = [l for l in lanes if l]
    # Then a second pass on technique. Rotating the palette stops two black
    # and white drawings sitting together, but not two charcoals in
    # different colourways, and the seller's point was about the eye: a
    # shopper scrolling should never see the same look twice in a row. So
    # any product whose technique matches the one before it is swapped with
    # the next one along that does not, as long as the swap does not break
    # the palette rotation. Nothing is dropped and nothing leaves its niche;
    # this only reorders within a niche.
    for a in range(1, len(woven)):
        if woven[a]["niche"] != woven[a - 1]["niche"]:
            continue
        if woven[a]["style"] != woven[a - 1]["style"]:
            continue
        for b in range(a + 1, len(woven)):
            if woven[b]["niche"] != woven[a]["niche"]:
                break
            if (woven[b]["style"] != woven[a - 1]["style"]
                    and woven[b]["colour"] == woven[a]["colour"]):
                woven[a], woven[b] = woven[b], woven[a]
                break

    assert len(woven) == len(products), (len(woven), len(products))
    products = woven

    runs = sum(1 for i in range(1, len(products))
               if products[i]["niche"] == products[i - 1]["niche"]
               and products[i]["style"] == products[i - 1]["style"])
    print(f"same-technique neighbours on a category page: {runs}")

    rows = [SCHEMA]
    rows.append("DELETE FROM facet_counts; DELETE FROM product_rooms; "
                "DELETE FROM variants; DELETE FROM products;")
    for rank, p in enumerate(products):
        rows.append(
            "INSERT INTO products (slug,sku,item_group_id,title,description,"
            "section,section_title,niche,niche_title,style,style_title,"
            "colour,colour_title,subject,product_type,brand,mpn,bucket,"
            "price_from,default_frame,default_size,rank) VALUES ("
            + ",".join(_q(p[k]) for k in (
                "slug", "sku", "item_group_id", "title", "description",
                "section", "section_title", "niche", "niche_title", "style",
                "style_title", "colour", "colour_title", "subject",
                "product_type", "brand", "mpn", "bucket", "price_from",
                "default_frame", "default_size"))
            + f",{rank});")
        for v in p["variants"]:
            rows.append(
                "INSERT INTO variants (id,slug,frame,frame_label,size,"
                "size_label,size_cm,price,title,image_path,availability) "
                "VALUES ("
                + ",".join(_q(x) for x in (
                    v["id"], p["slug"], v["frame"], v["frame_label"],
                    v["size"], v["size_label"], v["size_cm"], v["price"],
                    v["title"], v["image_path"], v["availability"]))
                + ");")
        for room in p["rooms"]:
            rows.append("INSERT INTO product_rooms (slug,room) VALUES ("
                        + _q(p["slug"]) + "," + _q(room) + ");")
    # The facet counts, computed once here rather than per request.
    room_title = {s: t for s, t, _ in T.ROOMS}
    facets = []
    for kind, keyf, titlef in (
            ("niche", "niche", "niche_title"),
            ("section", "section", "section_title"),
            ("style", "style", "style_title"),
            ("colour", "colour", "colour_title")):
        c = collections.Counter(p[keyf] for p in products)
        seen = {}
        for p in products:
            seen.setdefault(p[keyf], p)
        for k, n in c.items():
            par = (seen[k]["section"], seen[k]["section_title"]) \
                if kind == "niche" else (None, None)
            facets.append((kind, k, seen[k][titlef], par[0], par[1], n))
    rc = collections.Counter(r for p in products for r in p["rooms"])
    for k, n in rc.items():
        facets.append(("room", k, room_title.get(k, k), None, None, n))
    for f in facets:
        rows.append("INSERT INTO facet_counts (kind,key,title,parent,"
                    "parent_title,n) VALUES ("
                    + ",".join(_q(x) for x in f) + ");")

    sql = "\n".join(rows)
    open(OUT_SQL, "w").write(sql)

    # Build it locally too, so `astro dev` has something to read and so the
    # SQL is proven to execute before it is ever sent to D1.
    if os.path.exists(OUT_DB):
        os.remove(OUT_DB)
    con = sqlite3.connect(OUT_DB)
    con.executescript(sql)
    con.commit()
    n_p = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    n_v = con.execute("SELECT COUNT(*) FROM variants").fetchone()[0]
    n_r = con.execute("SELECT COUNT(*) FROM product_rooms").fetchone()[0]
    niches = con.execute(
        "SELECT niche_title, COUNT(*) c FROM products GROUP BY niche "
        "ORDER BY c DESC").fetchall()
    con.close()

    print(f"products {n_p:,}   variants {n_v:,}   room links {n_r:,}   "
          f"facet counts {len(facets):,}")
    print(f"niches with stock: {len(niches)}  "
          f"(smallest {min(c for _, c in niches)}, "
          f"largest {max(c for _, c in niches)})")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SQL}  ({len(sql)/1e6:.1f} MB)")
    print(f"wrote {OUT_DB}")


if __name__ == "__main__":
    main()
