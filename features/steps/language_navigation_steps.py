"""Steps for features/language-navigation.feature: the bar, the menu and the footer of the language case's editions against the English home."""

import html
import re
from urllib.parse import quote, unquote

from behave import then

from language_cases import SEGMENTS  # noqa: E402
from projection_support import page_text  # noqa: E402

LINK = re.compile(r'<a\b([^>]*?)href="([^"]*)"([^>]*)>(.*?)</a>', re.S)
ENGLISH_ONLY = ("/findings/", "/videos/", "/conversations/")


def region(page, opening, closing="</ul>"):
    return page.split(opening, 1)[1].split(closing, 1)[0]


def bar(page):
    return [(match[1], match[0] + match[2]) for match in LINK.findall(region(page, '<ul class="mom-nav-items">')) if "mom-home-pill" not in match[0] + match[2]]


def menu(page):
    return [match[1] for match in LINK.findall(region(page, '<ul class="mom-menu-list">'))]


def footer(page):
    return [(match[1], match[0] + match[2], re.sub(r"<[^>]+>", "", match[3])) for match in LINK.findall(region(page, '<ul class="mom-footer-links">'))]


def modulo_prefix(target):
    """A navigation target of an edition as the English one: without the prefix and with the first segment in English (`/es/conceptos/` is `/wiki/`)."""
    plain = unquote(re.sub(r"^/(es|zh)/", "/", target))
    inverse = {translated: english for table in SEGMENTS.values() for english, translated in table.items()}
    first, slash, rest = plain.lstrip("/").partition("/")
    english = inverse.get(first, first)
    return "/" + ("wiki" if english == "concepts" else english) + slash + rest


def in_language(prefix, original):
    """The address of an English navigation target under the language's prefix, with its first segment in the language."""
    tag = "es-419" if prefix.strip("/") == "es" else "zh-Hans"
    first, slash, rest = original.lstrip("/").partition("/")
    first = "concepts" if first == "wiki" else first
    return quote(prefix.rstrip("/") + "/" + SEGMENTS[tag].get(first, first) + slash + rest)


@then("the navigation has the same number of destinations as the English home and in the same order")
def step_same_navigation(context):
    english = bar(page_text(context.language_directory, "/"))
    found = bar(context.language_page)
    assert len(found) == len(english) == 6, (found, english)
    assert [modulo_prefix(target) for target, _ in found] == [target for target, _ in english], found


@then('each navigation target is the English target or the same address under "{prefix}"')
def step_targets(context, prefix):
    english = [target for target, _ in bar(page_text(context.language_directory, "/"))]
    for (target, _), original in zip(bar(context.language_page), english):
        assert target in (original, in_language(prefix, original)), (target, original)


@then('the English-only navigation entries "{paths}" go to the English page marked lang "en" and hreflang "en"')
def step_english_only(context, paths):
    found = dict(bar(context.language_page))
    for path in paths.split(", "):
        assert path in found and 'lang="en" hreflang="en"' in found[path], (path, found)
        assert 'data-icon="languages"' in region(context.language_page, '<ul class="mom-nav-items">').split(f'href="{path}"', 1)[1].split("</a>", 1)[0]


@then('the Concepts entry goes to "{target}"')
def step_concepts(context, target):
    assert bar(context.language_page)[-1][0] == target, bar(context.language_page)


@then("the menu lists the same targets as the bar and every destination has a line")
def step_menu(context):
    targets = menu(context.language_page)
    home = context.language_route
    assert targets[0] == home and targets[1:] == [target for target, _ in bar(context.language_page)], targets
    items = re.findall(r"<li><a class=\"mom-menu-link\".*?</a></li>", region(context.language_page, '<ul class="mom-menu-list">', "</ul><section"), re.S) or \
        re.findall(r"<li><a class=\"mom-menu-link\".*?</a></li>", region(context.language_page, '<ul class="mom-menu-list">'), re.S)
    assert items and all("mom-menu-sub" in item for item in items), items


@then('the footer has the same number of links as the English footer and "{labels}" first')
def step_footer(context, labels):
    english = footer(page_text(context.language_directory, "/"))
    found = footer(context.language_page)
    assert len(found) == len(english) == 8, (found, english)
    for (_, _, text), label in zip(found[:4], labels.split(", ")):
        assert html.unescape(text).strip().startswith(label), (text, label)
    assert [modulo_prefix(target) for target, _, _ in found] == [modulo_prefix(target) for target, _, _ in english]


@then('the footer\'s English-only links are marked lang "en"')
def step_footer_marked(context):
    for target, attributes, _ in footer(context.language_page):
        if target in ENGLISH_ONLY + ("/about/", "/corrections/", "/llms.txt"):
            assert 'lang="en"' in attributes, (target, attributes)
