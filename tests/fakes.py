"""Fake transport so the whole pipeline can be tested without a network."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

from ebay_research.config import Settings
from ebay_research.http import HttpClient


class FakeResponse:
    def __init__(self, status_code, payload, headers=None):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}
        self.text = json.dumps(payload)

    def json(self):
        if isinstance(self._payload, Exception):
            raise ValueError("not json")
        return self._payload


class FakeSession:
    """Records requests and replays queued responses.

    ``handler`` (url, params) -> payload gives per-request control; otherwise
    responses are popped from ``queue`` in order.
    """

    def __init__(self, queue=None, handler=None):
        self.queue = list(queue or [])
        self.handler = handler
        self.calls = []
        self._handler_arity = 3
        if handler is not None:
            try:
                import inspect

                self._handler_arity = len(
                    inspect.signature(handler).parameters
                )
            except (TypeError, ValueError):
                pass

    def request(self, method, url, headers=None, params=None, data=None, json=None, timeout=None, proxies=None):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "params": params or {},
                "data": data,
                "headers": headers or {},
                "proxies": proxies,
            }
        )
        if self.handler:
            if self._handler_arity >= 5:
                result = self.handler(url, params or {}, data, headers or {}, proxies)
            elif self._handler_arity == 4:
                result = self.handler(url, params or {}, data, headers or {})
            else:
                result = self.handler(url, params or {}, data)
            if isinstance(result, FakeResponse):
                return result
            return FakeResponse(200, result)
        if not self.queue:
            raise AssertionError(f"No queued response for {method} {url}")
        nxt = self.queue.pop(0)
        if isinstance(nxt, FakeResponse):
            return nxt
        return FakeResponse(200, nxt)


TOKEN_PAYLOAD = {"access_token": "fake-token", "expires_in": 7200}


def make_settings(**overrides):
    defaults = dict(
        client_id="id",
        client_secret="secret",
        environment="production",
        marketplace="EBAY_GB",
        cache_path="",  # disables the sqlite cache in tests
        cache_ttl=0,
        rate_limit_rps=1000.0,
        max_retries=2,
        timeout=5.0,
    )
    defaults.update(overrides)
    return Settings(**defaults)


def make_http(session, **overrides):
    return HttpClient(
        rate_limit_rps=overrides.pop("rate_limit_rps", 1000.0),
        max_retries=overrides.pop("max_retries", 2),
        timeout=5.0,
        session=session,
        sleep=lambda _seconds: None,
        **overrides,
    )


def summary(item_id, title, price, **kwargs):
    """Build a Browse item_summary payload."""
    payload = {
        "itemId": item_id,
        "title": title,
        "price": {"value": str(price), "currency": kwargs.get("currency", "GBP")},
        "seller": {
            "username": kwargs.get("seller", "wonderleaf"),
            "feedbackScore": kwargs.get("feedback_score", 1200),
            "feedbackPercentage": kwargs.get("feedback_pct", "99.5"),
        },
        "condition": kwargs.get("condition", "New"),
        "buyingOptions": kwargs.get("buying_options", ["FIXED_PRICE"]),
        "categories": [
            {
                "categoryId": kwargs.get("category_id", "267"),
                "categoryName": kwargs.get("category_name", "Books"),
            }
        ],
        "itemLocation": {"country": kwargs.get("country", "GB")},
        "itemWebUrl": f"https://www.ebay.co.uk/itm/{item_id}",
        "priorityListing": kwargs.get("promoted", False),
        "topRatedBuyingExperience": kwargs.get("top_rated", False),
    }
    shipping = kwargs.get("shipping")
    if shipping is not None:
        payload["shippingOptions"] = [
            {"shippingCost": {"value": str(shipping), "currency": "GBP"}}
        ]
    if kwargs.get("created"):
        payload["itemCreationDate"] = kwargs["created"]
    return payload


def sale(item_id, title, price, sold_date, quantity=1, seller="wonderleaf"):
    return {
        "itemId": item_id,
        "title": title,
        "lastSoldPrice": {"value": str(price), "currency": "GBP"},
        "lastSoldDate": sold_date,
        "totalSoldQuantity": quantity,
        "seller": {"username": seller},
        "categories": [{"categoryId": "267", "categoryName": "Books"}],
        "condition": "New",
        "itemWebUrl": f"https://www.ebay.co.uk/itm/{item_id}",
    }


def client_id_from_basic(headers):
    """Recover which keyset a token request used, for failover tests."""
    import base64

    raw = (headers or {}).get("Authorization", "")
    if not raw.startswith("Basic "):
        return None
    decoded = base64.b64decode(raw[6:]).decode("utf-8")
    return decoded.split(":", 1)[0]


def parse_params(url_or_params):
    if isinstance(url_or_params, dict):
        return url_or_params
    return {k: v[0] for k, v in parse_qs(urlparse(url_or_params).query).items()}
