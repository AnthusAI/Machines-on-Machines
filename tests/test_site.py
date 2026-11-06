import json
import re
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from projection_support import REPOSITORY_ROOT, page_text, project_to_temporary_directory  # noqa: E402

ARTICLE = "/field-notes/the-agents-are-writing-the-benchmarks-now/"
NO_IMAGE_ARTICLE = "/field-notes/a-team-byline-and-no-picture/"
HUMAN_ARTICLE = "/field-notes/who-owns-an-agents-mistakes/"
PAPYRUS_VERSION = "5.91.0"


def npm_version(pin):
    """PyPI spells the npm prerelease 5.69.0 as 5.69.0.dev2; compare in npm's spelling."""
    return re.sub(r"\.dev(\d+)$", r"-next.\1", pin)


class RepositoryContractTest(unittest.TestCase):
    def test_papyrus_is_pinned_in_all_four_places(self):
        pinned = {
            "package.json": json.loads((REPOSITORY_ROOT / "package.json").read_text())["dependencies"]["@anthusai/papyrus"],
            "infra/package.json": json.loads((REPOSITORY_ROOT / "infra" / "package.json").read_text())["dependencies"]["@anthusai/papyrus"],
            "infra/site.json": json.loads((REPOSITORY_ROOT / "infra" / "site.json").read_text())["papyrusVersion"],
            "requirements-publication.txt": npm_version((REPOSITORY_ROOT / "requirements-publication.txt").read_text().strip().split("==")[-1]),
        }
        self.assertEqual(set(pinned.values()), {PAPYRUS_VERSION}, pinned)

    def test_posts_and_articles_each_have_an_address(self):
        projection = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())
        self.assertEqual(projection["storyTypes"], {"default": "post", "types": ["post", "article"]})
        self.assertEqual(projection["urls"]["types"]["post"]["base"], "posts")
        self.assertEqual(projection["urls"]["types"]["article"]["base"], "articles")

    def test_the_site_identity_is_consistent(self):
        site = json.loads((REPOSITORY_ROOT / "infra" / "site.json").read_text())
        projection = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())
        self.assertEqual(site["siteId"], "machines-on-machines")
        self.assertEqual(projection["homePage"]["references"]["corpus"], "knowledge-corpus-ai-ml-research")  # the copied canonical corpus from read.p.apyr.us
        self.assertEqual(site["cms"]["siteOrigin"], projection["site"]["productionUrl"])
        self.assertEqual(site["cms"]["consoleOrigin"], "https://newsroom.machines-on-machines.anth.us")
        self.assertTrue(site["cms"]["cliRemoteLogin"] and site["cms"]["cliOnFederationClient"])
        self.assertEqual((site["github"]["ownerId"], site["github"]["repoId"]), (152415604, 1442003636))

    def test_the_home_page_plugin_is_on(self):
        self.assertIn('plugins: ["home-page"]', (REPOSITORY_ROOT / "papyrus.config.ts").read_text())

    def test_the_site_stylesheets_are_generated_from_their_sources(self):
        sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
        import sync_design_assets
        self.assertEqual(sync_design_assets.stale_copies(), [])

    def test_every_published_stylesheet_is_a_phone_block_and_a_scaled_block(self):
        for name in ("css/site-theme.css", "assets/mom-tokens.css", "assets/mom-components.css"):
            text = (REPOSITORY_ROOT / "web" / name).read_text()
            self.assertEqual(len(re.findall(r"(?m)^@media \(max-width: 599px\) \{$", text)), 1, name)
            self.assertEqual(len(re.findall(r"(?m)^@media \(min-width: 600px\) \{$", text)), 1, name)
            phone, scaled = text.split("@media (min-width: 600px) {")
            if name.startswith("css/"):
                self.assertIn("font-size: 17px", phone)
                self.assertIn("font-size: 12.75px", scaled)

    def test_no_stylesheet_draws_a_border_or_a_shadow(self):
        offenders = []
        for path in (REPOSITORY_ROOT / "web").rglob("*.css"):
            for number, line in enumerate(path.read_text().splitlines(), 1):
                if re.search(r"(?<![\w-])(border(-(top|right|bottom|left))?|box-shadow|text-shadow)\s*:\s*(?!0|none|\s)", line) and "border-radius" not in line:
                    offenders.append(f"{path.name}:{number}")
        self.assertEqual(offenders, [])

    def test_on_is_the_biggest_word_in_the_wordmark_and_sits_behind_it(self):
        tokens = (REPOSITORY_ROOT / "web" / "assets" / "mom-tokens.css").read_text()
        components = (REPOSITORY_ROOT / "web" / "assets" / "mom-components.css").read_text()
        on_scale = float(re.search(r"--wordmark-on-scale:\s*([\d.]+)em;", tokens).group(1))
        self.assertGreater(on_scale, 1.0)
        self.assertIn("--wordmark-seal-tilt:", tokens)
        seal_rule = re.search(r"\.mom-wordmark-on \{([^}]*)\}", components).group(1)
        for declaration in ("font-size: var(--wordmark-on-scale)", "border-radius: 50%", "transform: rotate(var(--wordmark-seal-tilt))", "z-index: 0"):
            self.assertIn(declaration, seal_rule)
        self.assertRegex(components, r"\.mom-wordmark > span:not\(\.mom-wordmark-on\) \{[^}]*z-index: 1")
        self.assertNotRegex(components, r"\.mom-wordmark-on \{[^}]*font-size: 0\.")

    def test_the_palette_stays_neutral_like_a_newspaper(self):
        tokens = (REPOSITORY_ROOT / "web" / "assets" / "mom-tokens.css").read_text()
        colors = re.findall(r"--([\w-]+):\s*#([0-9a-fA-F]{6});", tokens)
        self.assertTrue(colors)
        for name, value in colors:
            if name == "focus":
                continue
            channels = [int(value[index:index + 2], 16) for index in (0, 2, 4)]
            self.assertLessEqual((max(channels) - min(channels)) / 255, 0.35, f"--{name}: #{value} is too colorful")

    def test_links_inherit_their_color_without_outranking_components(self):
        theme = (REPOSITORY_ROOT / "web" / "css" / "site-theme.css").read_text()
        self.assertIn(":where(body.mom a) { color: inherit; }", theme)
        self.assertNotRegex(theme, r"(?m)^body\.mom a \{")

    def test_the_newsletter_theme_is_valid_and_its_wordmark_image_exists(self):
        theme_config = json.loads((REPOSITORY_ROOT / "design" / "newsletter" / "email-theme.json").read_text())
        wordmark_path = REPOSITORY_ROOT / "web" / "assets" / "email" / theme_config["wordmarkImageUrl"].rsplit("/", 1)[-1]
        self.assertTrue(wordmark_path.is_file(), wordmark_path)
        png_header = wordmark_path.read_bytes()[:24]
        pixel_width, pixel_height = int.from_bytes(png_header[16:20], "big"), int.from_bytes(png_header[20:24], "big")
        self.assertEqual((pixel_width, pixel_height), (theme_config["wordmarkWidth"] * 2, theme_config["wordmarkHeight"] * 2))
        self.assertTrue(theme_config["wordmarkImageUrl"].startswith("https://machines-on-machines.anth.us/assets/email/"))
        try:
            from papyrus_content.email_render import EmailFooter, render_issue, theme_from_config
        except ImportError:
            self.skipTest("Papyrus is not installed")
        theme = theme_from_config(theme_config, "Machines on Machines")
        footer = EmailFooter(site_name="Machines on Machines", site_url="https://machines-on-machines.anth.us/", reason="You get this because you subscribed.", manage_url="#preview", unsubscribe_url="#preview", postal_address="1 Example Way")
        sample = (REPOSITORY_ROOT / "design" / "newsletter" / "sample-weekly.md").read_text()
        mail = render_issue(subject="The Weekly", markus=sample, theme=theme, footer=footer, site_url="https://machines-on-machines.anth.us/", list_name="The Weekly")
        self.assertIn("mom-wordmark-on-navy-2x.png", mail.html)
        self.assertIn("Drafted by AI", mail.text)
        self.assertLess(len(mail.html.encode()), 100_000)

    def test_the_word_desk_appears_nowhere_in_the_site(self):
        offenders = [
            str(path.relative_to(REPOSITORY_ROOT))
            for root in ("web", "tests/fixtures")
            for path in (REPOSITORY_ROOT / root).rglob("*")
            if path.is_file() and re.search(r"\bdesk\b", path.read_text(errors="ignore"), re.I)
        ]
        self.assertEqual(offenders, [])


@unittest.skipUnless(
    (Path(sys.executable).parent / "papyrus").exists() or shutil.which("papyrus"),
    "the papyrus command from papyrus-newsroom is not installed",
)
class ProjectedSiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = project_to_temporary_directory()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def test_the_home_page_fills_its_slots_in_order(self):
        home = page_text(self.out, "/")
        main = home[home.index("<main"):]
        markers = ['class="mom-section-title">Top Articles', "mom-story-card-lead", "mom-sticker", 'id="mom-this-week"', 'class="mom-band mom-band-machine"', 'id="mom-latest-posts"', 'class="rh-mosaic"', "mom-band-on", 'aria-label="Just Found"', "home-page-explainer-card"]
        position = 0
        for marker in markers:
            found = main.find(marker, position)
            self.assertNotEqual(found, -1, marker)
            position = found

    def test_the_two_bands_are_the_same_colour(self):
        home = page_text(self.out, "/")
        self.assertEqual(home.count("mom-band-machine"), 2)
        self.assertNotIn("mom-band-brand", home)

    def test_just_found_leads_with_the_explainer_card_and_lists_references_once(self):
        home = page_text(self.out, "/")
        just_found = home.split('aria-label="Just Found"')[1].split("</section>")[0]
        self.assertIn("home-page-explainer-card", just_found)
        self.assertLess(just_found.index("home-page-explainer"), just_found.index('class="mom-reference-card"'))
        self.assertLessEqual(just_found.count('class="mom-reference-card"'), 16)
        self.assertNotIn("home-page-tile", home)

    def test_every_card_has_an_image_or_placeholder_art(self):
        home = page_text(self.out, "/")
        for card in re.findall(r'<a class="mom-(?:story|reference|thread)-card[^"]*".*?</a>', home, re.S):
            self.assertTrue("<img" in card or "mom-art " in card, card[:120])

    def test_a_reference_without_an_image_gets_seeded_art_for_its_address(self):
        findings = page_text(self.out, "/wire/")
        paper = re.search(r'<a class="mom-reference-card" href="https://arxiv.org/abs/0000.10001">.*?</a>', findings, re.S).group(0)
        self.assertIn("mom-art-pages", paper)

    def test_the_home_page_has_one_h1_and_no_hairline_markup(self):
        home = page_text(self.out, "/")
        self.assertEqual(home.count("<h1"), 1)
        self.assertNotIn("<hr", home)

    def test_provenance_chips_say_who_made_what(self):
        article = page_text(self.out, ARTICLE)
        self.assertIn("By various bots and Ada Reader", article)
        self.assertNotIn("Approved by", article)
        human = page_text(self.out, HUMAN_ARTICLE)
        self.assertIn("By Sam Rivera", human)
        self.assertIn("Editor’s pick", human)
        self.assertNotIn("various bots", human)

    def test_the_article_page_has_a_spine_with_the_section_and_no_colour_key(self):
        article = page_text(self.out, ARTICLE)
        self.assertIn('class="mom-spine"', article)
        self.assertNotIn("% read", article)
        self.assertNotIn("What the colors mean", article)

    def test_the_spine_tells_the_stylesheet_how_long_the_section_name_is(self):
        article = page_text(self.out, "/field-notes/steer-a-story/")
        self.assertIn("--mom-spine-characters: 20", article)  # "Machines on Field Notes"
        self.assertIn("Field Notes", article)

    def test_the_spine_type_is_the_smaller_of_the_usual_size_and_what_fits_the_name(self):
        theme = (REPOSITORY_ROOT / "web" / "css" / "site-theme.css").read_text()
        self.assertIn("var(--mom-spine-characters", theme)
        self.assertRegex(theme, r"font-size: min\(clamp\(32px, 5\.6vh, 70px\), calc\(var\(--mom-spine-room\)")
        self.assertIn("min-height: 521px", theme)  # too short for a vertical spine: it goes away

    def test_an_article_without_an_image_gets_a_slim_band_of_art_not_a_full_size_block(self):
        article = page_text(self.out, NO_IMAGE_ARTICLE)
        self.assertIn("mom-article-hero mom-article-hero-band", article)
        self.assertNotIn("mom-ratio-", article)
        theme = (REPOSITORY_ROOT / "web" / "css" / "site-theme.css").read_text()
        self.assertRegex(theme, r"\.mom-article-hero-band \.mom-card-image \{[^}]*height: 96px")

    def test_an_article_with_an_image_keeps_the_wide_picture(self):
        article = page_text(self.out, ARTICLE)
        self.assertIn('<div class="mom-article-hero"><span class="mom-media"><img class="mom-card-image"', article)
        self.assertNotIn("mom-ratio-", article)

    def test_a_legacy_team_byline_is_not_presented_as_a_person_or_an_approval(self):
        article = page_text(self.out, NO_IMAGE_ARTICLE)
        self.assertIn("By the editors", article)
        self.assertNotIn("By Papyrus Editorial Team", article)
        self.assertNotIn("Approved by", article)

    def test_a_blockquote_becomes_a_pull_quote_and_a_hashtag_with_a_wiki_page_becomes_a_link(self):
        article = page_text(self.out, ARTICLE)
        self.assertIn("mom-pull-quote-text", article)
        self.assertIn('<a class="mom-hashtag" href="/wiki/agent-evals/">#AgentEvals</a>', article)

    def test_the_section_page_has_the_sticker_and_topic_bands_with_words(self):
        section = page_text(self.out, "/field-notes/")
        self.assertIn("Machines</span><span class=\"mom-wordmark-on\">on</span><span>Machines", section)
        self.assertIn("New this week", section)
        self.assertIn("Editors are watching", section)

    def test_the_seed_sections_are_gone_from_the_navigation_and_their_addresses_are_not_projected(self):
        projection = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())
        self.assertEqual([link["label"] for link in projection["nav"]["links"]], ["Articles", "Posts", "Findings", "Videos", "Conversations", "Concepts"])
        self.assertEqual(list(projection["urls"]["sections"]), ["wiki"])
        for route in ("/papyrus/", "/how-to/"):
            self.assertFalse((self.out / route.strip("/") / "index.html").exists(), route)
        self.assertNotIn('href="/papyrus/"', page_text(self.out, "/"))
        self.assertNotIn('href="/how-to/"', page_text(self.out, "/"))

    def test_the_wiki_term_page_says_machines_on_meaning_and_who_edited_it(self):
        wiki = page_text(self.out, "/wiki/durable-execution/")
        self.assertIn("Machines on Meaning", wiki)
        self.assertIn("Edited by AI on 28 Oct 2026", wiki)
        self.assertIn("Draft, not yet reviewed", wiki)
        self.assertIn('class="mom-term-hash"', wiki)
        reviewed = page_text(self.out, "/wiki/agent-evals/")
        self.assertIn("Reviewed by Ada Reader on 29 Oct 2026", reviewed)

    def test_the_wiki_term_page_lists_the_stories_that_use_the_term(self):
        wiki = page_text(self.out, "/wiki/durable-execution/")
        self.assertIn("Stories that use this term", wiki)
        self.assertIn("/field-notes/durable-execution-for-agents/", wiki)

    def test_the_wire_lists_accepted_and_recommended_sources(self):
        wire = page_text(self.out, "/wire/")
        self.assertEqual(wire.count('class="mom-reference-card"'), 7)

    def test_conversations_lists_threads_and_each_thread_has_a_page(self):
        conversations = page_text(self.out, "/conversations/")
        self.assertEqual(conversations.count('class="mom-thread-card"'), 3)
        thread = page_text(self.out, "/conversations/b1c2d3e4f501/")
        self.assertIn("Is a judge that shares training data still a judge?", thread)

    def test_proposals_are_not_on_the_public_site(self):
        self.assertNotIn("Proposal", page_text(self.out, "/"))
        self.assertFalse((self.out / "proposals").exists())

    def test_the_component_gallery_renders_every_component_and_is_not_indexed(self):
        gallery = page_text(self.out, "/design/")
        for marker in ("mom-wordmark", "mom-sticker", "mom-spine", "mom-band", "mom-story-card", "mom-reference-card", "mom-thread-card", "mom-proposal-row", "mom-chip", "mom-button", "mom-nav-pill", "mom-wire-card", "mom-wiki-card", "mom-pull-quote", "mom-art"):
            self.assertIn(marker, gallery)
        self.assertIn("noindex", gallery)
        self.assertNotIn("/design/", (self.out / "sitemap.xml").read_text())

    def test_both_themes_ship_their_tokens(self):
        tokens = (self.out / "assets" / "mom-tokens.css").read_text()
        self.assertIn("prefers-color-scheme: dark", tokens)
        self.assertIn(':root[data-theme="dark"]', tokens)
        self.assertIn(":root {", tokens)
        self.assertIn("/assets/mom-tokens.css", page_text(self.out, "/"))

    def test_no_projected_page_says_desk_or_hides_that_a_machine_wrote_it(self):
        for path in self.out.rglob("*.html"):
            self.assertIsNone(re.search(r"\bdesk\b", path.read_text(), re.I), path)


if __name__ == "__main__":
    unittest.main()
