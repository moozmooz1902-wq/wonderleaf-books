"""Client for eBay's official REST APIs.

Covers the two APIs that matter for research:

* **Browse** (``/buy/browse/v1``) -- active listings.  Available to every
  registered application.  Supports filtering by seller, category, price,
  condition and buying format, which is what makes seller-wide sweeps
  possible without touching a single HTML page.
* **Marketplace Insights** (``/buy/marketplace_insights/v1_beta``) -- items
  *sold* in the last 90 days.  This is a limited-release API; if your
  application is not approved for it the client raises
  :class:`~ebay_research.errors.NotAvailableError` and callers fall back to
  active-listing analysis only.

Authentication is the client-credentials flow: an application token, no user
consent needed, refreshed automatically a minute before expiry.
"""

from __future__ import annotations

import base64
import threading
import time

from .cache import ResponseCache, make_key
from .config import MAX_PAGE_SIZE, MAX_RESULT_WINDOW, Settings, load_settings
from .credentials import Credential, CredentialPool, load_credentials
from .errors import ApiError, AuthError, NotAvailableError, RateLimitError
from .http import HttpClient
from .models import Listing, SoldRecord
from .quota import QuotaLedger, plan_sample, seconds_until_reset

BROWSE_PATH = "/buy/browse/v1/item_summary/search"
ITEM_PATH = "/buy/browse/v1/item/{item_id}"
INSIGHTS_PATH = "/buy/marketplace_insights/v1_beta/item_sales/search"
TOKEN_PATH = "/identity/v1/oauth2/token"

INSIGHTS_SCOPE = "https://api.ebay.com/oauth/api_scope/buy.marketplace.insights"

# Top-level eBay categories, used when sweeping a seller's whole catalogue.
# Browse requires a query or a category on every search, so a catalogue-wide
# sweep walks these one at a time.
TOP_LEVEL_CATEGORIES = {
    "20081": "Antiques",
    "550": "Art",
    "2984": "Baby",
    "267": "Books, Comics & Magazines",
    "12576": "Business & Industrial",
    "625": "Cameras & Photo",
    "15032": "Mobile Phones & Communication",
    "11450": "Clothes, Shoes & Accessories",
    "11116": "Coins & Paper Money",
    "1": "Collectables",
    "58058": "Computers/Tablets & Networking",
    "293": "Sound & Vision",
    "14339": "Crafts",
    "237": "Dolls & Bears",
    "11232": "DVDs, Films & TV",
    "45100": "Entertainment Memorabilia",
    "26395": "Health & Beauty",
    "11700": "Home, Furniture & DIY",
    "281": "Jewellery & Watches",
    "11233": "Music",
    "619": "Musical Instruments",
    "1281": "Pet Supplies",
    "870": "Pottery, Porcelain & Glass",
    "888": "Sporting Goods",
    "64482": "Sports Memorabilia",
    "260": "Stamps",
    "220": "Toys & Games",
    "1249": "Video Games & Consoles",
    "99": "Everything Else",
}


def build_filter(
    seller=None,
    price_min=None,
    price_max=None,
    currency=None,
    conditions=None,
    buying_options=None,
    country=None,
    free_shipping=None,
    returns_accepted=None,
    listed_after=None,
    sold_between=None,
):
    """Assemble eBay's comma-separated filter expression.

    eBay's filter grammar is positional and unforgiving; building it in one
    place keeps every caller honest.
    """
    parts = []
    if seller:
        sellers = seller if isinstance(seller, (list, tuple, set)) else [seller]
        cleaned = [str(s).strip() for s in sellers if str(s).strip()]
        if cleaned:
            parts.append("sellers:{%s}" % "|".join(cleaned))
    if price_min is not None or price_max is not None:
        low = "" if price_min is None else f"{float(price_min):g}"
        high = "" if price_max is None else f"{float(price_max):g}"
        parts.append(f"price:[{low}..{high}]")
        # eBay rejects a price filter that does not declare its currency.
        parts.append(f"priceCurrency:{currency or 'GBP'}")
    if conditions:
        parts.append("conditions:{%s}" % "|".join(conditions))
    if buying_options:
        parts.append("buyingOptions:{%s}" % "|".join(buying_options))
    if country:
        parts.append(f"itemLocationCountry:{country}")
    if free_shipping:
        parts.append("maxDeliveryCost:0")
    if returns_accepted is not None:
        parts.append("returnsAccepted:%s" % ("true" if returns_accepted else "false"))
    if listed_after:
        parts.append(f"itemStartDate:[{listed_after}]")
    if sold_between:
        start, end = sold_between
        parts.append(f"lastSoldDate:[{start}..{end}]")
    return ",".join(parts)


_QUOTA_MARKERS = (
    "call limit",
    "exceeded",
    "quota",
    "rate limit",
    "application access",
)


def _is_quota_error(exc):
    """Does this 403 mean 'out of allowance' rather than 'not permitted'?"""
    text = str(exc).lower()
    payload = getattr(exc, "payload", None)
    if isinstance(payload, dict):
        for error in payload.get("errors") or []:
            if isinstance(error, dict):
                text += " " + str(error.get("message", "")).lower()
                text += " " + str(error.get("longMessage", "")).lower()
    return any(marker in text for marker in _QUOTA_MARKERS)


class EbayClient:
    """Authenticated, rate-limited, cached access to the eBay REST APIs."""

    def __init__(
        self,
        settings=None,
        http=None,
        cache=None,
        clock=time.time,
        pool=None,
        ledger=None,
        extra_credentials=None,
    ):
        self.settings = settings or load_settings()
        if not isinstance(self.settings, Settings):
            raise TypeError("settings must be a Settings instance")
        self.http = http or HttpClient(
            rate_limit_rps=self.settings.rate_limit_rps,
            max_retries=self.settings.max_retries,
            timeout=self.settings.timeout,
            proxies=self.settings.proxies,
            user_agent=self.settings.user_agent,
        )
        self.cache = cache if cache is not None else ResponseCache(
            self.settings.cache_path, ttl=self.settings.cache_ttl
        )
        self.ledger = ledger if ledger is not None else QuotaLedger(
            self.settings.cache_path, limits=self.settings.quota_limits
        )
        if pool is None:
            credentials = load_credentials(extra=extra_credentials)
            if not credentials and self.settings.is_configured:
                credentials = [
                    Credential(
                        client_id=self.settings.client_id,
                        client_secret=self.settings.client_secret,
                        label="primary",
                    )
                ]
            pool = CredentialPool(credentials, ledger=self.ledger) if credentials else None
        self.pool = pool
        self._clock = clock
        self._tokens = {}  # credential id -> (token, expiry, scopes)
        self._token_lock = threading.Lock()
        self.insights_available = None  # None = untested, True/False once probed
        self.notices = []  # budget/degradation messages for the current run

    # -- budget ------------------------------------------------------------

    def reset_notices(self):
        self.notices = []

    def _note(self, message):
        if message not in self.notices:
            self.notices.append(message)

    def budget(self, resource="browse"):
        """Calls left today across every configured keyset."""
        if not self.pool or not self.ledger:
            return None
        return sum(
            self.ledger.remaining(credential.id, resource)
            for credential in self.pool.credentials
        )

    def plan(self, desired_items, resource="browse", page_size=MAX_PAGE_SIZE):
        """Trim a sample to what today's remaining allowance can pay for."""
        available = self.budget(resource)
        if available is None:
            return int(desired_items), False
        items, _calls, degraded = plan_sample(
            desired_items, available, page_size=page_size
        )
        if degraded:
            hours = int(seconds_until_reset() // 3600)
            if items:
                self._note(
                    f"Sample reduced to {items} listings: {available} API calls left "
                    f"in today's allowance (resets in ~{hours}h). Add another "
                    "application keyset to raise it — the allowance is per keyset, "
                    "not per IP address."
                )
            else:
                self._note(
                    "Today's API allowance is spent, so only cached results are "
                    f"available (resets in ~{hours}h)."
                )
        return items, degraded

    # -- auth --------------------------------------------------------------

    def _fetch_token(self, credential, scopes):
        raw = f"{credential.client_id}:{credential.client_secret}".encode("utf-8")
        headers = {
            "Authorization": "Basic " + base64.b64encode(raw).decode("ascii"),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        body = {"grant_type": "client_credentials", "scope": " ".join(scopes)}
        try:
            payload = self.http.post_json(
                self.settings.host + TOKEN_PATH, headers=headers, data=body
            )
        except ApiError as exc:
            raise AuthError(
                f"Could not get an eBay application token for keyset "
                f"{credential.display}. Check the client id/secret and that they "
                f"match EBAY_ENV={self.settings.environment}. ({exc})"
            ) from exc
        token = payload.get("access_token")
        if not token:
            raise AuthError(f"eBay token response contained no access_token: {payload}")
        expires_in = float(payload.get("expires_in") or 7200)
        return token, self._clock() + expires_in - 60.0

    def _credential(self, resource="browse"):
        if not self.pool:
            self.settings.require_credentials()
            raise AuthError("No credential pool configured.")
        return self.pool.require(resource)

    def token(self, scopes=None, credential=None):
        """A valid application token for a keyset, refreshed near expiry."""
        wanted = tuple(scopes or self.settings.scopes)
        credential = credential or self._credential()
        with self._token_lock:
            cached = self._tokens.get(credential.id)
            if cached:
                token, expiry, held = cached
                if self._clock() < expiry and set(wanted).issubset(held):
                    return token
            token, expiry = self._fetch_token(credential, wanted)
            self._tokens[credential.id] = (token, expiry, wanted)
            return token

    def _headers(self, credential, scopes=None, extra=None):
        headers = {
            "Authorization": f"Bearer {self.token(scopes, credential=credential)}",
            "X-EBAY-C-MARKETPLACE-ID": self.settings.marketplace,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    # -- low-level ---------------------------------------------------------

    def _get(self, path, params, scopes=None, cache_ttl=None, resource="browse"):
        """Cached, budgeted GET that fails over between keysets.

        A cache hit costs no allowance at all, which is why the cache is the
        first thing consulted and why it is shared: on a multi-user platform
        one fetch of a popular search serves everybody inside the TTL.
        """
        key = make_key(
            "GET", path, params, self.settings.marketplace, self.settings.environment
        )
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        if not self.pool:
            self.settings.require_credentials()

        attempted = set()
        last_error = None
        for _ in range(len(self.pool)):
            credential = self.pool.acquire(resource)
            if credential is None:
                raise self.pool.exhausted_error(resource)
            if credential.id in attempted:
                break
            attempted.add(credential.id)

            def on_throttle(retry_after, credential=credential):
                """Hand over to another keyset rather than sitting in backoff."""
                self.pool.mark_throttled(credential, resource, retry_after)
                return self.pool.acquire(resource) is not None

            try:
                payload = self.http.get_json(
                    self.settings.host + path,
                    headers=self._headers(credential, scopes),
                    params=params,
                    on_throttle=on_throttle,
                )
            except RateLimitError as exc:
                last_error = exc
                self._note(
                    f"Keyset {credential.display} was throttled; switching to "
                    "another keyset."
                )
                continue
            except ApiError as exc:
                if getattr(exc, "status", None) == 403 and _is_quota_error(exc):
                    self.pool.mark_exhausted(credential, resource)
                    last_error = exc
                    self._note(
                        f"Keyset {credential.display} has spent its daily "
                        "allowance; switching to another keyset."
                    )
                    continue
                raise

            if self.pool:
                self.pool.mark_success(credential, resource)
            self.cache.set(key, payload, ttl=cache_ttl)
            return payload

        if isinstance(last_error, RateLimitError):
            raise self.pool.exhausted_error(resource)
        raise last_error or ApiError(f"Request to {path} failed.")

    # -- Browse ------------------------------------------------------------

    def search_page(
        self,
        query=None,
        category_ids=None,
        filters=None,
        sort=None,
        limit=MAX_PAGE_SIZE,
        offset=0,
        fieldgroups="EXTENDED,MATCHING_ITEMS",
    ):
        """One page of ``item_summary/search``.  Returns the raw payload."""
        if not query and not category_ids:
            raise ValueError(
                "eBay's Browse API needs a keyword or a category on every search. "
                "Pass query=, category_ids=, or use sweep_seller() which walks "
                "categories for you."
            )
        params = {
            "limit": max(1, min(int(limit), MAX_PAGE_SIZE)),
            "offset": max(0, int(offset)),
        }
        if query:
            params["q"] = query
        if category_ids:
            ids = category_ids
            if isinstance(ids, (list, tuple, set)):
                ids = ",".join(str(c) for c in ids)
            params["category_ids"] = str(ids)
        if filters:
            params["filter"] = filters
        if sort:
            params["sort"] = sort
        if fieldgroups:
            params["fieldgroups"] = fieldgroups
        return self._get(BROWSE_PATH, params)

    def search(
        self,
        query=None,
        category_ids=None,
        filters=None,
        sort=None,
        max_items=200,
        page_size=MAX_PAGE_SIZE,
        progress=None,
        budget_aware=True,
    ):
        """Page through search results.

        Returns ``(listings, total_matches, truncated)`` where ``total_matches``
        is eBay's own count of everything matching -- often far larger than the
        sample we pull.
        """
        collected = []
        total = 0
        offset = 0
        page_size = max(1, min(int(page_size), MAX_PAGE_SIZE))
        max_items = max(0, int(max_items))
        if budget_aware:
            max_items, _degraded = self.plan(max_items, page_size=page_size)

        while len(collected) < max_items and offset < MAX_RESULT_WINDOW:
            want = min(page_size, max_items - len(collected))
            payload = self.search_page(
                query=query,
                category_ids=category_ids,
                filters=filters,
                sort=sort,
                limit=want,
                offset=offset,
            )
            total = int(payload.get("total") or total)
            summaries = payload.get("itemSummaries") or []
            for summary in summaries:
                try:
                    collected.append(
                        Listing.from_summary(summary, self.settings.marketplace)
                    )
                except (TypeError, ValueError):
                    continue
            if progress:
                progress(len(collected), min(total, max_items))
            if len(summaries) < want:
                break  # exhausted the result set
            offset += len(summaries)

        truncated = total > len(collected)
        return collected, total, truncated

    def sweep_seller(
        self,
        seller,
        query=None,
        category_ids=None,
        extra_filters=None,
        max_items=600,
        progress=None,
    ):
        """Pull as much of a seller's live catalogue as the API will give us.

        With a ``query`` or explicit ``category_ids`` this is a single paged
        search.  Without either, it walks the top-level categories, probing
        each with one small call and only paging the ones that come back
        non-empty -- so an unknown seller costs ~30 probe calls instead of
        thousands of blind pages.
        """
        base_filter = build_filter(seller=seller)
        if extra_filters:
            base_filter = ",".join(p for p in (base_filter, extra_filters) if p)

        # A blind sweep spends one probe call per top-level category before it
        # pages anything, so reserve that up front rather than running dry
        # halfway through the catalogue.
        if not query and not category_ids:
            available = self.budget()
            if available is not None:
                probes = len(TOP_LEVEL_CATEGORIES)
                if available <= probes:
                    self._note(
                        "Not enough daily allowance left for a full catalogue "
                        "sweep. Add a keyword to narrow it, or try again after "
                        "the reset."
                    )
                max_items = min(
                    max_items, max(available - probes, 0) * MAX_PAGE_SIZE
                )

        if query or category_ids:
            listings, total, truncated = self.search(
                query=query,
                category_ids=category_ids,
                filters=base_filter,
                max_items=max_items,
                progress=progress,
            )
            return listings, total, truncated, {}

        listings = []
        per_category = {}
        grand_total = 0
        truncated = False

        for category_id, name in TOP_LEVEL_CATEGORIES.items():
            if len(listings) >= max_items:
                truncated = True
                break
            probe = self.search_page(
                category_ids=category_id, filters=base_filter, limit=1, offset=0
            )
            found = int(probe.get("total") or 0)
            if not found:
                continue
            grand_total += found
            per_category[name] = found
            batch, _, batch_truncated = self.search(
                category_ids=category_id,
                filters=base_filter,
                max_items=min(max_items - len(listings), found),
                progress=None,
            )
            listings.extend(batch)
            truncated = truncated or batch_truncated
            if progress:
                progress(len(listings), max_items)

        return listings, grand_total, truncated or grand_total > len(listings), per_category

    def get_item(self, item_id):
        """Full item detail -- item specifics, description, return policy."""
        return self._get(ITEM_PATH.format(item_id=item_id), {})

    # -- Marketplace Insights ---------------------------------------------

    def search_sold(
        self,
        query=None,
        category_ids=None,
        filters=None,
        max_items=200,
        days=90,
        page_size=MAX_PAGE_SIZE,
    ):
        """Completed sales from the last ``days`` days (max 90).

        Raises :class:`NotAvailableError` when the application is not approved
        for Marketplace Insights, so callers can degrade to active-only stats.
        """
        from datetime import datetime, timedelta, timezone

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=max(1, min(int(days), 90)))
        window = build_filter(
            sold_between=(
                start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            )
        )
        combined = ",".join(p for p in (filters, window) if p)

        collected = []
        offset = 0
        total = 0
        page_size = max(1, min(int(page_size), MAX_PAGE_SIZE))
        max_items = max(0, int(max_items))

        while len(collected) < max_items and offset < MAX_RESULT_WINDOW:
            want = min(page_size, max_items - len(collected))
            params = {"limit": want, "offset": offset, "filter": combined}
            if query:
                params["q"] = query
            if category_ids:
                ids = category_ids
                if isinstance(ids, (list, tuple, set)):
                    ids = ",".join(str(c) for c in ids)
                params["category_ids"] = str(ids)
            try:
                payload = self._get(
                    INSIGHTS_PATH, params, scopes=(INSIGHTS_SCOPE,), resource="insights"
                )
            except (ApiError, AuthError) as exc:
                status = getattr(exc, "status", None)
                if status in (401, 403) or isinstance(exc, AuthError):
                    self.insights_available = False
                    raise NotAvailableError(
                        "Marketplace Insights (sold-item data) is not enabled for "
                        "this eBay application. Apply for it at "
                        "developer.ebay.com; until then the tools analyse active "
                        "listings only."
                    ) from exc
                raise
            self.insights_available = True
            total = int(payload.get("total") or total)
            sales = payload.get("itemSales") or []
            for sale in sales:
                try:
                    collected.append(
                        SoldRecord.from_sale(sale, self.settings.marketplace)
                    )
                except (TypeError, ValueError):
                    continue
            if len(sales) < want:
                break
            offset += len(sales)

        return collected, total

    # -- diagnostics -------------------------------------------------------

    def health(self):
        """Cheap self-test used by the UI to explain what is and isn't working."""
        report = {
            "environment": self.settings.environment,
            "marketplace": self.settings.marketplace,
            "egress": self.http.egress_status(),
            "keysets": len(self.pool) if self.pool else 0,
            "credentials": bool(self.pool),
            "browse_calls_left_today": self.budget("browse"),
            "insights_calls_left_today": self.budget("insights"),
            "browse": False,
            "insights": False,
            "notes": [],
        }
        if not self.pool:
            report["notes"].append(
                "No API credentials configured. Set EBAY_CLIENT_ID and "
                "EBAY_CLIENT_SECRET, or add per-user keysets."
            )
            return report
        try:
            self.search_page(query="test", limit=1)
            report["browse"] = True
            report["keyset_status"] = self.pool.status("browse")
        except Exception as exc:  # surfaced to the user, never raised
            report["notes"].append(f"Browse API unavailable: {exc}")
            return report
        try:
            self.search_sold(query="test", max_items=1, page_size=1)
            report["insights"] = True
        except NotAvailableError as exc:
            report["notes"].append(str(exc))
        except Exception as exc:
            report["notes"].append(f"Insights probe failed: {exc}")
        report["calls"] = dict(self.http.stats)
        report["keyset_status"] = self.pool.status("browse")
        return report
