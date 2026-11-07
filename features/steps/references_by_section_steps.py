import re
import sys
from pathlib import Path

from behave import then, when

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "web"))
import hooks  # noqa: E402

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


@then("the not-accepted list is one row of three")
def step_panel_rows(context):
    panel = context.page.split("mom-refs-panel-rows")[1]
    assert re.findall(r'mom-refs-row" data-card="tile" data-count="(\d)"', panel) == ["3"]


@then("sixteen not-accepted sources are in rows of three, with a closing two rows of two")
def step_sixteen(context):
    tiles = "".join('<li><article class="home-page-tile" data-status="recommended">x</article></li>' for _ in range(16))
    html = hooks._group_references(f'<div class="mom-by-rows"><section class="home-page-references">{tiles}</section></div>')
    assert re.findall(r'data-count="(\d)"', html) == ["3", "3", "3", "3", "2", "2"]


@then("a page with no accepted References keeps its plain empty text and has no section")
def step_empty(context):
    html = hooks._group_references('<div class="mom-by-section"><p class="home-page-empty">Nothing yet.</p></div>')
    assert "Nothing yet." in html and "mom-refs-section" not in html and "<h2" not in html
