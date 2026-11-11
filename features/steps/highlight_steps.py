import json
import os
import shutil
import subprocess

from behave import then, when

from image_ratio_steps import served_origin
from projection_support import REPOSITORY_ROOT


def _luminance(hex_color):
    channels = [int(hex_color.lstrip("#")[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first, second):
    lighter, darker = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _stylesheet(context, path):
    return (context.output_directory / path.lstrip("/")).read_text()


@then('the stylesheet "{path}" keeps the space between citation numbers that follow each other')
def step_citation_gap_rule(context, path):
    text = _stylesheet(context, path)
    assert ".mom-article-body .citation + .citation { margin-left: 0.15em; }" in text
    assert ".mom-article-body .citation { font-size: 0.7em;" in text and "margin-left: -0.3em; }" in text


@then('the stylesheet "{path}" draws a highlight as a flat rounded fill with heavier text and no outline')
def step_highlight_rule(context, path):
    rule = next(line for line in _stylesheet(context, path).splitlines() if line.startswith("body.mom mark {"))
    for required in ("background: var(--human)", "color: var(--on-human)", "font-weight: 600", "border-radius: var(--radius-sm)", "box-decoration-break: clone"):
        assert required in rule, required
    for forbidden in ("border:", "outline", "box-shadow", "text-decoration"):
        assert forbidden not in rule, forbidden


@then('the stylesheet "{path}" gives a highlight a forced-colors fallback and a print fallback that keep the emphasis')
def step_highlight_fallbacks(context, path):
    text = _stylesheet(context, path)
    assert "@media (forced-colors: active) { body.mom mark { background: Mark; color: MarkText;" in text
    assert "@media print { body.mom mark { background: none;" in text and "font-weight: 800; text-decoration: underline;" in text


@then("the highlight's text color on its fill reaches 4.5 to 1 in Day and in Night")
def step_highlight_tokens_contrast(context):
    tokens = json.loads((REPOSITORY_ROOT / "design/system/tokens.json").read_text())["color"]["tokens"]
    values = {token["name"]: token["value"] for token in tokens}
    for theme in ("light", "dark"):
        ratio = _contrast(values["on-human"][theme], values["human"][theme])
        assert ratio >= 4.5, (theme, ratio)


@when('I measure highlights at {width:d} pixels in "{theme}" mode')
def step_measure_highlights(context, width, theme):
    if not shutil.which("node"):
        context.scenario.skip("Node is not installed")
        return
    result = subprocess.run(
        ["node", str(REPOSITORY_ROOT / "tools/measure_highlight.cjs"), served_origin(context), str(width), theme],
        capture_output=True, text=True, env=os.environ,
    )
    if result.returncode == 2:
        context.scenario.skip(result.stderr.strip())
        return
    assert result.returncode == 0, result.stderr
    context.highlights = json.loads(result.stdout)


@then("every highlight is a rounded fill with no border or outline, heavier than body text, repeated on each wrapped line")
def step_highlight_shape(context):
    if not hasattr(context, "highlights"):
        return
    measured = context.highlights
    assert len(measured["marks"]) == 2, measured
    for mark in measured["marks"]:
        assert mark["radius"] > 0 and mark["borderStyle"] == "none" and mark["outlineStyle"] == "none", mark
        assert mark["weight"] > measured["bodyWeight"] and mark["weight"] < 800, mark
        assert mark["decorationBreak"] == "clone" and mark["paddingInline"] > 0, mark
        assert mark["background"] != "rgba(0, 0, 0, 0)", mark
    assert not measured["overflow"], measured


@then("every highlight's text, and the link inside one, reaches 4.5 to 1 against its fill")
def step_highlight_contrast(context):
    if not hasattr(context, "highlights"):
        return
    for ratios in context.highlights["contrasts"]:
        assert ratios["text"] >= 4.5, ratios
        assert ratios["link"] is None or ratios["link"] >= 4.5, ratios


@then("every citation number in a run is separated from the last by a gap of a few pixels")
def step_citation_gap(context):
    if not hasattr(context, "highlights"):
        return
    gaps = context.highlights["runGaps"]
    assert len(gaps) == 3 and all(2 <= gap <= 8 for gap in gaps), gaps


@then("a single citation number, and the first of a run, are still pulled against the text")
def step_citation_single(context):
    if not hasattr(context, "highlights"):
        return
    measured = context.highlights
    assert measured["singleMarginLeft"] < 0 and measured["firstOfRunMarginLeft"] < 0, measured


@then("the highlight that holds a link and emphasis keeps both inside the mark")
def step_nested_highlight(context):
    assert '<mark>the phrase an editor chose, with a <a href="https://example.com/source">link to the source</a> and some <em>emphasis</em> inside it</mark>' in context.page
