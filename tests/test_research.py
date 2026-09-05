"""End-to-end pipeline tests against a fake eBay."""

import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from ebay_research import export, research
from ebay_research.cache import ResponseCache, SnapshotStore
from ebay_research.client import EbayClient
from tests.fakes import FakeResponse, FakeSession, TOKEN_PAYLOAD, make_http, make_settings, sale, summary

RECENT = (datetime.now(timezone.utc) - timedelta(days=5)).strftime(
    "%Y-%m-%dT%H:%M:%S.000Z"
)
LISTED = (datetime.now(timezone.utc) - timedelta(days=120)).strftime(
    "%Y-%m-%dT%H:%M:%S.000Z"
)

CATALOGUE = [
    summary("v1|1", "Personalised Childrens Picture Book Unicorn Story Gift Hardback",
            12.99, seller="wonderleaf", shipping=0, created=LISTED),
    summary("v1|2", "Personalised Childrens Picture Book Dragon Story Gift Hardback",
            12.99, seller="wonderleaf", shipping=0, created=LISTED),
    summary("v1|3", "L@@K!! BOOK BOOK free postage WOW", 4.99,
            seller="wonderleaf", shipping=2.99, promoted=True),
    summary("v1|4", "Personalised Bedtime Story Book Custom Name Age 3-7 New",
            15.50, seller="wonderleaf", shipping=0),
]

SALES = [
    sale("v1|10", "Personalised Childrens Picture Book Unicorn Story Gift", 12.99, RECENT, 3),
    sale("v1|11", "Personalised Custom Name Story Book Gift Hardback", 14.00, RECENT, 2),
]


def fake_ebay(catalogue=CATALOGUE, sales=SALES, insights=True, category="267"):
    """Handler that serves a small, deterministic eBay."""

    def handler(url, params, data):
        if url.endswith("/oauth2/token"):
            return TOKEN_PAYLOAD
        if "item_sales" in url:
            if not insights:
                return FakeResponse(403, {"errors": [{"message": "no access"}]})
            return {"total": len(sales), "itemSales": list(sales)}
        # Browse search
        if int(params.get("limit", 200)) == 1 and "category_ids" in params:
            found = len(catalogue) if params["category_ids"] == category else 0
            return {"total": found, "itemSummaries": []}
        offset = int(params.get("offset", 0))
        limit = int(params.get("limit", 200))
        page = catalogue[offset : offset + limit]
        return {"total": len(catalogue), "itemSummaries": page}

    return handler


class ResearchTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.cache_path = os.path.join(self.dir.name, "cache.sqlite3")
        self.store = SnapshotStore(self.cache_path)

    def tearDown(self):
        self.dir.cleanup()

    def client(self, handler):
        return EbayClient(
            make_settings(cache_path=self.cache_path),
            http=make_http(FakeSession(handler=handler)),
            cache=ResponseCache("", enabled=False),
        )


class SellerResearchTests(ResearchTestCase):
    def test_full_report(self):
        report = research.research_seller(
            self.client(fake_ebay()), "wonderleaf", store=self.store
        )
        self.assertEqual(report["kind"], "seller")
        self.assertEqual(report["summary"]["listings_sampled"], 4)
        self.assertEqual(report["identity"]["username"], "wonderleaf")
        self.assertEqual(report["identity"]["feedback_score"], 1200)
        self.assertEqual(report["prices"]["count"], 4)
        self.assertTrue(report["keywords"])
        self.assertTrue(report["findings"])
        self.assertIn("sold", report)
        self.assertEqual(report["sold"]["performance"]["sold_units"], 5)

    def test_worst_listing_is_the_spammy_one(self):
        report = research.research_seller(
            self.client(fake_ebay()), "wonderleaf", store=self.store
        )
        self.assertEqual(report["weakest_listings"][0]["item_id"], "v1|3")
        self.assertTrue(report["weakest_listings"][0]["problems"])

    def test_findings_mention_sold_performance(self):
        report = research.research_seller(
            self.client(fake_ebay()), "wonderleaf", store=self.store
        )
        joined = " ".join(report["findings"])
        self.assertIn("Sold data (90 days)", joined)
        self.assertIn("Median asking price", joined)

    def test_degrades_without_insights_access(self):
        report = research.research_seller(
            self.client(fake_ebay(insights=False)), "wonderleaf", store=self.store
        )
        self.assertNotIn("sold", report)
        self.assertTrue(report["warnings"])
        self.assertIn("Marketplace Insights", report["warnings"][0])
        self.assertTrue(report["findings"])  # active-only analysis still works

    def test_empty_seller_gives_a_useful_message(self):
        report = research.research_seller(
            self.client(fake_ebay(catalogue=[], sales=[])), "ghost", store=self.store
        )
        self.assertEqual(report["summary"]["listings_sampled"], 0)
        self.assertIn("No live listings found", report["findings"][0])

    def test_second_run_reports_the_trend(self):
        first = fake_ebay()
        client = self.client(first)
        research.research_seller(client, "wonderleaf", store=self.store)

        moved = list(CATALOGUE[:2]) + [summary("v1|5", "Brand New Listing Story Book", 20.0)]
        moved[0] = dict(moved[0], price={"value": "19.99", "currency": "GBP"})
        report = research.research_seller(
            self.client(fake_ebay(catalogue=moved)), "wonderleaf", store=self.store
        )
        trend = report["trend"]
        self.assertIsNotNone(trend)
        self.assertEqual(trend["new_listings"], 1)
        self.assertEqual(trend["removed_listings"], 2)
        self.assertEqual(trend["price_changes"][0]["item_id"], "v1|1")
        self.assertEqual(trend["price_changes"][0]["change"], 7.0)

    def test_requires_a_username(self):
        with self.assertRaises(ValueError):
            research.research_seller(self.client(fake_ebay()), "  ", store=self.store)


class MarketResearchTests(ResearchTestCase):
    def test_full_report(self):
        report = research.research_market(
            self.client(fake_ebay()), "personalised picture book", store=self.store
        )
        self.assertEqual(report["kind"], "market")
        self.assertEqual(report["summary"]["listings_sampled"], 4)
        self.assertIn("competition", report)
        self.assertTrue(report["sellers"])
        self.assertTrue(report["findings"])
        self.assertIn("sold", report)

    def test_findings_cover_price_gap_and_keywords(self):
        report = research.research_market(
            self.client(fake_ebay()), "personalised picture book", store=self.store
        )
        joined = " ".join(report["findings"])
        self.assertIn("live listings match", joined)
        self.assertIn("distinct sellers", joined)
        self.assertIn("Gap analysis", joined)

    def test_warns_when_sold_data_is_missing(self):
        report = research.research_market(
            self.client(fake_ebay(insights=False)), "book", store=self.store
        )
        joined = " ".join(report["findings"])
        self.assertIn("asking prices, not achieved prices", joined)

    def test_no_matches(self):
        report = research.research_market(
            self.client(fake_ebay(catalogue=[], sales=[])), "nothing", store=self.store
        )
        self.assertIn("No live listings matched", report["findings"][0])

    def test_requires_a_subject(self):
        with self.assertRaises(ValueError):
            research.research_market(self.client(fake_ebay()), "", store=self.store)


class CompareSellersTests(ResearchTestCase):
    def test_side_by_side(self):
        result = research.compare_sellers(
            self.client(fake_ebay()), ["wonderleaf", "rival"], query="book"
        )
        self.assertEqual(len(result["sellers"]), 2)
        self.assertEqual(result["sellers"][0]["listings_sampled"], 4)
        self.assertTrue(result["sellers"][0]["top_keywords"])

    def test_ignores_blank_names(self):
        result = research.compare_sellers(self.client(fake_ebay()), ["", "  "], query="book")
        self.assertEqual(result["sellers"], [])


class ExportTests(ResearchTestCase):
    def test_markdown_brief_contains_the_findings(self):
        report = research.research_seller(
            self.client(fake_ebay()), "wonderleaf", store=self.store
        )
        markdown = export.report_to_markdown(report)
        self.assertIn("# eBay Seller Research — wonderleaf", markdown)
        self.assertIn("## What this means", markdown)
        self.assertIn(report["findings"][0][:40], markdown)
        self.assertIn("Sold performance", markdown)

    def test_csv_has_a_row_per_listing(self):
        report = research.research_seller(
            self.client(fake_ebay()), "wonderleaf", store=self.store
        )
        csv_text = export.rows_to_csv(report["listings"])
        self.assertEqual(len(csv_text.strip().splitlines()), 5)  # header + 4
        self.assertIn("item_id,title,price", csv_text)

    def test_csv_of_nothing(self):
        self.assertEqual(export.rows_to_csv([]), "")

    def test_json_round_trips(self):
        import json

        report = research.research_market(
            self.client(fake_ebay()), "book", store=self.store
        )
        self.assertEqual(
            json.loads(export.report_to_json(report))["subject"], "book"
        )


if __name__ == "__main__":
    unittest.main()
