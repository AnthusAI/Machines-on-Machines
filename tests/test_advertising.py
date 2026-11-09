import copy
import json
import re
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))

import hooks  # noqa: E402
import mom_components as mom  # noqa: E402
from projection_support import REPOSITORY_ROOT, page_text, project_to_temporary_directory  # noqa: E402

ADS_FILE = REPOSITORY_ROOT / "web" / "ads.json"
LONG_ARTICLE = "/field-notes/durable-execution-for-agents/"
SHORT_ARTICLE = "/field-notes/a-team-byline-and-no-picture/"
PICTURE = {"src": "/assets/ads/x.png", "alt": "An example", "width": 970, "height": 250}


def sample_ad(**changes):
    ad = {
        "id": "example", "advertiser": "Example Co", "units": list(mom.AD_UNIT_NAMES), "href": "https://example.test/?a=1&b=2",
        "headline": "A short headline", "body": "One sentence.", "cta": "Go now",
    }
    ad.update(changes)
    return ad


class AdvertisementComponentTest(unittest.TestCase):
    def test_every_unit_says_advertisement_in_words_and_names_the_advertiser(self):
        for unit in mom.AD_UNIT_NAMES:
            markup = mom.advertisement(unit, sample_ad())
            self.assertIn("Advertisement", markup, unit)
            self.assertIn("Example Co", markup, unit)

    def test_every_link_is_marked_sponsored_and_escaped(self):
        for unit in mom.AD_UNIT_NAMES:
            markup = mom.advertisement(unit, sample_ad())
            links = re.findall(r"<a [^>]*>", markup)
            self.assertTrue(links, unit)
            for link in links:
                self.assertIn('rel="sponsored noopener"', link, unit)
                self.assertIn("a=1&amp;b=2", link, unit)

    def test_the_card_is_a_story_card_and_the_others_are_asides(self):
        self.assertIn("mom-story-card", mom.advertisement("card", sample_ad()))
        self.assertTrue(mom.advertisement("band", sample_ad()).startswith('<aside class="mom-ad mom-ad-band'))

    def test_the_card_draws_placeholder_art_when_the_ad_has_no_picture(self):
        self.assertIn("mom-art ", mom.advertisement("card", sample_ad()))
        self.assertNotIn("<img", mom.advertisement("card", sample_ad()))

    def test_the_half_page_names_who_does_each_step(self):
        markup = mom.advertisement("half-page", sample_ad(points=[{"by": "machine", "text": "Find"}, {"by": "human", "text": "Approve"}]))
        self.assertIn("Machines", markup)
        self.assertIn("People", markup)

    def test_a_band_with_pictures_offers_each_width_its_own_size(self):
        images = {"band": {"wide": PICTURE, "medium": {**PICTURE, "width": 728, "height": 90}, "narrow": {**PICTURE, "width": 320, "height": 100}}}
        markup = mom.advertisement("band", sample_ad(images=images))
        self.assertIn('media="(min-width: 1042px)"', markup)
        self.assertIn('media="(min-width: 800px)"', markup)
        self.assertIn('width="320" height="100"', markup)

    def test_a_band_in_a_narrow_column_offers_only_its_smallest_picture(self):
        images = {"band": {"wide": PICTURE, "medium": {**PICTURE, "width": 728, "height": 90}, "narrow": {**PICTURE, "width": 320, "height": 100}}}
        markup = mom.advertisement("band", sample_ad(images=images), contained=True)
        self.assertNotIn("<source", markup)
        self.assertIn('width="320" height="100"', markup)

    def test_a_unit_can_carry_its_own_copy(self):
        ad = sample_ad(unit_copy={"story": {"headline": "Story words"}})
        self.assertIn("Story words", mom.advertisement("story", ad))
        self.assertNotIn("Story words", mom.advertisement("band", ad))

    def test_a_unit_without_its_own_pictures_uses_the_house_creative(self):
        markup = mom.advertisement("rectangle", sample_ad(images={"band": {"narrow": PICTURE}}))
        self.assertIn("mom-ad-creative", markup)
        self.assertNotIn("<picture", markup)


class AdvertisementValidationTest(unittest.TestCase):
    def assertRejected(self, expected, **changes):
        with self.assertRaisesRegex(ValueError, expected):
            mom.validate_advertisement(sample_ad(**changes))

    def test_a_good_ad_passes(self):
        mom.validate_advertisement(sample_ad())

    def test_missing_fields_are_named(self):
        for field in ("headline", "body", "cta", "href", "advertiser", "units"):
            self.assertRejected(field, **{field: ""})

    def test_unknown_units_are_rejected(self):
        self.assertRejected("unknown units", units=["skyscraper"])

    def test_a_long_headline_is_rejected(self):
        self.assertRejected("limit is 60", headline="x" * 61)

    def test_only_https_or_site_paths_are_allowed(self):
        self.assertRejected("https address", href="http://example.test/")
        self.assertRejected("https address", href="javascript:alert(1)")
        mom.validate_advertisement(sample_ad(href="/about/"))

    def test_every_picture_needs_alt_text_and_its_size(self):
        self.assertRejected("alt", images={"rectangle": {**PICTURE, "alt": ""}})
        self.assertRejected("narrow", images={"band": {"wide": PICTURE}})


class AdvertisementFileTest(unittest.TestCase):
    def test_the_ads_in_the_repository_are_valid_and_the_house_ad_is_papyrus(self):
        document = json.loads(ADS_FILE.read_text())
        ids = [ad["id"] for ad in document["ads"]]
        self.assertEqual(len(ids), len(set(ids)))
        for ad in document["ads"]:
            mom.validate_advertisement(ad)
        self.assertIn("papyrus-newsroom", ids)


class StoryPlacementTest(unittest.TestCase):
    def paragraphs(self, count):
        return "".join(f"<p>Paragraph {number}.</p>\n" for number in range(1, count + 1))

    def test_the_story_ad_follows_the_fourth_paragraph_of_a_long_story(self):
        html, total = hooks._after_paragraph(self.paragraphs(8), 4, "<AD>")
        self.assertEqual(total, 8)
        self.assertLess(html.index("Paragraph 4."), html.index("<AD>"))
        self.assertLess(html.index("<AD>"), html.index("Paragraph 5."))

    def test_a_short_story_gets_no_story_ad_because_nothing_would_follow_it(self):
        html, total = hooks._after_paragraph(self.paragraphs(6), 4, "<AD>")
        self.assertEqual((html, total), (self.paragraphs(6), 6))

    def test_paragraphs_inside_quotes_and_lists_do_not_count(self):
        before = "<p>First.</p><p>Second.</p>"
        inside = "<blockquote><p>Quoted one.</p><p>Quoted two.</p></blockquote><ul><li><p>Item.</p></li></ul>"
        after = "<p>Third.</p><p>Fourth.</p><p>Fifth.</p><p>Sixth.</p><p>Seventh.</p><p>Eighth.</p>"
        html, total = hooks._after_paragraph(f'<article class="markus-document">{before}{inside}{after}</article>', 4, "<AD>")
        self.assertEqual(total, 8)
        self.assertEqual(html.count("<AD>"), 1)
        self.assertLess(html.index("Fourth."), html.index("<AD>"))
        self.assertLess(html.index("<AD>"), html.index("Fifth."))


class ProjectedPlacementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = project_to_temporary_directory("mom-ads-")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def placements(self, route):
        return sorted(set(re.findall(r'data-ad-placement="([a-z-]+)"', page_text(self.out, route))))

    def test_the_home_page_has_one_band_after_the_latest_posts(self):
        home = page_text(self.out, "/")
        self.assertEqual(self.placements("/"), ["home-band"])
        self.assertGreater(home.index('data-ad-placement="home-band"'), home.index('id="mom-latest-posts"'))
        self.assertLess(home.index('data-ad-placement="home-band"'), home.index("rh-findings"))

    def test_a_section_page_has_a_card_in_the_grid_and_a_band_at_the_end(self):
        self.assertEqual(self.placements("/field-notes/"), ["listing-card", "listing-end"])

    def test_the_card_is_the_fifth_card_in_the_grid(self):
        grid = page_text(self.out, "/field-notes/").split('<div class="mom-story-grid">')[1]
        cards = re.findall(r'<a [^>]*class="mom-story-card[^"]*"', grid)
        self.assertIn("data-ad=", cards[4])
        self.assertEqual(sum("data-ad=" in card for card in cards), 1)

    def test_a_long_article_has_one_ad_the_closing_band(self):
        self.assertEqual(self.placements(LONG_ARTICLE), ["article-end"])

    def test_a_short_article_has_only_the_closing_band(self):
        self.assertEqual(self.placements(SHORT_ARTICLE), ["article-end"])

    def test_an_article_band_never_offers_a_picture_wider_than_its_column(self):
        self.assertNotIn("<source", page_text(self.out, LONG_ARTICLE))

    def test_a_wiki_term_has_one_rail_placement_drawn_as_two_sizes(self):
        wiki = page_text(self.out, "/wiki/durable-execution/")
        self.assertEqual(self.placements("/wiki/durable-execution/"), ["wiki-rail"])
        self.assertIn('data-ad-unit="half-page"', wiki)
        self.assertIn('data-ad-unit="rectangle"', wiki)

    def test_no_page_has_more_than_two_placements(self):
        for page in self.out.rglob("index.html"):
            if page.relative_to(self.out).parts[0] == "design":
                continue  # the component gallery shows every unit on purpose
            placements = set(re.findall(r'data-ad-placement="([a-z-]+)"', page.read_text(encoding="utf-8")))
            self.assertLessEqual(len(placements), 2, str(page.relative_to(self.out)))

    def test_the_findings_conversations_and_wiki_index_carry_no_ads(self):
        for route in ("/findings/", "/conversations/", "/wiki/"):
            self.assertEqual(self.placements(route), [], route)

    def test_an_ad_is_never_in_the_spine_the_nav_or_a_margin_note(self):
        for route in ("/", LONG_ARTICLE, "/wiki/durable-execution/"):
            page = page_text(self.out, route)
            for container in re.findall(r'<(?:nav|header)[^>]*class="mom-(?:spine|masthead)".*?</(?:nav|header)>', page, re.S):
                self.assertNotIn("data-ad=", container)

    def test_the_same_page_always_shows_the_same_ad(self):
        first = project_to_temporary_directory("mom-ads-again-")
        try:
            self.assertEqual(page_text(first, LONG_ARTICLE), page_text(self.out, LONG_ARTICLE))
        finally:
            shutil.rmtree(first, ignore_errors=True)

    def test_every_projected_ad_says_advertisement_and_marks_its_links(self):
        for route in ("/", "/field-notes/", LONG_ARTICLE, "/wiki/durable-execution/"):
            page = page_text(self.out, route)
            for element in re.findall(r"<(?:aside|a) [^>]*data-ad=.*?(?:</aside>|</a>)", page, re.S):
                self.assertIn("Advertisement", element)
                self.assertNotIn('<a class="mom-ad-button" href', element)
            self.assertNotRegex(page, r'<a class="mom-ad-button" href')


class AdvertisingStyleTest(unittest.TestCase):
    def test_the_stylesheet_reserves_the_standard_sizes_in_real_pixels_that_the_sites_scale_does_not_touch(self):
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        for declaration in ("min-height: 187.5pt", "height: 67.5pt", "height: 75pt", "width: 225pt", "height: 187.5pt", "height: 450pt"):
            self.assertIn(declaration, css)

    def test_ads_are_inverted_ink_never_the_publications_navy(self):
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        creative_rule = re.search(r"\.mom-ad-creative \{([^}]*)\}", css).group(1)
        self.assertIn("background: var(--ink)", creative_rule)
        advertising_css = css[css.index("/* Advertisement:"):]
        self.assertNotIn("--brand", advertising_css)

    def test_nothing_in_an_ad_animates_or_sticks(self):
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        advertising_css = css[css.index("/* Advertisement:"):]
        for forbidden in ("animation", "transition", "position: sticky", "position: fixed"):
            self.assertNotIn(forbidden, advertising_css)


if __name__ == "__main__":
    unittest.main()
