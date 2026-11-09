import re
from datetime import date
from types import SimpleNamespace

from behave import given, then, when

SECTION = re.compile(r'<section class="mom-section mom-stories-section" aria-label="([^"]*)" data-rank="(\d+)" data-tier="(\w+)">(.*?)</section>', re.S)
CARD = re.compile(r'<a class="mom-story-card[^"]*"')


def _unescape(text):
    return text.replace("&amp;", "&")


def _sections(context):
    return [(_unescape(label), int(rank), tier, body) for label, rank, tier, body in SECTION.findall(context.page)]


def _section(context, label):
    found = [section for section in _sections(context) if section[0] == label]
    assert found, f"no section {label!r} on the page"
    return found[0]


@then("the page lists its sections in this order")
def step_section_order(context):
    expected = [row["section"] for row in context.table]
    assert [section[0] for section in _sections(context)] == expected, [section[0] for section in _sections(context)]


@then('in the section "{label}" "{first}" comes before "{second}"')
def step_story_order(context, label, first, second):
    body = _section(context, label)[3]
    one, two = body.find(first), body.find(second)
    assert one != -1 and two != -1 and one < two, f"{first!r} at {one}, {second!r} at {two}"


@then('the section "{label}" has the "{tier}" layout')
def step_tier(context, label, tier):
    assert _section(context, label)[2] == tier, _section(context, label)[2]


@then('the section "{label}" has one feature card drawn beside its picture')
def step_feature(context, label):
    body = _section(context, label)[3]
    assert body.count("rh-first rh-solo") == 1 and 'data-count="1"' in body


@then('the section "{label}" has one card across two columns')
def step_wide(context, label):
    assert _section(context, label)[3].count("rh-wide") == 1


@then('the section "{label}" has no featured card and no card across two columns')
def step_plain(context, label):
    body = _section(context, label)[3]
    assert "rh-first" not in body and "rh-wide" not in body, label
    assert len(CARD.findall(body)) > 3


@then("the page has {count:d} sections")
def step_section_count(context, count):
    assert len(_sections(context)) == count, len(_sections(context))


@then('the section "{label}" says it has "{text}"')
def step_says(context, label, text):
    assert f"{text}" in _section(context, label)[3].split("</header>")[0]


@then('the section "{label}" does not say how many stories it has')
def step_says_not(context, label):
    assert " stories" not in _section(context, label)[3].split("</header>")[0]


@then('the section "{label}" links to "{href}" and ends with "{text}"')
def step_links(context, label, href, text):
    head, rest = _section(context, label)[3].split("</header>", 1)
    assert f'<a class="mom-section-title-link" href="{href}"' in head, head
    foot = rest.rsplit("</div>", 1)[-1]
    assert f'<p class="mom-more"><a class="mom-more-link" href="{href}">{text}</a></p>' in _unescape(foot), foot


@then('the section "{label}" links to "{href}" and has no More link')
def step_links_without_more(context, label, href):
    head, rest = _section(context, label)[3].split("</header>", 1)
    assert f'href="{href}"' in head and "mom-more" not in rest, (head, rest)


@then('the section "{label}" has no link to a section page')
def step_no_link(context, label):
    head, rest = _section(context, label)[3].split("</header>", 1)
    assert "<a " not in head and "mom-more" not in rest, (head, rest)


@then("every row on the page is a whole row of one, two or three cards")
def step_rows(context):
    for label, _, tier, body in _sections(context):
        for columns, row in re.findall(r'data-count="(\d)">((?:(?!<div class="papyrus-group).)*)', body, re.S):
            cards = len(CARD.findall(row))
            spans = cards + row.count("rh-wide")
            assert int(columns) in (1, 2, 3) and spans == int(columns), (label, columns, cards)


@then('the page has no section named "{label}"')
def step_no_section(context, label):
    assert label not in [section[0] for section in _sections(context)], label


@then("the page has no featured card and no card across two columns in any section")
def step_none_featured(context):
    assert "rh-first" not in context.page and "rh-wide" not in context.page


@then('the file "{path}" contains "{text}"')
def step_file_contains(context, path, text):
    assert text in (context.output_directory / path).read_text(encoding="utf-8"), f"{path} lacks {text!r}"


@then('the page "{route}" was not projected')
def step_not_projected(context, route):
    assert not (context.output_directory / route.strip("/") / "index.html").exists(), route


@then('the file "{path}" does not contain "{text}"')
def step_file_lacks(context, path, text):
    assert text not in (context.output_directory / path).read_text(encoding="utf-8"), f"{path} has {text!r}"


@then('the navigation lists "{labels}" in that order')
def step_nav_order(context, labels):
    nav = context.page.split('class="mom-nav"', 1)[1].split("</nav>", 1)[0]
    shown = re.findall(r'<a class="[^"]*mom-nav-pill[^"]*"[^>]*>([A-Za-z]+)</a>', nav)
    assert shown == labels.split(", "), shown


@then('the page redirects to "{href}"')
def step_redirects(context, href):
    assert f'<meta http-equiv="refresh" content="0; url={href}">' in context.page


@then('the page names "{href}" as its canonical address')
def step_canonical(context, href):
    assert f'<link rel="canonical" href="{href}">' in context.page


# ---- the ranking: Papyrus core's `rank_entries` (what `page.ranked` runs) applied to a small set of stories

WEEK_DAY = date(2026, 11, 8)


def _ranked_story(title, topic, day, kind, lineage):
    section = SimpleNamespace(is_type=False, label=topic, base=topic.lower())
    return SimpleNamespace(type=kind, title=title, url=f"/{lineage}/", topic=topic.lower().replace(" & ", "-"), updated=day, date=day, section=section,
                           summary=SimpleNamespace(lineage_id=lineage))


def _kind(noun):
    return noun.strip()


@given('two {noun}s of "Math & Science" and two of "History" published this week, {rating}')
def step_ranked_set(context, noun, rating):
    kind = _kind(noun)
    context.story_kind = kind
    context.story_stars = {}
    context.stories = [
        _ranked_story("science-new", "Math & Science", "2026-11-08", kind, "science-new"),
        _ranked_story("science-old", "Math & Science", "2026-11-07", kind, "science-old"),
        _ranked_story("history-new", "History", "2026-11-06", kind, "history-new"),
        _ranked_story("history-old", "History", "2026-11-04", kind, "history-old"),
    ]
    if "five stars" in rating:
        context.story_stars = {"history-old": 5}


@when("the {noun}s are grouped for the {page_name} page")
def step_group_ranked(context, noun, page_name):
    from papyrus_content.projection.standard.story_order import rank_entries

    import hooks

    rank = lambda entries: rank_entries(entries, context.story_stars, "week", WEEK_DAY)
    original = hooks._topic_label
    hooks._topic_label = lambda entry: entry.section.label
    try:
        context.grouped = [(label, [entry.title for entry in found]) for label, found in hooks._stories_by_section(context.stories, context.story_kind, rank)]
    finally:
        hooks._topic_label = original


@then('the first section is "{label}" and its first {noun} is the rated one')
def step_first_rated(context, label, noun):
    assert context.grouped[0] == (label, ["history-old", "history-new"]), context.grouped


@then('the first section is "{label}" and its first {noun} is the newest')
def step_first_newest(context, label, noun):
    assert context.grouped[0] == (label, ["science-new", "science-old"]), context.grouped


@then('the sections are "{labels}"')
def step_group_labels(context, labels):
    assert [label for label, _ in context.grouped] == labels.split(", "), context.grouped
