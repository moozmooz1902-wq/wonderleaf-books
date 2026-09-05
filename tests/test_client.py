import unittest

import requests

from ebay_research.cache import ResponseCache
from ebay_research.client import EbayClient, build_filter
from ebay_research.errors import ApiError, AuthError, NotAvailableError, RateLimitError
from ebay_research.http import HttpClient, TokenBucket
from tests.fakes import (
    FakeResponse,
    FakeSession,
    TOKEN_PAYLOAD,
    make_http,
    make_settings,
    sale,
    summary,
)


class TokenBucketTests(unittest.TestCase):
    def test_first_acquire_is_free(self):
        bucket = TokenBucket(rate_per_second=1000.0)
        self.assertEqual(bucket.acquire(), 0.0)

    def test_paces_when_drained(self):
        bucket = TokenBucket(rate_per_second=1000.0, capacity=1)
        bucket.acquire()
        self.assertGreaterEqual(bucket.acquire(), 0.0)


class HttpRetryTests(unittest.TestCase):
    def test_retries_then_succeeds(self):
        session = FakeSession(
            [
                FakeResponse(503, {"errors": [{"message": "busy"}]}),
                FakeResponse(200, {"ok": True}),
            ]
        )
        http = make_http(session)
        self.assertEqual(http.get_json("https://x/y"), {"ok": True})
        self.assertEqual(http.stats["retries"], 1)
        self.assertEqual(http.stats["requests"], 2)

    def test_rate_limit_exhausted_raises(self):
        session = FakeSession([FakeResponse(429, {}, {"Retry-After": "1"})] * 5)
        http = make_http(session, max_retries=2)
        with self.assertRaises(RateLimitError):
            http.get_json("https://x/y")
        self.assertEqual(http.stats["throttled"], 3)

    def test_client_error_is_not_retried(self):
        session = FakeSession(
            [FakeResponse(400, {"errors": [{"errorId": 12001, "message": "bad filter"}]})]
        )
        http = make_http(session)
        with self.assertRaises(ApiError) as ctx:
            http.get_json("https://x/y")
        self.assertIn("bad filter", str(ctx.exception))
        self.assertEqual(session.calls.__len__(), 1)

    def test_network_error_retries_then_gives_up(self):
        class Boom(FakeSession):
            def request(self, *args, **kwargs):
                raise requests.ConnectionError("down")

        http = make_http(Boom(), max_retries=1)
        with self.assertRaises(ApiError):
            http.get_json("https://x/y")


class FilterTests(unittest.TestCase):
    def test_seller_filter(self):
        self.assertEqual(build_filter(seller="wonderleaf"), "sellers:{wonderleaf}")

    def test_multiple_sellers(self):
        self.assertEqual(build_filter(seller=["a", "b"]), "sellers:{a|b}")

    def test_price_filter_always_declares_currency(self):
        result = build_filter(price_min=5, price_max=50, currency="GBP")
        self.assertIn("price:[5..50]", result)
        self.assertIn("priceCurrency:GBP", result)

    def test_open_ended_price(self):
        self.assertIn("price:[10..]", build_filter(price_min=10, currency="USD"))

    def test_conditions_and_options(self):
        result = build_filter(
            conditions=["NEW", "USED"], buying_options=["FIXED_PRICE"]
        )
        self.assertIn("conditions:{NEW|USED}", result)
        self.assertIn("buyingOptions:{FIXED_PRICE}", result)

    def test_empty(self):
        self.assertEqual(build_filter(), "")


class TokenTests(unittest.TestCase):
    def test_token_is_cached_between_calls(self):
        session = FakeSession(
            [TOKEN_PAYLOAD, {"total": 0, "itemSummaries": []}, {"total": 0, "itemSummaries": []}]
        )
        client = EbayClient(make_settings(), http=make_http(session), cache=ResponseCache("", enabled=False))
        client.search_page(query="a", limit=1)
        client.search_page(query="b", limit=1)
        token_calls = [c for c in session.calls if c["url"].endswith("/oauth2/token")]
        self.assertEqual(len(token_calls), 1)

    def test_bad_credentials_raise_auth_error(self):
        session = FakeSession([FakeResponse(401, {"errors": [{"message": "invalid"}]})])
        client = EbayClient(make_settings(), http=make_http(session), cache=ResponseCache("", enabled=False))
        with self.assertRaises(AuthError):
            client.token()

    def test_missing_credentials_raise_config_error(self):
        from ebay_research.errors import ConfigError

        client = EbayClient(
            make_settings(client_id="", client_secret=""),
            http=make_http(FakeSession()),
            cache=ResponseCache("", enabled=False),
        )
        with self.assertRaises(ConfigError):
            client.token()


class SearchTests(unittest.TestCase):
    def _client(self, handler):
        session = FakeSession(handler=handler)
        return (
            EbayClient(
                make_settings(),
                http=make_http(session),
                cache=ResponseCache("", enabled=False),
            ),
            session,
        )

    def test_requires_a_query_or_category(self):
        client, _ = self._client(lambda url, params, data: TOKEN_PAYLOAD)
        with self.assertRaises(ValueError):
            client.search_page()

    def test_pages_until_max_items(self):
        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return TOKEN_PAYLOAD
            offset = int(params.get("offset", 0))
            limit = int(params.get("limit", 200))
            remaining = max(0, 250 - offset)
            count = min(limit, remaining)
            return {
                "total": 250,
                "itemSummaries": [
                    summary(f"v1|{offset + i}", f"book {offset + i}", 9.99)
                    for i in range(count)
                ],
            }

        client, session = self._client(handler)
        listings, total, truncated = client.search(query="book", max_items=250, page_size=200)
        self.assertEqual(len(listings), 250)
        self.assertEqual(total, 250)
        self.assertFalse(truncated)
        search_calls = [c for c in session.calls if "item_summary" in c["url"]]
        self.assertEqual(len(search_calls), 2)
        self.assertEqual(search_calls[1]["params"]["offset"], 200)

    def test_stops_early_when_results_run_out(self):
        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return TOKEN_PAYLOAD
            return {"total": 3, "itemSummaries": [summary("v1|1", "a", 5.0)] * 3}

        client, session = self._client(handler)
        listings, total, truncated = client.search(query="book", max_items=100)
        self.assertEqual(len(listings), 3)
        self.assertFalse(truncated)
        self.assertEqual(len([c for c in session.calls if "item_summary" in c["url"]]), 1)

    def test_truncated_when_total_exceeds_sample(self):
        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return TOKEN_PAYLOAD
            limit = int(params.get("limit", 200))
            return {
                "total": 5000,
                "itemSummaries": [summary(f"v1|{i}", "a", 5.0) for i in range(limit)],
            }

        client, _ = self._client(handler)
        listings, total, truncated = client.search(query="book", max_items=50)
        self.assertEqual(len(listings), 50)
        self.assertEqual(total, 5000)
        self.assertTrue(truncated)

    def test_seller_sweep_probes_categories_and_skips_empty(self):
        calls = {"probe": 0}

        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return TOKEN_PAYLOAD
            category = params.get("category_ids")
            if int(params.get("limit", 200)) == 1:
                calls["probe"] += 1
                return {"total": 4 if category == "267" else 0, "itemSummaries": []}
            return {
                "total": 4,
                "itemSummaries": [
                    summary(f"v1|{i}", f"picture book {i}", 8.5) for i in range(4)
                ],
            }

        client, session = self._client(handler)
        listings, total, truncated, per_category = client.sweep_seller(
            "wonderleaf", max_items=100
        )
        self.assertEqual(len(listings), 4)
        self.assertEqual(total, 4)
        self.assertFalse(truncated)
        self.assertEqual(per_category, {"Books, Comics & Magazines": 4})
        # Every category gets one cheap probe; only the non-empty one is paged.
        self.assertGreater(calls["probe"], 5)
        full_pages = [
            c for c in session.calls
            if "item_summary" in c["url"] and c["params"].get("limit") != 1
        ]
        self.assertEqual(len(full_pages), 1)

    def test_seller_sweep_with_query_is_a_single_search(self):
        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return TOKEN_PAYLOAD
            self.assertEqual(params.get("filter"), "sellers:{wonderleaf}")
            return {"total": 1, "itemSummaries": [summary("v1|1", "unicorn book", 7.99)]}

        client, session = self._client(handler)
        listings, _total, _truncated, per_category = client.sweep_seller(
            "wonderleaf", query="unicorn"
        )
        self.assertEqual(len(listings), 1)
        self.assertEqual(per_category, {})


class SoldTests(unittest.TestCase):
    def test_insights_403_becomes_not_available(self):
        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return TOKEN_PAYLOAD
            return FakeResponse(403, {"errors": [{"message": "not authorised"}]})

        client = EbayClient(
            make_settings(),
            http=make_http(FakeSession(handler=handler)),
            cache=ResponseCache("", enabled=False),
        )
        with self.assertRaises(NotAvailableError):
            client.search_sold(query="book")
        self.assertIs(client.insights_available, False)

    def test_sold_search_sends_a_date_window(self):
        seen = {}

        def handler(url, params, data):
            if url.endswith("/oauth2/token"):
                return TOKEN_PAYLOAD
            seen.update(params)
            return {
                "total": 1,
                "itemSales": [sale("v1|1", "unicorn book", 9.99, "2026-08-01T10:00:00.000Z")],
            }

        client = EbayClient(
            make_settings(),
            http=make_http(FakeSession(handler=handler)),
            cache=ResponseCache("", enabled=False),
        )
        records, total = client.search_sold(query="book", max_items=10)
        self.assertEqual(total, 1)
        self.assertEqual(records[0].price, 9.99)
        self.assertIn("lastSoldDate:[", seen["filter"])
        self.assertIs(client.insights_available, True)


class ProxyTests(unittest.TestCase):
    def test_configured_proxy_is_passed_to_every_request(self):
        session = FakeSession([TOKEN_PAYLOAD, {"total": 0, "itemSummaries": []}])
        settings = make_settings(proxy_url="http://proxy.internal:8080")
        http = HttpClient(
            rate_limit_rps=1000.0,
            max_retries=1,
            timeout=5,
            proxies=settings.proxies,
            session=session,
            sleep=lambda _s: None,
        )
        client = EbayClient(settings, http=http, cache=ResponseCache("", enabled=False))
        client.search_page(query="a", limit=1)
        for call in session.calls:
            self.assertEqual(
                call["proxies"],
                {"http": "http://proxy.internal:8080", "https": "http://proxy.internal:8080"},
            )


if __name__ == "__main__":
    unittest.main()
