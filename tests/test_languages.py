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

THREE = {"en": "/articles/a/", "es-419": "/es/articles/a/", "zh-Hans": "/zh/articles/a/"}
TWO = {"en": "/articles/b/", "es-419": "/es/articles/b/"}
GROUPS = [THREE, TWO]


class AlternatesTests(unittest.TestCase):
    def test_a_page_lists_its_whole_group_in_native_names_itself_included(self):
        found = languages.alternates_for_page("/es/articles/a/", GROUPS)
        self.assertEqual([(a["tag"], a["name"], a["url"]) for a in found], [("en", "English", "/articles/a/"), ("es-419", "Español", "/es/articles/a/"), ("zh-Hans", "中文", "/zh/articles/a/")])

    def test_a_missing_translation_is_absent_and_nothing_stands_in_for_it(self):
        found = languages.alternates_for_page("/articles/b/", GROUPS)
        self.assertEqual([a["tag"] for a in found], ["en", "es-419"])
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
        self.assertEqual(languages.NATIVE_NAMES, {"en": "English", "es-419": "Español", "zh-Hans": "中文"})

    def test_hreflang_lists_every_language_with_absolute_addresses_and_x_default(self):
        alternates = languages.alternates_for_page("/articles/a/", GROUPS)
        links = languages.hreflang_links(alternates, "en", "https://example.test/")
        self.assertEqual(re.findall(r'hreflang="([^"]*)" href="([^"]*)"', links), [
            ("en", "https://example.test/articles/a/"), ("es-419", "https://example.test/es/articles/a/"),
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
        self.assertEqual(json.loads((REPOSITORY_ROOT / "web" / "language-groups.json").read_text(encoding="utf-8")), {"prefixes": {"es-419": "es", "zh-Hans": "zh"}, "slugPolicies": {"es-419": "translated", "zh-Hans": "characters"}, "groups": []})


class ComponentTests(unittest.TestCase):
    alternates = languages.alternates_for_page("/es/articles/a/", GROUPS)

    def test_the_switcher_marks_the_current_language_by_name_check_and_aria_current(self):
        markup = mom.language_switcher(self.alternates, "es-419", "Idioma")
        self.assertIn('aria-label="Idioma: Español"', markup)
        self.assertIn('<span class="mom-language-current">Español</span>', markup)
        self.assertEqual(markup.count('aria-current="true"'), 1)
        self.assertEqual(markup.count('data-icon="check"'), 1)
        self.assertIn('data-icon="languages"', markup)

    def test_every_option_is_a_link_with_lang_and_hreflang(self):
        markup = mom.language_switcher(self.alternates, "es-419", "Idioma")
        self.assertEqual(re.findall(r'<a class="mom-language-option" href="([^"]*)" lang="([^"]*)" hreflang="([^"]*)"', markup),
                         [("/articles/a/", "en", "en"), ("/es/articles/a/", "es-419", "es-419"), ("/zh/articles/a/", "zh-Hans", "zh-Hans")])

    def test_the_menu_section_lists_the_same_options(self):
        markup = mom.language_menu_section(self.alternates, "es-419", "Idioma")
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


PREFIXES = {"es-419": "es", "zh-Hans": "zh"}
STRINGS = languages.INTERFACE_STRINGS["es-419"]
LINK_GROUPS = [THREE, TWO, {"en": "/", "es-419": "/es/", "zh-Hans": "/zh/"}]


ICON = '<svg class="mom-icon" data-icon="languages"></svg>'


def localize(html, language="es-419", in_body=True):
    """The links in `html`, as found in the page's own words (inside <main>) unless `in_body` is False (navigation, menu and footer)."""
    page = f"<main>{html}</main>" if in_body else html
    found = languages.localize_links(page, language, "en", LINK_GROUPS, PREFIXES, languages.INTERFACE_STRINGS[language], "https://example.test", ICON)
    return found[len("<main>"):-len("</main>")] if in_body else found


class LinkLocalizationTests(unittest.TestCase):
    def test_a_language_is_known_by_its_prefix_when_its_page_is_in_no_group(self):
        self.assertEqual(languages.language_of_page("/es/articles/c/", [], "en", PREFIXES), "es-419")
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
        self.assertEqual(localize('<a href="/articles/b/">B</a>', "zh-Hans"),
                         f'<a href="/articles/b/" lang="en" hreflang="en">B<span class="mom-link-language">{ICON}<span class="mom-visually-hidden" lang="zh-Hans"> 英文</span></span></a>')
        self.assertEqual(localize('<a href="/articles/z/">Z</a>'),
                         f'<a href="/articles/z/" lang="en" hreflang="en">Z<span class="mom-link-language">{ICON}<span class="mom-visually-hidden" lang="es-419"> en inglés</span></span></a>')

    def test_the_marker_has_no_parentheses_and_the_name_is_for_a_screen_reader_only(self):
        found = localize('<a href="/articles/z/">Z</a>')
        self.assertNotIn("(", found)
        self.assertIn('aria-hidden="true"', mom.lucide_icon("languages"))

    def test_a_link_in_the_navigation_or_footer_is_never_marked(self):
        self.assertEqual(localize('<a href="/articles/z/">Z</a>', in_body=False), '<a href="/articles/z/">Z</a>')

    def test_a_link_with_nothing_to_mark_gets_hreflang_and_no_marker(self):
        found = localize('<a href="/articles/z/"><img src="/assets/x.png" alt=""></a>')
        self.assertIn('hreflang="en"', found)
        self.assertIn('lang="en"', found)
        self.assertNotIn("mom-link-language", found)

    def test_links_that_are_not_pages_or_not_internal_are_left_alone(self):
        for untouched in ('<a href="https://other.test/articles/a/">A</a>', '<a href="#top">A</a>', '<a href="/feed.xml">RSS</a>', '<a href="/assets/x.pdf">PDF</a>',
                          '<a href="/es/articles/b/">already Spanish</a>', '<a href="mailto:a@example.test">M</a>'):
            self.assertEqual(localize(untouched), untouched)

    def test_the_switcher_options_are_left_alone_so_each_goes_to_its_own_language(self):
        option = '<a class="mom-language-option" href="/articles/a/" lang="en" hreflang="en" data-language="en">English</a>'
        self.assertEqual(localize(option), option)

    def test_the_marker_is_escaped(self):
        self.assertNotIn("<script", localize('<a href="/articles/z/">Z</a>', "es-419").replace('<span class="mom-link-language">', ""))

    def test_the_link_map_is_the_language_groups_by_every_address(self):
        found = languages.link_map(LINK_GROUPS)
        self.assertEqual(found["/es/articles/b/"], {"en": "/articles/b/", "es-419": "/es/articles/b/"})
        self.assertEqual(found["/"]["zh-Hans"], "/zh/")

    def test_the_rule_is_one_function_of_the_link_map(self):
        links = languages.link_map(LINK_GROUPS)
        self.assertEqual(languages.localized_link_target("/articles/a/", "es-419", links, PREFIXES), ("/es/articles/a/", False))
        self.assertEqual(languages.localized_link_target("/articles/b/", "zh-Hans", links, PREFIXES), ("/articles/b/", True))
        self.assertEqual(languages.localized_link_target("/feed.xml", "es-419", links, PREFIXES), ("/feed.xml", False))


CHINESE = "/zh/articles/如何引导一篇报道/"
CHINESE_ENCODED = "/zh/articles/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/"


class UnicodeAddressTests(unittest.TestCase):
    groups = [{"en": "/articles/a/", "zh-Hans": CHINESE}]

    def test_decoded_and_encoded_paths_are_the_same_page_and_the_output_is_encoded(self):
        for here in (CHINESE, CHINESE_ENCODED):
            found = languages.alternates_for_page(here, self.groups)
            self.assertEqual([a["url"] for a in found], ["/articles/a/", CHINESE_ENCODED])
            self.assertEqual(languages.language_of_page(here, found, "en", PREFIXES), "zh-Hans")

    def test_hreflang_links_are_percent_encoded(self):
        found = languages.hreflang_links(languages.alternates_for_page("/articles/a/", self.groups), "en", "https://example.test")
        self.assertIn(f'hreflang="zh-Hans" href="https://example.test{CHINESE_ENCODED}"', found)
        self.assertTrue(found.isascii())

    def test_a_link_to_the_page_in_either_form_is_localized_to_the_encoded_address(self):
        for href in ("/articles/a/",):
            self.assertIn(f'href="{CHINESE_ENCODED}"', languages.localize_links(f'<a href="{href}">x</a>', "zh-Hans", "en", self.groups, PREFIXES, languages.INTERFACE_STRINGS["zh-Hans"]))
        for href in (CHINESE, CHINESE_ENCODED):
            self.assertEqual(languages.localize_links(f'<a href="{href}">x</a>', "zh-Hans", "en", self.groups, PREFIXES, languages.INTERFACE_STRINGS["zh-Hans"]), f'<a href="{href}">x</a>')

    def test_encoded_path_round_trips(self):
        self.assertEqual(languages.encoded_path(CHINESE), CHINESE_ENCODED)
        self.assertEqual(languages.normalize_path(CHINESE_ENCODED), CHINESE)


class SlugTests(unittest.TestCase):
    def test_characters_keep_han_strip_marks_and_hyphenate_spaces(self):
        self.assertEqual(languages.draft_slug("近一半的新歌由 AI 制作。几乎没人听。", "characters"), "近一半的新歌由-ai-制作几乎没人听")

    def test_a_slug_is_cut_only_at_the_filesystem_limit_at_a_whole_character(self):
        self.assertEqual(languages.draft_slug("中" * 40, "characters"), "中" * 40)
        cut = languages.draft_slug("中" * 100, "characters")
        self.assertEqual((len(cut), len(cut.encode("utf-8"))), (85, languages.MAX_SLUG_BYTES))
        self.assertEqual(len(languages.draft_slug("a" * 400, "translated")), 255)

    def test_the_longest_encoded_address_is_far_under_the_platform_limits(self):
        from urllib.parse import quote
        address = quote(f"/zh/articles/{languages.draft_slug('中' * 300, 'characters')}/index.html", safe="/")
        self.assertLess(len(address), 1024)

    def test_a_title_with_no_slug_is_an_error(self):
        for title in ("", "！？。，", "   "):
            with self.assertRaises(languages.NoSlugError):
                languages.draft_slug(title, "characters")

    def test_an_unknown_policy_and_a_missing_primary_slug_are_errors(self):
        with self.assertRaises(languages.NoSlugError):
            languages.draft_slug("x", "guess")
        with self.assertRaises(languages.NoSlugError):
            languages.draft_slug("x", "primary")

    def test_translated_folds_to_ascii_words(self):
        self.assertEqual(languages.draft_slug("Cómo ejecutar un monitor", "translated"), "como-ejecutar-un-monitor")


class InterfaceStringTests(unittest.TestCase):
    reference = {"a": "A", "b": "B", "months": ["x", "y"], "sections": {"s": "S"}}

    def test_a_language_with_every_key_is_complete(self):
        found = languages.complete_languages({"en": self.reference, "es-419": dict(self.reference)})
        self.assertEqual(found, ["en", "es-419"])

    def test_a_language_with_a_missing_empty_or_short_key_is_not_complete(self):
        for broken in ({"a": "A", "months": ["x", "y"], "sections": {"s": "S"}}, {**reference_copy(), "b": ""}, {**reference_copy(), "months": ["x"]}, {**reference_copy(), "sections": {}}):
            self.assertEqual(languages.complete_languages({"en": self.reference, "es-419": broken}), ["en"])

    def test_an_incomplete_language_is_in_no_group_so_nothing_offers_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "groups.json"
            path.write_text(json.dumps({"groups": [{"en": "/a/", "es-419": "/es/a/", "zh-Hans": "/zh/a/"}]}), encoding="utf-8")
            found = languages.language_groups(path, {"en": self.reference, "es-419": dict(self.reference), "zh-Hans": {"a": "A"}})
        self.assertEqual(found, [{"en": "/a/", "es-419": "/es/a/"}])

    def test_the_shipped_languages_are_complete_and_each_names_itself(self):
        self.assertEqual(languages.complete_languages(), ["en", "es-419", "zh-Hans"])
        self.assertEqual(languages.missing_strings(languages.INTERFACE_STRINGS["zh-Hans"], languages.INTERFACE_STRINGS["en"]), [])

    def test_the_chrome_the_engine_writes_is_translated_and_the_pages_own_words_are_not(self):
        spanish = languages.INTERFACE_STRINGS["es-419"]
        page = '<a aria-label="Home">Skip to main content</a><p>By various bots · 13 November 2026</p><p>Home sweet home</p><script>"Home"</script>'
        self.assertEqual(languages.translate_chrome(page, spanish),
                         '<a aria-label="Inicio">Saltar al contenido principal</a><p>Por varios bots · 13 de noviembre de 2026</p><p>Home sweet home</p><script>"Home"</script>')

    def test_dates_use_the_languages_own_names_and_order(self):
        self.assertEqual(languages.localized_date(13, 11, 2026, languages.INTERFACE_STRINGS["zh-Hans"]), "2026年11月13日")
        self.assertEqual(languages.localized_date(1, 3, 2026, languages.INTERFACE_STRINGS["es-419"]), "1 de marzo de 2026")

    def test_the_concepts_page_of_a_language_is_found_as_the_primary_wiki_page(self):
        groups = [{"en": "/wiki/", "es-419": "/es/concepts/"}]
        self.assertEqual(languages.primary_path("/es/concepts/", groups, "en", PREFIXES), "/wiki/")
        self.assertEqual(languages.primary_path("/es/other/", groups, "en", PREFIXES), "/other/")

    def test_the_active_destination_is_found_from_the_unprefixed_address(self):
        self.assertEqual(languages.unprefixed_path("/es/articles/", PREFIXES), "/articles/")
        self.assertEqual(languages.unprefixed_path("/articles/", PREFIXES), "/articles/")


def reference_copy():
    return {"a": "A", "b": "B", "months": ["x", "y"], "sections": {"s": "S"}}


if __name__ == "__main__":
    unittest.main()
