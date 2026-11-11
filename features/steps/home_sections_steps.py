"""Steps for features/home-sections.feature.

The scenarios on the projected fixtures read the home page the engine draws. The scenarios that need a particular set of topic sections, videos or concepts (the
fixtures name none of the sections the home page lists) build the markup the engine hands the hooks and call the hooks on it.
"""

import re
import sys
from types import SimpleNamespace

from behave import given, then, when

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "web"))

import hooks  # noqa: E402

SECTION_OPENING = '<section class="mom-section'
GROUP = re.compile(r'<section class="papyrus-group[^>]*data-section="([^"]*)"[^>]*data-count="(\d+)">(.*?)</section>', re.S)
VIDEO_NUMBER = re.compile(r"https://video\.example/(\d+)")


def _section(html: str, marker: str) -> str:
    start = html.index(marker)
    return html[start:html.index("</section>", start)]


def _numbers(markup: str) -> list[int]:
    return [int(number) for number in VIDEO_NUMBER.findall(markup)]


# ---------------------------------------------------------------------------------------------- the projected home page

@then("the home page's top row has the lead and the site title card and no conversations")
def step_top_row(context):
    html = context.page
    top = html[html.index('class="mom-home-top'):html.index('<div class="rh-features">')]
    assert "mom-home-lead" in top and "mom-sticker" in top
    assert "Conversations" not in top and "mom-thread-card" not in top and "home-page-thread" not in top and "mom-post-line" not in top, top[:600]


@then('these home page sections come in this order: "{markers}"')
def step_section_order(context, markers):
    position = 0
    for marker in markers.split(", "):
        found = context.page.find(marker, position)
        assert found != -1, f"{marker!r} does not come after the one before it"
        position = found + 1


@then("the Concepts section is the last section of the home page")
def step_concepts_last(context):
    html = context.page
    main = html[html.index("<main"):html.index("</main>")] if "</main>" in html else html[html.index("<main"):]
    last = main.rindex(SECTION_OPENING)
    assert main[last:].startswith('<section class="mom-section rh-concepts"'), main[last:last + 120]


@then('the home page section "{title}" has the heading with the link "{text}" to "{href}"')
def step_standard_heading(context, title, text, href):
    heading = re.search(
        rf'<div class="mom-section-head"><h2 id="mom-home-[a-z]+" class="mom-section-title">{re.escape(title)}</h2><a class="mom-section-link" href="{re.escape(href)}">{re.escape(text)}</a></div>',
        context.page,
    )
    assert heading, f"no standard heading for {title}"


@then("the Videos section shows at most {count:d} video cards, each once on the page")
def step_videos_section(context, count):
    section = _section(context.page, '<section class="mom-section rh-videos"')
    links = re.findall(r'<a class="mom-reference-card" href="([^"]*)"', section)
    assert 0 < len(links) <= count, links
    for link in links:
        assert context.page.count(f'<a class="mom-reference-card" href="{link}"') == 1, f"{link} is on the page more than once"


@then("the Conversations section shows between {fewest:d} and {most:d} thread cards")
def step_conversations_section(context, fewest, most):
    section = _section(context.page, '<section class="mom-section rh-conversations"')
    cards = section.count('class="mom-thread-card"')
    assert fewest <= cards <= most, cards


@then("the Concepts section is a concept grid with at most {most:d} cards, the most associated first")
def step_concepts_section(context, most):
    section = _section(context.page, '<section class="mom-section rh-concepts"')
    assert '<div class="mom-wiki-grid mom-home-concepts">' in section
    cards = re.findall(r'<a class="mom-wiki-card"[^>]*>', section)
    assert 0 < len(cards) <= most, len(cards)
    counts = [int(found.group(1)) if (found := re.search(r'data-associations="(\d+)"', card)) else -1 for card in cards]
    assert counts == sorted(counts, reverse=True), counts
    index = re.search(r'<div class="mom-wiki-grid">(.*?)</div>', __import__("projection_support").page_text(context.output_directory, "/wiki/"), re.S)
    if index:
        index_links = re.findall(r'<a class="mom-wiki-card" href="([^"]*)"', index.group(1))
        assert re.findall(r'<a class="mom-wiki-card" href="([^"]*)"', section) == index_links[:len(cards)], "not the order of the concept index"


def _outside_groups(html: str) -> str:
    return GROUP.sub("", html)


@then('no "Worth Watching" card is outside a topic section')
def step_no_floating_card(context):
    assert "mom-worth-watching" not in _outside_groups(context.page)
    assert "home-page-heading\">Worth Watching" not in context.page


@then('every "Worth Watching" card is in a topic section that the home page\'s list names')
def step_cards_in_listed_sections(context):
    for name, _count, inside in GROUP.findall(context.page):
        if "mom-worth-watching" in inside:
            assert name in hooks.HOME_WORTH_WATCHING_SECTIONS, name
            assert 1 <= len(re.findall(r'<li>', _section_div(inside))) <= hooks.HOME_WORTH_WATCHING_VIDEOS


def _section_div(inside: str) -> str:
    start = inside.index('<div class="mom-worth-watching"')
    return inside[start:inside.index("</ul>", start)]


@then('the stylesheet "{path}" draws the Worth Watching card as a flat panel across the columns of its section')
def step_stylesheet(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    rule = re.search(r"\.rh-group > \.mom-worth-watching \{([^}]*)\}", text)
    assert rule, "no rule for the card"
    assert "grid-column: 1 / -1" in rule.group(1) and "background: var(--brand)" in rule.group(1) and "border-radius" in rule.group(1)
    assert "border:" not in rule.group(1) and "outline" not in rule.group(1) and "box-shadow" not in rule.group(1)


# ---------------------------------------------------------------------------------------------- a home page made for the scenario

def _group_markup(name: str, cards: int) -> str:
    stories = "".join(f'<a class="mom-story-card" href="/articles/{name}-{number}/">{name} story {number}</a>' for number in range(1, cards + 1))
    return (
        f'<section class="papyrus-group rh-group papyrus-has-lead" data-section="{name}" data-label="{name}" data-index="0" data-count="{cards}">'
        f'<header class="papyrus-group-head"><h2 class="papyrus-group-title">{name}</h2></header>{stories}<p class="mom-more"><a class="mom-more-link" href="/{name}/">More {name}…</a></p></section>'
    )


def _tile(number: int) -> str:
    return (
        f'<li><article class="home-page-tile" data-status="accepted"><h3 class="home-page-title"><a href="https://video.example/{number}">Video {number}</a></h3></article></li>'
    )


@given('a home page with the topic sections "{sections}"')
def step_home_page(context, sections):
    context.group_names = []
    context.groups = ""
    for entry in sections.split(", "):
        name, _, cards = entry.partition(":")
        context.group_names.append(name)
        context.groups += _group_markup(name, int(cards or 2))
    context.videos = 0


@given("the engine offers {count:d} videos, best first")
def step_engine_videos(context, count):
    context.videos = count


@given("the site has no advertisements")
def step_no_ads(context):
    original = hooks._advertisements
    hooks._advertisements = lambda: []
    context.add_cleanup(setattr, hooks, "_advertisements", original)


def _home_markup(context) -> str:
    tiles = "".join(_tile(number) for number in range(1, context.videos + 1))
    region = f'<!--home:videos--><section class="home-page-references"><ul class="home-page-grid">{tiles}</ul></section><!--/home:videos-->'
    return f'<div class="rh-features">{context.groups}</div>{region}'


@when("the home page's videos are placed")
def step_place_videos(context):
    context.html = hooks._home_videos(_home_markup(context))


@then('the "Worth Watching" cards are in "{names}" with videos "{videos}"')
def step_cards(context, names, videos):
    placed = {name: _numbers(_section_div(inside)) for name, _count, inside in GROUP.findall(context.html) if "mom-worth-watching" in inside}
    expected_names = [name for name in names.split(", ") if name]
    expected_videos = [[int(number) for number in group.split()] for group in videos.split(", ") if group.strip()]
    assert list(placed) == expected_names, placed
    assert [placed[name] for name in expected_names] == expected_videos, placed
    assert all(1 <= len(found) <= hooks.HOME_WORTH_WATCHING_VIDEOS for found in placed.values())


@then('the Videos section shows videos "{videos}"')
def step_videos_shown(context, videos):
    expected = [] if videos == "none" else [int(number) for number in videos.split()]
    if not expected:
        assert "rh-videos" not in context.html
        return
    assert _numbers(_section(context.html, '<section class="mom-section rh-videos"')) == expected
    assert 'id="mom-home-videos"' in context.html and ">All videos<" in context.html


@then("every video is on the page once")
def step_once(context):
    numbers = _numbers(context.html)
    assert len(numbers) == len(set(numbers)), numbers
    assert set(numbers) <= set(range(1, context.videos + 1))


@then('the page has no "Worth Watching" card and no Videos section')
def step_nothing(context):
    assert "mom-worth-watching" not in context.html and "rh-videos" not in context.html and "Worth Watching" not in context.html
    assert "<!--home:videos-->" not in context.html and "@@home-videos@@" not in context.html


@when("the home page's advertisement cards are placed")
def step_place_ads(context):
    context.html = hooks._home_ad_cards(context.groups, SimpleNamespace(path="/"))


@then('an advertisement card is in "{names}" and nowhere else, and each of those sections has {columns:d} columns')
def step_ads(context, names, columns):
    expected = names.split(", ")
    with_ad = {name: count for name, count, inside in GROUP.findall(context.html) if 'data-ad=' in inside}
    assert sorted(with_ad) == sorted(expected), with_ad
    assert all(int(count) == columns for count in with_ad.values()), with_ad
    assert context.html.count('data-ad=') == len(expected)


@then("no advertisement card is on the page")
def step_no_ad(context):
    assert "data-ad=" not in context.html and "mom-ad" not in context.html


@when("the home page's conversations are made from a page with no conversations")
def step_conversations_none(context):
    context.html = hooks._home_conversations('<!--home:conversations--><section class="home-page-threads"><p class="home-page-empty">None</p></section><!--/home:conversations-->')


# ---------------------------------------------------------------------------------------------- concepts

@given("a site with {count:d} concepts")
def step_concepts_site(context, count):
    concepts = [
        SimpleNamespace(type=hooks.WIKI_TYPE, url=f"/wiki/concept-{number}/", title=f"Concept {number}", summary_text="" if number % 3 == 0 else f"What concept {number} means.", tags=[], data={})
        for number in range(count)
    ]
    context.use_counts = {number: (number * 7) % 11 for number in range(count)}
    stories = []
    for number, uses in context.use_counts.items():
        stories += [SimpleNamespace(type="article", url=f"/articles/s-{number}-{use}/", title=f"S {number} {use}", tags=[f"Concept {number}"], data={}) for use in range(uses)]
    context.page_for_concepts = SimpleNamespace(entries=concepts + stories, site=None)


@when("the home page's Concepts section is made")
def step_make_concepts(context):
    context.html = hooks._home_concepts(context.page_for_concepts)


@then('it holds {count:d} concept cards, the most associated first, and the link "{text}" to "{href}"')
def step_concepts_made(context, count, text, href):
    cards = re.findall(r'<a class="mom-wiki-card" href="([^"]*)"', context.html)
    expected = [f"/wiki/concept-{number}/" for number, _uses in sorted(context.use_counts.items(), key=lambda item: -item[1])][:count]
    assert cards == expected, (cards, expected)
    assert f'<a class="mom-section-link" href="{href}">{text}</a>' in context.html


@then("the cards without a definition have no definition text")
def step_no_definition(context):
    for number in range(20):
        card = re.search(rf'<a class="mom-wiki-card" href="/wiki/concept-{number}/"[^>]*>.*?</a>', context.html, re.S)
        if card:
            assert ("mom-wiki-card-definition" in card.group(0)) == (number % 3 != 0), card.group(0)


@then("the section is not drawn")
def step_not_drawn(context):
    assert getattr(context, "html", "") == "" or context.html.strip() == ""
