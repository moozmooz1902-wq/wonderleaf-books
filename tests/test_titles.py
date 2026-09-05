import unittest

from ebay_research import titles


class TokenizeTests(unittest.TestCase):
    def test_drops_stopwords_and_punctuation(self):
        tokens = titles.tokenize("The Big Book of Bedtime Stories!!!")
        self.assertEqual(tokens, ["big", "book", "bedtime", "stories"])

    def test_keeps_model_codes_and_digits(self):
        tokens = titles.tokenize("Sony WH-1000XM4 Headphones 2023")
        self.assertIn("wh-1000xm4", tokens)
        self.assertIn("2023", tokens)

    def test_drop_noise_removes_filler(self):
        tokens = titles.tokenize("RARE Vintage Teddy FREE POSTAGE", drop_noise=True)
        self.assertNotIn("rare", tokens)
        self.assertNotIn("postage", tokens)
        self.assertIn("vintage", tokens)


class NgramTests(unittest.TestCase):
    def test_bigrams(self):
        self.assertEqual(
            titles.ngrams(["a", "b", "c"], 2), ["a b", "b c"]
        )

    def test_too_short(self):
        self.assertEqual(titles.ngrams(["a"], 2), [])


class KeywordTableTests(unittest.TestCase):
    def test_document_frequency_not_raw_frequency(self):
        corpus = [
            "unicorn unicorn unicorn story",   # 'unicorn' 3x in ONE listing
            "dragon story",
            "dinosaur story",
            "fairy story",
        ]
        rows = titles.keyword_table(corpus, size=1, top=5)
        by_phrase = {row["phrase"]: row for row in rows}
        self.assertEqual(by_phrase["story"]["listings"], 4)
        self.assertEqual(by_phrase["unicorn"]["listings"], 1)
        self.assertEqual(by_phrase["unicorn"]["occurrences"], 3)
        # 'story' outranks 'unicorn' despite fewer total occurrences per title.
        self.assertEqual(rows[0]["phrase"], "story")
        self.assertEqual(by_phrase["story"]["share"], 1.0)

    def test_empty_corpus(self):
        self.assertEqual(titles.keyword_table([]), [])


class DistinctiveTermsTests(unittest.TestCase):
    def test_finds_terms_over_represented_in_target(self):
        sold = ["personalised unicorn book"] * 12 + ["personalised dragon book"] * 8
        active = ["plain unicorn book"] * 12 + ["plain dragon book"] * 8
        rows = titles.distinctive_terms(sold, active, top=5)
        phrases = [row["phrase"] for row in rows]
        self.assertEqual(phrases[0], "personalised")
        self.assertGreater(rows[0]["z_score"], 0)

    def test_ignores_rare_terms_below_min_count(self):
        rows = titles.distinctive_terms(["oneoff term here"], ["other words"] * 20)
        self.assertNotIn("oneoff", [row["phrase"] for row in rows])

    def test_empty_inputs(self):
        self.assertEqual(titles.distinctive_terms([], []), [])


class HygieneTests(unittest.TestCase):
    def test_spam_findings(self):
        findings = titles.spam_findings("L@@K!! RARE BOOK WOW FREE POSTAGE")
        self.assertTrue(any("L@@K" in f for f in findings))
        self.assertTrue(any("exclamation" in f.lower() for f in findings))

    def test_clean_title_has_no_findings(self):
        self.assertEqual(titles.spam_findings("Blue Cotton Shirt Size M 2022"), [])

    def test_repeated_words(self):
        self.assertEqual(titles.repeated_words("book book story"), ["book"])

    def test_caps_ratio(self):
        self.assertEqual(titles.caps_ratio("ABC"), 1.0)
        self.assertEqual(titles.caps_ratio("abc"), 0.0)
        self.assertEqual(titles.caps_ratio(""), 0.0)


class AttributeTests(unittest.TestCase):
    def test_detects_attributes(self):
        found = titles.detect_attributes("New Blue Nike Trainers Size 9 UK 2021 3x pack")
        self.assertTrue(found["colour"])
        self.assertTrue(found["condition"])
        self.assertTrue(found["year"])
        self.assertTrue(found["quantity"])

    def test_bare_title_declares_nothing(self):
        found = titles.detect_attributes("Story Book")
        self.assertFalse(any(found.values()))


class TitleStatsTests(unittest.TestCase):
    def test_shape_of_corpus(self):
        stats = titles.title_stats(["a" * 75, "b" * 20])
        self.assertEqual(stats["count"], 2)
        self.assertEqual(stats["avg_length"], 47.5)
        self.assertEqual(stats["pct_using_full_length"], 0.5)

    def test_empty(self):
        self.assertEqual(titles.title_stats([])["count"], 0)


if __name__ == "__main__":
    unittest.main()
