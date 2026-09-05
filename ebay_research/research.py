"""Research pipelines: the layer the UI (or a script) actually calls.

Each function pulls a corpus, runs the analytics, writes a snapshot for trend
comparison, and returns a plain JSON-serialisable report ending in a list of
plain-English findings.  Numbers nobody reads are not research.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from . import analytics, scoring, titles
from .cache import SnapshotStore
from .client import build_filter
from .errors import NotAvailableError
from .models import Corpus


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _fmt(value, currency="GBP"):
    if value is None:
        return "n/a"
    symbol = {"GBP": "£", "USD": "$", "EUR": "€"}.get(currency, "")
    return f"{symbol}{value:,.2f}" if symbol else f"{value:,.2f} {currency}"


def _collect_sold(client, query=None, category_ids=None, filters=None, max_items=200, days=90):
    """Fetch sold data, returning ``(records, warning)`` instead of raising."""
    try:
        records, _total = client.search_sold(
            query=query,
            category_ids=category_ids,
            filters=filters,
            max_items=max_items,
            days=days,
        )
        return records, None
    except NotAvailableError as exc:
        return [], str(exc)
    except Exception as exc:  # never let sold data break the whole report
        return [], f"Sold-item lookup failed: {exc}"


# ---------------------------------------------------------------------------
# Seller research
# ---------------------------------------------------------------------------


def research_seller(
    client,
    seller,
    query=None,
    category_ids=None,
    max_items=600,
    include_sold=True,
    store=None,
    progress=None,
):
    """Everything the API will tell us about one seller's live catalogue."""
    seller = (seller or "").strip()
    if not seller:
        raise ValueError("A seller username is required.")

    started = time.time()
    listings, total, truncated, per_category = client.sweep_seller(
        seller,
        query=query,
        category_ids=category_ids,
        max_items=max_items,
        progress=progress,
    )

    warnings = []
    sold = []
    if include_sold and listings:
        sold, warning = _collect_sold(
            client,
            query=query or None,
            category_ids=category_ids
            or (listings[0].category_id if not query else None),
            filters=build_filter(seller=seller),
            max_items=min(max_items, 200),
        )
        if warning:
            warnings.append(warning)

    corpus = Corpus(
        listings=listings,
        sold=sold,
        seller=seller,
        marketplace=client.settings.marketplace,
        total_matches=total,
        truncated=truncated,
        warnings=warnings,
    )

    report = _build_seller_report(corpus, per_category, client.settings.currency)
    report["elapsed_seconds"] = round(time.time() - started, 2)
    report["api_calls"] = dict(client.http.stats)

    if store is None:
        store = SnapshotStore(client.settings.cache_path)
    previous = store.history("seller", seller, corpus.marketplace, limit=1)
    report["trend"] = analytics.compare_snapshots(
        report, previous[0]["payload"] if previous else None
    )
    store.save("seller", seller, corpus.marketplace, _snapshot_payload(report))

    return report


def _snapshot_payload(report):
    """Trim a report to what trend comparison needs, so snapshots stay small."""
    return {
        "generated_at": report["generated_at"],
        "summary": report["summary"],
        "listings": [
            {
                "item_id": row["item_id"],
                "title": row["title"],
                "price": row["price"],
            }
            for row in report.get("listings", [])
        ],
    }


def _build_seller_report(corpus, per_category, currency):
    listings = corpus.listings
    title_texts = corpus.titles

    identity = {}
    if listings:
        scores = [l.seller_feedback_score for l in listings if l.seller_feedback_score]
        percentages = [l.seller_feedback_pct for l in listings if l.seller_feedback_pct]
        identity = {
            "username": corpus.seller,
            "feedback_score": max(scores) if scores else None,
            "feedback_pct": round(sum(percentages) / len(percentages), 2)
            if percentages
            else None,
            "countries": sorted({l.country for l in listings if l.country}),
            "top_rated_share": round(
                sum(1 for l in listings if l.top_rated) / len(listings), 4
            ),
        }

    prices = analytics.price_summary(listings)
    report = {
        "kind": "seller",
        "subject": corpus.seller,
        "marketplace": corpus.marketplace,
        "currency": currency,
        "generated_at": _now_iso(),
        "warnings": list(corpus.warnings),
        "summary": {
            "listings_sampled": len(listings),
            "listings_total": corpus.total_matches,
            "truncated": corpus.truncated,
            "median_price": prices.get("median"),
            "catalogue_value": round(
                sum(l.price for l in listings if l.price is not None), 2
            ),
        },
        "identity": identity,
        "prices": prices,
        "prices_excluding_shipping": analytics.price_summary(
            listings, include_shipping=False
        ),
        "price_histogram": analytics.histogram(
            [l.total_cost for l in listings if l.total_cost is not None]
        ),
        "format_mix": analytics.format_mix(listings),
        "condition_mix": analytics.condition_mix(listings),
        "category_mix": analytics.category_mix(listings),
        "category_totals": per_category or {},
        "shipping": analytics.shipping_profile(listings),
        "listing_age": analytics.listing_age_profile(listings),
        "promoted_share": analytics.promoted_share(listings),
        "title_stats": titles.title_stats(title_texts),
        "keywords": titles.keyword_table(title_texts, size=1, top=40, drop_noise=True),
        "phrases": titles.keyword_table(title_texts, size=2, top=25, drop_noise=True),
        "weakest_listings": scoring.audit_listings(listings, top=25),
        "listings": [l.to_row() for l in listings],
    }

    if corpus.sold:
        report["sold"] = {
            "records": [r.to_row() for r in corpus.sold],
            "performance": analytics.sell_through(len(listings), corpus.sold),
            "trend": analytics.sales_trend(corpus.sold),
            "price_bands": analytics.price_bands(listings, corpus.sold),
            "winning_terms": titles.distinctive_terms(
                [r.title for r in corpus.sold], title_texts, top=20
            ),
        }

    report["findings"] = _seller_findings(report)
    return report


def _seller_findings(report):
    """Turn the numbers into sentences a seller can act on."""
    out = []
    currency = report.get("currency", "GBP")
    summary = report["summary"]
    prices = report["prices"]
    stats = report["title_stats"]

    if not summary["listings_sampled"]:
        return [
            "No live listings found for this seller on this marketplace. Check the "
            "username spelling, or switch marketplace — a UK seller will not appear "
            "in an EBAY_US search."
        ]

    out.append(
        f"Sampled {summary['listings_sampled']} of {summary['listings_total']} live "
        f"listings. Median asking price (with postage) {_fmt(prices.get('median'), currency)}, "
        f"spanning {_fmt(prices.get('min'), currency)} to {_fmt(prices.get('max'), currency)}."
    )

    spread = prices.get("p75"), prices.get("p25")
    if all(spread) and spread[1] and spread[0] / spread[1] > 3:
        out.append(
            f"Very wide price spread: the top quartile starts at {_fmt(spread[0], currency)} "
            f"while the bottom quartile ends at {_fmt(spread[1], currency)}. This seller is "
            "running more than one product tier — analyse them separately."
        )

    formats = {row["value"]: row["share"] for row in report["format_mix"]}
    auction_share = formats.get("Auction", 0.0)
    if auction_share > 0.5:
        out.append(
            f"{auction_share:.0%} of the catalogue is auctions — they are letting the "
            "market set price rather than holding one."
        )
    offer_share = formats.get("Fixed price + Best Offer", 0.0)
    if offer_share > 0.3:
        out.append(
            f"{offer_share:.0%} of listings accept Best Offer, so advertised prices are "
            "a ceiling, not the real selling price."
        )

    shipping = report["shipping"]
    if shipping["listings_with_quote"]:
        out.append(
            f"{shipping['free_shipping_share']:.0%} of listings offer free postage"
            + (
                f"; the rest average {_fmt(shipping['paid_shipping'].get('mean'), currency)}."
                if shipping["paid_shipping"].get("count")
                else "."
            )
        )

    if report["promoted_share"] > 0.25:
        out.append(
            f"{report['promoted_share']:.0%} of their listings are promoted — they are "
            "paying for placement, which means organic ranking alone is not enough here."
        )

    age = report["listing_age"]
    if age.get("count") and age.get("stale_share", 0) > 0.3:
        out.append(
            f"{age['stale_share']:.0%} of stock has been listed over 90 days. Ageing "
            "inventory usually means the price is above what the market clears at."
        )

    if stats["count"]:
        out.append(
            f"Titles average {stats['avg_length']} of 80 characters "
            f"({stats['pct_using_full_length']:.0%} use 70+). "
            + (
                "There is unused search real estate in most of their listings."
                if stats["avg_length"] < 65
                else "They are using the title space well."
            )
        )
        if stats["pct_with_noise"] > 0.25:
            out.append(
                f"{stats['pct_with_noise']:.0%} of titles contain filler words "
                "('free postage', 'look', 'bargain') that match no real search."
            )

    if report["keywords"]:
        top = ", ".join(row["phrase"] for row in report["keywords"][:8])
        out.append(f"Their catalogue is built around: {top}.")

    sold = report.get("sold")
    if sold:
        performance = sold["performance"]
        out.append(
            f"Sold data (90 days): {performance['sold_units']} units, "
            f"{_fmt(performance['estimated_revenue'], currency)} estimated revenue, "
            f"sell-through {performance['sell_through_rate']:.0%}, averaging "
            f"{performance['units_per_day']} units/day."
        )
        winners = [row["phrase"] for row in sold["winning_terms"][:6]]
        if winners:
            out.append(
                "Terms that appear far more in their *sold* titles than their live ones: "
                + ", ".join(winners)
                + ". These are the words buyers are converting on."
            )

    trend = report.get("trend")
    if trend:
        out.append(
            f"Since the last run: {trend['new_listings']} new listings, "
            f"{trend['removed_listings']} gone (sold or ended), "
            f"{len(trend['price_changes'])} price changes."
        )

    if summary["truncated"]:
        out.append(
            f"Only part of the catalogue was sampled ({summary['listings_sampled']} of "
            f"{summary['listings_total']}). Raise the sample size or narrow with a "
            "keyword for a complete picture."
        )
    return out


# ---------------------------------------------------------------------------
# Market / keyword research
# ---------------------------------------------------------------------------


def research_market(
    client,
    query,
    category_ids=None,
    price_min=None,
    price_max=None,
    conditions=None,
    buying_options=None,
    max_items=400,
    include_sold=True,
    store=None,
    progress=None,
):
    """What a search term looks like as a market: supply, price, competition."""
    query = (query or "").strip()
    if not query and not category_ids:
        raise ValueError("Provide a search term or a category to research.")

    started = time.time()
    filters = build_filter(
        price_min=price_min,
        price_max=price_max,
        currency=client.settings.currency,
        conditions=conditions,
        buying_options=buying_options,
    )
    listings, total, truncated = client.search(
        query=query or None,
        category_ids=category_ids,
        filters=filters or None,
        max_items=max_items,
        progress=progress,
    )

    warnings = []
    sold = []
    if include_sold:
        sold, warning = _collect_sold(
            client,
            query=query or None,
            category_ids=category_ids,
            filters=filters or None,
            max_items=min(max_items, 200),
        )
        if warning:
            warnings.append(warning)

    corpus = Corpus(
        listings=listings,
        sold=sold,
        query=query,
        marketplace=client.settings.marketplace,
        total_matches=total,
        truncated=truncated,
        warnings=warnings,
    )
    report = _build_market_report(corpus, client.settings.currency)
    report["elapsed_seconds"] = round(time.time() - started, 2)
    report["api_calls"] = dict(client.http.stats)

    if store is None:
        store = SnapshotStore(client.settings.cache_path)
    previous = store.history("market", query, corpus.marketplace, limit=1)
    report["trend"] = analytics.compare_snapshots(
        report, previous[0]["payload"] if previous else None
    )
    store.save("market", query, corpus.marketplace, _snapshot_payload(report))
    return report


def _build_market_report(corpus, currency):
    listings = corpus.listings
    title_texts = corpus.titles
    prices = analytics.price_summary(listings)

    report = {
        "kind": "market",
        "subject": corpus.query,
        "marketplace": corpus.marketplace,
        "currency": currency,
        "generated_at": _now_iso(),
        "warnings": list(corpus.warnings),
        "summary": {
            "listings_sampled": len(listings),
            "listings_total": corpus.total_matches,
            "truncated": corpus.truncated,
            "median_price": prices.get("median"),
        },
        "prices": prices,
        "price_histogram": analytics.histogram(
            [l.total_cost for l in listings if l.total_cost is not None]
        ),
        "competition": analytics.competition(listings),
        "format_mix": analytics.format_mix(listings),
        "condition_mix": analytics.condition_mix(listings),
        "category_mix": analytics.category_mix(listings),
        "shipping": analytics.shipping_profile(listings),
        "listing_age": analytics.listing_age_profile(listings),
        "promoted_share": analytics.promoted_share(listings),
        "title_stats": titles.title_stats(title_texts),
        "keywords": titles.keyword_table(title_texts, size=1, top=40, drop_noise=True),
        "phrases": titles.keyword_table(title_texts, size=2, top=25, drop_noise=True),
        "sellers": analytics.seller_leaderboard(listings, corpus.sold),
        "listings": [l.to_row() for l in listings],
    }

    outlier_values, fences = analytics.outliers(
        [l.total_cost for l in listings if l.total_cost is not None]
    )
    report["price_outliers"] = {"values": outlier_values[:20], "fences": fences}

    if corpus.sold:
        report["sold"] = {
            "records": [r.to_row() for r in corpus.sold],
            "performance": analytics.sell_through(len(listings), corpus.sold),
            "trend": analytics.sales_trend(corpus.sold),
            "price_bands": analytics.price_bands(listings, corpus.sold),
            "winning_terms": titles.distinctive_terms(
                [r.title for r in corpus.sold], title_texts, top=20
            ),
            "sold_prices": analytics.describe([r.price for r in corpus.sold]),
        }

    report["findings"] = _market_findings(report)
    return report


def _market_findings(report):
    out = []
    currency = report.get("currency", "GBP")
    summary = report["summary"]
    prices = report["prices"]
    competition = report["competition"]

    if not summary["listings_sampled"]:
        return [
            "No live listings matched. Try a broader term, drop the price filter, "
            "or check you are on the right marketplace."
        ]

    out.append(
        f"{summary['listings_total']:,} live listings match '{report['subject']}'. "
        f"Sampled {summary['listings_sampled']} of them. Typical buyer pays "
        f"{_fmt(prices.get('median'), currency)} including postage; the middle 50% sits "
        f"between {_fmt(prices.get('p25'), currency)} and {_fmt(prices.get('p75'), currency)}."
    )

    out.append(
        f"{competition['sellers']} distinct sellers in the sample "
        f"({competition['listings_per_seller']} listings each on average) — "
        f"{competition['concentration']} (HHI {competition['hhi']})."
    )
    if competition["top_sellers"]:
        leader = competition["top_sellers"][0]
        if leader["share"] > 0.15:
            out.append(
                f"{leader['seller']} alone holds {leader['share']:.0%} of the listings "
                "on this search — study their titles and pricing before competing."
            )

    if report["promoted_share"] > 0.3:
        out.append(
            f"{report['promoted_share']:.0%} of results are promoted listings. Organic "
            "placement on page one is unlikely here without an ad budget."
        )

    stats = report["title_stats"]
    if stats["count"]:
        out.append(
            f"Competitor titles average {stats['avg_length']} characters; "
            f"{stats['pct_using_full_length']:.0%} use 70 or more. "
            + (
                "Most are leaving search coverage on the table — an easy edge."
                if stats["avg_length"] < 65
                else "The bar is high: write a full 80-character title."
            )
        )

    if report["keywords"]:
        must_have = [
            row["phrase"] for row in report["keywords"][:10] if row["share"] >= 0.25
        ]
        if must_have:
            out.append(
                "Words appearing in a quarter or more of listings — treat as mandatory: "
                + ", ".join(must_have)
                + "."
            )
        long_tail = [
            row["phrase"]
            for row in report["keywords"]
            if 0.03 <= row["share"] <= 0.12
        ][:8]
        if long_tail:
            out.append(
                "Long-tail terms used by only a few competitors (less contested, "
                "cheaper to rank for): " + ", ".join(long_tail) + "."
            )

    sold = report.get("sold")
    if sold:
        performance = sold["performance"]
        out.append(
            f"Demand check: {performance['sold_units']} units sold in 90 days "
            f"({performance['units_per_day']}/day), sell-through "
            f"{performance['sell_through_rate']:.0%}, average sale price "
            f"{_fmt(performance['average_sale_price'], currency)}."
        )
        asking = prices.get("median")
        selling = sold["sold_prices"].get("median")
        if asking and selling:
            gap = (asking - selling) / selling
            if abs(gap) > 0.1:
                direction = "above" if gap > 0 else "below"
                out.append(
                    f"Asking prices sit {abs(gap):.0%} {direction} what items actually "
                    f"sell for ({_fmt(asking, currency)} asked vs {_fmt(selling, currency)} paid). "
                    + (
                        "Sellers are over-pricing and waiting."
                        if gap > 0
                        else "Stock is scarce and buyers are paying up."
                    )
                )
        best = max(
            (band for band in sold["price_bands"] if band["sold"]),
            key=lambda band: band["sell_through_rate"],
            default=None,
        )
        if best:
            out.append(
                f"Best-converting price band: {_fmt(best['band_low'], currency)}–"
                f"{_fmt(best['band_high'], currency)} at "
                f"{best['sell_through_rate']:.0%} sell-through "
                f"({best['sold']} sold against {best['active']} on offer)."
            )
        winners = [row["phrase"] for row in sold["winning_terms"][:8]]
        if winners:
            out.append(
                "Gap analysis — words far more common in sold titles than in live ones: "
                + ", ".join(winners)
                + ". Put these in your title."
            )
    else:
        out.append(
            "Sold-item data was not available, so everything above is asking prices, "
            "not achieved prices. Treat the medians as an upper bound."
        )

    return out


# ---------------------------------------------------------------------------
# Head-to-head
# ---------------------------------------------------------------------------


def compare_sellers(client, sellers, query=None, max_items=200):
    """Put several sellers side by side on the same terms."""
    rows = []
    for seller in sellers:
        seller = (seller or "").strip()
        if not seller:
            continue
        listings, total, _truncated, _cats = client.sweep_seller(
            seller, query=query, max_items=max_items
        )
        prices = analytics.price_summary(listings)
        stats = titles.title_stats([l.title for l in listings])
        formats = {row["value"]: row["share"] for row in analytics.format_mix(listings)}
        rows.append(
            {
                "seller": seller,
                "listings_total": total,
                "listings_sampled": len(listings),
                "median_price": prices.get("median"),
                "p25_price": prices.get("p25"),
                "p75_price": prices.get("p75"),
                "avg_title_length": stats["avg_length"],
                "titles_with_noise": stats["pct_with_noise"],
                "free_shipping_share": analytics.shipping_profile(listings)[
                    "free_shipping_share"
                ],
                "promoted_share": analytics.promoted_share(listings),
                "auction_share": formats.get("Auction", 0.0),
                "top_keywords": [
                    row["phrase"]
                    for row in titles.keyword_table(
                        [l.title for l in listings], top=8, drop_noise=True
                    )
                ],
            }
        )
    return {
        "kind": "comparison",
        "generated_at": _now_iso(),
        "marketplace": client.settings.marketplace,
        "currency": client.settings.currency,
        "query": query or "",
        "sellers": rows,
    }
