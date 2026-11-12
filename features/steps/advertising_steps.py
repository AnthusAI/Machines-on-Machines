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
SLOT_MEASURE_SCRIPT = REPOSITORY_ROOT / "tools" / "measure_ad_slots.cjs"
MAXIMUM_LABEL_GAP = 12
PIXEL_TOLERANCE = 0.75


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


@then("every advertisement on the page is the site's label and slot around the advertiser's picture, and nothing the site styled")
def step_ads_are_only_slots(context):
    ads = re.findall(r"<aside [^>]*data-ad=.*?</aside>", context.page, re.S)
    assert ads, "the page has no advertisements"
    for ad in ads:
        assert re.search(r'<p class="mom-ad-label"><b>Advertisement</b> · [^<]+</p><div class="mom-ad-slot"><a rel="sponsored noopener" href="[^"]+">', ad), ad[:300]
        assert "<img" in ad and 'alt="' in ad, "an ad has a picture with alt text"
        assert not re.search(r"<(svg|h[1-6]|button|blockquote|figure)\b|style=|mom-ad-branded", ad), "the site drew inside the creative"
        for alt in re.findall(r'alt="([^"]*)"', ad):
            assert len(alt) >= mom.AD_ALT_MINIMUM_CHARACTERS, alt


@then('every advertisement picture on the page is a file under "{folder}"')
def step_pictures_in_folder(context, folder):
    sources = re.findall(r'(?:src|srcset)="([^"]+)"', "".join(re.findall(r"<aside [^>]*data-ad=.*?</aside>", context.page, re.S)))
    assert sources and all(source.startswith(folder) for source in sources), sources


@then('the advertisement says it is from "{advertiser}" outside its picture')
def step_label_names_advertiser(context, advertiser):
    assert f'<p class="mom-ad-label"><b>Advertisement</b> · {advertiser}</p>' in context.page


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
    offered = {ad["id"] for ad in hooks._advertisements() if "band" in mom.ad_units(ad)}
    assert {ad["id"] for ad in chosen_ads("band")} == offered


SHIPPED_PICTURE = "/assets/ads/papyrus-newsroom-half-page.webp"


def sample_ad(**changes):
    picture = {"src": SHIPPED_PICTURE, "alt": "Example: words that the picture carries", "width": 300, "height": 600}
    return {"id": "example", "advertiser": "Example", "href": "https://example.test/", "images": {"half-page": picture}, **changes}


def assert_refused(ad, expected: str):
    try:
        mom.validate_advertisement(ad)
    except ValueError as error:
        assert expected in str(error), str(error)
        return
    raise AssertionError(f"the ad was accepted; expected a refusal mentioning {expected!r}")


def with_picture(**changes):
    return sample_ad(images={"half-page": {**sample_ad()["images"]["half-page"], **changes}})


@then("every ad in the repository is an advertiser's picture for every unit, in Day and Night, with its own alt text")
def step_shipped_ads_are_assets(context):
    for ad in json.loads((REPOSITORY_ROOT / "web" / "ads.json").read_text())["ads"]:
        mom.validate_advertisement(ad)
        assert mom.ad_units(ad) == mom.AD_UNIT_NAMES, ad["id"]
        assert set(ad) == {"id", "advertiser", "href", "images"}, f"{ad['id']} holds copy or a brand the site would draw"


@then("an ad with no alt text, or alt text that is only the advertiser's name, is refused")
def step_alt_required(context):
    mom.validate_advertisement(sample_ad())
    assert_refused(with_picture(alt=""), "alt")
    assert_refused(with_picture(alt="Example"), "alt text must say")


@then("an ad whose picture is missing, outside the ads folder, or not a picture file is refused")
def step_asset_checked(context):
    assert_refused(with_picture(src="/assets/ads/not-there.webp"), "is not in web/assets/ads")
    assert_refused(with_picture(src="https://example.test/ad.webp"), "must be a")
    assert_refused(with_picture(src="/assets/ads/ad.exe"), "must be a")


@then("an ad with no advertiser, or a link that is not https or a path on the site, is refused")
def step_advertiser_and_link(context):
    assert_refused(sample_ad(advertiser=""), "advertiser")
    assert_refused(sample_ad(href="http://example.test/"), "https")
    assert_refused(sample_ad(href="javascript:alert(1)"), "https")


@then("an ad offering the text-only inline unit or any unit the site does not know is refused")
def step_unknown_unit(context):
    picture = sample_ad()["images"]["half-page"]
    assert_refused(sample_ad(images={"inline": picture}), "unknown units")
    assert_refused(sample_ad(images={"skyscraper": picture}), "unknown units")


@then("a stretchy unit without its narrow picture is refused")
def step_narrow_required(context):
    picture = sample_ad()["images"]["half-page"]
    assert_refused(sample_ad(images={"band": {"wide": picture}}), "narrow")


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


# --- the slot scenarios: every ad fills its slot, with its label on its left edge and on top of it ---

IN_CONTENT_PARAGRAPH_FOR_CASES = {"story": 4, "pullquote": 3, "aside": 2}


@given("the fixture article with the {unit} ad in its words")
def step_article_with_unit(context, unit):
    """A real article's ad is chosen by its address, so the case page is the fixture article with the named unit set where an article would carry it."""
    import hooks
    article = (context.output_directory / "field-notes" / "durable-execution-for-agents" / "index.html").read_text(encoding="utf-8")
    article = re.sub(r'<aside class="mom-ad.*?</aside>', "", article, flags=re.S)
    ad = hooks._advertisements()[0]
    start = article.index('<article class="markus-document">')
    if unit == "band":
        end = article.rindex("</article>")
        page = article[:end] + mom.advertisement("band", ad, placement="article-end", contained=True) + article[end:]
    else:
        inserted, _ = hooks._after_paragraph(article[start:], IN_CONTENT_PARAGRAPH_FOR_CASES[unit], mom.advertisement(unit, ad, placement=f"article-{unit}"))
        page = article[:start] + inserted
    folder = context.output_directory / "_ad_cases" / unit
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(page, encoding="utf-8")
    context.slot_route = f"/_ad_cases/{unit}/"


def measure_slots(context, route, width, theme="light"):
    context.slot_measurements = None
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return
    result = subprocess.run(["node", str(SLOT_MEASURE_SCRIPT), served_origin(context), route, str(width), theme], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available")
        return
    context.slot_measurements = json.loads(result.stdout)


@when("I measure its advertisement in a browser {width:d} pixels wide")
def step_measure_case(context, width):
    measure_slots(context, context.slot_route, width)


@when('I measure the advertisements on the page "{route}" in a browser {width:d} pixels wide in the {theme} theme')
def step_measure_page(context, route, width, theme):
    measure_slots(context, route, width, theme)


def describe(ad):
    return f"{ad['placement']} ({ad['unit']}): column {ad['columnLeft']:.1f}+{ad['columnWidth']:.1f}, slot {ad['slotLeft']:.1f}+{ad['slotWidth']:.1f}, label {ad['labelLeft']:.1f}, picture {ad['pictureLeft']:.1f}+{ad['pictureWidth']:.1f}, gap {ad['gap']:.1f}"


@then("the label's left edge, the picture's left edge and the slot's left edge are the same line")
def step_left_edges(context):
    if not context.slot_measurements:
        return
    for ad in context.slot_measurements:
        assert abs(ad["labelLeft"] - ad["pictureLeft"]) <= PIXEL_TOLERANCE and abs(ad["pictureLeft"] - ad["slotLeft"]) <= PIXEL_TOLERANCE, describe(ad)


@then("every advertisement that is not floated starts and ends where its column does and its picture fills it")
def step_fills_column(context):
    if not context.slot_measurements:
        return
    for ad in context.slot_measurements:
        if ad["floated"] or ad["unit"] == "card":
            continue  # words flow around a floated ad, and a card's column is a cell of the card grid
        assert abs(ad["slotLeft"] - ad["columnLeft"]) <= PIXEL_TOLERANCE and abs(ad["slotWidth"] - ad["columnWidth"]) <= PIXEL_TOLERANCE, describe(ad)
        assert abs(ad["pictureWidth"] - ad["slotWidth"]) <= PIXEL_TOLERANCE, describe(ad)


@then("the picture of a card or a floated ad fills its own slot")
def step_card_fills_cell(context):
    if not context.slot_measurements:
        return
    for ad in context.slot_measurements:
        assert abs(ad["pictureWidth"] - ad["slotWidth"]) <= PIXEL_TOLERANCE, describe(ad)


@then("the label sits no more than {limit:d} pixels above its picture")
def step_label_gap(context, limit):
    if not context.slot_measurements:
        return
    assert limit == MAXIMUM_LABEL_GAP
    for ad in context.slot_measurements:
        assert 0 <= ad["gap"] <= limit, describe(ad)


# ------------------------------------------------------------------------------------------- promotion events

PROMOTION_SCRIPT = REPOSITORY_ROOT / "web" / "assets" / "mom.js"
PROMOTION_HARNESS = r"""
const vm = require('vm');
const source = require('fs').readFileSync(process.argv[1], 'utf8');
const section = source.slice(source.indexOf('/* promotion-events:start'), source.indexOf('/* promotion-events:end */'));
const attributes = {'data-promotion-id': 'anthus-busywork', 'data-promotion-name': 'Anthus AI Solutions', 'data-ad-unit': 'card', 'data-ad-placement': 'home-card'};
const slot = {getAttribute: name => attributes[name] ?? null};
const link = {closest: selector => (selector === 'a[href]' ? link : selector === '[data-promotion-id]' ? slot : null)};
const outside = {closest: selector => (selector === 'a[href]' ? outside : null)};
const handlers = {}, calls = [];
let observer;
const window = {
  papyrusAnalytics: {track: (name, params) => calls.push([name, params])},
  IntersectionObserver: class { constructor(callback, options) { observer = {callback, options, watched: []}; this.unobserve = s => observer.watched.splice(observer.watched.indexOf(s), 1); }
    observe(s) { observer.watched.push(s); } },
};
const document = {readyState: 'complete', querySelectorAll: () => [slot], addEventListener: (type, handler) => { handlers[type] = handler; }};
vm.runInNewContext(section, {window, document});
const seen = () => observer.callback([...observer.watched].map(target => ({target, isIntersecting: true})));
observer.callback([{target: slot, isIntersecting: false}]);
const beforeView = calls.length;
seen(); seen();
handlers.click({target: outside});
handlers.click({target: link});
handlers.auxclick({target: link});
console.log(JSON.stringify({threshold: observer.options.threshold, beforeView, calls}));
"""


def promotion_events(context):
    if not hasattr(context, "promotion_events"):
        if not shutil.which("node"):
            context.scenario.skip("node is not installed")
            return None
        result = subprocess.run(["node", "-e", PROMOTION_HARNESS, str(PROMOTION_SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        context.promotion_events = json.loads(result.stdout)
    return context.promotion_events


@then("every advertisement names its ad, its advertiser, its unit and its placement for analytics")
def step_ads_name_their_promotion(context):
    advertiser_of = {ad["id"]: ad["advertiser"] for ad in json.loads((REPOSITORY_ROOT / "web" / "ads.json").read_text())["ads"]}
    openings = re.findall(r"<aside [^>]*data-ad=[^>]*>", context.page)
    assert openings, "the page has no advertisements"
    for opening in openings:
        ad = re.search(r'data-ad="([^"]+)"', opening).group(1)
        assert f'data-promotion-id="{ad}"' in opening, opening
        assert f'data-promotion-name="{advertiser_of[ad]}"' in opening, opening
        assert re.search(r'data-ad-unit="[a-z-]+"', opening) and re.search(r'data-ad-placement="[a-z0-9-]+"', opening), opening


@then('the site script reports "view_promotion" once when half of an ad is on screen')
def step_view_promotion(context):
    events = promotion_events(context)
    if events is None:
        return
    assert events["threshold"] == 0.5, events
    assert events["beforeView"] == 0, "an ad off screen was reported as viewed"
    assert [name for name, _ in events["calls"]].count("view_promotion") == 1, events["calls"]


@then("the site script reports \"select_promotion\" each time an ad's link is opened, with the ad, advertiser, unit and placement only")
def step_select_promotion(context):
    events = promotion_events(context)
    if events is None:
        return
    selections = [params for name, params in events["calls"] if name == "select_promotion"]
    assert len(selections) == 2, events["calls"]  # a click and a middle click on the ad; the click elsewhere is not one
    for params in selections:
        assert params == {"promotion_id": "anthus-busywork", "promotion_name": "Anthus AI Solutions", "creative_name": "card", "location_id": "home-card"}, params
