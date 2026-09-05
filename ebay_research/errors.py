"""Exception hierarchy for the eBay research package."""


class EbayResearchError(Exception):
    """Base class for every error raised by this package."""


class ConfigError(EbayResearchError):
    """Credentials or settings are missing/invalid."""


class AuthError(EbayResearchError):
    """OAuth token could not be obtained or was rejected."""


class RateLimitError(EbayResearchError):
    """Call limit hit and retries were exhausted."""

    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class ApiError(EbayResearchError):
    """eBay returned an error payload."""

    def __init__(self, message, status=None, payload=None):
        super().__init__(message)
        self.status = status
        self.payload = payload


class NotAvailableError(EbayResearchError):
    """A restricted-access API (e.g. Marketplace Insights) is not granted to this app."""
