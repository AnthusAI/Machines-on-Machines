import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

import languages  # noqa: E402
import mom_components as mom  # noqa: E402

THREE = {"en": "/articles/a/", "es": "/es/articles/a/", "zh-Hans": "/zh/articles/a/"}
TWO = {"en": "/articles/b/", "es": "/es/articles/b/"}
GROUPS = [THREE, TWO]


class AlternatesTests(unittest.TestCase):
    def test_a_page_lists_its_whole_group_in_native_names_itself_included(self):
        found = languages.alternates_for_page("/es/articles/a/", GROUPS)
        self.assertEqual([(a["tag"], a["name"], a["url"]) for a in found], [("en", "English", "/articles/a/"), ("es", "Español", "/es/articles/a/"), ("zh-Hans", "中文", "/zh/articles/a/")])

    def test_a_missing_translation_is_absent_and_nothing_stands_in_for_it(self):
        found = languages.alternates_for_page("/articles/b/", GROUPS)
        self.assertEqual([a["tag"] for a in found], ["en", "es"])
        self.assertNotIn("/zh/", json.dumps(found))

    def test_a_page_in_no_group_has_no_alternates(self):
        self.assertEqual(languages.alternates_for_page("/articles/c/", GROUPS), [])
        self.assertEqual(languages.alternates_for_page("/", []), [])

    def test_paths_match_with_or_without_slashes(self):
        self.assertEqual(len(languages.alternates_for_page("articles/a", GROUPS)), 3)

    def test_the_page_language_is_its_own_entry_or_the_primary(self):
        self.assertEqual(languages.language_of_page("/zh/articles/a/", languages.alternates_for_page("/zh/articles/a/", GROUPS), "en"), "zh-Hans")
        self.assertEqual(languages.language_of_page("/articles/c/", [], "en"), "en")

    def test_language_names_are_their_own_and_never_flags(self):
        for name in languages.NATIVE_NAMES.values():
            self.assertFalse(re.search("[\U0001F1E6-\U0001F1FF]", name))
        self.assertEqual(languages.NATIVE_NAMES, {"en": "English", "es": "Español", "zh-Hans": "中文"})

    def test_hreflang_lists_every_language_with_absolute_addresses_and_x_default(self):
        alternates = languages.alternates_for_page("/articles/a/", GROUPS)
        links = languages.hreflang_links(alternates, "en", "https://example.test/")
        self.assertEqual(re.findall(r'hreflang="([^"]*)" href="([^"]*)"', links), [
            ("en", "https://example.test/articles/a/"), ("es", "https://example.test/es/articles/a/"),
            ("zh-Hans", "https://example.test/zh/articles/a/"), ("x-default", "https://example.test/articles/a/")])

    def test_every_language_has_the_same_interface_strings(self):
        keys = {frozenset(strings) for strings in languages.INTERFACE_STRINGS.values()}
        self.assertEqual(len(keys), 1)
        self.assertEqual(set(languages.INTERFACE_STRINGS), set(languages.NATIVE_NAMES))
        for tag, strings in languages.INTERFACE_STRINGS.items():
            self.assertIn("{seconds}", strings["countdown"], tag)
            self.assertIn("{seconds}", strings["announce"], tag)

    def test_the_group_file_is_read_and_a_missing_file_means_no_groups(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "groups.json"
            self.assertEqual(languages.language_groups(path), [])
            path.write_text(json.dumps({"groups": GROUPS}), encoding="utf-8")
            self.assertEqual(languages.language_groups(path), GROUPS)
        self.assertEqual(json.loads((REPOSITORY_ROOT / "web" / "language-groups.json").read_text(encoding="utf-8")), {"groups": []})


class ComponentTests(unittest.TestCase):
    alternates = languages.alternates_for_page("/es/articles/a/", GROUPS)

    def test_the_switcher_marks_the_current_language_by_name_check_and_aria_current(self):
        markup = mom.language_switcher(self.alternates, "es", "Idioma")
        self.assertIn('aria-label="Idioma: Español"', markup)
        self.assertIn('<span class="mom-language-current">Español</span>', markup)
        self.assertEqual(markup.count('aria-current="true"'), 1)
        self.assertEqual(markup.count('data-icon="check"'), 1)
        self.assertIn('data-icon="languages"', markup)

    def test_every_option_is_a_link_with_lang_and_hreflang(self):
        markup = mom.language_switcher(self.alternates, "es", "Idioma")
        self.assertEqual(re.findall(r'<a class="mom-language-option" href="([^"]*)" lang="([^"]*)" hreflang="([^"]*)"', markup),
                         [("/articles/a/", "en", "en"), ("/es/articles/a/", "es", "es"), ("/zh/articles/a/", "zh-Hans", "zh-Hans")])

    def test_the_menu_section_lists_the_same_options(self):
        markup = mom.language_menu_section(self.alternates, "es", "Idioma")
        self.assertEqual(markup.count("<li>"), 3)
        self.assertIn("mom-language-menu-option", markup)
        self.assertEqual(markup.count('aria-current="true"'), 1)

    def test_the_banner_is_empty_and_hidden_with_a_polite_live_region(self):
        markup = mom.language_banner()
        self.assertIn("data-mom-language-banner hidden", markup)
        self.assertIn('role="status" aria-live="polite"></p>', markup)
        self.assertEqual(re.findall(r'data-action="(\w+)"', markup), ["switch", "read", "undo", "stay", "pause"])

    def test_the_menu_panel_places_extra_markup_after_the_destinations(self):
        markup = mom.menu_panel([("Home", "/", "", True)], extra="<section>X</section>")
        self.assertTrue(markup.endswith("</ul><section>X</section></nav>"))
        self.assertTrue(mom.menu_panel([("Home", "/", "", True)]).endswith("</ul></nav>"))

    def test_options_escape_what_they_are_given(self):
        markup = mom.language_switcher([{"tag": "en", "name": "<b>", "url": "/x/"}], "en", '"')
        self.assertNotIn("<b>", markup)


if __name__ == "__main__":
    unittest.main()
