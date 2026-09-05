import unittest

from ebay_research import scoring
from ebay_research.models import Listing

MARKET = [
    "Personalised Childrens Picture Book Unicorn Story Gift Age 3-7 Hardback",
    "Personalised Childrens Picture Book Dragon Story Gift Age 3-7 Hardback",
    "Personalised Picture Book Custom Name Story Gift for Kids Hardback New",
    "Childrens Picture Book Bedtime Story Personalised Gift Hardback Age 4",
    "Custom Personalised Story Book for Children Picture Gift Hardback New",
]


class VocabularyTests(unittest.TestCase):
    def test_builds_shares(self):
        vocabulary = scoring.market_vocabulary(MARKET)
        self.assertIn("personalised", vocabulary)
        self.assertEqual(vocabulary["personalised"]["share"], 1.0)

    def test_empty_corpus(self):
        self.assertEqual(scoring.market_vocabulary([]), {})


class ScoreTitleTests(unittest.TestCase):
    def test_good_title_beats_bad_one(self):
        good = scoring.score_title(MARKET[0], market_titles=MARKET)
        bad = scoring.score_title("L@@K!! book book WOW", market_titles=MARKET)
        self.assertGreater(good["score"], bad["score"])
        self.assertGreater(good["score"], 60)
        self.assertLess(bad["score"], 40)

    def test_over_length_is_penalised(self):
        result = scoring.score_title("x" * 120, market_titles=MARKET)
        length = next(c for c in result["components"] if c["name"] == "Length use")
        self.assertLess(length["score"], length["max"] * 0.5)
        self.assertIn("truncates", length["reason"])

    def test_short_title_flags_wasted_space(self):
        result = scoring.score_title("Book", market_titles=MARKET)
        length = next(c for c in result["components"] if c["name"] == "Length use")
        self.assertIn("going to waste", length["reason"])

    def test_reports_missing_market_keywords(self):
        result = scoring.score_title("Blue Widget Thing", market_titles=MARKET)
        missing = [row["phrase"] for row in result["missing_keywords"]]
        self.assertIn("personalised", missing)

    def test_components_sum_to_score(self):
        result = scoring.score_title(MARKET[0], market_titles=MARKET)
        total = sum(c["score"] for c in result["components"])
        self.assertAlmostEqual(total, result["score"], places=0)

    def test_score_is_bounded(self):
        for title in ["", "a", MARKET[0], "L@@K " * 30]:
            result = scoring.score_title(title, market_titles=MARKET)
            self.assertGreaterEqual(result["score"], 0)
            self.assertLessEqual(result["score"], 100)

    def test_empty_title(self):
        result = scoring.score_title("", market_titles=MARKET)
        self.assertEqual(result["score"], scoring.score_title("", market_titles=MARKET)["score"])
        self.assertIn("Poor", result["verdict"])

    def test_works_without_a_market(self):
        result = scoring.score_title("Blue Cotton Shirt Size M New 2022")
        self.assertGreater(result["score"], 0)


class SuggestTitleTests(unittest.TestCase):
    def test_never_exceeds_the_limit(self):
        result = scoring.suggest_title(["Sweet Dreams Little Unicorn"], MARKET)
        self.assertLessEqual(result["length"], 80)
        self.assertIn("Sweet Dreams Little Unicorn", result["title"])

    def test_pulls_in_market_terms(self):
        result = scoring.suggest_title(["Unicorn Book"], MARKET)
        self.assertIn("personalised", result["title"].lower())

    def test_does_not_repeat_core_terms(self):
        result = scoring.suggest_title(["Picture Book", "Picture Book"], MARKET)
        self.assertEqual(result["title"].lower().count("picture book"), 1)

    def test_no_core_terms(self):
        result = scoring.suggest_title([], MARKET)
        self.assertLessEqual(result["length"], 80)

    def test_respects_custom_limit(self):
        result = scoring.suggest_title(["Unicorn"], MARKET, max_length=30)
        self.assertLessEqual(result["length"], 30)


class CompareTests(unittest.TestCase):
    def test_delta_is_reported(self):
        result = scoring.compare_titles("Book", MARKET[0], MARKET)
        self.assertGreater(result["delta"], 0)
        self.assertEqual(result["after"]["title"], MARKET[0])


class AuditTests(unittest.TestCase):
    def test_worst_titles_come_first(self):
        listings = [
            Listing(item_id="1", title=MARKET[0]),
            Listing(item_id="2", title="L@@K!!! book"),
        ]
        rows = scoring.audit_listings(listings)
        self.assertEqual(rows[0]["item_id"], "2")
        self.assertLess(rows[0]["score"], rows[1]["score"])

    def test_skips_untitled_listings(self):
        self.assertEqual(scoring.audit_listings([Listing(item_id="1", title="")]), [])


if __name__ == "__main__":
    unittest.main()
