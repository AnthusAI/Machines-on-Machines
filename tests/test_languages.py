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
        self.assertEqual(json.loads((REPOSITORY_ROOT / "web" / "language-groups.json").read_text(encoding="utf-8")), {"prefixes": {"es": "es", "zh-Hans": "zh"}, "groups": []})


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


PREFIXES = {"es": "es", "zh-Hans": "zh"}
STRINGS = languages.INTERFACE_STRINGS["es"]
LINK_GROUPS = [THREE, TWO, {"en": "/", "es": "/es/", "zh-Hans": "/zh/"}]


def localize(html, language="es"):
    return languages.localize_links(html, language, "en", LINK_GROUPS, PREFIXES, languages.INTERFACE_STRINGS[language], "https://example.test")


class LinkLocalizationTests(unittest.TestCase):
    def test_a_language_is_known_by_its_prefix_when_its_page_is_in_no_group(self):
        self.assertEqual(languages.language_of_page("/es/articles/c/", [], "en", PREFIXES), "es")
        self.assertEqual(languages.language_of_page("/zh/", [], "en", PREFIXES), "zh-Hans")
        self.assertEqual(languages.language_of_page("/articles/c/", [], "en", PREFIXES), "en")
        self.assertEqual(languages.language_of_page("/espresso/", [], "en", PREFIXES), "en", "a prefix is a whole path segment")

    def test_a_link_to_a_page_with_a_localization_goes_to_it(self):
        self.assertEqual(localize('<a href="/articles/a/">A</a>'), '<a href="/es/articles/a/">A</a>')
        self.assertEqual(localize('<a href="/articles/a/">A</a>', "zh-Hans"), '<a href="/zh/articles/a/">A</a>')
        self.assertEqual(localize('<a class="x" href="/">Home</a>'), '<a class="x" href="/es/">Home</a>')

    def test_the_query_and_the_fragment_survive(self):
        self.assertEqual(localize('<a href="/articles/a/?x=1&amp;y=2#top">A</a>'), '<a href="/es/articles/a/?x=1&amp;y=2#top">A</a>')

    def test_the_site_own_absolute_address_is_an_internal_link(self):
        self.assertEqual(localize('<a href="https://example.test/articles/a/">A</a>'), '<a href="/es/articles/a/">A</a>')

    def test_a_link_to_a_page_with_no_localization_in_the_language_is_marked_and_says_the_language(self):
        self.assertEqual(localize('<a href="/articles/b/">B</a>', "zh-Hans"), '<a href="/articles/b/" hreflang="en">B <span class="mom-link-language">（英文）</span></a>')
        self.assertEqual(localize('<a href="/articles/z/">Z</a>'), '<a href="/articles/z/" hreflang="en">Z <span class="mom-link-language">(en inglés)</span></a>')

    def test_a_link_with_nothing_to_mark_gets_hreflang_and_no_marker(self):
        found = localize('<a href="/articles/z/"><img src="/assets/x.png" alt=""></a>')
        self.assertIn('hreflang="en"', found)
        self.assertNotIn("mom-link-language", found)

    def test_links_that_are_not_pages_or_not_internal_are_left_alone(self):
        for untouched in ('<a href="https://other.test/articles/a/">A</a>', '<a href="#top">A</a>', '<a href="/feed.xml">RSS</a>', '<a href="/assets/x.pdf">PDF</a>',
                          '<a href="/es/articles/b/">already Spanish</a>', '<a href="mailto:a@example.test">M</a>'):
            self.assertEqual(localize(untouched), untouched)

    def test_the_switcher_options_are_left_alone_so_each_goes_to_its_own_language(self):
        option = '<a class="mom-language-option" href="/articles/a/" lang="en" hreflang="en" data-language="en">English</a>'
        self.assertEqual(localize(option), option)

    def test_the_marker_is_escaped(self):
        self.assertNotIn("<script", localize('<a href="/articles/z/">Z</a>', "es").replace('<span class="mom-link-language">', ""))

    def test_the_link_map_is_the_language_groups_by_every_address(self):
        found = languages.link_map(LINK_GROUPS)
        self.assertEqual(found["/es/articles/b/"], {"en": "/articles/b/", "es": "/es/articles/b/"})
        self.assertEqual(found["/"]["zh-Hans"], "/zh/")

    def test_the_rule_is_one_function_of_the_link_map(self):
        links = languages.link_map(LINK_GROUPS)
        self.assertEqual(languages.localized_link_target("/articles/a/", "es", links, PREFIXES), ("/es/articles/a/", False))
        self.assertEqual(languages.localized_link_target("/articles/b/", "zh-Hans", links, PREFIXES), ("/articles/b/", True))
        self.assertEqual(languages.localized_link_target("/feed.xml", "es", links, PREFIXES), ("/feed.xml", False))


if __name__ == "__main__":
    unittest.main()
