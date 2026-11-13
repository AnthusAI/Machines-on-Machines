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
from functools import lru_cache
from html import escape
from pathlib import Path

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
        "switched": "Switched to English", "undo": "Undo", "readInThisLanguage": "Read in English", "dismiss": "Close",
    },
    "es": {
        "switcherLabel": "Idioma", "noticed": "Vemos que prefieres el español.", "countdown": "Cambiando a la versión en español en {seconds} segundos…",
        "switchNow": "Cambiar ahora", "stay": "Quedarme aquí", "pause": "Pausar", "resume": "Continuar", "paused": "En pausa.",
        "announce": "Hay una versión en español; cambiando en {seconds} segundos; pulsa Pausar para detenerlo.",
        "switched": "Cambiado a español", "undo": "Deshacer", "readInThisLanguage": "Leer en español", "dismiss": "Cerrar",
    },
    "zh-Hans": {
        "switcherLabel": "语言", "noticed": "我们注意到您偏好中文。", "countdown": "{seconds} 秒后切换到中文版…",
        "switchNow": "立即切换", "stay": "留在此页", "pause": "暂停", "resume": "继续", "paused": "已暂停。",
        "announce": "有中文版；{seconds} 秒后切换；按“暂停”可停止。",
        "switched": "已切换到中文", "undo": "撤销", "readInThisLanguage": "阅读中文版", "dismiss": "关闭",
    },
}


@lru_cache(maxsize=4)
def _read_groups(path: str, modified: int) -> tuple:
    found = json.loads(Path(path).read_text(encoding="utf-8"))
    return tuple(tuple(group.items()) for group in found["groups"])


def language_groups(path: Path = LANGUAGE_GROUPS_PATH) -> list[dict[str, str]]:
    """Every language group: `{language tag: site path of that page}`, in the order the languages are offered."""
    path = Path(path)
    if not path.exists():
        return []
    return [dict(group) for group in _read_groups(str(path), path.stat().st_mtime_ns)]


def normalize_path(path: str) -> str:
    return "/" + path.strip("/") + "/" if path.strip("/") else "/"


def alternates_for_page(page_path: str, groups: list[dict[str, str]], names: dict[str, str] = NATIVE_NAMES) -> list[dict[str, str]]:
    """The page's language group as `[{tag, name, url}]`, the page itself included; `[]` when the page belongs to no group (one language only)."""
    here = normalize_path(page_path)
    for group in groups:
        if any(normalize_path(url) == here for url in group.values()):
            return [{"tag": tag, "name": names.get(tag, tag), "url": normalize_path(url)} for tag, url in group.items()]
    return []


def language_of_page(page_path: str, alternates: list[dict[str, str]], primary: str) -> str:
    """The tag of the language this page is in: its own entry in the group, or the site's primary language when it has no group."""
    here = normalize_path(page_path)
    return next((alternate["tag"] for alternate in alternates if alternate["url"] == here), primary)


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
