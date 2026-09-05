"""eBay research and analytics tools for the Wonderleaf platform.

Built on eBay's official Browse and Marketplace Insights APIs, so the data is
structured, complete and permitted to use -- and the client never has to hide
where it is coming from.  Quota is protected by pacing, caching and retries
rather than by disguising traffic.

Typical use::

    from ebay_research import EbayClient, load_settings, research_market

    client = EbayClient(load_settings(marketplace="EBAY_GB"))
    report = research_market(client, "childrens picture book personalised")
    for finding in report["findings"]:
        print("-", finding)
"""

from .analytics import (
    competition,
    describe,
    price_bands,
    seller_leaderboard,
    sell_through,
)
from .cache import ResponseCache, SnapshotStore
from .client import TOP_LEVEL_CATEGORIES, EbayClient, build_filter
from .config import MARKETPLACES, Settings, load_settings
from .credentials import Credential, CredentialPool, load_credentials
from .errors import (
    ApiError,
    AuthError,
    ConfigError,
    EbayResearchError,
    NotAvailableError,
    RateLimitError,
)
from .export import report_to_json, report_to_markdown, rows_to_csv, score_to_markdown
from .models import Corpus, Listing, SoldRecord
from .quota import QuotaLedger, calls_needed, plan_sample
from .research import compare_sellers, research_market, research_seller
from .scoring import audit_listings, compare_titles, score_title, suggest_title
from .titles import distinctive_terms, keyword_table, title_stats

__version__ = "1.0.0"

__all__ = [
    "ApiError",
    "AuthError",
    "ConfigError",
    "Corpus",
    "Credential",
    "CredentialPool",
    "EbayClient",
    "EbayResearchError",
    "Listing",
    "MARKETPLACES",
    "NotAvailableError",
    "QuotaLedger",
    "RateLimitError",
    "ResponseCache",
    "Settings",
    "SnapshotStore",
    "SoldRecord",
    "TOP_LEVEL_CATEGORIES",
    "audit_listings",
    "build_filter",
    "calls_needed",
    "compare_sellers",
    "compare_titles",
    "competition",
    "describe",
    "distinctive_terms",
    "keyword_table",
    "load_credentials",
    "load_settings",
    "plan_sample",
    "price_bands",
    "report_to_json",
    "report_to_markdown",
    "research_market",
    "research_seller",
    "rows_to_csv",
    "score_title",
    "score_to_markdown",
    "sell_through",
    "seller_leaderboard",
    "suggest_title",
    "title_stats",
    "__version__",
]
