import json
import re
import sys
from pathlib import Path

from behave import given, then, when  # noqa: F401

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

from build_figure_style_guide import GUIDE_PATH, build_guide  # noqa: E402
from render_figures import GALLERY_ROOT, LABELS, MAX_RATIO_DIFFERENCE, load_mapping, png_size, source_problems  # noqa: E402


def gallery_folders():
    return sorted(path.parent for path in GALLERY_ROOT.glob("*/figure.svg"))


def source_of(slug):
    return (GALLERY_ROOT / slug / "figure.svg").read_text()


def metadata_of(slug):
    return json.loads((GALLERY_ROOT / slug / "figure.json").read_text())


@then("every gallery figure has a Day picture and a Night picture with the same proportions")
def step_pairs(context):
    for folder in gallery_folders():
        light_width, light_height = png_size(folder / f"{folder.name}.png")
        dark_width, dark_height = png_size(folder / f"{folder.name}.dark.png")
        assert abs(light_width / light_height - dark_width / dark_height) / (light_width / light_height) <= MAX_RATIO_DIFFERENCE, folder.name


@then("every gallery figure passes the source checks")
def step_sources(context):
    mapping = load_mapping()
    for folder in gallery_folders():
        problems = source_problems(source_of(folder.name), metadata_of(folder.name), mapping)
        assert not problems, f"{folder.name}: {problems}"


@when('the "{figure}" source has {change}')
def step_break_source(context, figure, change):
    source = source_of(figure)
    changes = {
        "a raw color": lambda text: text.replace('fill="{ground}"', 'fill="#ff0000"'),
        "navy in it": lambda text: text.replace('fill="{ground}"', 'fill="{brand}"'),
        "a second focal mark": lambda text: text.replace('fill="{ground}"', 'fill="{ground}" data-focal="true"'),
        "its stamp removed": lambda text: text.replace(LABELS["forecast"], "THE CLIMB"),
    }
    context.figure_problems = source_problems(changes[change](source), metadata_of(figure), load_mapping())


@then('the source checks report "{problem}"')
def step_reported(context, problem):
    assert any(problem in reported for reported in context.figure_problems), context.figure_problems


@then('the "{figure}" figure carries the stamp "{stamp}"')
def step_stamp(context, figure, stamp):
    assert stamp in source_of(figure)


@then('the "{figure}" figure shows no numbers')
def step_no_numbers(context, figure):
    assert not re.search(r"\d", " ".join(re.findall(r"<text[^>]*>([^<]*)</text>", source_of(figure))))


@then("no gallery figure names an approver")
def step_no_approver(context):
    for folder in gallery_folders():
        assert metadata_of(folder.name)["approved_by"] is None, folder.name


@then("the figure style guide is current")
def step_guide(context):
    assert GUIDE_PATH.read_text() == build_guide()


@then("the site theme removes the browser's figure margin and fits the picture to the column")
def step_theme_fits_figures(context):
    theme = (REPOSITORY_ROOT / "web" / "css" / "site-theme.css").read_text()
    assert ".mom-article-body .papyrus-image { margin: var(--space-8) 0; }" in theme
    assert re.search(r"\.mom-article-body \.papyrus-image img \{[^}]*width: 100%", theme)
