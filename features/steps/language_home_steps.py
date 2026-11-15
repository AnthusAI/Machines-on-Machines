"""Steps for features/language-home.feature: the home of a language edition (projected by tests/language_cases.py) and its empty and fallback cases (built from a stub page)."""

import html
import re
from types import SimpleNamespace

from behave import given, then

from projection_support import REPOSITORY_ROOT  # noqa: E402

import sys
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))
import hooks  # noqa: E402
import languages  # noqa: E402

STYLESHEET = REPOSITORY_ROOT / "web" / "css-src" / "site-theme.src.css"


def main_of(page):
    return page.split("<main", 1)[1].split("</main>", 1)[0]


def text(markup):
    return html.unescape(re.sub(r"<[^>]+>", "", markup))


@then('the home heading reads "{heading}"')
def step_heading(context, heading):
    assert re.search(rf'<h2 class="mom-section-title">{re.escape(heading)}</h2>', main_of(context.language_page)), heading


@then('the home lead article is "{title}"')
def step_lead(context, title):
    lead = re.search(r'<div class="mom-home-lead">(.*?)</div>', main_of(context.language_page), re.S).group(1)
    assert text(re.search(r'<span class="mom-story-card-headline">(.*?)</span>', lead).group(1)) == title, lead


@then('the site card tagline reads "{tagline}"')
def step_tagline(context, tagline):
    assert f'<p class="mom-sticker-tagline mom-sticker-tagline-display">{tagline}</p>' in main_of(context.language_page)


@then('the home purpose reads "{purpose}"')
def step_purpose(context, purpose):
    assert f'<p class="mom-home-purpose">{purpose}</p>' in main_of(context.language_page)


@then('every story link on the home is under "{prefix}"')
def step_links(context, prefix):
    links = re.findall(r'<a class="mom-story-card[^"]*" href="([^"]*)"', main_of(context.language_page))
    assert links and all(link.startswith(prefix) for link in links), links


@then('the home links "{words}" to "{address}"')
def step_link(context, words, address):
    assert re.search(rf'<a class="mom-more-link" href="{re.escape(address)}">{re.escape(words)}</a>', main_of(context.language_page)), words


@then('the home links "{words}" to "{address}" marked as English')
def step_english_link(context, words, address):
    found = re.search(rf'<a class="mom-section-link mom-link-english" href="{re.escape(address)}" lang="en" hreflang="en">{re.escape(words)}<svg', main_of(context.language_page))
    assert found, words


@then("the lead picture is eager with high priority and no other card picture is")
def step_eager(context):
    pictures = re.findall(r"<img [^>]*>", main_of(context.language_page))
    eager = [picture for picture in pictures if 'loading="eager" fetchpriority="high"' in picture]
    assert len(eager) <= 1 and all('loading="lazy"' in picture for picture in pictures if picture not in eager), pictures
    lead = re.search(r'<div class="mom-home-lead">(.*?)</div>', main_of(context.language_page), re.S).group(1)
    assert ("<img" not in lead) or ('loading="eager" fetchpriority="high"' in lead), lead


@then("the picture frames have a flat panel tone")
def step_tone(context):
    assert re.search(r"\.mom-card-image \{[^}]*background: var\(--panel\)", (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text(encoding="utf-8"))


def stub_page(entries, strings, primary="en", language="es-419"):
    return SimpleNamespace(
        kind="home", entries=entries, strings=strings, language=language, primary_language=primary, ranker=None,
        untranslated={"tag": "en", "name": "English", "url": "/"},
        ranked=lambda found, bucket=None: list(found),
        link_in_language=lambda path: (f"/es{path}", False),
        components=SimpleNamespace(untranslated_notice=lambda words, found: f'<p class="mom-untranslated">{words["listing.untranslated"].format(original=found["name"])}</p>'),
    )


def stub_entry(topic, title, url):
    section = SimpleNamespace(is_type=False, label=topic.title(), name=topic, base=topic)
    return SimpleNamespace(type="article", url=url, link=None, title=title, summary_text="Resumen.", date="2026-11-10", image=None, image_dark=None,
                           topic=topic, section=section, derived={}, summary=SimpleNamespace(front_matter={}), data={}, authors=(), tags=())


SPANISH = languages.interface_strings()["es-419"]


@given("a language home with no translated Story")
def step_empty(context):
    context.edition_home = hooks._edition_home(stub_page([], SPANISH))


@then("the home says nothing is translated yet and links to the English index")
def step_empty_says(context):
    assert "Todavía no hay traducciones aquí" in context.edition_home and "mom-untranslated" in context.edition_home


@then("the home has no article group")
def step_no_group(context):
    assert "rh-edition-group" not in context.edition_home


@given("a language home with a section the language does not name")
def step_unnamed(context):
    strings = {key: value for key, value in SPANISH.items() if not key.startswith("section.security.")}   # the language names every section now; this one it does not
    strings["section.agents.label"] = "Agentes"
    entries = [stub_entry("agents", "Primero", "/es/agentes/primero/"), stub_entry("agents", "Un agente", "/es/agentes/uno/"),
               stub_entry("security", "Segundo", "/es/seguridad/segundo/"), stub_entry("security", "Tercero", "/es/seguridad/tercero/")]
    context.edition_home = hooks._edition_home(stub_page(entries, strings))


@then('that section\'s heading is its English name marked lang "en"')
def step_english_name(context):
    assert re.search(r'<h2 id="mom-edition-\d+" class="mom-section-title" lang="en">Security</h2>', context.edition_home), context.edition_home


@then("a section the language names uses the language's name")
def step_named(context):
    assert re.search(r'<h2 id="mom-edition-\d+" class="mom-section-title">Agentes</h2>', context.edition_home), context.edition_home


@then("the Chinese stylesheet names Chinese faces, normal style and no letter-spacing")
def step_chinese_css(context):
    css = STYLESHEET.read_text(encoding="utf-8")
    block = css[css.index("Chinese typography"):]
    assert "PingFang SC" in block and "Noto Sans CJK SC" in block and "Microsoft YaHei" in block
    assert "font-style: normal" in block and "letter-spacing: 0" in block and "text-transform: none" in block


@then('each section group links "{words}" to its English page marked as English')
def step_section_links(context, words):
    groups = re.findall(r'<section class="mom-section rh-edition-group"[^>]*data-section="([^"]*)">(.*?)</section>', context.edition_home, re.S)
    assert groups
    for identifier, body in groups:
        assert re.search(rf'<a class="mom-section-link mom-link-english" href="/{identifier}/" lang="en" hreflang="en">{words}<span class="mom-visually-hidden">: [^<]+</span><svg', body), identifier


@given("a language sectioned page with a section the language names and one it does not")
def step_sectioned(context):
    strings = {key: value for key, value in SPANISH.items() if not key.startswith("section.security.")}
    strings["section.agents.label"] = "Agentes"
    entries = [stub_entry("agents", f"Agente {number}", f"/es/articulos/agente-{number}/") for number in range(30)] + [stub_entry("security", "Seguridad", "/es/articulos/seguridad/")]
    for entry in entries:
        entry.date = "2026-11-10"
        entry.updated = "2026-11-10"
        entry.slug = entry.title
        entry.section = SimpleNamespace(is_type=False, label=entry.topic.title(), name=entry.topic, base=entry.topic)
    context.sectioned = hooks._sectioned_page(entries, "article", "Artículos", "Lead", lambda name: (f"/{name}/", name), None, strings, strings["site.tagline"])


@then('the named section\'s heading is the language\'s name and the other is its English name marked lang "en"')
def step_sectioned_headings(context):
    assert '<h2 class="mom-section-title"><a class="mom-section-title-link" href="/agents/">Agentes</a></h2>' in context.sectioned, context.sectioned[:3000]
    assert '<span lang="en">Security</span>' in context.sectioned


@then('the count reads "{count}" and the link at the end reads "{link}"')
def step_sectioned_words(context, count, link):
    assert count in context.sectioned, context.sectioned
    assert link in context.sectioned


def ranked_page(entries, rank_of):
    """A stub edition page whose Story ranking puts the entries in `rank_of`'s order (best first) and whose `entries` stay newest first."""
    page = stub_page(entries, SPANISH)
    page.ranked = lambda found, bucket=None: sorted(found, key=lambda entry: rank_of[entry.title])
    return page


def post(number):
    entry = stub_entry("agents", f"Post {number}", f"/es/publicaciones/post-{number}/")
    entry.type = "post"
    entry.date = f"2026-11-{20 - number:02d}"
    return entry


@given("a language home with eight posts, newest first, that the ranking puts in the opposite order")
def step_posts(context):
    posts = [post(number) for number in range(1, 9)]   # Post 1 is the newest
    context.edition_home = hooks._edition_home(ranked_page([stub_entry("agents", "Un artículo", "/es/articulos/uno/"), *posts], {"Un artículo": -1, **{f"Post {n}": 9 - n for n in range(1, 9)}}))


@then("the latest posts are the six newest, newest first")
def step_latest(context):
    latest = context.edition_home.split('id="mom-latest-posts"', 1)[1].split("</section>", 1)[0]
    assert re.findall(r"Post \d", text(latest)) == [f"Post {n}" for n in range(1, 7)], text(latest)


@then("the top posts are the other two, in the ranking's order")
def step_top(context):
    top = context.edition_home.split('id="mom-top-posts"', 1)[1].split("</section>", 1)[0]
    assert re.findall(r"Post \d", text(top)) == ["Post 8", "Post 7"], text(top)


@given("a language home with two articles, the older one ranked first")
def step_two_articles(context):
    newer, older = stub_entry("agents", "Nuevo peor valorado", "/es/articulos/nuevo/"), stub_entry("agents", "Viejo mejor valorado", "/es/articulos/viejo/")
    newer.date, older.date = "2026-11-14", "2026-11-09"
    context.edition_home = hooks._edition_home(ranked_page([newer, older], {"Viejo mejor valorado": 0, "Nuevo peor valorado": 1}))


@then('the home lead article of the stub home is "{title}"')
def step_stub_lead(context, title):
    lead = re.search(r'<div class="mom-home-lead">(.*?)</div>', context.edition_home, re.S).group(1)
    assert text(re.search(r'<span class="mom-story-card-headline">(.*?)</span>', lead).group(1)) == title, lead


@then('the home has loop bands and the first reads "Machines on Machines" in English')
def step_bands(context):
    bands = re.findall(r'<div class="mom-band [^"]*"[^>]*>(.*?)</div>(?=</div>|<)', context.language_page, re.S)
    assert len(bands) >= 3, len(bands)
    words = re.findall(r'<span class="mom-band-(?:word|on)" lang="en">([^<]*)</span>', bands[0])
    assert words[:4] == ["Machines", "on", "Machines", "on"], words


@then('a band reads "{information}" and "{about}"')
def step_info_band(context, information, about):
    assert re.search(rf'<span class="mom-band-word">{information}</span><span class="mom-band-on">{about}</span>', context.language_page)


@then("the bands move only when motion is allowed and never carry meaning by colour alone")
def step_motion(context):
    assert "prefers-reduced-motion: reduce) { .mom-band-row { transform: none" in (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css").read_text(encoding="utf-8")
    assert 'class="mom-band-row" aria-hidden="true"' in context.language_page


@then('the title ends with "{name}" and og:site_name is "{name2}"')
def step_title(context, name, name2):
    assert re.search(rf"<title>[^<]*{re.escape(name)}</title>", context.language_page), re.search(r"<title>[^<]*", context.language_page)
    assert f'<meta property="og:site_name" content="{name2}">' in context.language_page
