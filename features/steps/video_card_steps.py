"""Steps for features/video-cards.feature: the click-to-play card on a projected page, and in a browser through tools/measure_video_cards.cjs
(the @browser scenarios skip themselves when Node or Playwright is missing; set PLAYWRIGHT_MODULE to the package's path to point at one)."""

import json
import os
import re
import shutil
import subprocess

from behave import then, when

from image_ratio_steps import served_directory_origin  # noqa: E402
from projection_support import REPOSITORY_ROOT  # noqa: E402

MEASURE_SCRIPT = REPOSITORY_ROOT / "tools" / "measure_video_cards.cjs"
PLAY_BUTTON = re.compile(r'<button type="button" class="mom-video-poster" aria-label="Play: ([^"]*)"')
CARD_TITLE = re.compile(r'<button type="button" class="mom-video-poster" aria-label="Play: ([^"]*)".*?<a class="mom-reference-card-title" href="[^"]*">([^<]*)</a>', re.S)
SIZE_TOLERANCE = 1.5


@then("the page has Play buttons and no player frame")
def step_posters(context):
    assert PLAY_BUTTON.search(context.page), "no Play button"
    assert "<iframe" not in context.page, "a player frame is in the page"


@then('every Play button is named "Play: " followed by its video\'s title')
def step_names(context):
    named = CARD_TITLE.findall(context.page)
    assert named and len(named) == len(PLAY_BUTTON.findall(context.page)), "a Play button has no headline after it"
    for name, title in named:
        assert name == title, (name, title)


@then("the site script replaces a pressed Play button with an iframe taken from the button's data and puts back the one that was playing")
def step_script(context):
    script = (REPOSITORY_ROOT / "web" / "assets" / "mom.js").read_text(encoding="utf-8")
    for needle in ('closest(".mom-video-poster")', 'getAttribute("data-player-src")', 'getAttribute("data-player-title")', 'getAttribute("data-player-allow")',
                   "poster.replaceWith(player)", "playingVideo.player.replaceWith(playingVideo.poster)", "player.focus()"):
        assert needle in script, needle


@then('the stylesheet "{path}" and the site script have nothing that scrolls a row of videos sideways')
def step_nothing_scrolls_in_sources(context, path):
    css = (REPOSITORY_ROOT / "web" / path.lstrip("/")).read_text(encoding="utf-8")
    script = (REPOSITORY_ROOT / "web" / "assets" / "mom.js").read_text(encoding="utf-8")
    for needle in ("mom-video-row", "mom-video-scroll", "scroll-snap-type", "grid-auto-flow: column"):
        assert needle not in css, needle
    for needle in ("setUpVideoRow", "scrollBy", "scrollLeft", "mom-video-scroll"):
        assert needle not in script, needle


@then('a section\'s block of videos is at most two rows of the card grid, with no scroll buttons')
def step_block_is_a_grid(context):
    page = context.page
    assert "mom-video-scroll" not in page and "mom-video-row" not in page
    blocks = re.findall(r'<section class="mom-section mom-refs-section"[^>]*>(.*?)</section>', page, re.S)
    assert blocks, "no section block on the page"
    for block in blocks:
        sizes = [int(count) for count in re.findall(r'class="home-page-grid mom-refs-row" data-card="tile" data-count="(\d)"', block)]
        assert 1 <= len(sizes) <= 2 and sum(sizes) <= 6, sizes


def _run(context, route, width):
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return None
    result = subprocess.run(["node", str(MEASURE_SCRIPT), served_directory_origin(context.case_directory), route, str(width)], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available: " + (result.stderr.strip().splitlines() or [""])[-1][:120])
        return None
    context.measured = json.loads(result.stdout)
    return context.measured


@when('I press nothing on "{route}" in a browser {width:d} pixels wide')
def step_look(context, route, width):
    _run(context, route, width)


@when('I press Play on three videos of "{route}" in a browser {width:d} pixels wide')
def step_press(context, route, width):
    _run(context, route, width)


@then("the page loaded no player and made no request to a video platform")
def step_nothing_loaded(context):
    measured = getattr(context, "measured", None)
    if measured:
        assert measured["atLoad"]["frames"] == 0 and measured["requestedAtLoad"] == 0, measured["atLoad"]
        assert measured["atLoad"]["posters"] >= 3 and measured["atLoad"]["unnamedPosters"] == 0, measured["atLoad"]


@then("the page does not scroll sideways at load")
def step_no_sideways_at_load(context):
    measured = getattr(context, "measured", None)
    if measured:
        assert not measured["atLoad"]["overflowX"], measured["atLoad"]


@then("the page does not scroll sideways after each press")
def step_no_sideways_after_pressing(context):
    measured = getattr(context, "measured", None)
    if not measured:
        return
    for name in ("first", "second", "keyboard"):
        for card in measured.get(name, {}).values():
            if isinstance(card, dict):
                assert not card["overflowX"], (name, card)


@then("no element on the page scrolls sideways, in light and in dark")
def step_no_scrolling_element(context):
    measured = getattr(context, "measured", None)
    if measured:
        assert measured["atLoad"]["scrollers"] == 0 and not measured["atLoad"]["overflowX"], measured["atLoad"]
        for scheme in ("light", "dark"):
            assert measured["schemes"][scheme]["scrollers"] == 0 and not measured["schemes"][scheme]["overflowX"], (scheme, measured["schemes"][scheme])


@then("each section's videos are a wrapping grid of at most two rows, and the page has no scroll buttons")
def step_grid_and_no_buttons(context):
    measured = getattr(context, "measured", None)
    if measured:
        at_load = measured["atLoad"]
        assert at_load["sections"], "no section block"
        for section in at_load["sections"]:
            assert section["cards"] <= 6 and (at_load["width"] < 1000 or section["rowsDrawn"] <= 2), section
        assert at_load["scrollButtons"] == 0, at_load


@then("the first card shows a player loaded with autoplay and keeps its size, and the focus is in the player")
def step_first(context):
    measured = getattr(context, "measured", None)
    if not measured:
        return
    before, after = measured["first"]["before"], measured["first"]["after"]
    assert after["frame"] and "autoplay=1" in after["frameSource"] and after["frameTitle"].endswith(", video player"), after
    assert not after["posterShown"] and after["focusedIsFrame"], after
    for size in ("height", "width", "mediaHeight", "mediaWidth"):
        assert abs(before[size] - after[size]) <= SIZE_TOLERANCE, (size, before, after)
    assert len(measured["requestedAfterFirst"]) == 1 and "autoplay=1" in measured["requestedAfterFirst"][0], measured["requestedAfterFirst"]


@then("pressing Play on a second video puts the first card's picture back and leaves one player")
def step_second(context):
    measured = getattr(context, "measured", None)
    if measured:
        first, second = measured["second"]["firstCard"], measured["second"]["secondCard"]
        assert first["posterShown"] and not first["frame"], first
        assert second["frame"] and not second["posterShown"] and second["frames"] == 1, second


@then("pressing Enter on a third video's Play button plays it and stops the second")
def step_keyboard(context):
    measured = getattr(context, "measured", None)
    if measured:
        second, third = measured["keyboard"]["secondCard"], measured["keyboard"]["thirdCard"]
        assert second["posterShown"] and not second["frame"], second
        assert third["frame"] and third["frames"] == 1 and third["focusedIsFrame"], third
        assert len(measured["requestedAfterKeyboard"]) == 3, measured["requestedAfterKeyboard"]
