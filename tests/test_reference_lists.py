import re
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

import hooks  # noqa: E402

SECTION_PAGES = {"security": ("/security/", "Privacy & Security"), "science": ("/science/", "Math & Science")}


def resolve(name):
    return hooks._section_resolver(SimpleNamespace(settings=SimpleNamespace(pages=[
        SimpleNamespace(id="section-security", path="security", title="Privacy & Security"),
        SimpleNamespace(id="section-science", path="science", title="Math & Science"),
    ])))(name)


def tile(name, section=None, video=False):
    chips = ('<span class="home-page-chip" data-kind="medium"><svg></svg><span>Video</span></span>' if video else "")
    chips += f'<span class="home-page-chip" data-kind="section">{section}</span>' if section else ""
    return (f'<article class="home-page-tile" data-status="accepted"><div class="home-page-body"><h3 class="home-page-title"><a href="https://example.org/{name}">{name}</a></h3>'
            f'<p class="home-page-chips">{chips}</p></div></article>')


def keyed(name, section=None, video=False):
    return f'<li data-key="{name}">{tile(name, section=section, video=video)}</li>'


def plain(name, section=None, video=False):
    return f"<li>{tile(name, section=section, video=video)}</li>"


def names(html):
    return re.findall(r'<a href="https://example.org/([^"]+)">', html)


def page_html(kind, stream_items, source_items=None, lead=4, more=True, empty=False, source_count=500):
    blocks = ""
    if source_items is not None:
        blocks = (f'<div class="mom-by-section" data-source-count="{source_count}"><section class="home-page-references" data-select="recent">'
                  f'<ul class="home-page-grid">{"".join(source_items)}</ul></section></div>\n')
    grid = f'<ul class="home-page-grid" data-card="tile" data-reference-grid>{"".join(stream_items)}</ul>'
    tail = '<div class="home-page-more-links" data-reference-more data-src="/x.json"><a>Load more</a></div>' if more else ""
    body = '<p class="home-page-empty">None.</p>' if empty else grid + tail
    return (f'<div class="mom-page" data-list-kind="{kind}"><!--sf:refs-lead:{lead}-->\n{blocks}'
            f'<section class="mom-section mom-refs-stream" data-noun="{kind}" aria-label="More {kind}">\n<!--sf:refs-stream-->'
            f'<section class="home-page-references" data-paged="true">{body}</section><!--/sf:refs-stream-->\n</section></div>')


PAGE = SimpleNamespace(kind="custom", path="/videos/", title="Videos")


def run(html, page=PAGE):
    return hooks._reference_list_page(html, page, resolve)


class FilingTest(unittest.TestCase):
    def test_a_reference_is_filed_when_its_section_has_a_page_here(self):
        self.assertTrue(hooks._is_filed(tile("a", "Privacy &amp; Security"), resolve))
        self.assertTrue(hooks._is_filed(tile("a", "Math &amp; Science"), resolve))

    def test_a_section_without_a_page_and_no_section_are_not_filed(self):
        self.assertFalse(hooks._is_filed(tile("a", "Papyrus"), resolve))
        self.assertFalse(hooks._is_filed(tile("a"), resolve))

    def test_videos_are_recognised_by_their_medium_chip(self):
        self.assertTrue(hooks._is_video(tile("a", video=True)))
        self.assertFalse(hooks._is_video(tile("a")))

    def test_videos_are_dropped_from_findings_only(self):
        findings, videos = hooks._keeps("findings", True, resolve), hooks._keeps("videos", True, resolve)
        self.assertFalse(findings(tile("a", video=True)))
        self.assertTrue(videos(tile("a", video=True)))
        self.assertTrue(findings(tile("a", "Papyrus")))

    def test_filed_references_are_dropped_on_the_overview_pages_but_not_on_a_sections_own_list(self):
        self.assertFalse(hooks._keeps("videos", True, resolve)(tile("a", "Math &amp; Science")))
        self.assertTrue(hooks._keeps("videos", False, resolve)(tile("a", "Math &amp; Science")))


class LeadTest(unittest.TestCase):
    def lead_of(self, count_kept, lead=4):
        items = [keyed(f"n{number}") for number in range(count_kept)]
        return run(page_html("videos", items, lead=lead, more=False))

    def test_the_lead_row_sizes(self):
        self.assertEqual([hooks._lead_row_sizes(number) for number in range(5)], [[], [1], [2], [3], [1, 3]])

    def test_the_lead_lifts_up_to_four_and_the_rows_follow_the_count(self):
        for kept, rows in ((0, []), (1, [1]), (2, [2]), (3, [3]), (4, [1, 3]), (5, [1, 3])):
            html = self.lead_of(kept)
            lead = re.search(r'<section class="mom-section mom-refs-lead"[^>]*>(.*?)</section>', html, re.S)
            if not rows:
                self.assertIsNone(lead, kept)
                continue
            self.assertEqual([int(size) for size in re.findall(r'data-count="(\d+)"', lead.group(1))], rows, kept)
            self.assertEqual(names(lead.group(1)), [f"n{number}" for number in range(min(kept, 4))])

    def test_the_lifted_cards_are_gone_from_the_stream(self):
        html = self.lead_of(7)
        stream = html[html.index("mom-refs-stream"):]
        self.assertEqual(names(stream), ["n4", "n5", "n6"])

    def test_the_lead_and_the_stream_have_no_heading(self):
        html = self.lead_of(7)
        self.assertIsNone(re.search(r"<h[1-6]", html.replace("<h3 class=\"home-page-title\"", "")))
        self.assertIn('aria-label="Videos"', html)

    def test_the_mark_is_gone_even_with_no_lead(self):
        self.assertNotIn("sf:refs-lead", self.lead_of(0))


class StreamTest(unittest.TestCase):
    def test_the_stream_is_removed_when_it_is_empty_and_has_no_load_more(self):
        html = run(page_html("videos", [keyed("a"), keyed("b")], more=False))
        self.assertNotIn("mom-refs-stream", html)
        self.assertIn("mom-refs-lead", html)

    def test_the_stream_is_kept_when_there_is_more_to_load(self):
        html = run(page_html("videos", [keyed("a")], more=True))
        self.assertIn("mom-refs-stream", html)
        self.assertIn("data-reference-more", html)

    def test_the_stream_keeps_the_empty_sentence_when_nothing_at_all_is_shown(self):
        html = run(page_html("videos", [], empty=True, more=False))
        self.assertIn("home-page-empty", html)
        self.assertNotIn("mom-refs-lead", html)

    def test_filed_references_leave_the_first_page_of_the_stream_of_an_overview_page(self):
        source = [plain("s1", "Math &amp; Science"), plain("u1")]
        html = run(page_html("videos", [keyed("s1", section="Math &amp; Science"), keyed("u1"), keyed("u2")], source_items=source, lead=1))
        stream = html[html.index("mom-refs-stream"):]
        self.assertNotIn("s1", names(stream))
        self.assertEqual(names(stream), ["u2"])

    def test_the_stream_is_removed_when_the_source_proves_nothing_is_unfiled(self):
        source = [plain("s1", "Math &amp; Science"), plain("s2", "Privacy &amp; Security")]
        html = run(page_html("videos", [keyed("s1", section="Math &amp; Science"), keyed("s2", section="Privacy &amp; Security")], source_items=source))
        self.assertNotIn("mom-refs-stream", html)
        self.assertNotIn("mom-refs-lead", html)
        self.assertIn("mom-refs-section", html)

    def test_a_full_source_proves_nothing(self):
        source = [plain("s1", "Math &amp; Science")]
        html = run(page_html("videos", [keyed("s1", section="Math &amp; Science")], source_items=source, source_count=1))
        self.assertIn("mom-refs-stream", html)


class BlocksTest(unittest.TestCase):
    def source(self):
        return [plain("p1", "Privacy &amp; Security"), plain("u1"), plain("s1", "Math &amp; Science"), plain("p2", "Privacy &amp; Security"), plain("x1", "Papyrus")]

    def blocks(self, with_lead=True):
        stream = [keyed("u1"), keyed("x1", section="Papyrus"), keyed("u3")] if with_lead else [keyed("s1", section="Math &amp; Science")]
        return run(page_html("videos", stream, source_items=self.source(), lead=2 if with_lead else 4))

    def test_a_block_per_filed_section_in_the_order_of_its_best_reference_and_none_for_a_page_less_section(self):
        html = self.blocks()
        labels = re.findall(r'<section class="mom-section mom-refs-section" aria-label="([^"]*)"', html)
        self.assertEqual(labels, ["Privacy &amp; Security", "Math &amp; Science"])
        self.assertNotIn("Papyrus</h2>", html)

    def test_the_title_links_to_the_sections_own_list(self):
        html = self.blocks()
        self.assertIn('<a class="mom-section-title-link" href="/security/videos/">Privacy &amp; Security</a>', html)
        findings = run(page_html("findings", [keyed("u1")], source_items=self.source()))
        self.assertIn('href="/security/findings/"', findings)

    def test_more_link_says_the_section_and_noun_and_only_appears_when_there_is_more(self):
        many = [plain(f"p{number}", "Privacy &amp; Security") for number in range(8)] + [plain("s1", "Math &amp; Science")]
        html = run(page_html("videos", [keyed("u1")], source_items=many, lead=1))
        self.assertIn('<p class="mom-more"><a class="mom-more-link" href="/security/videos/">More Privacy &amp; Security videos…</a></p>', html)
        science = html[html.index('aria-label="Math &amp; Science"'):]
        self.assertNotIn("mom-more", science)
        findings = run(page_html("findings", [keyed("u1")], source_items=many, lead=1))
        self.assertIn(">More Privacy &amp; Security findings…</a>", findings)

    def test_the_tier_depends_on_whether_there_is_a_lead(self):
        many = [plain(f"p{number}", "Privacy &amp; Security") for number in range(9)] + [plain(f"s{number}", "Math &amp; Science") for number in range(9)]
        with_lead = run(page_html("videos", [keyed("u1")], source_items=many, lead=1))
        without = run(page_html("videos", [], source_items=many, lead=1, more=False))
        self.assertEqual(re.findall(r'data-rank="(\d)" data-tier="(\w+)"', with_lead), [("0", "wide"), ("1", "wide")])
        self.assertEqual(re.findall(r'data-rank="(\d)" data-tier="(\w+)"', without), [("0", "feature"), ("1", "wide")])
        self.assertEqual(len(names(with_lead[with_lead.index('aria-label="Privacy'):with_lead.index('aria-label="Math &amp; Science"')])), 6)
        self.assertEqual(len(names(without[without.index('aria-label="Privacy'):without.index('aria-label="Math &amp; Science"')])), 7)

    def test_no_block_head_shows_a_count(self):
        many = [plain(f"p{number}", "Privacy &amp; Security") for number in range(12)]
        self.assertNotIn("papyrus-group-more", run(page_html("videos", [keyed("u1")], source_items=many)))

    def test_videos_never_make_a_block_on_findings(self):
        source = [plain("v1", "Math &amp; Science", video=True), plain("f1", "Privacy &amp; Security")]
        html = run(page_html("findings", [keyed("u1")], source_items=source), SimpleNamespace(kind="custom", path="/findings/", title="Findings"))
        self.assertEqual(re.findall(r'aria-label="([^"]*)" data-rank', html), ["Privacy &amp; Security"])

    def test_the_order_in_the_page_is_lead_then_blocks_then_stream(self):
        html = self.blocks()
        self.assertLess(html.index("mom-refs-lead"), html.index("mom-refs-section"))
        self.assertLess(html.index("mom-refs-section"), html.index("mom-refs-stream"))


class ChunkPageTest(unittest.TestCase):
    def chunk(self, path, items):
        return hooks._reference_list_page("".join(items), SimpleNamespace(kind="reference_list", path=path, title="x"), resolve)

    def items(self):
        return [keyed("filed", section="Math &amp; Science"), keyed("plain"), keyed("movie", video=True), keyed("filedmovie", section="Math &amp; Science", video=True)]

    def test_videos_overview_chunks_drop_filed_references(self):
        self.assertEqual(names(self.chunk("/reference-lists/videos/untagged/abc/", self.items())), ["plain", "movie"])

    def test_findings_overview_chunks_drop_filed_references_and_videos(self):
        self.assertEqual(names(self.chunk("/reference-lists/findings/untagged/abc/", self.items())), ["plain"])

    def test_a_sections_findings_chunks_drop_videos_only(self):
        self.assertEqual(names(self.chunk("/reference-lists/security--findings/all/abc/", self.items())), ["filed", "plain"])

    def test_other_chunks_are_unchanged(self):
        self.assertEqual(names(self.chunk("/reference-lists/security--videos/all/abc/", self.items())), ["filed", "plain", "movie", "filedmovie"])
        self.assertEqual(names(self.chunk("/reference-lists/just-found/recommended/abc/", self.items())), ["filed", "plain", "movie", "filedmovie"])


class SectionNameOnTheCardTest(unittest.TestCase):
    def test_a_reference_in_a_section_with_no_page_says_the_section_on_its_card(self):
        html = run(page_html("videos", [keyed("a", section="Papyrus")], source_items=[plain("a", "Papyrus")], lead=1), PAGE)
        card = re.search(r'<article class="home-page-tile".*?</article>', html, re.S).group(0)
        self.assertIn('data-shown="true">Papyrus<', card)
        self.assertIn("Papyrus</span>", hooks.STOCK_TILE.sub(hooks._tile_to_reference_card, card))

    def test_a_card_from_another_page_does_not_say_its_section(self):
        card = hooks.STOCK_TILE.sub(hooks._tile_to_reference_card, tile("a", "Papyrus"))
        self.assertNotIn("Papyrus", card)


class SectionFindingsPanelTest(unittest.TestCase):
    def panel(self, tiles, shown=3):
        found = re.match(r"<!--sf:findings:(\d+)-->(.*?)<!--/sf:findings-->", f"<!--sf:findings:{shown}-->{''.join(tiles)}<!--/sf:findings-->", re.S)
        return hooks._section_findings(found, "security")

    def test_no_findings_means_no_panel(self):
        self.assertEqual(self.panel([]), "")
        self.assertEqual(self.panel([plain("v", video=True)]), "")

    def test_two_findings_make_one_row_of_two_and_no_more_link(self):
        html = self.panel([plain("a"), plain("v", video=True), plain("b")])
        self.assertEqual(names(html), ["a", "b"])
        self.assertIn('data-count="2"', html)
        self.assertNotIn("mom-more", html)

    def test_the_heading_links_to_the_sections_list_of_findings(self):
        self.assertIn('<h2 class="mom-section-title"><a class="mom-section-title-link" href="/security/findings/">Findings</a></h2>', self.panel([plain("a")]))

    def test_three_findings_fill_the_row(self):
        html = self.panel([plain("a"), plain("b"), plain("c")])
        self.assertIn('data-count="3"', html)
        self.assertNotIn("mom-more", html)

    def test_four_findings_show_three_and_say_more(self):
        html = self.panel([plain("a"), plain("v", video=True), plain("b"), plain("c"), plain("d")])
        self.assertEqual(names(html), ["a", "b", "c"])
        self.assertIn('<p class="mom-more"><a class="mom-more-link" href="/security/findings/">More findings…</a></p>', html)


if __name__ == "__main__":
    unittest.main()
