"""Smoke tests for the Streamlit app: does it boot, and do both tools render?"""

import unittest

try:
    from streamlit.testing.v1 import AppTest

    STREAMLIT = True
except ImportError:  # the analysis package works without Streamlit
    STREAMLIT = False

APP = "wonderleaf_web.py"


@unittest.skipUnless(STREAMLIT, "streamlit is not installed")
class AppSmokeTests(unittest.TestCase):
    def app(self):
        import os

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), APP)
        test = AppTest.from_file(path, default_timeout=90)
        test.run()
        return test

    def test_app_boots_without_exceptions(self):
        test = self.app()
        self.assertEqual([e.value for e in test.exception], [])

    def test_both_tools_are_offered(self):
        test = self.app()
        self.assertEqual(
            test.sidebar.radio[0].options, ["Book Studio", "eBay Research"]
        )

    def test_book_studio_is_the_default(self):
        test = self.app()
        self.assertIn("🌙 Wonderleaf Books", [t.value for t in test.title])

    def test_ebay_research_renders_every_tab(self):
        test = self.app()
        test.sidebar.radio[0].set_value("eBay Research").run()
        self.assertEqual([e.value for e in test.exception], [])
        self.assertIn("🔎 eBay Research", [t.value for t in test.title])
        self.assertEqual(len(test.tabs), 5)

    def test_missing_credentials_are_explained_not_crashed(self):
        test = self.app()
        test.sidebar.radio[0].set_value("eBay Research").run()
        errors = " ".join(e.value for e in test.error)
        self.assertIn("No eBay API credentials found", errors)
        self.assertEqual([e.value for e in test.exception], [])

    def test_searching_without_credentials_reports_setup_not_a_traceback(self):
        test = self.app()
        test.sidebar.radio[0].set_value("eBay Research").run()
        test.text_input[0].set_value("unicorn book")
        test.button[0].click().run()
        self.assertEqual([e.value for e in test.exception], [])
        errors = " ".join(e.value for e in test.error)
        self.assertIn("EBAY_CLIENT_ID", errors)


if __name__ == "__main__":
    unittest.main()
