import json
import re
import shutil
import struct
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
EXAMPLE_ASSET = "/assets/ads/papyrus-newsroom-rectangle.webp"  # a real file, so the example ads pass the check that an asset exists
PICTURE = {"src": EXAMPLE_ASSET, "alt": "Example Co: an example creative with some words", "width": 300, "height": 250}
BAND_IMAGES = {"wide": {**PICTURE, "width": 970}, "medium": {**PICTURE, "width": 728}, "narrow": PICTURE}
RESPONSIVE_IMAGES = {"wide": PICTURE, "narrow": PICTURE}
PICTURES_BY_UNIT = {"band": BAND_IMAGES, "rectangle": PICTURE, "half-page": {**PICTURE, "height": 600}, "card": RESPONSIVE_IMAGES,
                    "story": RESPONSIVE_IMAGES, "pullquote": RESPONSIVE_IMAGES, "aside": RESPONSIVE_IMAGES}


def sample_ad(**changes):
    ad = {"id": "example", "advertiser": "Example Co", "href": "https://example.test/?a=1&b=2", "images": PICTURES_BY_UNIT}
    ad.update(changes)
    return ad


def webp_size(path: Path) -> tuple[int, int]:
    """The pixel size of a lossless or lossy WebP file, read from its header."""
    data = path.read_bytes()
    kind = data[12:16]
    if kind == b"VP8L":
        bits = struct.unpack("<I", data[21:25])[0]
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if kind == b"VP8 ":
        return struct.unpack("<HH", data[26:30])[0] & 0x3FFF, struct.unpack("<HH", data[26:30])[1] & 0x3FFF
    raise AssertionError(f"{path.name} is not a WebP file this test can read")


def shipped_pictures(ad):
    for unit, images in ad["images"].items():
        for size, image in ([(None, images)] if unit in mom.AD_FIXED_SIZE_UNITS else images.items()):
            yield unit, size, image


class AdvertisementComponentTest(unittest.TestCase):
    def test_every_unit_says_advertisement_in_words_and_names_the_advertiser(self):
        for unit in mom.AD_UNIT_NAMES:
            markup = mom.advertisement(unit, sample_ad())
            self.assertIn("<b>Advertisement</b> · Example Co", markup, unit)

    def test_every_link_is_marked_sponsored_and_escaped(self):
        for unit in mom.AD_UNIT_NAMES:
            markup = mom.advertisement(unit, sample_ad())
            links = re.findall(r"<a [^>]*>", markup)
            self.assertEqual(len(links), 1, unit)
            self.assertIn('rel="sponsored noopener"', links[0], unit)
            self.assertIn("a=1&amp;b=2", links[0], unit)

    def test_every_unit_is_the_same_slot_around_the_advertisers_picture(self):
        for unit in mom.AD_UNIT_NAMES:
            markup = mom.advertisement(unit, sample_ad())
            self.assertTrue(markup.startswith(f'<aside class="mom-ad mom-ad-{unit}" aria-label="Advertisement"'), unit)
            self.assertIn('<div class="mom-ad-slot"><a rel="sponsored noopener"', markup, unit)
            self.assertEqual(markup.count("<img"), 1 if unit in mom.AD_FIXED_SIZE_UNITS else markup.count("<img"), unit)
            self.assertNotIn("style=", markup, unit)

    def test_the_site_draws_nothing_of_the_advertisers_words_only_the_picture_carries_them(self):
        markup = mom.advertisement("band", sample_ad(headline="Never drawn", body="Never drawn", cta="Never drawn"))
        self.assertNotIn("Never drawn", markup)
        self.assertIn('alt="Example Co: an example creative with some words"', markup)

    def test_a_unit_the_ad_has_no_picture_for_is_refused(self):
        with self.assertRaisesRegex(ValueError, "no picture for the rectangle"):
            mom.advertisement("rectangle", sample_ad(images={"band": BAND_IMAGES}))
        with self.assertRaisesRegex(ValueError, "unknown ad unit"):
            mom.advertisement("inline", sample_ad())

    def test_the_inline_sentence_is_not_a_unit(self):
        self.assertNotIn("inline", mom.AD_UNIT_NAMES)

    def test_a_band_offers_each_width_its_own_size(self):
        markup = mom.advertisement("band", sample_ad())
        self.assertIn('media="(min-width: 1042px)"', markup)
        self.assertIn('media="(min-width: 800px)"', markup)
        self.assertIn('width="300" height="250"', markup)

    def test_a_band_in_a_narrow_column_offers_only_its_smallest_picture(self):
        markup = mom.advertisement("band", sample_ad(), contained=True)
        self.assertNotIn("<source", markup)
        self.assertIn('width="300" height="250"', markup)

    def test_the_other_stretchy_units_offer_a_wide_picture_from_600_pixels(self):
        for unit in ("card", "story", "pullquote", "aside"):
            self.assertIn('media="(min-width: 600px)"', mom.advertisement(unit, sample_ad()), unit)

    def test_fixed_size_units_are_one_picture_with_no_sources(self):
        for unit in mom.AD_FIXED_SIZE_UNITS:
            markup = mom.advertisement(unit, sample_ad())
            self.assertNotIn("<picture", markup, unit)
            self.assertEqual(markup.count("<img"), 1, unit)

    def test_a_night_picture_is_drawn_beside_the_day_one_and_the_theme_shows_one(self):
        night = {**PICTURE, "src_dark": "/assets/ads/papyrus-newsroom-rectangle-night.webp"}
        markup = mom.advertisement("rectangle", sample_ad(images={"rectangle": night}))
        self.assertIn('<span class="mom-ad-day"><img src="/assets/ads/papyrus-newsroom-rectangle.webp"', markup)
        self.assertIn('<span class="mom-ad-night"><img src="/assets/ads/papyrus-newsroom-rectangle-night.webp"', markup)
        self.assertNotIn("mom-ad-night", mom.advertisement("rectangle", sample_ad()))


class AdvertisementValidationTest(unittest.TestCase):
    def assertRejected(self, expected, **changes):
        with self.assertRaisesRegex(ValueError, expected):
            mom.validate_advertisement(sample_ad(**changes))

    def test_a_good_ad_passes(self):
        mom.validate_advertisement(sample_ad())

    def test_missing_fields_are_named(self):
        for field in ("href", "advertiser", "images", "id"):
            self.assertRejected(field, **{field: ""})

    def test_unknown_units_are_rejected(self):
        self.assertRejected("unknown units", images={"skyscraper": PICTURE})
        self.assertRejected("unknown units", images={"inline": PICTURE})

    def test_only_https_or_site_paths_are_allowed(self):
        self.assertRejected("https address", href="http://example.test/")
        self.assertRejected("https address", href="javascript:alert(1)")
        mom.validate_advertisement(sample_ad(href="/about/"))

    def test_every_picture_needs_alt_text_and_its_size(self):
        self.assertRejected("alt", images={"rectangle": {**PICTURE, "alt": ""}})
        self.assertRejected("width", images={"rectangle": {**PICTURE, "width": 0}})
        self.assertRejected("height", images={"rectangle": {key: value for key, value in PICTURE.items() if key != "height"}})

    def test_alt_text_must_say_what_the_creative_says(self):
        self.assertRejected("alt text must say", images={"rectangle": {**PICTURE, "alt": "Example Co"}})
        self.assertRejected("alt text must say", images={"rectangle": {**PICTURE, "alt": "ad"}})

    def test_a_stretchy_unit_needs_its_narrow_picture_and_only_known_sizes(self):
        self.assertRejected("narrow", images={"band": {"wide": PICTURE}})
        self.assertRejected("narrow", images={"story": {"wide": PICTURE}})
        self.assertRejected("no sizes", images={"story": {"narrow": PICTURE, "medium": PICTURE}})

    def test_a_picture_is_a_file_under_the_ads_folder_that_exists_and_is_small(self):
        self.assertRejected("must be a", images={"rectangle": {**PICTURE, "src": "https://example.test/ad.webp"}})
        self.assertRejected("must be a", images={"rectangle": {**PICTURE, "src": "/assets/ads/ad.exe"}})
        self.assertRejected("must be a", images={"rectangle": {**PICTURE, "src": "/assets/other/ad.webp"}})
        self.assertRejected("is not in web/assets/ads", images={"rectangle": {**PICTURE, "src": "/assets/ads/nothing-here.webp"}})
        self.assertRejected("not in web/assets/ads", images={"rectangle": {**PICTURE, "src_dark": "/assets/ads/nothing-here.webp"}})

    def test_a_night_picture_is_for_every_size_of_a_unit_or_none(self):
        night = {**PICTURE, "src_dark": EXAMPLE_ASSET}
        self.assertRejected("Night picture", images={"story": {"wide": night, "narrow": PICTURE}})
        mom.validate_advertisement(sample_ad(images={"story": {"wide": night, "narrow": night}}))


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

    def test_every_house_ad_is_an_asset_for_every_unit_with_day_and_night_pictures(self):
        for ad in json.loads(ADS_FILE.read_text())["ads"]:
            self.assertEqual(mom.ad_units(ad), mom.AD_UNIT_NAMES, ad["id"])
            self.assertEqual(set(ad), {"id", "advertiser", "href", "images"}, "the site holds no copy, brand or template of an ad")
            for unit, size, image in shipped_pictures(ad):
                self.assertTrue(image.get("src_dark"), f"{ad['id']} {unit} {size} has a Night picture")

    def test_the_shipped_pictures_are_the_size_they_say_at_twice_the_pixels(self):
        for ad in json.loads(ADS_FILE.read_text())["ads"]:
            for unit, size, image in shipped_pictures(ad):
                for source in (image["src"], image["src_dark"]):
                    width, height = webp_size(REPOSITORY_ROOT / "web" / source.lstrip("/"))
                    self.assertEqual((width, height), (image["width"] * 2, height), f"{source} is twice its width")
                    self.assertAlmostEqual(height / 2, image["height"], delta=1, msg=f"{source} is twice its height")

    def test_the_standard_sizes_are_what_the_pictures_say(self):
        for ad in json.loads(ADS_FILE.read_text())["ads"]:
            images = ad["images"]
            self.assertEqual((images["rectangle"]["width"], images["half-page"]["width"]), (300, 300), ad["id"])
            self.assertEqual((images["rectangle"]["height"], images["half-page"]["height"]), (250, 600), ad["id"])
            for size, width in (("wide", 970), ("medium", 728), ("narrow", 300)):
                self.assertEqual(images["band"][size]["width"], width, ad["id"])
                self.assertAlmostEqual(images["band"][size]["height"], 250, delta=1, msg=ad["id"])

    def test_no_anthus_variant_sells_owning_code_or_an_aws_account(self):
        for ad in json.loads(ADS_FILE.read_text())["ads"]:
            if ad["advertiser"] != "Anthus AI Solutions":
                continue
            words = " ".join(image["alt"] for _, _, image in shipped_pictures(ad)).lower()
            for phrase in ("aws", "own the code", "yours to keep", "answers to your people"):
                self.assertNotIn(phrase, words, ad["id"])


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
        cards = re.findall(r'<(?:a|aside) [^>]*class="mom-(?:story-card|ad mom-ad-card)[^"]*"[^>]*>', grid)
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
                for link in re.findall(r"<a [^>]*>", element):
                    self.assertIn('rel="sponsored noopener"', link)

    def test_every_projected_ad_is_only_a_label_and_a_picture_in_a_slot_the_site_draws(self):
        for route in ("/", "/field-notes/", LONG_ARTICLE, "/wiki/durable-execution/"):
            for ad in re.findall(r"<aside [^>]*data-ad=.*?</aside>", page_text(self.out, route), re.S):
                self.assertIn('<div class="mom-ad-slot">', ad)
                self.assertIn("<img", ad)
                self.assertNotRegex(ad, r"<(svg|h[1-6]|button|blockquote|figure)\b|style=")
                self.assertNotIn("mom-ad-branded", ad)


class AdvertisingStyleTest(unittest.TestCase):
    def advertising_css(self):
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        return css[css.index("/* Advertisement:"):css.index("/* In an article's words */")]

    def test_the_stylesheet_reserves_the_standard_sizes_in_real_pixels_that_the_sites_scale_does_not_touch(self):
        self.assertIn("width: 225pt", self.advertising_css())

    def test_the_site_styles_the_slot_and_never_the_inside_of_a_creative(self):
        css = self.advertising_css()
        for forbidden in ("background", "color:", "font", "border-radius", "mom-ad-creative", "mom-ad-branded", "--brand"):
            self.assertNotIn(forbidden, re.sub(r"/\*.*?\*/", "", css, flags=re.S).replace("color: var(--ink-muted)", "").replace("color: var(--ink)", "").replace("font: 600 13px/1.4 var(--font-text)", "").replace("font-weight: 800", ""), forbidden)

    def test_no_article_rule_takes_away_the_asides_gutter(self):
        theme = (REPOSITORY_ROOT / "web" / "css-src" / "site-theme.src.css").read_text()
        self.assertNotRegex(theme, r"\.mom-article \.mom-ad \{[^}]*margin", "an article-wide ad margin overrides the aside's gutter")
        css = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text()
        aside_rule = re.search(r"\.mom-article \.mom-ad-aside \{([^}]*)\}", css)
        self.assertIsNotNone(aside_rule, "the aside's gutter is set for the article it sits in")
        self.assertIn("--mom-ad-aside-gutter", aside_rule.group(1))

    def test_a_picture_is_never_scaled_up_only_down_to_its_column(self):
        self.assertRegex(self.advertising_css(), r"\.mom-ad-slot img \{[^}]*max-width: 100%; height: auto")

    def test_nothing_in_an_ad_animates_or_sticks(self):
        for forbidden in ("animation", "transition", "position: sticky", "position: fixed"):
            self.assertNotIn(forbidden, self.advertising_css())


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

    def test_the_units_an_article_can_carry_are_the_band_and_the_in_content_units(self):
        units = {unit for number in range(200) for _, unit in hooks._article_ad_choices(self.Page(f"/articles/u{number}/"))}
        self.assertEqual(units, {"band", *mom.AD_IN_CONTENT_UNITS})


class InContentUnitTest(unittest.TestCase):
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
        for ad in json.loads(ADS_FILE.read_text())["ads"]:
            self.assertIn(f'data-ad="{ad["id"]}"', markup)
