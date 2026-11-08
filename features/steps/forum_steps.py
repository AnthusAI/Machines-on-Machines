"""Steps for features/forum.feature: the conversations page as a forum (boards of rows) and a thread page as a topic (posts).

The `@browser` scenarios draw the projected site through tools/measure_forum.cjs and skip themselves when Node or Playwright is missing.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace

from behave import given, then, when

from projection_support import REPOSITORY_ROOT  # noqa: E402
from image_ratio_steps import served_origin, stylesheet_versions  # noqa: E402

sys.path.insert(0, str(REPOSITORY_ROOT / "web"))
import hooks  # noqa: E402

MEASURE_FORUM_SCRIPT = REPOSITORY_ROOT / "tools" / "measure_forum.cjs"
BOARD = re.compile(r'<section class="mom-forum-board"[^>]*>(.*?)</section>', re.S)
BOARD_TITLE = re.compile(r'<h2 id="[^"]*" class="mom-forum-board-title">(?:<a href="([^"]*)">)?([^<]*)')
ROW = re.compile(r'<li class="mom-forum-row"[^>]*>(.*?)</li>', re.S)
POST = re.compile(r'<article class="mom-post" id="([^"]*)">(.*?)</article>', re.S)


def _plain(markup):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", markup)).replace("&amp;", "&").strip()


def _boards(context):
    return [(BOARD_TITLE.search(board).group(2).replace("&amp;", "&"), BOARD_TITLE.search(board).group(1), board) for board in BOARD.findall(context.page)]


def _board(context, name):
    found = [board for board in _boards(context) if board[0] == name]
    assert found, f"no board {name!r}; boards are {[board[0] for board in _boards(context)]}"
    return found[0]


def _row_titles(board_markup):
    return [_plain(re.search(r'class="mom-forum-title"[^>]*>(.*?)</a>', row, re.S).group(1)) for row in ROW.findall(board_markup)]


@then("the conversations page has the boards in this order")
def step_boards_in_order(context):
    expected = [row["board"] for row in context.table]
    assert [board[0] for board in _boards(context)] == expected, [board[0] for board in _boards(context)]


@then('the board "{name}" heading links to "{href}"')
def step_board_links(context, name, href):
    assert _board(context, name)[1] == href, _board(context, name)[1]


@then('the board "{name}" heading does not link anywhere')
def step_board_unlinked(context, name):
    assert _board(context, name)[1] is None


@then('the board "{name}" says "{text}" in its heading row')
def step_board_says(context, name, text):
    head = _board(context, name)[2].split("</header>")[0]
    assert text in _plain(head), _plain(head)


@then('in the board "{name}" the conversations come in this order')
def step_board_rows(context, name):
    assert _row_titles(_board(context, name)[2]) == [row["title"] for row in context.table], _row_titles(_board(context, name)[2])


@then('the board "{name}" has {count:d} conversations')
def step_board_count(context, name, count):
    assert len(ROW.findall(_board(context, name)[2])) == count, len(ROW.findall(_board(context, name)[2]))


@then("the conversations page has {count:d} conversation rows in all and none is hidden in the markup")
def step_all_rows(context, count):
    assert len(ROW.findall(context.page)) == count, len(ROW.findall(context.page))
    assert not re.search(r"<li class=\"mom-forum-row\"[^>]*\bhidden\b", context.page)


@then('the row "{title}" shows the title, "{anchor}" as what it is about, the latest author "{author}", "{replies}" and a last activity time with an exact moment')
def step_row_details(context, title, anchor, author, replies):
    row = next((row for row in ROW.findall(context.page) if _plain(re.search(r'class="mom-forum-title"[^>]*>(.*?)</a>', row, re.S).group(1)) == title), None)
    assert row, f"no row {title!r}"
    assert f"On: " in row and anchor in _plain(row), _plain(row)
    assert re.search(rf'class="mom-author mom-author-\w+">{re.escape(author)}</span>', row), row
    assert replies in _plain(row), _plain(row)
    assert re.search(r'<time class="mom-when mom-forum-when" datetime="[^"]+" title="\d{4}-\d\d-\d\d \d\d:\d\d UTC">', row), row


@then('the row "{title}" links its title to "{href}" and what it is about to "{anchor_href}"')
def step_row_links(context, title, href, anchor_href):
    row = next(row for row in ROW.findall(context.page) if f">{title}</a>" in row)
    assert f'class="mom-forum-title" href="{href}"' in row and f'<a href="{anchor_href}">' in row


@then("the header strip counts the boards, conversations and messages and names the most recently active conversation")
def step_strip(context):
    strip = re.search(r'<div class="mom-forum-strip">(.*?)</div><section', context.page, re.S).group(1)
    text = _plain(strip)
    assert re.search(r"\d+ boards?\s*\d+ conversations?\s*\d+ messages?", text), text
    assert "Recently active:" in text and "Who audits the audit log?" in text, text


@then("every mark in the forum is a Lucide icon with words beside it")
def step_marks(context):
    marks = re.findall(r'<span class="mom-forum-mark" title="([^"]*)">(.*?)</span></span>', context.page, re.S)
    assert marks
    for words, inner in marks:
        assert 'data-icon="message-' in inner and 'class="mom-forum-words">' + words in inner, inner[:200]
    assert "mom-forum-mark" in context.page and len({words for words, _ in marks}) == 2, "a conversation with replies and one without are marked differently"


@then('the stylesheet "{path}" gives the forum no border, outline or shadow')
def step_forum_borderless(context, path):
    for version in stylesheet_versions(context, path):
        for selector, body in re.findall(r"([^{}]*\.mom-(?:forum|post(?!-line)|topic|crumbs)[^{}]*)\{([^{}]*)\}", version):
            assert not re.search(r"(?<![\w-])(?:border(?!-radius)|outline|box-shadow)(?:-\w+)*\s*:", body), f"{selector.strip()} draws a border, outline or shadow"


@then("the thread page is a topic with the board breadcrumb {breadcrumb} and the story it discusses")
def step_topic_header(context, breadcrumb):
    crumbs = re.search(r'<nav class="mom-crumbs"[^>]*>(.*?)</nav>', context.page, re.S).group(1)
    assert '<a href="/conversations/">Conversations</a>' in crumbs
    assert breadcrumb.strip('"') in crumbs, crumbs
    assert re.search(r'class="mom-topic-about-label">Discussing</p>', context.page)


@then('the board in the breadcrumb is a link to "{href}"')
def step_crumb_link(context, href):
    assert f'<a href="{href}">' in re.search(r'<nav class="mom-crumbs"[^>]*>(.*?)</nav>', context.page, re.S).group(1)


@then('the board in the breadcrumb is plain text "{name}"')
def step_crumb_plain(context, name):
    crumbs = re.search(r'<nav class="mom-crumbs"[^>]*>(.*?)</nav>', context.page, re.S).group(1)
    assert f"<span>{name}</span>" in crumbs and crumbs.count("<a ") == 1, crumbs


@then("the thread page stacks {count:d} posts numbered {numbers}")
def step_posts(context, count, numbers):
    posts = POST.findall(context.page)
    assert len(posts) == count, len(posts)
    assert [re.search(r'class="mom-post-number" href="#[^"]*">(#\d+)</a>', body).group(1) for _, body in posts] == numbers.split(", ")


@then("every post has an author block on the left with its number, and a time with an exact moment")
def step_post_blocks(context):
    for identifier, body in POST.findall(context.page):
        assert '<aside class="mom-post-author">' in body and body.index("mom-post-author") < body.index("mom-post-main"), identifier
        assert re.search(r'<time class="mom-when" datetime="[^"]+" title="[^"]+">', body), identifier


@then('the post by a reader "{handle}" shows the handle and the role "Reader"')
def step_reader_post(context, handle):
    assert re.search(rf'<span class="mom-post-handle">.*?<span>{handle}</span></span><span class="mom-author mom-author-reader">Reader</span>', context.page, re.S)


@then('the post by "{label}" shows the role label "{label_again}"')
def step_label_post(context, label, label_again):
    assert re.search(rf'<span class="mom-author mom-author-\w+ mom-post-role">.*?<span>{label}</span></span>', context.page, re.S)


@given('a conversation card in the engine\'s markup that names its section "{section}" and is about a story of the section "{story_section}"')
def step_card_with_section(context, section, story_section):
    story = "/articles/synthetic-science-article-1/" if story_section == "Science" else "/articles/synthetic-security-article-1/"
    context.card = (
        f'<article class="home-page-thread" data-anchor="story" data-section="{section}"><div class="home-page-body">'
        f'<p class="home-page-eyebrow home-page-anchor" data-kind="story"><span>Story: <a href="{story}">A story</a></span></p>'
        '<h3 class="home-page-title"><a href="/conversations/aaaaaaaaaaaa/">Sectioned</a></h3>'
        '<p class="home-page-thread-meta"><span class="home-page-count"><span>2 messages</span></span><time datetime="2026-10-31T10:00:00Z">31 Oct 2026</time></p></div></article>'
    )


@given("a conversation card in the engine's markup that names no section and is about a reference")
def step_card_without_section(context):
    context.card2 = (
        '<article class="home-page-thread" data-anchor="reference"><div class="home-page-body">'
        '<p class="home-page-eyebrow home-page-anchor" data-kind="reference"><span>Reference: A paper</span></p>'
        '<h3 class="home-page-title"><a href="/conversations/bbbbbbbbbbbb/">Unsectioned</a></h3>'
        '<p class="home-page-thread-meta"><span class="home-page-count"><span>1 message</span></span><time datetime="2026-10-30T10:00:00Z">30 Oct 2026</time></p></div></article>'
    )


@then('the first is on the board "{first}" and the second is on the board "{second}"')
def step_card_boards(context, first, second):
    pages = [SimpleNamespace(id=f"section-{path}", path=path, title=title, description="") for path, title in (("security", "Privacy & Security"), ("science", "Science"))]
    page = SimpleNamespace(
        settings=SimpleNamespace(pages=pages, sections=[]), site=None,
        entries=[SimpleNamespace(url="/articles/synthetic-security-article-1/", topic="security"), SimpleNamespace(url="/articles/synthetic-science-article-1/", topic="science")],
    )
    threads = hooks._forum_threads(context.card + context.card2)
    assert [hooks._board_of_thread(page, thread).name for thread in threads] == [first, second], [hooks._board_of_thread(page, thread).name for thread in threads]


def _measure_forum(context, route, width):
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return
    result = subprocess.run(["node", str(MEASURE_FORUM_SCRIPT), served_origin(context), route, str(width)], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available")
        return
    context.measured_forum = json.loads(result.stdout)


@when('I draw "{route}" in a browser {width:d} pixels wide')
def step_draw(context, route, width):
    context.width = width
    _measure_forum(context, route, width)


@then("the page does not scroll sideways and nothing in the forum is drawn past the window")
def step_no_sideways(context):
    measured = getattr(context, "measured_forum", None)
    if measured:
        for state in ("before", "after"):
            assert not measured[state]["horizontalScroll"], measured[state]
            assert measured[state]["outside"] == 0, measured[state]


@then("no title, anchor line or number overflows its row and no two rows or posts overlap")
def step_no_overflow(context):
    measured = getattr(context, "measured_forum", None)
    if measured:
        for state in ("before", "after"):
            assert measured[state]["clippedText"] == [], measured[state]["clippedText"]
            assert measured[state]["overlapping"] == 0, measured[state]


@then("the forum has no border, outline or shadow as drawn")
def step_drawn_borderless(context):
    measured = getattr(context, "measured_forum", None)
    if measured:
        assert measured["before"]["bordered"] == 0, measured["before"]


@then("the forum is no wider than {limit:d} pixels")
def step_limit(context, limit):
    measured = getattr(context, "measured_forum", None)
    if measured:
        assert measured["before"]["rootWidth"] <= limit, measured["before"]["rootWidth"]


@then("pressing Load more until it is gone shows all {count:d} conversations")
def step_load_more(context, count):
    measured = getattr(context, "measured_forum", None)
    if measured:
        assert measured["before"]["rowsTotal"] == count
        assert measured["before"]["rowsShown"] < count and measured["before"]["loadMoreButtons"] >= 1, measured["before"]
        assert measured["after"]["rowsShown"] == count and measured["after"]["loadMoreButtons"] == 0 and measured["presses"] >= 1, measured
