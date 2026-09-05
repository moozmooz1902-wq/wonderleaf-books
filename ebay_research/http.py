"""HTTP transport: adaptive pacing, retries, and resilient egress.

What actually limits this tool
------------------------------
These are eBay's official REST APIs, called with an OAuth application token.
The allowance is counted against the **application keyset**, not the network
address the call arrives from, so extra IP addresses buy no extra capacity.
Everything here is therefore aimed at spending a fixed budget well:

* ``TokenBucket`` paces requests so a wide sweep cannot burst past the limit.
* ``AdaptiveRate`` halves the rate the moment eBay throttles and walks it back
  up when the coast is clear (AIMD, the same control loop TCP uses).  In
  practice this means you get throttled at most once, briefly, instead of
  repeatedly.
* Retries are exponential with jitter and honour ``Retry-After``.  A 400 is our
  bug and is surfaced immediately rather than hammered.
* ``on_throttle`` lets the caller hand the request to a different keyset
  instead of waiting, which is how the credential pool keeps a report running.

Egress
------
``proxies`` may be a single mapping or a list.  A list is failover: if an
egress dies mid-run the next healthy one takes over, and regional marketplaces
can be reached from the right country.  It is ordered and health-tracked, not
a rotation pool -- there is no block here to hide from, and disguising traffic
would not raise the keyset allowance that actually constrains the tool.
"""

from __future__ import annotations

import random
import threading
import time

import requests

from .errors import ApiError, RateLimitError

RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


class TokenBucket:
    """Thread-safe token bucket rate limiter with an adjustable rate."""

    def __init__(self, rate_per_second, capacity=None):
        self.rate = max(float(rate_per_second), 0.01)
        self.capacity = float(capacity if capacity is not None else max(self.rate, 1.0))
        self._tokens = self.capacity
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    def set_rate(self, rate_per_second):
        with self._lock:
            self.rate = max(float(rate_per_second), 0.01)
            self.capacity = max(self.capacity, self.rate)

    def acquire(self, tokens=1.0):
        """Block until ``tokens`` are available.  Returns seconds waited."""
        waited = 0.0
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._updated
                self._updated = now
                self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return waited
                delay = (tokens - self._tokens) / self.rate
            time.sleep(delay)
            waited += delay


class AdaptiveRate:
    """Additive-increase / multiplicative-decrease control of the send rate.

    Throttling is a signal that the current rate is too high for right now.
    Halving on that signal and creeping back up afterwards keeps throughput
    close to the ceiling without repeatedly crossing it.
    """

    def __init__(self, bucket, start, minimum=0.5, maximum=None, step=0.25, recovery=25):
        self.bucket = bucket
        self.rate = float(start)
        self.minimum = float(minimum)
        self.maximum = float(maximum if maximum is not None else start)
        self.step = float(step)
        self.recovery = int(recovery)
        self._successes = 0
        self._lock = threading.Lock()

    def on_success(self):
        with self._lock:
            self._successes += 1
            if self._successes < self.recovery or self.rate >= self.maximum:
                return
            self._successes = 0
            self.rate = min(self.rate + self.step, self.maximum)
        self.bucket.set_rate(self.rate)

    def on_throttle(self):
        with self._lock:
            self._successes = 0
            self.rate = max(self.rate / 2.0, self.minimum)
        self.bucket.set_rate(self.rate)


def _normalise_proxies(proxies):
    """Accept ``None``, one mapping, or a list of mappings/URLs."""
    if not proxies:
        return []
    if isinstance(proxies, dict):
        return [proxies]
    routes = []
    for entry in proxies:
        if isinstance(entry, dict):
            routes.append(entry)
        elif isinstance(entry, str) and entry.strip():
            url = entry.strip()
            routes.append({"http": url, "https": url})
    return routes


class HttpClient:
    """Requests wrapper with pacing, retries, egress failover and metrics."""

    def __init__(
        self,
        rate_limit_rps=4.0,
        max_retries=4,
        timeout=30.0,
        proxies=None,
        user_agent="WonderleafResearch/1.0",
        session=None,
        sleep=time.sleep,
        adaptive=True,
        min_rate=0.5,
    ):
        self.bucket = TokenBucket(rate_limit_rps)
        self.adaptive = (
            AdaptiveRate(self.bucket, rate_limit_rps, minimum=min_rate)
            if adaptive
            else None
        )
        self.max_retries = max(int(max_retries), 0)
        self.timeout = timeout
        self.routes = _normalise_proxies(proxies)
        self._route_index = 0
        self._route_failures = {}
        self.user_agent = user_agent
        self.session = session or requests.Session()
        self._sleep = sleep
        self.stats = {
            "requests": 0,
            "retries": 0,
            "throttled": 0,
            "wait_seconds": 0.0,
            "egress_failovers": 0,
        }

    # -- egress ------------------------------------------------------------

    @property
    def current_proxies(self):
        if not self.routes:
            return None
        return self.routes[self._route_index % len(self.routes)]

    def _next_route(self):
        """Move to the next configured egress after a transport failure."""
        if len(self.routes) <= 1:
            return False
        failed = self._route_index % len(self.routes)
        self._route_failures[failed] = self._route_failures.get(failed, 0) + 1
        self._route_index += 1
        self.stats["egress_failovers"] += 1
        return True

    def egress_status(self):
        rows = []
        for index, route in enumerate(self.routes):
            rows.append(
                {
                    "egress": route.get("https") or route.get("http") or "direct",
                    "active": index == self._route_index % len(self.routes),
                    "failures": self._route_failures.get(index, 0),
                }
            )
        return rows or [{"egress": "direct", "active": True, "failures": 0}]

    # -- internals ---------------------------------------------------------

    def _backoff(self, attempt, retry_after=None):
        if retry_after:
            try:
                return min(float(retry_after), 60.0)
            except (TypeError, ValueError):
                pass
        return min(2.0 ** attempt, 30.0) * (0.5 + random.random() / 2.0)

    # -- public API --------------------------------------------------------

    def request(
        self,
        method,
        url,
        *,
        headers=None,
        params=None,
        data=None,
        json_body=None,
        on_throttle=None,
    ):
        """Perform a request, retrying transient failures.

        ``on_throttle(retry_after)`` is called the first time eBay throttles.
        Returning ``True`` means the caller can handle it (typically by moving
        to another keyset), so we stop retrying here and raise immediately
        instead of sitting in a backoff loop.
        """
        headers = dict(headers or {})
        headers.setdefault("User-Agent", self.user_agent)
        last_error = None

        for attempt in range(self.max_retries + 1):
            self.stats["wait_seconds"] += self.bucket.acquire()
            self.stats["requests"] += 1
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_body,
                    timeout=self.timeout,
                    proxies=self.current_proxies,
                )
            except requests.RequestException as exc:
                last_error = exc
                switched = self._next_route()
                if attempt >= self.max_retries:
                    raise ApiError(
                        f"Network error calling {url}: {exc}"
                        + (
                            " All configured egress routes failed."
                            if self.routes
                            else ""
                        )
                    ) from exc
                self.stats["retries"] += 1
                # A fresh egress is worth trying straight away.
                self._sleep(0 if switched else self._backoff(attempt))
                continue

            if response.status_code == 429:
                self.stats["throttled"] += 1
                retry_after = response.headers.get("Retry-After")
                if self.adaptive:
                    self.adaptive.on_throttle()
                if on_throttle and on_throttle(retry_after):
                    raise RateLimitError(
                        "eBay throttled this keyset.", retry_after=retry_after
                    )
                if attempt >= self.max_retries:
                    raise RateLimitError(
                        "eBay call limit reached and retries exhausted. The daily "
                        "allowance is counted per application keyset, so add another "
                        "keyset, narrow the search, or wait for the reset.",
                        retry_after=retry_after,
                    )
                self.stats["retries"] += 1
                self._sleep(self._backoff(attempt, retry_after))
                continue

            if response.status_code in RETRY_STATUSES:
                if attempt >= self.max_retries:
                    raise ApiError(
                        f"eBay returned HTTP {response.status_code} after "
                        f"{attempt + 1} attempts",
                        status=response.status_code,
                        payload=_safe_json(response),
                    )
                self.stats["retries"] += 1
                self._sleep(self._backoff(attempt, response.headers.get("Retry-After")))
                continue

            if self.adaptive and response.status_code < 400:
                self.adaptive.on_success()
            return response

        raise ApiError(f"Request to {url} failed: {last_error}")

    def get_json(self, url, *, headers=None, params=None, on_throttle=None):
        response = self.request(
            "GET", url, headers=headers, params=params, on_throttle=on_throttle
        )
        return _require_json(response, url)

    def post_json(self, url, *, headers=None, data=None, json_body=None):
        response = self.request(
            "POST", url, headers=headers, data=data, json_body=json_body
        )
        return _require_json(response, url)


def _safe_json(response):
    try:
        return response.json()
    except ValueError:
        return {"raw": (response.text or "")[:500]}


def _require_json(response, url):
    payload = _safe_json(response)
    if response.status_code >= 400:
        raise ApiError(
            _describe(payload, response.status_code, url),
            status=response.status_code,
            payload=payload,
        )
    return payload


def _describe(payload, status, url):
    """Turn eBay's error envelope into a one-line message."""
    errors = payload.get("errors") if isinstance(payload, dict) else None
    if isinstance(errors, list) and errors:
        first = errors[0]
        message = first.get("longMessage") or first.get("message") or "unknown error"
        code = first.get("errorId")
        return f"eBay API error {code} (HTTP {status}) on {url}: {message}"
    return f"eBay API returned HTTP {status} on {url}"
