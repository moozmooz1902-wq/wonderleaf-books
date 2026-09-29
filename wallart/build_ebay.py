#!/usr/bin/env python3
"""Turn a store's catalogue into eBay File Exchange upload files.

    python3 build_ebay.py                       every store in plan.json
    python3 build_ebay.py --store luxvia-art    one store
    python3 build_ebay.py --check               verify files already built

Each design becomes ONE listing with six variations:
    Size  A4 / A3 / A2   x   Frame  Unframed / Black Frame
Shape of a variation group, as File Exchange requires (matches the live tee files):
    parent  Action=Add, CustomLabel=SKU, title, pictures, description, profiles,
            no price or quantity
    child   Action and CustomLabel blank, Relationship=Variation, price + quantity only
The parent SKU is what an order carries, so order.py / print_tool.py find
art/raw/<SKU>.png in the bucket exactly as they do today.

Output: out/ebay/<bucket>/<bucket>_0001.csv ... (plan.json ebay.listings_per_file
listings per file), plus a zip per store.
"""
import argparse, csv, gzip, html, json, sys, zipfile
from pathlib import Path

from compliance import check as ip_check

HERE = Path(__file__).resolve().parent
ACTION = "*Action(SiteID=UK|Country=GB|Currency=GBP|Version=1193|CC=UTF-8)"
HEADER = [ACTION, "CustomLabel", "*Category", "StoreCategory", "*Title", "Subtitle",
          "Relationship", "RelationshipDetails", "*ConditionID", "*Description", "PicURL",
          "*Format", "*Duration", "*StartPrice", "*Quantity", "*Location", "PostalCode",
          "DispatchTimeMax", "ShippingProfileName", "ReturnProfileName", "PaymentProfileName",
          "C:Brand", "C:Artist", "C:Type", "C:Size", "C:Frame", "C:Framing", "C:Subject", "C:Style",
          "C:Theme", "C:Room", "C:Colour", "C:Material", "C:Production Technique", "C:Orientation",
          "C:Features", "C:Unit Type"]

STYLE_WORD = {"stack": "Typography", "subway": "Typography", "left": "Modern", "frame": "Classic",
              "rules": "Typography", "arch": "Boho", "badge": "Minimalist", "ribbon": "Typography",
              "corner": "Modern", "block": "Modern"}
THEME = {
    "faith_christian": "Religion & Spirituality", "scripture": "Religion & Spirituality",
    "faith_blessings": "Religion & Spirituality", "faith_islamic": "Religion & Spirituality",
    "faith_dharmic": "Religion & Spirituality", "memorial": "Religion & Spirituality",
    "nursery_kids": "Children", "classroom": "Education", "biz_education": "Education",
    "travel_coastal": "Travel", "places_towns": "Cities & Places", "pets": "Animals",
    "christmas_seasonal": "Holidays & Seasons", "wedding_love": "Love & Romance",
    "kitchen": "Food & Drink", "coffee_cafe": "Food & Drink", "bar_pub": "Food & Drink",
    "biz_hospitality": "Food & Drink", "garden_outdoor": "Flowers & Plants",
}


THEME.update({"charts": "Education", "maps_country": "Maps", "maps_home": "Maps", "animals_flowers": "Animals",
              "animals_bw": "Animals", "bathroom_animals": "Animals", "nursery_animals": "Children",
              "dictionary_art": "Animals", "dressed_animals": "Animals", "christmas_animals": "Holidays & Seasons",
              "mummy_baby": "Animals", "animals_crown": "Animals", "animals_colourpop": "Animals",
              "animals_fun": "Animals", "botanical": "Flowers & Plants"})


def subject(row):
    kind = row.get("kind") or "text"
    if kind == "chart":
        return "Education"
    if kind == "map":
        return "Maps"
    if kind == "ai":
        return row.get("subject") or "Animals"
    return row["niche"].split("_")[-1].title() if not row["niche"].startswith("biz_") else "Typography"


def style_of(row):
    kind = row.get("kind") or "text"
    if kind == "text":
        return STYLE_WORD.get(row["layout"], "Typography")
    if kind == "chart":
        return "Educational"
    if kind == "map":
        return "Minimalist"
    t = row["title"].lower()
    return "Watercolour" if "watercolour" in t else "Vintage" if ("dictionary" in t or "vintage" in t) else "Photographic"


def money(x):
    return f"{x:.2f}"


KIND_TEXT = {
    "chart": "An educational wall chart for classrooms, playrooms and bedrooms. Clear, colourful and easy to read, "
             "printed on a clean white background in the UK on quality paper.",
    "map": "A map print drawn from accurate country outlines, printed on a clean white background in the UK on quality paper.",
    "ai": "An art print for your {room}, printed in the UK on quality paper.",
}
SOURCES = {"text": "{b}.csv.gz", "visual": "{b}_visual.csv.gz", "ai": "{b}_ai.csv.gz"}


def description(row, eb):
    kind = row.get("kind") or "text"
    if kind != "text":
        return _desc(html.escape(row["title"].split(" Print")[0], quote=False),
                     KIND_TEXT[kind].format(room=html.escape(row["room"].lower())), eb)
    phrase = html.escape(row["phrase"].split(" ~ ")[0].replace(" / ", " ").replace("*", ""), quote=False)
    ref = row["phrase"].split(" ~ ")[1] if " ~ " in row["phrase"] else ""
    return _desc(phrase + (" - " + html.escape(ref, quote=False) if ref else ""),
                 f'A typography print for your {html.escape(row["room"].lower())}. '
                 'Crisp lettering on a clean white background, printed in the UK on quality paper.', eb)


def _desc(heading, blurb, eb):
    sizes = ", ".join(eb["sizes"])
    lines = [
        f'<div style="font-family:Arial,sans-serif;max-width:760px;margin:auto;color:#222">',
        f'<h2 style="font-weight:normal">{heading}</h2>',
        f'<p>{blurb}</p>',
        "<h3>Options</h3><ul>",
        f"<li><b>Sizes:</b> {sizes} (A4 21 x 29.7 cm, A3 29.7 x 42 cm, A2 42 x 59.4 cm)</li>",
        "<li><b>Unframed:</b> print only, posted flat or rolled with protection.</li>",
        "<li><b>Black Frame:</b> the same print in a black frame, ready to hang.</li>",
        "</ul><p>Colours may vary slightly between screens and print.</p></div>",
    ]
    return "".join(lines)


def rows_for(row, store, eb, ebay_title):
    base = store["pic_base"].rstrip("/")
    pics = f"{base}/art/mock/{row['sku']}.jpg"          # one photo: the print in a black frame
    prof = {k: store["profiles"].get(k) or eb["profiles"].get(k, "") for k in ("shipping", "returns", "payment")}
    parent = dict.fromkeys(HEADER, "")
    parent.update({
        ACTION: "Add", "CustomLabel": row["sku"], "*Category": eb["category"], "*Title": ebay_title,
        "RelationshipDetails": "Size=" + ";".join(eb["sizes"]) + "|Frame=" + ";".join(eb["frames"]),
        "*ConditionID": eb["condition_id"], "*Description": description(row, eb), "PicURL": pics,
        "*Format": "FixedPrice", "*Duration": "GTC", "*Location": eb["location"],
        "DispatchTimeMax": str(eb["dispatch_days"]),
        "ShippingProfileName": prof["shipping"], "ReturnProfileName": prof["returns"],
        "PaymentProfileName": prof["payment"],
        "C:Brand": eb["brand"], "C:Artist": store["name"], "C:Type": "Print",
        "C:Subject": subject(row),
        "C:Style": style_of(row), "C:Theme": THEME.get(row["niche"], "Quotes & Sayings"),
        "C:Room": row["room"], "C:Colour": row["colour"], "C:Material": "Paper",
        "C:Production Technique": "Digital Print", "C:Orientation": "Portrait",
        "C:Features": "Unframed or Black Frame", "C:Unit Type": "Unit",
    })
    out = [parent]
    for frame in eb["frames"]:
        for size in eb["sizes"]:
            c = dict.fromkeys(HEADER, "")
            c.update({"Relationship": "Variation", "RelationshipDetails": f"Size={size}|Frame={frame}",
                      "*StartPrice": money(eb["prices"][frame][size]), "*Quantity": str(eb["quantity"]),
                      "C:Size": size, "C:Frame": frame,
                      "C:Framing": "Unframed" if frame == "Unframed" else "Framed"})
            out.append(c)
    return out


def build(store, eb, out_root, src_dir, sources=("text", "visual", "ai"), uploaded=None):
    """One set of files per source (text / visual / ai), so e.g. the AI files can be
    built later, once the GPU pod has uploaded those pictures."""
    dest = out_root / store["bucket"]
    dest.mkdir(parents=True, exist_ok=True)
    per = eb["listings_per_file"]
    rows_per_listing = 1 + len(eb["sizes"]) * len(eb["frames"])
    cap = eb.get("max_rows_per_file", 500000)
    if 1 + per * rows_per_listing > cap:          # header + listings must fit eBay's row limit
        per = (cap - 1) // rows_per_listing
    total = 0
    for source in sources:
        src = src_dir / SOURCES[source].format(b=store["bucket"])
        if not src.exists():
            continue
        for old in dest.glob(f"{store['bucket']}_{source}_*.csv"):
            old.unlink()
        n = files = blocked = missing = 0
        fh = w = None
        with gzip.open(src, "rt", encoding="utf-8") as fin:
            for row in csv.DictReader(fin):
                title = row["title"][:80]
                if ip_check(title) or ip_check(row.get("phrase") or ""):
                    blocked += 1
                    continue
                if uploaded is not None and f"art/mock/{row['sku']}.jpg" not in uploaded:
                    missing += 1          # no picture in the bucket yet - never list without one
                    continue
                if n % per == 0:
                    if fh:
                        fh.close()
                    files += 1
                    fh = open(dest / f"{store['bucket']}_{source}_{files:04d}.csv", "w", encoding="utf-8", newline="")
                    w = csv.DictWriter(fh, fieldnames=HEADER, extrasaction="ignore")
                    w.writeheader()
                w.writerows(rows_for(row, store, eb, title))
                n += 1
        if fh:
            fh.close()
        total += n
        print(f"{store['bucket']:20s} {source:6s} {n:>9,} listings  {files:>3} files  (IP-blocked {blocked}"
              + (f", waiting for pictures {missing:,}" if uploaded is not None else "") + ")", flush=True)
    z = out_root / f"{store['bucket']}_ebay_upload.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for f in sorted(dest.glob("*.csv")):
            zf.write(f, f"{store['bucket']}/{f.name}")
    return total


def check_files(out_root, eb):
    """Structural check: every parent is followed by exactly its variations."""
    bad = 0
    for f in sorted(out_root.glob("*/*.csv")):
        with open(f, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        i = 0
        while i < len(rows):
            p = rows[i]
            kids = rows[i + 1:i + 1 + len(eb["sizes"]) * len(eb["frames"])]
            if p[ACTION] != "Add" or not p["CustomLabel"] or not p["PicURL"] or len(p["*Title"]) > 80 \
                    or any(k[ACTION] or k["CustomLabel"] or k["Relationship"] != "Variation" or not k["*StartPrice"] for k in kids):
                bad += 1
            i += 1 + len(kids)
    print("structure problems:", bad)
    big = []
    for f in sorted(out_root.glob("*/*.csv")):
        with open(f, "rb") as fh:
            lines = sum(1 for _ in csv.reader(line.decode("utf-8") for line in fh))
        if lines > eb.get("max_rows_per_file", 500000):
            big.append((f.name, lines))
    print("files over the row limit:", big or "none")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--src", default=str(HERE / "out"), help="folder with <bucket>.csv.gz")
    ap.add_argument("--dest", help="default <src>/ebay")
    ap.add_argument("--source", choices=["text", "visual", "ai"], action="append",
                    help="only these catalogue parts (repeatable); default all")
    ap.add_argument("--only-uploaded", action="store_true",
                    help="skip listings whose picture is not in the bucket yet (needs R2 credentials)")
    a = ap.parse_args()
    plan = json.loads((HERE / "plan.json").read_text())
    eb = plan["ebay"]
    out_root = Path(a.dest) if a.dest else Path(a.src) / "ebay"
    if a.check:
        return check_files(out_root, eb)
    missing = [s["bucket"] for s in plan["stores"] if not s.get("pic_base")]
    if missing:
        print("WARNING: no public picture URL yet for", ", ".join(missing),
              "- PicURL will be relative. Set stores[].pic_base in plan.json (Cloudflare -> R2 -> "
              "bucket -> Settings -> Public access) and rebuild.", file=sys.stderr)
    empty = [k for k, v in eb["profiles"].items() if not v]
    if empty and not all(s["profiles"].get(k) for s in plan["stores"] for k in empty):
        print("WARNING: business policy names missing:", ", ".join(empty),
              "- set ebay.profiles (or per store) in plan.json to the exact names in each eBay account.",
              file=sys.stderr)
    for s in plan["stores"]:
        if a.store and s["bucket"] != a.store:
            continue
        uploaded = None
        if a.only_uploaded:
            from publish import s3, existing
            uploaded = existing(s3(), s["bucket"], "art/mock/")
        build(s, eb, out_root, Path(a.src), tuple(a.source or ("text", "visual", "ai")), uploaded)


if __name__ == "__main__":
    main()
