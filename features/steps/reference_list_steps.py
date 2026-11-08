"""Steps for features/reference-lists.feature and features/section-lists.feature: the Videos, Findings and section list pages in every case.

Cases come from tests/reference_cases.py. A page "reaches" a Reference when the Reference is in the lead, in the first page of the list, or in a data file
found by following the Load more control to the end; the data files are written through the site's hook like the page.
The `@browser` scenarios draw the projected case through tools/measure_reference_lists.cjs and skip themselves when Node or Playwright is missing.
"""

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from html import unescape

from behave import given, then, when

from image_ratio_steps import served_directory_origin  # noqa: E402
from projection_support import REPOSITORY_ROOT, project_reference_case  # noqa: E402

MEASURE_SCRIPT = REPOSITORY_ROOT / "tools" / "measure_reference_lists.cjs"
CARD_ADDRESS = re.compile(r'<a class="mom-reference-card" href="([^"]*)"')
LEAD = re.compile(r'<section class="mom-section mom-refs-lead"[^>]*>(.*?)</section>', re.S)
BLOCK = re.compile(r'<section class="mom-section mom-refs-section" aria-label="([^"]*)" data-rank="(\d+)" data-tier="(\w+)">(.*?)</section>', re.S)
HEADING = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.S)
ROW_COUNT = re.compile(r'<ul class="home-page-grid mom-refs-row" data-card="tile" data-count="(\d+)">')
QUOTED = re.compile(r'"([^"]*)"')
WEEK_DAYS = 7
PHONE_MAX_WIDTH = 600      # tools/scale_css.py: from 600px the site renders at 75%, so the designed 640 and 900 breakpoints are 480 and 675 wide, and the designed phone rules end at 599
LAPTOP_MIN_WIDTH = 675


def _plain(markup):
    return unescape(re.sub(r"<[^>]+>", "", markup)).strip()


def _case(context, case, declares_sections=True):
    key = (case, declares_sections)
    if key not in context.reference_cases:
        context.reference_cases[key] = project_reference_case(case, declares_sections)
    context.case_directory, context.expected = context.reference_cases[key]
    context.declares_sections = declares_sections


def _read(context, route):
    target = context.case_directory / route.strip("/") / "index.html"
    assert target.exists(), f"{route} was not projected"
    return target.read_text(encoding="utf-8")


def _main(page):
    return page[page.index("<main"):page.index("</main>")]


def _lead_markup(page):
    found = LEAD.search(page)
    return found.group(1) if found else ""


def _stream_markup(page):
    return page[page.index("mom-refs-stream"):] if "mom-refs-stream" in page else ""


def _blocks(page):
    return [(unescape(label), int(rank), tier, body) for label, rank, tier, body in BLOCK.findall(page)]


def _data_files(context, stream):
    """The addresses in every data file the Load more control reaches, in order, and the files themselves."""
    found = re.search(r'data-reference-more data-src="([^"]*)"', stream)
    source = found.group(1) if found else None
    addresses, files = [], []
    while source:
        files.append(source)
        document = json.loads((context.case_directory / source.lstrip("/")).read_text(encoding="utf-8"))
        addresses += CARD_ADDRESS.findall(document["html"])
        source = document["next"]
    return addresses, files


def _list_kind(context, route):
    context.list_kind = "findings" if "findings" in route else "videos"


def _reached(context):
    page = context.page
    stream = _stream_markup(page)
    from_data, context.data_files = _data_files(context, stream)
    return CARD_ADDRESS.findall(_lead_markup(page)), CARD_ADDRESS.findall(stream), from_data


@given('the "{case}" Reference case is projected')
def step_case(context, case):
    _case(context, case)


@given('the "{case}" Reference case is projected for a publication that declares no sections')
def step_case_without_sections(context, case):
    _case(context, case, declares_sections=False)


@when('I open the case page "{route}"')
def step_open_case_page(context, route):
    context.route = route
    _list_kind(context, route)
    context.page = _read(context, route)


@then("the page has no heading other than its title")
def step_only_the_title(context):
    headings = [(level, _plain(text)) for level, text in HEADING.findall(_main(context.page))]
    assert len(headings) == 1 and headings[0][0] == "1", headings


@then("the lead has {count:d} cards, in rows of {sizes} and no heading")
def step_lead_rows(context, count, sizes):
    lead = _lead_markup(context.page)
    assert lead, "no lead"
    wanted = [int(size) for size in re.findall(r"\d+", sizes)]
    assert [int(size) for size in ROW_COUNT.findall(lead)] == wanted, ROW_COUNT.findall(lead)
    assert len(CARD_ADDRESS.findall(lead)) == count
    assert not HEADING.search(lead)


@then("the list has no heading, shows {count:d} cards on its first page and has a Load more link")
def step_stream(context, count):
    stream = _stream_markup(context.page)
    assert stream and not HEADING.search(stream.split("</main>")[0]), "the list has a heading"
    assert len(CARD_ADDRESS.findall(stream.split("</main>")[0])) == count, len(CARD_ADDRESS.findall(stream.split("</main>")[0]))
    assert "data-reference-more" in stream and 'class="home-page-load-more"' in stream


@then("the lead and the list reach all {count:d} {kind:w} exactly once")
def step_reach_all(context, count, kind):
    lead, first, more = _reached(context)
    reached = lead + first + more
    expected = context.expected[kind]["unfiled" if context.declares_sections else "urls"]   # with no section declared, every Reference is in no section
    assert len(reached) == len(set(reached)) == count, (len(reached), len(set(reached)), count)
    assert sorted(reached) == sorted(expected)


@then("the lead and the list reach all {count:d} {kind} filed under \"{label}\" exactly once")
def step_reach_section(context, count, kind, label):
    lead, first, more = _reached(context)
    reached = lead + first + more
    expected = context.expected[kind]["by_section"][label]
    assert len(reached) == len(set(reached)) == count == len(expected), (len(reached), len(set(reached)), count)
    assert reached == expected, "the section list is not in the shared order"


@then("the page has no block for any section")
def step_no_blocks(context):
    assert "mom-refs-section" not in context.page


@then("the page has no lead")
def step_no_lead(context):
    assert "mom-refs-lead" not in context.page


@then("the lead holds the {count:d} best unfiled {kind} in the shared order")
def step_lead_best(context, count, kind):
    lead = CARD_ADDRESS.findall(_lead_markup(context.page))
    assert lead == context.expected[kind]["unfiled"][:count], (lead, context.expected[kind]["unfiled"][:count])


@then("the page has blocks for {have} and none for {lack}")
def step_blocks(context, have, lack):
    labels = [label for label, _rank, _tier, _body in _blocks(context.page)]
    assert labels == QUOTED.findall(have), labels
    assert not set(labels) & set(QUOTED.findall(lack))


@then("the list holds every unfiled {kind} that the lead does not")
def step_list_rest(context, kind):
    lead, first, more = _reached(context)
    assert sorted(first + more) == sorted(set(context.expected[kind]["unfiled"]) - set(lead))


@then('the "{label}" {kind} are in the lead or the list and say their section on the card')
def step_pageless(context, label, kind):
    lead, first, more = _reached(context)
    addresses = context.expected[kind]["pageless"]
    assert addresses and set(addresses) <= set(lead + first + more), addresses
    shown = [address for address in addresses if address in lead + first]
    assert shown, "none of them is on the page itself"
    for address in shown:
        card = re.search(rf'<a class="mom-reference-card" href="{re.escape(address)}">.*?</a>', context.page, re.S).group(0)
        assert f" · {label} · " in _plain(card) or f"{label}" in _plain(card), card
    for file in context.data_files:
        document = json.loads((context.case_directory / file.lstrip("/")).read_text(encoding="utf-8"))
        for card in re.findall(r'<a class="mom-reference-card".*?</a>', document["html"], re.S):
            if CARD_ADDRESS.search(card).group(1) in addresses:
                assert label in _plain(card), card


@then("no address appears twice across the lead, the blocks, the list and its data files")
def step_no_repeats(context):
    lead, first, more = _reached(context)
    blocks = [address for _label, _rank, _tier, body in _blocks(context.page) for address in CARD_ADDRESS.findall(body)]
    everything = lead + blocks + first + more
    assert len(everything) == len(set(everything)), [address for address in set(everything) if everything.count(address) > 1][:5]


@then("every {kind} in a block is filed under that block's section")
def step_blocks_are_filed(context, kind):
    for label, _rank, _tier, body in _blocks(context.page):
        assert set(CARD_ADDRESS.findall(body)) <= set(context.expected[kind]["by_section"][label]), label


@then("the page has no lead, no list, no Load more link and no empty sentence")
def step_nothing_but_blocks(context):
    for marker in ("mom-refs-lead", "mom-refs-stream", "data-reference-more", "home-page-empty", "have been accepted yet", "Nothing has been accepted"):
        assert marker not in _main(context.page), marker


@then("the page has no lead, no Load more link and no block")
def step_nothing(context):
    for marker in ("mom-refs-lead", "data-reference-more", "mom-refs-section"):
        assert marker not in context.page, marker


@then('the first block is "{label}" with the "{tier}" layout')
def step_first_block(context, label, tier):
    first = _blocks(context.page)[0]
    assert (first[0], first[2]) == (label, tier), first[:3]


@then("the lead holds both unfiled {kind} in one row of {size:d}")
def step_few(context, kind, size):
    lead = _lead_markup(context.page)
    assert [int(count) for count in ROW_COUNT.findall(lead)] == [size]
    assert CARD_ADDRESS.findall(lead) == context.expected[kind]["unfiled"] and len(context.expected[kind]["unfiled"]) == size


@then("the page has no list and no Load more link")
def step_no_list(context):
    assert "mom-refs-stream" not in context.page and "data-reference-more" not in context.page


@then('no page exists at "{route}" in the case')
def step_no_page(context, route):
    assert not (context.case_directory / route.strip("/") / "index.html").exists()


def _snapshot_videos(context):
    data = json.loads((context.case_directory / "_data" / "home-page" / "references.json").read_text(encoding="utf-8"))
    return [record for record in data["references"] if record["status"] == "accepted" and record.get("medium") == "video"]


def _accepted_on(record):
    return datetime.fromisoformat(record["acceptedAt"].replace("Z", "+00:00")).date()


@then("the first card of the lead is this week's highest-starred video")
def step_first_is_starred(context):
    today = datetime.now(timezone.utc).date()
    this_week = [record for record in _snapshot_videos(context) if (today - _accepted_on(record)).days < WEEK_DAYS]
    best = max(record.get("stars", 0) for record in this_week)
    assert best >= 3
    first = CARD_ADDRESS.findall(_lead_markup(context.page))[0]
    leader = min((record for record in this_week if record.get("stars", 0) == best), key=lambda record: record["rank"])
    assert first == leader["url"], (first, leader["url"])


@then("the video with five stars, accepted 20 days ago, comes after every video accepted in the last seven days")
def step_old_five_star(context):
    today = datetime.now(timezone.utc).date()
    lead, first, more = _reached(context)
    reached = lead + first + more
    videos = _snapshot_videos(context)
    old = next(record for record in videos if record.get("stars") == 5)
    assert (today - _accepted_on(old)).days >= 20 - 1
    this_week = [record["url"] for record in videos if (today - _accepted_on(record)).days < WEEK_DAYS]
    assert this_week and all(reached.index(address) < reached.index(old["url"]) for address in this_week)


@then("a data file of the list is also a page with the site's chrome and Previous and Next links")
def step_chunk_pages(context):
    _reached(context)
    assert len(context.data_files) >= 2
    middle = context.case_directory / context.data_files[1].lstrip("/").removesuffix(".json") / "index.html"
    html = middle.read_text(encoding="utf-8")
    assert "mom-footer" in html and "mom-masthead" in html or "<nav" in html
    assert 'rel="next"' in html and "Previous" in html and "mom-reference-card" in html


@then('no videos appear on "{first}", its data files, "{second}"{rest}')
def step_no_videos(context, first, second, rest):
    videos = set(context.expected["videos"]["urls"])
    pages = [first, second] + QUOTED.findall(rest)
    pages = [route for route in pages if route.startswith("/")]
    texts = []
    for route in pages:
        page = _read(context, route)
        context.page = page
        texts.append(page if "findings panel" not in rest or route != "/security/" else _panel(page))
        if route in ("/findings/", "/security/findings/", "/science/findings/"):
            _lead, _first, more = _reached(context)
            texts += [json.dumps(more)]
    if "findings panel" in rest:
        texts.append(_panel(_read(context, "/security/")))
    for text in texts:
        assert not any(address in text for address in videos)


def _panel(page):
    found = re.search(r'<div class="mom-sf-findings">(.*?)</div>\s*</div>\s*<div class="mom-sf-posts-block">', page, re.S)
    return found.group(1) if found else ""


@then('the case stylesheet hides a stream with nothing in it, and has no ".mom-untagged" or ".mom-all-refs"')
def step_stylesheet(context):
    text = (context.case_directory / "css" / "site-theme.css").read_text(encoding="utf-8")
    assert ".mom-refs-stream:not(:has(a, .home-page-empty)) { display: none; }" in text
    assert ".mom-untagged" not in text and ".mom-all-refs" not in text


@then('the file "{path}" exists in the case')
def step_case_file(context, path):
    assert (context.case_directory / path).is_file(), path


@then('the page title is "{title}" and its sentence is "{sentence}"')
def step_title_and_sentence(context, title, sentence):
    assert _plain(re.search(r'<h1 class="mom-page-title">(.*?)</h1>', context.page, re.S).group(1)) == title
    assert _plain(re.search(r'<p class="mom-dek">(.*?)</p>', context.page, re.S).group(1)) == sentence


# --- the Findings panel on a section's front page ---

@then("the findings panel shows {count:d} findings in one row, none of them a video")
def step_panel_cards(context, count):
    panel = _panel(context.page)
    addresses = CARD_ADDRESS.findall(panel)
    assert len(addresses) == count, addresses
    assert [int(size) for size in ROW_COUNT.findall(panel)] == [count]
    assert not set(addresses) & set(context.expected["videos"]["urls"])


@then('the findings panel is headed "{heading}" and the heading links to "{href}"')
def step_panel_heading(context, heading, href):
    panel = _panel(context.page)
    assert f'<h2 class="mom-section-title"><a class="mom-section-title-link" href="{href}">{heading}</a></h2>' in panel, panel[:300]


@then('the findings panel ends with "{text}" linking to "{href}"')
def step_panel_more(context, text, href):
    assert f'<p class="mom-more"><a class="mom-more-link" href="{href}">{text}</a></p>' in _panel(context.page)


@then("the findings panel has no More link")
def step_panel_no_more(context):
    assert "mom-more" not in _panel(context.page)


@then("the page has no findings panel")
def step_no_panel(context):
    assert not _panel(context.page).strip()


@then("the findings panel comes after the Worth Watching videos")
def step_panel_order(context):
    assert context.page.index("Worth Watching") < context.page.index('class="mom-sf-findings"') and CARD_ADDRESS.search(_panel(context.page))


# --- browser checks ---

def _measure(context, route, width, to_end=False):
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return None
    command = ["node", str(MEASURE_SCRIPT), served_directory_origin(context.case_directory), route, str(width)] + (["--to-end"] if to_end else [])
    result = subprocess.run(command, capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available: " + (result.stderr.strip().splitlines() or [""])[-1][:120])
        return None
    context.measured = json.loads(result.stdout)
    context.measured_width = width
    return context.measured


@when('I look at the list page "{route}" in a browser {width:d} pixels wide')
def step_draw(context, route, width):
    context.route = route
    _list_kind(context, route)
    _measure(context, route, width)


@when('I look at the list page "{route}" in a browser {width:d} pixels wide and scroll to the end')
def step_draw_to_end(context, route, width):
    context.route = route
    _list_kind(context, route)
    _measure(context, route, width, to_end=True)


@then("every row of the lead and of every block is full")
def step_rows_full(context):
    measured = getattr(context, "measured", None)
    if not measured:
        return
    width = measured["width"]
    rows = [("lead", row) for row in measured["leadRows"]] + [(name, row) for name, found in measured["blockRows"].items() for row in found]
    assert rows, "no rows were drawn"
    for name, row in rows:
        size = row["of"]
        if width < PHONE_MAX_WIDTH:
            wanted = [1] * size                      # a phone: one card across
        elif width < LAPTOP_MIN_WIDTH:
            wanted = [1] if size == 1 else [2] if size == 2 else [2, 1]    # a tablet: two across, the third of three spanning the width
        else:
            wanted = [size]                          # a laptop and wider: the whole row across
        assert row["visual"] == wanted, (name, row, width)


@then("the list's first page fills whole rows")
def step_stream_whole_rows(context):
    measured = getattr(context, "measured", None)
    if not measured:
        return
    count, columns = measured["streamFirstPageCount"], measured["streamColumns"]
    assert count and count % columns == 0, (count, columns)


@then("the page does not scroll sideways and has no heading in its lead or list")
def step_no_sideways(context):
    measured = getattr(context, "measured", None)
    if measured:
        assert not measured["overflowX"], measured
        assert measured["headingsInLeadOrStream"] == 0, measured


@then("the site title card touches no card")
def step_card_free(context):
    measured = getattr(context, "measured", None)
    if measured:
        assert not measured["siteCardTouches"], measured


@then("every one of the {count:d} {kind} is shown exactly once and the list says \"{status}\"")
def step_all_shown(context, count, kind, status):
    measured = getattr(context, "measured", None)
    if measured:
        assert measured["uniqueAddresses"] == count and measured["duplicates"] == 0, measured
        assert measured["status"].endswith(status), measured["status"]


@then("all {count:d} {kind} are shown exactly once")
def step_all_shown_plain(context, count, kind):
    measured = getattr(context, "measured", None)
    if measured:
        assert measured["uniqueAddresses"] == count and measured["duplicates"] == 0, measured


@then("there is no lead, no list and no Load more control, and the first block has the feature layout")
def step_blocks_only_drawn(context):
    measured = getattr(context, "measured", None)
    if measured:
        assert measured["leadRows"] == [] and measured["streamFirstPageCount"] == 0 and not measured["loadMore"], measured
        assert measured["blockTiers"][0] == "feature", measured


@then("the empty sentence is visible and the site title card does not cover it")
def step_empty_visible(context):
    measured = getattr(context, "measured", None)
    if measured:
        assert measured["emptyVisible"] and not measured["emptyCovered"], measured


# --- the Just Found page ---

@then("the Just Found page shows only pending References, the most confident first")
def step_just_found(context):
    addresses = CARD_ADDRESS.findall(context.page)
    recommended = context.expected["findings"]["recommended"] + context.expected["videos"]["recommended"]
    assert addresses and set(addresses) <= set(recommended)
    assert not set(addresses) & (set(context.expected["findings"]["urls"]) | set(context.expected["videos"]["urls"]))
    data = json.loads((context.case_directory / "_data" / "home-page" / "references.json").read_text(encoding="utf-8"))
    confidence = {record["url"]: record["confidence"] for record in data["references"]}
    shown = [confidence[address] for address in addresses]
    assert shown == sorted(shown, reverse=True), shown


@then('the Just Found page shows {count:d} cards, has a Load more control and data files under "{prefix}" that reach all {total:d}')
def step_just_found_more(context, count, prefix, total):
    first = CARD_ADDRESS.findall(context.page)
    assert len(first) == count and "data-reference-more" in context.page
    more, files = _data_files(context, context.page)
    assert files and all(file.lstrip("/").startswith(prefix) for file in files), files
    assert len(first + more) == len(set(first + more)) == total


@then('the projection has no redirect from "{path}"')
def step_no_redirect(context, path):
    projection = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text(encoding="utf-8"))
    assert path not in json.dumps(projection.get("redirects", {}))
