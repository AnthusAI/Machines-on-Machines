import re
import sys
from pathlib import Path
from types import SimpleNamespace

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


@then("a page with no accepted References keeps its plain empty text and has no section")
def step_empty(context):
    html = hooks._group_references('<div class="mom-by-section"><p class="home-page-empty">Nothing yet.</p></div>', lambda name: None)
    assert "Nothing yet." in html and "mom-refs-section" not in html and "<h2" not in html


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


# --- the paged list of References with no section ---

import json  # noqa: E402

FIXTURE_REFERENCES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "_data" / "home-page" / "references.json"
CARD_ADDRESS = re.compile(r'<a class="mom-reference-card" href="([^"]*)"')


def _fixture_accepted(medium):
    records = json.loads(FIXTURE_REFERENCES.read_text())["references"]
    return [record for record in records if record["status"] == "accepted" and (medium is None or record.get("medium") == medium)]


def _untagged_region(page):
    start = page.index('<section class="mom-section mom-untagged"')
    end = page.find('<section class="mom-panel', start)
    return page[start:end if end != -1 else len(page)]


def _reached_through_the_list(context):
    """Every address the list reaches: its first page, then each data file the Load more control names, to the end."""
    region = _untagged_region(context.page)
    addresses = CARD_ADDRESS.findall(region)
    source = re.search(r'data-reference-more data-src="([^"]*)"', region)
    context.data_files = []
    while source:
        context.data_files.append(source.group(1))
        document = json.loads((context.output_directory / source.group(1).lstrip("/")).read_text())
        addresses += CARD_ADDRESS.findall(document["html"])
        source = type("Next", (), {"group": lambda self, _: document["next"]})() if document["next"] else None
    return addresses


@then('the list headed "{heading}" shows only References with no section and has no link')
def step_untagged_heading(context, heading):
    region = _untagged_region(context.page)
    assert f'<h2 class="mom-section-title">{heading}</h2>' in region and "<a class=\"mom-section-title-link\"" not in region
    assert 'data-kind="section"' not in region


@then("the list has a Load more control and a data file that reaches the rest")
def step_load_more(context):
    region = _untagged_region(context.page)
    assert "data-reference-more" in region and 'class="home-page-load-more"' in region, "no Load more control"
    _reached_through_the_list(context)
    assert context.data_files and all((context.output_directory / name.lstrip("/")).is_file() for name in context.data_files)


@then("the first page of the list has at most {count:d} cards")
def step_first_page(context, count):
    assert len(CARD_ADDRESS.findall(_untagged_region(context.page))) <= count


@then("the list reaches every {kind} with no section exactly once")
def step_reaches_all(context, kind):
    expected = [record["url"] for record in _fixture_accepted("video" if kind == "video" else None) if not record.get("section")]
    reached = _reached_through_the_list(context)
    assert sorted(reached) == sorted(expected) and len(reached) == len(set(reached)), (len(reached), len(expected))
    assert len(expected) > 50


@then("the list is newest first")
def step_newest_first(context):
    archive = {record["url"]: record["acceptedAt"] for record in _fixture_accepted(None) if record["title"].startswith("Fixture talk: archive number")}
    reached = [archive[address] for address in _reached_through_the_list(context) if address in archive]
    assert len(reached) == 60 and reached == sorted(reached, reverse=True)


@then("a page of the list that a reader without a script can follow is in the site")
def step_chunk_pages(context):
    page = context.output_directory / re.search(r'data-reference-more data-src="([^"]*)\.json"', context.page).group(1).lstrip("/") / "index.html"
    html = page.read_text(encoding="utf-8")
    assert "mom-reference-card" in html and 'rel="next"' in html or "Next" in html
    assert 'data-kind="section"' not in html


@then('the full video list of the section "{label}" at "{route}" shows all {count:d} of its videos')
def step_section_video_list(context, label, route, count):
    from projection_support import page_text
    page = page_text(context.output_directory, route)
    shown = len(CARD_ADDRESS.findall(page))
    own = [record for record in _fixture_accepted("video") if record.get("section") == label]
    assert shown == len(own) == count, (shown, len(own))


@then('a Reference list page with no section groups is headed "{plain}" and one with groups is headed "{grouped}"')
def step_headings(context, plain, grouped):
    region = '<section class="mom-section mom-untagged" data-noun="videos" aria-label="Videos">\n<!--sf:untagged-heading-->\n<ul></ul>\n<!--/sf:untagged-->\n</section>'
    page = SimpleNamespace(kind="custom", path="/videos/")
    assert f'<h2 class="mom-section-title">{plain}</h2>' in hooks._untagged_lists(region, page)
    assert f'<h2 class="mom-section-title">{grouped}</h2>' in hooks._untagged_lists('<section class="mom-section mom-refs-section">' + region.replace("<ul></ul>", '<ul data-reference-more></ul>'), page)


@then('the file "{path}" exists in the site')
def step_file_exists(context, path):
    assert (context.output_directory / path).is_file(), path


@then('the stylesheet "{path}" gives the list of everything its own room and hides it when it is empty')
def step_paged_css(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-untagged, .mom-all-refs { margin-top: var(--space-12); }" in text
    assert ".mom-untagged:not(:has(a, .home-page-empty)), .mom-all-refs:not(:has(a, .home-page-empty)) { display: none; }" in text
