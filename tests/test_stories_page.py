import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))

import hooks  # noqa: E402


def story(title, topic, updated, kind="post", url="/x/", section_base=None):
    section = SimpleNamespace(is_type=section_base is None, label=topic or "", base=section_base or "posts")
    return SimpleNamespace(type=kind, title=title, url=url, topic=topic, updated=updated, date=updated, section=section)


class StoriesBySectionTest(unittest.TestCase):
    def labels(self, entries):
        return [label for label, _ in hooks._stories_by_section(entries)]

    def test_articles_and_posts_are_both_stories(self):
        grouped = hooks._stories_by_section([story("a", "science", "2026-11-01", "article"), story("b", "science", "2026-11-02", "post")])
        self.assertEqual([entry.title for entry in grouped[0][1]], ["b", "a"])

    def test_nothing_else_is_a_story_and_a_story_needs_an_address(self):
        entries = [story("w", "science", "2026-11-01", "wiki_page"), story("r", "science", "2026-11-01", "reference"), story("n", "science", "2026-11-01", url=None)]
        self.assertEqual(hooks._stories_by_section(entries), [])

    def test_the_most_recently_updated_section_is_first_and_updated_beats_date(self):
        old = story("old", "history", "2026-10-01")
        late = story("late", "security", "2026-09-01")
        late.updated = "2026-11-04"
        self.assertEqual(self.labels([old, late, story("mid", "science", "2026-11-01")]), ["Privacy & Security", "Science", "History"])

    def test_a_missing_update_falls_back_to_the_date(self):
        dated = story("d", "science", None)
        dated.date = "2026-11-03"
        self.assertEqual(self.labels([story("x", "history", "2026-11-01"), dated]), ["Science", "History"])

    def test_stories_with_no_section_come_last_however_new(self):
        self.assertEqual(self.labels([story("n", "", "2026-11-05"), story("s", "science", "2026-10-01")]), ["Science", "More stories"])

    def test_no_section_is_dropped(self):
        entries = [story(str(i), f"topic-{i}", f"2026-10-{i + 1:02d}") for i in range(12)]
        self.assertEqual(len(self.labels(entries)), 12)


class StoriesLayoutTest(unittest.TestCase):
    def test_tiers_follow_the_rank(self):
        self.assertEqual([hooks._story_tier(rank) for rank in range(5)], ["feature", "wide", "wide", "plain", "plain"])

    def test_the_top_section_has_a_feature_then_full_rows(self):
        self.assertEqual(hooks._stories_rows("feature", 7), [["feature"], ["plain"] * 3, ["plain"] * 3])
        self.assertEqual(hooks._stories_rows("feature", 2), [["feature", "plain"]])

    def test_the_next_sections_have_one_wide_card_then_a_grid(self):
        self.assertEqual(hooks._stories_rows("wide", 5), [["wide", "plain"], ["plain"] * 3])

    def test_later_sections_are_plain_grids_with_no_feature(self):
        for count in range(1, 12):
            roles = {role for row in hooks._stories_rows("plain", count) for role in row}
            self.assertFalse(roles & {"feature", "wide"}, count)

    def test_a_section_of_one_is_a_single_card_across_the_row(self):
        for tier in ("feature", "wide", "plain"):
            self.assertEqual(hooks._stories_rows(tier, 1), [["solo"]])

    def test_no_row_is_longer_than_three_and_no_count_leaves_a_hole(self):
        for tier in ("feature", "wide", "plain"):
            for count in range(1, 20):
                rows = hooks._stories_rows(tier, count)
                self.assertEqual(sum(len(row) for row in rows), min(count, hooks.STORIES_SHOWN[tier]))
                for row in rows:
                    self.assertLessEqual(len(row) + ("wide" in row), 3)
                    self.assertNotEqual(len(row), 0)

    def test_the_head_says_how_many_stories_there_are_when_some_are_not_shown(self):
        self.assertIn("12 stories", hooks._stories_head("Science", 12, 6, None))
        self.assertNotIn("stories", hooks._stories_head("Science", 4, 4, None))

    def test_a_more_link_exists_only_for_a_section_with_a_page(self):
        self.assertIn('href="/science/"', hooks._stories_head("Science", 12, 6, "/science/"))
        self.assertNotIn("<a", hooks._stories_head("Science", 12, 6, None))
        self.assertIsNone(hooks._stories_more_href([story("a", "science", "2026-11-01")]))
        self.assertEqual(hooks._stories_more_href([story("a", "science", "2026-11-01"), story("b", "science", "2026-11-01", "article", section_base="science")]), "/science/")


if __name__ == "__main__":
    unittest.main()
