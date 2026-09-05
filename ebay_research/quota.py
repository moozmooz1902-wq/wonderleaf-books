"""Call-budget accounting.

The real constraint on an eBay research tool is not IP blocking -- it is the
daily call allowance, which eBay counts **per application keyset**, not per IP
address.  A pool of a thousand IPs sharing one keyset still stops at the same
call.  So the way to keep the tool usable for many users is to know the budget,
spend it deliberately, and never waste a call.

This module keeps a persistent per-key, per-day ledger so the tool can answer
"can I afford this sweep?" *before* starting it, degrade the sample size when
budget is tight, and hand over to another keyset when one is spent.

eBay's allowances reset at midnight UTC.
"""

from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

# Default daily allowances for a newly registered production application.
# eBay raises these on request once an app shows real usage, so they are
# configurable rather than baked in.
DEFAULT_LIMITS = {
    "browse": 5000,
    "insights": 5000,
    "auth": 1000,
}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS quota (
    credential_id TEXT NOT NULL,
    resource      TEXT NOT NULL,
    day           TEXT NOT NULL,
    calls         INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (credential_id, resource, day)
);
CREATE TABLE IF NOT EXISTS quota_events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    credential_id TEXT NOT NULL,
    resource      TEXT NOT NULL,
    kind          TEXT NOT NULL,
    at            REAL NOT NULL
);
"""


def utc_day(when=None):
    """The quota day a moment belongs to (eBay resets at 00:00 UTC)."""
    when = when or datetime.now(timezone.utc)
    return when.astimezone(timezone.utc).strftime("%Y-%m-%d")


def seconds_until_reset(when=None):
    when = when or datetime.now(timezone.utc)
    when = when.astimezone(timezone.utc)
    tomorrow = (when + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return max((tomorrow - when).total_seconds(), 0.0)


class QuotaLedger:
    """Durable daily call counter, shared by every process using this cache."""

    def __init__(self, path, limits=None, enabled=True):
        self.path = path
        self.limits = dict(DEFAULT_LIMITS)
        if limits:
            self.limits.update(limits)
        self.enabled = enabled and bool(path)
        self._lock = threading.Lock()
        self._memory = {}  # fallback when sqlite is unavailable

    # -- storage -----------------------------------------------------------

    def _connect(self):
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=15)
        conn.executescript(_SCHEMA)
        return conn

    def _memory_key(self, credential_id, resource, day):
        return (credential_id, resource, day)

    # -- public API --------------------------------------------------------

    def limit_for(self, resource):
        return int(self.limits.get(resource, DEFAULT_LIMITS.get(resource, 5000)))

    def record(self, credential_id, resource, calls=1, when=None):
        """Count calls against a keyset.  Returns the new daily total."""
        day = utc_day(when)
        key = self._memory_key(credential_id, resource, day)
        with self._lock:
            self._memory[key] = self._memory.get(key, 0) + calls
            memory_total = self._memory[key]
        if not self.enabled:
            return memory_total
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO quota (credential_id, resource, day, calls)"
                    " VALUES (?, ?, ?, ?)"
                    " ON CONFLICT(credential_id, resource, day)"
                    " DO UPDATE SET calls = calls + excluded.calls",
                    (credential_id, resource, day, calls),
                )
                row = conn.execute(
                    "SELECT calls FROM quota WHERE credential_id = ? AND resource = ?"
                    " AND day = ?",
                    (credential_id, resource, day),
                ).fetchone()
            return int(row[0]) if row else memory_total
        except (sqlite3.Error, OSError):
            return memory_total

    def used(self, credential_id, resource, when=None):
        day = utc_day(when)
        if self.enabled:
            try:
                with self._connect() as conn:
                    row = conn.execute(
                        "SELECT calls FROM quota WHERE credential_id = ?"
                        " AND resource = ? AND day = ?",
                        (credential_id, resource, day),
                    ).fetchone()
                if row:
                    return int(row[0])
            except (sqlite3.Error, OSError):
                pass
        with self._lock:
            return self._memory.get(self._memory_key(credential_id, resource, day), 0)

    def remaining(self, credential_id, resource, when=None):
        return max(self.limit_for(resource) - self.used(credential_id, resource, when), 0)

    def can_spend(self, credential_id, resource, calls=1, when=None):
        return self.remaining(credential_id, resource, when) >= calls

    def note(self, credential_id, resource, kind, when=None):
        """Record a notable event (throttled / exhausted) for diagnostics."""
        if not self.enabled:
            return
        import time as _time

        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO quota_events (credential_id, resource, kind, at)"
                    " VALUES (?, ?, ?, ?)",
                    (credential_id, resource, kind, _time.time()),
                )
        except (sqlite3.Error, OSError):
            pass

    def snapshot(self, credential_ids, when=None):
        """Per-key budget report for the UI."""
        rows = []
        for credential_id in credential_ids:
            for resource in ("browse", "insights"):
                limit = self.limit_for(resource)
                used = self.used(credential_id, resource, when)
                rows.append(
                    {
                        "credential": credential_id,
                        "resource": resource,
                        "used": used,
                        "limit": limit,
                        "remaining": max(limit - used, 0),
                        "used_share": round(used / limit, 4) if limit else 0.0,
                    }
                )
        return rows

    def reset(self, credential_id=None):
        """Clear counters — for tests, or after eBay raises an allowance."""
        with self._lock:
            self._memory.clear()
        if not self.enabled:
            return
        try:
            with self._connect() as conn:
                if credential_id:
                    conn.execute(
                        "DELETE FROM quota WHERE credential_id = ?", (credential_id,)
                    )
                else:
                    conn.execute("DELETE FROM quota")
        except (sqlite3.Error, OSError):
            pass


def calls_needed(items, page_size=200):
    """How many search calls a sample of ``items`` will cost."""
    if items <= 0:
        return 0
    page_size = max(1, int(page_size))
    return -(-int(items) // page_size)  # ceiling division


def plan_sample(desired_items, available_calls, page_size=200, reserve=2):
    """Shrink a request to what the remaining budget can actually pay for.

    Returns ``(items, calls, degraded)``.  Degrading a sweep and saying so
    beats failing halfway through with a half-written report.
    """
    page_size = max(1, int(page_size))
    spendable = max(int(available_calls) - int(reserve), 0)
    if spendable <= 0:
        return 0, 0, True
    affordable_items = spendable * page_size
    if desired_items <= affordable_items:
        return int(desired_items), calls_needed(desired_items, page_size), False
    return affordable_items, spendable, True
