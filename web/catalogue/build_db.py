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
import json, os, sqlite3, sys

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

    rows = [SCHEMA]
    rows.append("DELETE FROM product_rooms; DELETE FROM variants; "
                "DELETE FROM products;")
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

    print(f"products {n_p:,}   variants {n_v:,}   room links {n_r:,}")
    print(f"niches with stock: {len(niches)}  "
          f"(smallest {min(c for _, c in niches)}, "
          f"largest {max(c for _, c in niches)})")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SQL}  ({len(sql)/1e6:.1f} MB)")
    print(f"wrote {OUT_DB}")


if __name__ == "__main__":
    main()
