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


@then('the page has a spine after its masthead that reads "{subject}"')
def step_page_spine(context, subject):
    after = context.page.split("</header>", 1)[1]
    spine = after[after.index('<nav class="mom-spine"'):].split("</nav>")[0]
    assert after.index('<nav class="mom-spine"') < after.index("<main"), context.route
    assert f"<span>{subject}</span>" in spine, spine[-300:]


@then('the stylesheet "{path}" shows the spine only when the window has room for it')
def step_spine_room(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert "body.mom > .mom-spine { display: none; }" in text
    room = text.split("@media (min-width: 1512px) and (min-height: 521px) {")[1].split("\n}")[0]
    assert "body.mom > .mom-spine { display: block;" in room and ".mom-brand-pill, .mom-home-pill { display: none; }" in room


@then("the article's picture is a slim band of placeholder art")
def step_slim_band(context):
    hero = context.page.split('class="mom-article-hero')[1].split("</div>")[0]
    assert "mom-article-hero-band" in context.page and "mom-art" in hero and "mom-ratio-" not in hero


@then("a body that opens with a figure has no separate picture above it")
def step_figure_body_no_band(context):
    body = '<article class="markus-document"><style>.a{}</style><figure class="papyrus-image"></figure></article>'
    assert _hero_for_body(body) == ""


@then("a body that opens with a figure has no separate picture above it, even with a card image")
def step_card_image_no_duplicate(context):
    body = '<article class="markus-document"><figure class="papyrus-image"></figure></article>'
    assert _hooks()._article_hero(SimpleNamespace(image="/card.png", url="/x/", title="X"), body) == ""


@then("a body whose opening figure sits inside a paragraph has no separate picture above it, even with a stored card image")
def step_wrapped_figure_no_duplicate(context):
    body = '<article class="markus-document"><p><figure class="papyrus-image papyrus-image--inline"></figure></p></article>'
    entry = SimpleNamespace(image="media/assets/a-story/cover.png", url="/x/", title="X")
    assert _hooks()._article_hero(entry, body) == ""


@then("a body whose style and figure both sit inside the opening paragraph has no separate picture above it, even with a stored card image")
def step_style_in_paragraph_no_duplicate(context):
    body = '<article class="markus-document"><p><style>.papyrus-image-dark{display:none}</style><figure class="papyrus-image papyrus-image--full"></figure></p></article>'
    entry = SimpleNamespace(image="media/assets/a-story/cover.png", url="/x/", title="X")
    assert _hooks()._article_hero(entry, body) == ""


@then("the side of the lead has no story cards")
def step_side_no_cards(context):
    side = context.page.split('class="mom-home-side"')[1].split('class="rh-features"')[0]
    assert "mom-sticker" in side and "mom-story-card" not in side


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


@then("the home page shows {count:d} findings, accepted ones only")
def step_findings_count(context, count):
    source = (REPOSITORY_ROOT / "web" / "pages" / "home.md").read_text()
    assert 'select="confident" bucket="week"' in source and 'heading="Findings"' in source and 'select="recommended"' not in source
    assert __import__("hooks").HOME_FINDINGS_SHOWN == count


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


@then('the stylesheet "{path}" aligns table headers left')
def step_table_headers_left(context, path):
    assert ".mom-article-body th { text-align: left; }" in (context.output_directory / path.lstrip("/")).read_text()


@then("the home page has {count:d} bands")
def step_band_count(context, count):
    assert context.page.count('class="mom-band mom-band-machine"') == count, context.page.count("mom-band-machine")


@then("the home page lists the most recent conversations in the side column")
def step_conversations_rail(context):
    home = (REPOSITORY_ROOT / "web" / "pages" / "home.md").read_text()
    rail = home.split('class="mom-home-rail"')[1].split('class="rh-features"')[0]
    assert 'kind="threads"' in rail and 'select="recent"' in rail and "mom-post-lines" not in home.split("::include")[0]


@then('the stylesheet "{path}" sets card headlines, article headlines and subheads in sentence case')
def step_sentence_case(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert re.search(r"\.mom-story-card:not\(\.mom-story-card-lead\) \.mom-story-card-headline \{[^}]*text-transform: none", text)
    for selector in (r"\.mom-headline", r"\.mom-article-body h2"):
        assert "uppercase" not in re.search(selector + r" \{[^}]*\}", text).group(0)


@then('the site\'s analytics property is "{measurement_id}" with consent mode on')
def step_analytics(context, measurement_id):
    chrome = __import__("json").loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())["chrome"]
    assert chrome["ga_measurement_id"] == measurement_id and "consent_mode" in chrome


def _output_page(context, route):
    return (context.output_directory / route.strip("/") / "index.html").read_text()


@then("the navigation starts with the site name, then a labelled home link with the Lucide house icon")
def step_home_pill(context):
    nav = context.page.split('class="mom-nav"', 1)[1]
    first, pill = nav.split("</a>", 2)[:2]
    assert 'class="mom-brand-pill"' in first, first
    assert 'class="mom-nav-pill mom-home-pill" href="/" aria-label="Home"' in pill and 'data-icon="house"' in pill, pill


@then("the spine's home link is the Lucide house icon")
def step_spine_home_icon(context):
    home = context.page.split('class="mom-spine-home"', 1)[1].split("</a>", 1)[0]
    assert 'aria-label="Home"' in home and 'data-icon="house"' in home and "mom-wordmark" not in home, home


@then('the stylesheet "{path}" hides the name and home pills exactly when the spine shows')
def step_home_pill_css(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-home-pill { display: inline-flex; justify-content: center; width: 44px; padding: 0; }" in text
    room = text.split("@media (min-width: 1512px) and (min-height: 521px) {")[1].split("\n}")[0]
    assert ".mom-brand-pill, .mom-home-pill { display: none; }" in room


@then('the stylesheet "{path}" sets the home card and latest posts side by side on a tablet')
def step_home_tablet(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert "@media (min-width: 640px) and (max-width: 899px) {\n  .mom-home-side { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));" in text


@then('the stylesheet "{path}" adds a column for each step up in window width')
def step_wide_cols(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    for query, cols in (("(min-width: 1512px) and (max-width: 1839px)", 4), ("(min-width: 1840px) and (max-width: 2199px)", 5), ("(min-width: 2200px)", 6)):
        assert f"@media {query} {{\n  body.mom {{ --mom-cols: {cols}; }}" in text


@then("the videos page shows no References of another medium")
def step_videos_only(context):
    assert context.page.count('class="mom-reference-card"') >= 1
    assert "Fixture paper" not in context.page and "Fixture report" not in context.page


@then('the stylesheet "{path}" keeps the card from covering the page when no accepted videos reserve room for it')
def step_videos_empty(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-refs-page:has(.mom-refs-stream .home-page-empty) .mom-page-card { height: auto; }" in text


@then('the stylesheet "{path}" hides an empty post rail and an empty story section, even with whitespace inside')
def step_empty_blocks(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-home-rail:has(.mom-post-lines:not(:has(> *))) { display: none; }" in text
    assert ".mom-section:has(> .mom-story-grid:not(:has(> *)))," in text


@then("a card with a Night image holds a Day picture and a Night picture")
def step_card_night(context):
    html = _mom().card_image("/day.png", seed="s", image_dark="/night.png")
    assert '<span class="mom-card-image-day"><img' in html and 'src="/day.png"' in html
    assert '<span class="mom-card-image-night"><img' in html and 'src="/night.png"' in html


@then("a card with no Night image holds one picture")
def step_card_one(context):
    html = _mom().card_image("/day.png", seed="s")
    assert html.count("<img") == 1 and "mom-card-image-night" not in html


@then('the stylesheet "{path}" shows the Night card image on a dark theme')
def step_card_night_css(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ":root[data-theme=dark] .mom-card-image-night { display: contents; }" in text
    assert ":root:not([data-theme=light]) .mom-card-image-night { display: contents; }" in text


@then('an accepted Reference rated 4 stars in the published data shows as our card with "{label}" on Findings')
def step_real_rated_card(context, label):
    page = (context.output_directory / "findings" / "index.html").read_text()
    assert f'aria-label="{label}"' in page
    assert 'class="home-page-tile"' not in page


@then("a thread card puts its anchor, title, picture, latest message and meta directly in the card")
def step_thread_card_flat(context):
    html = _mom().thread_card("A title", "/x", anchor="Reference: A source", author="AI", latest="A note", messages=1, last_at="1 Nov")
    assert "mom-thread-card-head" not in html
    for part in ("mom-thread-card-anchor", "mom-thread-card-title", "mom-thread-card-thumb", "mom-thread-card-latest", "mom-thread-card-meta"):
        assert part in html, part


@then('the stylesheet "{path}" shares the rows of thread cards across a row of cards')
def step_thread_rows(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-page .home-page-grid > li > .mom-thread-card { grid-row: span 4; grid-template-rows: subgrid; }" in text
    assert ".mom-page-top + .mom-section .home-page-grid:has(> li > .mom-thread-card)::before { grid-row: 1 / span 4; }" in text


@then('the stylesheet "{path}" shares the rows of story and finding cards across a row of cards')
def step_card_rows(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-page .home-page-grid > li > .mom-reference-card { display: grid; grid-row: span 6; grid-template-rows: subgrid; row-gap: 0; }" in text
    assert ".mom-story-grid > .mom-story-card > .mom-story-card-headline { grid-row: 4;" in text


@then("a thread card whose title repeats its source shows the title once")
def step_thread_once(context):
    html = _mom().thread_card("A source", "/x", anchor="Reference: A source")
    assert "mom-thread-card-anchor" not in html and html.count("A source") == 1
    assert "mom-thread-card-anchor" in _mom().thread_card("A question", "/x", anchor="Reference: A source")


@then('a suggested card with confidence {confidence:g} says "{prediction}"')
def step_acceptance_prediction(context, confidence, prediction):
    card = _mom().reference_card("A source", "/x", status="recommended", confidence=confidence)
    assert prediction in card and "%" not in card, card


def _home_band(page, index):
    bands = re.findall(r'<div class="mom-band mom-band-machine".*?</div></div>', page, re.S)
    assert len(bands) == 2, len(bands)
    return re.findall(r'<span class="mom-band-(?:word|on)">([^<]*)</span>', bands[index])


@then('the first home page band repeats "{phrase}"')
def step_first_band(context, phrase):
    assert " ".join(_home_band(context.page, 0)).startswith(phrase)
    assert set(_home_band(context.page, 0)) == {"Machines", "on"}


@then('the second home page band repeats "{phrase}"')
def step_second_band(context, phrase):
    assert " ".join(_home_band(context.page, 1)).startswith(phrase)
    assert set(_home_band(context.page, 1)) == {"Machines", "on"}


@then("the nav marks Findings, Videos, Conversations and Concepts as the newsroom group, and not Articles or Posts")
def step_nav_groups(context):
    nav = context.page.split('class="mom-nav"', 1)[1].split("</nav>", 1)[0]
    pills = dict((label, classes) for classes, label in re.findall(r'<a class="([^"]*mom-nav-pill[^"]*)"[^>]*>([A-Za-z]+)</a>', nav))
    for label in ("Findings", "Videos", "Conversations", "Concepts"):
        assert "mom-nav-pill-newsroom" in pills[label], pills
    for label in ("Articles", "Posts"):
        assert "mom-nav-pill-newsroom" not in pills[label], pills


@then('the stylesheet "{path}" styles every nav pill the same')
def step_uniform_nav(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-nav-pill-newsroom" not in text


@then('the stylesheet "{path}" shows every item of the home page lists and lays out the Latest Posts mosaic')
def step_home_rows(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-home .home-page-grid > li:nth-child(n + 4) { display: none; }" not in text
    assert ".rh-mosaic { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));" in text


@then('the stylesheet "{path}" turns the spine\'s name to read from the bottom up')
def step_spine_bottom_up(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert "body.mom > .mom-spine .mom-wordmark-vertical { transform: rotate(180deg); }" in text


@then('the stylesheet "{path}" lines up the home sentence and the Latest posts heading with the post titles')
def step_rail_edges(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-home-rail .mom-section-head { padding-left: var(--space-4); }" in text
    assert ".mom-home-purpose { margin: var(--space-12) 0 0;" in text
    assert "@media (min-width: 900px) and (max-width: 1839px) { .mom-home-purpose { padding-left: calc(var(--space-4) + var(--space-2)); } }" in text


@then('the page "{source}" lists accepted findings by week, highest rated first')
def step_ranked_by_week(context, source):
    text = (REPOSITORY_ROOT / source.lstrip("/")).read_text()
    assert 'select="recent" bucket="week"' in text, source


@then('"{route}" has the shared page header titled "{title}"')
def step_page_top(context, route, title):
    page = _output_page(context, route)
    assert f'<div class="mom-page-top"><header class="mom-page-head"><h1 class="mom-page-title">{title}</h1>' in page, route
    assert '<div class="mom-page-card mom-site-card-slot"><div class="mom-sticker' in page, route
    assert page.count("<h1") == 1, route


@then('"{route}" has the same site title card as the home page')
def step_same_card(context, route):
    assert _hooks()._site_card(heading_level=None) in _output_page(context, route), route


@then('the home page places the card with the same slot as every other page')
def step_home_slot(context):
    assert '<div class="mom-home-card mom-site-card-slot">' in _output_page(context, "/")


@then('"{route}" leads with "{lead}"')
def step_page_lead(context, route, lead):
    assert f'<p class="mom-dek">{lead}</p>' in _output_page(context, route)


@then('the stylesheet "{path}" lets the card bust out, up and right to the spine, with three columns')
def step_card_busts(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-site-card-slot { --mom-card-rise: var(--space-2); margin: var(--mom-card-rise) calc(2 * var(--space-3) - var(--space-12)) 0 calc(-1 * var(--space-2));" in text
    assert ".mom-grid-sticker { --mom-card-rise: -96px; }" in text


@then('the stylesheet "{path}" keeps the first grid\'s last cell free for the card in the page header')
def step_card_cell_free(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert '.mom-page-top + .mom-story-grid::before, .mom-page-top + .mom-section:not(.mom-refs-lead, .mom-refs-section, .mom-refs-stream) .home-page-grid::before, .mom-page-top + .mom-section > .mom-story-grid::before { content: ""; grid-column: -2 / -1; grid-row: 1 / span 6; }' in text


@then('the stylesheet "{path}" hides the header\'s card on a phone')
def step_card_phone(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert "@media (max-width: 639px) {\n  .mom-page-top { display: block; }\n  .mom-page-card { display: none; }" in text


@then("the home page and a type's listing both use the one site title card")
def step_one_site_card(context):
    hooks = _hooks()
    assert f'mom-site-card-slot">{hooks._site_card()}<p class="mom-home-purpose">' in hooks.block("sticker", {}, None)
    assert hooks.TAGLINE in hooks._site_card()


@then('the navigation links Articles to "{href}"')
def step_articles_nav(context, href):
    links = __import__("json").loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())["nav"]["links"]
    assert links[0] == {"label": "Articles", "href": href}


@then('the navigation links Posts to "{href}"')
def step_posts_nav(context, href):
    links = __import__("json").loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())["nav"]["links"]
    assert {"label": "Posts", "href": href} in links


@then("sections with newer updates come first on the Articles page")
def step_sections_by_recency(context):
    def story(topic, updated):
        return SimpleNamespace(type="article", url="/x/", topic=topic, updated=updated, date=updated, section=SimpleNamespace(is_type=True, label="Articles"))
    entries = [story("methods", "2026-11-01"), story("security", "2026-11-04"), story("methods", "2026-10-01")]
    assert [label for label, _ in _hooks()._stories_by_section(entries, "article")] == ["Privacy & Security", "Methods"]


@then('the stylesheet "{path}" gives a header\'s site title card a width')
def step_header_card_width(context, path):
    assert ".mom-section-hero .mom-sticker-fit { width: min(100%, 420px); }" in (context.output_directory / path.lstrip("/")).read_text()


@then('the stylesheet "{path}" stretches the main content to fill the window')
def step_main_fills(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert "min-height: 100dvh" in text and re.search(r"(?m)^main \{[^}]*flex: 1 0 auto", text)


def _mom():
    _hooks()
    return __import__("mom_components")


@then('an accepted card rated {stars:d} shows "{label}"')
def step_card_stars(context, stars, label):
    assert f'aria-label="{label}"' in _mom().reference_card("A source", "/x", stars=stars)


@then("an accepted card with no rating shows no stars")
def step_card_no_stars(context):
    assert "mom-stars" not in _mom().reference_card("A source", "/x")


@then("a suggested card shows no stars")
def step_suggested_no_stars(context):
    assert "mom-stars" not in _mom().reference_card("A source", "/x", status="recommended", stars=4)


@then("the card reads the rating from the stock tile's data-stars")
def step_tile_stars(context):
    tile = re.search(r"(.)(.*)", '"<h3 class="home-page-title"><a href="/x">A source</a></h3><span class="home-page-stars" data-stars="3"></span>', re.S)
    assert 'aria-label="3 of 5 stars"' in _hooks()._tile_to_reference_card(SimpleNamespace(group=lambda index: ("accepted", tile.group(2))[index - 1]))


@then("the spine shows no reading progress")
def step_spine_no_progress(context):
    assert "% read" not in context.page and "mom-spine-fill" not in context.page


@then('the stylesheet "{path}" fills the window with the spine and keeps the masthead and footer beside it')
def step_spine_full_window(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert re.search(r"body\.mom > \.mom-spine \{ display: block; position: fixed; top: 0; left: 0; bottom: 0;", text)
    assert "body.mom { padding-left: var(--spine-width); }" in text


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
    assert '<div class="mom-article-hero"><span class="mom-media"><img class="mom-card-image"' in context.page


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


def stylesheet_versions(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    phone, scaled = text.split("@media (min-width: 600px) {")
    assert "@media (max-width: 599px) {" in phone, f"{path} has no phone version"
    return phone, scaled


@then('the stylesheet "{path}" applies its designed sizes below 600 pixels and its sizes at 75% from 600 pixels up')
def step_stylesheet_is_dual(context, path):
    phone, scaled = stylesheet_versions(context, path)
    assert phone.count("@media (max-width: 599px) {") == 1 and scaled.strip(), path


@then('the stylesheet "{path}" sets the page text to {phone_size} pixels below 600 pixels and {scaled_size} pixels from 600 pixels up')
def step_page_text_sizes(context, path, phone_size, scaled_size):
    phone, scaled = stylesheet_versions(context, path)
    assert f"font-size: {phone_size}px; line-height: 1.5" in phone
    assert f"font-size: {scaled_size}px; line-height: 1.5" in scaled


@then('the stylesheet "{path}" opens its wide layout at {phone_width} pixels in the phone version and at {scaled_width} pixels in the scaled version')
def step_breakpoints_scaled(context, path, phone_width, scaled_width):
    phone, scaled = stylesheet_versions(context, path)
    assert f"@media (min-width: {phone_width}px)" in phone and f"@media (min-width: {phone_width}px)" not in scaled
    assert f"@media (min-width: {scaled_width}px)" in scaled


@then('the stylesheet "{path}" keeps its line height of 1.5 in both versions')
def step_unitless_untouched(context, path):
    phone, scaled = stylesheet_versions(context, path)
    assert "line-height: 1.5" in phone and "line-height: 1.5" in scaled and "line-height: 1.125" not in scaled


@then('the stylesheet "{path}" sets the root font size to 75% from 600 pixels up and not below')
def step_root_font_size(context, path):
    phone, scaled = stylesheet_versions(context, path)
    assert "html { font-size: 75%; }" in scaled and "html { font-size: 75%; }" not in phone


@when('I read the file "{route}"')
def step_read_file(context, route):
    context.file_route = route
    context.file_text = (context.output_directory / route.lstrip("/")).read_text(encoding="utf-8")


@then('the file allows everyone with "{line}"')
def step_file_allows_everyone(context, line):
    assert context.file_text.startswith(f"{line}\nAllow: /\n"), context.file_text


@then('the file allows "{agent}" to read everything')
def step_file_allows_agent(context, agent):
    assert f"\nUser-agent: {agent}\nAllow: /\n" in context.file_text, context.file_text


@then("the file blocks nobody")
def step_file_blocks_nobody(context):
    assert "Disallow" not in context.file_text, context.file_text


@then("the file points to the sitemap")
def step_file_points_to_sitemap(context):
    assert context.file_text.rstrip().splitlines()[-1].startswith("Sitemap: https://"), context.file_text


@given("the site's backend configuration")
def step_backend_configuration(context):
    context.backend_configuration = (REPOSITORY_ROOT / "papyrus.config.ts").read_text(encoding="utf-8")


@then("it turns edge invalidation off")
def step_invalidation_off(context):
    assert 'invalidation: "off"' in context.backend_configuration


@then("it lets the edge keep a page for {seconds:d} seconds")
def step_edge_lifetime(context, seconds):
    assert f"htmlSMaxAgeSeconds: {seconds}" in context.backend_configuration


@then("the concept cards appear in this order")
def step_concept_cards_in_order(context):
    found = re.findall(r'<span class="mom-wiki-card-term">([^<]+)</span>', context.page)
    expected = [row["concept"] for row in context.table]
    assert found == expected, f"{found} != {expected}"


@given("the site's stylesheet source")
def step_stylesheet_source(context):
    context.stylesheet_source = (REPOSITORY_ROOT / "web" / "css-src" / "site-theme.src.css").read_text(encoding="utf-8")


def _concept_spacer_rule(context):
    rules = [line for line in context.stylesheet_source.splitlines() if ".mom-page-top + .mom-wiki-grid::before" in line]
    assert len(rules) == 1, rules
    return rules[0]


@then("the concepts grid reserves the site card's column by height in proportion to the column")
def step_concept_spacer_proportional(context):
    assert "padding-bottom: 80%" in _concept_spacer_rule(context)


@then("it does not reserve a fixed number of rows")
def step_concept_spacer_no_row_count(context):
    assert "span" not in _concept_spacer_rule(context)


@then("the article headline fills its width and does not balance its lines")
def step_headline_fills_width(context):
    rules = [line for line in context.stylesheet_source.splitlines() if line.startswith(".mom-headline {")]
    assert len(rules) == 1, rules
    assert "text-wrap: pretty" in rules[0] and "balance" not in rules[0]


@then('the stylesheet "{path}" gives the mosaic and the featured sections more columns on a very wide window')
def step_wide_mosaic_and_features(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".rh-mosaic { grid-template-columns: repeat(var(--mom-cols, 4), minmax(0, 1fr)); }" in text
    assert ".rh-features { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr))" in text


@then('the stylesheet "{path}" lays a section\'s rows two across on a very wide window')
def step_wide_section_rows(context, path):
    text = (context.output_directory / path.lstrip("/")).read_text()
    assert ".mom-stories-section { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr))" in text
    assert '.mom-stories-section > .mom-stories-row[data-count="1"] { grid-column: 1 / -1; }' in text or '.mom-stories-row[data-count="1"] { grid-column: 1 / -1; }' in text


# ---------------------------------------------------------------------------------------------- section pages
# A section page is the home page for one section, so its blocks are found by the home page's own classes.

SECTION_BLOCK_OPENINGS = {
    "lead": '<div class="mom-home-lead">', "card": '<div class="mom-home-card mom-site-card-slot">', "conversations": '<section class="mom-home-rail"',
    "articles": '<div class="mom-story-grid mom-sf-cards">', "videos": '<div class="rh-mosaic mom-sf-videos">', "posts": '<section class="mom-section rh-latest mom-sf-posts"',
}


def _section_block(context, block):
    """The markup of one block of a section page: from where it opens to where the next block, or the end of the page, begins."""
    starts = {name: context.page.find(opening) for name, opening in SECTION_BLOCK_OPENINGS.items() if context.page.find(opening) != -1}
    assert block in starts, f"no {block} block on {context.route}"
    later = [position for position in starts.values() if position > starts[block]] + [context.page.index("</main>")]
    return context.page[starts[block]:min(later)]


def _section_title(context):
    return re.search(r'<h1 class="mom-section-title">(.*?)</h1>', context.page).group(1).replace("&amp;", "&")


@then('the page "{route}" was projected')
def step_projected_page(context, route):
    assert (context.output_directory / route.strip("/") / "index.html").exists(), route


@then("the generated section pages are up to date with web/sections.json and the template")
def step_sections_generated(context):
    sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
    import sync_section_pages
    assert sync_section_pages.stale_files() == [], sync_section_pages.stale_files()


@then('the section page is titled "{title}" with a small label heading like the home page\'s')
def step_section_label(context, title):
    assert f'<div class="mom-section-head rh-label"><h1 class="mom-section-title">{title}</h1>' in context.page
    assert context.page.count("<h1") == 1


@then('the section page counts "{text}"')
def step_section_counts(context, text):
    assert f'<p class="mom-meta mom-sf-counts">{text}</p>' in context.page, re.findall(r'mom-sf-counts">(.*?)</p>', context.page)


@then("the section page has the home page's top row: the lead article, then the site title card with the conversations rail beside it")
def step_section_top_row(context):
    assert '<div class="mom-home-top rh-top"><div class="mom-home-lead">' in context.page.replace("\n", "")
    assert context.page.index("mom-home-lead") < context.page.index("mom-home-side") < context.page.index("mom-sticker") < context.page.index("mom-home-rail")


@then('the section page says "{text}" under the site title card')
def step_section_purpose(context, text):
    assert f'<p class="mom-home-purpose">{text}</p>' in context.page


@then('the section page\'s lead article is "{title}"')
def step_section_lead(context, title):
    lead = _section_block(context, "lead")
    assert "mom-story-card-lead" in lead and title in lead, lead[:300]


@then("the section page shows only articles of its own section")
def step_section_only_own(context):
    cards = re.findall(r'<a class="mom-story-card[^"]*" href="([^"]*)">.*?<span class="mom-kicker">(.*?)</span>', _section_block(context, "articles"), re.S)
    assert cards and all(href.startswith("/articles/") and kicker.replace("&amp;", "&") == _section_title(context) for href, kicker in cards), cards


def _lines(block):
    return re.findall(r'<a class="mom-post-line" href="[^"]*"><span class="mom-post-line-title">(.*?)</span>', block)


@then('the rail lists the conversations "{titles}" as lines')
def step_section_conversations(context, titles):
    assert _lines(_section_block(context, "conversations")) == titles.split(", "), _lines(_section_block(context, "conversations"))


@then('the section page shows {count:d} posts as picture cards in the mosaic, each a small card with no blurb')
def step_section_posts(context, count):
    block = _section_block(context, "posts")
    cards = re.findall(r'<a class="mom-story-card mom-story-card-small rh-post" href="/posts/[^"]*">.*?</a>', block, re.S)
    assert len(cards) == count, len(cards)
    assert all("mom-card-image" in card and "mom-blurb" not in card and "mom-kicker" not in card for card in cards)
    assert "mom-story-card-large" not in block and "mom-post-line" not in block and '<div class="rh-mosaic mom-sf-post-grid">' in block


@then("no post on the page is drawn as a large card or as a line")
def step_no_large_post(context):
    assert not re.search(r'<a class="mom-story-card[^"]*mom-story-card-(?:large|lead)[^"]*" href="/posts/', context.page)
    assert 'class="mom-post-line" href="/posts/' not in context.page


@then("the section page shows {count:d} videos in the Worth Watching panel, all from its own section")
def step_section_videos(context, count):
    import json
    block = _section_block(context, "videos")
    shown = re.findall(r'<span class="mom-reference-card-title">(.*?)</span>', block)
    own = {
        reference["title"] for reference in json.loads((REPOSITORY_ROOT / "tests" / "fixtures" / "_data" / "home-page" / "references.json").read_text())["references"]
        if reference.get("medium") == "video" and reference.get("status") == "accepted" and reference.get("section") == _section_title(context)
    }
    assert "Worth Watching</h2>" in block and len(shown) == count and set(shown) <= own, (shown, own)


@then('the section page ends its videos with the link "{text}" to "{href}"')
def step_section_more_videos(context, text, href):
    assert f'<p class="mom-more"><a class="mom-more-link" href="{href}">{text}</a></p>' in _section_block(context, "videos")


@then('the section page has no "{text}" link')
def step_section_no_more(context, text):
    assert f">{text}</a>" not in context.page


@then("the section page has no videos panel and no conversations and no findings panel")
def step_section_no_blocks(context):
    assert "mom-reference-card" not in context.page and "Worth Watching" not in context.page and 'class="mom-section-title-link" href="/gaming/findings/"' not in context.page
    assert not _lines(_section_block(context, "conversations"))


@then("the section page has no articles, no videos, no posts and no conversations")
def step_section_nothing(context):
    assert "mom-story-card" not in context.page and "mom-reference-card" not in context.page and not _lines(_section_block(context, "conversations"))


@then("the section page's blocks come in this order in the markup")
def step_section_block_order(context):
    positions = [context.page.find(SECTION_BLOCK_OPENINGS[row["block"]]) for row in context.table]
    assert all(position != -1 for position in positions) and positions == sorted(positions), positions


@then('the home page group "{label}" links to "{href}" and ends with "{text}"')
def step_home_group_links(context, label, href, text):
    group = _home_group(context, label)
    assert f'<a class="mom-section-title-link" href="{href}">' in group, group[:300]
    assert group.replace("&amp;", "&").rstrip().endswith(f'<p class="mom-more"><a class="mom-more-link" href="{href}">{text}</a></p>'), group[-300:]


@then('the home page group "{label}" links to "{href}" and has no More link')
def step_home_group_no_more(context, label, href):
    group = _home_group(context, label)
    assert f'<a class="mom-section-title-link" href="{href}">' in group and "mom-more" not in group, group[:300]


def _home_group(context, label):
    groups = re.findall(r'<section class="papyrus-group [^"]*" data-section="[^"]*"[^>]*>(.*?)</section>', context.page, re.S)
    found = [group for group in groups if f">{label}</a>".replace("&", "&amp;") in group]
    assert found, f"no group named {label!r}"
    return found[0]


@then('the stylesheet "{path}" shows only whole rows of cards on wide windows, and hides a block with nothing in it')
def step_section_whole_rows(context, path):
    phone, _ = stylesheet_versions(context, path)
    assert ".mom-sf-cards > :nth-child(n + 11), .mom-sf-post-grid > :nth-child(n + 11) { display: none; }" in phone
    assert ".mom-sf-cards:not(:has(> *)), .mom-sf-videos:not(:has(a)), .mom-sf-posts-block:not(:has(.mom-story-card)) { display: none; }" in phone
    assert ".rh-mosaic > .rh-post { grid-column: span 1;" in phone


@then('the link preview picture "{address}" is served from "{expected}"')
def step_social_image(context, address, expected):
    hooks = _hooks()
    assert hooks._social_image_url(address) == expected, hooks._social_image_url(address)
    meta = f'<meta property="og:image" content="{address}">'
    assert expected in hooks._social_image_urls(meta)


@then('the byline of a story drafted by an agent whose author is "{author}" reads "{expected}"')
def step_byline_author_only(context, author, expected):
    entry = SimpleNamespace(authors=[author], data={"drafting": {"by": "agent"}})
    assert _hooks()._byline(entry) == expected, _hooks()._byline(entry)


@then('the byline of a story drafted by an agent approved by "{approver}" with author "{author}" reads "{expected}"')
def step_byline_approved_and_author(context, approver, author, expected):
    entry = SimpleNamespace(authors=[author], data={"drafting": {"by": "agent"}, "approval": {"status": "approved", "by": approver}})
    assert _hooks()._byline(entry) == expected, _hooks()._byline(entry)

FINDINGS_GRID = 'aria-label="Findings"'


@then('"{first}" comes before the Findings grid')
def step_before_findings(context, first):
    one, two = context.page.find(first), context.page.find(FINDINGS_GRID)
    assert one != -1 and two != -1 and one < two, f"{first!r} at {one}, the Findings grid at {two}"


@then('the home page ends with a "Findings" grid of accepted References, none of them a video')
def step_home_findings(context):
    grid = context.page.split(FINDINGS_GRID, 1)[1].split("</section>", 1)[0]
    cards = re.findall(r'<a class="mom-reference-card"[^>]*href="([^"]*)"', grid) or re.findall(r'class="mom-reference-card" href="([^"]*)"', grid)
    assert 0 < len(cards) <= 16 and len(cards) == len(set(cards)), cards
    assert "youtube.com/watch" not in grid, "a video is in the Findings grid"
    assert "Accepted" in grid and "Not accepted yet" not in grid and "Recommended by Cyclotron" not in grid
    assert FINDINGS_GRID not in context.page.split(FINDINGS_GRID, 1)[1], "more than one Findings grid"
    assert "mom-reference-card" not in context.page.split(FINDINGS_GRID, 1)[1].split("</section>", 1)[1]


@then('no projected page links to "{address}" and none is projected there')
def step_no_links_to(context, address):
    assert not (context.output_directory / address.strip("/")).exists(), address
    for page in context.output_directory.rglob("*.html"):
        assert f'href="{address}"' not in page.read_text(encoding="utf-8"), page


@then('the page asks "{path}" on its own origin without credentials')
def step_consent_lookup(context, path):
    assert f'fetch("{path}",' in context.page and "credentials:'omit'" in context.page, "no same-origin consent request"


@then("the cookie notice is in the page but hidden")
def step_notice_hidden(context):
    banner = re.search(r'<div id="papyrus-consent-banner"[^>]*>', context.page)
    assert banner and " hidden" in banner.group(0), banner and banner.group(0)


@then("the page's notice decision for the answer {answer} is {decision}")
def step_notice_decision(context, answer, decision):
    import json
    import subprocess
    function = re.search(r"c\.needsNotice=(function\(a\)\{.*?\});", context.page).group(1)
    script = f"const f={function};process.stdout.write(String(f(JSON.parse(process.argv[1]))))"
    result = subprocess.run(["node", "-e", script, answer], capture_output=True, text=True, check=True).stdout
    assert result == {"notice": "true", "no notice": "false"}[decision], (answer, result)
