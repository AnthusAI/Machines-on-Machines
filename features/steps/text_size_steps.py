"""Steps for features/text-size.feature: the minimum text size policy (floors live in tools/scale_css.py).

The `@browser` scenarios draw the projected site through tools/measure_text.cjs and skip themselves when Node or Playwright is missing.
"""

import json
import os
import re
import shutil
import subprocess
import sys

from behave import then, when

from projection_support import REPOSITORY_ROOT  # noqa: E402
from image_ratio_steps import served_origin, stylesheet_versions  # noqa: E402

sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
import scale_css  # noqa: E402

MEASURE_TEXT_SCRIPT = REPOSITORY_ROOT / "tools" / "measure_text.cjs"


@then("the scale tool's floors are {reading:d} pixels for reading text, {interface:d} for interface text and {label:d} for micro-labels")
def step_floors(context, reading, interface, label):
    assert (scale_css.READING_FLOOR_PX, scale_css.INTERFACE_FLOOR_PX, scale_css.LABEL_FLOOR_PX) == (reading, interface, label)


@then('no font size in "{first}" and "{second}" is below {floor:d} pixels in either version')
def step_no_small_sizes(context, first, second, floor):
    for path in (first, second):
        for version in stylesheet_versions(context, path):
            for size in re.findall(r"(?<![\w-])font(?:-size)?:\s*(?:[\w ]*? )?(\d*\.?\d+)px", version):
                assert float(size) >= floor, f"{path} sets text to {size}px"


@when('I check the text sizes of "{route}" in a browser {width:d} pixels wide')
def step_measure_text(context, route, width):
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return
    floors = json.dumps({"reading": scale_css.READING_FLOOR_PX, "interface": scale_css.INTERFACE_FLOOR_PX, "label": scale_css.LABEL_FLOOR_PX})
    result = subprocess.run(["node", str(MEASURE_TEXT_SCRIPT), served_origin(context), route, str(width), floors], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available")
        return
    context.measured_text = json.loads(result.stdout)
    assert context.measured_text["checked"] > 0, f"{route} has no visible text"


@then("no visible text is drawn below its floor")
def step_no_small_text(context):
    measured = getattr(context, "measured_text", None)
    if measured:
        assert not measured["offenders"], "text below its floor: " + json.dumps(measured["offenders"][:6])


@then('the stylesheet "{path}" sets the article body to {phone_size:d} pixels on a line of {phone_line:d} pixels below 600 pixels and {scaled_size:d} pixels on a line of {scaled_line:d} pixels from 600 pixels up')
def step_article_body(context, path, phone_size, phone_line, scaled_size, scaled_line):
    phone, scaled = stylesheet_versions(context, path)
    assert re.search(rf"\.mom-article-body \{{[^}}]*font: 400 {phone_size}px ?/ ?{phone_line}px", phone)
    assert re.search(rf"\.mom-article-body \{{[^}}]*font: 400 {scaled_size}px ?/ ?{scaled_line}px", scaled)


@then('the stylesheet "{path}" sets the text measure to {phone_width:d} pixels below 600 pixels and {scaled_width:d} pixels from 600 pixels up')
def step_measure(context, path, phone_width, scaled_width):
    phone, scaled = stylesheet_versions(context, path)
    assert f"--measure: {phone_width}px;" in phone and f"--measure: {scaled_width}px;" in scaled


@then('the stylesheet "{path}" gives the article a {gutter:d} pixel side gutter below 600 pixels')
def step_article_gutter(context, path, gutter):
    phone, _ = stylesheet_versions(context, path)
    assert re.search(r"max-width: 899px\) \{[^@]*\.mom-article \{ padding: var\(--space-6\) var\(--space-4\) var\(--space-10\); \}", phone)
    assert "--space-4: 16px" in (context.output_directory / "assets/mom-tokens.css").read_text().split("@media (min-width: 600px)")[0]


@then('the stylesheet "{path}" sets no maximum height on the knowledge chart figure')
def step_chart_not_clipped(context, path):
    for version in stylesheet_versions(context, path):
        rule = re.search(r"\.papyrus-knowledge-chart \{[^}]*\}", version)
        assert rule and "max-height" not in rule.group(0) and "height" not in rule.group(0)
