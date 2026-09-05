import unittest
from datetime import datetime, timezone

from ebay_research.models import Listing, SoldRecord
from tests.fakes import sale, summary


class ListingParsingTests(unittest.TestCase):
    def test_parses_a_full_summary(self):
        listing = Listing.from_summary(
            summary("v1|123|0", "Unicorn Book", 9.99, shipping=2.5, seller="wonderleaf"),
            marketplace="EBAY_GB",
        )
        self.assertEqual(listing.item_id, "v1|123|0")
        self.assertEqual(listing.price, 9.99)
        self.assertEqual(listing.shipping_cost, 2.5)
        self.assertEqual(listing.total_cost, 12.49)
        self.assertEqual(listing.seller, "wonderleaf")
        self.assertEqual(listing.seller_feedback_pct, 99.5)
        self.assertEqual(listing.category_name, "Books")
        self.assertEqual(listing.marketplace, "EBAY_GB")
        self.assertTrue(listing.is_fixed_price)
        self.assertFalse(listing.is_auction)

    def test_free_shipping_detected(self):
        listing = Listing.from_summary(summary("1", "a", 5.0, shipping=0))
        self.assertTrue(listing.free_shipping)
        self.assertEqual(listing.total_cost, 5.0)

    def test_missing_shipping_quote(self):
        listing = Listing.from_summary(summary("1", "a", 5.0))
        self.assertIsNone(listing.shipping_cost)
        self.assertFalse(listing.free_shipping)
        self.assertEqual(listing.total_cost, 5.0)

    def test_auction_falls_back_to_current_bid(self):
        payload = summary("1", "a", 0, buying_options=["AUCTION"])
        payload.pop("price")
        payload["currentBidPrice"] = {"value": "14.50", "currency": "GBP"}
        payload["bidCount"] = 7
        listing = Listing.from_summary(payload)
        self.assertEqual(listing.price, 14.50)
        self.assertEqual(listing.bid_count, 7)
        self.assertTrue(listing.is_auction)

    def test_best_offer_flag(self):
        listing = Listing.from_summary(
            summary("1", "a", 5.0, buying_options=["FIXED_PRICE", "BEST_OFFER"])
        )
        self.assertTrue(listing.accepts_offers)

    def test_garbage_values_do_not_crash(self):
        listing = Listing.from_summary(
            {"itemId": "1", "title": "x", "price": {"value": "not-a-number"}}
        )
        self.assertIsNone(listing.price)
        self.assertIsNone(listing.total_cost)

    def test_missing_fields_default_safely(self):
        listing = Listing.from_summary({})
        self.assertEqual(listing.title, "")
        self.assertEqual(listing.buying_options, ())
        self.assertIsNone(listing.age_days())

    def test_rejects_non_dict(self):
        with self.assertRaises(TypeError):
            Listing.from_summary(["not", "a", "dict"])

    def test_parses_dates_and_age(self):
        listing = Listing.from_summary(
            summary("1", "a", 5.0, created="2026-08-06T00:00:00.000Z")
        )
        self.assertEqual(listing.created.tzinfo, timezone.utc)
        age = listing.age_days(now=datetime(2026, 9, 5, tzinfo=timezone.utc))
        self.assertAlmostEqual(age, 30.0, places=1)

    def test_estimated_quantities(self):
        payload = summary("1", "a", 5.0)
        payload["estimatedAvailabilities"] = [
            {"estimatedAvailableQuantity": 4, "estimatedSoldQuantity": 11}
        ]
        listing = Listing.from_summary(payload)
        self.assertEqual(listing.available_quantity, 4)
        self.assertEqual(listing.sold_quantity, 11)

    def test_to_row_is_flat(self):
        row = Listing.from_summary(summary("1", "a", 5.0, shipping=1.0)).to_row()
        self.assertEqual(row["total_cost"], 6.0)
        self.assertEqual(row["format"], "Fixed price")
        self.assertTrue(all(not isinstance(v, (dict, list)) for v in row.values()))


class SoldRecordTests(unittest.TestCase):
    def test_parses_a_sale(self):
        record = SoldRecord.from_sale(
            sale("v1|9", "Dragon Book", 12.0, "2026-08-20T09:00:00.000Z", quantity=3)
        )
        self.assertEqual(record.price, 12.0)
        self.assertEqual(record.quantity, 3)
        self.assertEqual(record.sold_date.year, 2026)
        self.assertEqual(record.seller, "wonderleaf")

    def test_quantity_defaults_to_one(self):
        payload = sale("1", "a", 5.0, "2026-08-20T09:00:00.000Z")
        payload.pop("totalSoldQuantity")
        self.assertEqual(SoldRecord.from_sale(payload).quantity, 1)

    def test_bad_date_is_none(self):
        payload = sale("1", "a", 5.0, "not-a-date")
        self.assertIsNone(SoldRecord.from_sale(payload).sold_date)


if __name__ == "__main__":
    unittest.main()
