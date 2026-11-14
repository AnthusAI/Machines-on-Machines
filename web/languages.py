"""The languages a page is offered in, and the words the language switcher and its welcoming banner use.

A language group is the same page in each language it exists in. Papyrus will provide it (the localizations of one Story, or of a listing or the home
page) as an `alternates` list of `{tag, name, url}`; until it does, `language_groups()` reads `language-groups.json` beside this file and
`alternates_for_page()` turns the group that holds a page into that list. Everything that draws a switcher, a banner, `hreflang` links or `<html lang>`
reads the list this module returns, so the real data source replaces `language_groups()` and nothing else changes.

The rule from the multilingual plan ("Missing localizations (no fallbacks)"): a language that has no page for this page is not in the list. The switcher
never offers another page as if it were a translation.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from html import escape
from pathlib import Path
from urllib.parse import quote, unquote

LANGUAGE_GROUPS_PATH = Path(__file__).with_name("language-groups.json")

INTERFACE_STRINGS_PATH = Path(__file__).with_name("interface-strings.json")
PRIMARY_LANGUAGE = "en"

# The words of the site's chrome in each language (navigation, menu, footer, page furniture, the language switcher and its welcoming banner, the words of a listing that has
# nothing in the language, month names and each section's title), keyed by language tag in `interface-strings.json`. The primary language's entry is the reference: it holds
# every key, and its text is exactly what the site and the engine write in that language, which is how the chrome the engine writes is found and translated. The wording of
# the other languages was drafted by a machine and has not been reviewed by a speaker of the language. `{seconds}` is filled in by the script.
BANNER_KEYS = ("switcherLabel", "noticed", "countdown", "switchNow", "stay", "pause", "resume", "paused", "announce", "switched", "undo", "readInThisLanguage", "dismiss")


@lru_cache(maxsize=4)
def _read_strings(path: str, modified: int) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def interface_strings(path: Path = INTERFACE_STRINGS_PATH) -> dict[str, dict]:
    path = Path(path)
    return _read_strings(str(path), path.stat().st_mtime_ns) if path.exists() else {}


def missing_strings(strings: dict, reference: dict) -> list[str]:
    """The keys of `reference` that `strings` lacks or leaves empty (a section title, a month, a nested key is named `sections.history`, `months.3`)."""
    missing = []
    for key, expected in reference.items():
        found = strings.get(key)
        if isinstance(expected, dict):
            missing += [f"{key}.{inner}" for inner in missing_strings(found if isinstance(found, dict) else {}, expected)]
        elif isinstance(expected, list):
            missing += [f"{key}.{index}" for index in range(len(expected)) if not isinstance(found, list) or index >= len(found) or not found[index]]
        elif not found:
            missing.append(key)
    return missing


def complete_languages(strings: dict[str, dict] | None = None, primary: str = PRIMARY_LANGUAGE) -> list[str]:
    """The languages whose interface strings are complete: every key of the primary language's entry exists. Only these are public (the plan: a language becomes
    public only when its interface strings are complete), so only these are offered by the switcher, named in `hreflang` or linked."""
    strings = interface_strings() if strings is None else strings
    reference = strings.get(primary, {})
    return [tag for tag, found in strings.items() if tag == primary or not missing_strings(found, reference)]


INTERFACE_STRINGS = interface_strings()
NATIVE_NAMES = {tag: found["name"] for tag, found in INTERFACE_STRINGS.items()}  # each language is named in its own language and script, never by a flag


@lru_cache(maxsize=4)
def _read_config(path: str, modified: int) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _config(path: Path) -> dict:
    path = Path(path)
    return _read_config(str(path), path.stat().st_mtime_ns) if path.exists() else {}


def language_groups(path: Path = LANGUAGE_GROUPS_PATH, strings: dict[str, dict] | None = None) -> list[dict[str, str]]:
    """Every language group: `{language tag: site path of that page}`, in the order the languages are offered. A language whose interface strings are not complete
    is not in any group, so nothing offers it."""
    public = set(complete_languages(strings))
    return [{tag: url for tag, url in group.items() if tag in public} for group in _config(path).get("groups", [])]


def language_prefixes(path: Path = LANGUAGE_GROUPS_PATH) -> dict[str, str]:
    """The URL prefix of each non-primary language, `{language tag: prefix}` (`{"es-419": "es", "zh-Hans": "zh"}`). The prefix is configured apart from the BCP 47 tag
    because paths use the prefix while `<html lang>` and `hreflang` use the tag; the primary language has none (its URLs are the site's existing ones)."""
    return dict(_config(path).get("prefixes", {}))


def slug_policies(path: Path = LANGUAGE_GROUPS_PATH) -> dict[str, str]:
    """How each non-primary language drafts the slug of a page, `{language tag: policy}` (`draft_slug`): `translated` (a Latin-script language drafts its own from its
    title), `characters` (the title's own characters, for Chinese), or `primary` (reuse the primary language's slug). A setting, so no language is special-cased in code."""
    return dict(_config(path).get("slugPolicies", {}))


def normalize_path(path: str) -> str:
    """A path as a key to compare by: slashes normalised and any percent-encoding undone, so `/zh/x/%E4%B8%AD/` and `/zh/x/中/` are the same page."""
    plain = unquote(path)
    return "/" + plain.strip("/") + "/" if plain.strip("/") else "/"


def encoded_path(path: str) -> str:
    """A path as it is written in a link, a `canonical`, an `hreflang`, a sitemap and the address bar when it is copied: percent-encoded UTF-8 (`/zh/x/%E4%B8%AD/`)."""
    return quote(normalize_path(path), safe="/")


# ---------------------------------------------------------------------------------------------------- slugs

# A slug is a directory name (`<slug>/index.html`) on the filesystems the build writes to, and a directory name is at most 255 BYTES in UTF-8 (ext4, APFS, NTFS, and
# the S3 key it becomes is limited to 1024 bytes). A Han character is 3 bytes in UTF-8, so a Chinese slug holds 85 characters; an ASCII one 255. That is the only limit on a
# slug: it is cut only when it would not fit, at a whole character. Percent-encoded, 255 bytes are at most 765 characters, far under CloudFront's 8192 for a whole URL.
MAX_SLUG_BYTES = 255


class NoSlugError(ValueError):
    """A title that yields no slug (nothing but punctuation, say). Said out loud: a guessed slug would be a published address nobody chose."""


def draft_slug(title: str, policy: str, primary_slug: str = "") -> str:
    """The slug a localization drafts at first publish, by the language's policy; fixed afterwards by the slug lock.

    `characters` keeps the title's letters, numbers and marks (Han characters included), turns spaces into hyphens and drops punctuation and full-width marks. `translated`
    folds the title to plain ASCII words. `primary` reuses the primary language's slug. A slug is cut only at the filesystem's limit (MAX_SLUG_BYTES), at a whole character."""
    if policy == "primary":
        slug = primary_slug
    elif policy in ("characters", "translated"):
        folded = unicodedata.normalize("NFKC", title).lower()
        if policy == "translated":
            folded = unicodedata.normalize("NFKD", folded).encode("ascii", "ignore").decode()
        kept = "".join(character for character in folded if unicodedata.category(character)[0] in "LNM" or character.isspace() or character in "-_")
        slug = "-".join(word for word in re.split(r"[\s_\-]+", kept) if word)
    else:
        raise NoSlugError(f"unknown slug policy {policy!r}")
    if not slug.strip("-"):
        raise NoSlugError(f"no slug can be drafted from {title!r} with the {policy!r} policy")
    return fit_filesystem(slug).strip("-")


def fit_filesystem(slug: str) -> str:
    """The slug, cut at a whole character if its UTF-8 length would pass the filesystem's limit for a directory name."""
    kept = ""
    for character in slug:
        if len((kept + character).encode("utf-8")) > MAX_SLUG_BYTES:
            break
        kept += character
    return kept


def alternates_for_page(page_path: str, groups: list[dict[str, str]], names: dict[str, str] = NATIVE_NAMES) -> list[dict[str, str]]:
    """The page's language group as `[{tag, name, url}]`, the page itself included; `[]` when the page belongs to no group (one language only)."""
    here = normalize_path(page_path)
    for group in groups:
        if any(normalize_path(url) == here for url in group.values()):
            return [{"tag": tag, "name": names.get(tag, tag), "url": encoded_path(url)} for tag, url in group.items()]
    return []


def language_of_page(page_path: str, alternates: list[dict[str, str]], primary: str, prefixes: dict[str, str] | None = None) -> str:
    """The tag of the language this page is in: its own entry in the group, else the language whose URL prefix its path starts with, else the primary language."""
    here = normalize_path(page_path)
    in_group = next((alternate["tag"] for alternate in alternates if normalize_path(alternate["url"]) == here), None)
    return in_group or prefixed_language(here, prefixes or {}) or primary


def prefixed_language(path: str, prefixes: dict[str, str]) -> str | None:
    """The language a path belongs to by its URL prefix (`/es/articles/x/` is `es`), or None for a path in the primary language."""
    return next((tag for tag, prefix in prefixes.items() if normalize_path(path).startswith(f"/{prefix.strip('/')}/")), None)


def unprefixed_path(path: str, prefixes: dict[str, str]) -> str:
    """The same address in the primary language (`/es/articles/` is `/articles/`), to tell which destination of the navigation a page belongs to."""
    tag = prefixed_language(path, prefixes)
    return normalize_path(path)[len(prefixes[tag].strip("/")) + 1:] if tag else path


def primary_path(path: str, groups: list[dict[str, str]], primary: str, prefixes: dict[str, str]) -> str:
    """The same page in the primary language (`/es/concepts/` is `/wiki/`), to tell which destination of the navigation a page belongs to: from the groups when the page
    is in one, else by taking its prefix off."""
    found = link_map(groups).get(normalize_path(path), {})
    return found.get(primary) or unprefixed_path(path, prefixes)


def strings_for(alternates: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """The interface strings of every language the page is offered in: all the browser script needs, so it makes no request."""
    return {alternate["tag"]: {key: INTERFACE_STRINGS[alternate["tag"]][key] for key in BANNER_KEYS} for alternate in alternates}


def hreflang_links(alternates: list[dict[str, str]], primary: str, origin: str) -> str:
    """One `<link rel="alternate" hreflang>` for every language of the group, itself included, and `x-default` (the primary language's page)."""
    def link(tag: str, url: str) -> str:
        return f'<link rel="alternate" hreflang="{escape(tag, quote=True)}" href="{escape(origin.rstrip("/") + url, quote=True)}">'

    links = [link(alternate["tag"], alternate["url"]) for alternate in alternates]
    primary_page = next((alternate for alternate in alternates if alternate["tag"] == primary), None)
    if primary_page is not None:
        links.append(link("x-default", primary_page["url"]))
    return "\n".join(links)


# ---------------------------------------------------------------------------------------------------- links inside a translated page

PAGE_LINK = re.compile(r'<a\b([^>]*?)(?<![\w-])href="([^"]*)"([^>]*)>(.*?)</a>', re.S)
BLOCK_CONTENT = re.compile(r"<(?:h[1-6]|div|p|ul|ol|figure|img|picture|svg)\b", re.I)
ORIGINAL_LINK_SCHEME = "original:"  # `[text](original:/findings/)` links to the page in the primary language, whatever localizations it has
NOT_A_PAGE = re.compile(r"\.[A-Za-z0-9]{2,5}$")


def link_map(groups: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """`{path of a page in any language: {language tag: path of that page in the language}}`. Papyrus will supply this map with the localizations; it is
    built from the same language groups, so the one thing that decides where a link goes is data, and the translator never chooses a link target."""
    return {normalize_path(url): {tag: encoded_path(other) for tag, other in group.items()} for group in groups for url in group.values()}


def localized_link_target(path: str, language: str, links: dict[str, dict[str, str]], prefixes: dict[str, str]) -> tuple[str, bool]:
    """Where a link found in a page in `language` goes: `(path, leaves_the_language)`.

    A page that has a localization in the reader's language is linked at that localization. A page that has none is linked at the page it is (the primary
    language's), and `leaves_the_language` is True so the link is marked: the reader is never switched to another language without being told. Paths that are not
    pages (feeds, files, assets) and paths already under a language prefix are left alone."""
    here = normalize_path(path)
    if NOT_A_PAGE.search(path) or here.startswith("/assets/") or prefixed_language(here, prefixes):
        return path, False
    found = links.get(here, {})
    return (found[language], False) if language in found else (path, True)


def localize_links(html: str, language: str, primary: str, groups: list[dict[str, str]], prefixes: dict[str, str], strings: dict, origin: str = "", icon: str = "") -> str:
    """Keep a reader inside `language` (not the primary): every internal link in the page goes through `localized_link_target`. A link in the page's own words (inside
    `<main>`) that has no localization still goes to the page that exists, and says so without words in the text: it carries `lang` and `hreflang` of the destination and
    a small Languages icon after its text, with the language's name for a screen reader only ("en inglés"). Navigation, menu and footer links are never marked: their
    destinations exist in every public language, so they never leave it. It is the only place the site rewrites links."""
    links = link_map(groups)
    origin = origin.rstrip("/")
    body = [found.span() for found in re.finditer(r"<main\b.*?</main>", html, re.S)]

    def rewrite(match: re.Match) -> str:
        before, href, after, inner = match.groups()
        bare = href[len(origin):] if origin and href.startswith(origin + "/") else href
        explicit_original = bare.startswith(ORIGINAL_LINK_SCHEME)
        bare = bare[len(ORIGINAL_LINK_SCHEME):] if explicit_original else bare
        if "data-language=" in before + after or not bare.startswith("/") or bare.startswith("//"):  # the switcher's own options name their language
            return match.group(0)
        path, suffix = re.match(r"([^?#]*)(.*)", bare).groups()
        target, leaves = localized_link_target(path, language, links, prefixes)
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
    "home", "tagline", "skipToMain", "ariaSite", "ariaSiteMenu", "ariaMenu", "ariaSiteAndSection", "ariaBreadcrumb", "ariaFooter", "ariaCookieConsent",
    "advertisement", "viewAsMarkdown", "share", "postOnX", "postOnReddit", "shareWebPage", "shareMarkdown",
    "cookieTitle", "cookieText", "privacyPolicy", "rejectAll", "acceptAll",
)
SKIPPED_ELEMENTS = re.compile(r"(<(script|style|pre|code)\b.*?</\2>)", re.S | re.I)
TEXT_NODE = re.compile(r">([^<>]+)<")
LABEL_ATTRIBUTE = re.compile(r'\b(aria-label|title|alt)="([^"]*)"')


def localized_date(day: int, month: int, year: int, strings: dict) -> str:
    """A date in the language's own month names and order (`13 November 2026` / `13 de noviembre de 2026` / `2026年11月13日`)."""
    return strings["dateFormat"].format(day=day, month=strings["months"][month - 1], year=year)


def translate_chrome(html: str, target: dict, source: dict | None = None) -> str:
    """Put the chrome the engine writes (skip link, breadcrumb, share and Markdown labels, the cookie banner, bylines, dates) into the page's language. The reference language's
    text is the exact English the engine writes, so a text node or a label that is exactly one of those strings is replaced by the language's, and nothing else is touched:
    the page's own words are never matched. Scripts, styles and code are skipped."""
    source = source or INTERFACE_STRINGS[PRIMARY_LANGUAGE]
    words = {source[key]: target[key] for key in CHROME_KEYS}
    months = "|".join(source["months"])
    dated = re.compile(rf"\b(\d{{1,2}}) ({months}) (\d{{4}})\b")
    by_line = re.compile(rf"^{re.escape(source['by'])} (.+?)( · .*)?$")

    def date(found: re.Match) -> str:
        return localized_date(int(found.group(1)), source["months"].index(found.group(2)) + 1, int(found.group(3)), target)

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
