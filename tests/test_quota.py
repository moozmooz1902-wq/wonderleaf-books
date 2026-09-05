import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from ebay_research.quota import (
    DEFAULT_LIMITS,
    QuotaLedger,
    calls_needed,
    plan_sample,
    seconds_until_reset,
    utc_day,
)


class DayTests(unittest.TestCase):
    def test_day_is_utc(self):
        moment = datetime(2026, 9, 5, 23, 30, tzinfo=timezone.utc)
        self.assertEqual(utc_day(moment), "2026-09-05")

    def test_reset_countdown_is_positive(self):
        self.assertGreater(seconds_until_reset(), 0)
        self.assertLessEqual(seconds_until_reset(), 86400)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "cache.sqlite3")
        self.ledger = QuotaLedger(self.path)

    def tearDown(self):
        self.dir.cleanup()

    def test_counts_calls(self):
        self.ledger.record("key1", "browse", 3)
        self.assertEqual(self.ledger.used("key1", "browse"), 3)
        self.assertEqual(
            self.ledger.remaining("key1", "browse"), DEFAULT_LIMITS["browse"] - 3
        )

    def test_keysets_are_counted_separately(self):
        self.ledger.record("key1", "browse", 10)
        self.assertEqual(self.ledger.used("key2", "browse"), 0)

    def test_resources_are_counted_separately(self):
        self.ledger.record("key1", "browse", 10)
        self.assertEqual(self.ledger.used("key1", "insights"), 0)

    def test_persists_across_instances(self):
        self.ledger.record("key1", "browse", 7)
        reopened = QuotaLedger(self.path)
        self.assertEqual(reopened.used("key1", "browse"), 7)

    def test_allowance_resets_the_next_day(self):
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        self.ledger.record("key1", "browse", 4999, when=yesterday)
        self.assertEqual(self.ledger.used("key1", "browse"), 0)
        self.assertTrue(self.ledger.can_spend("key1", "browse", 100))

    def test_can_spend_respects_the_ceiling(self):
        self.ledger.record("key1", "browse", DEFAULT_LIMITS["browse"])
        self.assertFalse(self.ledger.can_spend("key1", "browse"))
        self.assertEqual(self.ledger.remaining("key1", "browse"), 0)

    def test_custom_limits(self):
        ledger = QuotaLedger(self.path, limits={"browse": 10})
        ledger.record("k", "browse", 9)
        self.assertEqual(ledger.remaining("k", "browse"), 1)

    def test_snapshot(self):
        self.ledger.record("key1", "browse", 100)
        rows = self.ledger.snapshot(["key1"])
        browse = next(row for row in rows if row["resource"] == "browse")
        self.assertEqual(browse["used"], 100)
        self.assertEqual(browse["remaining"], DEFAULT_LIMITS["browse"] - 100)

    def test_reset(self):
        self.ledger.record("key1", "browse", 100)
        self.ledger.reset()
        self.assertEqual(self.ledger.used("key1", "browse"), 0)

    def test_unwritable_path_falls_back_to_memory(self):
        ledger = QuotaLedger("/proc/nope/cache.db")
        ledger.record("key1", "browse", 5)
        self.assertEqual(ledger.used("key1", "browse"), 5)


class PlanningTests(unittest.TestCase):
    def test_calls_needed_rounds_up(self):
        self.assertEqual(calls_needed(1, 200), 1)
        self.assertEqual(calls_needed(200, 200), 1)
        self.assertEqual(calls_needed(201, 200), 2)
        self.assertEqual(calls_needed(0, 200), 0)

    def test_plan_within_budget_is_untouched(self):
        items, calls, degraded = plan_sample(400, available_calls=100)
        self.assertEqual(items, 400)
        self.assertEqual(calls, 2)
        self.assertFalse(degraded)

    def test_plan_shrinks_when_budget_is_short(self):
        items, calls, degraded = plan_sample(2000, available_calls=5, page_size=200)
        self.assertTrue(degraded)
        self.assertEqual(items, 600)  # (5 - 2 reserved) * 200
        self.assertEqual(calls, 3)

    def test_plan_with_no_budget_left(self):
        items, calls, degraded = plan_sample(500, available_calls=1)
        self.assertEqual((items, calls), (0, 0))
        self.assertTrue(degraded)


if __name__ == "__main__":
    unittest.main()
