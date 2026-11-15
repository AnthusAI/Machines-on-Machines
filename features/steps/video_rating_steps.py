"""Steps for features/video-rating-index.feature: a video rated two stars or lower stays out of every public video index (the "rated" case in tests/reference_cases.py)."""

import json
import re

from behave import then

from reference_list_steps import CARD_ADDRESS, _data_files, _read, _stream_markup  # noqa: E402

LOW_STARS = (1, 2)


def _snapshot(context):
    return json.loads((context.case_directory / "_data" / "home-page" / "references.json").read_text(encoding="utf-8"))["references"]


def _excluded(context):
    return context.expected["videos"]["excluded"]


def _mentions(markup, address):
    return address in markup or address.replace("&", "&amp;") in markup or address.rsplit("=", 1)[-1] in markup


def _pages_of_an_index(context, route):
    """The page at `route` and the text of every data file its Load more control reaches, in order."""
    page = _read(context, route)
    _addresses, files = _data_files(context, _stream_markup(page))
    return [page] + [(context.case_directory / source.lstrip("/")).read_text(encoding="utf-8") for source in files]


@then('the videos rated two stars or lower are absent from the home page, "{videos}", every page of its list, "{section}", "{section_videos}" and every page of its list')
def step_absent_everywhere(context, videos, section, section_videos):
    assert len(_excluded(context)) == 12, _excluded(context)
    documents = {"/": _read(context, "/")}
    for route in (videos, section, section_videos):
        for position, document in enumerate(_pages_of_an_index(context, route)):
            documents[f"{route} #{position}"] = document
    assert len(documents) > 4, "no page of a list was reached"
    for where, document in documents.items():
        for address in _excluded(context):
            assert not _mentions(document, address), f"{address} is on {where}"


@then("the videos rated two stars or lower are still accepted in the snapshot")
def step_still_accepted(context):
    records = {record["url"]: record for record in _snapshot(context)}
    for address in _excluded(context):
        assert records[address]["status"] == "accepted" and records[address]["stars"] in LOW_STARS, address


@then("the videos rated three and four stars are on the page in the shared order")
def step_eligible_present(context):
    records = {record["url"]: record for record in _snapshot(context)}
    rated = [address for address in context.expected["videos"]["urls"] if records[address].get("stars") in (3, 4)]
    assert len(rated) == 2
    shown = CARD_ADDRESS.findall(context.page) + [address for document in _pages_of_an_index(context, context.route)[1:] for address in CARD_ADDRESS.findall(document)]
    assert [address for address in shown if address in rated] == rated, (shown[:8], rated)


@then("the lists contain no video rated two stars or lower")
def step_lists_clean(context):
    for document in _pages_of_an_index(context, context.route):
        for address in _excluded(context):
            assert not _mentions(document, address), address


@then("the Worth Watching panel has videos and none of them is rated two stars or lower")
def step_panel(context):
    panel = context.page[context.page.index("mom-sf-videos"):]
    panel = panel[:panel.index("</div>")] if "</div>" in panel else panel
    shown = CARD_ADDRESS.findall(panel)
    assert shown, "the Worth Watching panel is empty"
    assert not set(shown) & set(_excluded(context)), shown


@then('the article "{slug}" links directly to a video rated two stars or lower')
def step_article_links(context, slug):
    found = list(context.case_directory.glob(f"**/{slug}/index.html"))
    assert found, f"{slug} was not projected"
    markup = found[0].read_text(encoding="utf-8")
    context.linked_address = next((address for address in _excluded(context) if _mentions(markup, address)), None)
    assert context.linked_address, "the article lost its direct link"


@then('that video is absent from "{route}"')
def step_linked_absent(context, route):
    for document in _pages_of_an_index(context, route):
        assert not _mentions(document, context.linked_address)
