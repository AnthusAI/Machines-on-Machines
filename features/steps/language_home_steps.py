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
    strings = dict(SPANISH)
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
