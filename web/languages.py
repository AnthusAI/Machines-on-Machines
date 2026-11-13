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

# Each language is named in its own language and script, never by a flag. The Chinese name drops "(简体)" while Simplified is the only Chinese edition.
NATIVE_NAMES = {"en": "English", "es": "Español", "zh-Hans": "中文"}

# The words of the language switcher and the welcoming banner, written in each language, so a visitor reads them in their own language whatever the page's.
# `{seconds}` and `{language}` are filled in by the script. Wording of the banner is the plan's (hard problem 4); review by a speaker of each language is open.
INTERFACE_STRINGS = {
    "en": {
        "switcherLabel": "Language", "noticed": "We noticed you prefer English.", "countdown": "Switching to the English version in {seconds} seconds…",
        "switchNow": "Switch now", "stay": "Stay here", "pause": "Pause", "resume": "Resume", "paused": "Paused.",
        "announce": "English version available; switching in {seconds} seconds; press Pause to stop.",
        "switched": "Switched to English", "undo": "Undo", "readInThisLanguage": "Read in English", "dismiss": "Close", "inPrimaryLanguage": "(in English)",
    },
    "es": {
        "switcherLabel": "Idioma", "noticed": "Vemos que prefieres el español.", "countdown": "Cambiando a la versión en español en {seconds} segundos…",
        "switchNow": "Cambiar ahora", "stay": "Quedarme aquí", "pause": "Pausar", "resume": "Continuar", "paused": "En pausa.",
        "announce": "Hay una versión en español; cambiando en {seconds} segundos; pulsa Pausar para detenerlo.",
        "switched": "Cambiado a español", "undo": "Deshacer", "readInThisLanguage": "Leer en español", "dismiss": "Cerrar", "inPrimaryLanguage": "(en inglés)",
    },
    "zh-Hans": {
        "switcherLabel": "语言", "noticed": "我们注意到您偏好中文。", "countdown": "{seconds} 秒后切换到中文版…",
        "switchNow": "立即切换", "stay": "留在此页", "pause": "暂停", "resume": "继续", "paused": "已暂停。",
        "announce": "有中文版；{seconds} 秒后切换；按“暂停”可停止。",
        "switched": "已切换到中文", "undo": "撤销", "readInThisLanguage": "阅读中文版", "dismiss": "关闭", "inPrimaryLanguage": "（英文）",
    },
}


@lru_cache(maxsize=4)
def _read_config(path: str, modified: int) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _config(path: Path) -> dict:
    path = Path(path)
    return _read_config(str(path), path.stat().st_mtime_ns) if path.exists() else {}


def language_groups(path: Path = LANGUAGE_GROUPS_PATH) -> list[dict[str, str]]:
    """Every language group: `{language tag: site path of that page}`, in the order the languages are offered."""
    return [dict(group) for group in _config(path).get("groups", [])]


def language_prefixes(path: Path = LANGUAGE_GROUPS_PATH) -> dict[str, str]:
    """The URL prefix of each non-primary language, `{language tag: prefix}` (`{"es": "es", "zh-Hans": "zh"}`). The prefix is configured apart from the BCP 47 tag
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

MAX_TRANSLATED_SLUG_LENGTH = 56  # a Latin-script slug stays readable at about eight words
MAX_ENCODED_SLUG_LENGTH = 120  # the longest a slug may be once percent-encoded, which is what a copied address, an email or a chat message carries
TRAILING_FILLER = {"y", "de", "la", "el", "a", "en", "que", "un", "una", "los", "las", "o", "del", "al", "casi", "su", "sus", "uno", "para", "por", "con", "se", "es"}


class NoSlugError(ValueError):
    """A title that yields no slug (nothing but punctuation, say). Said out loud: a guessed slug would be a published address nobody chose."""


def draft_slug(title: str, policy: str, primary_slug: str = "") -> str:
    """The slug a localization drafts at first publish, by the language's policy; fixed afterwards by the slug lock.

    `characters` keeps the title's letters, numbers and marks (Han characters included), turns spaces into hyphens, drops punctuation and full-width marks, and stops at the
    last whole character that keeps the percent-encoded slug within MAX_ENCODED_SLUG_LENGTH. `translated` folds the title to plain ASCII words and trims a trailing filler
    word. `primary` reuses the primary language's slug."""
    if policy == "primary":
        slug = primary_slug
    elif policy in ("characters", "translated"):
        folded = unicodedata.normalize("NFKC", title).lower()
        if policy == "translated":
            folded = unicodedata.normalize("NFKD", folded).encode("ascii", "ignore").decode()
        kept = "".join(character for character in folded if unicodedata.category(character)[0] in "LNM" or character.isspace() or character in "-_")
        limit = MAX_ENCODED_SLUG_LENGTH if policy == "characters" else MAX_TRANSLATED_SLUG_LENGTH
        slug = ""
        for word in (word for word in re.split(r"[\s_\-]+", kept) if word):
            joined = f"{slug}-{word}" if slug else word
            if len(quote(joined, safe="")) <= limit:
                slug = joined
                continue
            if policy == "characters":  # a Chinese title has few spaces: stop at the last whole character that fits
                taken = f"{slug}-" if slug else ""
                for character in word:
                    if len(quote(taken + character, safe="")) > limit:
                        break
                    taken += character
                slug = taken.rstrip("-")
            break
        if policy == "translated":
            parts = slug.split("-")
            while len(parts) > 3 and parts[-1] in TRAILING_FILLER:
                parts.pop()
            slug = "-".join(parts)
    else:
        raise NoSlugError(f"unknown slug policy {policy!r}")
    if not slug.strip("-"):
        raise NoSlugError(f"no slug can be drafted from {title!r} with the {policy!r} policy")
    return slug.strip("-")


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


def strings_for(alternates: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """The interface strings of every language the page is offered in: all the browser script needs, so it makes no request."""
    return {alternate["tag"]: INTERFACE_STRINGS[alternate["tag"]] for alternate in alternates}


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


def localize_links(html: str, language: str, primary: str, groups: list[dict[str, str]], prefixes: dict[str, str], strings: dict[str, str], origin: str = "") -> str:
    """Keep a reader inside `language` (not the primary): every internal link in the page goes through `localized_link_target`, and a link that must leave the language
    carries `hreflang` and a small visible marker in the page's language ("(en inglés)"). It is the only place the site rewrites links."""
    links, marker = link_map(groups), strings["inPrimaryLanguage"]
    origin = origin.rstrip("/")

    def rewrite(match: re.Match) -> str:
        before, href, after, inner = match.groups()
        bare = href[len(origin):] if origin and href.startswith(origin + "/") else href
        if "data-language=" in before + after or not bare.startswith("/") or bare.startswith("//"):  # the switcher's own options name their language
            return match.group(0)
        path, suffix = re.match(r"([^?#]*)(.*)", bare).groups()
        target, leaves = localized_link_target(path, language, links, prefixes)
        attributes = f'{before}href="{escape(target, quote=True)}{suffix}"{after}'
        if not leaves:
            return f"<a{attributes}>{inner}</a>" if target != path else match.group(0)
        if "hreflang=" not in attributes:
            attributes += f' hreflang="{escape(primary, quote=True)}"'
        marked = "" if BLOCK_CONTENT.search(inner) or not re.sub(r"<[^>]+>", "", inner).strip() else f' <span class="mom-link-language">{escape(marker)}</span>'
        return f"<a{attributes}>{inner}{marked}</a>"

    return PAGE_LINK.sub(rewrite, html)
