import os
import unittest
from unittest import mock

from ebay_research import cli


class ParserTests(unittest.TestCase):
    def test_requires_a_command(self):
        with self.assertRaises(SystemExit):
            cli.build_parser().parse_args([])

    def test_market_command(self):
        args = cli.build_parser().parse_args(["market", "unicorn book", "--markdown"])
        self.assertEqual(args.command, "market")
        self.assertEqual(args.query, "unicorn book")
        self.assertTrue(args.markdown)

    def test_seller_command_with_narrowing_query(self):
        args = cli.build_parser().parse_args(
            ["seller", "wonderleaf", "--query", "picture book", "--max-items", "50"]
        )
        self.assertEqual(args.username, "wonderleaf")
        self.assertEqual(args.query, "picture book")
        self.assertEqual(args.max_items, 50)

    def test_compare_takes_several_sellers(self):
        args = cli.build_parser().parse_args(["compare", "a", "b", "c"])
        self.assertEqual(args.usernames, ["a", "b", "c"])

    def test_rejects_an_unknown_marketplace(self):
        with self.assertRaises(SystemExit):
            cli.build_parser().parse_args(["--marketplace", "EBAY_MARS", "market", "x"])


class BudgetCommandTests(unittest.TestCase):
    def env(self, **values):
        clean = {k: v for k, v in os.environ.items() if not k.startswith("EBAY_")}
        clean.update(values)
        return mock.patch.dict(os.environ, clean, clear=True)

    def test_reports_missing_credentials_as_a_failure(self):
        with self.env():
            self.assertEqual(cli.main(["budget"]), 1)

    def test_reports_the_allowance_when_configured(self):
        with self.env(EBAY_CLIENT_ID="a", EBAY_CLIENT_SECRET="b", EBAY_CACHE_PATH=""):
            self.assertEqual(cli.main(["budget"]), 0)


if __name__ == "__main__":
    unittest.main()


class FlagPositionTests(unittest.TestCase):
    """Shared flags must work before *and* after the subcommand."""

    def test_flag_after_the_subcommand(self):
        args = cli.build_parser().parse_args(["market", "book", "--markdown"])
        self.assertTrue(args.markdown)

    def test_flag_before_the_subcommand(self):
        args = cli.build_parser().parse_args(["--markdown", "market", "book"])
        self.assertTrue(args.markdown)

    def test_max_items_after_the_subcommand(self):
        args = cli.build_parser().parse_args(["seller", "x", "--max-items", "25"])
        self.assertEqual(args.max_items, 25)

    def test_marketplace_after_the_subcommand(self):
        args = cli.build_parser().parse_args(
            ["market", "book", "--marketplace", "EBAY_US"]
        )
        self.assertEqual(args.marketplace, "EBAY_US")
