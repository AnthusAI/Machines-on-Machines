import json
import re
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from projection_support import REPOSITORY_ROOT, page_text, project_to_temporary_directory  # noqa: E402

ARTICLE = "/papyrus/the-agents-are-writing-the-benchmarks-now/"
HUMAN_ARTICLE = "/papyrus/who-owns-an-agents-mistakes/"
PAPYRUS_VERSION = "5.69.0-next.2"


def npm_version(pin):
    """PyPI spells the npm prerelease 5.69.0-next.2 as 5.69.0.dev2; compare in npm's spelling."""
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

    def test_the_site_identity_is_consistent(self):
        site = json.loads((REPOSITORY_ROOT / "infra" / "site.json").read_text())
        projection = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())
        self.assertEqual(site["siteId"], "machines-on-machines")
        self.assertEqual(projection["homePage"]["references"]["corpus"], "ai-ml-research")  # the copied canonical corpus from read.p.apyr.us
        self.assertEqual(site["cms"]["siteOrigin"], projection["site"]["productionUrl"])
        self.assertEqual(site["cms"]["consoleOrigin"], "https://newsroom.machines-on-machines.anth.us")
        self.assertTrue(site["cms"]["cliRemoteLogin"] and site["cms"]["cliOnFederationClient"])
        self.assertEqual((site["github"]["ownerId"], site["github"]["repoId"]), (152415604, 1442003636))

    def test_the_home_page_plugin_is_on(self):
        self.assertIn('plugins: ["home-page"]', (REPOSITORY_ROOT / "papyrus.config.ts").read_text())

    def test_the_site_stylesheets_are_the_design_systems(self):
        for source, copy in (("design/system/tokens.css", "web/assets/mom-tokens.css"), ("design/system/components/bundle.css", "web/assets/mom-components.css")):
            self.assertEqual((REPOSITORY_ROOT / source).read_bytes(), (REPOSITORY_ROOT / copy).read_bytes(), copy)

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
        markers = ["mom-story-card-lead", "mom-sticker", 'id="mom-just-accepted"', "mom-story-grid", 'id="mom-talking-now"', "mom-band-brand", 'id="mom-recommends"', 'id="mom-proposals"']
        positions = [home.find(marker) for marker in markers]
        self.assertNotIn(-1, positions, dict(zip(markers, positions)))
        self.assertEqual(positions, sorted(positions))

    def test_just_accepted_shows_three_reference_cards_and_recommends_shows_three_more(self):
        home = page_text(self.out, "/")
        accepted = home.split('id="mom-just-accepted"')[1].split("</section>")[0]
        recommended = home.split('id="mom-recommends"')[1].split("</section>")[0]
        self.assertEqual(accepted.count('class="mom-reference-card"'), 3)
        self.assertEqual(recommended.count('class="mom-reference-card"'), 3)
        self.assertEqual(recommended.count("Recommended by Cyclotron, not yet accepted"), 3)
        self.assertNotIn("home-page-tile", home)

    def test_talking_now_shows_two_thread_cards(self):
        home = page_text(self.out, "/")
        talking = home.split('id="mom-talking-now"')[1].split("</section>")[0]
        self.assertEqual(talking.count('class="mom-thread-card"'), 2)
        self.assertNotIn("<a href=\"/conversations/b1c2d3e4f501/\"><", talking)

    def test_every_card_has_an_image_or_placeholder_art(self):
        home = page_text(self.out, "/")
        for card in re.findall(r'<a class="mom-(?:story|reference|thread)-card[^"]*".*?</a>', home, re.S):
            self.assertTrue("<img" in card or "mom-art " in card, card[:120])

    def test_a_reference_without_an_image_gets_seeded_art_for_its_address(self):
        home = page_text(self.out, "/")
        paper = re.search(r'<a class="mom-reference-card" href="https://arxiv.org/abs/0000.10001">.*?</a>', home, re.S).group(0)
        self.assertIn("mom-art-pages", paper)

    def test_the_home_page_has_one_h1_and_no_hairline_markup(self):
        home = page_text(self.out, "/")
        self.assertEqual(home.count("<h1"), 1)
        self.assertNotIn("<hr", home)

    def test_provenance_chips_say_who_made_what(self):
        article = page_text(self.out, ARTICLE)
        self.assertIn("Drafted by AI", article)
        self.assertIn("Approved by Ada Reader", article)
        human = page_text(self.out, HUMAN_ARTICLE)
        self.assertIn("Written by Sam Rivera", human)
        self.assertIn("Editor’s pick", human)
        self.assertNotIn("Drafted by AI", human)

    def test_the_article_page_has_a_spine_with_the_section_and_a_colour_key_in_words(self):
        article = page_text(self.out, ARTICLE)
        self.assertIn('class="mom-spine"', article)
        self.assertIn("0% read", article)
        self.assertIn("What the colors mean", article)
        for word in ("Teal", "Gold", "Pink"):
            self.assertIn(word, article)

    def test_a_blockquote_becomes_a_pull_quote_and_a_hashtag_with_a_wiki_page_becomes_a_link(self):
        article = page_text(self.out, ARTICLE)
        self.assertIn("mom-pull-quote-text", article)
        self.assertIn('<a class="mom-hashtag" href="/wiki/agent-evals/">#AgentEvals</a>', article)

    def test_the_section_page_has_the_sticker_and_topic_bands_with_words(self):
        section = page_text(self.out, "/papyrus/")
        self.assertIn("Machines</span><span class=\"mom-wordmark-on\">on</span><span>Papyrus", section)
        self.assertIn("New this week", section)
        self.assertIn("Editors are watching", section)

    def test_the_how_to_section_keeps_its_name_and_address(self):
        self.assertIn("Newsroom How-To", page_text(self.out, "/how-to/"))

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
        self.assertIn("/papyrus/durable-execution-for-agents/", wiki)

    def test_the_wire_lists_accepted_and_recommended_sources(self):
        wire = page_text(self.out, "/wire/")
        self.assertEqual(wire.count('class="mom-reference-card"'), 7)

    def test_conversations_lists_threads_and_each_thread_has_a_page(self):
        conversations = page_text(self.out, "/conversations/")
        self.assertEqual(conversations.count('class="mom-thread-card"'), 3)
        thread = page_text(self.out, "/conversations/b1c2d3e4f501/")
        self.assertIn("Is a judge that shares training data still a judge?", thread)

    def test_proposals_are_labelled_placeholders_proposed_by_ai(self):
        proposals = page_text(self.out, "/proposals/")
        self.assertIn("Placeholder", proposals)
        self.assertIn("Proposed by AI", proposals)

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
