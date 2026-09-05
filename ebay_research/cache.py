"""SQLite-backed caches.

Two things live here:

``ResponseCache``
    Short-lived cache of raw API responses.  Its real job is quota protection:
    eBay grants a fixed number of Browse calls per day, and paging a large
    seller burns through them fast.  Re-running the same research inside the
    TTL costs nothing.

``SnapshotStore``
    Long-lived record of every research run.  Because each run is stored with
    a timestamp, the tools can answer questions a single scrape never can:
    did this seller raise prices?  Did the listing count grow?  Which titles
    disappeared (and therefore probably sold)?
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time

_SCHEMA = """
CREATE TABLE IF NOT EXISTS responses (
    key         TEXT PRIMARY KEY,
    body        TEXT NOT NULL,
    created_at  REAL NOT NULL,
    expires_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS responses_expires ON responses (expires_at);

CREATE TABLE IF NOT EXISTS snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    kind        TEXT NOT NULL,
    subject     TEXT NOT NULL,
    marketplace TEXT NOT NULL,
    created_at  REAL NOT NULL,
    payload     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS snapshots_lookup
    ON snapshots (kind, subject, marketplace, created_at);
"""


def _connect(path):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def make_key(*parts):
    """Stable cache key from arbitrary JSON-serialisable parts."""
    blob = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class ResponseCache:
    """TTL cache for API responses.  ``enabled=False`` turns it into a no-op."""

    def __init__(self, path, ttl=900, enabled=True):
        self.path = path
        self.ttl = ttl
        self.enabled = enabled and bool(path)

    def get(self, key):
        if not self.enabled:
            return None
        try:
            with _connect(self.path) as conn:
                row = conn.execute(
                    "SELECT body FROM responses WHERE key = ? AND expires_at > ?",
                    (key, time.time()),
                ).fetchone()
        except (sqlite3.Error, OSError):
            return None
        if not row:
            return None
        try:
            return json.loads(row["body"])
        except json.JSONDecodeError:
            return None

    def set(self, key, value, ttl=None):
        if not self.enabled:
            return
        now = time.time()
        expires = now + (self.ttl if ttl is None else ttl)
        try:
            with _connect(self.path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO responses (key, body, created_at, expires_at)"
                    " VALUES (?, ?, ?, ?)",
                    (key, json.dumps(value), now, expires),
                )
        except (sqlite3.Error, OSError, TypeError, ValueError):
            # A cache that cannot write must never break the caller.
            pass

    def purge_expired(self):
        if not self.enabled:
            return 0
        try:
            with _connect(self.path) as conn:
                cur = conn.execute(
                    "DELETE FROM responses WHERE expires_at <= ?", (time.time(),)
                )
                return cur.rowcount
        except (sqlite3.Error, OSError):
            return 0

    def clear(self):
        if not self.enabled:
            return
        try:
            with _connect(self.path) as conn:
                conn.execute("DELETE FROM responses")
        except (sqlite3.Error, OSError):
            pass


class SnapshotStore:
    """Append-only history of research runs, used for trend comparisons."""

    def __init__(self, path, enabled=True):
        self.path = path
        self.enabled = enabled and bool(path)

    def save(self, kind, subject, marketplace, payload, created_at=None):
        """Store one run and return its row id (or ``None`` when disabled)."""
        if not self.enabled:
            return None
        try:
            with _connect(self.path) as conn:
                cur = conn.execute(
                    "INSERT INTO snapshots (kind, subject, marketplace, created_at, payload)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (
                        kind,
                        subject.strip().lower(),
                        marketplace,
                        created_at if created_at is not None else time.time(),
                        json.dumps(payload, default=str),
                    ),
                )
                return cur.lastrowid
        except (sqlite3.Error, OSError, TypeError, ValueError):
            return None

    def history(self, kind, subject, marketplace, limit=30):
        """Most recent runs first: ``[{"id", "created_at", "payload"}, ...]``."""
        if not self.enabled:
            return []
        try:
            with _connect(self.path) as conn:
                rows = conn.execute(
                    "SELECT id, created_at, payload FROM snapshots"
                    " WHERE kind = ? AND subject = ? AND marketplace = ?"
                    " ORDER BY created_at DESC LIMIT ?",
                    (kind, subject.strip().lower(), marketplace, limit),
                ).fetchall()
        except (sqlite3.Error, OSError):
            return []
        out = []
        for row in rows:
            try:
                payload = json.loads(row["payload"])
            except json.JSONDecodeError:
                continue
            out.append(
                {"id": row["id"], "created_at": row["created_at"], "payload": payload}
            )
        return out

    def subjects(self, kind=None, limit=100):
        """Distinct subjects tracked so far, most recently seen first."""
        if not self.enabled:
            return []
        sql = (
            "SELECT subject, marketplace, kind, MAX(created_at) AS last_seen,"
            " COUNT(*) AS runs FROM snapshots"
        )
        params = []
        if kind:
            sql += " WHERE kind = ?"
            params.append(kind)
        sql += " GROUP BY subject, marketplace, kind ORDER BY last_seen DESC LIMIT ?"
        params.append(limit)
        try:
            with _connect(self.path) as conn:
                rows = conn.execute(sql, params).fetchall()
        except (sqlite3.Error, OSError):
            return []
        return [dict(row) for row in rows]
