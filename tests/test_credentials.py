import os
import tempfile
import unittest
from unittest import mock

from ebay_research.credentials import Credential, CredentialPool, load_credentials
from ebay_research.errors import ConfigError, RateLimitError
from ebay_research.quota import QuotaLedger


def cred(name):
    return Credential(client_id=f"{name}-client-id", client_secret="secret", label=name)


class CredentialTests(unittest.TestCase):
    def test_id_is_stable_and_not_the_key(self):
        first, second = cred("a"), cred("a")
        self.assertEqual(first.id, second.id)
        self.assertNotIn("client-id", first.id)
        self.assertEqual(len(first.id), 16)

    def test_different_keys_get_different_ids(self):
        self.assertNotEqual(cred("a").id, cred("b").id)

    def test_display_never_leaks_the_full_key(self):
        credential = Credential(client_id="SUPERSECRETVALUE", client_secret="s")
        self.assertNotIn("SUPERSECRET", credential.display)

    def test_incomplete_credential_is_rejected(self):
        with self.assertRaises(ConfigError):
            Credential(client_id="x", client_secret="")


class PoolTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.ledger = QuotaLedger(
            os.path.join(self.dir.name, "c.sqlite3"), limits={"browse": 10}
        )
        self.now = [1000.0]

    def tearDown(self):
        self.dir.cleanup()

    def pool(self, names=("a", "b")):
        return CredentialPool(
            [cred(n) for n in names], ledger=self.ledger, clock=lambda: self.now[0]
        )

    def test_empty_pool_is_rejected(self):
        with self.assertRaises(ConfigError):
            CredentialPool([])

    def test_spreads_load_across_keysets(self):
        pool = self.pool()
        picked = set()
        for _ in range(4):
            credential = pool.acquire()
            picked.add(credential.label)
            pool.mark_success(credential)
        self.assertEqual(picked, {"a", "b"})

    def test_throttled_keyset_is_skipped(self):
        pool = self.pool()
        first = pool.acquire()
        pool.mark_throttled(first, retry_after=30)
        for _ in range(3):
            self.assertNotEqual(pool.acquire().id, first.id)

    def test_throttle_expires(self):
        pool = self.pool(("a",))
        first = pool.acquire()
        pool.mark_throttled(first, retry_after=30)
        self.assertIsNone(pool.acquire())
        self.now[0] += 31
        self.assertIsNotNone(pool.acquire())

    def test_spent_keyset_is_skipped_and_the_other_serves(self):
        pool = self.pool()
        a = next(c for c in pool.credentials if c.label == "a")
        self.ledger.record(a.id, "browse", 10)  # limit is 10
        for _ in range(3):
            self.assertEqual(pool.acquire().label, "b")

    def test_prefers_the_keyset_with_most_allowance_left(self):
        pool = self.pool()
        a = next(c for c in pool.credentials if c.label == "a")
        self.ledger.record(a.id, "browse", 8)
        self.assertEqual(pool.acquire().label, "b")

    def test_mark_exhausted_burns_the_days_budget(self):
        pool = self.pool(("a",))
        credential = pool.acquire()
        pool.mark_exhausted(credential)
        self.assertEqual(self.ledger.remaining(credential.id, "browse"), 0)
        self.assertIsNone(pool.acquire())

    def test_require_explains_itself_when_everything_is_spent(self):
        pool = self.pool()
        for credential in pool.credentials:
            self.ledger.record(credential.id, "browse", 10)
        with self.assertRaises(RateLimitError) as ctx:
            pool.require()
        message = str(ctx.exception)
        self.assertIn("resets in", message)
        self.assertIn("per application key", message)  # not an IP problem

    def test_success_is_counted_against_the_ledger(self):
        pool = self.pool(("a",))
        credential = pool.acquire()
        pool.mark_success(credential)
        self.assertEqual(self.ledger.used(credential.id, "browse"), 1)

    def test_status_report(self):
        pool = self.pool()
        rows = pool.status()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["status"], "ready")
        self.assertEqual(rows[0]["remaining_today"], 10)


class LoadingTests(unittest.TestCase):
    def env(self, **values):
        clean = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith("EBAY_")
        }
        clean.update(values)
        return mock.patch.dict(os.environ, clean, clear=True)

    def test_primary_only(self):
        with self.env(EBAY_CLIENT_ID="a", EBAY_CLIENT_SECRET="b"):
            found = load_credentials()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].label, "primary")

    def test_numbered_keysets(self):
        with self.env(
            EBAY_CLIENT_ID="a",
            EBAY_CLIENT_SECRET="b",
            EBAY_CLIENT_ID_2="c",
            EBAY_CLIENT_SECRET_2="d",
        ):
            found = load_credentials()
        self.assertEqual([c.client_id for c in found], ["a", "c"])

    def test_json_bundle(self):
        with self.env(
            EBAY_CREDENTIALS='[{"client_id": "x", "client_secret": "y", "label": "user-a"}]'
        ):
            found = load_credentials()
        self.assertEqual(found[0].label, "user-a")

    def test_bad_json_is_rejected_clearly(self):
        with self.env(EBAY_CREDENTIALS="not json"):
            with self.assertRaises(ConfigError):
                load_credentials()

    def test_duplicates_are_collapsed(self):
        with self.env(
            EBAY_CLIENT_ID="a",
            EBAY_CLIENT_SECRET="b",
            EBAY_CLIENT_ID_2="a",
            EBAY_CLIENT_SECRET_2="b",
        ):
            self.assertEqual(len(load_credentials()), 1)

    def test_user_supplied_keys_come_first(self):
        with self.env(EBAY_CLIENT_ID="platform", EBAY_CLIENT_SECRET="s"):
            found = load_credentials(
                extra=[{"client_id": "user", "client_secret": "s", "owner": "alice"}]
            )
        self.assertEqual(found[0].client_id, "user")
        self.assertEqual(found[0].owner, "alice")
        self.assertEqual(len(found), 2)

    def test_no_credentials_configured(self):
        with self.env():
            self.assertEqual(load_credentials(), [])


if __name__ == "__main__":
    unittest.main()
