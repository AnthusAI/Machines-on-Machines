"""The pages a translated site has beside its articles, for the preview and the tests.

Papyrus will generate a language's home, listings and section lists from the localizations it publishes. Until it does, this module builds them from the language's
interface strings (web/interface-strings.json) and the stories that exist in it, and says which pages are the same page in each language (the language groups). A
language lists only what exists in it. A listing with nothing in the language says so, in the language, with the navigation intact; a page whose content is not
translated in the MVP (Findings, Videos, Conversations, Concepts, About, Corrections) says that, in the language, and offers the original through a link that names
its language. Nothing here redirects to English and nothing is faked.
"""

from __future__ import annotations

from html import escape

SITE_NAME = "Machines on Machines"
# (path under the prefix, key of its title, key of its lead, key of the sentence when it has nothing, kind): `stories` pages list the translated articles
LISTING_PAGES = (
    ("articles", "navArticles", "leadArticles", "emptyArticles", "stories"),
    ("posts", "navPosts", "leadPosts", "emptyPosts", "stories"),
    ("findings", "navFindings", "leadFindings", "notTranslatedFindings", "original"),
    ("videos", "navVideos", "leadVideos", "notTranslatedVideos", "original"),
    ("conversations", "navConversations", "leadConversations", "notTranslatedConversations", "original"),
    ("wiki", "navConcepts", "leadConcepts", "notTranslatedConcepts", "original"),
    ("about", "footerAbout", None, "notTranslatedPage", "original"),
    ("corrections", "footerCorrections", None, "notTranslatedPage", "original"),
)
SECTION_FOLDER = "field-notes"  # the fixture site's article section


def _quote(text: str) -> str:
    return escape(text, quote=True).replace('"', "&quot;")


def _page(identifier: str, path: str, title: str, lead: str, body: str) -> dict:
    return {"id": identifier, "path": path, "title": title, "description": lead or title, "source": f"pages/{identifier}.md",
            "text": f'::band{{size="bare"}}\n\n::include{{kind="block" name="page-top" title="{_quote(title)}" lead="{_quote(lead)}"}}\n\n{body}\n'}


def listing_pages(tag: str, prefix: str, strings: dict, stories: list[tuple[str, str]]) -> list[dict]:
    """Every page of the language that the navigation and the footer lead to, and the language's home. `stories` is `[(title, path)]`, what is translated into the language."""
    pages = []
    for slug, title_key, lead_key, sentence_key, kind in LISTING_PAGES:
        if kind == "stories" and slug == "articles" and stories:
            body = f"## {strings['translatedArticlesHeading']}\n\n" + "".join(f"- [{title}]({path})\n" for title, path in stories)
        elif kind == "original":
            body = f'{strings[sentence_key]}\n\n[{strings["readOriginal"]}](original:/{slug}/)'
        else:
            body = strings[sentence_key]
        pages.append(_page(f"{slug}-{prefix}", f"{prefix}/{slug}", strings[title_key], strings[lead_key] if lead_key else "", body))
    home_body = (f"## {strings['translatedArticlesHeading']}\n\n" + "".join(f"- [{title}]({path})\n" for title, path in stories)) if stories else strings["emptyArticles"]
    pages.append(_page(f"home-{prefix}", prefix, SITE_NAME, strings["tagline"], home_body))
    return pages


def article_section(prefix: str, strings: dict) -> dict:
    """The language's article section: its pages live under `/<prefix>/field-notes/` and its title is the section's title in the language."""
    return {f"{prefix}-{SECTION_FOLDER}": {"base": f"{prefix}/{SECTION_FOLDER}", "label": strings["sections"][SECTION_FOLDER], "description": strings["leadArticles"]}}


def listing_groups(prefixes: dict[str, str], primary: str = "en") -> list[dict[str, str]]:
    """The groups that say a listing, the home and the section list are the same page in each language."""
    groups = [{primary: f"/{slug}/", **{tag: f"/{prefix}/{slug}/" for tag, prefix in prefixes.items()}} for slug, *_ in LISTING_PAGES]
    groups.append({primary: f"/{SECTION_FOLDER}/", **{tag: f"/{prefix}/{SECTION_FOLDER}/" for tag, prefix in prefixes.items()}})
    groups.append({primary: "/", **{tag: f"/{prefix}/" for tag, prefix in prefixes.items()}})
    return groups
