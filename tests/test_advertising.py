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
        images = {"band": {"wide": PICTURE, "medium": {**PICTURE, "width": 728, "height": 250}, "narrow": {**PICTURE, "width": 300, "height": 250}}}
        markup = mom.advertisement("band", sample_ad(images=images))
        self.assertIn('media="(min-width: 1042px)"', markup)
        self.assertIn('media="(min-width: 800px)"', markup)
        self.assertIn('width="300" height="250"', markup)

    def test_a_band_in_a_narrow_column_offers_only_its_smallest_picture(self):
        images = {"band": {"wide": PICTURE, "medium": {**PICTURE, "width": 728, "height": 250}, "narrow": {**PICTURE, "width": 300, "height": 250}}}
        markup = mom.advertisement("band", sample_ad(images=images), contained=True)
        self.assertNotIn("<source", markup)
        self.assertIn('width="300" height="250"', markup)

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
        for variant in ("anthus-brought-to-you-by", "anthus-busywork", "anthus-like-this-site"):
            self.assertIn(variant, ids)

    def test_no_anthus_variant_sells_owning_code_or_an_aws_account(self):
        for ad in json.loads(ADS_FILE.read_text())["ads"]:
            if ad["advertiser"] != "Anthus AI Solutions":
                continue
            words = json.dumps({key: ad.get(key) for key in ("headline", "body", "cta", "points", "unit_copy")}).lower()
            for phrase in ("aws", "own the code", "yours to keep", "answers to your people"):
                self.assertNotIn(phrase, words, ad["id"])

    def test_every_house_ad_wears_its_own_brand(self):
        for ad in json.loads(ADS_FILE.read_text())["ads"]:
            self.assertTrue(ad.get("brand"), ad["id"])
            self.assertIn(ad["brand"].get("face"), mom.AD_BRAND_FACES, ad["id"])


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

    def test_the_home_page_has_one_band_at_the_end_after_the_findings(self):
        home = page_text(self.out, "/")
        self.assertEqual(self.placements("/"), ["home-band"])
        self.assertGreater(home.index('data-ad-placement="home-band"'), home.index("rh-findings"))

    def test_the_home_band_is_not_next_to_the_animated_brand_band(self):
        home = page_text(self.out, "/")
        advertisement_at = home.index('data-ad-placement="home-band"')
        self.assertEqual(home.count("mom-band-machine"), home.count("mom-band-machine", 0, advertisement_at))

    def test_a_section_page_has_a_card_in_the_grid_and_a_band_at_the_end(self):
        self.assertEqual(self.placements("/field-notes/"), ["listing-card", "listing-end"])

    def test_the_card_is_the_fifth_card_in_the_grid(self):
        grid = page_text(self.out, "/field-notes/").split('<div class="mom-story-grid">')[1]
        cards = re.findall(r'<a [^>]*class="mom-story-card[^"]*"', grid)
        self.assertIn("data-ad=", cards[4])
        self.assertEqual(sum("data-ad=" in card for card in cards), 1)

    def test_a_long_article_has_exactly_one_ad_inside_the_words_or_at_the_end(self):
        page = page_text(self.out, LONG_ARTICLE)
        self.assertEqual(len(re.findall(r'data-ad-placement="article-[a-z]+"', page)), 1)

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
        for declaration in ("min-height: 187.5pt", "width: 225pt", "height: 187.5pt", "height: 450pt"):
            self.assertIn(declaration, css)

    def test_a_band_keeps_its_250_pixel_height_at_every_width(self):
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        advertising_css = css[css.index("/* Advertisement:"):]
        self.assertNotRegex(advertising_css, r"\.mom-ad-band \.mom-ad-(creative|slot) \{[^}]*(?<!min-)height: (67\.5|75)pt")
        for query in re.findall(r"@media \(max-width: [0-9]+pt\) \{.*?\n\}", advertising_css, re.S):
            self.assertNotRegex(query, r"\.mom-ad-band \.mom-ad-creative \{[^}]*min-height: (?!187\.5pt)")

    def test_ads_are_inverted_ink_never_the_publications_navy(self):
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        creative_rule = re.search(r"\.mom-ad-creative \{([^}]*)\}", css).group(1)
        self.assertIn("background: var(--ink)", creative_rule)
        advertising_css = css[css.index("/* Advertisement:"):]
        self.assertNotIn("--brand", advertising_css)

    def test_no_article_rule_takes_away_the_asides_gutter(self):
        theme = (REPOSITORY_ROOT / "web" / "css-src" / "site-theme.src.css").read_text()
        self.assertNotRegex(theme, r"\.mom-article \.mom-ad \{[^}]*margin", "an article-wide ad margin overrides the aside's gutter")
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        aside_rule = re.search(r"\.mom-article \.mom-ad-aside \{([^}]*)\}", css)
        self.assertIsNotNone(aside_rule, "the aside's gutter is set for the article it sits in")
        self.assertIn("--mom-ad-aside-gutter", aside_rule.group(1))

    def test_nothing_in_an_ad_animates_or_sticks(self):
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        advertising_css = css[css.index("/* Advertisement:"):]
        for forbidden in ("animation", "transition", "position: sticky", "position: fixed"):
            self.assertNotIn(forbidden, advertising_css)


if __name__ == "__main__":
    unittest.main()


PAPYRUS_BRAND = {
    "name": "Papyrus", "mark": "papyrus-plant", "face": "serif", "art": "papyrus-sun",
    "ground": {"day": "#1b1d20", "night": "#f4f1ea"}, "ink": {"day": "#f4f1ea", "night": "#1b1d20"},
    "accent": {"day": "#e2725f", "night": "#a3271f"},
}
ANTHUS_BRAND = {
    "name": "Anthus AI Solutions", "wordmark": "anthus-lockup", "face": "pixel", "art": "anthus-pixels",
    "ground": {"day": "#150f20", "night": "#ff57b4"}, "ink": {"day": "#f3eef8", "night": "#150f20"},
    "accent": {"day": "#ff57b4", "night": "#150f20"},
}


class AdvertiserBrandTest(unittest.TestCase):
    def test_a_branded_band_shows_the_advertisers_name_and_mark_and_none_of_the_sites_shapes(self):
        markup = mom.advertisement("band", sample_ad(brand=PAPYRUS_BRAND))
        self.assertIn('class="mom-ad-brand-name">Papyrus<', markup)
        self.assertIn("mom-ad-mark-papyrus-plant", markup)
        self.assertNotIn("mom-ad-disc", markup)
        self.assertNotIn("mom-ad-slab", markup)

    def test_an_unbranded_ad_keeps_the_sites_shapes(self):
        markup = mom.advertisement("band", sample_ad())
        self.assertIn("mom-ad-disc", markup)
        self.assertNotIn("mom-ad-branded", markup)

    def test_the_brands_colors_for_both_themes_travel_with_the_ad(self):
        markup = mom.advertisement("band", sample_ad(brand=PAPYRUS_BRAND))
        for custom_property in ("--ad-ground-day:#1b1d20", "--ad-ground-night:#f4f1ea", "--ad-ink-day:#f4f1ea", "--ad-ink-night:#1b1d20",
                                "--ad-accent-day:#e2725f", "--ad-accent-night:#a3271f"):
            self.assertIn(custom_property, markup)

    def test_a_brand_whose_colors_cannot_be_read_fails_the_build(self):
        weak = {**PAPYRUS_BRAND, "ink": {"day": "#2a2e33", "night": "#1b1d20"}}
        with self.assertRaisesRegex(ValueError, "contrast"):
            mom.validate_advertisement(sample_ad(brand=weak))

    def test_a_brand_needs_its_colors_as_hex_for_day_and_night(self):
        with self.assertRaisesRegex(ValueError, "#rrggbb"):
            mom.validate_advertisement(sample_ad(brand={**PAPYRUS_BRAND, "ground": {"day": "navy"}}))

    def test_a_brand_names_a_known_mark(self):
        with self.assertRaisesRegex(ValueError, "unknown brand mark"):
            mom.validate_advertisement(sample_ad(brand={**PAPYRUS_BRAND, "mark": "dragon"}))

    def test_the_shipped_papyrus_ad_is_branded_as_papyrus(self):
        ad = json.loads(ADS_FILE.read_text())["ads"][0]
        self.assertEqual(ad["brand"]["name"], "Papyrus")
        self.assertEqual(ad["brand"]["mark"], "papyrus-plant")
        mom.validate_advertisement(ad)

    def test_the_shipped_anthus_ad_is_branded_with_its_lockup(self):
        variants = [ad for ad in json.loads(ADS_FILE.read_text())["ads"] if ad["advertiser"] == "Anthus AI Solutions"]
        self.assertEqual(len(variants), 3)
        for ad in variants:
            self.assertEqual(ad["brand"]["wordmark"], "anthus-lockup")
            mom.validate_advertisement(ad)

    def test_an_accent_that_cannot_be_read_on_the_ground_fails_the_build(self):
        with self.assertRaisesRegex(ValueError, "accent"):
            mom.validate_advertisement(sample_ad(brand={**PAPYRUS_BRAND, "accent": {"day": "#3a3d42", "night": "#a3271f"}}))

    def test_a_brand_names_a_known_face_wordmark_and_art(self):
        for field, expected in (("face", "face"), ("wordmark", "wordmark"), ("art", "art")):
            with self.assertRaisesRegex(ValueError, expected):
                mom.validate_advertisement(sample_ad(brand={**PAPYRUS_BRAND, field: "dragon"}))

    def test_a_wordmark_takes_the_place_of_the_mark_and_name_and_still_names_the_advertiser(self):
        markup = mom.advertisement("band", sample_ad(brand=ANTHUS_BRAND))
        self.assertIn("mom-ad-wordmark-anthus-lockup", markup)
        self.assertIn('aria-label="Anthus AI Solutions"', markup)
        self.assertIn("mom-ad-face-pixel", markup)

    def test_a_brands_art_is_drawn_behind_its_creative(self):
        self.assertIn("mom-ad-art-papyrus-sun", mom.advertisement("band", sample_ad(brand=PAPYRUS_BRAND)))
        self.assertIn("mom-ad-art-anthus-pixels", mom.advertisement("rectangle", sample_ad(brand=ANTHUS_BRAND)))

    def test_a_branded_card_shows_the_brands_art_in_place_of_placeholder_art(self):
        markup = mom.advertisement("card", sample_ad(brand=PAPYRUS_BRAND))
        self.assertIn("mom-ad-card-art", markup)
        self.assertIn("mom-ad-art-papyrus-sun", markup)
        self.assertNotIn("mom-art ", markup)

    def test_the_branded_aside_wears_the_brands_colors(self):
        markup = mom.advertisement("aside", sample_ad(brand=ANTHUS_BRAND))
        self.assertIn("mom-ad-branded", markup)
        self.assertIn("--ad-ground-day:#150f20", markup)


class AdvertiserTurnsTest(unittest.TestCase):
    class Page:
        def __init__(self, path):
            self.path = path

    def test_variants_of_one_advertiser_share_one_turn(self):
        from collections import Counter
        ads = [sample_ad(id="a", advertiser="A")] + [sample_ad(id=f"b{number}", advertiser="B") for number in range(3)]
        groups = hooks._advertisers_with_variants(ads)
        self.assertEqual([[ad["id"] for ad in group] for group in groups], [["a"], ["b0", "b1", "b2"]])
        turns = Counter(hooks._choose_by_path(self.Page(f"/p{number}/"), groups)[0]["advertiser"] for number in range(400))
        self.assertLess(abs(turns["A"] - turns["B"]), 60)

    def test_an_articles_ad_comes_from_one_advertiser_and_each_advertiser_gets_articles(self):
        from collections import Counter
        advertisers = Counter()
        for number in range(400):
            choices = hooks._article_ad_choices(self.Page(f"/articles/a{number}/"))
            self.assertEqual(len({ad["id"] for ad, _ in choices}), 1)
            advertisers[choices[0][0]["advertiser"]] += 1
        self.assertEqual(set(advertisers), {"Papyrus", "Anthus AI Solutions"})
        self.assertLess(abs(advertisers["Papyrus"] - advertisers["Anthus AI Solutions"]), 80)


class HeadlineEmphasisTest(unittest.TestCase):
    def test_words_between_asterisks_are_emphasized_and_escaped(self):
        markup = mom.advertisement("band", sample_ad(headline="This is *literally* <true>"))
        self.assertIn("This is <em>literally</em> &lt;true&gt;", markup)
        self.assertNotIn("*", re.sub(r"<svg.*?</svg>", "", markup))

    def test_the_card_and_the_pull_quote_show_the_emphasis_too(self):
        for unit in ("card", "pullquote", "aside", "story"):
            self.assertIn("<em>literally</em>", mom.advertisement(unit, sample_ad(headline="It *literally* works")), unit)

    def test_the_limit_counts_what_a_reader_sees(self):
        mom.validate_advertisement(sample_ad(headline="*" + "x" * 60 + "*"))
        with self.assertRaisesRegex(ValueError, "limit"):
            mom.validate_advertisement(sample_ad(headline="*" + "x" * 61 + "*"))


class InContentUnitTest(unittest.TestCase):
    def test_the_inline_unit_is_one_sentence_with_a_sponsored_link_and_no_box(self):
        markup = mom.advertisement("inline", sample_ad(body="Built with Example."))
        self.assertIn("Advertisement · Example Co", markup)
        self.assertIn("Built with Example.", markup)
        self.assertNotIn("mom-ad-creative", markup)

    def test_the_pull_quote_unit_uses_the_stories_own_quote_style(self):
        markup = mom.advertisement("pullquote", sample_ad(headline="A bold claim"))
        self.assertIn('class="mom-pull-quote mom-ad', markup)
        self.assertIn("A bold claim", markup)
        self.assertIn("Advertisement · Example Co", markup)

    def test_the_aside_unit_carries_a_headline_and_a_sentence(self):
        markup = mom.advertisement("aside", sample_ad(headline="Aside words", body="Aside sentence."))
        self.assertIn("Aside words", markup)
        self.assertIn("Aside sentence.", markup)

    def test_every_in_content_unit_has_a_place_to_go(self):
        self.assertEqual(set(mom.AD_IN_CONTENT_UNITS), set(hooks.IN_CONTENT_AD_AFTER_PARAGRAPH))

    def test_an_in_content_ad_lands_among_the_paragraphs_of_a_long_article(self):
        class Page:
            path = "article-with-eight-paragraphs"
        body = "".join(f"<p>Paragraph {number}.</p>" for number in range(1, 9))
        seen = set()
        for suffix in range(40):
            Page.path = f"article-{suffix}"
            with_ad, closing = hooks._article_ad(Page, body)
            placements = re.findall(r'data-ad-placement="([a-z-]+)"', with_ad + closing)
            self.assertEqual(len(placements), 1)
            seen.add(placements[0])
        self.assertGreater(len(seen), 2)

    def test_a_story_too_short_for_an_in_content_ad_gets_the_closing_band(self):
        class Page:
            path = "x"
        body = "".join(f"<p>Paragraph {number}.</p>" for number in range(1, 4))
        for suffix in range(40):
            Page.path = f"short-{suffix}"
            with_ad, closing = hooks._article_ad(Page, body)
            self.assertEqual(with_ad, body)
            self.assertIn('data-ad-placement="article-end"', closing)

    def test_the_component_gallery_shows_every_unit_of_every_ad(self):
        markup = "".join(hooks._gallery_advertisements())
        for unit in mom.AD_UNIT_NAMES:
            self.assertIn(f'data-ad-unit="{unit}"', markup)
