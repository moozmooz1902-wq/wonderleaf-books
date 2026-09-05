"""Configuration for the eBay research tools.

Settings come from (in priority order):

1. Explicit arguments passed to :func:`load_settings`.
2. Environment variables.
3. Streamlit secrets, when running inside Streamlit.

Nothing here ever hard-codes a credential.  Set these before use::

    EBAY_CLIENT_ID       = "YourApp-PRD-..."      # "App ID (Client ID)"
    EBAY_CLIENT_SECRET   = "PRD-..."             # "Cert ID (Client Secret)"

Optional::

    EBAY_ENV             = "production" | "sandbox"     (default production)
    EBAY_MARKETPLACE     = "EBAY_GB"                    (default EBAY_GB)
    EBAY_PROXY_URL       = "http://user:pass@host:port"  egress proxy
    EBAY_PROXY_URLS      = "http://a:8080,http://b:8080"  ordered failover list
    EBAY_CACHE_PATH      = "~/.wonderleaf/ebay_cache.sqlite3"
    EBAY_CACHE_TTL       = "900"                        seconds
    EBAY_RATE_LIMIT_RPS  = "4.0"                        requests/second ceiling
    EBAY_MAX_RETRIES     = "4"
    EBAY_TIMEOUT         = "30"                         seconds

Extra application keysets (each has its own daily allowance -- see
``credentials.py`` for why this, and not IP rotation, is what raises capacity)::

    EBAY_CLIENT_ID_2 / EBAY_CLIENT_SECRET_2 ... _9
    EBAY_CREDENTIALS  = '[{"label": "user-a", "client_id": "...",
                           "client_secret": "..."}]'

Daily allowances, if eBay has raised yours above the defaults::

    EBAY_DAILY_LIMIT_BROWSE   = "5000"
    EBAY_DAILY_LIMIT_INSIGHTS = "5000"

Get credentials by registering a free application at
https://developer.ebay.com/my/keys -- the Browse API is available to every
registered application.  Marketplace Insights (90 days of *sold* data) is a
limited-release API you must apply for; the tools degrade gracefully without it.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .errors import ConfigError

# Marketplaces the Browse API serves, mapped to their default currency.  Used
# for display only -- every response also carries its own currency code.
MARKETPLACES = {
    "EBAY_GB": ("United Kingdom", "GBP"),
    "EBAY_US": ("United States", "USD"),
    "EBAY_DE": ("Germany", "EUR"),
    "EBAY_AU": ("Australia", "AUD"),
    "EBAY_CA": ("Canada", "CAD"),
    "EBAY_FR": ("France", "EUR"),
    "EBAY_IT": ("Italy", "EUR"),
    "EBAY_ES": ("Spain", "EUR"),
    "EBAY_IE": ("Ireland", "EUR"),
    "EBAY_NL": ("Netherlands", "EUR"),
    "EBAY_PL": ("Poland", "PLN"),
    "EBAY_AT": ("Austria", "EUR"),
    "EBAY_CH": ("Switzerland", "CHF"),
    "EBAY_BE": ("Belgium", "EUR"),
    "EBAY_HK": ("Hong Kong", "HKD"),
    "EBAY_SG": ("Singapore", "SGD"),
    "EBAY_MY": ("Malaysia", "MYR"),
    "EBAY_PH": ("Philippines", "PHP"),
    "EBAY_TW": ("Taiwan", "TWD"),
}

_HOSTS = {
    "production": "https://api.ebay.com",
    "sandbox": "https://api.sandbox.ebay.com",
}

# The Browse API refuses offsets past this point; every paging loop is capped
# here so we fail loudly in tests rather than silently at runtime.
MAX_RESULT_WINDOW = 10_000
MAX_PAGE_SIZE = 200


def _from_streamlit(key):
    """Read a Streamlit secret, returning None outside Streamlit."""
    try:
        import streamlit as st  # imported lazily: the package works without it
    except Exception:
        return None
    try:
        value = st.secrets.get(key)
    except Exception:
        return None
    return value or None


def _setting(key, default=None):
    value = os.environ.get(key)
    if value not in (None, ""):
        return value
    value = _from_streamlit(key)
    if value not in (None, ""):
        return value
    return default


def _float(key, default):
    raw = _setting(key)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        raise ConfigError(f"{key} must be a number, got {raw!r}")


def _int(key, default):
    return int(_float(key, default))


@dataclass
class Settings:
    """Resolved configuration for a client session."""

    client_id: str = ""
    client_secret: str = ""
    environment: str = "production"
    marketplace: str = "EBAY_GB"
    proxy_url: str = ""
    proxy_urls: tuple = ()
    cache_path: str = ""
    cache_ttl: int = 900
    rate_limit_rps: float = 4.0
    max_retries: int = 4
    timeout: float = 30.0
    user_agent: str = "WonderleafResearch/1.0 (+https://github.com/wonderleaf-books)"
    scopes: tuple = field(default=("https://api.ebay.com/oauth/api_scope",))
    quota_limits: dict = field(default_factory=dict)

    @property
    def host(self):
        try:
            return _HOSTS[self.environment]
        except KeyError:
            raise ConfigError(
                f"EBAY_ENV must be one of {sorted(_HOSTS)}, got {self.environment!r}"
            )

    @property
    def currency(self):
        return MARKETPLACES.get(self.marketplace, ("", "GBP"))[1]

    @property
    def country(self):
        return MARKETPLACES.get(self.marketplace, ("Unknown", ""))[0]

    @property
    def proxies(self):
        """Egress routes for requests.

        Returns ``None`` for direct connection, a single mapping for one proxy,
        or an ordered list of mappings used as failover when several are
        configured (a dead egress must not take the tool down).
        """
        routes = [url for url in (self.proxy_url, *self.proxy_urls) if url]
        if not routes:
            return None
        mappings = [{"http": url, "https": url} for url in routes]
        return mappings[0] if len(mappings) == 1 else mappings

    @property
    def is_configured(self):
        return bool(self.client_id and self.client_secret)

    def require_credentials(self):
        if not self.is_configured:
            raise ConfigError(
                "eBay API credentials are missing. Set EBAY_CLIENT_ID and "
                "EBAY_CLIENT_SECRET (developer.ebay.com/my/keys) as environment "
                "variables or Streamlit secrets."
            )


def default_cache_path():
    override = _setting("EBAY_CACHE_PATH")
    if override:
        return os.path.expanduser(override)
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(
        os.path.expanduser("~"), ".cache"
    )
    return os.path.join(base, "wonderleaf", "ebay_cache.sqlite3")


def load_settings(**overrides):
    """Build a :class:`Settings` from env/secrets, applying keyword overrides."""
    settings = Settings(
        client_id=_setting("EBAY_CLIENT_ID", "") or "",
        client_secret=_setting("EBAY_CLIENT_SECRET", "") or "",
        environment=(_setting("EBAY_ENV", "production") or "production").lower(),
        marketplace=(_setting("EBAY_MARKETPLACE", "EBAY_GB") or "EBAY_GB").upper(),
        proxy_url=_setting("EBAY_PROXY_URL", "") or "",
        proxy_urls=tuple(
            url.strip()
            for url in (_setting("EBAY_PROXY_URLS", "") or "").split(",")
            if url.strip()
        ),
        cache_path=default_cache_path(),
        cache_ttl=_int("EBAY_CACHE_TTL", 900),
        rate_limit_rps=_float("EBAY_RATE_LIMIT_RPS", 4.0),
        max_retries=_int("EBAY_MAX_RETRIES", 4),
        timeout=_float("EBAY_TIMEOUT", 30.0),
        quota_limits={
            "browse": _int("EBAY_DAILY_LIMIT_BROWSE", 5000),
            "insights": _int("EBAY_DAILY_LIMIT_INSIGHTS", 5000),
        },
    )
    for key, value in overrides.items():
        if value is None:
            continue
        if not hasattr(settings, key):
            raise ConfigError(f"Unknown setting {key!r}")
        setattr(settings, key, value)
    if settings.marketplace not in MARKETPLACES:
        raise ConfigError(
            f"Unsupported marketplace {settings.marketplace!r}. "
            f"Choose one of: {', '.join(sorted(MARKETPLACES))}"
        )
    return settings
