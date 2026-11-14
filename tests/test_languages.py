import json
import re
import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

import languages  # noqa: E402
import mom_components as mom  # noqa: E402

# What Papyrus hands a page (`page.alternates`): the page in every public language it exists in, itself included, primary first, each named in its own language.
ALTERNATES = [{"tag": "en", "name": "English", "url": "/articles/a/"}, {"tag": "es-419", "name": "Español", "url": "/es/articles/a/"},
              {"tag": "zh-Hans", "name": "中文", "url": "/zh/articles/a/"}]
STRINGS = languages.interface_strings()


class StringsTests(unittest.TestCase):
    def test_the_strings_are_one_flat_file_per_language_and_every_language_has_every_key_of_the_primary(self):
        self.assertEqual(sorted(STRINGS), ["en", "es-419", "zh-Hans"])
        for tag, strings in STRINGS.items():
            self.assertTrue(all(isinstance(key, str) and isinstance(value, str) and value for key, value in strings.items()), tag)
            self.assertEqual(set(strings), set(STRINGS["en"]), tag)

    def test_language_names_are_their_own_and_never_flags(self):
        for strings in STRINGS.values():
            self.assertFalse(re.search("[\U0001F1E6-\U0001F1FF]", strings["language.name"]))
        self.assertEqual({tag: strings["language.name"] for tag, strings in STRINGS.items()}, {"en": "English", "es-419": "Español", "zh-Hans": "中文"})

    def test_the_banner_words_have_their_seconds(self):
        for tag, strings in STRINGS.items():
            self.assertIn("{seconds}", strings["countdown"], tag)
            self.assertIn("{seconds}", strings["announce"], tag)
            self.assertIn("{page}", strings["listing.pageSuffix"], tag)

    def test_the_banner_is_given_the_words_of_every_language_the_page_exists_in_and_no_other(self):
        found = languages.strings_for(ALTERNATES[:2])
        self.assertEqual(sorted(found), ["en", "es-419"])
        self.assertEqual(sorted(found["en"]), sorted(languages.BANNER_KEYS))

    def test_twelve_month_names_in_every_language(self):
        for strings in STRINGS.values():
            self.assertEqual(len(languages.month_names(strings)), 12)


class ComponentTests(unittest.TestCase):
    alternates = ALTERNATES

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


ICON = '<svg class="mom-icon" data-icon="languages"></svg>'
# Papyrus's link map: `{page path: {tag: path}}` for every page that exists in more than one language; `page.link_in_language` answers from it.
LINK_MAP = {
    "/articles/a/": {"en": "/articles/a/", "es-419": "/es/articles/a/", "zh-Hans": "/zh/articles/a/"},
    "/es/articles/a/": {"en": "/articles/a/", "es-419": "/es/articles/a/", "zh-Hans": "/zh/articles/a/"},
    "/articles/b/": {"en": "/articles/b/", "es-419": "/es/articles/b/"},
    "/": {"en": "/", "es-419": "/es/", "zh-Hans": "/zh/"},
}


def link_in_language(language):
    """The page's `page.link_in_language` (papyrus_content.projection.standard.page.StandardPage), for a page in `language`."""
    def found(path):
        links = LINK_MAP.get(path)
        if links is None:
            return path, not path.startswith(f"/{language.split('-')[0]}/")
        return (links[language], False) if language in links else (path, True)
    return found


def localize(html, language="es-419", in_body=True):
    """The links in `html`, as found in the page's own words (inside <main>) unless `in_body` is False (navigation, menu and footer)."""
    page = f"<main>{html}</main>" if in_body else html
    found = languages.localize_links(page, language, "en", link_in_language(language), STRINGS[language], "https://example.test", ICON)
    return found[len("<main>"):-len("</main>")] if in_body else found


class LinkLocalizationTests(unittest.TestCase):
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

    def test_a_link_to_the_original_is_marked_whatever_localizations_it_has(self):
        found = localize('<a href="original:/articles/a/">A</a>')
        self.assertIn('href="/articles/a/"', found)
        self.assertIn('hreflang="en"', found)

    def test_the_rule_is_one_function_of_the_pages_link_in_language(self):
        here = link_in_language("es-419")
        self.assertEqual(languages.localized_link_target("/articles/a/", here), ("/es/articles/a/", False))
        self.assertEqual(languages.localized_link_target("/articles/z/", here), ("/articles/z/", True))
        self.assertEqual(languages.localized_link_target("/feed.xml", here), ("/feed.xml", False))


CHINESE = "/zh/articles/如何引导一篇报道/"
CHINESE_ENCODED = "/zh/articles/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/"


class UnicodeAddressTests(unittest.TestCase):
    """Papyrus keys its link map by the percent-encoded address; a link in a page may be written either way."""

    link_map = {"/articles/a/": {"en": "/articles/a/", "zh-Hans": CHINESE_ENCODED}, CHINESE_ENCODED: {"en": "/articles/a/", "zh-Hans": CHINESE_ENCODED}}

    def found(self, path):
        links = self.link_map.get(path)
        return (links["zh-Hans"], False) if links else (path, True)

    def localize(self, href):
        return languages.localize_links(f'<a href="{href}">x</a>', "zh-Hans", "en", self.found, STRINGS["zh-Hans"])

    def test_a_link_to_the_page_goes_to_the_encoded_address(self):
        self.assertIn(f'href="{CHINESE_ENCODED}"', self.localize("/articles/a/"))

    def test_a_link_to_the_localization_in_either_form_is_left_at_that_page(self):
        for href in (CHINESE, CHINESE_ENCODED):
            self.assertEqual(self.localize(href), f'<a href="{href}">x</a>')

    def test_encoded_path_round_trips(self):
        self.assertEqual(languages.encoded_path(CHINESE), CHINESE_ENCODED)
        self.assertEqual(languages.normalize_path(CHINESE_ENCODED), CHINESE)


class ChromeTests(unittest.TestCase):
    def test_the_chrome_the_engine_writes_is_translated_and_the_pages_own_words_are_not(self):
        page = '<a aria-label="Home">Skip to main content</a><p>By various bots · 13 November 2026</p><p>Home sweet home</p><script>"Home"</script>'
        self.assertEqual(languages.translate_chrome(page, STRINGS["es-419"]),
                         '<a aria-label="Inicio">Saltar al contenido principal</a><p>Por varios bots · 13 de noviembre de 2026</p><p>Home sweet home</p><script>"Home"</script>')

    def test_dates_use_the_languages_own_names_and_order(self):
        self.assertEqual(languages.localized_date(13, 11, 2026, STRINGS["zh-Hans"]), "2026年11月13日")
        self.assertEqual(languages.localized_date(1, 3, 2026, STRINGS["es-419"]), "1 de marzo de 2026")


if __name__ == "__main__":
    unittest.main()
