import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

import hooks  # noqa: E402


class CardVariantTest(unittest.TestCase):
    """The site's card hook draws the Latest Posts tile and the group cards; a group of one is a feature, and the first card is the largest."""

    def setUp(self):
        self.calls = []
        self.original_story_card = hooks._story_card
        self.original_is_wiki = hooks._is_wiki
        hooks._is_wiki = lambda entry: False
        hooks._story_card = lambda entry, size="large", extra_class=None: self.calls.append((size, extra_class)) or "<a>card</a>"

    def tearDown(self):
        hooks._story_card = self.original_story_card
        hooks._is_wiki = self.original_is_wiki

    def drawn(self, variant, index=0, count=None):
        self.calls.clear()
        hooks.card(SimpleNamespace(), None, variant=variant, index=index, count=count)
        return self.calls[-1]

    def test_a_tile_is_a_large_card_in_the_tile_class(self):
        self.assertEqual(self.drawn("tile", 0, 1), ("large", "rh-tile"))

    def test_a_group_of_one_is_a_solo_feature_card(self):
        self.assertEqual(self.drawn("large", 0, 1), ("large", "rh-large rh-first rh-solo"))

    def test_the_first_of_several_is_the_largest_and_the_rest_are_plain_large(self):
        self.assertEqual(self.drawn("large", 0, 2), ("large", "rh-large rh-first"))
        self.assertEqual(self.drawn("large", 1, 2), ("large", "rh-large"))

    def test_a_large_card_without_a_count_is_still_drawn(self):
        self.assertEqual(self.drawn("large"), ("large", "rh-large rh-first"))

    def test_the_existing_variants_are_unchanged(self):
        self.assertEqual(self.drawn("lead"), ("large", "mom-story-card-lead"))
        self.assertEqual(self.drawn(None), ("large", None))
        self.assertEqual(self.drawn("small"), ("small", None))


if __name__ == "__main__":
    unittest.main()
