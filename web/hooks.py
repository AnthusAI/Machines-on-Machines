"""Machines on Machines named hooks for the standard Papyrus front end (projection.json names this module).

The design system lives in `design/system/`; its components are ported to Python in `mom_components.py`, a sibling module
this file imports. This file decides where each component goes: the masthead, the footer, the cards, the section
page, the article page with its spine, the wiki term page, and the blocks the authored pages place.

Provenance is data, never assumed. A story says "Drafted by AI" only when its front matter says an agent drafted it, and
"Approved by <name>" only when it carries an approval; a story with neither says nothing about who made it.
"""

from __future__ import annotations

import re
from datetime import date
from html import escape, unescape

import mom_components as mom

SITE_NAME = "Machines on Machines"
TAGLINE = "Information About Information Systems"
WIKI_SECTION = "wiki"
WIKI_TYPE = "wiki_page"
WIKI_SUBJECT = "Meaning"
CONVERSATIONS_PATH = "/conversations/"
WIRE_PATH = "/wire/"
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

TOKEN_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")
HASHTAG = re.compile(r"(?<![\w&/#])#([A-Za-z][A-Za-z0-9]*)")
HTML_TAG_SPLIT = re.compile(r"(<[^>]*>)")
MARKUS_HEADER = re.compile(r'<header class="markus-header">.*?</header>', re.S)
CITATION_LIST_WITH_ITEMS = '<ol class="citationslist"><li'
BODY_OPENS_WITH_FIGURE = re.compile(r"\s*<article\b[^>]*>\s*(?:<style>.*?</style>\s*)?<figure\b", re.S)
PLAIN_BLOCKQUOTE = re.compile(r"<blockquote>\s*<p>([^<]*)</p>\s*</blockquote>", re.S)
STOCK_TILE = re.compile(r'<article class="home-page-tile" data-status="([^"]*)">(.*?)</article>', re.S)
STOCK_THREAD = re.compile(r'<article class="home-page-thread" data-anchor="([^"]*)">(.*?)</article>', re.S)
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


STORIES_PER_SECTION = 6
# The projection knows a section's id but not the name the newsroom gives it.
TOPIC_LABELS = {"security": "Privacy & Security", "law-policy": "Law & Policy"}


def _topic_label(entry) -> str:
    """The Story's section, a topic, and never the type its address is grouped under."""
    if entry.section is not None and not entry.section.is_type:
        return entry.section.label
    return TOPIC_LABELS.get(entry.topic, entry.topic.replace("-", " ").title()) if entry.topic else ""


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


def _byline(entry) -> str:
    """Bots write a story unless it names its human authors; an editor who approved it joins the byline."""
    if entry.authors and str(_dict(entry.data.get("drafting")).get("by", "")).lower() not in AGENT_DRAFTERS:
        return "By " + ", ".join(_public_author_names(entry.authors))
    approval = _dict(entry.data.get("approval"))
    if approval.get("status") != "approved":
        return "By various bots"
    return f"By various bots and {approval.get('by') or 'an editor'}"


def _provenance(entry) -> list[tuple[str, str]]:
    """The provenance chips of a story, from its front matter only: who drafted it, who approved it, whether it is an editor's pick."""
    data = entry.data
    chips = []
    drafting = _dict(data.get("drafting"))
    if str(drafting.get("by", "")).lower() in AGENT_DRAFTERS:
        chips.append(("machine", "Drafted by AI"))
    elif entry.authors:
        chips.append(("human", "Written by " + ", ".join(_public_author_names(entry.authors))))
    approval = _dict(data.get("approval"))
    if approval.get("status") == "approved":
        chips.append(("human", f"Approved by {approval['by']}" if approval.get("by") else "Approved by an editor"))
    if _truthy(data.get("editorsPick")):
        chips.append(("human", "Editor’s pick"))
    edited = _dict(data.get("edited"))
    if str(edited.get("by", "")).lower() in AGENT_DRAFTERS and edited.get("on"):
        chips.append(("machine", f"Edited by AI on {_date_text(edited['on'])}"))
    return chips


def _wiki_chips(entry) -> list[tuple[str, str]]:
    review = _dict(entry.data.get("review"))
    when = _date_text(review.get("on"))
    if review.get("actor") == "human":
        who = review.get("name") or "an editor"
        return [("human", f"Reviewed by {who} on {when}")]
    if review.get("actor") == "ai":
        return [("machine", f"Edited by AI on {when}"), ("quiet", "Draft, not yet reviewed")]
    return [("quiet", "Draft, not yet reviewed")]


def _chips_html(chips) -> str:
    if not chips:
        return ""
    parts = []
    for role, label in chips:
        parts.append(f'<span class="mom-chip mom-chip-quiet">{_e(label)}</span>' if role == "quiet" else mom.provenance_chip(role, label))
    return '<span class="mom-chip-row">' + "".join(parts) + "</span>"


# ---------------------------------------------------------------------------------------------- cards

def _story_card(entry, size: str = "large", extra_class: str | None = None) -> str:
    meta_parts = [_date_text(entry.date)]
    meta_parts.insert(0, _byline(entry))
    return mom.story_card(
        headline=entry.title, href=entry.url or entry.link or "#", blurb=entry.summary_text or None, kicker=_topic_label(entry) or None,
        meta=" · ".join(part for part in meta_parts if part) or None, image=entry.image, image_seed=entry.url or entry.title,
        provenance=_provenance(entry), size=size, class_name=extra_class,
    )


def _wiki_entry_card(entry) -> str:
    relation = str(entry.data.get("kind") or "").strip() or None
    return mom.wiki_card(entry.title, entry.url or "#", relation=relation.title() if relation else None, definition=entry.summary_text or None)


def card(entry, page, variant=None, index=0):
    if _is_wiki(entry):
        return _wiki_entry_card(entry)
    if variant == "line":
        return f'<a class="mom-post-line" href="{_e(entry.url or "#")}"><span class="mom-post-line-title">{_e(entry.title)}</span><span class="mom-meta">{_e(_date_text(entry.date))}</span></a>'
    if variant == "small":
        return _story_card(entry, "small")
    if variant == "lead":
        return _story_card(entry, "large", "mom-story-card-lead")
    return _story_card(entry)


# ---------------------------------------------------------------------------------------------- chrome

def head_extra(page):
    return f'<meta name="color-scheme" content="light dark">\n<script src="{SCRIPT_PATH}" defer></script>'


def body_class(page):
    return f"mom mom-{page.kind}"


def _is_active(href: str, path: str) -> bool:
    if href == "/":
        return path == "/"
    return path.rstrip("/").startswith(href.rstrip("/"))


def masthead(page):
    pills = "".join(mom.nav_pill(link.label, link.href, _is_active(link.href, page.path)) for link in page.settings.nav)
    shows_brand_pill = page.kind not in ("home", "item")
    brand_pill = f'<a class="mom-brand-pill" href="/" aria-label="{SITE_NAME}, home">{mom.wordmark("inline")}</a>' if shows_brand_pill else ""
    return f'  <header class="mom-masthead"><nav class="mom-nav" aria-label="Site">{brand_pill}{pills}</nav></header>'


def footer(page):
    links = (
        ("Findings", WIRE_PATH), ("Conversations", CONVERSATIONS_PATH), ("About", "/about/"), ("Corrections", "/corrections/"), ("RSS", FEED_PATH),
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
    html = PLAIN_BLOCKQUOTE.sub(lambda found: mom.pull_quote(unescape(found.group(1)).strip()), html)
    return _link_hashtags(html, _wiki_terms(site)) if site is not None else html


# ---------------------------------------------------------------------------------------------- pages

def _body_of(page) -> str:
    return MARKUS_HEADER.sub("", page.fragment, count=1)


def _article_hero(entry, body: str) -> str:
    """The article's picture. A body that opens with a figure already has one. Without one, the seeded placeholder art is a slim band: cards need the full-size art, a reading page does not."""
    if BODY_OPENS_WITH_FIGURE.match(body):
        return ""
    if entry.image:
        return f'<div class="mom-article-hero">{mom.card_image(entry.image, "", entry.url or entry.title, class_name="mom-ratio-wide")}</div>'
    return f'<div class="mom-article-hero mom-article-hero-band">{mom.card_image(None, "", entry.url or entry.title, class_name="mom-ratio-band")}</div>'


def _article_main(page) -> str:
    entry = page.entry
    section = entry.section
    subject = _topic_label(entry) or "Machines"
    subtitle = _subtitle(entry)
    section_href = f"/{section.base}/" if section is not None else "/"
    meta = " · ".join(
        part for part in (_byline(entry), _date_text(entry.date)) if part
    )
    terms = _wiki_terms(page.site)
    hashtags = _hashtags_html(entry, terms)
    body = _body_of(page)
    topic = _topic_label(entry)
    kicker = f'<a class="mom-kicker" href="{_e(section_href)}">{_e(topic)}</a>' if topic else ""
    actions = mom.article_actions(entry.url, entry.title, page.settings.identity.production_url or "") if entry.url else ""
    return (
        '<div class="mom-article-layout">'
        '<article class="mom-article">'
        f'<header class="mom-article-header"><div class="mom-article-eyebrow">{kicker}{actions}</div>{_chips_html(_provenance(entry))}'
        f'<h1 class="mom-headline">{_e(entry.title)}</h1>'
        + (f'<p class="mom-dek">{_e(subtitle)}</p>' if subtitle else "")
        + (f'<p class="mom-meta">{_e(meta)}</p>' if meta else "")
        + "</header>"
        f'{_article_hero(entry, body)}'
        f'<div class="mom-article-body">{_with_end_matter(body, _see_also_html(entry, page, terms))}</div>'
        f"{hashtags}</article>"
        f'{mom.spine(subject=subject, home_href="/", section_href=section_href)}'
        "</div>"
    )


def _see_also_html(entry, page, terms: dict) -> str:
    """The concepts tagged to a story that have a wiki page, the ones the most stories use first. Nothing at all when there are none."""
    concepts = [tag for tag in entry.tags if _hashtag_key(tag) in terms]
    if not concepts:
        return ""
    concepts.sort(key=lambda tag: (-len(_stories_using(page, _hashtag_key(tag))), tag.casefold()))
    items = "".join(f'<li><a class="mom-hashtag" href="{_e(terms[_hashtag_key(tag)])}">#{_e(tag)}</a></li>' for tag in concepts)
    return f'<section class="mom-see-also"><h2 id="see-also">See also</h2><ul class="mom-hashtags">{items}</ul></section>'


def _with_end_matter(body: str, see_also: str) -> str:
    """Puts See also and the References heading before the citation list, each only when it has something under it."""
    list_start = body.find(CITATION_LIST_WITH_ITEMS)
    if list_start >= 0:
        return f'{body[:list_start]}{see_also}<h2 id="references">References</h2>{body[list_start:]}'
    if not see_also:
        return body
    document_end = body.rfind("</article>")
    return f"{body[:document_end]}{see_also}{body[document_end:]}" if document_end >= 0 else body + see_also


def _hashtags_html(entry, terms: dict) -> str:
    items = [f'<li><span class="mom-hashtag">#{_e(tag)}</span></li>' for tag in entry.tags if _hashtag_key(tag) not in terms]
    if not items:
        return ""
    return f'<ul class="mom-hashtags" aria-label="Hashtags">{"".join(items)}</ul>'


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
    return (
        '<div class="mom-article-layout mom-wiki-layout">'
        '<article class="mom-article mom-wiki-term">'
        f'<header class="mom-article-header"><a class="mom-kicker" href="/{WIKI_SECTION}/">Machines on {WIKI_SUBJECT}</a>{_chips_html(_wiki_chips(entry))}'
        f'<h1 class="mom-term"><span class="mom-term-hash" aria-hidden="true">#</span>{_e(entry.title)}</h1></header>'
        + (superseded.group(0) if superseded else "")
        + f'<div class="mom-article-body mom-wiki-body">{_body_of(page)}</div>'
        f"{stories_html}{page.wiki_footer}</article>"
        f'{mom.spine(subject=WIKI_SUBJECT, home_href="/", section_href=f"/{WIKI_SECTION}/")}'
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


def _site_card(subject: str = "Machines", description: str = "") -> str:
    """The one site title card every page uses. It says what its page is about, or the site's tagline when nothing narrower applies."""
    if description:
        return mom.sticker(subject=subject, tagline=description, tagline_variant="text", heading_level=1, class_name="mom-sticker-fit")
    return mom.sticker(subject=subject, tagline=TAGLINE if subject == "Machines" else None, heading_level=1, class_name="mom-sticker-fit")


def _listing_main(page) -> str:
    view = page.listing
    if view is None:
        return None
    section = next((candidate for candidate in page.settings.sections if candidate.name == view.section), None)
    is_wiki = view.section == WIKI_SECTION
    if page.kind == "tag":
        subject = f"#{view.label}"
    else:
        subject = WIKI_SUBJECT if is_wiki else _listing_subject(section, view.label)
    description = section.description if section is not None and page.kind == "listing" else ""
    entries = view.featured + view.entries
    cards = "".join(card(entry, page) for entry in entries)
    grid_class = "mom-wiki-grid" if is_wiki else "mom-story-grid"
    pager = page.components.pager(view.page, view.pages, view.url_for_page) if view.pages > 1 else ""
    bands = "" if is_wiki or view.page != 1 else _topic_bands(view.all_entries)
    intro = page.fragment if page.fragment and not is_wiki else ""
    sticker = _site_card(subject, description)
    if cards and not intro:
        return (
            f'<div class="mom-page mom-section-page">{bands}'
            f'<div class="{grid_class}"><div class="mom-grid-sticker">{sticker}</div>{cards}</div>'
            f"{pager}</div>"
        )
    return (
        '<div class="mom-page mom-section-page">'
        f'<header class="mom-section-hero">{sticker}'
        + (f'<div class="mom-section-intro">{intro}</div>' if intro else "")
        + f"</header>{bands}"
        + (f'<div class="{grid_class}">{cards}</div>' if cards else '<p class="mom-empty">Nothing has been published here yet.</p>')
        + f"{pager}</div>"
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
    return mom.reference_card(
        title=title, href=href, status=status, actor=actor, image=unescape(image) if image else None, host=_plain(host) if host else None,
        meta_date=(accepted or published).group(1) if (accepted or published) else None,
        confidence=int(percent) / 100 if percent else None,
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


def page_finish(html, page):
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


def _gallery_html() -> str:
    def section(title: str, body: str) -> str:
        return f'<section class="mom-gallery-section"><h2 class="mom-panel-head">{_e(title)}</h2><div class="mom-gallery-row">{body}</div></section>'

    papers = mom.placeholder_art("https://arxiv.org/abs/0000.00000", kind="paper", class_name="mom-ratio-wide")
    arts = "".join(mom.placeholder_art(seed, class_name="mom-ratio-wide") for seed in ("seed-one", "seed-two", "seed-three", "seed-four", "seed-five", "seed-six"))
    return "".join((
        section("Wordmark", mom.wordmark("inline") + mom.wordmark("stacked", size="48px")),
        section("Sticker", mom.sticker(tagline=TAGLINE, heading_level=2)),
        section("Provenance chips", mom.provenance_chips([("machine", "Drafted by AI"), ("human", "Approved by Ada Reader"), ("brand", "Machines on Machines")])),
        section("Buttons and nav pills", mom.button("Steer this story") + mom.button("Read the wire", "/wire/", "brand") + mom.button("Suggest an edit", None, "quiet") + mom.nav_pill("Wire", "/wire/", True)),
        section("Loop bands", mom.loop_band("brand") + mom.loop_band("machine", ["#DurableExecution", "#AgentEvals"], 4, "Rising fast") + mom.loop_band("human", ["#Accountability"], 8, "Editors are watching")),
        section("Placeholder art", arts + papers),
        section("Story cards", mom.story_card("Who owns an agent’s mistakes?", "#", "A person wrote this one, so the label says so.", "Papyrus", "30 Oct 2026", provenance=[("human", "Written by Sam Rivera"), ("human", "Editor’s pick")]) + mom.story_card("Durable execution", "#", "Agents survive a crash.", "How-To", size="small", provenance=[("machine", "Drafted by AI"), ("human", "Approved by Ada Reader")])),
        section("Reference cards", mom.reference_card("Judges that grade themselves", "https://arxiv.org/abs/0000.00000", "accepted", "cyclotron", "A paper on judges that share training data.", host="arxiv.org", meta_date="30 Oct 2026") + mom.reference_card("A benchmark that rewrites its own questions", "https://example.test/post", "recommended", None, "Not yet accepted.", host="example.test", meta_date="30 Oct 2026", confidence=0.91)),
        section("Thread cards", mom.thread_card("Is a judge that shares training data still a judge?", "#", "Reference: Judges that grade themselves", "AI", "The overlap is about a third.", 2, "30 Oct 2026") + mom.thread_card("What counts as a crash?", "#", "Story: Durable execution", "Editor", "Are a restart and a crash the same?", 1, "29 Oct 2026")),
        section("Proposal rows", _proposal_rows_html()),
        section("Wire and wiki cards", mom.wire_card("Judges that grade themselves", "#", "Papyrus", "arxiv.org", 0.93) + mom.wiki_card("Durable execution", "#", "Topic", "Resume a long program where it stopped.")),
        section("Pull quote", mom.pull_quote("Who grades the graders?")),
        section("Spine", f'<div class="mom-gallery-spine">{mom.spine("Research", 0.4, "/", "#")}</div>'),
    ))


def _stories_by_section(entries) -> list[tuple[str, list]]:
    """Articles grouped by their section, the section with the most recent update first."""
    sections: dict[str, list] = {}
    for entry in entries:
        if entry.type == "article" and entry.url:
            sections.setdefault(_topic_label(entry) or "More stories", []).append(entry)
    return sorted(sections.items(), key=lambda section: max(str(entry.updated or entry.date or "") for entry in section[1]), reverse=True)


def _stories_page(page) -> str:
    sections = _stories_by_section(page.entries)
    if not sections:
        return f'<div class="mom-page mom-section-page"><header class="mom-section-hero">{_site_card()}</header><p class="mom-empty">Nothing has been published here yet.</p></div>'
    blocks = []
    for position, (label, entries) in enumerate(sections):
        sticker = f'<div class="mom-grid-sticker">{_site_card()}</div>' if position == 0 else ""
        cards = "".join(_story_card(entry) for entry in entries[:STORIES_PER_SECTION])
        blocks.append(f'<section class="mom-section" aria-label="{_e(label)}"><h2 class="mom-section-title">{_e(label)}</h2><div class="mom-story-grid">{sticker}{cards}</div></section>')
    return f'<div class="mom-page mom-section-page">{"".join(blocks)}</div>'


def block(name, attributes, page):
    if name == "sticker":
        return _site_card()
    if name == "stories-by-section":
        return _stories_page(page)
    if name == "loop-band":
        role = attributes.get("role", "brand")
        return mom.loop_band(role, None, 4, attributes.get("label"), speed=float(attributes.get("speed", 1)))
    if name == "proposal-rows":
        return _proposal_rows_html()
    if name == "component-gallery":
        return _gallery_html()
    raise ValueError(f"unknown block {name!r}")
