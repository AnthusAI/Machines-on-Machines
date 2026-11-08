import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

import hooks  # noqa: E402
import mom_components as mom  # noqa: E402


def card(key, title, kind="story", url=None, section=None, count=2, at="2026-10-31T10:00:00Z", author="ada"):
    attribute = f' data-section="{section}"' if section else ""
    link = f'<a href="{url}">A story</a>' if url else "A paper"
    return (
        f'<article class="home-page-thread" data-anchor="{kind}"{attribute}><div class="home-page-body">'
        f'<p class="home-page-eyebrow home-page-anchor" data-kind="{kind}"><span>{kind.title()}: {link}</span></p>'
        f'<h3 class="home-page-title"><a href="/conversations/{key}/">{title}</a></h3>'
        f'<p class="home-page-thread-meta"><span class="home-page-count"><span>{count} messages</span></span><time datetime="{at}">31 Oct 2026</time></p>'
        f'<p class="home-page-excerpt">Latest words</p><p class="home-page-author">by {author}</p></div></article>'
    )


def page(sections=(("security", "Privacy & Security"), ("science", "Math & Science")), stories=None):
    pages = [SimpleNamespace(id=f"section-{path}", path=path, title=title, description=f"About {title}") for path, title in sections]
    entries = [SimpleNamespace(url=url, topic=topic) for url, topic in (stories or {}).items()]
    return SimpleNamespace(settings=SimpleNamespace(pages=pages, sections=[]), site=None, entries=entries, kind="custom", custom_id="conversations", thread=None)


class ForumBoardsTest(unittest.TestCase):
    def test_the_section_the_thread_data_names_beats_the_story_it_is_about(self):
        threads = hooks._forum_threads(card("aaaaaaaaaaaa", "T", url="/articles/s/", section="Math & Science"))
        board = hooks._board_of_thread(page(stories={"/articles/s/": "security"}), threads[0])
        self.assertEqual((board.name, board.href), ("Math & Science", "/science/"))

    def test_a_card_with_the_extra_attribute_is_still_read(self):
        self.assertEqual(len(hooks._forum_threads(card("aaaaaaaaaaaa", "T", section="Math & Science") + card("bbbbbbbbbbbb", "U"))), 2)

    def test_without_a_section_the_story_decides_and_a_reference_goes_to_general(self):
        threads = hooks._forum_threads(card("aaaaaaaaaaaa", "T", url="/articles/s/") + card("bbbbbbbbbbbb", "U", kind="reference"))
        fixture = page(stories={"/articles/s/": "security"})
        self.assertEqual([hooks._board_of_thread(fixture, thread).name for thread in threads], ["Privacy & Security", "General"])

    def test_a_section_without_a_page_is_a_board_with_no_link(self):
        threads = hooks._forum_threads(card("aaaaaaaaaaaa", "T", section="Made Up"))
        board = hooks._board_of_thread(page(), threads[0])
        self.assertEqual((board.name, board.href), ("Made Up", None))

    def test_boards_are_ordered_by_latest_activity_and_general_is_last_whatever_its_date(self):
        markup = (
            card("aaaaaaaaaaaa", "Old science", url="/a/", section="Math & Science", at="2026-10-01T00:00:00Z")
            + card("bbbbbbbbbbbb", "New security", url="/b/", section="Privacy & Security", at="2026-10-20T00:00:00Z")
            + card("cccccccccccc", "Newest general", kind="reference", at="2026-10-30T00:00:00Z")
        )
        boards = hooks._forum_boards(page(), hooks._forum_threads(markup))
        self.assertEqual([board.name for board, _ in boards], ["Privacy & Security", "Math & Science", "General"])

    def test_the_index_holds_every_row_and_marks_those_after_the_first_page_for_the_script(self):
        markup = "".join(card(f"{index:012x}", f"T{index}", section="Math & Science", at=f"2026-10-{index + 1:02d}T00:00:00Z") for index in range(25))
        html = hooks._forum_index_body(page(), markup)
        self.assertEqual(html.count('class="mom-forum-row"'), 25)
        self.assertEqual(html.count('class="mom-forum-row" data-later'), 15)
        self.assertLess(html.index("T24"), html.index("T23"))

    def test_a_thread_page_takes_its_board_from_the_thread_document_first(self):
        fixture = page(stories={"/articles/s/": "security"})
        fixture.thread = {"section": "Math & Science", "anchor": {"kind": "story", "url": "/articles/s/"}}
        self.assertEqual(hooks._thread_board(fixture).name, "Math & Science")
        fixture.thread = {"anchor": {"kind": "story", "url": "/articles/s/"}}
        self.assertEqual(hooks._thread_board(fixture).name, "Privacy & Security")
        fixture.thread = {"anchor": {"kind": "reference", "title": "x"}}
        self.assertEqual(hooks._thread_board(fixture).name, "General")


class ForumComponentTest(unittest.TestCase):
    def test_a_conversation_with_no_reply_has_a_different_mark_and_words(self):
        quiet, busy = mom.forum_row("T", "/c/", 1), mom.forum_row("T", "/c/", 3)
        self.assertIn('data-icon="message-circle"', quiet)
        self.assertIn("No replies yet", quiet)
        self.assertIn('data-icon="message-square"', busy)
        self.assertIn("2 replies", busy)

    def test_the_exact_moment_is_in_the_title_and_everything_is_escaped(self):
        row = mom.forum_row("<b>T</b>", "/c/", 2, last_iso="2026-10-31T10:05:00Z", last_text="31 Oct 2026")
        self.assertIn('title="2026-10-31 10:05 UTC"', row)
        self.assertNotIn("<b>", row)

    def test_a_board_heading_links_only_with_an_address(self):
        self.assertIn('<a href="/security/">Security</a>', mom.forum_board("b", "Security", "/security/", None, 1, None, None, "", 1))
        self.assertNotIn("<a ", mom.forum_board("b", "General", None, None, 1, None, None, "", 1))

    def test_a_reply_count_reads_in_the_singular(self):
        self.assertEqual((mom.reply_phrase(1), mom.reply_phrase(0), mom.reply_phrase(4)), ("1 reply", "0 replies", "4 replies"))


if __name__ == "__main__":
    unittest.main()
