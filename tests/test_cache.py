import os
import tempfile
import unittest

from ebay_research.cache import ResponseCache, SnapshotStore, make_key


class KeyTests(unittest.TestCase):
    def test_stable_regardless_of_dict_order(self):
        self.assertEqual(
            make_key("GET", {"a": 1, "b": 2}), make_key("GET", {"b": 2, "a": 1})
        )

    def test_different_inputs_differ(self):
        self.assertNotEqual(make_key("GET", "/a"), make_key("GET", "/b"))


class ResponseCacheTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "cache.sqlite3")

    def tearDown(self):
        self.dir.cleanup()

    def test_round_trip(self):
        cache = ResponseCache(self.path, ttl=60)
        cache.set("k", {"total": 3})
        self.assertEqual(cache.get("k"), {"total": 3})

    def test_expiry(self):
        cache = ResponseCache(self.path, ttl=60)
        cache.set("k", {"v": 1}, ttl=-1)
        self.assertIsNone(cache.get("k"))

    def test_purge_expired(self):
        cache = ResponseCache(self.path, ttl=60)
        cache.set("a", {"v": 1}, ttl=-1)
        cache.set("b", {"v": 2}, ttl=60)
        self.assertEqual(cache.purge_expired(), 1)
        self.assertEqual(cache.get("b"), {"v": 2})

    def test_clear(self):
        cache = ResponseCache(self.path, ttl=60)
        cache.set("k", {"v": 1})
        cache.clear()
        self.assertIsNone(cache.get("k"))

    def test_disabled_cache_is_a_no_op(self):
        cache = ResponseCache(self.path, enabled=False)
        cache.set("k", {"v": 1})
        self.assertIsNone(cache.get("k"))

    def test_unwritable_path_does_not_raise(self):
        cache = ResponseCache("/proc/definitely/not/writable/cache.db", ttl=60)
        cache.set("k", {"v": 1})  # must not raise
        self.assertIsNone(cache.get("k"))

    def test_unserialisable_value_is_ignored(self):
        cache = ResponseCache(self.path, ttl=60)
        cache.set("k", {"v": object()})
        self.assertIsNone(cache.get("k"))


class SnapshotStoreTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "cache.sqlite3")
        self.store = SnapshotStore(self.path)

    def tearDown(self):
        self.dir.cleanup()

    def test_history_is_newest_first(self):
        self.store.save("seller", "wonderleaf", "EBAY_GB", {"n": 1}, created_at=100)
        self.store.save("seller", "wonderleaf", "EBAY_GB", {"n": 2}, created_at=200)
        history = self.store.history("seller", "wonderleaf", "EBAY_GB")
        self.assertEqual([row["payload"]["n"] for row in history], [2, 1])

    def test_subject_lookup_is_case_insensitive(self):
        self.store.save("seller", "WonderLeaf", "EBAY_GB", {"n": 1})
        self.assertEqual(len(self.store.history("seller", "wonderleaf", "EBAY_GB")), 1)

    def test_marketplaces_are_kept_apart(self):
        self.store.save("seller", "a", "EBAY_GB", {"n": 1})
        self.assertEqual(self.store.history("seller", "a", "EBAY_US"), [])

    def test_subjects_listing(self):
        self.store.save("market", "unicorn book", "EBAY_GB", {"n": 1})
        self.store.save("market", "unicorn book", "EBAY_GB", {"n": 2})
        subjects = self.store.subjects("market")
        self.assertEqual(subjects[0]["subject"], "unicorn book")
        self.assertEqual(subjects[0]["runs"], 2)

    def test_disabled_store(self):
        store = SnapshotStore("", enabled=False)
        self.assertIsNone(store.save("seller", "a", "EBAY_GB", {}))
        self.assertEqual(store.history("seller", "a", "EBAY_GB"), [])


if __name__ == "__main__":
    unittest.main()
