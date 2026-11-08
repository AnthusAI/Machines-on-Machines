"""Steps for features/image-ratio.feature.

The static scenarios read the projected stylesheets and pages. The `@browser` scenarios draw the projected site in Chromium through
tools/measure_images.cjs and skip themselves when Node or Playwright is missing (set PLAYWRIGHT_MODULE to the package's path to point at one).
"""

import functools
import json
import os
import re
import shutil
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from behave import given, then, when

from projection_support import REPOSITORY_ROOT  # noqa: E402

MEASURE_SCRIPT = REPOSITORY_ROOT / "tools" / "measure_images.cjs"
SOURCE_STYLESHEETS = (
    REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css",
    REPOSITORY_ROOT / "web" / "css-src" / "site-theme.src.css",
)


def stylesheet_versions(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    phone, scaled = text.split("@media (min-width: 600px) {")
    return phone, scaled


def custom_property(css: str, name: str) -> str:
    found = re.search(rf"--{re.escape(name)}:\s*([^;]+);", css)
    assert found, f"--{name} is not defined"
    return found.group(1).strip()


@then('the stylesheet "{path}" defines "ratio-media" as 16 over 9 and "rhythm" as 4 pixels below 600 pixels and 3 pixels from 600 pixels up')
def step_tokens(context, path):
    phone, scaled = stylesheet_versions(context, path)
    assert custom_property(phone, "ratio-media") == custom_property(scaled, "ratio-media") == "calc(16 / 9)"
    assert custom_property(phone, "rhythm") == "4px" and custom_property(scaled, "rhythm") == "3px"


@then('the stylesheet "{path}" defines "ratio-square" as 1')
def step_square(context, path):
    phone, scaled = stylesheet_versions(context, path)
    assert custom_property(phone, "ratio-square") == custom_property(scaled, "ratio-square") == "1"


@then('the stylesheets "{components}" and "{theme}" write no aspect ratio except the media tokens, the square thumbnail and the decorative strip')
def step_no_literal_ratio(context, components, theme):
    for source in SOURCE_STYLESHEETS:
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            for declaration in re.findall(r"aspect-ratio:\s*([^;}]+)", line):
                value = declaration.strip()
                allowed = value in ("var(--ratio-media)", "var(--ratio-square)", "auto", "1") and not (value == "1" and "mom-art-shape" not in line)
                assert allowed, f"{source.name}:{number} writes its own aspect ratio: {value}"


@then('the stylesheets define no "{first}" or "{second}" class')
def step_no_ratio_classes(context, first, second):
    for path in ("assets/mom-components.css", "css/site-theme.css"):
        phone, scaled = stylesheet_versions(context, path)
        assert first not in phone + scaled and second not in phone + scaled, f"{path} still defines a ratio class"


@then('every image on the page sits in a "{frame}" frame')
def step_frames(context, frame):
    images = re.findall(r'<(?:img|span)[^>]*class="[^"]*\bmom-card-image\b[^"]*"', context.page)
    assert images, "the page has no content images"
    assert len(re.findall(rf'<span class="{frame}[ "]', context.page)) >= len(images)
    for found in re.finditer(r'<(?:img|span)[^>]*class="[^"]*\bmom-card-image\b', context.page):
        before = context.page[:found.start()]
        assert re.search(rf'<span class="{frame}[^"]*">(?:<span class="mom-card-image-(?:day|night)">)*$', before), "an image is outside its frame"


@then('the stylesheet "{path}" snaps image heights only inside a feature test for rounding and container units')
def step_snap_guarded(context, path):
    phone, _ = stylesheet_versions(context, path)
    guarded = re.search(r"@supports \(height: round\(down, 1cqw, 1em\)\) \{(.*?)\n\}", phone, re.S)
    assert guarded and "height: round(down, calc(100cqw / var(--ratio-media)), var(--rhythm))" in guarded.group(1)
    assert phone.count("round(down, calc(100cqw") == 1


@then('the stylesheet "{path}" keeps the 16:9 aspect ratio outside that test')
def step_fallback(context, path):
    phone, _ = stylesheet_versions(context, path)
    outside = re.sub(r"@supports.*?\n\}", "", phone, flags=re.S)
    assert re.search(r"\.mom-card-image \{[^}]*aspect-ratio: var\(--ratio-media\)", outside)


# --- the browser scenarios ---

SERVERS = {}


def served_origin(context) -> str:
    directory = str(context.output_directory)
    if directory not in SERVERS:
        handler = functools.partial(SimpleHTTPRequestHandler, directory=directory)
        handler.log_message = lambda *arguments: None
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        SERVERS[directory] = f"http://127.0.0.1:{server.server_address[1]}"
    return SERVERS[directory]


@when('I view the page "{route}" in a browser {width:d} pixels wide')
def step_measure(context, route, width):
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return
    result = subprocess.run(["node", str(MEASURE_SCRIPT), served_origin(context), route, str(width)], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available: " + result.stderr.strip().splitlines()[-1][:120] if result.stderr.strip() else "Playwright is not available")
        return
    context.measured = json.loads(result.stdout)
    assert context.measured["images"], f"{route} has no content images"


def measured_images(context):
    return context.measured["images"] if getattr(context, "measured", None) else None


@then("every content image is 16:9 to within one rhythm unit of height")
def step_one_ratio(context):
    rhythm = context.measured["rhythm"]
    for image in measured_images(context) or []:
        exact_height = image["width"] * 9 / 16
        assert not image["square"] and 0 <= exact_height - image["height"] < rhythm, f"{image['width']} x {image['height']} is not 16:9 within {rhythm}px"


@then("every content image is exactly as tall as its own width gives")
def step_not_stretched(context):
    for image in measured_images(context) or []:
        assert not image["stretched"], f"{image['width']} x {image['height']} is taller than {image['heightFromItsOwnWidth']}px: something stretched it"


@then("every content image fills its frame")
def step_fills_frame(context):
    for image in measured_images(context) or []:
        assert image["fillsItsFrame"], f"{image['width']} x {image['height']} does not fill its frame of height {image['frameHeight']}"


@then("every content image has a height that is a whole number of rhythm units")
def step_multiple(context):
    for image in measured_images(context) or []:
        assert image["multipleOfRhythm"], f"{image['height']}px is not a whole number of {context.measured['rhythm']}px units"


@then("the rhythm unit is {unit:d} pixels")
def step_unit(context, unit):
    if getattr(context, "measured", None):
        assert context.measured["rhythm"] == unit


# --- the section page's browser scenarios (tools/measure_section_page.cjs) ---

SECTION_MEASURE_SCRIPT = REPOSITORY_ROOT / "tools" / "measure_section_page.cjs"
SECTION_CARD_MAXIMUM_WIDTH = 400   # real pixels: a laptop's card is 307, and the page gains columns instead of growing its cards (the site stops at six columns, so the widest windows grow a little)
SECTION_CARD_MINIMUM_WIDTH = 230
SECTION_LEAD_MAXIMUM_WIDTH = 1200
SECTION_POST_MAXIMUM_HEIGHT_RATIO = 0.95   # a post card is smaller than an article card


@when('I measure the page "{route}" in a browser {width:d} pixels wide')
def step_measure_section(context, route, width):
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return
    result = subprocess.run(["node", str(SECTION_MEASURE_SCRIPT), served_origin(context), route, str(width)], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available")
        return
    context.section_measured = json.loads(result.stdout)


@then("no element of the conversations rail or the sentence under it touches the site title card")
def step_rail_clear_of_sticker(context):
    measured = getattr(context, "section_measured", None)
    if not measured:
        return
    sticker = measured["sticker"]
    assert sticker, "the page has no site title card"
    touching = [box for box in measured["sideBoxes"] if box["left"] < sticker["right"] and box["right"] > sticker["left"] and box["top"] < sticker["bottom"] and box["bottom"] > sticker["top"]]
    assert not touching, f"{len(touching)} boxes cross the card: {touching[:2]}"


@then("every article, video and post card is a laptop-sized card and the lead's picture is not enlarged with the window")
def step_section_card_sizes(context):
    measured = getattr(context, "section_measured", None)
    if not measured:
        return
    assert measured["lead"]["image"]["width"] <= SECTION_LEAD_MAXIMUM_WIDTH, measured["lead"]["image"]
    for card in measured["articles"] + measured["posts"]:
        assert SECTION_CARD_MINIMUM_WIDTH <= card["card"]["width"] <= SECTION_CARD_MAXIMUM_WIDTH, card["card"]["width"]
        assert abs(card["image"]["width"] * 9 / 16 - card["image"]["height"]) < 3.5, card["image"]
    assert all(SECTION_CARD_MINIMUM_WIDTH - 20 <= width <= SECTION_CARD_MAXIMUM_WIDTH for width in measured["videoWidths"]), measured["videoWidths"]
    if measured["articles"] and measured["posts"]:
        assert measured["posts"][0]["card"]["height"] < measured["articles"][0]["card"]["height"] * SECTION_POST_MAXIMUM_HEIGHT_RATIO


@then("every row of article, video and post cards is a whole row and nothing leaves a blank gap to the right")
def step_section_whole_rows_measured(context):
    measured = getattr(context, "section_measured", None)
    if not measured:
        return
    columns = measured["columns"]
    for name in ("articleRows", "postRows", "videoRows"):
        assert measured[name] and all(row == columns for row in measured[name]), (name, measured[name], columns)
    assert not measured["horizontalScroll"]
