import unittest

import markusmd


class HighlightMarkupTest(unittest.TestCase):
    def render(self, source):
        return markusmd.render(markusmd.parse(source), include_css=False, full_document=False)

    def test_double_equals_become_a_mark_that_nests_with_emphasis_and_a_link(self):
        html = self.render("A ==*key* claim with [a source](https://example.com)== here.")
        self.assertIn("<mark><em>key</em> claim with <a href=\"https://example.com\">a source</a></mark>", html)

    def test_a_single_equals_sign_is_plain_text(self):
        self.assertNotIn("<mark>", self.render("a = b and c == d"))


if __name__ == "__main__":
    unittest.main()
