import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

import hooks  # noqa: E402
import mom_components as mom  # noqa: E402

SETTINGS = SimpleNamespace(
    sections=[SimpleNamespace(base="wiki", description="Concept lead")],
    pages=[SimpleNamespace(path="findings", description="Findings lead"), SimpleNamespace(path="empty", description="")],
)


class NavSubtitleTests(unittest.TestCase):
    def test_home_is_the_tagline_and_listings_use_their_leads(self):
        self.assertEqual(hooks._nav_subtitle(SETTINGS, "/"), hooks.TAGLINE)
        self.assertEqual(hooks._nav_subtitle(SETTINGS, "/articles/"), hooks.ARTICLES_LEAD)
        self.assertEqual(hooks._nav_subtitle(SETTINGS, "/posts/"), hooks.POSTS_LEAD)

    def test_sections_and_pages_use_their_configured_descriptions(self):
        self.assertEqual(hooks._nav_subtitle(SETTINGS, "/wiki/"), "Concept lead")
        self.assertEqual(hooks._nav_subtitle(SETTINGS, "/findings/"), "Findings lead")

    def test_unknown_destination_has_no_subtitle(self):
        self.assertEqual(hooks._nav_subtitle(SETTINGS, "/nowhere/"), "")
        self.assertEqual(hooks._nav_subtitle(SETTINGS, "/empty/"), "")


class MenuMarkupTests(unittest.TestCase):
    def test_button_is_a_named_collapsed_button_controlling_the_panel(self):
        html = mom.menu_button()
        self.assertIn('<button type="button" class="mom-menu-button" aria-label="Menu" aria-expanded="false" aria-controls="mom-menu">', html)
        self.assertIn('data-icon="menu"', html)
        self.assertIn('data-icon="x"', html)

    def test_panel_marks_only_the_current_destination_and_escapes_text(self):
        html = mom.menu_panel([("Home", "/", "Tag & line", False), ("Posts", "/posts/", "", True)])
        self.assertIn("hidden>", html)
        self.assertIn("Tag &amp; line", html)
        self.assertEqual(html.count('aria-current="page"'), 1)
        self.assertEqual(html.count("You are here"), 1)
        self.assertEqual(html.count("mom-menu-sub"), 1)


if __name__ == "__main__":
    unittest.main()
