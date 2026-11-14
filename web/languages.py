"""MoM's own side of the site's languages: the interface strings the language banner and the chrome the engine writes need, and how links in a translated page are marked.

Papyrus provides everything about which languages a page exists in (docs/multilingual-serving.md in the Papyrus repository): `page.language`, `page.strings`,
`page.primary_language`, `page.alternates`, `page.link_map` and `page.link_in_language(path)`, and it writes `<html lang>`, `hreflang`, `x-default`, the canonical
address, `og:locale` and JSON-LD `inLanguage` itself. The site keeps its interface strings in `web/strings/<tag>.json`, one flat object of `key: text` per language,
which Papyrus checks before a language can be public. This module keeps only what is the site's: the words the banner script needs for every language a page exists in
(the engine hands a page only its own language's strings), the chrome the engine writes (skip link, share labels, cookie banner, bylines, dates), and the rule that a
link in a translated page to a page with no localization is marked.

The rule from the multilingual plan ("Missing localizations (no fallbacks)"): a language that has no page for this page is not in `alternates`. The switcher never
offers another page as if it were a translation.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from html import escape
from pathlib import Path
from urllib.parse import quote, unquote

STRINGS_DIRECTORY = Path(__file__).with_name("strings")
PRIMARY_LANGUAGE = "en"

# The words the banner script shows (the keys are in every language's file). `{seconds}` is filled in by the script.
BANNER_KEYS = ("switcherLabel", "noticed", "countdown", "switchNow", "stay", "pause", "resume", "paused", "announce", "switched", "undo", "readInThisLanguage", "dismiss")


@lru_cache(maxsize=4)
def _read_strings(directory: str, modified: tuple) -> dict:
    return {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in sorted(Path(directory).glob("*.json"))}


def interface_strings(directory: Path = STRINGS_DIRECTORY) -> dict[str, dict[str, str]]:
    """`{tag: {key: text}}` from `strings/<tag>.json`, the files Papyrus reads for `page.strings`. The site reads them itself only where a page needs the words of a
    language other than its own: the banner of a page that exists in several languages."""
    directory = Path(directory)
    stamp = tuple(path.stat().st_mtime_ns for path in sorted(directory.glob("*.json"))) if directory.is_dir() else ()
    return _read_strings(str(directory), stamp) if stamp else {}


def month_names(strings: dict) -> list[str]:
    """The twelve month names of a language's strings (`month.1` to `month.12`)."""
    return [strings[f"month.{number}"] for number in range(1, 13)]


def normalize_path(path: str) -> str:
    """A path as a key to compare by: slashes normalised and any percent-encoding undone, so `/zh/x/%E4%B8%AD/` and `/zh/x/中/` are the same page."""
    plain = unquote(path)
    return "/" + plain.strip("/") + "/" if plain.strip("/") else "/"


def encoded_path(path: str) -> str:
    """A path as Papyrus writes an address (and keys its link map): percent-encoded UTF-8 (`/zh/x/%E4%B8%AD/`)."""
    return quote(normalize_path(path), safe="/")


def strings_for(alternates) -> dict[str, dict[str, str]]:
    """The banner's words in every language the page is offered in: all the browser script needs, so it makes no request."""
    found = interface_strings()
    return {alternate["tag"]: {key: found[alternate["tag"]][key] for key in BANNER_KEYS} for alternate in alternates}


# ---------------------------------------------------------------------------------------------------- links inside a translated page

PAGE_LINK = re.compile(r'<a\b([^>]*?)(?<![\w-])href="([^"]*)"([^>]*)>(.*?)</a>', re.S)
BLOCK_CONTENT = re.compile(r"<(?:h[1-6]|div|p|ul|ol|figure|img|picture|svg)\b", re.I)
ORIGINAL_LINK_SCHEME = "original:"  # `[text](original:/findings/)` links to the page in the primary language, whatever localizations it has
NOT_A_PAGE = re.compile(r"\.[A-Za-z0-9]{2,5}$")


def localized_link_target(path: str, link_in_language) -> tuple[str, bool]:
    """Where a link found in a translated page goes: `(path, leaves_the_language)`. `link_in_language` is the page's own (`page.link_in_language`), which answers from the
    published language groups: a page that has a localization in the page's language is linked at it; a page that has none keeps its address and `leaves_the_language` is True,
    so the link is marked and the reader is never switched to another language without being told. Paths that are not pages (feeds, files, assets) are left alone."""
    if NOT_A_PAGE.search(path) or normalize_path(path).startswith("/assets/"):
        return path, False
    here = encoded_path(path)
    target, leaves = link_in_language(here)
    if leaves:
        return path, True
    return (path, False) if target == here else (target, False)


def localize_links(html: str, language: str, primary: str, link_in_language, strings: dict, origin: str = "", icon: str = "") -> str:
    """Keep a reader inside `language` (not the primary): every internal link in the page goes through `localized_link_target`. A link in the page's own words (inside
    `<main>`) that has no localization still goes to the page that exists, and says so without words in the text: it carries `lang` and `hreflang` of the destination and
    a small Languages icon after its text, with the language's name for a screen reader only ("en inglés"). Navigation, menu and footer links are never marked: the engine
    keeps only destinations that exist in the language, and the site drops the others. It is the only place the site rewrites links."""
    origin = origin.rstrip("/")
    body = [found.span() for found in re.finditer(r"<main\b.*?</main>", html, re.S)]
    # The line that says a page is a translation already names the language of its link ("original en inglés"); it is Papyrus's and is not marked again.
    notices = [found.span() for found in re.finditer(r'<p class="markus-translation">.*?</p>', html, re.S)]

    def rewrite(match: re.Match) -> str:
        before, href, after, inner = match.groups()
        if any(start <= match.start() < end for start, end in notices):
            return match.group(0)
        bare = href[len(origin):] if origin and href.startswith(origin + "/") else href
        explicit_original = bare.startswith(ORIGINAL_LINK_SCHEME)
        bare = bare[len(ORIGINAL_LINK_SCHEME):] if explicit_original else bare
        if "data-language=" in before + after or not bare.startswith("/") or bare.startswith("//"):  # the switcher's own options name their language
            return match.group(0)
        path, suffix = re.match(r"([^?#]*)(.*)", bare).groups()
        target, leaves = localized_link_target(path, link_in_language)
        if explicit_original or f'hreflang="{primary}"' in before + after:  # a link that says its destination is the original is not rewritten
            target, leaves = path, True
        attributes = f'{before}href="{escape(target, quote=True)}{suffix}"{after}'
        if not leaves:
            return f"<a{attributes}>{inner}</a>" if target != path else match.group(0)
        if not any(start <= match.start() < end for start, end in body):
            return match.group(0)
        for name in ("lang", "hreflang"):
            if f" {name}=" not in attributes:
                attributes += f' {name}="{escape(primary, quote=True)}"'
        marked = "" if BLOCK_CONTENT.search(inner) or not re.sub(r"<[^>]+>", "", inner).strip() else (
            f'<span class="mom-link-language">{icon}<span class="mom-visually-hidden" lang="{escape(language, quote=True)}"> {escape(strings["inPrimaryLanguageName"])}</span></span>')
        return f"<a{attributes}>{inner}{marked}</a>"

    return PAGE_LINK.sub(rewrite, html)


# ---------------------------------------------------------------------------------------------------- the chrome the engine writes

CHROME_KEYS = (
    "home.label", "site.tagline", "skipToMain", "ariaSite", "ariaSiteMenu", "ariaMenu", "ariaSiteAndSection", "ariaBreadcrumb", "ariaFooter", "ariaCookieConsent",
    "advertisement", "viewAsMarkdown", "share", "postOnX", "postOnReddit", "shareWebPage", "shareMarkdown",
    "cookieTitle", "cookieText", "privacyPolicy", "rejectAll", "acceptAll", "updated", "emptyListing", "leadArticles", "leadPosts",
)
SKIPPED_ELEMENTS = re.compile(r"(<(script|style|pre|code)\b.*?</\2>)", re.S | re.I)
TEXT_NODE = re.compile(r">([^<>]+)<")
LABEL_ATTRIBUTE = re.compile(r'\b(aria-label|title|alt)="([^"]*)"')


def localized_date(day: int, month: int, year: int, strings: dict) -> str:
    """A date in the language's own month names and order (`13 November 2026` / `13 de noviembre de 2026` / `2026年11月13日`)."""
    return strings["dateFormat"].format(day=day, month=month_names(strings)[month - 1], year=year)


def translate_chrome(html: str, target: dict, source: dict | None = None) -> str:
    """Put the chrome the engine writes (skip link, breadcrumb, share and Markdown labels, the cookie banner, bylines, dates) into the page's language. The reference language's
    text is the exact English the engine writes, so a text node or a label that is exactly one of those strings is replaced by the language's, and nothing else is touched:
    the page's own words are never matched. Scripts, styles and code are skipped."""
    source = source or interface_strings()[PRIMARY_LANGUAGE]
    words = {source[key]: target[key] for key in CHROME_KEYS}
    source_months = month_names(source)
    months = "|".join(source_months)
    dated = re.compile(rf"\b(\d{{1,2}}) ({months}) (\d{{4}})\b")
    by_line = re.compile(rf"^{re.escape(source['by'])} (.+?)( · .*)?$")

    def date(found: re.Match) -> str:
        return localized_date(int(found.group(1)), source_months.index(found.group(2)) + 1, int(found.group(3)), target)

    def text(found: re.Match) -> str:
        original = found.group(1)
        trimmed = original.strip()
        if trimmed in words:
            return original.replace(trimmed, words[trimmed], 1).join((">", "<"))
        line = by_line.match(trimmed)
        if line:
            authors = line.group(1).replace(source["variousBots"], target["variousBots"]).replace(source["and"], target["and"])
            joiner = "" if target["by"].endswith(("：", ":")) else " "
            trimmed = f"{target['by']}{joiner}{authors}{line.group(2) or ''}"
        return original.replace(original.strip(), dated.sub(date, trimmed), 1).join((">", "<"))

    def label(found: re.Match) -> str:
        return f'{found.group(1)}="{words.get(found.group(2), found.group(2))}"'

    pieces = SKIPPED_ELEMENTS.split(html)
    out = []
    index = 0
    while index < len(pieces):
        if index % 3 == 0:
            out.append(LABEL_ATTRIBUTE.sub(label, TEXT_NODE.sub(text, pieces[index])))
        elif index % 3 == 1:
            out.append(pieces[index])
        index += 1
    return "".join(out)
