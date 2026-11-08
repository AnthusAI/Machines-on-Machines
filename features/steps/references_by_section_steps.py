import re

from behave import then, when

SECTION = re.compile(r'<section class="mom-section mom-refs-section" aria-label="([^"]*)" data-rank="(\d+)" data-tier="(\w+)">(.*?)</section>', re.S)


def _sections(context):
    return [(label.replace("&amp;", "&"), int(rank), tier, body) for label, rank, tier, body in SECTION.findall(context.page)]


def _section(context, label):
    found = [section for section in _sections(context) if section[0] == label]
    assert found, f"no section {label!r}: {[section[0] for section in _sections(context)]}"
    return found[0]


@when('I read the Markdown twin "{route}"')
def step_twin(context, route):
    context.page = (context.output_directory / route.strip("/")).read_text(encoding="utf-8")


@then('the page has a section named "{label}"')
def step_has_section(context, label):
    _section(context, label)


@then("the references sections appear in this order")
def step_order(context):
    assert [section[0] for section in _sections(context)] == [row["section"] for row in context.table], [section[0] for section in _sections(context)]


@then('in the references section "{label}" "{first}" comes before "{second}"')
def step_item_order(context, label, first, second):
    body = _section(context, label)[3]
    one, two = body.find(first), body.find(second)
    assert one != -1 and two != -1 and one < two, f"{first!r} at {one}, {second!r} at {two}"


@then('the references section "{label}" has the "{tier}" layout')
def step_tier(context, label, tier):
    assert _section(context, label)[2] == tier


@then('the references section "{label}" has the "{tier}" layout with one card on its own row')
def step_feature(context, label, tier):
    body = _section(context, label)[3]
    assert _section(context, label)[2] == tier and body.count('data-count="1"') == 1 and body.index('data-count="1"') < body.index('data-count="2"' if 'data-count="2"' in body else 'data-count="3"')


@then("no card on the page links to the same address twice")
def step_unique(context):
    hrefs = re.findall(r'<a class="mom-reference-card" href="([^"]*)"', context.page)
    assert hrefs and len(hrefs) == len(set(hrefs)), hrefs


@then('the stylesheet "{path}" gives a row of one, two or three References its own columns on every width')
def step_css(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    for count in (1, 2, 3):
        assert f'.mom-page .home-page-grid.mom-refs-row[data-count="{count}"]' in text
    assert ".mom-page .home-page-grid.mom-refs-row[data-count] { grid-template-columns: minmax(0, 1fr); }" in text


def _section_parts(context, label):
    body = _section(context, label)[3]
    head, rest = body.split("</header>", 1)
    return head, rest


@then('the references section "{label}" links to "{href}" and ends with "{text}"')
def step_links(context, label, href, text):
    head, rest = _section_parts(context, label)
    assert f'<a class="mom-section-title-link" href="{href}"' in head, head
    assert f'<p class="mom-more"><a class="mom-more-link" href="{href}">{text}</a></p>' in rest.replace("&amp;", "&"), rest[-300:]


@then('the references section "{label}" links to "{href}" and has no More link')
def step_links_without_more(context, label, href):
    head, rest = _section_parts(context, label)
    assert f'href="{href}"' in head and "mom-more" not in rest, (head, rest[-300:])


@then('the references section "{label}" has no link to a section page')
def step_no_link(context, label):
    head, rest = _section_parts(context, label)
    assert "mom-section-title-link" not in head and "mom-more" not in rest, (head, rest[-300:])


@then("no block head shows a count")
def step_no_count(context):
    assert _sections(context)
    for _label, _rank, _tier, body in _sections(context):
        assert "papyrus-group-more" not in body and not re.search(r"\d+ (videos|findings)", body.split("</header>")[0]), body[:200]
