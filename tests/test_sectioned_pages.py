import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))

import hooks  # noqa: E402


def story(title, topic, updated, kind="post", url="/x/", section_base=None):
    section = SimpleNamespace(is_type=section_base is None, label=topic or "", base=section_base or "posts")
    return SimpleNamespace(type=kind, title=title, url=url, topic=topic, updated=updated, date=updated, section=section)


class SectionNamesTest(unittest.TestCase):
    def test_ai_stays_in_capitals_in_a_section_made_from_a_topic(self):
        self.assertEqual(hooks._topic_label(story("a", "ai-safety", "2026-11-01")), "AI Safety")
        self.assertEqual(hooks._topic_label(story("a", "ai-ethics-and-law", "2026-11-01")), "AI Ethics And Law")

    def test_other_topics_are_still_title_cased_and_known_labels_win(self):
        self.assertEqual(hooks._topic_label(story("a", "history", "2026-11-01")), "History")
        self.assertEqual(hooks._topic_label(story("a", "security", "2026-11-01")), "Privacy & Security")


class StoriesBySectionTest(unittest.TestCase):
    def labels(self, entries, story_type="post"):
        return [label for label, _ in hooks._stories_by_section(entries, story_type)]

    def test_each_page_has_only_its_own_type(self):
        entries = [story("a", "science", "2026-11-01", "article"), story("b", "science", "2026-11-02", "post"), story("c", "history", "2026-11-03", "post")]
        self.assertEqual([[entry.title for entry in stories] for _, stories in hooks._stories_by_section(entries, "article")], [["a"]])
        self.assertEqual([[entry.title for entry in stories] for _, stories in hooks._stories_by_section(entries, "post")], [["c"], ["b"]])

    def test_the_sections_are_ordered_the_same_way_for_both_types(self):
        for kind in ("article", "post"):
            entries = [story("o", "history", "2026-10-01", kind), story("n", "science", "2026-11-01", kind), story("m", "science", "2026-10-15", kind)]
            grouped = hooks._stories_by_section(entries, kind)
            self.assertEqual([label for label, _ in grouped], ["Science", "History"])
            self.assertEqual([entry.title for entry in grouped[0][1]], ["n", "m"])

    def test_stories_with_no_section_are_named_for_their_page(self):
        self.assertEqual(self.labels([story("n", "", "2026-11-05", "post")], "post"), ["More posts"])
        self.assertEqual(self.labels([story("n", "", "2026-11-05", "article")], "article"), ["More stories"])

    def test_nothing_else_is_a_story_and_a_story_needs_an_address(self):
        entries = [story("w", "science", "2026-11-01", "wiki_page"), story("r", "science", "2026-11-01", "reference"), story("n", "science", "2026-11-01", url=None)]
        for kind in ("article", "post"):
            self.assertEqual(hooks._stories_by_section(entries, kind), [])

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
        self.assertEqual(self.labels([story("n", "", "2026-11-05"), story("s", "science", "2026-10-01")]), ["Science", "More posts"])

    def test_no_section_is_dropped(self):
        entries = [story(str(i), f"topic-{i}", f"2026-10-{i + 1:02d}") for i in range(12)]
        self.assertEqual(len(self.labels(entries)), 12)


class SectionedPageTest(unittest.TestCase):
    def setUp(self):
        self.originals = (hooks._page_top, hooks._story_card)
        hooks._page_top = lambda title, lead: f"<top>{title}|{lead}</top>"
        hooks._story_card = lambda entry, size="large", extra_class=None: f'<a class="mom-story-card {extra_class}">{entry.title}</a>'

    def tearDown(self):
        hooks._page_top, hooks._story_card = self.originals

    def test_an_empty_page_says_nothing_has_been_published(self):
        for kind in ("article", "post"):
            html = hooks._sectioned_page([], kind, "Title", "Lead")
            self.assertIn("Nothing has been published here yet.", html)
            self.assertNotIn("mom-stories-section", html)

    def test_both_pages_use_the_same_layout(self):
        entries = [story(f"s{i}", "science", "2026-11-0%d" % (i + 1), kind) for i in range(4) for kind in ("article", "post")]
        for kind in ("article", "post"):
            html = hooks._sectioned_page(entries, kind, "Title", "Lead")
            self.assertIn('data-tier="feature"', html)
            self.assertEqual(html.count('class="mom-story-card'), 4)


class MovedPageTest(unittest.TestCase):
    def test_the_old_stories_address_sends_readers_to_articles(self):
        head = hooks.head_extra(SimpleNamespace(path="/stories/"))
        self.assertIn('<meta http-equiv="refresh" content="0; url=/articles/">', head)
        self.assertIn('<link rel="canonical" href="/articles/">', head)

    def test_other_pages_are_not_redirected(self):
        self.assertNotIn("refresh", hooks.head_extra(SimpleNamespace(path="/articles/")))

    def test_articles_and_posts_listings_are_both_sectioned(self):
        self.assertEqual({kind for kind, _ in hooks.SECTIONED_LISTINGS.values()}, {"article", "post"})
        self.assertEqual(hooks.SECTIONED_LISTINGS["type:article"][1], hooks.ARTICLES_LEAD)


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


class ConceptWordingTest(unittest.TestCase):
    def test_associations_are_connected_concepts_plus_stories_and_nothing_when_neither(self):
        self.assertEqual(hooks._concept_associations(2, 1), 3)
        self.assertEqual(hooks._concept_associations(0, 4), 4)
        self.assertIsNone(hooks._concept_associations(0, 0))
        self.assertIsNone(hooks._concept_associations(None, None))

    def test_the_card_says_the_number_first_and_carries_it_as_data(self):
        import mom_components as mom
        card = mom.wiki_card("A", "/a/", associations=12)
        self.assertIn(">12 associations<", card)
        self.assertIn('data-associations="12"', card)
        self.assertIn(">1 association<", mom.wiki_card("A", "/a/", associations=1))

    def test_a_card_without_associations_has_no_metric_and_no_type_label(self):
        import mom_components as mom
        card = mom.wiki_card("A", "/a/", associations=None)
        self.assertNotIn("associations", card)
        self.assertNotIn("data-associations", card)
        for word in ("Topic", "Concept"):
            self.assertNotIn(word, card)

    def test_a_connected_term_of_a_concept_kind_loses_its_kind_label_and_others_keep_theirs(self):
        chip = '<a class="papyrus-knowledge-chip" data-kind="%s" href="/x/"><span class="papyrus-knowledge-chip-kind">%s</span><span class="papyrus-knowledge-chip-name">N</span></a>'
        self.assertNotIn("chip-kind", hooks._unlabel_concept_chips(chip % ("topic", "Topic")))
        self.assertIn(">Maker<", hooks._unlabel_concept_chips(chip % ("maker", "Maker")))


if __name__ == "__main__":
    unittest.main()
