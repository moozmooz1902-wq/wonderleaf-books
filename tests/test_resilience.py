"""The capacity layer: keyset failover, budget degradation, egress failover.

These cover the behaviour that decides whether the tool stays usable under
load -- which on eBay's API is a question of call allowance per application
keyset, not of network addresses.
"""

import os
import tempfile
import unittest

import requests

from ebay_research.cache import ResponseCache
from ebay_research.client import EbayClient
from ebay_research.credentials import Credential, CredentialPool
from ebay_research.errors import RateLimitError
from ebay_research.http import AdaptiveRate, HttpClient, TokenBucket
from ebay_research.quota import QuotaLedger
from tests.fakes import (
    FakeResponse,
    FakeSession,
    client_id_from_basic,
    make_http,
    make_settings,
    summary,
)


def keyset(name):
    return Credential(client_id=f"{name}-id", client_secret="secret", label=name)


PAGE = {"total": 2, "itemSummaries": [summary("v1|1", "unicorn story book", 9.99)] * 2}


class AdaptiveRateTests(unittest.TestCase):
    def test_halves_on_throttle(self):
        bucket = TokenBucket(4.0)
        adaptive = AdaptiveRate(bucket, start=4.0, minimum=0.5)
        adaptive.on_throttle()
        self.assertEqual(adaptive.rate, 2.0)
        self.assertEqual(bucket.rate, 2.0)

    def test_never_drops_below_the_floor(self):
        adaptive = AdaptiveRate(TokenBucket(4.0), start=4.0, minimum=1.0)
        for _ in range(10):
            adaptive.on_throttle()
        self.assertEqual(adaptive.rate, 1.0)

    def test_recovers_after_a_run_of_successes(self):
        bucket = TokenBucket(4.0)
        adaptive = AdaptiveRate(bucket, start=4.0, minimum=0.5, step=0.5, recovery=3)
        adaptive.on_throttle()
        self.assertEqual(adaptive.rate, 2.0)
        for _ in range(3):
            adaptive.on_success()
        self.assertEqual(adaptive.rate, 2.5)

    def test_never_exceeds_the_configured_ceiling(self):
        adaptive = AdaptiveRate(TokenBucket(4.0), start=4.0, maximum=4.0, recovery=1)
        for _ in range(20):
            adaptive.on_success()
        self.assertEqual(adaptive.rate, 4.0)

    def test_throttling_is_applied_through_the_http_client(self):
        session = FakeSession(
            [FakeResponse(429, {}, {"Retry-After": "1"}), FakeResponse(200, {"ok": 1})]
        )
        http = make_http(session, max_retries=2)
        http.get_json("https://x/y")
        self.assertEqual(http.adaptive.rate, 500.0)  # halved from 1000


class EgressFailoverTests(unittest.TestCase):
    def test_dead_egress_fails_over_to_the_next(self):
        used = []

        def handler(url, params, data, headers, proxies):
            used.append(proxies["https"])
            if proxies["https"] == "http://dead:8080":
                raise requests.ConnectionError("refused")
            return {"ok": True}

        http = HttpClient(
            rate_limit_rps=1000.0,
            max_retries=3,
            timeout=5,
            proxies=["http://dead:8080", "http://alive:8080"],
            session=FakeSession(handler=handler),
            sleep=lambda _s: None,
        )
        self.assertEqual(http.get_json("https://x/y"), {"ok": True})
        self.assertEqual(used, ["http://dead:8080", "http://alive:8080"])
        self.assertEqual(http.stats["egress_failovers"], 1)

    def test_all_egress_down_reports_it(self):
        def handler(url, params, data, headers, proxies):
            raise requests.ConnectionError("refused")

        http = HttpClient(
            rate_limit_rps=1000.0,
            max_retries=2,
            timeout=5,
            proxies=["http://a:8080", "http://b:8080"],
            session=FakeSession(handler=handler),
            sleep=lambda _s: None,
        )
        with self.assertRaises(Exception) as ctx:
            http.get_json("https://x/y")
        self.assertIn("egress routes failed", str(ctx.exception))

    def test_egress_status_reports_health(self):
        http = HttpClient(proxies=["http://a:8080", "http://b:8080"], session=FakeSession())
        rows = http.egress_status()
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0]["active"])

    def test_direct_connection_is_reported(self):
        http = HttpClient(session=FakeSession())
        self.assertEqual(http.egress_status()[0]["egress"], "direct")


class KeysetFailoverTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "c.sqlite3")

    def tearDown(self):
        self.dir.cleanup()

    def build(self, handler, names=("a", "b"), limits=None):
        ledger = QuotaLedger(self.path, limits=limits or {"browse": 1000})
        pool = CredentialPool([keyset(n) for n in names], ledger=ledger)
        client = EbayClient(
            make_settings(cache_path=self.path),
            http=make_http(FakeSession(handler=handler)),
            cache=ResponseCache("", enabled=False),
            pool=pool,
            ledger=ledger,
        )
        return client, pool, ledger

    def _handler(self, throttle_keysets=(), exhaust_keysets=()):
        """Serve pages, but throttle/exhaust the named keysets."""
        tokens = {}

        def handler(url, params, data, headers):
            if url.endswith("/oauth2/token"):
                client_id = client_id_from_basic(headers)
                tokens[f"token-{client_id}"] = client_id
                return {"access_token": f"token-{client_id}", "expires_in": 7200}
            bearer = headers.get("Authorization", "").replace("Bearer ", "")
            client_id = tokens.get(bearer, "")
            label = client_id.split("-")[0]
            if label in throttle_keysets:
                return FakeResponse(429, {}, {"Retry-After": "30"})
            if label in exhaust_keysets:
                return FakeResponse(
                    403, {"errors": [{"message": "Application call limit exceeded"}]}
                )
            return PAGE

        return handler

    def test_throttled_keyset_hands_over_mid_request(self):
        client, pool, _ = self.build(self._handler(throttle_keysets=("a",)))
        payload = client.search_page(query="book", limit=2)
        self.assertEqual(payload["total"], 2)
        self.assertTrue(any("throttled" in note for note in client.notices))
        statuses = {row["keyset"]: row["status"] for row in pool.status()}
        self.assertEqual(statuses["a"], "throttled")
        self.assertEqual(statuses["b"], "ready")

    def test_exhausted_keyset_hands_over_and_is_marked_spent(self):
        client, pool, ledger = self.build(self._handler(exhaust_keysets=("a",)))
        payload = client.search_page(query="book", limit=2)
        self.assertEqual(payload["total"], 2)
        spent = next(c for c in pool.credentials if c.label == "a")
        self.assertEqual(ledger.remaining(spent.id, "browse"), 0)
        self.assertTrue(any("daily allowance" in note for note in client.notices))

    def test_every_keyset_throttled_raises_a_useful_error(self):
        client, _pool, _ = self.build(self._handler(throttle_keysets=("a", "b")))
        with self.assertRaises(RateLimitError) as ctx:
            client.search_page(query="book", limit=2)
        message = str(ctx.exception)
        self.assertIn("per application key", message)
        self.assertIn("resets in", message)

    def test_a_full_report_survives_one_keyset_dying(self):
        from ebay_research import research
        from ebay_research.cache import SnapshotStore

        client, _pool, _ = self.build(self._handler(throttle_keysets=("a",)))
        report = research.research_market(
            client,
            "unicorn story book",
            max_items=2,
            include_sold=False,
            store=SnapshotStore(self.path),
        )
        self.assertEqual(report["summary"]["listings_sampled"], 2)
        self.assertTrue(report["findings"])

    def test_successful_calls_are_billed_to_the_right_keyset(self):
        client, pool, ledger = self.build(self._handler(), names=("a",))
        client.search_page(query="book", limit=2)
        credential = pool.credentials[0]
        self.assertEqual(ledger.used(credential.id, "browse"), 1)

    def test_each_keyset_gets_its_own_token(self):
        seen = []

        def handler(url, params, data, headers):
            if url.endswith("/oauth2/token"):
                client_id = client_id_from_basic(headers)
                seen.append(client_id)
                return {"access_token": f"token-{client_id}", "expires_in": 7200}
            return PAGE

        client, _pool, _ = self.build(handler)
        client.search_page(query="a", limit=1)
        client.search_page(query="b", limit=1)
        self.assertEqual(sorted(seen), ["a-id", "b-id"])


class BudgetDegradationTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "c.sqlite3")

    def tearDown(self):
        self.dir.cleanup()

    def build(self, browse_limit, already_used=0):
        ledger = QuotaLedger(self.path, limits={"browse": browse_limit})
        pool = CredentialPool([keyset("a")], ledger=ledger)
        if already_used:
            ledger.record(pool.credentials[0].id, "browse", already_used)

        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return {"access_token": "t", "expires_in": 7200}
            limit = int(params.get("limit", 200))
            return {
                "total": 10000,
                "itemSummaries": [summary(f"v1|{i}", "book", 5.0) for i in range(limit)],
            }

        client = EbayClient(
            make_settings(cache_path=self.path),
            http=make_http(FakeSession(handler=handler)),
            cache=ResponseCache("", enabled=False),
            pool=pool,
            ledger=ledger,
        )
        return client, ledger

    def test_budget_reports_calls_left(self):
        client, _ = self.build(100, already_used=40)
        self.assertEqual(client.budget("browse"), 60)

    def test_budget_sums_across_keysets(self):
        ledger = QuotaLedger(self.path, limits={"browse": 100})
        pool = CredentialPool([keyset("a"), keyset("b")], ledger=ledger)
        client = EbayClient(
            make_settings(cache_path=self.path),
            http=make_http(FakeSession()),
            cache=ResponseCache("", enabled=False),
            pool=pool,
            ledger=ledger,
        )
        self.assertEqual(client.budget("browse"), 200)

    def test_sample_shrinks_to_fit_the_remaining_allowance(self):
        client, _ = self.build(10, already_used=5)  # 5 calls left, reserve 2 -> 3 pages
        listings, _total, truncated = client.search(query="book", max_items=5000)
        self.assertEqual(len(listings), 600)
        self.assertTrue(truncated)
        self.assertTrue(any("Sample reduced" in note for note in client.notices))
        self.assertTrue(any("per keyset" in note for note in client.notices))

    def test_full_sample_when_the_budget_is_healthy(self):
        client, _ = self.build(5000)
        listings, _total, _truncated = client.search(query="book", max_items=400)
        self.assertEqual(len(listings), 400)
        self.assertEqual(client.notices, [])

    def test_spent_allowance_is_explained_not_crashed(self):
        client, _ = self.build(10, already_used=10)
        with self.assertRaises(RateLimitError):
            client.search(query="book", max_items=400, budget_aware=False)

    def test_budget_aware_search_returns_nothing_rather_than_failing(self):
        client, _ = self.build(10, already_used=10)
        listings, _total, _truncated = client.search(query="book", max_items=400)
        self.assertEqual(listings, [])
        self.assertTrue(any("allowance is spent" in note for note in client.notices))


class CacheSavesQuotaTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "c.sqlite3")

    def tearDown(self):
        self.dir.cleanup()

    def test_a_repeated_search_costs_no_allowance(self):
        calls = {"n": 0}

        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return {"access_token": "t", "expires_in": 7200}
            calls["n"] += 1
            return PAGE

        ledger = QuotaLedger(self.path, limits={"browse": 100})
        pool = CredentialPool([keyset("a")], ledger=ledger)
        client = EbayClient(
            make_settings(cache_path=self.path),
            http=make_http(FakeSession(handler=handler)),
            cache=ResponseCache(os.path.join(self.dir.name, "resp.sqlite3"), ttl=900),
            pool=pool,
            ledger=ledger,
        )
        client.search_page(query="book", limit=2)
        before = ledger.used(pool.credentials[0].id, "browse")
        client.search_page(query="book", limit=2)  # identical -> served from cache
        self.assertEqual(calls["n"], 1)
        self.assertEqual(ledger.used(pool.credentials[0].id, "browse"), before)


if __name__ == "__main__":
    unittest.main()
