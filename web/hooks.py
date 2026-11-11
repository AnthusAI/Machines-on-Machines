"""Machines on Machines named hooks for the standard Papyrus front end (projection.json names this module).

The design system lives in `design/system/`; its components are ported to Python in `mom_components.py`, a sibling module
this file imports. This file decides where each component goes: the masthead, the footer, the cards, the section
page, the article page with its spine, the wiki term page, and the blocks the authored pages place.

Bylines are data, never assumed. A story is "By various bots", or "By various bots and <name>" when an editor approved it, and
a story a person wrote names that person. The byline says who made it, so no chip repeats it.
"""

from __future__ import annotations

import json
import re
from datetime import date
from html import escape, unescape
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit, urlunsplit
from typing import NamedTuple

import mom_components as mom

SITE_NAME = "Machines on Machines"
SITE_HOST = "machines-on-machines.anth.us"
TAGLINE = "Information About Information Systems"
WIKI_SECTION = "wiki"
WIKI_TYPE = "wiki_page"
WIKI_SUBJECT = "Meaning"
# The spine always reads "Machines on Machines": on an article page it is the only place the site's name shows
SITE_SPINE_SUBJECT = "Machines"
CONVERSATIONS_PATH = "/conversations/"
FINDINGS_PATH = "/findings/"
FEED_PATH = "/feed.xml"
LLMS_PATH = "/llms.txt"
SCRIPT_PATH = "/assets/mom.js"
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
AGENT_DRAFTERS = ("agent", "ai")
RISING_WINDOW_DAYS = 14
NEW_THIS_WEEK_DAYS = 7
BAND_MINIMUM_WORDS = 16
BAND_KINDS = (
    ("rising", "machine", "Rising fast"),
    ("watching", "human", "Editors are watching"),
    ("new", "brand", "New this week"),
)
DEPENDS_ON = None
ADS_PATH = Path(__file__).with_name("ads.json")
IN_CONTENT_AD_AFTER_PARAGRAPH = {"story": 4, "pullquote": 3, "aside": 2}  # the aside goes early so the words that follow can flow around it
IN_CONTENT_AD_MINIMUM_PARAGRAPHS = 7
SECTION_AD_CARD_POSITION = 5
# The home page's pre-programmed choices (named by the section's address): which topic sections carry a "Worth Watching" card of videos, how many videos it holds,
# which sections carry an advertisement as one more card, how many videos the Videos section shows, and how many concepts end the page.
HOME_WORTH_WATCHING_SECTIONS = ("agents", "music", "history")
HOME_WORTH_WATCHING_VIDEOS = 2
HOME_AD_CARD_SECTIONS = ("science", "art")
HOME_VIDEOS_SHOWN = 6
HOME_CONCEPTS_SHOWN = 12
PARAGRAPH_CONTAINER_TAGS = ("blockquote", "ul", "ol", "figure", "aside", "table", "pre", "details", "dl")

TOKEN_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")
HASHTAG = re.compile(r"(?<![\w&/#])#([A-Za-z][A-Za-z0-9]*)")
HTML_TAG_SPLIT = re.compile(r"(<[^>]*>)")
MARKUS_HEADER = re.compile(r'<header class="markus-header">.*?</header>', re.S)
CITATION_LIST_WITH_ITEMS = '<ol class="citationslist"><li'
BODY_OPENS_WITH_FIGURE = re.compile(r"\s*<article\b[^>]*>\s*(?:<style>.*?</style>\s*)?(?:<p>\s*)?(?:<style>.*?</style>\s*)?<figure\b", re.S)
ARTICLE_QUOTE = re.compile(
    r'(?P<markus_quote><figure\b[^>]*class="markus-pull-quote\b[^"]*"[^>]*>.*?</figure>)'
    r'|<blockquote>\s*<p>(?P<plain_quote>[^<]*)</p>\s*</blockquote>',
    re.S,
)
STOCK_TILE = re.compile(r'<article class="home-page-tile" data-status="([^"]*)"[^>]*>(.*?)</article>', re.S)
STOCK_THREAD = re.compile(r'<article class="home-page-thread" data-anchor="([^"]*)"[^>]*>(.*?)</article>', re.S)
STOCK_SUPERSEDED = re.compile(r'<aside class="papyrus-wiki-superseded".*?</aside>', re.S)
TAG_PATTERN = re.compile(r"<[^>]+>")


# ---------------------------------------------------------------------------------------------- small helpers

def _e(value) -> str:
    return escape("" if value is None else str(value), quote=True)


def _plain(markup: str) -> str:
    return unescape(TAG_PATTERN.sub("", markup)).strip()


def _first(pattern: str, text: str, flags: int = re.S):
    found = re.search(pattern, text, flags)
    return found.group(1) if found else None


def _date_text(value) -> str:
    """`2026-10-30` as `30 Oct 2026`; the value as written when it is not a date."""
    text = str(value or "")[:10]
    try:
        year, month, day = (int(part) for part in text.split("-"))
        date(year, month, day)
    except ValueError:
        return str(value or "")
    return f"{day} {MONTHS[month - 1]} {year}"


def _hashtag_key(text) -> str:
    return TOKEN_NON_ALPHANUMERIC.sub("", str(text or "").lower())


def _section_subject(section, label: str) -> str:
    return section.label if section is not None else label


# The projection knows a section's id but not the name the newsroom gives it.
NEWSROOM_NAV_PATHS = frozenset({FINDINGS_PATH, "/videos/", CONVERSATIONS_PATH, f"/{WIKI_SECTION}/"})
HOME_PURPOSE = "What happens when machines shape the world, and each other? Machines report it, people steer them, and you can watch it all happen."
LISTING_LEADS = {"Posts": "Quick pointers to the latest in information systems."}
TOPIC_LABELS = {"security": "Privacy & Security", "ai-safety": "Safety & Alignment", "science": "Math & Science", "law-policy": "Law & Policy"}
# Words a section name keeps in capitals when it is made from a topic id (history reads "History"; the newsroom's own names live in TOPIC_LABELS).
TOPIC_ACRONYMS = {"ai": "AI"}


def _titled_topic(topic: str) -> str:
    return " ".join(TOPIC_ACRONYMS.get(word, word.title()) for word in topic.split("-"))


def _topic_label(entry) -> str:
    """The Story's section, a topic, and never the type its address is grouped under."""
    if entry.section is not None and not entry.section.is_type:
        return entry.section.label
    return TOPIC_LABELS.get(entry.topic, _titled_topic(entry.topic)) if entry.topic else ""


SECTION_PAGE_PREFIX = "section-"
MORE_ELLIPSIS = "…"


def _section_pages(page) -> dict:
    """The sections that have a page of their own, by every name a section is known by: its id (`security`) and its title (`Privacy & Security`), both
    reduced to letters and digits. Each maps to `(address, title)`. The pages are the `section-*` pages of `projection.json`, which
    `tools/sync_section_pages.py` writes from `web/sections.json`."""
    pages = {}
    for custom in getattr(page.settings, "pages", ()):
        if str(custom.id).startswith(SECTION_PAGE_PREFIX):
            found = (f"/{custom.path}/", custom.title)
            pages[_hashtag_key(custom.path)] = found
            pages[_hashtag_key(custom.title)] = found
    return pages


def _section_resolver(page):
    """`resolve(name)` is the `(address, title)` of the section page a section name points to, or None when that section has no page (no dead link)."""
    pages = _section_pages(page)
    return lambda name: pages.get(_hashtag_key(unescape(str(name or "")))) if name else None


def _count_text(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _linked_title(label_html: str, href: str | None) -> str:
    return f'<a class="mom-section-title-link" href="{_e(href)}">{label_html}</a>' if href else label_html


def _more_link(title: str, href: str | None) -> str:
    """The link at the bottom of a block of more than one item: "More security…". Only a section that has a page gets one."""
    return f'<p class="mom-more"><a class="mom-more-link" href="{_e(href)}">More {_e(title)}{MORE_ELLIPSIS}</a></p>' if href else ""


def _listing_subject(section, label: str) -> str:
    """What a listing's title says it is "Machines on": a type's list is not a topic."""
    return "Machines" if section is not None and section.is_type else _section_subject(section, label)


def _subtitle(entry) -> str:
    """The line under an article's headline. The blurb is a different field, written to lead readers in from index pages."""
    return str(entry.data.get("deck") or entry.data.get("dek") or "")


def _is_wiki(entry) -> bool:
    return entry is not None and entry.type == WIKI_TYPE


def _truthy(value) -> bool:
    return str(value).strip().lower() in ("true", "yes", "1")


def _dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _wiki_terms(site) -> dict:
    """Hashtag key to wiki page path, for every wiki page the site has; built once per version of the site."""
    def build():
        terms = {}
        for summary in site.items:
            if summary.type == WIKI_TYPE:
                title = summary.front_matter.get("title") or summary.title or summary.slug
                terms[_hashtag_key(title)] = f"/{WIKI_SECTION}/{summary.slug}/"
        return terms
    return site.memo("wiki-terms", build)


# ---------------------------------------------------------------------------------------------- provenance

TEAM_AUTHOR_WORDS = re.compile(r"\b(team|staff|editors?|editorial|newsroom)\b", re.IGNORECASE)


def _public_author_names(authors) -> list[str]:
    """Names for the "Written by" chip. A team byline carried over from a legacy site ("Papyrus Editorial Team") is not a person, so it reads as "the editors"; real names pass through."""
    names = []
    for author in authors:
        name = "the editors" if TEAM_AUTHOR_WORDS.search(str(author)) else str(author)
        if name not in names:
            names.append(name)
    return names


MACHINE_AUTHOR_LABELS = ("ai", "bot", "bots", "various bots", "agent", "agents")


def _human_authors(authors) -> list[str]:
    """The authors who are people. A story whose author is just "AI" was written by the bots, so it says "various bots", not "By AI"."""
    return [str(author) for author in authors if str(author).strip().lower() not in MACHINE_AUTHOR_LABELS]


def _names_in_words(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def _byline(entry) -> str:
    """Bots write a story unless it names its human authors only. A story the bots drafted says so, and the people who shaped it join the byline: an editor who approved it and any human named as an author. A post has no byline at all: nobody writes it, so no card, page or Markdown twin of a post names an author."""
    if getattr(entry, "type", None) == "post":
        return ""
    humans = _human_authors(entry.authors or [])
    if humans and str(_dict(entry.data.get("drafting")).get("by", "")).lower() not in AGENT_DRAFTERS:
        return "By " + ", ".join(_public_author_names(humans))
    approval = _dict(entry.data.get("approval"))
    people = []
    if approval.get("status") == "approved":
        people.append(str(approval.get("by") or "an editor"))
    for name in _public_author_names(humans):
        if name not in people:
            people.append(name)
    return "By various bots" + (f" and {_names_in_words(people)}" if people else "")


def byline(entry):
    """The byline text for the Markdown twin and any core byline: the same rule as the page, so a page and its twin never disagree about who made a story."""
    return _byline(entry)


def _provenance(entry) -> list[tuple[str, str]]:
    """The chips of a story, from its front matter only: whether it is an editor's pick. The byline says who made it, and the site as a whole says it is drafted by AI, so no page carries an AI-drafted disclaimer."""
    return [("human", "Editor’s pick")] if _truthy(entry.data.get("editorsPick")) else []


def _wiki_chips(entry) -> list[tuple[str, str]]:
    """A wiki page names the person who reviewed it; it carries no AI-edited or draft disclaimer."""
    review = _dict(entry.data.get("review"))
    if review.get("actor") == "human":
        return [("human", f"Reviewed by {review.get('name') or 'an editor'} on {_date_text(review.get('on'))}")]
    return []


def _chips_html(chips) -> str:
    if not chips:
        return ""
    parts = []
    for role, label in chips:
        parts.append(f'<span class="mom-chip mom-chip-quiet">{_e(label)}</span>' if role == "quiet" else mom.provenance_chip(role, label))
    return '<span class="mom-chip-row">' + "".join(parts) + "</span>"


# ---------------------------------------------------------------------------------------------- advertisements

def _advertisements() -> list[dict]:
    """The ads in `web/ads.json`, checked; none when the file is missing or `enabled` is false. A bad ad stops the build, so nothing broken reaches a page."""
    if not ADS_PATH.is_file():
        return []
    document = json.loads(ADS_PATH.read_text(encoding="utf-8"))
    if not document.get("enabled", True):
        return []
    ads = document.get("ads") or []
    for ad in ads:
        mom.validate_advertisement(ad)
    return ads


def _advertisers_with_variants(ads: list[dict]) -> list[list[dict]]:
    """The ads grouped by advertiser, in file order: one advertiser can run several variants, and the advertisers, not the variants, take turns."""
    groups: dict[str, list[dict]] = {}
    for ad in ads:
        groups.setdefault(ad["advertiser"], []).append(ad)
    return list(groups.values())


def _choose_by_path(page, choices: list, slot: int = 0):
    """One of `choices` for one page, the same every time; `slot` moves a second slot on the page to the next choice."""
    return choices[(mom.hash_seed_to_unsigned_integer(page.path) + slot) % len(choices)]


def _variant_by_path(page, variants: list):
    """One advertiser's variant for a page, from a different part of the path's hash than the advertiser was chosen from."""
    return variants[(mom.hash_seed_to_unsigned_integer(page.path + "#variant")) % len(variants)]


def _ad_for_slot(page, unit: str, slot: int = 0):
    """The ad for one slot on one page: the same page always shows the same ad, two slots on a page show different advertisers when more than one is
    available, and each advertiser gets the same share of turns however many variants it runs."""
    advertisers = _advertisers_with_variants([ad for ad in _advertisements() if unit in mom.ad_units(ad)])
    if not advertisers:
        return None
    return _variant_by_path(page, _choose_by_path(page, advertisers, slot))


def _advertisement_html(page, unit: str, slot: int = 0, placement: str | None = None, contained: bool = False) -> str:
    ad = _ad_for_slot(page, unit, slot)
    return mom.advertisement(unit, ad, placement=placement, contained=contained) if ad is not None else ""


def _article_ad_choices(page) -> list[tuple[dict, str]]:
    """Every (ad, unit) an article can carry from the advertiser whose turn it is on this page and the variant it shows here: the closing band, and each
    in-content unit the ad offers. One is chosen per page, so an article still has one ad."""
    advertisers = _advertisers_with_variants(_advertisements())
    if not advertisers:
        return []
    ad = _variant_by_path(page, _choose_by_path(page, advertisers))
    return [(ad, unit) for unit in ("band", *mom.AD_IN_CONTENT_UNITS) if unit in mom.ad_units(ad)]


def _article_ad(page, body: str) -> tuple[str, str]:
    """The article body with its ad, and the closing markup after it. An in-content ad goes inside the words; a story too short to hold one gets the closing band instead."""
    choices = _article_ad_choices(page)
    if not choices:
        return body, ""
    ad, unit = _choose_by_path(SimpleNamespace(path=page.path + "#unit"), choices)
    if unit in IN_CONTENT_AD_AFTER_PARAGRAPH:
        markup = mom.advertisement(unit, ad, placement=f"article-{unit}")
        with_ad, _ = _after_paragraph(body, IN_CONTENT_AD_AFTER_PARAGRAPH[unit], markup)
        if with_ad != body:
            return with_ad, ""
        ad, unit = next(((a, u) for a, u in choices if u == "band"), (None, None))
        if ad is None:
            return body, ""
    return body, mom.advertisement("band", ad, placement="article-end", contained=True)


def _after_paragraph(html: str, paragraph_number: int, insertion: str) -> tuple[str, int]:
    """`html` with `insertion` after the Nth top-level paragraph (paragraphs inside quotes, lists and figures do not count), and the number of top-level paragraphs."""
    pieces = HTML_TAG_SPLIT.split(html)
    depth = 0
    paragraphs = 0
    insert_at = None
    for index, piece in enumerate(pieces):
        if not piece.startswith("<"):
            continue
        name = re.match(r"</?\s*([a-zA-Z0-9]+)", piece)
        tag = name.group(1).lower() if name else ""
        closing = piece.startswith("</")
        if tag in PARAGRAPH_CONTAINER_TAGS:
            depth = max(depth + (-1 if closing else 1), 0)
        elif tag == "p" and closing and depth == 0:
            paragraphs += 1
            if paragraphs == paragraph_number:
                insert_at = index
    if insert_at is None or paragraphs < IN_CONTENT_AD_MINIMUM_PARAGRAPHS:
        return html, paragraphs
    pieces[insert_at] += insertion
    return "".join(pieces), paragraphs


# ---------------------------------------------------------------------------------------------- cards

def _card_image(path):
    """A story's stored picture path as a root-absolute URL. The newsroom stores a picture as `media/assets/<slug>/<file>`; a card on the home or a list page would read that relative to its own folder and find nothing, while the file is served from `/assets/<slug>/<file>`."""
    if not path or re.match(r"^(https?:)?//", path) or path.startswith("/"):
        return path
    return "/" + (path[len("media/"):] if path.startswith("media/assets/") else path)


def _story_card(entry, size: str = "large", extra_class: str | None = None) -> str:
    meta_parts = [_date_text(entry.date)]
    meta_parts.insert(0, _byline(entry))
    return mom.story_card(
        headline=entry.title, href=entry.url or entry.link or "#", blurb=entry.summary_text or None, kicker=_topic_label(entry) or None,
        meta=" · ".join(part for part in meta_parts if part) or None, image=_card_image(entry.image), image_dark=_card_image(entry.image_dark), image_seed=entry.url or entry.title,
        provenance=_provenance(entry), size=size, class_name=extra_class,
    )


# The site says "concept" for what the knowledge graph calls a concept entity. "Topic" means topic analysis here, a neighbouring but different thing,
# so an entity of kind topic (or editor-concept) is a concept, and a concept never carries a type label.
CONCEPT_KINDS = frozenset({"concept", "topic", "editor-concept", "editor_concept", "editorconcept"})


def _concept_associations(connected_concepts: int, stories: int) -> int | None:
    """How well connected a concept is, the one number a later ranking reads: the concepts it is connected to in the knowledge graph plus the Stories
    that use it. None when it has neither, so a card shows nothing rather than a 0."""
    total = max(int(connected_concepts or 0), 0) + max(int(stories or 0), 0)
    return total or None


def _connected_concepts(site, entity_key) -> int:
    """Distinct other entities in the entity's neighbourhood in the knowledge snapshot (the same list the page's Connected terms prints)."""
    if site is None or not entity_key:
        return 0
    try:
        entity = site.knowledge._source.entity(str(entity_key)) or {}
    except Exception:  # a missing or unreadable snapshot is no association data, never a build failure
        return 0
    return len({row.get("key") for row in entity.get("neighbours") or [] if isinstance(row, dict) and row.get("key") and row.get("key") != entity_key})


def _story_use_counts(page) -> dict:
    def build():
        counts: dict = {}
        for entry in page.entries:
            if not _is_wiki(entry):
                for key in {_hashtag_key(tag) for tag in entry.tags}:
                    counts[key] = counts.get(key, 0) + 1
        return counts
    return page.site.memo("story-use-counts", build) if page.site is not None else build()


def _wiki_associations(entry, page) -> int | None:
    return _concept_associations(_connected_concepts(page.site, entry.data.get("entityKey")), _story_use_counts(page).get(_hashtag_key(entry.title), 0))


def _wiki_entry_card(entry, page) -> str:
    return mom.wiki_card(entry.title, entry.url or "#", associations=_wiki_associations(entry, page), definition=entry.summary_text or None)


def _large_card_classes(index: int, count: int | None) -> str:
    """A group's cards: the first is the largest (the list is best first), and a group of one is a feature, drawn beside its picture."""
    classes = ["rh-large"]
    if index == 0:
        classes.append("rh-first")
    if count == 1:
        classes.append("rh-solo")
    return " ".join(classes)


def _brief_markup(title, url, image, image_dark, date) -> str:
    """A post as a compact row: a small square picture beside the headline and the date, no blurb and no by-line (nobody writes a post). The home page's Latest Posts and an article's Posts use it."""
    picture = mom.card_image(_card_image(image), "", url or title, image_dark=_card_image(image_dark), square=True)
    return (f'<a class="rh-brief" href="{_e(url or "#")}">{picture}<span class="rh-brief-text">'
            f'<span class="rh-brief-title">{_e(title)}</span><span class="mom-meta">{_e(_date_text(date))}</span></span></a>')


def _brief_card(entry) -> str:
    return _brief_markup(entry.title, entry.url or entry.link, entry.image, entry.image_dark, entry.date)


def card(entry, page, variant=None, index=0, count=None):
    if _is_wiki(entry):
        return _wiki_entry_card(entry, page)
    if variant == "line":
        return f'<a class="mom-post-line" href="{_e(entry.url or "#")}"><span class="mom-post-line-title">{_e(entry.title)}</span><span class="mom-meta">{_e(" · ".join(part for part in (_byline(entry), _date_text(entry.date)) if part))}</span></a>'
    if variant == "post":
        return mom.story_card(headline=entry.title, href=entry.url or entry.link or "#", meta=_date_text(entry.date) or None,
                              image=_card_image(entry.image), image_dark=_card_image(entry.image_dark), image_seed=entry.url or entry.title, size="small", class_name="rh-post")
    if variant == "brief":
        return _brief_card(entry)
    if variant == "small":
        return _story_card(entry, "small")
    if variant == "lead":
        return _story_card(entry, "large", "mom-story-card-lead")
    if variant == "tile":
        return _story_card(entry, "large", "rh-tile")
    if variant == "large":
        return _story_card(entry, "large", _large_card_classes(index, count))
    return _story_card(entry)


# ---------------------------------------------------------------------------------------------- chrome

def head_extra(page):
    moved_to = MOVED_PAGES.get(page.path)
    redirect = f'\n<meta http-equiv="refresh" content="0; url={moved_to}">\n<link rel="canonical" href="{moved_to}">' if moved_to else ""
    return f'<meta name="color-scheme" content="light dark">\n<script>document.documentElement.classList.add("mom-js")</script>\n<script src="{SCRIPT_PATH}" defer></script>{redirect}'


def body_class(page):
    return f"mom mom-{page.kind}"


def _is_active(href: str, path: str) -> bool:
    if href == "/":
        return path == "/"
    return path.rstrip("/").startswith(href.rstrip("/"))


def _page_spine_with_brand(page) -> str:
    """The side of every page. The wordmark is the site's name, so every part of it links home, whatever section the page is in."""
    return mom.spine(subject=SITE_SPINE_SUBJECT, home_href="/", section_href="/")


def _page_spine(page) -> str:
    """The spine's top holds the home icon. The site card already names the publication, so the stacked wordmark there only repeated it."""
    return _page_spine_with_brand(page).replace(
        f'aria-label="{SITE_NAME}, home">{mom.wordmark("stacked")}</a>',
        f'aria-label="Home" title="Home">{mom.HOME_ICON}</a>', 1,
    )


def _page_path(page) -> str:
    return "/" + page.path.strip("/") + "/" if page.path.strip("/") else "/"


def _page_actions_row(page) -> str:
    """Every page offers its Markdown and sharing. An article carries them in its eyebrow row; other pages carry them here."""
    return f'<div class="mom-page-actions-row">{mom.article_actions(_page_path(page), page.title, page.settings.identity.production_url or "")}</div>'


def _nav_subtitle(settings, href: str) -> str:
    """The line under a destination in the menu, from the site's own data. Home is the tagline, Articles and Posts have their listing leads, a
    section (Concepts) has its configured description, and a page (Findings, Videos, Conversations) has its page description. Defined once: nothing here
    repeats a string that is written elsewhere."""
    if href == "/":
        return TAGLINE
    explicit = {"/articles/": ARTICLES_LEAD, "/posts/": POSTS_LEAD}
    if href in explicit:
        return explicit[href]
    section = next((candidate for candidate in settings.sections if f"/{candidate.base}/" == href and candidate.description), None)
    if section is not None:
        return section.description
    page = next((candidate for candidate in settings.pages if f"/{candidate.path.strip('/')}/" == href and candidate.description), None)
    return page.description if page is not None else ""


def masthead(page):
    settings = page.settings
    pills = "".join(
        f'<li>{mom.nav_pill(link.label, link.href, _is_active(link.href, page.path), "mom-nav-pill-newsroom" if link.href in NEWSROOM_NAV_PATHS else None)}</li>'
        for link in settings.nav
    )
    home_pill = f'<li class="mom-nav-home"><a class="mom-nav-pill mom-home-pill" href="/" aria-label="Home" title="Home">{mom.HOME_ICON}</a></li>'
    brand_pill = f'<a class="mom-brand-pill" href="/" aria-label="{SITE_NAME}, home">{mom.wordmark("inline")}</a>'
    destinations = [("Home", "/", _nav_subtitle(settings, "/"), page.path == "/")] + [
        (link.label, link.href, _nav_subtitle(settings, link.href), _is_active(link.href, page.path)) for link in settings.nav
    ]
    actions = "" if page.entry is not None and not _is_wiki(page.entry) else _page_actions_row(page)
    return (
        f'  <header class="mom-masthead"><nav class="mom-nav" aria-label="Site">{brand_pill}<ul class="mom-nav-items">{home_pill}{pills}</ul>{mom.menu_button()}</nav>'
        f'{mom.menu_panel(destinations)}</header>{_page_spine(page)}{actions}'
    )


def footer(page):
    links = (
        ("Findings", FINDINGS_PATH), ("Conversations", CONVERSATIONS_PATH), ("About", "/about/"), ("Corrections", "/corrections/"), ("RSS", FEED_PATH),
        ("For agents", LLMS_PATH), ("Privacy", "https://anth.us/privacy/"), ("Cookie settings", "#cookie-settings"),
    )
    link_html = "".join(f'<li><a href="{_e(href)}">{_e(label)}</a></li>' for label, href in links)
    return (
        '<div class="mom-footer">'
        f'<a class="mom-footer-wordmark" href="/" aria-label="{SITE_NAME}, home">{mom.wordmark("inline")}</a>'
        f'<p class="mom-footer-tagline">{TAGLINE}</p>'
        f'<nav aria-label="Footer"><ul class="mom-footer-links">{link_html}</ul></nav>'
        '<p class="mom-footer-note">Published by <a href="https://anth.us">Anthus AI Solutions</a>. Built with <a href="https://p.apyr.us">Papyrus</a>.</p></div>'
    )


# ---------------------------------------------------------------------------------------------- hashtags and pull quotes

def _link_hashtags(html: str, terms: dict) -> str:
    """Turn `#CamelCase` in running text into a link to its wiki term, outside links, code and headings. A hashtag with no wiki page stays text."""
    skipped_depth = 0
    pieces = []
    for piece in HTML_TAG_SPLIT.split(html):
        if piece.startswith("<"):
            name = re.match(r"</?\s*([a-zA-Z0-9]+)", piece)
            tag = name.group(1).lower() if name else ""
            if tag in ("a", "code", "pre", "h1", "h2", "h3", "h4"):
                skipped_depth += -1 if piece.startswith("</") else 1
                skipped_depth = max(skipped_depth, 0)
            pieces.append(piece)
        elif skipped_depth:
            pieces.append(piece)
        else:
            def link(found):
                path = terms.get(_hashtag_key(found.group(1)))
                return f'<a class="mom-hashtag" href="{_e(path)}">#{found.group(1)}</a>' if path else found.group(0)
            pieces.append(HASHTAG.sub(link, piece))
    return "".join(pieces)


def item_decorator(html, summary, site=None):
    html = ARTICLE_QUOTE.sub(
        lambda found: found["markus_quote"] or mom.pull_quote(unescape(found["plain_quote"]).strip()),
        html,
    )
    return _link_hashtags(html, _wiki_terms(site)) if site is not None else html


# ---------------------------------------------------------------------------------------------- pages

def _body_of(page) -> str:
    return MARKUS_HEADER.sub("", page.fragment, count=1)


def _article_hero(entry, body: str) -> str:
    """The article's picture. A body that opens with a figure already has one. Without one, the seeded placeholder art is a slim band: cards need the full-size art, a reading page does not."""
    if BODY_OPENS_WITH_FIGURE.match(body):
        return ""
    if entry.image:
        return f'<div class="mom-article-hero">{mom.card_image(_card_image(entry.image), "", entry.url or entry.title)}</div>'
    return f'<div class="mom-article-hero mom-article-hero-band">{mom.card_image(None, "", entry.url or entry.title)}</div>'


def _article_main(page) -> str:
    entry = page.entry
    section = entry.section
    subject = _topic_label(entry) or "Machines"
    subtitle = _subtitle(entry)
    section_page = _section_resolver(page)(entry.topic)
    section_href = section_page[0] if section_page else f"/{section.base}/" if section is not None else "/"
    meta = " · ".join(
        part for part in (_byline(entry), _date_text(entry.date)) if part
    )
    terms = _wiki_terms(page.site)
    rail = _article_rail(page)
    body = _body_of(page)
    body, closing_band = _article_ad(page, body)  # one ad on an article page: inside the words, or at the end where the reader has finished
    topic = _topic_label(entry)
    kicker = f'<a class="mom-kicker" href="{_e(section_href)}">{_e(topic)}</a>' if topic else ""
    actions = mom.article_actions(entry.url, entry.title, page.settings.identity.production_url or "") if entry.url else ""
    return (
        f'<div class="mom-article-layout{" mom-has-article-rail" if rail else ""}">'
        '<article class="mom-article">'
        f'<header class="mom-article-header"><div class="mom-article-eyebrow">{kicker}{actions}</div>{_chips_html(_provenance(entry))}'
        f'<h1 class="mom-headline">{_e(entry.title)}</h1>'
        + (f'<p class="mom-dek">{_e(subtitle)}</p>' if subtitle else "")
        + (f'<p class="mom-meta">{_e(meta)}</p>' if meta else "")
        + "</header>"
        f'{_article_hero(entry, body)}'
        f'<div class="mom-article-body">{_with_end_matter(body, _concepts_html(entry, page, terms))}</div>{closing_band}'
        f"</article>{rail}"
        "</div>"
    )


def _hashtag_text(name: str) -> str:
    """A concept's name as a hashtag: the words joined, each starting with a capital, so `voice cloning` reads `#VoiceCloning` and `AI agent` reads `#AIAgent`."""
    return "".join(word[:1].upper() + word[1:] for word in re.findall(r"[A-Za-z0-9]+", str(name or "")))


def _concepts_html(entry, page, terms: dict) -> str:
    """The concepts a story is tagged with that have a public page, as hashtag-styled links, the ones the most stories use first. The page's relations supply them
    (`page.concept_links`); a story's own front-matter tags that match a concept page join them. Nothing at all when there are none. There is no list of hashtags that are not links."""
    found = [(link["href"], link["name"], link.get("stories") or 0) for link in getattr(page, "concept_links", ()) if link.get("href") and link.get("name")]
    known = {href for href, _, _ in found}
    for tag in entry.tags:
        href = terms.get(_hashtag_key(tag))
        if href and href not in known:
            known.add(href)
            found.append((href, tag, len(_stories_using(page, _hashtag_key(tag)))))
    if not found:
        return ""
    found.sort(key=lambda row: (-row[2], row[1].casefold()))
    items = "".join(f'<li><a class="mom-hashtag" href="{_e(href)}">#{_e(_hashtag_text(name))}</a></li>' for href, name, _ in found)
    return f'<section class="mom-concepts" aria-label="Concepts"><ul class="mom-hashtags">{items}</ul></section>'


def _with_end_matter(body: str, concepts: str) -> str:
    """Puts the concepts and then the References heading before the citation list, each only when it has something under it."""
    list_start = body.find(CITATION_LIST_WITH_ITEMS)
    if list_start >= 0:
        return f'{body[:list_start]}{concepts}<h2 id="references">References</h2>{body[list_start:]}'
    if not concepts:
        return body
    document_end = body.rfind("</article>")
    return f"{body[:document_end]}{concepts}{body[document_end:]}" if document_end >= 0 else body + concepts


def _article_rail(page) -> str:
    """What sits beside the text on a wide window and under it on a narrow one: See also (the related articles, with the large story card) and Posts (the related posts, as the
    compact rows of the home page). Each only when there is something to show; with neither, no rail. The links come from the page's relations (`page.related_stories`)."""
    related = [story for story in getattr(page, "related_stories", ()) if story.get("url") and story.get("title")]
    articles = [story for story in related if story.get("type") == "article"]
    posts = [story for story in related if story.get("type") == "post"]
    sections = []
    if articles:
        cards = "".join(
            mom.story_card(headline=story["title"], href=story["url"], blurb=story.get("summary") or None, meta=_date_text(story.get("date")) or None,
                           image=_card_image(story.get("image")), image_seed=story["url"], size="large", class_name="rh-large")
            for story in articles
        )
        sections.append(f'<section class="mom-rail-section" aria-labelledby="mom-see-also-h"><h2 id="mom-see-also-h" class="mom-rail-title">See also</h2><div class="mom-rail-cards">{cards}</div></section>')
    if posts:
        rows = "".join(_brief_markup(story["title"], story["url"], story.get("image"), None, story.get("date")) for story in posts)
        sections.append(f'<section class="mom-rail-section" aria-labelledby="mom-posts-h"><h2 id="mom-posts-h" class="mom-rail-title">Posts</h2><div class="mom-rail-posts">{rows}</div></section>')
    sources = [source for source in getattr(page, "related_references", ()) if source.get("url") and source.get("title")]
    if sources:
        tiles = "".join(_source_tile(source) for source in sources)
        sections.append(f'<section class="mom-rail-section" aria-labelledby="mom-sources-h"><h2 id="mom-sources-h" class="mom-rail-title">Related findings</h2><div class="mom-rail-sources">{tiles}</div></section>')
    return f'<aside class="mom-article-rail">{"".join(sections)}</aside>' if sections else ""


def _source_tile(source) -> str:
    """A related Reference: somebody else's page, so a quiet text tile (the site, the headline, a short summary when there is one) that opens in a new tab and says so with the external-link icon. It has no picture on purpose: many sources have none, and the three kinds of related content should look different."""
    host = source.get("host") or ""
    kind = "Video" if source.get("medium") == "video" else ""
    label = " · ".join(part for part in (host, kind) if part)
    summary = f'<span class="mom-source-summary">{_e(source["summary"])}</span>' if source.get("summary") else ""
    return (f'<a class="mom-source" href="{_e(source["url"])}" target="_blank" rel="noopener noreferrer">'
            f'<span class="mom-source-host">{_e(label)}{mom.lucide_icon("external-link")}</span>'
            f'<span class="mom-source-title">{_e(source["title"])}</span>{summary}</a>')


def _stories_using(page, term_key: str) -> list:
    return [
        entry for entry in page.entries
        if not _is_wiki(entry) and any(_hashtag_key(tag) == term_key for tag in entry.tags)
    ]


def _wiki_main(page) -> str:
    entry = page.entry
    stories = _stories_using(page, _hashtag_key(entry.title))
    stories_html = (
        '<section class="mom-wiki-stories" aria-labelledby="mom-wiki-stories-h"><h2 id="mom-wiki-stories-h" class="mom-panel-head">Stories that use this term</h2>'
        f'<div class="mom-story-grid">{"".join(_story_card(story, "small") for story in stories)}</div></section>'
        if stories else ""
    )
    superseded = STOCK_SUPERSEDED.search(page.wiki_stamp)
    rail_ad = _advertisement_html(page, "half-page", 0, "wiki-rail")
    in_flow_ad = f'<div class="mom-ad-in-flow">{_advertisement_html(page, "story", 0, "wiki-rail")}</div>' if rail_ad else ""
    rail = f'<div class="mom-ad-rail">{rail_ad}</div>' if rail_ad else ""
    return (
        f'<div class="mom-article-layout mom-wiki-layout{" mom-has-rail" if rail_ad else ""}">'
        '<article class="mom-article mom-wiki-term">'
        f'<header class="mom-article-header"><a class="mom-kicker" href="/{WIKI_SECTION}/">Machines on {WIKI_SUBJECT}</a>{_chips_html(_wiki_chips(entry))}'
        f'<h1 class="mom-term"><span class="mom-term-hash" aria-hidden="true">#</span>{_e(entry.title)}</h1></header>'
        + (superseded.group(0) if superseded else "")
        + f'<div class="mom-article-body mom-wiki-body">{_body_of(page)}</div>'
        f"{in_flow_ad}{stories_html}{page.wiki_footer}</article>{rail}"
        "</div>"
    )


def _recent_tag_counts(entries, newest: str, days: int) -> dict:
    """Hashtag counts among entries dated within `days` of `newest`; the reference is the newest entry, so a page does not change just because time passes."""
    counts = {}
    try:
        newest_day = date.fromisoformat(newest)
    except ValueError:
        return counts
    for entry in entries:
        try:
            age = (newest_day - date.fromisoformat(entry.date)).days
        except ValueError:
            continue
        if 0 <= age < days:
            for tag in entry.tags:
                counts[tag] = counts.get(tag, 0) + 1
    return counts


def _topic_bands(entries) -> str:
    """Loop bands for a section: topics rising fast (machine), topics editors are watching (human), topics new this week (brand). Each band appears only when it has topics."""
    stories = [entry for entry in entries if not _is_wiki(entry) and entry.date]
    if not stories:
        return ""
    newest = max(entry.date for entry in stories)
    recent = _recent_tag_counts(stories, newest, RISING_WINDOW_DAYS)
    earlier_cutoff = date.fromisoformat(newest).toordinal() - RISING_WINDOW_DAYS if recent else 0
    earlier = {}
    for entry in stories:
        if date.fromisoformat(entry.date).toordinal() <= earlier_cutoff:
            for tag in entry.tags:
                earlier[tag] = earlier.get(tag, 0) + 1
    topics = {
        "rising": sorted((tag for tag, count in recent.items() if count > earlier.get(tag, 0)), key=lambda tag: (-recent[tag], tag)),
        "watching": sorted({tag for entry in stories if _truthy(entry.data.get("editorsPick")) for tag in entry.tags}),
        "new": sorted(_recent_tag_counts(stories, newest, NEW_THIS_WEEK_DAYS), key=lambda tag: tag),
    }
    bands = []
    for index, (kind, role, label) in enumerate(BAND_KINDS):
        tags = topics[kind]
        if tags:
            speed = 1 + min(len(tags), 6) / 6 if kind == "rising" else 1
            bands.append(_loop_band(role, [f"#{tag}" for tag in tags], label, speed, index))
    return f'<div class="mom-bands" aria-label="Topics in this section">{"".join(bands)}</div>' if bands else ""


def _loop_band(role: str, words, label: str | None, speed: float, band_index: int) -> str:
    pattern = list(words)
    repeat = max(4, -(-BAND_MINIMUM_WORDS // len(pattern)))
    return mom.loop_band(role, pattern, repeat, label, speed=speed, class_name=f"mom-band-direction-{'left' if band_index % 2 == 0 else 'right'}")


def _site_card(heading_level: int | None = 1) -> str:
    """The one site title card every page uses, always the site's own name and tagline. The spine says what the page is about."""
    return mom.sticker(tagline=TAGLINE, heading_level=heading_level, class_name="mom-sticker-fit")


def _page_top(title: str, dek_html: str = "", card: bool = True) -> str:
    """The one page header: title and lead on the left, the site title card busting out at the top right. The title is the page's heading, so the card has none.
    A page that places the card itself (the forum's pages put it in their side column) asks for `card="none"`."""
    card_html = f'<div class="mom-page-card mom-site-card-slot">{_site_card(heading_level=None)}</div>' if card else ""
    return (
        '<div class="mom-page-top">'
        f'<header class="mom-page-head"><h1 class="mom-page-title">{_e(title)}</h1>{dek_html}</header>'
        f"{card_html}"
        "</div>"
    )


def _listing_main(page) -> str:
    view = page.listing
    if view is None:
        return None
    if page.kind == "listing" and view.section in SECTIONED_LISTINGS:
        story_type, lead = SECTIONED_LISTINGS[view.section]
        return _sectioned_page(page.entries, story_type, view.label, lead, _section_resolver(page), page.ranked)
    section = next((candidate for candidate in page.settings.sections if candidate.name == view.section), None)
    is_wiki = view.section == WIKI_SECTION
    collection = page.settings.collection(view.collection) if view.collection else None
    description = (section.description if section is not None and page.kind == "listing" else "") or (collection.description if collection is not None else "") or LISTING_LEADS.get(view.label, "")
    entries = view.featured + view.entries
    card_markup = [card(entry, page) for entry in entries]
    if not is_wiki and len(card_markup) >= SECTION_AD_CARD_POSITION:
        ad_card = _advertisement_html(page, "card", 0, "listing-card")
        if ad_card:
            card_markup.insert(SECTION_AD_CARD_POSITION - 1, ad_card)
    cards = "".join(card_markup)
    closing_band = "" if is_wiki or not card_markup else _advertisement_html(page, "band", 1, "listing-end")
    grid_class = "mom-wiki-grid" if is_wiki else "mom-story-grid"
    pager = page.components.pager(view.page, view.pages, view.url_for_page) if view.pages > 1 else ""
    bands = "" if is_wiki or view.page != 1 or collection is not None else _topic_bands(view.all_entries)
    intro = page.fragment if page.fragment and not is_wiki else ""
    lead = f'<div class="mom-section-intro">{intro}</div>' if intro else (f'<p class="mom-dek">{_e(description)}</p>' if description else "")
    title = f"#{view.label}" if page.kind == "tag" else view.label
    return (
        f'<div class="mom-page mom-section-page">{_page_top(title, lead)}'
        + (f'<div class="{grid_class}">{cards}</div>' if cards else '<p class="mom-empty">Nothing has been published here yet.</p>')
        + f"{bands}{pager}{closing_band}</div>"
    )


def main(page):
    if page.kind == "item":
        return _wiki_main(page) if _is_wiki(page.entry) else _article_main(page)
    if page.kind in ("listing", "tag"):
        return _listing_main(page)
    return None


# ---------------------------------------------------------------------------------------------- stock home-page cards, drawn as design-system cards

def _tile_to_reference_card(found) -> str:
    status, inner = found.group(1), found.group(2)
    image = _first(r'<img class="home-page-image" src="([^"]*)"', inner)
    host = _first(r'<p class="home-page-eyebrow">(.*?)</p>', inner)
    linked = re.search(r'<h3 class="home-page-title"><a href="([^"]*)"[^>]*>(.*?)</a></h3>', inner, re.S)
    title = _plain(linked.group(2)) if linked else _plain(_first(r'<h3 class="home-page-title">(.*?)</h3>', inner) or "Untitled")
    href = unescape(linked.group(1)) if linked else "#"
    accepted = re.search(r'Accepted <time datetime="[^"]*">([^<]*)</time>', inner)
    published = re.search(r'Published <time datetime="[^"]*">([^<]*)</time>', inner)
    percent = _first(r'home-page-confidence-value">(\d+)% confidence', inner)
    actor_text = _plain(_first(r'<p class="home-page-actor">(.*?)</p>', inner) or "")
    actor = "human" if actor_text == "Accepted by an editor" else None
    stars = _first(r'data-stars="([1-5])"', inner)
    section = _first(r'<span class="home-page-chip" data-kind="section" data-shown="true">(.*?)</span>', inner)
    return mom.reference_card(
        title=title, href=href, status=status, actor=actor, image=unescape(image) if image else None, host=_plain(host) if host else None,
        meta_date=(accepted or published).group(1) if (accepted or published) else None,
        confidence=int(percent) / 100 if percent else None, stars=int(stars) if stars else None, section=_plain(section) if section else None,
    )


def _thread_to_thread_card(found) -> str:
    inner = found.group(2)
    anchor = _plain(_first(r'<p class="home-page-eyebrow home-page-anchor"[^>]*>(.*?)</p>', inner) or "")
    linked = re.search(r'<h3 class="home-page-title"><a href="([^"]*)">(.*?)</a></h3>', inner, re.S)
    title = _plain(linked.group(2)) if linked else _plain(_first(r'<h3 class="home-page-title">(.*?)</h3>', inner) or "Conversation")
    count = _first(r"<span>(\d+) messages?</span>", inner)
    last = _first(r'<time datetime="[^"]*">([^<]*)</time>', inner)
    excerpt = _first(r'<p class="home-page-excerpt">(.*?)</p>', inner)
    author = _first(r'<p class="home-page-author">by (.*?)</p>', inner)
    return mom.thread_card(
        title=title, href=unescape(linked.group(1)) if linked else "#", anchor=anchor or None, author=_plain(author) if author else None,
        latest=_plain(excerpt) if excerpt else None, messages=int(count) if count else None, last_at=last,
    )


CONCEPT_CHIP_KIND = re.compile(
    r'(<(?:a|span) class="papyrus-knowledge-chip[^"]*" data-kind="(?:%s)"[^>]*>)<span class="papyrus-knowledge-chip-kind">[^<]*</span>' % "|".join(sorted(CONCEPT_KINDS))
)


def _unlabel_concept_chips(html: str) -> str:
    """Core prints the entity kind before a connected term ("Topic Benchmarks"). Every concept here is a concept, so it carries no type label; chips of
    other kinds keep theirs."""
    return CONCEPT_CHIP_KIND.sub(r"\1", html)


WIKI_GRID = re.compile(r'(<div class="mom-wiki-grid">)(.*?)(</div>)', re.S)
WIKI_CARD = re.compile(r'<a class="mom-wiki-card"[^>]*>.*?</a>', re.S)
WIKI_CARD_ASSOCIATIONS = re.compile(r'data-associations="(\d+)"')


def _most_connected_first(html: str) -> str:
    """The concept index lists the most connected concept first. Core lists the concept pages in the order their pages say; the site's measure is a concept's
    associations (the `data-associations` on its card), so the cards are put in that order: most associations first, a concept with no count last, and
    concepts with the same count keep the order core gave them. It orders the cards of one page of the index, which is the whole index until it has more
    concepts than a page holds."""
    def reorder(found):
        cards = WIKI_CARD.findall(found.group(2))
        if len(cards) < 2:
            return found.group(0)
        def associations(card):
            counted = WIKI_CARD_ASSOCIATIONS.search(card)
            return int(counted.group(1)) if counted else -1
        return found.group(1) + "".join(sorted(cards, key=lambda card: -associations(card))) + found.group(3)
    return WIKI_GRID.sub(reorder, html, count=1)


RAIL = re.compile(r'(<section class="mom-home-rail"[^>]*>)(.*?)(</section>\s*</div>)', re.S)
RAIL_THREADS = re.compile(r'<section class="home-page-threads"[^>]*>(.*?)</section>', re.S)


def _thread_to_line(found) -> str:
    """A conversation as one line of the home page's rail: its title, and how many messages it has and when the last one came."""
    inner = found.group(2)
    linked = re.search(r'<h3 class="home-page-title"><a href="([^"]*)">(.*?)</a></h3>', inner, re.S)
    title = _plain(linked.group(2)) if linked else _plain(_first(r'<h3 class="home-page-title">(.*?)</h3>', inner) or "Conversation")
    count = _first(r"<span>(\d+) messages?</span>", inner)
    last = _first(r'<time datetime="[^"]*">([^<]*)</time>', inner)
    parts = [f"{count} message{'' if count == '1' else 's'}" if count else "", last or ""]
    meta = " · ".join(part for part in parts if part)
    href = unescape(linked.group(1)) if linked else "#"
    return f'<a class="mom-post-line" href="{_e(href)}"><span class="mom-post-line-title">{_e(title)}</span>' + (f'<span class="mom-meta">{_e(meta)}</span>' if meta else "") + "</a>"


def _rail_conversations(html: str) -> str:
    """The rail beside the lead lists conversations as lines. The page offers as many as it has; the stylesheet shows the whole lines that fit beside the lead."""
    def rail(found):
        def lines(threads):
            return '<div class="mom-post-lines">' + STOCK_THREAD.sub(_thread_to_line, threads.group(1)).replace("<ul class=\"home-page-grid\" data-layout=\"list\">", "").replace("</ul>", "").replace("<li>", "").replace("</li>", "") + "</div>"
        body = RAIL_THREADS.sub(lines, found.group(2))
        if 'class="mom-post-lines"' not in body:
            body += '<div class="mom-post-lines"></div>'
        return found.group(1) + body + found.group(3)
    return RAIL.sub(rail, html, count=1)


# ---------------------------------------------------------------------------------------------- links to section pages, "More <thing>…" links

HOME_GROUP = re.compile(
    r'(<section class="papyrus-group [^"]*" data-section="([^"]*)" data-label="[^"]*" data-index="\d+" data-count="(\d+)">)(.*?)(</section>)', re.S,
)
HOME_GROUP_TITLE = re.compile(r'(<h2 class="papyrus-group-title">)(.*?)(</h2>)', re.S)
HOME_GROUP_MORE = re.compile(r'<a class="papyrus-group-more"[^>]*>.*?</a>', re.S)
MORE_LINKS = {"/videos/": "More videos", "/findings/": "More Findings"}
MORE_LINK = re.compile(r'<a href="(/videos/|/findings/)">More</a>')


def _home_group_label(name: str, resolve) -> str:
    found = resolve(name)
    return found[1] if found else TOPIC_LABELS.get(name) or _titled_topic(name)


HOME_FEATURES = '<div class="rh-features">'
HOME_GROUP_OPENING = '<section class="papyrus-group rh-group'
HOME_BAND_OPENING = '<div class="mom-band '
HOME_PAGE_OPENING = '<div class="mom-page'


def _band_midway(html: str) -> str:
    """The first branding band of the home page sits halfway through the articles, not after them. The band is full width, so the page container closes before it
    and opens again after it; the article sections split into two halves (the second half the larger when the count is odd)."""
    features = html.find(HOME_FEATURES)
    if features == -1 or ">Top Articles<" not in html:
        return html
    band_start = html.find(HOME_BAND_OPENING, features)
    if band_start == -1:
        return html
    ends = [position for position in (html.find(HOME_BAND_OPENING, band_start + 1), html.find(HOME_PAGE_OPENING, band_start)) if position != -1]
    if not ends:
        return html
    band_end = min(ends)  # a band ends where the next band or the next page container begins
    starts = [found.start() for found in re.finditer(re.escape(HOME_GROUP_OPENING), html[features:band_start])]
    if len(starts) < 2:
        return html
    band = html[band_start:band_end]
    split = features + starts[len(starts) // 2]
    return (html[:split] + "</div></div>" + band + '<div class="mom-page mom-home rh-home">' + HOME_FEATURES
            + html[split:band_start] + html[band_end:])


def _home_groups(html: str, resolve) -> str:
    """A group of stories on the home page is named for its section. The name links to the section's page, and a group of more than one story ends with
    "More <section>…" to the same place. A section with no page gets neither link."""
    def group(found):
        opening, name, count, inside, closing = found.groups()
        label = _home_group_label(name, resolve)
        found_page = resolve(name)
        href = found_page[0] if found_page else None
        inside = HOME_GROUP_MORE.sub("", inside)
        inside = HOME_GROUP_TITLE.sub(lambda title: title.group(1) + _linked_title(_e(label), href) + title.group(3), inside, count=1)
        return opening + inside + (_more_link(label, href) if int(count) > 1 else "") + closing
    return HOME_GROUP.sub(group, html)


HOME_FINDINGS_SHOWN = 12
HOME_FINDINGS = re.compile(r'(<section class="mom-section rh-findings" aria-label="Findings">.*?<ul class="home-page-grid[^"]*"[^>]*>)(.*?)(</ul>)', re.S)


def _finding_row(tile: str) -> str:
    """A finding on the home page as a compact row, like a post: a small square picture, the headline, and the site it is on with the date. It leads to somebody else's page, so it opens in a
    new tab and says so with the external-link icon; it is a quiet row, not a card."""
    image = _first(r'<img class="home-page-image" src="([^"]*)"', tile)
    host = _first(r'<p class="home-page-eyebrow">(.*?)</p>', tile)
    linked = re.search(r'<h3 class="home-page-title"><a href="([^"]*)"[^>]*>(.*?)</a></h3>', tile, re.S)
    title = _plain(linked.group(2)) if linked else _plain(_first(r'<h3 class="home-page-title">(.*?)</h3>', tile) or "Untitled")
    href = unescape(linked.group(1)) if linked else "#"
    dated = re.search(r'(?:Accepted|Published) <time datetime="[^"]*">([^<]*)</time>', tile)
    meta = " · ".join(part for part in (_plain(host) if host else "", dated.group(1) if dated else "") if part)
    picture = mom.card_image(unescape(image) if image else None, "", href or title, square=True)
    return (f'<a class="rh-brief rh-finding" href="{_e(href)}" target="_blank" rel="noopener noreferrer">{picture}<span class="rh-brief-text">'
            f'<span class="rh-brief-title">{_e(title)}</span><span class="mom-meta">{_e(meta)}{mom.lucide_icon("external-link")}</span></span></a>')


def _home_findings(html: str) -> str:
    """The home page's Findings: the best accepted References of the week, never a video, as the same compact rows as Latest Posts. The page asks for more than it shows, because the engine's
    list cannot yet leave videos out (Papyrus 5.95.0 has no notMedium; it is in 5.96.0-next.1), and this keeps the first HOME_FINDINGS_SHOWN that are not videos."""
    def grid(found):
        opening, body, closing = found.groups()
        tiles = [tile for tile in TILE_ITEM.findall(body) if not _is_video(tile)][:HOME_FINDINGS_SHOWN]
        counted = lambda text: re.sub(r'data-count="\d+"', f'data-count="{len(tiles)}"', text)
        return counted(opening) + "".join(f"<li>{_finding_row(tile)}</li>" for tile in tiles) + closing
    return HOME_FINDINGS.sub(grid, html, count=1)


def _more_links_say_what(html: str) -> str:
    """A "More" link that the engine writes after a Reference block says what it leads to: "More videos…"."""
    return MORE_LINK.sub(lambda found: f'<a href="{found.group(1)}">{MORE_LINKS[found.group(1)]}{MORE_ELLIPSIS}</a>', html)



# ---------------------------------------------------------------------------------------------- the home page's video, conversation and concept sections
# The home page asks the engine once for the best videos of the week (the site's rolling bucket, then stars; the ranking the Videos page and the section pages use). The
# videos are handed out here: first to the Worth Watching cards of HOME_WORTH_WATCHING_SECTIONS (HOME_WORTH_WATCHING_VIDEOS each, in the order the sections are listed),
# then to the Videos section, so a video appears once on the page. No Reference is filed under a section yet in production, so a section's card is not about the
# section; it is the next best videos. A part with nothing to show is left out of the page.
HOME_VIDEOS_REGION = re.compile(r'<!--home:videos-->(.*?)<!--/home:videos-->', re.S)
HOME_CONVERSATIONS_REGION = re.compile(r'<!--home:conversations-->(.*?)<!--/home:conversations-->', re.S)
HOME_GROUP_ANY = re.compile(r'(<section class="papyrus-group [^"]*" data-section="([^"]*)"[^>]*data-count=")(\d+)(">)(.*?)(</section>)', re.S)
LAST_MORE_LINK = '<p class="mom-more">'


def _home_section_head(identifier: str, title: str, href: str, link_text: str) -> str:
    return (f'<div class="mom-section-head"><h2 id="{identifier}" class="mom-section-title">{_e(title)}</h2>'
            f'<a class="mom-section-link" href="{_e(href)}">{_e(link_text)}</a></div>')


def _before_last_more_link(inside: str, addition: str) -> str:
    position = inside.rfind(LAST_MORE_LINK)
    return inside + addition if position == -1 else inside[:position] + addition + inside[position:]


def _worth_watching_card(tiles: list[str]) -> str:
    items = "".join(f"<li>{tile}</li>" for tile in tiles)
    return (
        '<div class="mom-worth-watching" role="group" aria-label="Worth Watching"><div class="mom-section-head">'
        '<h3 class="mom-worth-watching-title">Worth Watching</h3><a class="mom-section-link" href="/videos/">More videos' + MORE_ELLIPSIS + '</a></div>'
        f'<ul class="home-page-grid mom-worth-watching-row" data-card="tile" data-count="{len(tiles)}">{items}</ul></div>'
    )


def _in_group(html: str, name: str, change) -> str:
    """`change(found)` for the home page's group of the section called `name`, if it has one."""
    return HOME_GROUP_ANY.sub(lambda found: change(found) if found.group(2) == name else found.group(0), html)


def _home_videos(html: str) -> str:
    """Worth Watching cards inside the chosen topic sections, then the Videos section with the videos that are left."""
    region = HOME_VIDEOS_REGION.search(html)
    if not region:
        return html
    queue = TILE_ITEM.findall(region.group(1))
    html = html.replace(region.group(0), "@@home-videos@@")

    def with_card(found):
        nonlocal queue
        if not queue:
            return found.group(0)
        taken, queue = queue[:HOME_WORTH_WATCHING_VIDEOS], queue[HOME_WORTH_WATCHING_VIDEOS:]
        return found.group(1) + found.group(3) + found.group(4) + _before_last_more_link(found.group(5), _worth_watching_card(taken)) + found.group(6)
    for name in HOME_WORTH_WATCHING_SECTIONS:
        html = _in_group(html, name, with_card)
    shown = queue[:HOME_VIDEOS_SHOWN]
    section = ""
    if shown:
        section = (
            '<div class="mom-page mom-home rh-home"><section class="mom-section rh-videos" aria-labelledby="mom-home-videos">'
            + _home_section_head("mom-home-videos", "Videos", "/videos/", "All videos")
            + _reference_rows_html(shown, _row_sizes(len(shown))) + "</section></div>"
        )
    return html.replace("@@home-videos@@", section)


def _home_ad_cards(html: str, page) -> str:
    """An advertisement as one more card in each of the chosen topic sections that has two cards (it makes the row three); none when the site has no card ad."""
    def group(found):
        name = found.group(2)
        if name not in HOME_AD_CARD_SECTIONS or found.group(3) != "2":
            return found.group(0)
        ad = _advertisement_html(page, "card", HOME_AD_CARD_SECTIONS.index(name), "home-card")
        if not ad:
            return found.group(0)
        return found.group(1) + "3" + found.group(4) + _before_last_more_link(found.group(5), ad) + found.group(6)
    return HOME_GROUP_ANY.sub(group, html)


def _home_conversations(html: str) -> str:
    """The Conversations section: the most recent conversations as the site's thread cards, with the standard section heading. Nothing when there are none."""
    def section(found):
        body = found.group(1)
        if '<article class="home-page-thread"' not in body:
            return ""
        return (
            '<div class="mom-page mom-home rh-home"><section class="mom-section rh-conversations" aria-labelledby="mom-home-conversations">'
            + _home_section_head("mom-home-conversations", "Conversations", CONVERSATIONS_PATH, "All conversations") + body + "</section></div>"
        )
    return HOME_CONVERSATIONS_REGION.sub(section, html)


def _home_concepts(page) -> str:
    """The Concepts section that ends the home page: the most connected concepts (the order the concept index uses: associations, most first, ties in the index's order),
    as the index's own cards, with a link to all of them."""
    concepts = [entry for entry in page.entries if _is_wiki(entry) and entry.url]
    associations = {id(entry): _wiki_associations(entry, page) or -1 for entry in concepts}
    top = sorted(concepts, key=lambda entry: -associations[id(entry)])[:HOME_CONCEPTS_SHOWN]
    if not top:
        return ""
    cards = "".join(_wiki_entry_card(entry, page) for entry in top)
    return (
        '<div class="mom-page mom-home rh-home"><section class="mom-section rh-concepts" aria-labelledby="mom-home-concepts">'
        + _home_section_head("mom-home-concepts", "Concepts", f"/{WIKI_SECTION}/", "All concepts")
        + f'<div class="mom-wiki-grid mom-home-concepts">{cards}</div></section></div>'
    )

# ---------------------------------------------------------------------------------------------- section pages
# Every section page is made from one template (web/pages/section.template.md, filled in by tools/sync_section_pages.py). Its articles, posts and videos are
# the engine's own includes, already filtered to the section and ranked by the site's rule. The conversations include has no section filter yet, so the page
# asks for the recent ones and keeps those anchored to a Story of this section here (a Story's address says which section it is in).
CONVERSATION_LINES = 8
ARTICLES_PATH_FORMAT = "/{section}/articles/"
POSTS_PATH_FORMAT = "/{section}/posts/"
SECTION_VIDEOS = re.compile(r'<!--sf:videos:(\d+)-->(.*?)<!--/sf:videos-->', re.S)
SECTION_FINDINGS = re.compile(r'<!--sf:findings:(\d+)-->(.*?)<!--/sf:findings-->', re.S)
SECTION_CONVERSATIONS = re.compile(r'<!--sf:conversations-->(.*?)<!--/sf:conversations-->', re.S)
SECTION_VIDEO_ITEM = re.compile(r'<li>.*?</li>', re.S)
THREAD_ANCHOR_LINK = re.compile(r'class="home-page-eyebrow home-page-anchor"[^>]*>.*?<a href="([^"]*)"', re.S)
CONVERSATION_COUNT_MARK = "<!--sf:conversation-count-->"


def _section_page_name(page) -> str | None:
    custom = getattr(page, "custom_id", None) or ""
    return custom[len(SECTION_PAGE_PREFIX):] if page.kind == "custom" and custom.startswith(SECTION_PAGE_PREFIX) else None


def _section_stories(page, name: str, story_type: str | None = None) -> list:
    return [entry for entry in page.entries if entry.topic == name and entry.url and (story_type is None or entry.type == story_type)]


VIDEO_GRID_OPENING = re.compile(r'<ul class="home-page-grid[^"]*"[^>]*>')


def _section_videos(found, section: str) -> str:
    """The home page's Worth Watching panel, cut to the videos a section page shows. The page asks for one video more than it shows, to know whether to say "More videos…"."""
    shown, body = int(found.group(1)), found.group(2)
    items = SECTION_VIDEO_ITEM.findall(body)
    opening = VIDEO_GRID_OPENING.search(body)
    if not items or not opening:
        return ""
    kept = min(len(items), shown)
    before, after = body[:opening.start()], body[body.index("</ul>") + len("</ul>"):]
    more = f'<p class="mom-more"><a class="mom-more-link" href="/{section}/videos/">More videos{MORE_ELLIPSIS}</a></p>' if len(items) > shown else ""
    counted = lambda text: re.sub(r'data-count="\d+"', f'data-count="{kept}"', text)
    return counted(before) + counted(opening.group(0)) + "".join(items[:kept]) + "</ul>" + more + after


def _section_findings(found, section: str) -> str:
    """The section front's Findings panel: one row of the section's best findings (never a video), its heading linking to the section's own list of findings. The page
    asks for more than it shows so that videos, which the engine's list cannot leave out yet, can be dropped here."""
    shown, body = int(found.group(1)), found.group(2)
    cards = [tile for tile in TILE_ITEM.findall(body) if not _is_video(tile)]
    if not cards:
        return ""
    address = f"/{section}/findings/"
    row = _reference_rows_html(cards[:shown], [min(len(cards), shown)])
    more = f'<p class="mom-more"><a class="mom-more-link" href="{address}">More findings{MORE_ELLIPSIS}</a></p>' if len(cards) > shown else ""
    head = f'<div class="mom-section-head"><h2 class="mom-section-title"><a class="mom-section-title-link" href="{address}">Findings</a></h2></div>'
    return head + row + more


def _section_conversations(body: str) -> tuple[str, int]:
    """The lines for the section's conversations, drawn as the home page's rail draws them, and how many there are. The include asks the engine for this section's threads
    (its `section` attribute), so a conversation on a Reference in the section is here too."""
    lines = [_thread_to_line(thread) for thread in STOCK_THREAD.finditer(body)]
    return f'<div class="mom-post-lines">{"".join(lines[:CONVERSATION_LINES])}</div>', len(lines)


def _section_front(html: str, page) -> str:
    name = _section_page_name(page)
    if name is None:
        return html
    counted = [0]

    def conversations(found):
        body, counted[0] = _section_conversations(found.group(1))
        return body
    html = SECTION_CONVERSATIONS.sub(conversations, html)
    html = SECTION_VIDEOS.sub(lambda found: _section_videos(found, name), html)
    html = SECTION_FINDINGS.sub(lambda found: _section_findings(found, name), html)
    return html.replace(CONVERSATION_COUNT_MARK, f" · {_count_text(counted[0], 'conversation')}" if counted[0] else "")


# ---------------------------------------------------------------------------------------------- Videos, Findings and a section's own lists
# Papyrus 5.92.0 cannot yet leave References out of a paged list, group them by section, or skip the ones an earlier block placed (Papyrus PPY-a9402d and PPY-2d9715 add
# that). Until then the pages are made from the markup `tools/sync_section_pages.py` generates and this code does the rest, from the engine's own stock tiles:
#
#   * The lead: the best few References in no section, lifted out of the paged list's first page, so the lead and the list can never show the same Reference.
#   * One block per section that has a page here, from a single large include of the whole ranked selection (Videos and Findings only).
#   * The stream: the paged list, with the References that are in a section taken out of its first page and out of every later data file (the data files are drawn
#     through this same hook), so what is left is the References in no section, reached by Load more. None of it has a heading.
# A section with no page here counts as "no section": its References stay in the lead and the stream, with their section chip, so they stay reachable.

LIST_TILE_ITEM = re.compile(r'<li(?: data-key="[^"]*")?>(<article class="home-page-tile".*?</article>)</li>', re.S)
LEAD_MARK = re.compile(r'<!--sf:refs-lead:(\d+)-->')
STREAM_REGION = re.compile(
    r'(<section class="mom-section mom-refs-stream" data-noun="([^"]*)"[^>]*>)\s*<!--sf:refs-stream-->(.*?)(<!--/sf:refs-stream-->\s*</section>)', re.S,
)
BLOCKS_REGION = re.compile(r'<div class="mom-by-section"([^>]*)>(.*?)</div>\s*(?=<section class="mom-section mom-refs-stream")', re.S)
BLOCKS_SOURCE = re.compile(r'<section class="home-page-references"[^>]*>(.*?)</section>', re.S)
LIST_KIND = re.compile(r'data-list-kind="(videos|findings)"')
SOURCE_COUNT = re.compile(r'data-source-count="(\d+)"')
MEDIUM_CHIP = re.compile(r'<span class="home-page-chip" data-kind="medium">')
STREAM_GRID = re.compile(r'(<ul class="home-page-grid"[^>]*data-reference-grid[^>]*>)(.*?)(</ul>)', re.S)
CHUNK_PATH = re.compile(r'^/?reference-lists/(?P<page>[^/]+)/(?P<list>[^/]+)/')
OVERVIEW_PAGES = ("videos", "findings")
OVERVIEW_LIST = "untagged"
SECTION_FINDINGS_PAGE_SUFFIX = "--findings"
LEAD_ROW_SIZES = {0: [], 1: [1], 2: [2], 3: [3], 4: [1, 3]}
NO_SECTION = ""


def _is_filed(tile: str, resolve) -> bool:
    """A Reference is filed when its section is one this site has a page for."""
    chip = SECTION_CHIP.search(tile)
    return bool(chip) and resolve(chip.group(1)) is not None


def _is_video(tile: str) -> bool:
    return bool(MEDIUM_CHIP.search(tile))


def _keeps(list_kind: str, is_overview: bool, resolve):
    """Which tiles a list shows: on Videos and Findings only those in no section, and on any list of findings never a video."""
    def keep(tile: str) -> bool:
        if is_overview and _is_filed(tile, resolve):
            return False
        return not (list_kind == "findings" and _is_video(tile))
    return keep


def _with_section_shown(tile: str) -> str:
    """A Reference left in no section by this site but carrying a section name (one this site has no page for) says that name on its card, so it can be told apart."""
    return tile.replace('data-kind="section">', 'data-kind="section" data-shown="true">')


def _filtered_items(markup: str, keep, show_section: bool = False) -> str:
    """The list items `keep` accepts. On the overview pages the ones left have no section page, and a section name they carry is shown on the card."""
    def item(found):
        if not keep(found.group(1)):
            return ""
        return found.group(0).replace(found.group(1), _with_section_shown(found.group(1))) if show_section else found.group(0)
    return LIST_TILE_ITEM.sub(item, markup)


def _chunk_keep_rule(page, resolve):
    found = CHUNK_PATH.match(str(page.path))
    if not found:
        return None
    name, list_name = found.group("page"), found.group("list")
    if name in OVERVIEW_PAGES and list_name == OVERVIEW_LIST:
        return _keeps(name, True, resolve)
    if name.endswith(SECTION_FINDINGS_PAGE_SUFFIX):
        return _keeps("findings", False, resolve)
    return None


def _is_overview_chunk(page) -> bool:
    found = CHUNK_PATH.match(str(page.path))
    return bool(found) and found.group("page") in OVERVIEW_PAGES and found.group("list") == OVERVIEW_LIST


def _lead_row_sizes(count: int) -> list[int]:
    return LEAD_ROW_SIZES[count]


def _lifted_from_stream(stream_body: str, count: int) -> tuple[str, list[str]]:
    """The stream's first `count` cards (their tile markup) taken out of its grid."""
    cards: list[str] = []

    def lift(found):
        if len(cards) >= count:
            return found.group(0)
        cards.append(found.group(1))
        return ""

    def grid(found):
        return found.group(1) + LIST_TILE_ITEM.sub(lift, found.group(2)) + found.group(3)
    return STREAM_GRID.sub(grid, stream_body, count=1), cards


def _blocks_html(source: str, list_kind: str, resolve, lead_present: bool) -> str:
    """One block per section that has a page, from the whole ranked selection: only the References filed under such a section, in the order given."""
    tiles = [tile for tile in TILE_ITEM.findall(source) if _is_filed(tile, resolve) and not (list_kind == "findings" and _is_video(tile))]
    ranked = _ranked_references("".join(f"<li>{tile}</li>" for tile in tiles))
    sections = _references_by_section(ranked, NO_SECTION)
    noun = list_kind

    def list_href(label):
        found = resolve(label)
        return (found[1], f"{found[0]}{noun}/") if found else None
    return "".join(_reference_section(rank, label, references, noun, list_href, lead_present) for rank, (label, references) in enumerate(sections))


def _chunk_page(html: str, page, resolve) -> str:
    keep = _chunk_keep_rule(page, resolve)
    return html if keep is None else _filtered_items(html, keep, show_section=_is_overview_chunk(page))


def _reference_list_page(html: str, page, resolve) -> str:
    if page.kind == "reference_list":
        return _chunk_page(html, page, resolve)
    found_kind = LIST_KIND.search(html)
    if not found_kind:
        return html
    list_kind = found_kind.group(1)
    blocks = BLOCKS_REGION.search(html)
    keep = _keeps(list_kind, blocks is not None, resolve)
    lead_mark = LEAD_MARK.search(html)
    stream = STREAM_REGION.search(html)

    cards: list[str] = []
    stream_body = stream.group(3) if stream else ""
    if stream:
        stream_body, cards = _lifted_from_stream(_filtered_items(stream_body, keep, show_section=blocks is not None), int(lead_mark.group(1)) if lead_mark else 0)
    lead_present = bool(cards)

    blocks_html, proven_nothing_unfiled = "", False
    if blocks:
        source = BLOCKS_SOURCE.search(blocks.group(2))
        source_tiles = TILE_ITEM.findall(source.group(1)) if source else []
        blocks_html = _blocks_html(source.group(1), list_kind, resolve, lead_present) if source else ""
        budget = int(SOURCE_COUNT.search(blocks.group(1)).group(1)) if SOURCE_COUNT.search(blocks.group(1)) else 0
        proven_nothing_unfiled = bool(source) and len(source_tiles) < budget and not any(keep(tile) for tile in source_tiles)
        html = html.replace(blocks.group(0), blocks_html)

    lead_html = (
        f'<section class="mom-section mom-refs-lead" aria-label="{_e(page.title)}">{_reference_rows_html(cards, _lead_row_sizes(len(cards)))}</section>' if cards else ""
    )
    html = LEAD_MARK.sub(lambda _found: lead_html, html, count=1)

    if stream:
        stream_now = STREAM_REGION.search(html)
        opening, noun, _body, closing = stream_now.groups()
        has_items = bool(LIST_TILE_ITEM.search(stream_body)) or "data-reference-more" in stream_body
        only_the_empty_sentence = "home-page-empty" in stream_body and not has_items and not lead_present and not blocks_html
        keep_region = (has_items or only_the_empty_sentence) and not proven_nothing_unfiled
        html = html[:stream_now.start()] + (f"{opening}{stream_body}</section>" if keep_region else "") + html[stream_now.end():]
    return html

# ---------------------------------------------------------------------------------------------- the forum: /conversations/ and the thread pages
# The conversations page asks the engine for every public thread and this code redraws them as a forum. A board is a section; a board's rows are its conversations,
# newest activity first, and boards are ordered by their latest activity, with the conversations that belong to no section on a last board, "General".
# Which board a conversation is on, in the order of preference:
#   1. The section the thread data names (`section` in `_data/home-page/threads.json`, a Papyrus feature newer than the pinned engine). The engine's card does not carry
#      it yet, so this reads `data-section` on the card (what the engine is expected to print); today it is absent and the next rule decides.
#   2. The section of the Story the conversation is about, found from the Story's address.
#   3. General.
# A board's heading links to its section page only when that page exists. The whole list is in the page; the site script shows the first rows of a board and a
# "Load more" button reveals the rest (without a script every row shows), because the engine pages Reference lists but has no paged list of threads.
FORUM_ROWS_PER_PAGE = 10
GENERAL_BOARD = "General"
GENERAL_BOARD_NOTE = "Conversations that are not about a story in one of our sections."
FORUM_REGION = re.compile(r"<!--sf:forum-->(.*?)<!--/sf:forum-->", re.S)
THREAD_SECTION_ATTRIBUTE = re.compile(r'data-section="([^"]*)"')
THREAD_KEY = re.compile(r"/([0-9a-f]{12})/?$")
THREAD_KIND_PREFIX = re.compile(r"^(?:Story|Reference): ")


class _ForumThread(NamedTuple):
    key: str
    title: str
    href: str
    anchor_kind: str
    anchor_title: str
    anchor_href: str | None
    messages: int
    last_iso: str
    last_text: str
    excerpt: str
    author: str
    section: str


def _forum_threads(markup: str) -> list:
    """The conversations in the engine's cards, with everything a card carries."""
    found = []
    for card in STOCK_THREAD.finditer(markup):
        kind, inner = card.group(1), card.group(2)
        linked = re.search(r'<h3 class="home-page-title"><a href="([^"]*)">(.*?)</a></h3>', inner, re.S)
        if not linked:
            continue
        anchor_link = THREAD_ANCHOR_LINK.search(inner)
        anchor = _plain(_first(r'<p class="home-page-eyebrow home-page-anchor"[^>]*>(.*?)</p>', inner) or "")
        count = _first(r"<span>(\d+) messages?</span>", inner)
        time = re.search(r'<time datetime="([^"]*)">([^<]*)</time>', inner)
        excerpt = _first(r'<p class="home-page-excerpt">(.*?)</p>', inner)
        author = _first(r'<p class="home-page-author">by (.*?)</p>', inner)
        found.append(_ForumThread(
            key=THREAD_KEY.search(unescape(linked.group(1))).group(1) if THREAD_KEY.search(unescape(linked.group(1))) else linked.group(1),
            title=_plain(linked.group(2)), href=unescape(linked.group(1)), anchor_kind=kind, anchor_title=THREAD_KIND_PREFIX.sub("", anchor),
            anchor_href=unescape(anchor_link.group(1)) if anchor_link else None, messages=int(count) if count else 0,
            last_iso=unescape(time.group(1)) if time else "", last_text=unescape(time.group(2)) if time else "",
            excerpt=_plain(excerpt) if excerpt else "", author=_plain(author) if author else "",
            section=unescape(THREAD_SECTION_ATTRIBUTE.search(card.group(0)).group(1)) if THREAD_SECTION_ATTRIBUTE.search(card.group(0)) else "",
        ))
    return found


class _Board(NamedTuple):
    key: str
    name: str
    href: str | None
    description: str


def _board_of_section(page, name: str) -> _Board:
    """The board for a section named by its id (`security`) or its title (`Privacy & Security`): its page's address and description when the section has a page, its configured label otherwise."""
    pages = _section_pages(page)
    found = pages.get(_hashtag_key(name))
    if found:
        address, title = found
        described = next((custom.description for custom in getattr(page.settings, "pages", ()) if f"/{custom.path}/" == address), "")
        return _Board(_hashtag_key(title), title, address, described or "")
    configured = next((section for section in page.settings.sections if _hashtag_key(section.name) == _hashtag_key(name) or _hashtag_key(section.label) == _hashtag_key(name)), None)
    if configured is not None:
        return _Board(_hashtag_key(configured.label), configured.label, None, getattr(configured, "description", "") or "")
    return _Board(_hashtag_key(name), name, None, "")


_GENERAL = _Board("general", GENERAL_BOARD, None, GENERAL_BOARD_NOTE)


def _story_topics(page) -> dict:
    return page.site.memo("story-topics", lambda: {entry.url: entry.topic for entry in page.entries if entry.url and entry.topic}) if page.site is not None else {entry.url: entry.topic for entry in page.entries if entry.url and entry.topic}


def _board_of_thread(page, thread: _ForumThread) -> _Board:
    if thread.section:
        return _board_of_section(page, thread.section)
    topic = _story_topics(page).get(thread.anchor_href) if thread.anchor_kind == "story" and thread.anchor_href else None
    return _board_of_section(page, topic) if topic else _GENERAL


def _forum_boards(page, threads: list) -> list:
    """`[(board, threads newest first)]`, boards by their latest activity, General last."""
    grouped: dict = {}
    for thread in threads:
        board = _board_of_thread(page, thread)
        grouped.setdefault(board.key, (board, []))[1].append(thread)
    for _, members in grouped.values():
        members.sort(key=lambda thread: (thread.last_iso, thread.key), reverse=True)
    latest = lambda entry: entry[1][0].last_iso
    named = sorted((entry for entry in grouped.values() if entry[0].key != _GENERAL.key), key=latest, reverse=True)
    return named + ([grouped[_GENERAL.key]] if _GENERAL.key in grouped else [])


def _forum_row(thread: _ForumThread, position: int) -> str:
    return mom.forum_row(
        title=thread.title, href=thread.href, messages=thread.messages, anchor_kind=thread.anchor_kind, anchor_title=thread.anchor_title, anchor_href=thread.anchor_href,
        author=thread.author, excerpt=thread.excerpt, last_iso=thread.last_iso, last_text=thread.last_text, later=position >= FORUM_ROWS_PER_PAGE,
    )


BOARD_PAGE_PREFIX = "sectionconversations-"
MOST_ACTIVE_COUNT = 5


def _board_page_section(page) -> str | None:
    """The id of the section whose board page this is (`/security/conversations/` is `security`), or None."""
    custom = getattr(page, "custom_id", None) or ""
    return custom[len(BOARD_PAGE_PREFIX):] if page.kind == "custom" and custom.startswith(BOARD_PAGE_PREFIX) else None


def _forum_card() -> str:
    """The site card in the forum's side column. It is the only copy on the page: below the width where the side column fits, the stylesheet moves it between two boards."""
    return f'<div class="mom-forum-card">{_site_card(heading_level=None)}</div>'


def _forum_panel(title: str, items: list) -> str:
    """A compact panel in the side column: a title and a list of `(href, text, detail)`."""
    entries = "".join(f'<li><a href="{_e(href)}">{_e(text)}</a><span>{_e(detail)}</span></li>' for href, text, detail in items)
    return f'<section class="mom-forum-panel"><h2 class="mom-forum-panel-title">{_e(title)}</h2><ol>{entries}</ol></section>'


def _forum_index_body(page, markup: str, only: _Board | None = None) -> str:
    """The forum: the side column (the site card, the counts, the most active conversations) and the boards. On a board page `only` is the one board, and every thread the engine
    printed is on it."""
    threads = _forum_threads(markup)
    if not threads:
        return f'<div class="mom-forum mom-forum-empty" data-boards="1"><div class="mom-forum-aside">{_forum_card()}</div><div class="mom-forum-boards">{markup}</div></div>' if only else markup
    if only is not None:
        boards = [(only, sorted(threads, key=lambda thread: (thread.last_iso, thread.key), reverse=True))]
    else:
        boards = _forum_boards(page, threads)
    newest = max(threads, key=lambda thread: (thread.last_iso, thread.key))
    messages = sum(thread.messages for thread in threads)
    totals = f'<span>{mom.lucide_icon("layout-list")}{_count_text(len(boards), "board")}</span>' if only is None else ""
    strip = (
        '<div class="mom-forum-strip">'
        f'<p class="mom-forum-totals">{totals}'
        f'<span>{mom.lucide_icon("message-square")}{_count_text(len(threads), "conversation")}</span><span>{mom.lucide_icon("message-circle")}{_count_text(messages, "message")}</span></p>'
        f'<p class="mom-forum-recent">{mom.lucide_icon("clock")}<span>Recently active: <a href="{_e(newest.href)}">{_e(newest.title)}</a> {mom.when_markup(newest.last_iso, newest.last_text)}</span></p></div>'
    )
    busiest = sorted(threads, key=lambda thread: (thread.messages, thread.last_iso, thread.key), reverse=True)[:MOST_ACTIVE_COUNT]
    panel = _forum_panel("Most active", [(thread.href, thread.title, _count_text(thread.messages, "message")) for thread in busiest])
    rendered = "".join(
        mom.forum_board(
            f"mom-board-{board.key}", board.name, board.href, board.description, len(members), members[0].last_iso, members[0].last_text,
            "".join(_forum_row(thread, position) for position, thread in enumerate(members)), min(FORUM_ROWS_PER_PAGE, len(members)),
            more_html=(f'<p class="mom-more"><a class="mom-more-link" href="{_e(board.href)}conversations/">More {_e(board.name)} conversations{MORE_ELLIPSIS}</a></p>'
                       if only is None and board.href and len(members) > FORUM_ROWS_PER_PAGE else ""),
        )
        for board, members in boards
    )
    return (
        f'<div class="mom-forum" data-rows-per-page="{FORUM_ROWS_PER_PAGE}" data-boards="{len(boards)}">'
        f'<div class="mom-forum-aside">{_forum_card()}{strip}{panel}</div><div class="mom-forum-boards">{rendered}</div></div>'
    )


def _forum_index(html: str, page) -> str:
    if page.kind != "custom":
        return html
    section = _board_page_section(page)
    if getattr(page, "custom_id", None) != "conversations" and section is None:
        return html
    only = _board_of_section(page, section) if section else None
    return FORUM_REGION.sub(lambda found: _forum_index_body(page, found.group(1), only), html)


THREAD_PAGE = re.compile(
    r'<div class="markus-document home-page-thread-page"><header class="home-page-thread-header">(?P<anchor><div class="home-page-thread-anchor".*?</div>)'
    r'<h1 class="home-page-thread-title">(?P<title>.*?)</h1><p class="home-page-thread-meta">(?P<meta>.*?)</p></header>'
    r'<ol class="home-page-message-list">(?P<messages>.*)</ol></div>', re.S,
)
THREAD_MESSAGE = re.compile(
    r'<li><article class="home-page-message" id="(?P<id>[^"]*)"><header class="home-page-message-head">'
    r'<span class="home-page-author-name" data-author-kind="(?P<kind>[^"]*)">(?P<icon><svg.*?</svg>)<span>(?P<name>.*?)</span></span>'
    r'(?P<time><time datetime="(?P<iso>[^"]*)">(?P<text>[^<]*)</time>)?(?P<edited><span class="home-page-edited">.*?</span>)?</header>'
    r'<div class="home-page-message-text">(?P<body>.*?)</div></article></li>', re.S,
)


def _forum_post(found, number: int) -> str:
    handle = found.group("kind") == "handle"
    name = found.group("name")
    role = "Reader" if handle else None
    if handle:
        author = f'<span class="mom-post-handle">{found.group("icon")}<span>{name}</span></span><span class="mom-author mom-author-reader">{role}</span>'
    else:
        tone = mom.THREAD_AUTHOR_ROLES.get(_plain(name), "reader")
        author = f'<span class="mom-author mom-author-{tone} mom-post-role">{found.group("icon")}<span>{name}</span></span>'
    when = mom.when_markup(unescape(found.group("iso") or ""), unescape(found.group("text") or ""), "mom-when") if found.group("iso") else ""
    return (
        f'<li><article class="mom-post" id="{found.group("id")}"><aside class="mom-post-author">{author}'
        f'<a class="mom-post-number" href="#{found.group("id")}">#{number}</a></aside>'
        f'<div class="mom-post-main"><header class="mom-post-head">{when}{found.group("edited") or ""}</header><div class="mom-post-text">{found.group("body")}</div></div></article></li>'
    )


def _thread_board(page) -> _Board:
    thread = getattr(page, "thread", None) or {}
    if thread.get("section"):
        return _board_of_section(page, str(thread["section"]))
    anchor = thread.get("anchor") or {}
    topic = _story_topics(page).get(anchor.get("url")) if anchor.get("kind") == "story" else None
    return _board_of_section(page, topic) if topic else _GENERAL


def _thread_facts(board: _Board, messages: list) -> str:
    """The thread page's side panel on a wide window: the board it is on, how many posts and voices, when it started and when it was last active. (Narrower windows hide it:
    the header already says what the conversation discusses.)"""
    if not messages:
        return ""
    voices = len({_plain(message.group("name")) for message in messages})
    first, last = messages[0], messages[-1]
    when = lambda message: mom.when_markup(unescape(message.group("iso") or ""), unescape(message.group("text") or ""), "mom-when") if message.group("iso") else ""
    board_link = f'<a href="{_e(board.href)}conversations/">{_e(board.name)}</a>' if board.href else _e(board.name)
    rows = (
        ("Board", board_link), ("Posts", str(len(messages))), ("Voices", str(voices)),
        ("Started", when(first)), ("Last post", when(last)),
    )
    items = "".join(f"<div><dt>{label}</dt><dd>{value}</dd></div>" for label, value in rows if value)
    return f'<aside class="mom-topic-facts" aria-label="About this conversation"><h2 class="mom-forum-panel-title">About this conversation</h2><dl>{items}</dl></aside>'


def _forum_thread(html: str, page) -> str:
    """A thread page as a forum topic: breadcrumb to the board, the title and what it discusses, then the posts in order, each with an author block and its number."""
    if page.kind != "thread":
        return html

    def topic(found):
        board = _thread_board(page)
        board_crumb = f'<a href="{_e(board.href)}">{_e(board.name)}</a>' if board.href else f"<span>{_e(board.name)}</span>"
        chevron = mom.lucide_icon("chevron-right")
        crumbs = f'<nav class="mom-crumbs" aria-label="Breadcrumb"><a href="{CONVERSATIONS_PATH}">Conversations</a>{chevron}{board_crumb}</nav>'
        messages = list(THREAD_MESSAGE.finditer(found.group("messages")))
        posts = "".join(_forum_post(message, number) for number, message in enumerate(messages, start=1))
        facts = _thread_facts(board, messages)
        return (
            f'<div class="markus-document home-page-thread-page mom-topic">{crumbs}<header class="home-page-thread-header mom-topic-head">'
            f'<h1 class="home-page-thread-title">{found.group("title")}</h1>'
            f'<div class="mom-topic-about"><p class="mom-topic-about-label">Discussing</p>{found.group("anchor")}</div>'
            f'<p class="home-page-thread-meta">{found.group("meta")}</p></header><ol class="mom-posts">{posts}</ol>{facts}</div>'
        )
    return THREAD_PAGE.sub(topic, html, count=1)


SOCIAL_IMAGE_META = re.compile(r'(<meta (?:property|name)="(?:og|twitter):image" content=")([^"]*)(")')


def _social_image_url(address: str) -> str:
    """The address a link preview fetches, made one the site serves. A story's stored picture can be written as `media/assets/<slug>/<file>`, which the page
    turned into `/media/assets/...` (nothing is served there: the file is at `/assets/...`), and a relative `../../assets/...` came out as an address with
    dots in its path. Only this site's own addresses are corrected; a picture hosted elsewhere is left as it is."""
    found = urlsplit(unescape(address))
    if not found.netloc or found.netloc != SITE_HOST:
        return address
    parts = []
    for part in found.path.split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part not in ("", "."):
            parts.append(part)
    if parts[:2] == ["media", "assets"]:
        parts = parts[1:]
    return urlunsplit((found.scheme, found.netloc, "/" + "/".join(parts), found.query, ""))


def _social_image_urls(html: str) -> str:
    return SOCIAL_IMAGE_META.sub(lambda found: found.group(1) + _e(_social_image_url(found.group(2))) + found.group(3), html)


def page_finish(html, page):
    resolve = _section_resolver(page)
    html = _social_image_urls(html)
    html = _section_front(html, page)
    html = _forum_index(html, page)
    html = _forum_thread(html, page)
    html = _rail_conversations(html)
    html = _home_groups(html, resolve)
    html = _home_videos(html)
    html = _home_ad_cards(html, page)
    html = _home_conversations(html)
    html = _band_midway(html)
    html = _more_links_say_what(html)
    html = _home_findings(html)
    html = _most_connected_first(html)
    html = _unlabel_concept_chips(html)
    html = _reference_list_page(html, page, resolve)
    html = STOCK_TILE.sub(_tile_to_reference_card, html)
    return STOCK_THREAD.sub(_thread_to_thread_card, html)


# ---------------------------------------------------------------------------------------------- blocks

SAMPLE_PROPOSALS = (
    ("Placeholder proposal: explain how judges are chosen", 4, "Open for editors", False),
    ("Placeholder proposal: add a wiki term for trace grading", 2, "Open for editors", False),
    ("Placeholder proposal: merge two stories on durable execution", 1, "Approved", True),
)


def _proposal_rows_html() -> str:
    rows = "".join(mom.proposal_row(title, "#", net, state, approved) for title, net, state, approved in SAMPLE_PROPOSALS)
    return f'<div class="mom-proposal-list">{rows}</div>'


def _gallery_advertisements() -> list[str]:
    ads = _advertisements()
    return [mom.advertisement(unit, ad, placement=f"gallery-{unit}") for ad in ads for unit in mom.ad_units(ad)]


GALLERY_SAMPLE_PARAGRAPHS = (
    "This is a sample of an article's words, set exactly as a story is set, so the room around an in-text ad can be seen at every width.",
    "The aside floats to the right of the words after the second paragraph. The words keep a gutter beside it and below it, and never run into it.",
    "On a phone there is no room to flow words beside a box, so the aside takes the column's full width, with the words above and below it.",
    "A real article chooses its one ad from its address, so the same page always shows the same ad, and two advertisers take turns across the site.",
    "Every ad says Advertisement and names its advertiser, and every link in it is marked sponsored, so nobody mistakes it for the publication's own words.",
    "What is inside an ad is the advertiser's own picture; the site draws only the label and the slot around it, so an ad never passes for a story or a quote that an editor chose.",
)


def _gallery_aside_samples() -> str:
    """The aside ad in a sample of article text, once per advertiser, so its gutter can be reviewed and measured in the reading column."""
    samples = []
    for ad in [ad for ad in _advertisements() if "aside" in mom.ad_units(ad)]:
        paragraphs = [f"<p>{_e(text)}</p>" for text in GALLERY_SAMPLE_PARAGRAPHS]
        paragraphs.insert(2, mom.advertisement("aside", ad, placement="article-aside"))
        samples.append(f'<div class="mom-gallery-article"><article class="mom-article"><div class="mom-article-body"><article class="markus-document">{"".join(paragraphs)}</article></div></article></div>')
    return "".join(samples)


def _gallery_html() -> str:
    def section(title: str, body: str) -> str:
        return f'<section class="mom-gallery-section"><h2 class="mom-panel-head">{_e(title)}</h2><div class="mom-gallery-row">{body}</div></section>'

    papers = mom.card_image(None, "", "https://arxiv.org/abs/0000.00000", kind="paper")
    arts = "".join(mom.card_image(None, "", seed) for seed in ("seed-one", "seed-two", "seed-three", "seed-four", "seed-five", "seed-six"))
    return "".join((
        section("Wordmark", mom.wordmark("inline") + mom.wordmark("stacked", size="48px")),
        section("Sticker", mom.sticker(tagline=TAGLINE, heading_level=2)),
        section("Provenance chips", mom.provenance_chips([("machine", "Accepted by Cyclotron"), ("human", "Editor’s pick"), ("brand", "Machines on Machines")])),
        section("Buttons and nav pills", mom.button("Steer this story") + mom.button("Read the findings", "/findings/", "brand") + mom.button("Suggest an edit", None, "quiet") + mom.nav_pill("Wire", "/findings/", True)),
        section("Loop bands", mom.loop_band("brand") + mom.loop_band("machine", ["#DurableExecution", "#AgentEvals"], 4, "Rising fast") + mom.loop_band("human", ["#Accountability"], 8, "Editors are watching")),
        section("Placeholder art", arts + papers),
        section("Story cards", mom.story_card("Who owns an agent’s mistakes?", "#", "A person wrote this one, so the label says so.", "Papyrus", "30 Oct 2026", provenance=[("human", "Written by Sam Rivera"), ("human", "Editor’s pick")]) + mom.story_card("Durable execution", "#", "Agents survive a crash.", "How-To", size="small", provenance=[("machine", "Accepted by Cyclotron"), ("human", "Editor’s pick")])),
        section("Reference cards", mom.reference_card("Judges that grade themselves", "https://arxiv.org/abs/0000.00000", "accepted", "cyclotron", "A paper on judges that share training data.", host="arxiv.org", meta_date="30 Oct 2026") + mom.reference_card("A benchmark that rewrites its own questions", "https://example.test/post", "recommended", None, "Not yet accepted.", host="example.test", meta_date="30 Oct 2026", confidence=0.91)),
        section("Thread cards", mom.thread_card("Is a judge that shares training data still a judge?", "#", "Reference: Judges that grade themselves", "AI", "The overlap is about a third.", 2, "30 Oct 2026") + mom.thread_card("What counts as a crash?", "#", "Story: Durable execution", "Editor", "Are a restart and a crash the same?", 1, "29 Oct 2026")),
        section("Proposal rows", _proposal_rows_html()),
        section("Wire and wiki cards", mom.wire_card("Judges that grade themselves", "#", "Papyrus", "arxiv.org", 0.93) + mom.wiki_card("Durable execution", "#", 12, "Resume a long program where it stopped.")),
        section("Advertisements", "".join(_gallery_advertisements())),
        section("An aside ad in an article's words", _gallery_aside_samples()),
        section("Pull quote", mom.pull_quote("Who grades the graders?")),
        section("Spine", f'<div class="mom-gallery-spine">{mom.spine("Research", 0.4, "/", "#")}</div>'),
    ))


# ---------------------------------------------------------------------------------------------- the Articles and Posts pages
# The Articles page is the articles and the Posts page is the posts, nothing else on either. Sections are ranked by how recently they were updated, and the layout
# thins out as the rank grows. These numbers are the only place the tiers are defined; the CSS reads the tier name.
ARTICLE_TYPE, POST_TYPE = "article", "post"
# What the stories with no section are called, by the type the page shows
UNSECTIONED_LABELS = {ARTICLE_TYPE: "More stories", POST_TYPE: "More posts"}
TIER_FEATURE, TIER_WIDE, TIER_PLAIN = "feature", "wide", "plain"
FEATURE_TIER_RANKS = 1   # rank 0 only: the first section (the one holding the best-ranked Story) has a large feature, drawn like a home page solo card
WIDE_TIER_RANKS = 3      # ranks 1 and 2: one feature card across two columns, then a grid
# Stories shown per section, by tier. A section with more says how many it has. Every count fills whole rows.
STORIES_SHOWN = {TIER_FEATURE: 7, TIER_WIDE: 8, TIER_PLAIN: 6}
STORIES_PER_ROW = 3


def _story_tier(rank: int) -> str:
    if rank < FEATURE_TIER_RANKS:
        return TIER_FEATURE
    return TIER_WIDE if rank < WIDE_TIER_RANKS else TIER_PLAIN


def _recency(entry) -> str:
    return str(entry.updated or entry.date or "")


def _stories_by_section(entries, story_type: str, rank=None) -> list[tuple[str, list]]:
    """The Stories of one type grouped by section, in the order the home page ranks them. `rank` is `page.ranked` (Papyrus core's Story ranking: the rolling
    recency bucket first, then the editors' stars inside it); without it, or with nothing rated, the order is newest first (by the date of the last update).
    Sections come in the order of their best-ranked Story, so a section holding a five-star Story rises, and the Stories inside a section keep the ranked order.
    Stories with no section come last."""
    unsectioned = UNSECTIONED_LABELS[story_type]
    stories = sorted((entry for entry in entries if entry.type == story_type and entry.url), key=_recency, reverse=True)
    sections: dict[str, list] = {}
    for entry in (rank(stories) if rank is not None else stories):
        sections.setdefault(_topic_label(entry) or unsectioned, []).append(entry)
    ranked = [(label, found) for label, found in sections.items() if label != unsectioned]
    return ranked + ([(unsectioned, sections[unsectioned])] if unsectioned in sections else [])


def _row_sizes(count: int) -> list[int]:
    """Row lengths for a grid of cards, each row a whole row at any width: threes, then a row of two (or two rows of two) for what is left."""
    sizes = [STORIES_PER_ROW] * (count // STORIES_PER_ROW)
    left = count % STORIES_PER_ROW
    if left == 1 and sizes:
        sizes[-1:] = [2, 2]
    elif left:
        sizes.append(left)
    return sizes


def _stories_rows(tier: str, count: int) -> list[list[str]]:
    """The rows of one section, each a list of card roles: feature (large, beside its picture), wide (two columns), plain, or solo (the one card of a row, drawn beside its picture)."""
    shown = min(count, STORIES_SHOWN[tier])
    if shown == 1:
        return [["solo"]]
    rows: list[list[str]] = []
    if tier == TIER_FEATURE:
        rows.append(["feature"]) if shown > 2 else rows.append(["feature", "plain"])
        grid = shown - len(rows[0])
    elif tier == TIER_WIDE:
        rows.append(["wide", "plain"])
        grid = shown - 2
    else:
        grid = shown
    rows.extend([["plain"] * size for size in _row_sizes(grid)])
    return [["solo"] if row == ["plain"] else row for row in rows]


def _stories_more_href(stories, resolve) -> str | None:
    """A section's own page, when there is one: one of the section pages, or a section the site declares with a listing. A Story's topic is not always a section with an address."""
    found = resolve(stories[0].topic)
    if found:
        return found[0]
    for entry in stories:
        if entry.section is not None and not entry.section.is_type and getattr(entry.section, "base", None):
            return f"/{entry.section.base}/"
    return None


def _stories_head(label: str, total: int, shown: int, href: str | None) -> str:
    """The section's title, a link to the section's page when it has one, and how many stories it has when not all are shown."""
    more = f'<span class="papyrus-group-more">{total} stories</span>' if total > shown else ""
    return f'<header class="papyrus-group-head"><h2 class="mom-section-title">{_linked_title(_e(label), href)}</h2>{more}</header>'


def _stories_section(rank: int, label: str, stories: list, resolve) -> str:
    tier = _story_tier(rank)
    rows = _stories_rows(tier, len(stories))
    shown = sum(len(row) for row in rows)
    cards = iter(stories[:shown])
    blocks = []
    for row in rows:
        row_cards = []
        for role in row:
            extra = {"feature": "rh-large rh-first rh-solo", "solo": "rh-large rh-solo", "wide": "rh-large rh-first rh-wide", "plain": "rh-large"}[role]
            row_cards.append(_story_card(next(cards), "large", extra))
        columns = len(row) + 1 if "wide" in row else len(row)
        blocks.append(f'<div class="papyrus-group rh-group mom-stories-row" data-count="{columns}">{"".join(row_cards)}</div>')
    href = _stories_more_href(stories, resolve)
    return (
        f'<section class="mom-section mom-stories-section" aria-label="{_e(label)}" data-rank="{rank}" data-tier="{tier}">'
        f'{_stories_head(label, len(stories), shown, href)}{"".join(blocks)}{_more_link(label, href) if shown > 1 else ""}</section>'
    )


ARTICLES_LEAD = "Every article from Machines on Machines, by section."
POSTS_LEAD = LISTING_LEADS["Posts"]
# The type listings the projector draws, and the sectioned page each one gets: its Story type and its lead
SECTIONED_LISTINGS = {f"type:{ARTICLE_TYPE}": (ARTICLE_TYPE, ARTICLES_LEAD), f"type:{POST_TYPE}": (POST_TYPE, POSTS_LEAD)}
# Stories was the old name of the Articles page; its old address shows a notice that sends readers on
MOVED_PAGES = {"/stories/": "/articles/"}
EMPTY_TEXT = "Nothing has been published here yet."


def _sectioned_page(entries, story_type: str, title: str, lead: str, resolve, rank=None) -> str:
    """The page for one Story type: the shared page header, then one block per section, the section with the best-ranked Story first. The Articles page and the Posts page both come from here."""
    top = _page_top(title, f'<p class="mom-dek">{_e(lead)}</p>')
    sections = _stories_by_section(entries, story_type, rank)
    if not sections:
        return f'<div class="mom-page mom-section-page">{top}<p class="mom-empty">{_e(EMPTY_TEXT)}</p></div>'
    blocks = "".join(_stories_section(rank, label, stories, resolve) for rank, (label, stories) in enumerate(sections))
    return f'<div class="mom-page mom-section-page mom-stories">{top}{blocks}</div>'


# ---------------------------------------------------------------------------------------------- Findings and Videos, grouped by section
# A Reference's section is the newsroom section it is filed under: the snapshot carries its name and the stock tile prints it as a chip. The References come from one
# include, already in the home page's order (the site's rolling bucket, then an editor's stars, then the crowd's prediction, then the newest), so grouping keeps that order
# inside each section. Sections are ordered by their most recently updated Reference, and thin out by the same tiers. A Reference filed under no section is
# never given one: those come last, named for the page.
REFERENCES_SHOWN = {TIER_FEATURE: 7, TIER_WIDE: 6, TIER_PLAIN: 3}   # whole rows: a feature then two rows of three, two rows of three, one row of three
TILE_ITEM = re.compile(r'<li>(<article class="home-page-tile".*?</article>)</li>', re.S)
SECTION_CHIP = re.compile(r'<span class="home-page-chip" data-kind="section">(.*?)</span>', re.S)
ACCEPTED_AT = re.compile(r'Accepted <time datetime="([^"]*)"')
MEDIUM_ATTRIBUTE = re.compile(r'data-medium="([^"]*)"')


class _RankedReference(NamedTuple):
    section: str    # the section's name as the stock tile printed it (already escaped), "" when the Reference has none
    accepted: str   # when it was accepted, ISO 8601
    markup: str     # the stock tile, which `page_finish` draws as our card afterwards


def _ranked_references(items_html: str) -> list[_RankedReference]:
    references = []
    for tile in TILE_ITEM.findall(items_html):
        chip, accepted = SECTION_CHIP.search(tile), ACCEPTED_AT.search(tile)
        references.append(_RankedReference(chip.group(1) if chip else "", accepted.group(1) if accepted else "", tile))
    return references


def _references_by_section(references, unsectioned: str) -> list[tuple[str, list]]:
    """References grouped by section, each in the order given. `references` arrive in the site's one ranked order (this week's first, then an editor's stars, then
    the crowd's prediction), so a section is placed where its best Reference sits in that order: the first card on the page is the best-ranked one. A section
    is not placed by how recently it was accepted into, which would put a section of three-star items above one holding the week's five-star items.
    References with no section come last under `unsectioned` and are never given one."""
    sections: dict[str, list] = {}
    for reference in references:
        sections.setdefault(reference.section or unsectioned, []).append(reference)
    ranked = [(label, found) for label, found in sections.items() if label != unsectioned]   # dicts keep first appearance, which is the best Reference's place
    return ranked + ([(unsectioned, sections[unsectioned])] if unsectioned in sections else [])


def _reference_row_sizes(tier: str, count: int) -> list[int]:
    """Row lengths for one section's References: the best one on a row of its own as a feature (top tier, when a few follow it), then rows of whole threes."""
    shown = min(count, REFERENCES_SHOWN[tier])
    if tier == TIER_FEATURE and shown > STORIES_PER_ROW:
        return [1] + _row_sizes(shown - 1)
    return _row_sizes(shown)


def _reference_rows_html(cards: list[str], sizes: list[int]) -> str:
    """Each row is its own list, so its data-count (the cards in it) sets its columns and the row is full at any width."""
    queue = iter(cards)
    rows = []
    for size in sizes:
        items = "".join(f"<li>{next(queue)}</li>" for _ in range(size))
        rows.append(f'<ul class="home-page-grid mom-refs-row" data-card="tile" data-count="{size}">{items}</ul>')
    return "".join(rows)


def _more_list_link(title: str, noun: str, href: str) -> str:
    return f'<p class="mom-more"><a class="mom-more-link" href="{_e(href)}">More {_e(title)} {noun}{MORE_ELLIPSIS}</a></p>'


def _reference_section(rank: int, label: str, references: list, noun: str, list_href, lead_present: bool) -> str:
    """One section's block on Videos or Findings: its best few References, the title linking to the section's own list, and "More <Title> <noun>…" when the section has more."""
    tier = _story_tier(rank + (1 if lead_present else 0))
    sizes = _reference_row_sizes(tier, len(references))
    shown = sum(sizes)
    found = list_href(label)
    title, href = found if found else (unescape(label), None)
    more = _more_list_link(title, noun, href) if href and len(references) > shown else ""
    return (
        f'<section class="mom-section mom-refs-section" aria-label="{_e(title)}" data-rank="{rank}" data-tier="{tier}">'
        f'<header class="papyrus-group-head"><h2 class="mom-section-title">{_linked_title(_e(title), href)}</h2></header>'
        f'{_reference_rows_html([reference.markup for reference in references[:shown]], sizes)}{more}</section>'
    )


def _section_name(attributes) -> str:
    return attributes["section"]


def _section_block(name, attributes, page):
    section = _section_name(attributes)
    articles = len(_section_stories(page, section, ARTICLE_TYPE))
    posts = len(_section_stories(page, section, POST_TYPE))
    part = attributes.get("part")
    if name == "section-top":
        counts = " · ".join(text for text in (_count_text(articles, "article") if articles else "", _count_text(posts, "post") if posts else "") if text)
        return (
            f'<div class="mom-section-head rh-label"><h1 class="mom-section-title">{_e(page.title)}</h1>'
            f'<p class="mom-meta mom-sf-counts">{counts}{CONVERSATION_COUNT_MARK}</p></div>'
        )
    if name == "section-sticker":
        return _home_card(page.description, heading_level=None)
    heading, total, address = {
        "articles": ("Articles", articles, ARTICLES_PATH_FORMAT), "posts": ("Posts", posts, POSTS_PATH_FORMAT),
    }[part]
    if name == "section-heading":
        return f'<div class="mom-section-head"><h2 class="mom-section-title">{heading}</h2></div>' if total else ""
    shown = int(attributes["shown"])
    return f'<p class="mom-more"><a class="mom-more-link" href="{_e(address.format(section=section))}">More {heading.lower()}{MORE_ELLIPSIS}</a></p>' if total > shown else ""


def _home_card(purpose: str, heading_level: int | None = 1) -> str:
    """The site title card with a sentence under it: the home page's card, and the section pages' card (whose heading is the section's name)."""
    return f'<div class="mom-home-card mom-site-card-slot">{_site_card(heading_level)}<p class="mom-home-purpose">{_e(purpose)}</p></div>'


def block(name, attributes, page):
    if name == "ad":
        return _advertisement_html(page, attributes.get("unit", "band"), int(attributes.get("slot", 0)), attributes.get("placement"))
    if name.startswith("section-"):
        return _section_block(name, attributes, page)
    if name == "sticker":
        return _home_card(HOME_PURPOSE)
    if name == "home-concepts":
        return _home_concepts(page)
    if name == "page-top":
        lead = attributes.get("lead")
        return _page_top(attributes["title"], f'<p class="mom-dek">{_e(lead)}</p>' if lead else "", card=attributes.get("card") != "none")
    if name == "loop-band":
        role = attributes.get("role", "brand")
        words = attributes.get("words", "").split() or None
        return mom.loop_band(role, words, 4, attributes.get("label"), speed=float(attributes.get("speed", 1)))
    if name == "proposal-rows":
        return _proposal_rows_html()
    if name == "component-gallery":
        return _gallery_html()
    raise ValueError(f"unknown block {name!r}")
