"""Application keysets and how the tool chooses between them.

Why a pool exists
-----------------
eBay counts its daily call allowance against an **application keyset**.  That
is the ceiling a busy platform hits -- not an IP ban -- and the supported way
to raise it is more allowance, not more network addresses.  Two legitimate
routes give a platform more allowance, and this pool serves both:

1. **Bring-your-own keys.**  Each user of the platform registers their own free
   eBay developer application and pastes their keys in.  Capacity then scales
   with the user base, every user's usage is counted against their own app, and
   nobody is borrowing anyone else's budget.  This is the primary design.
2. **Multiple first-party applications** the operator legitimately holds (for
   example a separate keyset per marketplace or per product line).

When a keyset is throttled or spent for the day, the pool fails over to the
next one mid-run rather than aborting the report.

Configuration::

    EBAY_CLIENT_ID / EBAY_CLIENT_SECRET            the primary keyset
    EBAY_CLIENT_ID_2 / EBAY_CLIENT_SECRET_2        additional keysets, 2..9
    EBAY_CREDENTIALS = '[{"label": "...", "client_id": "...",
                          "client_secret": "..."}, ...]'
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass

from .config import _setting
from .errors import ConfigError


@dataclass
class Credential:
    """One eBay application keyset."""

    client_id: str
    client_secret: str
    label: str = ""
    owner: str = ""  # which user supplied it, for bring-your-own-keys

    @property
    def id(self):
        """Stable, non-reversible identifier — safe to log and to store."""
        digest = hashlib.sha256(self.client_id.encode("utf-8")).hexdigest()
        return digest[:16]

    @property
    def display(self):
        if self.label:
            return self.label
        # Never render a full key; the tail is enough to tell keysets apart.
        return f"…{self.client_id[-6:]}" if len(self.client_id) > 6 else "key"

    def __post_init__(self):
        if not self.client_id or not self.client_secret:
            raise ConfigError("A credential needs both a client_id and a client_secret.")


@dataclass
class _State:
    """Runtime health of one keyset."""

    throttled_until: float = 0.0
    exhausted_day: str = ""
    consecutive_failures: int = 0
    calls: int = 0


class CredentialPool:
    """Chooses a keyset per request and fails over when one runs dry."""

    def __init__(self, credentials, ledger=None, clock=time.time):
        self.credentials = list(credentials or [])
        if not self.credentials:
            raise ConfigError(
                "No eBay credentials configured. Set EBAY_CLIENT_ID and "
                "EBAY_CLIENT_SECRET, or let each user supply their own keys."
            )
        self.ledger = ledger
        self._clock = clock
        self._state = {c.id: _State() for c in self.credentials}
        self._cursor = 0
        self._lock = threading.Lock()

    def __len__(self):
        return len(self.credentials)

    @property
    def ids(self):
        return [c.id for c in self.credentials]

    # -- selection ---------------------------------------------------------

    def _usable(self, credential, resource, now, cost):
        state = self._state[credential.id]
        if state.throttled_until > now:
            return False
        if self.ledger and not self.ledger.can_spend(credential.id, resource, cost):
            return False
        return True

    def acquire(self, resource="browse", cost=1):
        """Pick the healthiest keyset with budget left.

        Round-robin among usable keysets so load spreads evenly, preferring
        whichever has the most remaining allowance.
        """
        now = self._clock()
        with self._lock:
            usable = [c for c in self.credentials if self._usable(c, resource, now, cost)]
            if not usable:
                return None
            if self.ledger:
                usable.sort(
                    key=lambda c: self.ledger.remaining(c.id, resource), reverse=True
                )
                best = usable[0]
                top = [
                    c
                    for c in usable
                    if self.ledger.remaining(c.id, resource)
                    == self.ledger.remaining(best.id, resource)
                ]
            else:
                top = usable
            chosen = top[self._cursor % len(top)]
            self._cursor += 1
            self._state[chosen.id].calls += 1
            return chosen

    def require(self, resource="browse", cost=1):
        """Like :meth:`acquire` but explains itself when nothing is available."""
        credential = self.acquire(resource, cost)
        if credential:
            return credential
        raise self.exhausted_error(resource)

    def exhausted_error(self, resource="browse"):
        from .errors import RateLimitError
        from .quota import seconds_until_reset

        minutes = int(seconds_until_reset() // 60)
        detail = ""
        if self.ledger:
            spent = sum(self.ledger.used(c.id, resource) for c in self.credentials)
            detail = f" {spent:,} calls used across {len(self)} keyset(s)."
        return RateLimitError(
            f"Daily eBay {resource} allowance is spent.{detail} It resets in "
            f"{minutes // 60}h {minutes % 60}m. Add another application keyset, "
            "narrow the search, or rely on cached results until then. Note that "
            "the allowance is counted per application key, so extra IP addresses "
            "would not raise it.",
            retry_after=seconds_until_reset(),
        )

    # -- feedback ----------------------------------------------------------

    def mark_success(self, credential, resource="browse"):
        state = self._state[credential.id]
        state.consecutive_failures = 0
        if self.ledger:
            self.ledger.record(credential.id, resource)

    def mark_throttled(self, credential, resource="browse", retry_after=None):
        """Park a keyset briefly after a 429 so the next request uses another."""
        try:
            pause = float(retry_after) if retry_after else 60.0
        except (TypeError, ValueError):
            pause = 60.0
        state = self._state[credential.id]
        state.throttled_until = self._clock() + min(max(pause, 5.0), 900.0)
        state.consecutive_failures += 1
        if self.ledger:
            self.ledger.note(credential.id, resource, "throttled")

    def mark_exhausted(self, credential, resource="browse"):
        """Burn the rest of today's budget for a keyset that eBay says is done."""
        from .quota import utc_day

        state = self._state[credential.id]
        state.exhausted_day = utc_day()
        if self.ledger:
            remaining = self.ledger.remaining(credential.id, resource)
            if remaining:
                self.ledger.record(credential.id, resource, remaining)
            self.ledger.note(credential.id, resource, "exhausted")

    def status(self, resource="browse"):
        """Per-keyset health for the UI."""
        now = self._clock()
        rows = []
        for credential in self.credentials:
            state = self._state[credential.id]
            rows.append(
                {
                    "keyset": credential.display,
                    "owner": credential.owner or "platform",
                    "calls_this_session": state.calls,
                    "remaining_today": self.ledger.remaining(credential.id, resource)
                    if self.ledger
                    else None,
                    "status": "throttled"
                    if state.throttled_until > now
                    else ("ready" if self._usable(credential, resource, now, 1) else "spent"),
                }
            )
        return rows


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_credentials(extra=None):
    """Collect every configured keyset, primary first.

    ``extra`` lets a caller inject per-user keys (bring-your-own-keys) on top
    of whatever the platform has configured.
    """
    found = []
    seen = set()

    def add(client_id, client_secret, label="", owner=""):
        client_id = (client_id or "").strip()
        client_secret = (client_secret or "").strip()
        if not client_id or not client_secret or client_id in seen:
            return
        seen.add(client_id)
        found.append(
            Credential(
                client_id=client_id,
                client_secret=client_secret,
                label=label,
                owner=owner,
            )
        )

    for credential in extra or []:
        if isinstance(credential, Credential):
            if credential.client_id not in seen:
                seen.add(credential.client_id)
                found.append(credential)
        elif isinstance(credential, dict):
            add(
                credential.get("client_id"),
                credential.get("client_secret"),
                credential.get("label", ""),
                credential.get("owner", ""),
            )

    add(_setting("EBAY_CLIENT_ID"), _setting("EBAY_CLIENT_SECRET"), "primary")

    for index in range(2, 10):
        add(
            _setting(f"EBAY_CLIENT_ID_{index}"),
            _setting(f"EBAY_CLIENT_SECRET_{index}"),
            f"keyset {index}",
        )

    blob = _setting("EBAY_CREDENTIALS")
    if blob:
        try:
            parsed = json.loads(blob)
        except (TypeError, ValueError):
            raise ConfigError("EBAY_CREDENTIALS must be a JSON list of keysets.")
        if not isinstance(parsed, list):
            raise ConfigError("EBAY_CREDENTIALS must be a JSON list of keysets.")
        for entry in parsed:
            if isinstance(entry, dict):
                add(
                    entry.get("client_id"),
                    entry.get("client_secret"),
                    entry.get("label", ""),
                    entry.get("owner", ""),
                )

    return found
