"""Typed records parsed from eBay API payloads.

Everything downstream (analytics, scoring, exports) works on these objects
rather than raw dicts, so a change in eBay's JSON shape is a one-file fix.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def _money(node):
    """Extract ``(value, currency)`` from an eBay Amount node."""
    if not isinstance(node, dict):
        return None, None
    raw = node.get("value")
    if raw in (None, ""):
        return None, node.get("currency")
    try:
        return float(raw), node.get("currency")
    except (TypeError, ValueError):
        return None, node.get("currency")


def _parse_date(raw):
    """eBay timestamps are ISO-8601 with a trailing Z."""
    if not raw:
        return None
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _int(raw):
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _shipping(summary):
    """Cheapest shipping option: ``(cost, is_free)``.

    ``None`` cost means eBay did not quote one (collection only, or a
    calculated rate that needs a destination postcode).
    """
    options = summary.get("shippingOptions")
    if not isinstance(options, list) or not options:
        return None, False
    costs = []
    for option in options:
        value, _ = _money(option.get("shippingCost"))
        if value is not None:
            costs.append(value)
    if not costs:
        return None, False
    cheapest = min(costs)
    return cheapest, cheapest == 0.0


@dataclass
class Listing:
    """One active listing from the Browse API's ``item_summary`` search."""

    item_id: str = ""
    legacy_id: str = ""
    title: str = ""
    subtitle: str = ""
    price: float | None = None
    currency: str = ""
    shipping_cost: float | None = None
    free_shipping: bool = False
    condition: str = ""
    condition_id: str = ""
    buying_options: tuple = ()
    bid_count: int | None = None
    seller: str = ""
    seller_feedback_pct: float | None = None
    seller_feedback_score: int | None = None
    categories: tuple = ()
    category_id: str = ""
    category_name: str = ""
    country: str = ""
    created: datetime | None = None
    ends: datetime | None = None
    image_url: str = ""
    url: str = ""
    top_rated: bool = False
    promoted: bool = False
    available_quantity: int | None = None
    sold_quantity: int | None = None
    marketplace: str = ""

    # -- derived -----------------------------------------------------------

    @property
    def total_cost(self):
        """Price plus cheapest quoted shipping -- what the buyer actually pays."""
        if self.price is None:
            return None
        return round(self.price + (self.shipping_cost or 0.0), 2)

    @property
    def is_auction(self):
        return "AUCTION" in self.buying_options

    @property
    def is_fixed_price(self):
        return "FIXED_PRICE" in self.buying_options

    @property
    def accepts_offers(self):
        return "BEST_OFFER" in self.buying_options

    @property
    def title_length(self):
        return len(self.title or "")

    def age_days(self, now=None):
        if not self.created:
            return None
        now = now or datetime.now(timezone.utc)
        return max((now - self.created).total_seconds() / 86400.0, 0.0)

    # -- construction ------------------------------------------------------

    @classmethod
    def from_summary(cls, summary, marketplace=""):
        if not isinstance(summary, dict):
            raise TypeError("item summary must be a dict")

        price, currency = _money(summary.get("price"))
        if price is None:
            # Auctions in progress report the live bid instead of a fixed price.
            price, currency = _money(summary.get("currentBidPrice"))

        shipping_cost, free_shipping = _shipping(summary)
        seller = summary.get("seller") or {}
        categories = tuple(
            (str(c.get("categoryId") or ""), str(c.get("categoryName") or ""))
            for c in (summary.get("categories") or [])
            if isinstance(c, dict)
        )
        location = summary.get("itemLocation") or {}

        availability = summary.get("estimatedAvailabilities") or []
        available = sold = None
        if isinstance(availability, list) and availability:
            first = availability[0] if isinstance(availability[0], dict) else {}
            available = _int(first.get("estimatedAvailableQuantity"))
            sold = _int(first.get("estimatedSoldQuantity"))

        feedback_pct = seller.get("feedbackPercentage")
        try:
            feedback_pct = float(feedback_pct) if feedback_pct is not None else None
        except (TypeError, ValueError):
            feedback_pct = None

        return cls(
            item_id=str(summary.get("itemId") or ""),
            legacy_id=str(summary.get("legacyItemId") or ""),
            title=(summary.get("title") or "").strip(),
            subtitle=(summary.get("subtitle") or "").strip(),
            price=price,
            currency=currency or "",
            shipping_cost=shipping_cost,
            free_shipping=free_shipping,
            condition=(summary.get("condition") or "").strip(),
            condition_id=str(summary.get("conditionId") or ""),
            buying_options=tuple(summary.get("buyingOptions") or ()),
            bid_count=_int(summary.get("bidCount")),
            seller=str(seller.get("username") or ""),
            seller_feedback_pct=feedback_pct,
            seller_feedback_score=_int(seller.get("feedbackScore")),
            categories=categories,
            category_id=categories[0][0] if categories else "",
            category_name=categories[0][1] if categories else "",
            country=str(location.get("country") or ""),
            created=_parse_date(summary.get("itemCreationDate")),
            ends=_parse_date(summary.get("itemEndDate")),
            image_url=((summary.get("image") or {}).get("imageUrl") or ""),
            url=str(summary.get("itemWebUrl") or ""),
            top_rated=bool(summary.get("topRatedBuyingExperience")),
            promoted=bool(summary.get("priorityListing")),
            available_quantity=available,
            sold_quantity=sold,
            marketplace=marketplace,
        )

    def to_row(self):
        """Flat dict suitable for CSV export or a dataframe."""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "price": self.price,
            "shipping": self.shipping_cost,
            "total_cost": self.total_cost,
            "currency": self.currency,
            "format": "Auction" if self.is_auction else "Fixed price",
            "best_offer": self.accepts_offers,
            "bids": self.bid_count,
            "condition": self.condition,
            "seller": self.seller,
            "seller_feedback_pct": self.seller_feedback_pct,
            "seller_feedback_score": self.seller_feedback_score,
            "category": self.category_name,
            "category_id": self.category_id,
            "country": self.country,
            "listed": self.created.isoformat() if self.created else "",
            "ends": self.ends.isoformat() if self.ends else "",
            "sold_estimate": self.sold_quantity,
            "available": self.available_quantity,
            "promoted": self.promoted,
            "title_length": self.title_length,
            "url": self.url,
        }


@dataclass
class SoldRecord:
    """A completed sale from the Marketplace Insights API (last 90 days)."""

    item_id: str = ""
    title: str = ""
    price: float | None = None
    currency: str = ""
    sold_date: datetime | None = None
    quantity: int = 1
    condition: str = ""
    seller: str = ""
    category_id: str = ""
    category_name: str = ""
    url: str = ""

    @classmethod
    def from_sale(cls, sale, marketplace=""):
        price, currency = _money(sale.get("lastSoldPrice"))
        seller = sale.get("seller") or {}
        categories = [c for c in (sale.get("categories") or []) if isinstance(c, dict)]
        first = categories[0] if categories else {}
        quantity = _int(sale.get("totalSoldQuantity")) or 1
        return cls(
            item_id=str(sale.get("itemId") or ""),
            title=(sale.get("title") or "").strip(),
            price=price,
            currency=currency or "",
            sold_date=_parse_date(sale.get("lastSoldDate")),
            quantity=quantity,
            condition=(sale.get("condition") or "").strip(),
            seller=str(seller.get("username") or ""),
            category_id=str(first.get("categoryId") or ""),
            category_name=str(first.get("categoryName") or ""),
            url=str(sale.get("itemWebUrl") or ""),
        )

    def to_row(self):
        return {
            "item_id": self.item_id,
            "title": self.title,
            "price": self.price,
            "currency": self.currency,
            "quantity": self.quantity,
            "sold_date": self.sold_date.isoformat() if self.sold_date else "",
            "condition": self.condition,
            "seller": self.seller,
            "category": self.category_name,
            "url": self.url,
        }


@dataclass
class SellerIdentity:
    """Who a seller is, aggregated from the listings we sampled."""

    username: str = ""
    feedback_score: int | None = None
    feedback_pct: float | None = None
    countries: tuple = ()
    top_rated_share: float = 0.0

    def as_dict(self):
        return asdict(self)


@dataclass
class Corpus:
    """A sampled set of listings plus the query that produced it."""

    listings: list = field(default_factory=list)
    sold: list = field(default_factory=list)
    query: str = ""
    seller: str = ""
    marketplace: str = ""
    total_matches: int = 0
    truncated: bool = False
    warnings: list = field(default_factory=list)

    def __len__(self):
        return len(self.listings)

    @property
    def titles(self):
        return [item.title for item in self.listings if item.title]
