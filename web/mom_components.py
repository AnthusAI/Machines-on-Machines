"""The Machines on Machines design-system components as Python, for the Papyrus hooks.

Each function emits the same markup and `mom-` class names as the reference React components in
`design/system/components/bundle.js`, so `design/system/components/bundle.css` styles them unchanged.
Every text argument is escaped here; every `*_html` argument is trusted markup built by this module.
The seeded choice of placeholder art is the same algorithm as `choosePlaceholderArt` in `bundle.js`
(32-bit FNV-1a over the UTF-8 bytes of the seed), and tests prove the two agree.
"""

from __future__ import annotations

import re
from html import escape
from urllib.parse import urlencode

KNOWN_ROLES = ("brand", "machine", "human")
PLACEHOLDER_SHAPE_COUNTS = {"sun-slab": 2, "rising": 1, "eclipse": 1, "moon": 1, "horizon": 1, "pages": 3}
GENERAL_PLACEHOLDER_COMPOSITIONS = ("sun-slab", "rising", "eclipse", "moon", "horizon")
PLACEHOLDER_TONES = KNOWN_ROLES
RESEARCH_PAPER_HOSTS = (
    "arxiv.org", "openreview.net", "aclanthology.org", "proceedings.mlr.press", "papers.nips.cc",
    "proceedings.neurips.cc", "dl.acm.org", "ieeexplore.ieee.org", "semanticscholar.org", "biorxiv.org",
)
PDF_LOCATION_PATTERN = re.compile(r"\.pdf($|[?#])")
FNV_OFFSET_BASIS = 0x811C9DC5
FNV_PRIME = 0x01000193
UNSIGNED_32_BIT_MASK = 0xFFFFFFFF
METER_SEGMENT_COUNT = 5
SPINE_NAME_PREFIX_CHARACTERS = len("Machines on ")

REFERENCE_STATUS_LABELS = {
    "accepted-human": (None, "human"),   # an editor's acceptance is the normal case and says nothing a reader can use, so it has no chip
    "accepted-cyclotron": ("Accepted by Cyclotron", "machine"),
    "accepted-agent": ("Accepted by AI", "machine"),
    "accepted-rule": ("Accepted by a rule", "machine"),
    "accepted-automatic": ("Accepted automatically", "machine"),
    "recommended": ("Recommended by Cyclotron, not yet accepted", "pending"),
}
THREAD_AUTHOR_ROLES = {"AI": "machine", "Editor": "human"}


def _text(value) -> str:
    return escape("" if value is None else str(value), quote=True)


def join_class_names(*names) -> str:
    return " ".join(name for name in names if name)


def role_or_default(role, fallback_role) -> str:
    return role if role in KNOWN_ROLES else fallback_role


def clamp_between_zero_and_one(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number or number in (float("inf"), float("-inf")):
        return 0.0
    return max(0.0, min(1.0, number))


def js_round(value: float) -> int:
    """`Math.round` semantics (halves round up), not Python's banker's rounding."""
    return int(value + 0.5) if value >= 0 else -int(-value + 0.5)


def wordmark(layout: str = "inline", subject: str = "Machines", tag: str = "span", size: str | None = None, class_name: str | None = None) -> str:
    classes = join_class_names("mom-wordmark", f"mom-wordmark-{layout}", class_name)
    style = f' style="font-size: {_text(size)}"' if size else ""
    return f'<{tag} class="{classes}"{style}><span>Machines</span><span class="mom-wordmark-on">on</span><span>{_text(subject)}</span></{tag}>'


def provenance_chip(role: str, label: str, class_name: str | None = None) -> str:
    classes = join_class_names("mom-chip", f"mom-chip-{role_or_default(role, 'machine')}", class_name)
    return f'<span class="{classes}">{_text(label)}</span>'


def provenance_chips(chips) -> str:
    """A row of chips from `(role, label)` pairs; nothing when there are none."""
    if not chips:
        return ""
    return '<span class="mom-chip-row">' + "".join(provenance_chip(role, label) for role, label in chips) + "</span>"


def button(label: str, href: str | None = None, variant: str = "human", button_type: str = "button", class_name: str | None = None) -> str:
    chosen_variant = variant if variant in ("brand", "quiet") else "human"
    classes = join_class_names("mom-button", f"mom-button-{chosen_variant}", class_name)
    if href:
        return f'<a class="{classes}" href="{_text(href)}">{_text(label)}</a>'
    return f'<button class="{classes}" type="{_text(button_type)}">{_text(label)}</button>'


def nav_pill(label: str, href: str = "#", active: bool = False, class_name: str | None = None) -> str:
    classes = join_class_names("mom-nav-pill", "mom-nav-pill-active" if active else None, class_name)
    current = ' aria-current="page"' if active else ""
    return f'<a class="{classes}" href="{_text(href)}"{current}>{_text(label)}</a>'


MENU_ID = "mom-menu"


def menu_button(controls: str = MENU_ID) -> str:
    """The hamburger. A real button; the script shows it when some destinations do not fit in the bar, and the menu panel is what it opens."""
    return (
        f'<button type="button" class="mom-menu-button" aria-label="Menu" aria-expanded="false" aria-controls="{_text(controls)}">'
        f'{MENU_ICON}{CLOSE_ICON}</button>'
    )


def menu_panel(destinations, panel_id: str = MENU_ID) -> str:
    """The full-page menu: one big block per destination with its name and a subtitle. `destinations` are `(label, href, subtitle, active)` tuples.

    Hidden until the script opens it. The current page carries `aria-current="page"` and the words "You are here", so it is not marked by colour alone."""
    rows = []
    for label, href, subtitle, active in destinations:
        current = ' aria-current="page"' if active else ""
        here = '<span class="mom-menu-here">You are here</span>' if active else ""
        sub = f'<span class="mom-menu-sub">{_text(subtitle)}</span>' if subtitle else ""
        rows.append(
            f'<li><a class="mom-menu-link" href="{_text(href)}"{current}>'
            f'<span class="mom-menu-head"><span class="mom-menu-name">{_text(label)}</span>{here}</span>{sub}</a></li>'
        )
    return f'<nav class="mom-menu" id="{_text(panel_id)}" aria-label="Site menu" hidden><ul class="mom-menu-list">{"".join(rows)}</ul></nav>'


def sticker(subject: str = "Machines", tagline: str | None = None, tagline_variant: str = "display", flat: bool = False,
            heading_level: int | None = None, actions_html: str = "", class_name: str | None = None) -> str:
    classes = join_class_names("mom-sticker", "mom-sticker-flat" if flat else None, class_name)
    tag = f"h{heading_level}" if heading_level else "span"
    tagline_html = f'<p class="mom-sticker-tagline mom-sticker-tagline-{_text(tagline_variant)}">{_text(tagline)}</p>' if tagline else ""
    actions = f'<div class="mom-sticker-actions">{actions_html}</div>' if actions_html else ""
    return (
        f'<div class="{classes}"><div class="mom-sticker-backing" aria-hidden="true"></div>'
        f'<div class="mom-sticker-face">{wordmark("stacked", subject, tag)}{tagline_html}{actions}</div></div>'
    )


def spine(subject: str = "Machines", home_href: str = "/", section_href: str = "#", class_name: str | None = None) -> str:
    return (
        f'<nav class="{join_class_names("mom-spine", class_name)}" aria-label="Site and section" style="--mom-spine-characters: {SPINE_NAME_PREFIX_CHARACTERS + len(str(subject))}">'
        '<div class="mom-spine-content">'
        f'<a class="mom-spine-home" href="{_text(home_href)}" aria-label="Machines on Machines, home">{wordmark("stacked")}</a>'
        f'<a class="mom-spine-section" href="{_text(section_href)}">{wordmark("vertical", subject)}</a>'
        "</div></nav>"
    )


def loop_band(role: str = "brand", words=None, repeat: int = 4, label: str | None = None, offset: float = 0,
              speed: float | None = None, class_name: str | None = None) -> str:
    chosen_role = role_or_default(role, "brand")
    word_pattern = list(words) if words else ["Machines", "on", "Machines", "on"]
    repeated_words = word_pattern * repeat
    spans = []
    for word in repeated_words:
        word_kind = "on" if word == "on" else "tag" if word[:1] == "#" else "word"
        spans.append(f'<span class="mom-band-{word_kind}">{_text(word)}</span>')
    speed_attribute = (f' data-speed="{speed:g}"' if speed is not None else "") + f' data-repeat="{repeat}"'
    label_html = f'<span class="mom-band-label">{_text(label)}</span>' if label else ""
    offset_text = f"{offset:g}"
    return (
        f'<div class="{join_class_names("mom-band", f"mom-band-{chosen_role}", class_name)}"{speed_attribute}>'
        f'<div class="mom-band-row" aria-hidden="true" style="transform: translateX({offset_text}px)">{"".join(spans)}</div>{label_html}</div>'
    )


def hash_seed_to_unsigned_integer(seed) -> int:
    hash_value = FNV_OFFSET_BASIS
    for byte in str("" if seed is None else seed).encode("utf-8"):
        hash_value ^= byte
        hash_value = (hash_value * FNV_PRIME) & UNSIGNED_32_BIT_MASK
    return hash_value


def is_research_paper_location(location) -> bool:
    if not location:
        return False
    normalized_location = str(location).lower()
    if PDF_LOCATION_PATTERN.search(normalized_location):
        return True
    return any(paper_host in normalized_location for paper_host in RESEARCH_PAPER_HOSTS)


def choose_placeholder_art(seed, kind: str | None = None) -> tuple[str, str]:
    """The composition and tone for a seed: the same answer as `choosePlaceholderArt` in bundle.js."""
    hash_value = hash_seed_to_unsigned_integer(seed)
    composition = "pages" if kind == "paper" else GENERAL_PLACEHOLDER_COMPOSITIONS[hash_value % len(GENERAL_PLACEHOLDER_COMPOSITIONS)]
    tone = PLACEHOLDER_TONES[(hash_value >> 8) % len(PLACEHOLDER_TONES)]
    return composition, tone


def media_frame(content: str, class_name: str | None = None) -> str:
    """The slot an image sits in. It is the image's container: the stylesheet reads its width to give the image a 16:9 height that is a whole number of rhythm units. Layout classes (grid placement, width) go on the frame, never on the image."""
    return f'<span class="{join_class_names("mom-media", class_name)}">{content}</span>'


def placeholder_art(seed, kind: str | None = None, tone: str | None = None, composition: str | None = None, class_name: str | None = None) -> str:
    chosen_composition, chosen_tone = choose_placeholder_art(seed, kind)
    final_composition = composition if composition in PLACEHOLDER_SHAPE_COUNTS else chosen_composition
    final_tone = tone if tone in KNOWN_ROLES else chosen_tone
    shapes = "".join(f'<span class="mom-art-shape mom-art-shape-{index}"></span>' for index in range(1, PLACEHOLDER_SHAPE_COUNTS[final_composition] + 1))
    classes = join_class_names("mom-card-image", "mom-art", f"mom-art-{final_composition}", f"mom-art-tone-{final_tone}", class_name)
    return f'<span class="{classes}" aria-hidden="true" data-composition="{final_composition}" data-tone="{final_tone}">{shapes}</span>'


def card_image(src: str | None, alt: str = "", seed=None, kind: str | None = None, tone: str | None = None,
               composition: str | None = None, class_name: str | None = None, image_dark: str | None = None, square: bool = False) -> str:
    """The card's image in its frame, or `PlaceholderArt` when there is none. The image is always 16:9; `square=True` makes the one other shape, a small square thumbnail. `class_name` goes on the frame. An image that fails to load is swapped for the same art by `assets/mom.js`. With a Night version it draws both and the stylesheet shows the one the theme calls for."""
    return media_frame(_card_image_content(src, alt, seed, kind, tone, composition, image_dark, "mom-card-image-square" if square else None), class_name)


def _card_image_content(src, alt, seed, kind, tone, composition, image_dark, shape_class) -> str:
    if src:
        classes = join_class_names("mom-card-image", shape_class)
        kind_attribute = f' data-art-kind="{_text(kind)}"' if kind else ""
        def picture(path: str) -> str:
            return f'<img class="{classes}" src="{_text(path)}" alt="{_text(alt)}" loading="lazy" data-art-seed="{_text(seed)}"{kind_attribute}>'
        if image_dark:
            return f'<span class="mom-card-image-day">{picture(src)}</span><span class="mom-card-image-night">{picture(image_dark)}</span>'
        return picture(src)
    return placeholder_art(seed, kind, tone, composition, shape_class)


def story_card(headline: str, href: str = "#", blurb: str | None = None, kicker: str | None = None, meta: str | None = None,
               image: str | None = None, image_alt: str = "", image_seed=None, image_tone: str | None = None,
               provenance=None, size: str = "large", class_name: str | None = None, image_dark: str | None = None) -> str:
    chosen_size = "small" if size == "small" else "large"
    seed = image_seed or href or headline
    parts = [
        card_image(image, image_alt, seed, tone=image_tone, image_dark=image_dark),
        f'<span class="mom-kicker">{_text(kicker)}</span>' if kicker else "",
        provenance_chips(provenance),
        f'<span class="mom-story-card-headline">{_text(headline)}</span>',
        f'<span class="mom-blurb">{_text(blurb)}</span>' if blurb else "",
        f'<span class="mom-meta">{_text(meta)}</span>' if meta else "",
    ]
    classes = join_class_names("mom-story-card", f"mom-story-card-{chosen_size}", class_name)
    return f'<a class="{classes}" href="{_text(href)}">{"".join(parts)}</a>'


ACCEPTANCE_PREDICTIONS = ("Very unlikely to be accepted", "Unlikely to be accepted", "May be accepted", "Likely to be accepted", "Very likely to be accepted")


def confidence_meter(confidence) -> str:
    """How likely Cyclotron thinks an editor is to accept this, on five steps in words. It's a prediction, not a rating of the source, so it uses segments rather than stars and shows no percentage."""
    filled_segment_count = min(int(clamp_between_zero_and_one(confidence) * METER_SEGMENT_COUNT) + 1, METER_SEGMENT_COUNT)
    prediction = ACCEPTANCE_PREDICTIONS[filled_segment_count - 1]
    segments = "".join(
        '<span class="mom-meter-segment mom-meter-segment-filled"></span>' if index < filled_segment_count else '<span class="mom-meter-segment"></span>'
        for index in range(METER_SEGMENT_COUNT)
    )
    return (
        f'<span class="mom-meter"><span class="mom-meter-track" role="img" aria-label="Prediction: {filled_segment_count} of {METER_SEGMENT_COUNT}">{segments}</span>'
        f'<span class="mom-meter-label">{prediction}</span></span>'
    )


def reference_status(status: str | None, actor: str | None) -> tuple[str | None, str]:
    if status == "recommended":
        return REFERENCE_STATUS_LABELS["recommended"]
    return REFERENCE_STATUS_LABELS.get(f"accepted-{actor}", REFERENCE_STATUS_LABELS["accepted-automatic"])


STAR_POINTS = "12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"


def star_rating(stars) -> str:
    """Filled and outlined Lucide stars, so the count reads by shape, with the count in words for screen readers."""
    count = max(0, min(5, int(stars)))
    marks = "".join(
        f'<svg class="mom-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="{"currentColor" if position < count else "none"}" '
        f'stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true" focusable="false" data-icon="star"><polygon points="{STAR_POINTS}"/></svg>'
        for position in range(5)
    )
    return f'<span class="mom-stars" role="img" aria-label="{count} of 5 stars">{marks}</span>'


def reference_card(title: str, href: str = "#", status: str | None = None, actor: str | None = None, summary: str | None = None,
                   image: str | None = None, image_seed=None, image_tone: str | None = None, site_name: str | None = None,
                   host: str | None = None, meta_date: str | None = None, confidence=None, kind: str | None = None,
                   stars=None, class_name: str | None = None, section: str | None = None) -> str:
    label, role = reference_status(status, actor)
    seed = image_seed or href or title
    chosen_kind = kind or ("paper" if is_research_paper_location(href) or is_research_paper_location(host) else None)
    site_html = f'<span class="mom-reference-card-site">{_text(site_name)}</span>' if site_name else ""
    meter = confidence_meter(confidence) if confidence is not None and status == "recommended" else ""
    rating = star_rating(stars) if stars and status != "recommended" else ""
    meta = " · ".join(part for part in (host, section, meta_date) if part)
    status_html = f'<span class="mom-reference-status mom-reference-status-{role}">{_text(label)}</span>' if label else ""
    return (
        f'<a class="{join_class_names("mom-reference-card", class_name)}" href="{_text(href)}">'
        f'<span class="mom-reference-card-media">{card_image(image, "", seed, chosen_kind, image_tone)}{site_html}</span>'
        + status_html
        + f'<span class="mom-reference-card-title">{_text(title)}</span>'
        + (f'<span class="mom-reference-card-summary">{_text(summary)}</span>' if summary else "")
        + rating
        + meter
        + f'<span class="mom-meta">{_text(meta)}</span></a>'
    )


def thread_card(title: str, href: str = "#", anchor: str | None = None, author: str | None = None, latest: str | None = None,
                messages: int | None = None, last_at: str | None = None, image: str | None = None, image_seed=None,
                image_tone: str | None = None, class_name: str | None = None) -> str:
    author_role = THREAD_AUTHOR_ROLES.get(author or "", "reader")
    seed = image_seed or href or title
    latest_html = (
        f'<span class="mom-thread-card-latest"><span class="mom-author mom-author-{author_role}">{_text(author)}</span><span>{_text(latest)}</span></span>'
        if latest else ""
    )
    meta = " · ".join(part for part in ((f"{messages} message" if messages == 1 else f"{messages} messages") if messages is not None else None, last_at) if part)
    # A conversation with no title of its own is titled after what it's about, so saying that twice adds nothing
    repeats_title = anchor and anchor.split(": ", 1)[-1].strip() == title.strip()
    anchor_html = f'<span class="mom-meta mom-thread-card-anchor">{_text(anchor)}</span>' if anchor and not repeats_title else ""
    return (
        f'<a class="{join_class_names("mom-thread-card", class_name)}" href="{_text(href)}">'
        f'{anchor_html}<span class="mom-thread-card-title">{_text(title)}</span>{card_image(image, "", seed, tone=image_tone, class_name="mom-thread-card-thumb", square=True)}'
        f'{latest_html}<span class="mom-meta mom-thread-card-meta">{_text(meta)}</span></a>'
    )


# ---------------------------------------------------------------------------------------------- forum (the conversations pages)
# A forum is boards (a section each), and a board is rows (a conversation each). Marks are Lucide icons with words beside them, never colour alone.

LUCIDE_PATHS = {
    "message-square": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "message-circle": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "external-link": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "layout-list": '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/><path d="M14 4h7"/><path d="M14 9h7"/><path d="M14 15h7"/><path d="M14 20h7"/>',
}


def lucide_icon(name: str) -> str:
    return (
        '<svg class="mom-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" data-icon="{name}">{LUCIDE_PATHS[name]}</svg>'
    )


def count_phrase(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def reply_phrase(replies: int) -> str:
    return f"{replies} reply" if replies == 1 else f"{replies} replies"


def when_markup(iso: str | None, text: str | None, class_name: str = "mom-when") -> str:
    """A time as the page can write it with no script: the date as given, the exact moment in the title; the site script rewrites the text as "2h ago"."""
    if not iso:
        return f'<span class="{class_name}">{_text(text)}</span>' if text else ""
    exact = re.sub(r"^(\d{4})-(\d\d)-(\d\d)T(\d\d:\d\d).*$", r"\1-\2-\3 \4 UTC", iso)
    return f'<time class="{class_name}" datetime="{_text(iso)}" title="{_text(exact)}">{_text(text or iso[:10])}</time>'


def forum_row(title: str, href: str, messages: int, anchor_kind: str | None = None, anchor_title: str | None = None, anchor_href: str | None = None,
              author: str | None = None, excerpt: str | None = None, last_iso: str | None = None, last_text: str | None = None, later: bool = False) -> str:
    """One conversation in a board: a mark, the title with what it is about and the latest message, and the numbers on the right."""
    replies = max(messages - 1, 0)
    mark = "message-square" if replies else "message-circle"
    mark_words = "Has replies" if replies else "No replies yet"
    about = ""
    if anchor_title:
        kind_icon = "file-text" if anchor_kind == "story" else "link"
        linked = f'<a href="{_text(anchor_href)}">{_text(anchor_title)}</a>' if anchor_href else _text(anchor_title)
        about = f'<p class="mom-meta mom-forum-about">{lucide_icon(kind_icon)}<span>On: {linked}</span></p>'
    role = THREAD_AUTHOR_ROLES.get(author or "", "reader")
    latest = ""
    if excerpt:
        by = f'<span class="mom-author mom-author-{role}">{_text(author)}</span>' if author else ""
        latest = f'<p class="mom-forum-latest">{by}<span class="mom-forum-excerpt">{_text(excerpt)}</span></p>'
    last_by = f'<span class="mom-meta mom-forum-last-by">Latest from {_text(author)}</span>' if author else ""
    return (
        f'<li class="mom-forum-row"{" data-later" if later else ""}>'
        f'<span class="mom-forum-mark" title="{mark_words}">{lucide_icon(mark)}<span class="mom-forum-words">{mark_words}</span></span>'
        f'<div class="mom-forum-main"><a class="mom-forum-title" href="{_text(href)}">{_text(title)}</a>{about}{latest}</div>'
        f'<div class="mom-forum-numbers"><span class="mom-forum-replies">{reply_phrase(replies)}</span>'
        f'{when_markup(last_iso, last_text, "mom-when mom-forum-when")}{last_by}</div></li>'
    )


def forum_board(board_id: str, name: str, href: str | None, description: str | None, conversations: int, last_iso: str | None, last_text: str | None, rows_html: str,
                shown_first: int, more_html: str = "") -> str:
    """A board: a heading row (the section's name, linked to its page when it has one), then its conversations, newest activity first, then `more_html` (a link to the rest)."""
    title = f'<a href="{_text(href)}">{_text(name)}</a>' if href else _text(name)
    note = f'<p class="mom-forum-board-note">{_text(description)}</p>' if description else ""
    active = when_markup(last_iso, last_text, "mom-when")
    return (
        f'<section class="mom-forum-board" aria-labelledby="{_text(board_id)}" data-shown="{shown_first}">'
        f'<header class="mom-forum-board-head"><div class="mom-forum-board-name"><h2 id="{_text(board_id)}" class="mom-forum-board-title">{title}</h2>{note}</div>'
        f'<p class="mom-forum-board-stats"><span>{count_phrase(conversations, "conversation")}</span><span class="mom-forum-active">Last activity {active}</span></p></header>'
        f'<ol class="mom-forum-rows">{rows_html}</ol>{more_html}</section>'
    )


VOTE_ICON = (
    '<svg class="mom-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" data-icon="arrow-up-down">'
    '<path d="m21 16-4 4-4-4"/><path d="M17 20V4"/><path d="m3 8 4-4 4 4"/><path d="M7 4v16"/></svg>'
)


def proposal_row(title: str, href: str = "#", net=0, state: str | None = None, approved: bool = False, class_name: str | None = None) -> str:
    """A proposal and its net votes. Reader voting is closed, so the count is read-only: a Lucide arrow-up-down icon and the signed number in words."""
    try:
        net_votes = int(net)
    except (TypeError, ValueError):
        net_votes = 0
    signed_votes = f"+{net_votes}" if net_votes > 0 else str(net_votes)
    state_chip = ""
    if state:
        state_chip = f'<span class="mom-chip {"mom-chip-human" if approved else "mom-chip-quiet"}">{_text(state)}</span>'
    return (
        f'<div class="{join_class_names("mom-proposal-row", class_name)}">'
        f'<span class="mom-proposal-row-text"><a class="mom-proposal-row-title" href="{_text(href)}">{_text(title)}</a>'
        f'<span class="mom-chip-row">{provenance_chip("machine", "Proposed by AI")}{state_chip}</span></span>'
        f'<span class="mom-vote" role="group" aria-label="Net votes">{VOTE_ICON}<span class="mom-vote-count">{signed_votes}</span>'
        '<span class="mom-vote-word">net votes</span></span></div>'
    )


def wire_card(title: str, href: str = "#", section: str | None = None, source: str | None = None, score=0, class_name: str | None = None) -> str:
    score_fraction = clamp_between_zero_and_one(score)
    return (
        f'<a class="{join_class_names("mom-wire-card", class_name)}" href="{_text(href)}">'
        + (f'<span class="mom-wire-card-section">{_text(section)}</span>' if section else "")
        + f'<span class="mom-wire-card-title">{_text(title)}</span>'
        f'<span class="mom-wire-card-meta">{_text(source)}'
        f'<span class="mom-score-track" role="img" aria-label="Classifier score {score_fraction:.2f}">'
        f'<span class="mom-score-bar" style="width: {js_round(score_fraction * 100)}%"></span></span>{score_fraction:.2f}</span></a>'
    )


# The one place the wording of a concept's metric lives: "12 associations", "1 association".
ASSOCIATIONS_NOUN = ("association", "associations")


def associations_label(count: int) -> str:
    return f"{count} {ASSOCIATIONS_NOUN[0] if count == 1 else ASSOCIATIONS_NOUN[1]}"


def wiki_card(term: str, href: str = "#", associations: int | None = None, definition: str | None = None, class_name: str | None = None) -> str:
    """A concept. Top right is how well connected it is (its association count), never a type label; with no count the corner is empty."""
    shown = associations if associations else None
    metric_html = f'<span class="mom-wiki-card-associations">{_text(associations_label(shown))}</span>' if shown else ""
    count_attribute = f' data-associations="{shown}"' if shown else ""
    definition_html = f'<span class="mom-wiki-card-definition">{_text(definition)}</span>' if definition else ""
    return (
        f'<a class="{join_class_names("mom-wiki-card", class_name)}" href="{_text(href)}"{count_attribute}>'
        f'<span class="mom-wiki-card-head"><span class="mom-wiki-card-term">{_text(term)}</span>{metric_html}</span>{definition_html}</a>'
    )


def pull_quote(text: str, class_name: str | None = None) -> str:
    return (
        f'<figure class="{join_class_names("mom-pull-quote", class_name)}">'
        f'<blockquote class="mom-pull-quote-text">{_text(text)}</blockquote></figure>'
    )


HOME_ICON = (
    '<svg class="mom-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" data-icon="house">'
    '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>'
)
# Lucide "menu" and "x": the menu button shows one and the other swaps in while the menu is open (the stylesheet decides which)
MENU_ICON = (
    '<svg class="mom-icon mom-icon-menu" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" data-icon="menu">'
    '<path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/></svg>'
)
CLOSE_ICON = (
    '<svg class="mom-icon mom-icon-close" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" data-icon="x">'
    '<path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>'
)
MARKDOWN_MARK = (
    '<svg class="mom-icon mom-icon-markdown" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 208 128" aria-hidden="true" focusable="false" data-icon="markdown">'
    '<rect x="5" y="5" width="198" height="118" rx="10" fill="none" stroke="currentColor" stroke-width="10"/>'
    '<path fill="currentColor" d="M30 98V30h20l20 25 20-25h20v68H90V59L70 84 50 59v39zm125 0l-30-33h20V30h20v35h20z"/></svg>'
)
SHARE_ICON = (
    '<svg class="mom-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" data-icon="share">'
    '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" x2="12" y1="2" y2="15"/></svg>'
)


X_MARK = (
    '<svg class="mom-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false" data-icon="x">'
    '<path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
)
REDDIT_MARK = (
    '<svg class="mom-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" focusable="false" data-icon="reddit">'
    '<path fill="currentColor" d="M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.047-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z"/></svg>'
)


def article_actions(page_path: str, title: str = "", site_url: str = "") -> str:
    """View as Markdown, post to X or Reddit, and a popup that shares the web page or its Markdown. The script fills in the full addresses for the popup."""
    markdown_path = page_path.rstrip("/") + "/index.md"
    page_url = site_url.rstrip("/") + page_path
    x_href = "https://x.com/intent/post?" + urlencode({"text": title, "url": page_url})
    reddit_href = "https://www.reddit.com/submit?" + urlencode({"url": page_url, "title": title})
    return (
        '<div class="mom-article-actions">'
        f'<a class="mom-icon-button" href="{_text(markdown_path)}" aria-label="View as Markdown" title="View as Markdown">{MARKDOWN_MARK}</a>'
        f'<a class="mom-icon-button" href="{_text(x_href)}" target="_blank" rel="noopener noreferrer" aria-label="Post on X" title="Post on X">{X_MARK}</a>'
        f'<a class="mom-icon-button" href="{_text(reddit_href)}" target="_blank" rel="noopener noreferrer" aria-label="Post on Reddit" title="Post on Reddit">{REDDIT_MARK}</a>'
        f'<div class="mom-share" data-mom-share data-title="{_text(title)}">'
        f'<button type="button" class="mom-icon-button" aria-label="Share" title="Share" aria-expanded="false">{SHARE_ICON}</button>'
        '<div class="mom-share-panel" hidden>'
        f'<button type="button" data-share-path="{_text(page_path)}">Share the web page</button>'
        f'<button type="button" data-share-path="{_text(markdown_path)}">Share the Markdown</button>'
        '<p class="mom-share-status" role="status"></p>'
        "</div></div></div>"
    )



# ---------------------------------------------------------------------------------------------- advertisements

AD_UNIT_NAMES = ("band", "rectangle", "half-page", "card", "story", "pullquote", "aside", "inline")
AD_IN_CONTENT_UNITS = ("story", "pullquote", "aside", "inline")  # the units that sit inside the words of an article, not after them
AD_HEADLINE_LIMIT = 60
AD_HEADLINE_EMPHASIS = re.compile(r"\*([^*]+)\*")  # *words* in a headline are set in italics (and the brand's accent); the marks do not count toward the limit
AD_LINK_RELATIONSHIP = "sponsored noopener"
AD_BAND_BREAKPOINTS = (("wide", 1042), ("medium", 800))  # real pixels: a 970 picture plus the page gutters, a 728 picture plus the gutters
AD_BAND_PICTURE_HEIGHT = 250  # every band size is 250 tall (970, 728 and 300 wide), so the unit holds the same weight at every width
AD_ROLE_WORDS = {"machine": "Machines", "human": "People"}
AD_REQUIRED_FIELDS = ("id", "advertiser", "headline", "body", "cta", "href", "units")
AD_IMAGE_FIELDS = ("src", "alt", "width", "height")
AD_BRAND_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
AD_BRAND_MINIMUM_CONTRAST = 4.5
AD_BRAND_ROLES = ("ground", "ink", "accent")  # accent is optional: the button, the emphasized words and the art; it falls back to ink
AD_BRAND_FACES = ("serif", "pixel")  # serif: Playfair Display headlines, Georgia text (Papyrus). pixel: Jersey 25 headlines, Jersey 10 labels (Anthus)

# The papyrus plant, Papyrus's own mark (a vector drawing of the plant on p.apyr.us, simplified to read at 16px). Filled, so it needs no stroke width.
AD_PAPYRUS_PLANT_PATH = (
        'M12.03 10.95Q7 10.17 3.84 12.94Q6.89 11.17 11.97 11.45ZM12.08 10.96Q6.98 9.04 3.65 10.34Q6.67 9.99 11.92 11.44ZM12.12 10.98Q7.27 7.89 3.97 7.8Q6.77 8.'
        '76 11.88 11.42ZM12.17 11.01Q7.87 6.81 4.81 5.48Q7.2 7.56 11.83 11.39ZM12.2 11.05Q8.76 5.89 6.12 3.52Q7.95 6.48 11.8 11.35ZM12.23 11.1Q9.88 5.21 7.84 2'
        '.03Q8.97 5.61 11.77 11.3ZM12.24 11.15Q11.15 4.82 9.85 1.11Q10.18 5.02 11.76 11.25ZM12.25 11.2Q12.5 4.75 12 0.8Q11.5 4.75 11.75 11.2ZM12.24 11.25Q13.82'
        ' 5.02 14.15 1.11Q12.85 4.82 11.76 11.15ZM12.23 11.3Q15.03 5.61 16.16 2.03Q14.12 5.21 11.77 11.1ZM12.2 11.35Q16.05 6.48 17.88 3.52Q15.24 5.89 11.8 11.0'
        '5ZM12.17 11.39Q16.8 7.56 19.19 5.48Q16.13 6.81 11.83 11.01ZM12.12 11.42Q17.23 8.76 20.03 7.8Q16.73 7.89 11.88 10.98ZM12.08 11.44Q17.33 9.99 20.35 10.3'
        '4Q17.02 9.04 11.92 10.96ZM12.03 11.45Q17.11 11.17 20.16 12.94Q17 10.17 11.97 10.95ZM12.65 22.6L12.3 10.4H11.7L11.35 22.6ZM11.5 22.6Q9.7 19.9 8.1 16.6Q'
        '10.4 19.4 12 21.9ZM12.5 22.6Q14.5 19.4 16.2 15.4Q13.7 18.9 12 21.9ZM15.8 22.6Q12 21.5 8.2 22.6ZM10.6 11.2Q12 12.5 13.4 11.2Q12 9.8 10.6 11.2Z'
)
# The Anthus lockup from anth.us (web/anthus_dom.py): the pixel A on its tile, the word ANTHUS, then AI SOLUTIONS in a lighter pixel face, so the
# pair reads as one phrase and the two halves differ by letterform, not by color alone.
AD_ANTHUS_A_PATH = (
        'M142.5 0h285v75h-285zM71.25 75h142.5v75h-142.5zM356.25 75h142.5v75h-142.5zM71.25 150h142.5v75h-142.5zM356.25 150h142.5v75h-142.5zM0 225h142.5v75h-142.'
        '5zM427.5 225h142.5v75h-142.5zM0 300h142.5v75h-142.5zM427.5 300h142.5v75h-142.5zM0 375h570v75h-570zM0 450h570v75h-570zM0 525h142.5v75h-142.5zM427.5 525'
        'h142.5v75h-142.5zM0 600h142.5v75h-142.5zM427.5 600h142.5v75h-142.5zM0 675h142.5v75h-142.5zM427.5 675h142.5v75h-142.5z'
)
AD_ANTHUS_WORD_PATH = (
        'M1159 450V0H1309V750H1129V720H1099V660H1069V600H1039V540H1009V480H979V420H949V360H919V300H889V750H739V0H919V30H949V90H979V150H1009V210H1039V270H1069V3'
        '30H1099V390H1129V450ZM1928 0V150H1778V750H1628V150H1478V0ZM2457 300V0H2607V750H2457V450H2247V750H2097V0H2247V300ZM2956 570V600H3106V570H3136V0H3286V63'
        '0H3256V690H3226V720H3166V750H2896V720H2836V690H2806V630H2776V0H2926V570ZM3635 570V600H3785V570H3815V480H3785V450H3575V420H3515V390H3485V330H3455V120H3'
        '485V60H3515V30H3575V0H3845V30H3905V60H3935V120H3965V210H3815V180H3785V150H3635V180H3605V270H3635V300H3845V330H3905V360H3935V420H3965V630H3935V690H3905'
        'V720H3845V750H3575V720H3515V690H3485V630H3455V510H3605V570Z'
)
AD_ANTHUS_SOLUTIONS_PATH = (
        'M0 289H66V223H132V157H198V91H264V157H329V223H395V289H461V750H329V618H132V750H0ZM132 486H329V355H264V289H198V355H132ZM601 91H733V750H601ZM1210 552H1342'
        'V618H1539V486H1276V421H1210V157H1276V91H1605V157H1671V289H1539V223H1342V355H1605V421H1671V684H1605V750H1276V684H1210ZM1811 157H1877V91H2206V157H2272V6'
        '84H2206V750H1877V684H1811ZM2074 552H2140V289H2074V223H2008V289H1943V552H2008V618H2074ZM2543 618H2741V750H2412V91H2543ZM3144 552H3210V91H3342V684H3276V'
        '750H2947V684H2881V91H3013V552H3079V618H3144ZM3614 223H3482V91H3877V223H3745V750H3614ZM4017 91H4149V750H4017ZM4288 157H4354V91H4684V157H4750V684H4684V7'
        '50H4354V684H4288ZM4552 552H4618V289H4552V223H4486V289H4420V552H4486V618H4552ZM5153 552H5087V421H5021V750H4889V91H5087V223H5153V355H5219V486H5285V91H54'
        '16V750H5219V684H5153ZM5556 552H5688V618H5886V486H5622V421H5556V157H5622V91H5951V157H6017V289H5886V223H5688V355H5951V421H6017V684H5951V750H5622V684H555'
        '6Z'
)


def _filled_svg(class_name: str, view_box: str, body: str, label: str | None = None) -> str:
    accessibility = f'role="img" aria-label="{_text(label)}"' if label else 'aria-hidden="true"'
    return f'<svg class="{class_name}" xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" {accessibility} focusable="false">{body}</svg>'


# A brand's small mark, drawn before its name. A brand names one of these; a new advertiser's mark is added here.
AD_BRAND_MARKS = {
    "papyrus-plant": _filled_svg("mom-ad-mark mom-ad-mark-papyrus-plant", "0 0 24 24", f'<path fill="currentColor" d="{AD_PAPYRUS_PLANT_PATH}"/>'),
    # Lucide "newspaper", the first Papyrus mark, kept for an advertiser that wants a plain line icon.
    "newspaper": (
        '<svg class="mom-ad-mark mom-ad-mark-newspaper" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
        '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/>'
        '<path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>'
    ),
}
# A brand's whole lockup, drawn in place of its mark and name when the name is itself a drawing. Labelled with the brand's name for screen readers.
AD_BRAND_WORDMARKS = {
    "anthus-lockup": lambda name: _filled_svg(
        "mom-ad-wordmark mom-ad-wordmark-anthus-lockup", "-71.25 -75 10486.8 900",
        '<rect class="mom-ad-wordmark-tile" x="-71.25" y="-75" width="712.5" height="900"/>'
        f'<path class="mom-ad-wordmark-glyph" d="{AD_ANTHUS_A_PATH}"/>'
        f'<path fill="currentColor" d="{AD_ANTHUS_WORD_PATH}"/>'
        f'<path class="mom-ad-wordmark-accent" transform="translate(4332.5 0)" d="{AD_ANTHUS_SOLUTIONS_PATH}"/>',
        label=name,
    ),
}
# A brand's art: one composition behind (or beside) the words of its band, rectangle, half page and story panel, and the picture of its card.
# Drawn in the brand's own three colors through custom properties, so Day and Night follow the page. Decoration only: it carries no meaning.
AD_ANTHUS_PIXEL_TRAIL = ((-3, 4, 0.55), (-5, 6, 0.32), (-4, 9, 0.4), (-7, 8, 0.18), (-2, 11, 0.28), (-9, 5, 0.12), (-6, 2, 0.2))
AD_BRAND_ART = {
    # The Nile sun: the accent as a disc, the plant standing in it in the ground color.
    "papyrus-sun": _filled_svg(
        "mom-ad-art-drawing", "0 0 240 240",
        '<circle cx="120" cy="120" r="112" fill="var(--ad-accent)"/>'
        f'<path fill="var(--ad-ground)" transform="translate(30 22) scale(7.5)" d="{AD_PAPYRUS_PLANT_PATH}"/>',
    ),
    # The pixel A on its tile, large, with a trail of loose pixels behind it, as a sprite moving right.
    "anthus-pixels": _filled_svg(
        "mom-ad-art-drawing", "-784 -150 1496 1050",
        "".join(f'<rect x="{column * 71.25:g}" y="{row * 75 - 75:g}" width="71.25" height="75" fill="var(--ad-accent)" opacity="{opacity}"/>'
                for column, row, opacity in AD_ANTHUS_PIXEL_TRAIL)
        + '<rect x="-71.25" y="-75" width="712.5" height="900" rx="54" fill="var(--ad-accent)"/>'
        f'<path fill="var(--ad-ground)" d="{AD_ANTHUS_A_PATH}"/>',
    ),
}
AD_ADDRESS_PATTERN = re.compile(r"^(https://|/)")


def _visible_headline(headline: str) -> str:
    return AD_HEADLINE_EMPHASIS.sub(r"\1", headline)


def validate_advertisement(ad) -> None:
    """Raise `ValueError` naming what is wrong with an ad before it can reach a page."""
    if not isinstance(ad, dict):
        raise ValueError("an ad is an object")
    name = ad.get("id", "(no id)")
    for field in AD_REQUIRED_FIELDS:
        if not ad.get(field):
            raise ValueError(f"ad {name}: {field} is required")
    for unit, copy in (ad.get("unit_copy") or {}).items():
        if unit not in AD_UNIT_NAMES:
            raise ValueError(f"ad {name}: unit_copy names unknown unit {unit!r}")
        if len(_visible_headline(copy.get("headline", ""))) > AD_HEADLINE_LIMIT:
            raise ValueError(f"ad {name}: the {unit} headline is longer than the limit of {AD_HEADLINE_LIMIT} characters")
    unknown_units = [unit for unit in ad["units"] if unit not in AD_UNIT_NAMES]
    if unknown_units:
        raise ValueError(f"ad {name}: unknown units {unknown_units}; the standard units are {list(AD_UNIT_NAMES)}")
    if len(_visible_headline(ad["headline"])) > AD_HEADLINE_LIMIT:
        raise ValueError(f"ad {name}: the headline is {len(_visible_headline(ad['headline']))} characters; the limit is {AD_HEADLINE_LIMIT}")
    if not AD_ADDRESS_PATTERN.match(ad["href"]):
        raise ValueError(f"ad {name}: href must be an https address or a path on this site")
    if ad.get("brand"):
        _validate_ad_brand(name, ad["brand"])
    for unit, images in _ad_images(ad).items():
        for image in (images.values() if unit == "band" else [images]):
            missing = [field for field in AD_IMAGE_FIELDS if not image.get(field)]
            if missing:
                raise ValueError(f"ad {name}: the {unit} image needs {missing}; every creative has alt text and its pixel size")
        if unit == "band" and "narrow" not in images:
            raise ValueError(f"ad {name}: a band image needs a narrow (300x250) version, the one every width can show")


def _relative_luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted((_relative_luminance(first), _relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _validate_ad_brand(name: str, brand) -> None:
    """An advertiser's own look: its name, its mark or whole wordmark, its type face, its art and its colors for Day and Night. The build refuses
    unreadable pairs: ink on ground, and the accent on ground (the accent is the button, with the ground color as its text)."""
    if not brand.get("name"):
        raise ValueError(f"ad {name}: a brand needs a name")
    for field, known in (("mark", AD_BRAND_MARKS), ("wordmark", AD_BRAND_WORDMARKS), ("art", AD_BRAND_ART), ("face", AD_BRAND_FACES)):
        if brand.get(field) and brand[field] not in known:
            raise ValueError(f"ad {name}: unknown brand {field} {brand[field]!r}; the known ones are {list(known)}")
    for theme in ("day", "night"):
        colors = {role: (brand.get(role) or {}).get(theme) for role in AD_BRAND_ROLES}
        required = ("ground", "ink", "accent") if brand.get("accent") else ("ground", "ink")
        for role in required:
            if not colors[role] or not AD_BRAND_COLOR_PATTERN.match(colors[role]):
                raise ValueError(f"ad {name}: the brand needs its {role} color as #rrggbb for day and night")
        for role in required[1:]:
            contrast = _contrast_ratio(colors["ground"], colors[role])
            if contrast < AD_BRAND_MINIMUM_CONTRAST:
                raise ValueError(f"ad {name}: the brand's {theme} {role} on its ground has contrast {contrast:.1f}; the minimum is {AD_BRAND_MINIMUM_CONTRAST}")


def _ad_images(ad) -> dict:
    return ad.get("images") or {}


def _ad_attributes(unit: str, ad, placement: str | None) -> str:
    return f'data-ad="{_text(ad["id"])}" data-ad-unit="{unit}" data-ad-placement="{_text(placement or unit)}"'


def _ad_label(ad) -> str:
    return f'<p class="mom-ad-label"><b>Advertisement</b> · {_text(ad["advertiser"])}</p>'


def _ad_button(ad) -> str:
    return f'<a class="mom-ad-button" rel="{AD_LINK_RELATIONSHIP}" href="{_text(ad["href"])}">{_text(ad["cta"])}</a>'


def _ad_headline_html(headline: str) -> str:
    """The headline, escaped, with its *emphasized* words in italics."""
    return AD_HEADLINE_EMPHASIS.sub(lambda found: f"<em>{found.group(1)}</em>", _text(headline))


def _ad_art(ad) -> str:
    """What stands behind a house creative: the brand's art when it has one, its mark drawn large when it has only a mark, and the site's disc and slab
    when the ad has no brand."""
    brand = ad.get("brand") or {}
    if brand.get("art"):
        return f'<span class="mom-ad-art mom-ad-art-{brand["art"]}" aria-hidden="true">{AD_BRAND_ART[brand["art"]]}</span>'
    if brand.get("mark"):
        return f'<span class="mom-ad-brand-art" aria-hidden="true">{AD_BRAND_MARKS[brand["mark"]]}</span>'
    if brand:
        return ""
    return '<span class="mom-ad-disc" aria-hidden="true"></span><span class="mom-ad-slab" aria-hidden="true"></span>'


def _ad_brand_row(ad) -> str:
    """The advertiser's name as the first line of a branded creative: its whole wordmark when it has one, else its mark and its name. Nothing for an ad with no brand."""
    brand = ad.get("brand")
    if not brand:
        return ""
    if brand.get("wordmark"):
        return f'<p class="mom-ad-brand mom-ad-brand-wordmark">{AD_BRAND_WORDMARKS[brand["wordmark"]](brand["name"])}</p>'
    mark = AD_BRAND_MARKS[brand["mark"]] if brand.get("mark") else ""
    return f'<p class="mom-ad-brand">{mark}<span class="mom-ad-brand-name">{_text(brand["name"])}</span></p>'


def _ad_brand_style(ad) -> str:
    """The advertiser's colors for Day and Night as custom properties on the ad; the stylesheet picks the set that matches the page's theme."""
    brand = ad.get("brand")
    if not brand:
        return ""
    colors = {role: brand.get(role) or brand["ink"] for role in AD_BRAND_ROLES}
    properties = "".join(f"--ad-{role}-{theme}:{colors[role][theme]};" for role in AD_BRAND_ROLES for theme in ("day", "night"))
    return f' style="{properties}"'


def _ad_brand_classes(ad) -> str:
    brand = ad.get("brand")
    if not brand:
        return ""
    return " mom-ad-branded" + (f" mom-ad-face-{brand['face']}" if brand.get("face") else "")


def _ad_headline(ad) -> str:
    return f'<p class="mom-ad-headline">{_ad_headline_html(ad["headline"])}</p>'


def _ad_points(ad) -> str:
    tiles = []
    for point in ad.get("points") or []:
        role = "human" if point.get("by") == "human" else "machine"
        tiles.append(f'<li class="mom-ad-point mom-ad-point-{role}"><span class="mom-label">{_text(point.get("label") or AD_ROLE_WORDS[role])}</span><span class="mom-ad-point-text">{_text(point["text"])}</span></li>')
    return f'<ul class="mom-ad-points">{"".join(tiles)}</ul>' if tiles else ""


def _ad_house_creative(unit: str, ad) -> str:
    points = _ad_points(ad) if unit == "half-page" else ""
    text = f'<div class="mom-ad-text">{_ad_headline(ad)}<p class="mom-ad-body">{_text(ad["body"])}</p></div>'
    return f'<div class="mom-ad-creative">{_ad_art(ad)}<div class="mom-ad-copy">{_ad_brand_row(ad)}{text}{points}{_ad_button(ad)}</div></div>'


def _ad_image_tag(image) -> str:
    return f'<img src="{_text(image["src"])}" alt="{_text(image["alt"])}" width="{int(image["width"])}" height="{int(image["height"])}" loading="lazy">'


def _ad_image_creative(unit: str, ad, contained: bool) -> str:
    images = _ad_images(ad)[unit]
    if unit == "band":
        usable = [] if contained else [(name, width) for name, width in AD_BAND_BREAKPOINTS if name in images]
        sources = "".join(
            f'<source media="(min-width: {width}px)" srcset="{_text(images[name]["src"])}" width="{int(images[name]["width"])}" height="{int(images[name]["height"])}">'
            for name, width in usable
        )
        picture = f'<picture>{sources}{_ad_image_tag(images["narrow"])}</picture>'
    else:
        picture = _ad_image_tag(images)
    return f'<div class="mom-ad-slot"><a rel="{AD_LINK_RELATIONSHIP}" href="{_text(ad["href"])}">{picture}</a></div>'


def _ad_in_content(unit: str, ad, attributes: str) -> str:
    """The units that live inside an article's words. The inline sentence and the pull-quote borrow the page's own furniture; the aside is a small
    poster in the advertiser's colors. Each says Advertisement and the advertiser's name where a byline would go."""
    sponsor = f'Advertisement · {_text(ad["advertiser"])}'
    classes = f'mom-ad mom-ad-{unit}{_ad_brand_classes(ad)}'
    link = f'<a class="mom-ad-link" rel="{AD_LINK_RELATIONSHIP}" href="{_text(ad["href"])}">{_text(ad["cta"])}</a>'
    if unit == "inline":
        return (f'<aside class="{classes}" aria-label="Advertisement" {attributes}{_ad_brand_style(ad)}>'
                f'<p class="mom-ad-inline-text"><span class="mom-ad-tag">{sponsor}</span> {_text(ad["body"])} {link}</p></aside>')
    if unit == "pullquote":
        return (f'<figure class="mom-pull-quote {classes}" aria-label="Advertisement" {attributes}{_ad_brand_style(ad)}>'
                f'<blockquote class="mom-pull-quote-text">{_ad_headline_html(ad["headline"])}</blockquote>'
                f'<figcaption class="mom-ad-pullquote-by"><span class="mom-ad-tag">{sponsor}</span> {link}</figcaption></figure>')
    return (f'<aside class="{classes}" aria-label="Advertisement" {attributes}{_ad_brand_style(ad)}>'
            f'<p class="mom-ad-label"><b>Advertisement</b> · {_text(ad["advertiser"])}</p>'
            f'<div class="mom-ad-aside-poster">{_ad_brand_row(ad)}'
            f'<p class="mom-ad-aside-headline">{_ad_headline_html(ad["headline"])}</p><p class="mom-ad-aside-body">{_text(ad["body"])}</p>'
            f'<a class="mom-ad-button" rel="{AD_LINK_RELATIONSHIP}" href="{_text(ad["href"])}">{_text(ad["cta"])}</a></div></aside>')


def _ad_card(ad, attributes: str) -> str:
    """The card is a story card. A branded ad's card shows its brand's art on its own ground where another card has its picture."""
    card = story_card(
        _visible_headline(ad["headline"]), ad["href"], ad.get("body"), kicker=f"Advertisement · {ad['advertiser']}", meta=ad["cta"],
        image=ad.get("card_image"), image_alt=ad.get("card_image_alt") or "", image_seed=ad["id"], class_name="mom-ad-card",
    )
    art = (ad.get("brand") or {}).get("art")
    if art and not ad.get("card_image"):
        placeholder = card_image(None, "", ad["id"])
        branded_art = media_frame(f'<span class="mom-card-image mom-ad-art mom-ad-art-{art}" aria-hidden="true">{AD_BRAND_ART[art]}</span>', "mom-ad-card-art")
        card = card.replace(placeholder, branded_art, 1)
    headline = _ad_headline_html(ad["headline"])
    card = card.replace(f'<span class="mom-story-card-headline">{_text(_visible_headline(ad["headline"]))}</span>', f'<span class="mom-story-card-headline">{headline}</span>', 1)
    card = card.replace('<a class="', f'<a {attributes} rel="{AD_LINK_RELATIONSHIP}"{_ad_brand_style(ad)} class="', 1)
    return card.replace('class="mom-story-card', f'class="mom-story-card{_ad_brand_classes(ad)}', 1)


def advertisement(unit: str, ad, placement: str | None = None, contained: bool = False) -> str:
    """One of the standard units, drawn from an ad. `contained` is for a column narrower than the page: a band there offers only its 300x250 picture.

    The band, rectangle and half page show the ad's own pictures when it supplies them for that unit, and the house creative built from its words otherwise.
    The card is a story card and the story panel is native, so both are always built from the ad's words.
    """
    if unit not in AD_UNIT_NAMES:
        raise ValueError(f"unknown ad unit {unit!r}")
    ad = {**ad, **(ad.get("unit_copy") or {}).get(unit, {})}
    attributes = _ad_attributes(unit, ad, placement)
    if unit == "card":
        return _ad_card(ad, attributes)
    if unit in ("inline", "pullquote", "aside"):
        return _ad_in_content(unit, ad, attributes)
    has_pictures = unit in _ad_images(ad)
    creative = _ad_image_creative(unit, ad, contained) if has_pictures else _ad_house_creative(unit, ad)
    return f'<aside class="mom-ad mom-ad-{unit}{_ad_brand_classes(ad)}" aria-label="Advertisement" {attributes}{_ad_brand_style(ad)}>{_ad_label(ad)}{creative}</aside>'
