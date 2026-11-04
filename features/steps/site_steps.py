import re
import sys
from types import SimpleNamespace

from behave import given, then, when

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "tests"))

from projection_support import REPOSITORY_ROOT, page_text  # noqa: E402


@given("the Machines on Machines site is projected from the fixtures")
def step_projected(context):
    assert (context.output_directory / "index.html").exists()


@when('I open the page "{route}"')
def step_open(context, route):
    context.route = route
    context.page = page_text(context.output_directory, route)


@then('the page contains "{text}"')
def step_contains(context, text):
    assert text in context.page, f"{context.route} does not contain {text!r}"


@then('the page does not contain "{text}"')
def step_lacks(context, text):
    assert text not in context.page, f"{context.route} contains {text!r}"


@then('"{first}" comes before "{second}"')
def step_order(context, first, second):
    one, two = context.page.find(first), context.page.find(second)
    assert one != -1 and two != -1 and one < two, f"{first!r} at {one}, {second!r} at {two}"


@then("the page shows {count:d} reference cards under \"{heading_id}\"")
def step_reference_count(context, count, heading_id):
    block = context.page.split(f'id="{heading_id}"')[1].split("</section>")[0]
    assert block.count('class="mom-reference-card"') == count, block.count('class="mom-reference-card"')


@then("the page shows {count:d} thread cards under \"{heading_id}\"")
def step_thread_count(context, count, heading_id):
    block = context.page.split(f'id="{heading_id}"')[1].split("</section>")[0]
    assert block.count('class="mom-thread-card"') == count


@then('the reference card for "{address}" is drawn with the "{composition}" placeholder art')
def step_reference_art(context, address, composition):
    card = re.search(rf'<a class="mom-reference-card" href="{re.escape(address)}">.*?</a>', context.page, re.S)
    assert card, f"no card for {address}"
    assert f"mom-art-{composition}" in card.group(0), card.group(0)[:300]


@then("every card on the page has an image or placeholder art")
def step_every_card(context):
    cards = re.findall(r'<a class="mom-(?:story|reference|thread)-card[^"]*".*?</a>', context.page, re.S)
    assert cards
    bad = [card[:100] for card in cards if "<img" not in card and "mom-art " not in card]
    assert not bad, bad


@then("the same address always draws the same art")
def step_same_art(context):
    import mom_components as mom
    assert mom.placeholder_art("https://example.test/x") == mom.placeholder_art("https://example.test/x")


@then('the seed "{seed}" chooses the "{composition}" composition in the "{tone}" tone')
def step_seed(context, seed, composition, tone):
    import mom_components as mom
    assert mom.choose_placeholder_art(seed) == (composition, tone), mom.choose_placeholder_art(seed)


@then('the stylesheet "{path}" defines Day colors and Night colors')
def step_themes(context, path):
    text = (context.output_directory / path).read_text()
    assert ":root {" in text and "prefers-color-scheme: dark" in text and ':root[data-theme="dark"]' in text


@then('the stylesheet "{path}" gives "{token}" a different value by night than by day')
def step_token_differs(context, path, token):
    text = (context.output_directory / path).read_text()
    values = re.findall(rf"--{re.escape(token)}:\s*([^;]+);", text)
    assert len(set(values)) > 1, values


@then("no projected page contains the word \"{word}\"")
def step_no_word(context, word):
    offenders = [p.name for p in context.output_directory.rglob("*.html") if re.search(rf"\b{word}\b", p.read_text(), re.I)]
    assert not offenders, offenders


@then('the stylesheet "{path}" sets "{token}" above {minimum:g}em')
def step_token_above(context, path, token, minimum):
    text = (context.output_directory / path).read_text()
    value = float(re.search(rf"--{re.escape(token)}:\s*([\d.]+)em;", text).group(1))
    assert value > minimum, value


@then('in the stylesheet "{path}" the wordmark seal is drawn behind the words')
def step_seal_behind(context, path):
    text = (context.output_directory / path).read_text()
    assert re.search(r"\.mom-wordmark-on \{[^}]*z-index: 0", text)
    assert re.search(r"\.mom-wordmark > span:not\(\.mom-wordmark-on\) \{[^}]*z-index: 1", text)


@then("the spine tells the stylesheet its name is {characters:d} characters long")
def step_spine_characters(context, characters):
    assert f"--mom-spine-characters: {characters}" in context.page, context.route


@then('the stylesheet "{path}" sizes the spine\'s section name to fit the room it has')
def step_spine_fits(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert re.search(r"font-size: min\(clamp\(32px, 5\.6vh, 70px\), calc\(var\(--mom-spine-room\) / \(var\(--mom-spine-characters", text)


@then('the stylesheet "{path}" collapses the spine to a band on a page shorter than {height:d}px')
def step_spine_band(context, path, height):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert re.search(rf"@media \(max-height: {height}px\) and \(min-width: 900px\) \{{[^@]*\.mom-spine \{{[^}}]*height: 56px", text)


@then("the article's picture is a slim band of placeholder art")
def step_slim_band(context):
    hero = context.page.split('class="mom-article-hero')[1].split("</div>")[0]
    assert "mom-article-hero-band" in context.page and "mom-art" in hero and "mom-ratio-wide" not in hero


@then("a body that opens with a figure has no separate picture above it")
def step_figure_body_no_band(context):
    body = '<article class="markus-document"><style>.a{}</style><figure class="papyrus-image"></figure></article>'
    assert _hero_for_body(body) == ""


@then("a body that opens with a figure has no separate picture above it, even with a card image")
def step_card_image_no_duplicate(context):
    body = '<article class="markus-document"><figure class="papyrus-image"></figure></article>'
    assert _hooks()._article_hero(SimpleNamespace(image="/card.png", url="/x/", title="X"), body) == ""


@then("the side of the lead holds only the wordmark")
def step_side_only_wordmark(context):
    side = context.page.split('class="mom-home-side"')[1].split('<section')[0]
    assert "mom-sticker" in side and "mom-story-card" not in side and "mom-reference-card" not in side


@then("a body with no figure at the top still gets the band")
def step_plain_body_band(context):
    body = '<article class="markus-document"><p>Words.</p><figure class="papyrus-image"></figure></article>'
    assert "mom-article-hero-band" in _hero_for_body(body)


@then('the stylesheet "{path}" centers everything in an article in one reading column')
def step_centered_column(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert re.search(r"\.mom-article > \* \{[^}]*max-width: var\(--measure\); margin-inline: auto;", text)


@then("concepts used by more stories come first in See also")
def step_see_also_ranked(context):
    def story(*tags):
        return SimpleNamespace(type="article", tags=tags)
    entry = story("Rare", "Common")
    page = SimpleNamespace(entries=[entry, story("Common"), story("Common")])
    hooks = _hooks()
    html = hooks._see_also_html(entry, page, {hooks._hashtag_key("Rare"): "/wiki/rare/", hooks._hashtag_key("Common"): "/wiki/common/"})
    assert html.index("#Common") < html.index("#Rare"), html


@then("a body with citations gets a References heading after See also")
def step_references_heading(context):
    html = _hooks()._with_end_matter('<article><p>Text.</p><ol class="citationslist"><li>One</li></ol></article>', "<section>SEE</section>")
    assert html.index("SEE") < html.index(">References<") < html.index("citationslist"), html


@then("a body with no citations gets no References heading")
def step_no_references_heading(context):
    assert "References" not in _hooks()._with_end_matter("<article><p>Text.</p></article>", "")


@then("the home page asks for {count:d} findings")
def step_consideration_count(context, count):
    assert f'select="recommended" count="{count}"' in (REPOSITORY_ROOT / "web" / "pages" / "home.md").read_text()


@then('the stylesheet "{path}" splits a panel of cards into three, two and one columns')
def step_panel_columns(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-panel .home-page-grid[data-card] { grid-template-columns: repeat(3, minmax(0, 1fr)); }" in text
    tablet = text.split("@media (max-width: 899px) {")[1]
    assert re.search(r"\.mom-panel \.home-page-grid\[data-card\] \{ grid-template-columns: repeat\(2", tablet)
    phone = text.split("@media (max-width: 640px) {")[1]
    assert ".mom-panel .home-page-grid[data-card]" in phone.split("}")[0]


@then('the stylesheet "{path}" draws a callout as a filled, rounded panel')
def step_callout_panel(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert re.search(r"\.markus-callout \{[^}]*padding: var\(--space-6\)[^}]*border-radius[^}]*background: var\(--panel\)", text)


@then("the spine shows no reading progress")
def step_spine_no_progress(context):
    assert "% read" not in context.page and "mom-spine-fill" not in context.page


@then('the stylesheet "{path}" fills the window with the spine and keeps the masthead and footer beside it')
def step_spine_full_window(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert re.search(r"\.mom-article-layout \.mom-spine \{ position: fixed; top: 0; right: 0; bottom: 0;", text)
    assert "body.mom:has(.mom-article-layout) { padding-right: var(--spine-width); }" in text


@then('the stylesheet "{path}" paints the canvas in the brand color')
def step_canvas_brand_color(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert "html { background: var(--brand); }" in text
    assert re.search(r"body\.mom \{[^}]*background: var\(--brand\)", text)
    assert re.search(r"(?m)^main \{[^}]*background: var\(--paper\)", text)


@then("the browser chrome is told to use the brand color in Day and Night")
def step_chrome_brand_color(context):
    page = page_text(context.output_directory, "/")
    assert '<meta name="theme-color" content="#1f2a44">' in page
    assert '<meta name="theme-color" content="#2a3a5e" media="(prefers-color-scheme: dark)">' in page


@given('an article published under "/articles/" with the section "{section}"')
def step_article_with_section(context, section):
    context.article = SimpleNamespace(section=SimpleNamespace(is_type=True, label="Articles"), topic=section)


@given('an article published under "/articles/" with no section')
def step_article_without_section(context):
    context.article = SimpleNamespace(section=SimpleNamespace(is_type=True, label="Articles"), topic=None)


@then('its topic reads "{topic}"')
def step_topic_reads(context, topic):
    assert _hooks()._topic_label(context.article) == topic


@then("it has no topic label")
def step_no_topic(context):
    assert _hooks()._topic_label(context.article) == ""


@then('the list of articles is titled "Machines on Machines"')
def step_type_list_subject(context):
    assert _hooks()._listing_subject(SimpleNamespace(is_type=True, label="Articles"), "Articles") == "Machines"


@then('the line under the headline is "{text}"')
def step_subtitle(context, text):
    assert f'<p class="mom-dek">{text}</p>' in context.page, context.page[:400]


@then('the page does not contain "{text}" in its article')
def step_not_in_article(context, text):
    article = context.page.split('<article class="mom-article">')[1].split("</article>")[0]
    assert text not in article


def _hooks():
    sys.path.insert(0, str(REPOSITORY_ROOT / "web"))
    import hooks
    return hooks


def _hero_for_body(body):
    return _hooks()._article_hero(SimpleNamespace(image=None, url="/x/", title="X"), body)


@then("the article's picture is the wide image")
def step_wide_image(context):
    assert '<div class="mom-article-hero"><img class="mom-card-image mom-ratio-wide"' in context.page


@then('every color in the stylesheet "{path}" except the focus ring is close to gray or ink blue')
def step_neutral_palette(context, path):
    text = (context.output_directory / path).read_text()
    too_colorful = []
    for name, value in re.findall(r"--([\w-]+):\s*#([0-9a-fA-F]{6});", text):
        channels = [int(value[index:index + 2], 16) for index in (0, 2, 4)]
        if name != "focus" and (max(channels) - min(channels)) / 255 > 0.35:
            too_colorful.append(f"--{name}: #{value}")
    assert not too_colorful, too_colorful


@then('the site does not serve "{route}"')
def step_not_served(context, route):
    assert not (context.output_directory / route.strip("/") / "index.html").exists(), f"{route} was projected"


SITE_STYLESHEET = __import__("pathlib").Path(__file__).resolve().parents[2] / "web" / "css" / "site-theme.css"


@given("the site's stylesheet")
def step_site_stylesheet(context):
    context.stylesheet = SITE_STYLESHEET.read_text()


@then('the rule for "{selector}" sets "{property_name}" to "{value}"')
def step_rule_sets(context, selector, property_name, value):
    bodies = re.findall(rf"(?:^|\n){re.escape(selector)} {{([^}}]*)}}", context.stylesheet)
    assert any(re.search(rf"(?:^|[;\s]){re.escape(property_name)}:\s*{re.escape(value)}\s*(?:;|$)", body.strip()) for body in bodies), f"{selector} does not set {property_name}: {value}"


@then('the stylesheet does not set "{property_name}"')
def step_stylesheet_lacks(context, property_name):
    assert not re.search(rf"^\s*[^/\s].*\b{re.escape(property_name)}:", context.stylesheet, re.M), f"the stylesheet sets {property_name}"
