"""Listing rotation: find the dead ones, free the slot, replace, retest.

You have a hard cap on live listings. A listing that has had twenty videos
pointed at it and sold nothing is not "still warming up" - it is occupying a
slot that an untested listing could be using. This module makes that call on
evidence rather than on how much you like the product.

  python -m wonderfeed.listings status
  python -m wonderfeed.listings add --sku WL-001 --product botanical-3set --title "..."
  python -m wonderfeed.listings import --csv seller-center-export.csv
  python -m wonderfeed.listings review
  python -m wonderfeed.listings cull --sku WL-001
"""

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .config import ConfigError, ROOT, load_settings
from .state import State

DEFAULTS = {
    "cap": 100,
    "grace_days": 14,
    "review_window_days": 30,
    "min_units": 1,
    "min_views": 300,
    "cull_after_videos": 15,
}

# TikTok Shop's export headers move around between markets and versions, so
# match loosely on lowercased fragments.
COLUMN_HINTS = {
    "sku": ["seller sku", "sku", "product id", "listing id"],
    "title": ["product name", "title", "product"],
    "views": ["product views", "views", "impressions", "page views"],
    "clicks": ["clicks", "product clicks", "visitors"],
    "units": ["units sold", "items sold", "sku orders", "orders", "sold"],
    "revenue": ["gmv", "revenue", "sales amount", "sales"],
}


class Listings:
    def __init__(self, path=None):
        self.path = Path(path) if path else ROOT / "out" / "listings.json"
        self.data = {"listings": []}
        if self.path.exists():
            with self.path.open(encoding="utf-8") as fh:
                self.data = json.load(fh)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2)
        tmp.replace(self.path)

    def find(self, sku):
        return next((l for l in self.data["listings"] if l["sku"] == sku), None)

    def live(self):
        return [l for l in self.data["listings"] if l.get("status", "live") == "live"]

    def add(self, sku, product_id, title="", link="", listed_on=None):
        if self.find(sku):
            raise ConfigError(f"listing '{sku}' already exists")
        self.data["listings"].append({
            "sku": sku,
            "product_id": product_id,
            "title": title,
            "link": link,
            "listed_on": listed_on or date.today().isoformat(),
            "status": "live",
            "stats": [],
        })

    def record_stats(self, sku, row, on=None):
        listing = self.find(sku)
        if not listing:
            return False
        row = dict(row)
        row["on"] = on or date.today().isoformat()
        listing.setdefault("stats", []).append(row)
        return True

    def cull(self, sku, reason=""):
        listing = self.find(sku)
        if not listing:
            raise ConfigError(f"no listing '{sku}'")
        listing["status"] = "culled"
        listing["culled_on"] = date.today().isoformat()
        listing["cull_reason"] = reason
        return listing


# -- evidence ------------------------------------------------------------


def _latest(listing, window_days):
    """Most recent stats row inside the window, plus totals across it."""
    cutoff = date.today() - timedelta(days=window_days)
    rows = []
    for r in listing.get("stats", []):
        try:
            when = date.fromisoformat(r["on"])
        except (KeyError, ValueError):
            continue
        if when >= cutoff:
            rows.append(r)
    totals = {k: 0 for k in ("views", "clicks", "units")}
    for r in rows:
        for k in totals:
            try:
                totals[k] += int(float(r.get(k) or 0))
            except (TypeError, ValueError):
                pass
    return totals, len(rows)


def days_live(listing):
    try:
        return (date.today() - date.fromisoformat(listing["listed_on"])).days
    except (KeyError, ValueError):
        return 0


def videos_for(product_id, state):
    return sum(1 for v in state.data.get("videos", [])
               if v.get("product_id") == product_id and not v.get("dry_run"))


def assess(listing, cfg, state):
    """KEEP / WATCH / CULL / TOO EARLY, with the reason spelled out."""
    age = days_live(listing)
    totals, n_rows = _latest(listing, cfg["review_window_days"])
    videos = videos_for(listing["product_id"], state)

    if age < cfg["grace_days"]:
        return ("TOO EARLY",
                f"{age}d live, needs {cfg['grace_days']}d before judging", totals, videos)

    if not n_rows:
        return ("NO DATA",
                f"{age}d live but no stats imported - run `listings import`", totals, videos)

    if totals["units"] >= cfg["min_units"]:
        return ("KEEP",
                f"{totals['units']} units in {cfg['review_window_days']}d", totals, videos)

    # Zero sales from here down. How hard did we actually try?
    if videos >= cfg["cull_after_videos"]:
        return ("CULL",
                f"{videos} videos posted, {totals['views']} views, 0 units", totals, videos)

    if totals["views"] >= cfg["min_views"]:
        return ("CULL",
                f"{totals['views']} views but 0 units - traffic converts nowhere",
                totals, videos)

    return ("WATCH",
            f"only {totals['views']} views from {videos} videos - not enough traffic "
            f"to judge the listing yet", totals, videos)


def config(settings):
    cfg = dict(DEFAULTS)
    cfg.update(settings.get("listings") or {})
    return cfg


# -- CSV import ----------------------------------------------------------


def map_columns(header):
    """Map a Seller Center export's headers onto our fields, loosely."""
    lowered = [(h or "").strip().lower() for h in header]
    mapping = {}
    for field, hints in COLUMN_HINTS.items():
        for hint in hints:  # most specific hints first
            for i, col in enumerate(lowered):
                if hint == col or (hint in col and i not in mapping.values()):
                    mapping[field] = i
                    break
            if field in mapping:
                break
    return mapping


def import_csv(listings, csv_path, log=print):
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        raise ConfigError("CSV is empty")

    header, body = rows[0], rows[1:]
    mapping = map_columns(header)
    if "sku" not in mapping:
        raise ConfigError(
            f"Could not find a SKU column in: {', '.join(header[:12])}\n"
            "Rename the column to 'Seller SKU' and retry."
        )
    log(f"  columns mapped: " + ", ".join(f"{k}->{header[i]!r}" for k, i in mapping.items()))

    def cell(row, field):
        i = mapping.get(field)
        if i is None or i >= len(row):
            return None
        return (row[i] or "").replace(",", "").replace("£", "").strip() or None

    matched = unknown = 0
    for row in body:
        if not any(row):
            continue
        sku = cell(row, "sku")
        if not sku:
            continue
        stats = {f: cell(row, f) for f in ("views", "clicks", "units", "revenue")}
        if listings.record_stats(sku, stats):
            matched += 1
        else:
            unknown += 1
            log(f"  ! unknown SKU '{sku}' - add it with `listings add` first")
    log(f"  {matched} listing(s) updated, {unknown} unrecognised")
    return matched


# -- CLI -----------------------------------------------------------------


def cmd_status(listings, cfg, state, args):
    live = listings.live()
    culled = [l for l in listings.data["listings"] if l.get("status") == "culled"]
    free = cfg["cap"] - len(live)
    print(f"Live listings : {len(live)}/{cfg['cap']}")
    print(f"Free slots    : {free}")
    print(f"Culled to date: {len(culled)}")
    if not live:
        print("\nNothing registered yet. Add one:\n"
              "  python -m wonderfeed.listings add --sku WL-001 "
              "--product botanical-3set --title 'Botanical Trio'")
        return 0
    print(f"\n{'SKU':<14} {'PRODUCT':<18} {'AGE':>5} {'VIDS':>5} {'VIEWS':>7} {'UNITS':>6}")
    print("-" * 60)
    for l in sorted(live, key=lambda x: x["listed_on"]):
        totals, _ = _latest(l, cfg["review_window_days"])
        print(f"{l['sku']:<14} {l['product_id'][:18]:<18} {days_live(l):>4}d "
              f"{videos_for(l['product_id'], state):>5} {totals['views']:>7} "
              f"{totals['units']:>6}")
    return 0


def cmd_review(listings, cfg, state, args):
    live = listings.live()
    if not live:
        print("No live listings to review.")
        return 0

    buckets = {}
    for l in live:
        verdict, reason, totals, videos = assess(l, cfg, state)
        buckets.setdefault(verdict, []).append((l, reason))

    order = ["CULL", "WATCH", "NO DATA", "TOO EARLY", "KEEP"]
    for verdict in order:
        items = buckets.get(verdict)
        if not items:
            continue
        print(f"\n{verdict}  ({len(items)})")
        print("-" * 60)
        for l, reason in items:
            print(f"  {l['sku']:<14} {l['title'][:30]:<32} {reason}")

    to_cull = buckets.get("CULL", [])
    free_now = cfg["cap"] - len(live)
    print(f"\n{'=' * 60}")
    print(f"Slots: {len(live)}/{cfg['cap']} used, {free_now} free now.")
    if to_cull:
        print(f"Culling the {len(to_cull)} above frees {len(to_cull)} more "
              f"-> {free_now + len(to_cull)} slots to fill with new tests.")
        print("\nApply with:")
        for l, _ in to_cull:
            print(f"  python -m wonderfeed.listings cull --sku {l['sku']}")
    else:
        print("Nothing to cull. Every live listing is either selling or still "
              "inside its test window.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Manage listing rotation.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="cap usage and per-listing performance")
    sub.add_parser("review", help="verdicts and what to cull")

    p_add = sub.add_parser("add", help="register a new live listing")
    p_add.add_argument("--sku", required=True)
    p_add.add_argument("--product", required=True, help="product id from products.yaml")
    p_add.add_argument("--title", default="")
    p_add.add_argument("--link", default="")
    p_add.add_argument("--listed-on", help="YYYY-MM-DD (defaults to today)")

    p_imp = sub.add_parser("import", help="ingest a Seller Center CSV export")
    p_imp.add_argument("--csv", required=True)

    p_cull = sub.add_parser("cull", help="mark a listing dead and free its slot")
    p_cull.add_argument("--sku", required=True)
    p_cull.add_argument("--reason", default="manual")

    args = ap.parse_args(argv)

    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    cfg = config(settings)
    listings = Listings()
    state = State()

    try:
        if args.cmd == "status":
            return cmd_status(listings, cfg, state, args)
        if args.cmd == "review":
            return cmd_review(listings, cfg, state, args)
        if args.cmd == "add":
            listings.add(args.sku, args.product, args.title, args.link, args.listed_on)
            listings.save()
            live = len(listings.live())
            print(f"Added {args.sku}. Live: {live}/{cfg['cap']} "
                  f"({cfg['cap'] - live} slots free).")
            return 0
        if args.cmd == "import":
            import_csv(listings, args.csv)
            listings.save()
            print("Imported. Run `python -m wonderfeed.listings review` next.")
            return 0
        if args.cmd == "cull":
            listing = listings.cull(args.sku, args.reason)
            listings.save()
            live = len(listings.live())
            print(f"Culled {listing['sku']}. Live: {live}/{cfg['cap']} "
                  f"({cfg['cap'] - live} slots free).")
            print("Remove it in Seller Center too - this only tracks the decision.")
            return 0
    except ConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
