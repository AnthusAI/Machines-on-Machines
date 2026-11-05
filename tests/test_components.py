import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

import mom_components as mom  # noqa: E402

BUNDLE_PATH = REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.js"
SEEDS = [
    "", "a", "https://machines-on-machines.anth.us/field-notes/x/", "https://arxiv.org/abs/0000.00000",
    "Who owns an agent’s mistakes?", "é中文 \U0001f600", "seed-one", "seed-two", "seed-three", "seed-four", "seed-five", "seed-six",
]


def _javascript_choices(seeds):
    script = (
        "const window = { React: { createElement() {} } };"
        f"eval(require('fs').readFileSync({json.dumps(str(BUNDLE_PATH))}, 'utf8'));"
        f"const seeds = {json.dumps(seeds)};"
        "console.log(JSON.stringify(seeds.flatMap(seed => [window.MoM.choosePlaceholderArt(seed), window.MoM.choosePlaceholderArt(seed, 'paper')])));"
    )
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class PlaceholderArtTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_the_python_choice_matches_the_javascript_choice_for_every_seed(self):
        javascript = _javascript_choices(SEEDS)
        python = []
        for seed in SEEDS:
            for kind in (None, "paper"):
                composition, tone = mom.choose_placeholder_art(seed, kind)
                python.append({"composition": composition, "tone": tone})
        self.assertEqual(javascript, python)

    def test_the_same_seed_draws_the_same_art(self):
        self.assertEqual(mom.placeholder_art("https://example.test/a"), mom.placeholder_art("https://example.test/a"))

    def test_research_papers_get_the_pages_composition_with_three_shapes(self):
        art = mom.placeholder_art("https://arxiv.org/abs/0000.00000", kind="paper")
        self.assertIn("mom-art-pages", art)
        self.assertEqual(art.count("mom-art-shape mom-art-shape-"), 3)

    def test_paper_locations_are_recognised_like_the_javascript(self):
        for location in ("https://arxiv.org/abs/1", "https://x.test/a.pdf", "https://x.test/a.pdf?download=1", "https://x.test/?file=a.pdf"):
            self.assertTrue(mom.is_research_paper_location(location), location)
        for location in ("https://x.test/a.pdfx", "https://blog.test/post", None, ""):
            self.assertFalse(mom.is_research_paper_location(location), location)

    def test_art_is_decorative_and_never_a_stock_photo(self):
        art = mom.placeholder_art("seed")
        self.assertIn('aria-hidden="true"', art)
        self.assertNotIn("<img", art)

    def test_a_card_without_an_image_draws_art_and_a_card_with_one_keeps_its_seed_for_the_fallback(self):
        self.assertIn("mom-art", mom.card_image(None, seed="s"))
        with_image = mom.card_image("/a.png", seed="s")
        self.assertIn('data-art-seed="s"', with_image)
        self.assertIn("<img", with_image)


class ComponentWordingTest(unittest.TestCase):
    def test_reference_status_says_who_accepted_in_words(self):
        self.assertIn("Accepted by an editor", mom.reference_card("t", status="accepted", actor="human"))
        self.assertIn("Accepted by Cyclotron", mom.reference_card("t", status="accepted", actor="cyclotron"))
        self.assertIn("Accepted automatically", mom.reference_card("t", status="accepted", actor=None))

    def test_a_recommended_reference_says_it_is_not_accepted_and_shows_confidence_in_words(self):
        card = mom.reference_card("t", status="recommended", confidence=0.91)
        self.assertIn("Recommended by Cyclotron, not yet accepted", card)
        self.assertIn("91% confidence", card)
        self.assertEqual(card.count("mom-meter-segment-filled"), 5)

    def test_thread_authors_use_the_role_labels(self):
        self.assertIn("mom-author-machine", mom.thread_card("t", author="AI", latest="x"))
        self.assertIn("mom-author-human", mom.thread_card("t", author="Editor", latest="x"))
        self.assertIn("mom-author-reader", mom.thread_card("t", author="ada", latest="x"))

    def test_a_single_message_is_not_pluralised(self):
        self.assertIn("1 message<", mom.thread_card("t", messages=1))
        self.assertIn("2 messages<", mom.thread_card("t", messages=2))

    def test_text_is_escaped(self):
        self.assertNotIn("<script>", mom.story_card("<script>alert(1)</script>"))

    def test_proposals_are_read_only_and_use_a_lucide_icon(self):
        row = mom.proposal_row("x", net=3)
        self.assertIn('data-icon="arrow-up-down"', row)
        self.assertIn("+3", row)
        self.assertNotIn("<button", row)

    def test_the_wordmark_is_type_not_an_image(self):
        mark = mom.wordmark("stacked")
        self.assertNotIn("<img", mark)
        self.assertIn('<span class="mom-wordmark-on">on</span>', mark)

    def test_the_spine_reports_the_length_of_the_full_name_for_fitting(self):
        self.assertIn("--mom-spine-characters: 19", mom.spine("Papyrus"))
        self.assertIn("--mom-spine-characters: 56", mom.spine("A very long section name that must still fit"))

    def test_band_words_that_start_with_a_hash_are_tags(self):
        self.assertIn("mom-band-tag", mom.loop_band("machine", ["#Evals"]))

    def test_unknown_roles_fall_back(self):
        self.assertIn("mom-chip-machine", mom.provenance_chip("nope", "x"))
        self.assertIn("mom-band-brand", mom.loop_band("nope"))


if __name__ == "__main__":
    unittest.main()
