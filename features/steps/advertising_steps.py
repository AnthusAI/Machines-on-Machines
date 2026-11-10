"""Steps for the advertisers and the aside ad's gutter in features/advertising.feature.

The `@browser` scenarios draw a projected article in Chromium through tools/measure_aside_ad.cjs and skip themselves when Node or Playwright is
missing (set PLAYWRIGHT_MODULE to the package's path to point at one).
"""

import json
import os
import re
import shutil
import subprocess

from behave import given, then, when

import mom_components as mom
from image_ratio_steps import served_origin
from projection_support import REPOSITORY_ROOT

ASIDE_MEASURE_SCRIPT = REPOSITORY_ROOT / "tools" / "measure_aside_ad.cjs"


def ad_in_placement(page: str, placement: str) -> str:
    found = re.search(rf'data-ad="([a-z0-9-]+)"[^>]*data-ad-placement="{placement}"', page)
    assert found, f"no ad in the placement {placement}"
    return found.group(1)


@then('the ads in the placements "{first}" and "{second}" are from different advertisers')
def step_different_advertisers(context, first, second):
    assert ad_in_placement(context.page, first) != ad_in_placement(context.page, second), "both slots show the same ad"


@then('the projected pages carry ads from the advertisers "{first}" and "{second}"')
def step_both_advertisers_appear(context, first, second):
    advertiser_of = {ad["id"]: ad["advertiser"] for ad in json.loads((REPOSITORY_ROOT / "web" / "ads.json").read_text())["ads"]}
    seen = set()
    for page in context.output_directory.rglob("index.html"):
        if page.relative_to(context.output_directory).parts[:1] == ("design",):
            continue  # the component gallery shows every ad on purpose
        seen.update(advertiser_of[found] for found in re.findall(r'data-ad="([a-z0-9-]+)"', page.read_text(encoding="utf-8")))
    assert {first, second} <= seen, f"only {sorted(seen)} appear"


class SamplePage:
    def __init__(self, path):
        self.path = path


def chosen_ads(unit: str, pages: int = 600):
    import hooks
    return [hooks._ad_for_slot(SamplePage(f"/articles/sample-{number}/"), unit) for number in range(pages)]


@then("over many pages each advertiser fills about the same share of a slot, however many variants it has")
def step_even_share(context):
    from collections import Counter
    shares = Counter(ad["advertiser"] for ad in chosen_ads("band"))
    assert len(shares) >= 2 and max(shares.values()) - min(shares.values()) < 0.15 * sum(shares.values()), shares


@then("over many pages every variant of an advertiser appears")
def step_every_variant(context):
    import hooks
    offered = {ad["id"] for ad in hooks._advertisements() if "band" in ad["units"]}
    assert {ad["id"] for ad in chosen_ads("band")} == offered


def sample_ad(**brand_changes):
    brand = {
        "name": "Example", "face": "serif",
        "ground": {"day": "#1b1d20", "night": "#f4f1ea"}, "ink": {"day": "#f4f1ea", "night": "#1b1d20"},
        "accent": {"day": "#e2725f", "night": "#a3271f"},
    }
    brand.update(brand_changes)
    return {"id": "example", "advertiser": "Example", "units": ["band"], "href": "https://example.test/", "headline": "Words",
            "body": "One sentence.", "cta": "Go", "brand": brand}


def assert_refused(ad, expected: str):
    try:
        mom.validate_advertisement(ad)
    except ValueError as error:
        assert expected in str(error), str(error)
        return
    raise AssertionError(f"the ad was accepted; expected a refusal mentioning {expected!r}")


@then("an ad whose brand accent has contrast below 4.5 on its ground is refused")
def step_weak_accent(context):
    mom.validate_advertisement(sample_ad())
    assert_refused(sample_ad(accent={"day": "#3a3d42", "night": "#a3271f"}), "accent")


@then("an ad whose brand names an unknown type face is refused")
def step_unknown_face(context):
    assert_refused(sample_ad(face="comic"), "face")


@then("an ad whose brand names an unknown wordmark or art is refused")
def step_unknown_wordmark(context):
    assert_refused(sample_ad(wordmark="dragon"), "wordmark")
    assert_refused(sample_ad(art="dragon"), "art")


@then("a headline's length counts the words a reader sees, not its emphasis marks")
def step_headline_length_without_marks(context):
    exactly_the_limit = "*" + "x" * 10 + "*" + "y" * (mom.AD_HEADLINE_LIMIT - 10)
    mom.validate_advertisement({**sample_ad(), "headline": exactly_the_limit})
    assert_refused({**sample_ad(), "headline": exactly_the_limit + "z"}, "limit")


# --- the browser scenarios ---

@given("the sample of article words with the aside ad on the component gallery")
def step_article_with_aside(context):
    # A real article's ad is chosen by its address, so which fixture article carries the aside changes whenever an ad is added. The gallery sets the
    # aside in an article's own markup (the same classes as a story), so the gutter is measured the same way every time.
    page = (context.output_directory / "design" / "index.html").read_text(encoding="utf-8")
    assert 'class="mom-gallery-article"' in page and 'data-ad-placement="article-aside"' in page, "the gallery has no aside in a sample of article words"
    context.aside_route = "/design/"


@when("I measure the aside ad in a browser {width:d} pixels wide")
def step_measure_aside(context, width):
    context.aside_measured = None
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return
    result = subprocess.run(["node", str(ASIDE_MEASURE_SCRIPT), served_origin(context), context.aside_route, str(width)], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available")
        return
    context.aside_measured = json.loads(result.stdout)


@then("no line of the article's words comes within {gutter:d} pixels of the aside's side or {below:d} pixels of its foot")
def step_aside_gutter(context, gutter, below):
    measured = context.aside_measured
    if not measured:
        return
    assert measured["floated"], f"the aside is not floated at {measured['width']} pixels"
    aside = measured["aside"]
    beside = [line for line in measured["lines"] if line["top"] < aside["bottom"] and line["bottom"] > aside["top"]]
    assert beside, "no words run beside the aside"
    for line in beside:
        assert aside["left"] - line["right"] >= gutter, f"a line ends {aside['left'] - line['right']:.1f}px from the aside: {line['text']!r}"
    under = [line for line in measured["lines"] if line["top"] >= aside["top"] and line["right"] > aside["left"]]
    assert under, "no words run under the aside"
    assert min(line["top"] for line in under) - aside["bottom"] >= below, f"the words under the aside start {min(line['top'] for line in under) - aside['bottom']:.1f}px below it"


@then("the aside is not floated and spans the article's text column")
def step_aside_on_a_phone(context):
    measured = context.aside_measured
    if not measured:
        return
    assert not measured["floated"], "the aside still floats on a phone"
    assert abs(measured["aside"]["width"] - measured["column"]["width"]) < 1, (measured["aside"], measured["column"])
    assert measured["viewportOverflow"] <= 0, f"the page scrolls sideways by {measured['viewportOverflow']}px"
