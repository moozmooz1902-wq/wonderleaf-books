import unittest
from datetime import datetime, timedelta, timezone

from ebay_research import analytics
from ebay_research.models import Listing, SoldRecord


def listing(price, seller="a", shipping=0.0, promoted=False, created=None, condition="New"):
    return Listing(
        item_id=f"v1|{price}|{seller}",
        title=f"item {price}",
        price=price,
        shipping_cost=shipping,
        free_shipping=shipping == 0.0,
        seller=seller,
        promoted=promoted,
        created=created,
        condition=condition,
        buying_options=("FIXED_PRICE",),
    )


class PercentileTests(unittest.TestCase):
    def test_interpolates(self):
        self.assertEqual(analytics.percentile([1, 2, 3, 4], 0.5), 2.5)

    def test_single_value(self):
        self.assertEqual(analytics.percentile([7], 0.9), 7.0)

    def test_empty(self):
        self.assertIsNone(analytics.percentile([], 0.5))


class DescribeTests(unittest.TestCase):
    def test_full_summary(self):
        result = analytics.describe([10, 20, 30, 40, 50])
        self.assertEqual(result["count"], 5)
        self.assertEqual(result["median"], 30)
        self.assertEqual(result["min"], 10)
        self.assertEqual(result["max"], 50)
        self.assertEqual(result["mean"], 30)

    def test_ignores_non_numeric(self):
        self.assertEqual(analytics.describe([None, "x", 5])["count"], 1)

    def test_empty(self):
        self.assertEqual(analytics.describe([]), {"count": 0})


class HistogramTests(unittest.TestCase):
    def test_bins_cover_everything(self):
        bins = analytics.histogram([1, 2, 3, 4, 5, 6], bins=3)
        self.assertEqual(sum(count for _, _, count in bins), 6)

    def test_constant_series(self):
        self.assertEqual(analytics.histogram([5, 5, 5]), [(5, 5, 3)])


class OutlierTests(unittest.TestCase):
    def test_flags_extremes(self):
        flagged, fences = analytics.outliers([10, 11, 12, 13, 14, 1000])
        self.assertIn(1000, flagged)
        self.assertIsNotNone(fences[1])

    def test_too_few_points(self):
        flagged, _ = analytics.outliers([1, 2])
        self.assertEqual(flagged, [])


class CompetitionTests(unittest.TestCase):
    def test_monopoly_is_concentrated(self):
        result = analytics.competition([listing(10, "big") for _ in range(10)])
        self.assertEqual(result["sellers"], 1)
        self.assertEqual(result["hhi"], 1.0)
        self.assertIn("concentrated", result["concentration"])

    def test_fragmented_market(self):
        items = [listing(10, f"seller{i}") for i in range(20)]
        result = analytics.competition(items)
        self.assertEqual(result["sellers"], 20)
        self.assertLess(result["hhi"], 0.10)
        self.assertIn("fragmented", result["concentration"])

    def test_no_listings(self):
        self.assertEqual(analytics.competition([])["sellers"], 0)


class SellThroughTests(unittest.TestCase):
    def test_rate_and_revenue(self):
        sold = [
            SoldRecord(item_id="1", price=10.0, quantity=2, sold_date=None),
            SoldRecord(item_id="2", price=20.0, quantity=1, sold_date=None),
        ]
        result = analytics.sell_through(active_count=8, sold_records=sold)
        self.assertEqual(result["sold_listings"], 2)
        self.assertEqual(result["sold_units"], 3)
        self.assertEqual(result["sell_through_rate"], 0.2)  # 2 / (2 + 8)
        self.assertEqual(result["estimated_revenue"], 40.0)
        self.assertAlmostEqual(result["average_sale_price"], 13.33, places=2)

    def test_no_sales(self):
        result = analytics.sell_through(5, [])
        self.assertEqual(result["sell_through_rate"], 0.0)
        self.assertIsNone(result["average_sale_price"])


class TrendTests(unittest.TestCase):
    def test_buckets_by_week(self):
        now = datetime(2026, 9, 5, tzinfo=timezone.utc)
        sold = [
            SoldRecord(item_id="1", price=10.0, sold_date=now - timedelta(days=1)),
            SoldRecord(item_id="2", price=10.0, sold_date=now - timedelta(days=10)),
        ]
        rows = analytics.sales_trend(sold, bucket_days=7, now=now)
        self.assertEqual(len(rows), 2)
        # Oldest bucket first.
        self.assertLess(rows[0]["period_start"], rows[1]["period_start"])

    def test_records_without_dates_are_skipped(self):
        self.assertEqual(analytics.sales_trend([SoldRecord(item_id="1")]), [])


class PriceBandTests(unittest.TestCase):
    def test_finds_the_converting_band(self):
        active = [listing(p) for p in [10, 12, 14, 90, 95, 98]]
        sold = [SoldRecord(item_id=str(i), price=p) for i, p in enumerate([90, 92, 96])]
        bands = analytics.price_bands(active, sold, bands=4)
        self.assertEqual(len(bands), 4)
        best = max(bands, key=lambda b: b["sell_through_rate"])
        self.assertGreater(best["band_low"], 50)

    def test_no_data(self):
        self.assertEqual(analytics.price_bands([], []), [])


class AgeTests(unittest.TestCase):
    def test_stale_share(self):
        now = datetime(2026, 9, 5, tzinfo=timezone.utc)
        items = [
            listing(10, created=now - timedelta(days=200)),
            listing(11, created=now - timedelta(days=2)),
        ]
        profile = analytics.listing_age_profile(items, now=now)
        self.assertEqual(profile["over_90_days"], 1)
        self.assertEqual(profile["stale_share"], 0.5)

    def test_no_dates(self):
        self.assertEqual(analytics.listing_age_profile([listing(10)])["count"], 0)


class LeaderboardTests(unittest.TestCase):
    def test_aggregates_per_seller(self):
        items = [listing(10, "a"), listing(30, "a"), listing(20, "b")]
        sold = [SoldRecord(item_id="1", price=10.0, quantity=4, seller="a")]
        rows = analytics.seller_leaderboard(items, sold)
        self.assertEqual(rows[0]["seller"], "a")
        self.assertEqual(rows[0]["listings"], 2)
        self.assertEqual(rows[0]["median_price"], 20.0)
        self.assertEqual(rows[0]["sold_units_90d"], 4)


class SnapshotDiffTests(unittest.TestCase):
    def test_detects_new_removed_and_price_moves(self):
        previous = {
            "generated_at": "2026-09-01T00:00:00+00:00",
            "listings": [
                {"item_id": "1", "title": "A", "price": 10.0},
                {"item_id": "2", "title": "B", "price": 20.0},
            ],
        }
        current = {
            "generated_at": "2026-09-05T00:00:00+00:00",
            "listings": [
                {"item_id": "1", "title": "A", "price": 12.0},
                {"item_id": "3", "title": "C", "price": 30.0},
            ],
        }
        diff = analytics.compare_snapshots(current, previous)
        self.assertEqual(diff["new_listings"], 1)
        self.assertEqual(diff["removed_listings"], 1)
        self.assertEqual(diff["price_changes"][0]["change"], 2.0)
        self.assertEqual(diff["removed_examples"][0]["item_id"], "2")

    def test_no_previous_run(self):
        self.assertIsNone(analytics.compare_snapshots({"listings": []}, None))


if __name__ == "__main__":
    unittest.main()
