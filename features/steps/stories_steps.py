import re

from behave import then

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


@then('the section "{label}" links to "{href}"')
def step_links(context, label, href):
    head = _section(context, label)[3].split("</header>")[0]
    assert f'href="{href}"' in head and f"More in {label}" in _unescape(head), head


@then('the section "{label}" has no link to a section page')
def step_no_link(context, label):
    assert "<a " not in _section(context, label)[3].split("</header>")[0]


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
