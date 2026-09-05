"""Statistics over a corpus of listings and sales.

Pure Python by design: no pandas, no numpy.  The Streamlit layer is free to
wrap these results in a dataframe, but the maths is testable on its own and
runs anywhere.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone


def _clean(values):
    return sorted(v for v in values if isinstance(v, (int, float)) and not math.isnan(v))


def percentile(values, q):
    """Linear-interpolation percentile.  ``q`` is 0..1."""
    ordered = _clean(values)
    if not ordered:
        return None
    if len(ordered) == 1:
        return float(ordered[0])
    position = (len(ordered) - 1) * min(max(q, 0.0), 1.0)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return float(ordered[int(position)])
    weight = position - low
    return float(ordered[low] * (1 - weight) + ordered[high] * weight)


def describe(values):
    """Full numeric summary of a series."""
    ordered = _clean(values)
    if not ordered:
        return {"count": 0}
    count = len(ordered)
    mean = sum(ordered) / count
    variance = sum((v - mean) ** 2 for v in ordered) / count if count > 1 else 0.0
    return {
        "count": count,
        "min": round(ordered[0], 2),
        "p10": round(percentile(ordered, 0.10), 2),
        "p25": round(percentile(ordered, 0.25), 2),
        "median": round(percentile(ordered, 0.50), 2),
        "p75": round(percentile(ordered, 0.75), 2),
        "p90": round(percentile(ordered, 0.90), 2),
        "max": round(ordered[-1], 2),
        "mean": round(mean, 2),
        "stdev": round(math.sqrt(variance), 2),
    }


def histogram(values, bins=12):
    """``[(low, high, count), ...]`` over the observed range."""
    ordered = _clean(values)
    if not ordered:
        return []
    low, high = ordered[0], ordered[-1]
    if high == low:
        return [(low, high, len(ordered))]
    bins = max(1, int(bins))
    width = (high - low) / bins
    counts = [0] * bins
    for value in ordered:
        index = min(int((value - low) / width), bins - 1)
        counts[index] += 1
    return [
        (round(low + i * width, 2), round(low + (i + 1) * width, 2), counts[i])
        for i in range(bins)
    ]


def outliers(values, factor=1.5):
    """Values beyond the Tukey fences — usually mispriced or miscategorised."""
    ordered = _clean(values)
    if len(ordered) < 4:
        return [], (None, None)
    q1 = percentile(ordered, 0.25)
    q3 = percentile(ordered, 0.75)
    iqr = q3 - q1
    low_fence = q1 - factor * iqr
    high_fence = q3 + factor * iqr
    flagged = [v for v in ordered if v < low_fence or v > high_fence]
    return flagged, (round(low_fence, 2), round(high_fence, 2))


def share_of(items, key):
    """Counter of ``key(item)`` plus each value's share of the whole."""
    counts = Counter()
    for item in items:
        value = key(item)
        if value in (None, ""):
            value = "Unknown"
        counts[value] += 1
    total = sum(counts.values()) or 1
    return [
        {"value": value, "count": count, "share": round(count / total, 4)}
        for value, count in counts.most_common()
    ]


def price_summary(listings, include_shipping=True):
    """Price statistics, optionally on the buyer's true total cost."""
    getter = (lambda l: l.total_cost) if include_shipping else (lambda l: l.price)
    return describe([getter(l) for l in listings])


def format_mix(listings):
    def label(listing):
        if listing.is_auction:
            return "Auction"
        if listing.accepts_offers:
            return "Fixed price + Best Offer"
        return "Fixed price"

    return share_of(listings, label)


def condition_mix(listings):
    return share_of(listings, lambda l: l.condition or "Unspecified")


def category_mix(listings):
    return share_of(listings, lambda l: l.category_name or "Unknown")


def shipping_profile(listings):
    """Free-shipping share and what the rest actually charge."""
    quoted = [l.shipping_cost for l in listings if l.shipping_cost is not None]
    free = sum(1 for cost in quoted if cost == 0)
    paid = [cost for cost in quoted if cost > 0]
    return {
        "listings_with_quote": len(quoted),
        "free_shipping_share": round(free / len(quoted), 4) if quoted else 0.0,
        "paid_shipping": describe(paid),
    }


def competition(listings):
    """How concentrated the market is.

    The Herfindahl-Hirschman Index over listing share tells a seller whether
    they are entering a market owned by two big players or a long tail of
    small ones.  Above ~0.25 is concentrated; below ~0.10 is fragmented.
    """
    sellers = Counter(l.seller for l in listings if l.seller)
    total = sum(sellers.values())
    if not total:
        return {"sellers": 0, "hhi": 0.0, "top_sellers": [], "concentration": "unknown"}
    hhi = sum((count / total) ** 2 for count in sellers.values())
    if hhi >= 0.25:
        label = "concentrated — a few sellers own this search"
    elif hhi >= 0.10:
        label = "moderately concentrated"
    else:
        label = "fragmented — no single seller dominates"
    top = [
        {
            "seller": seller,
            "listings": count,
            "share": round(count / total, 4),
        }
        for seller, count in sellers.most_common(15)
    ]
    return {
        "sellers": len(sellers),
        "listings": total,
        "listings_per_seller": round(total / len(sellers), 2),
        "hhi": round(hhi, 4),
        "concentration": label,
        "top_sellers": top,
    }


def sell_through(active_count, sold_records, days=90):
    """Sell-through rate and sales velocity for a market.

    STR is defined here as ``sold / (sold + active)`` over the window, the
    convention research tools use.  It is an estimate: eBay's sold data covers
    90 days while the active count is a snapshot of right now.
    """
    units = sum(max(record.quantity, 1) for record in sold_records)
    listings_sold = len(sold_records)
    denominator = listings_sold + max(active_count, 0)
    revenue = sum(
        (record.price or 0.0) * max(record.quantity, 1) for record in sold_records
    )
    return {
        "window_days": days,
        "sold_listings": listings_sold,
        "sold_units": units,
        "active_listings": active_count,
        "sell_through_rate": round(listings_sold / denominator, 4) if denominator else 0.0,
        "units_per_day": round(units / days, 2) if days else 0.0,
        "estimated_revenue": round(revenue, 2),
        "average_sale_price": round(revenue / units, 2) if units else None,
    }


def sales_trend(sold_records, bucket_days=7, now=None):
    """Units sold per bucket, oldest first — the shape of demand over time."""
    now = now or datetime.now(timezone.utc)
    buckets = defaultdict(int)
    values = defaultdict(float)
    for record in sold_records:
        if not record.sold_date:
            continue
        age = (now - record.sold_date).days
        if age < 0:
            age = 0
        index = age // max(1, bucket_days)
        buckets[index] += max(record.quantity, 1)
        values[index] += (record.price or 0.0) * max(record.quantity, 1)
    if not buckets:
        return []
    out = []
    for index in sorted(buckets, reverse=True):
        start = now - timedelta(days=(index + 1) * bucket_days)
        out.append(
            {
                "period_start": start.date().isoformat(),
                "units": buckets[index],
                "revenue": round(values[index], 2),
            }
        )
    return out


def price_bands(listings, sold_records, bands=6):
    """Where the demand sits.

    Splits the price range into bands and reports active supply against sold
    demand in each.  The band with the highest sell-through is where a new
    listing has the best chance — and it is very often not the cheapest band.
    """
    active_prices = [l.total_cost for l in listings if l.total_cost is not None]
    sold_prices = [r.price for r in sold_records if r.price is not None]
    combined = _clean(active_prices + sold_prices)
    if not combined:
        return []
    low = percentile(combined, 0.02)
    high = percentile(combined, 0.98)
    if high <= low:
        high = low + 1.0
    width = (high - low) / max(1, bands)

    rows = []
    for i in range(bands):
        start = low + i * width
        end = low + (i + 1) * width
        in_band = lambda v, s=start, e=end, last=(i == bands - 1): (
            s <= v <= e if last else s <= v < e
        )
        active = sum(1 for v in active_prices if in_band(v))
        sold = sum(1 for v in sold_prices if in_band(v))
        denominator = active + sold
        rows.append(
            {
                "band_low": round(start, 2),
                "band_high": round(end, 2),
                "active": active,
                "sold": sold,
                "sell_through_rate": round(sold / denominator, 4) if denominator else 0.0,
            }
        )
    return rows


def listing_age_profile(listings, now=None):
    """How long stock has been sitting — stale inventory is a pricing signal."""
    now = now or datetime.now(timezone.utc)
    ages = [l.age_days(now) for l in listings]
    ages = [age for age in ages if age is not None]
    if not ages:
        return {"count": 0}
    summary = describe(ages)
    summary["over_30_days"] = sum(1 for age in ages if age > 30)
    summary["over_90_days"] = sum(1 for age in ages if age > 90)
    summary["stale_share"] = round(summary["over_90_days"] / len(ages), 4)
    return summary


def promoted_share(listings):
    """Share of listings paying for promotion — a proxy for how hard it is to rank."""
    if not listings:
        return 0.0
    return round(sum(1 for l in listings if l.promoted) / len(listings), 4)


def seller_leaderboard(listings, sold_records=None, top=20):
    """Per-seller aggregates across whatever corpus we sampled."""
    grouped = defaultdict(list)
    for listing in listings:
        if listing.seller:
            grouped[listing.seller].append(listing)

    sold_by_seller = Counter()
    revenue_by_seller = Counter()
    for record in sold_records or []:
        if record.seller:
            sold_by_seller[record.seller] += max(record.quantity, 1)
            revenue_by_seller[record.seller] += (record.price or 0.0) * max(
                record.quantity, 1
            )

    rows = []
    for seller, items in grouped.items():
        prices = [i.total_cost for i in items if i.total_cost is not None]
        feedback = [
            i.seller_feedback_score for i in items if i.seller_feedback_score is not None
        ]
        rows.append(
            {
                "seller": seller,
                "listings": len(items),
                "median_price": round(percentile(prices, 0.5), 2) if prices else None,
                "min_price": round(min(prices), 2) if prices else None,
                "max_price": round(max(prices), 2) if prices else None,
                "feedback_score": max(feedback) if feedback else None,
                "promoted_share": promoted_share(items),
                "free_shipping_share": round(
                    sum(1 for i in items if i.free_shipping) / len(items), 4
                ),
                "sold_units_90d": sold_by_seller.get(seller, 0) or None,
                "revenue_90d": round(revenue_by_seller[seller], 2)
                if revenue_by_seller.get(seller)
                else None,
            }
        )
    rows.sort(key=lambda row: row["listings"], reverse=True)
    return rows[:top]


def compare_snapshots(current, previous):
    """Diff two research runs of the same subject.

    Answers the questions a one-off scrape cannot: did the catalogue grow, did
    prices move, and which items vanished (usually because they sold).
    """
    if not previous:
        return None
    now_ids = {l["item_id"] for l in current.get("listings", []) if l.get("item_id")}
    then_ids = {l["item_id"] for l in previous.get("listings", []) if l.get("item_id")}
    then_by_id = {
        l["item_id"]: l for l in previous.get("listings", []) if l.get("item_id")
    }
    now_by_id = {l["item_id"]: l for l in current.get("listings", []) if l.get("item_id")}

    changed = []
    for item_id in now_ids & then_ids:
        before = then_by_id[item_id].get("price")
        after = now_by_id[item_id].get("price")
        if before and after and abs(after - before) > 0.005:
            changed.append(
                {
                    "item_id": item_id,
                    "title": now_by_id[item_id].get("title", ""),
                    "was": before,
                    "now": after,
                    "change": round(after - before, 2),
                    "change_pct": round((after - before) / before, 4),
                }
            )
    changed.sort(key=lambda row: abs(row["change_pct"]), reverse=True)

    current_prices = [
        l.get("price") for l in current.get("listings", []) if l.get("price")
    ]
    previous_prices = [
        l.get("price") for l in previous.get("listings", []) if l.get("price")
    ]

    return {
        "previous_run": previous.get("generated_at"),
        "listings_before": len(then_ids),
        "listings_now": len(now_ids),
        "new_listings": len(now_ids - then_ids),
        "removed_listings": len(then_ids - now_ids),
        "median_price_before": round(percentile(previous_prices, 0.5), 2)
        if previous_prices
        else None,
        "median_price_now": round(percentile(current_prices, 0.5), 2)
        if current_prices
        else None,
        "price_changes": changed[:50],
        "removed_examples": [
            {"item_id": i, "title": then_by_id[i].get("title", "")}
            for i in list(then_ids - now_ids)[:25]
        ],
    }
