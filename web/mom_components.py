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
from pathlib import Path
from urllib.parse import urlencode

KNOWN_ROLES = ("brand", "machine", "human")
PLACEHOLDER_SHAPE_COUNTS = {"sun-slab": 2, "rising": 1, "eclipse": 1, "moon": 1, "horizon": 1, "pages": 3}
GENERAL_PLACEHOLDER_COMPOSITIONS = ("sun-slab", "rising", "eclipse", "moon", "horizon")
PLACEHOLDER_TONES = KNOWN_ROLES
BAND_CONNECTOR_WORDS = ("on", "about")  # the small words of a band phrase, drawn in the accent colour
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


def menu_panel(destinations, panel_id: str = MENU_ID, extra: str = "", here_label: str = "You are here") -> str:
    """The full-page menu: one big block per destination with its name and a subtitle. `destinations` are `(label, href, subtitle, active)` tuples.

    `extra` is markup placed after the destinations (the language list on a page that has translations).
    Hidden until the script opens it. The current page carries `aria-current="page"` and the words "You are here", so it is not marked by colour alone."""
    rows = []
    for label, href, subtitle, active in destinations:
        current = ' aria-current="page"' if active else ""
        here = f'<span class="mom-menu-here">{_text(here_label)}</span>' if active else ""
        sub = f'<span class="mom-menu-sub">{_text(subtitle)}</span>' if subtitle else ""
        rows.append(
            f'<li><a class="mom-menu-link" href="{_text(href)}"{current}>'
            f'<span class="mom-menu-head"><span class="mom-menu-name">{_text(label)}</span>{here}</span>{sub}</a></li>'
        )
    return f'<nav class="mom-menu" id="{_text(panel_id)}" aria-label="Site menu" hidden><ul class="mom-menu-list">{"".join(rows)}</ul>{extra}</nav>'


# ---------------------------------------------------------------------------------------------- language switcher and welcoming banner
# `alternates` are `{tag, name, url}`: the page in each language it exists in, itself included, names in their own language (see languages.py). The current
# language is marked by its name in the control, a check mark and `aria-current`, never by colour alone. Every option is a real link with `lang` and `hreflang`.

def language_option(alternate: dict, current_tag: str, class_name: str = "mom-language-option") -> str:
    current = alternate["tag"] == current_tag
    mark = lucide_icon("check") if current else ""
    flag = ' aria-current="true"' if current else ""
    tag = _text(alternate["tag"])
    return (
        f'<a class="{class_name}" href="{_text(alternate["url"])}" lang="{tag}" hreflang="{tag}" data-language="{tag}"{flag}>'
        f'<span class="mom-language-name">{_text(alternate["name"])}</span>{mark}</a>'
    )


def language_switcher(alternates, current_tag: str, label: str) -> str:
    """The control in the bar: the Languages icon and the current language's own name open a list of the page's languages (a `details`, so it works without JavaScript).
    `label` is the word "Language" in the page's language; the accessible name is "<label>: <current name>"."""
    current = next(alternate for alternate in alternates if alternate["tag"] == current_tag)
    options = "".join(f"<li>{language_option(alternate, current_tag)}</li>" for alternate in alternates)
    return (
        '<div class="mom-language-switcher" data-mom-language-switcher><details class="mom-language-details">'
        f'<summary class="mom-language-trigger" aria-label="{_text(label)}: {_text(current["name"])}">{lucide_icon("languages")}'
        f'<span class="mom-language-current">{_text(current["name"])}</span>{lucide_icon("chevron-down")}</summary>'
        f'<ul class="mom-language-list">{options}</ul></details></div>'
    )


def language_menu_section(alternates, current_tag: str, label: str) -> str:
    """The same languages inside the full-page menu: the way to switch on a phone, where the bar holds only the brand, the icon and the menu button."""
    options = "".join(f"<li>{language_option(alternate, current_tag, 'mom-language-option mom-language-menu-option')}</li>" for alternate in alternates)
    return (
        '<section class="mom-menu-languages" data-mom-language-switcher aria-labelledby="mom-menu-languages-title">'
        f'<h2 class="mom-menu-languages-title" id="mom-menu-languages-title">{lucide_icon("languages")}<span>{_text(label)}</span></h2>'
        f'<ul class="mom-menu-language-list">{options}</ul></section>'
    )


def language_banner() -> str:
    """The welcoming banner, empty and hidden. `assets/mom-language.js` fills it in the visitor's language and shows it only when the visitor prefers another
    language this page exists in; it is drawn before the page's own content so nothing moves when it appears. Three modes share it: an offer with a countdown,
    a quiet "Read in <primary language>" link, and a note after a remembered choice switched the page, with Undo."""
    def action(name: str, icon: str) -> str:
        icons = lucide_icon(icon) + (lucide_icon("play") if name == "pause" else "")  # Pause shows Play while the clock is stopped
        return f'<button type="button" class="mom-language-banner-button" data-action="{name}">{icons}<span></span></button>'

    return (
        '<div class="mom-language-banner" data-mom-language-banner hidden>'
        '<p class="mom-language-banner-text"><span class="mom-language-banner-message"></span> <span class="mom-language-banner-count" aria-hidden="true"></span></p>'
        f'<div class="mom-language-banner-actions">{action("switch", "languages")}'
        f'<a class="mom-language-banner-button" data-action="read" href="#">{lucide_icon("languages")}<span></span></a>'
        f'{action("undo", "languages")}{action("stay", "x")}{action("pause", "pause")}</div>'
        '<span class="mom-language-banner-progress" aria-hidden="true"><span></span></span>'
        '<p class="mom-language-banner-live" role="status" aria-live="polite"></p></div>'
    )


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
        word_kind = "on" if word in BAND_CONNECTOR_WORDS else "tag" if word[:1] == "#" else "word"
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
        f'<span class="mom-card-date">{_text(meta)}</span>' if meta else "",
        f'<span class="mom-blurb">{_text(blurb)}</span>' if blurb else "",
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
                   stars=None, class_name: str | None = None, section: str | None = None, player: dict | None = None) -> str:
    """`player` (`src`, `title`, `allow`) makes the card a click-to-play video: its picture (or the site's placeholder art) is a Play button, and pressing it swaps in the provider's own embed, loaded from `src`, in the picture's place (assets/mom.js does the swap; no frame exists until then). A button is interactive, so it cannot sit inside the card's link: the card is then a plain box and its headline carries the link."""
    label, role = reference_status(status, actor)
    seed = image_seed or href or title
    chosen_kind = kind or ("paper" if is_research_paper_location(href) or is_research_paper_location(host) else None)
    site_html = f'<span class="mom-reference-card-site">{_text(site_name)}</span>' if site_name else ""
    meter = confidence_meter(confidence) if confidence is not None and status == "recommended" else ""
    rating = star_rating(stars) if stars and status != "recommended" else ""
    meta = " · ".join(part for part in (host, section, meta_date) if part)
    status_html = f'<span class="mom-reference-status mom-reference-status-{role}">{_text(label)}</span>' if label else ""
    summary_html = f'<span class="mom-reference-card-summary">{_text(summary)}</span>' if summary else ""
    date_html = f'<span class="mom-card-date">{_text(meta)}</span>'
    if player:
        poster = _card_image_content(image, "", seed, chosen_kind, image_tone, None, None, None)
        play_button = (
            f'<button type="button" class="mom-video-poster" aria-label="Play: {_text(title)}" data-player-src="{_text(player["src"])}" '
            f'data-player-title="{_text(player["title"])}" data-player-allow="{_text(player["allow"])}">'
            f'{poster}<span class="mom-video-play">{lucide_icon("play")}<span>Play</span></span></button>'
        )
        return (
            f'<div class="{join_class_names("mom-reference-card mom-reference-card-video", class_name)}">'
            f'<span class="mom-reference-card-media">{media_frame(play_button, "mom-video-frame")}</span>'
            + status_html
            + f'<a class="mom-reference-card-title" href="{_text(href)}">{_text(title)}</a>'
            + summary_html + rating + meter + date_html + "</div>"
        )
    return (
        f'<a class="{join_class_names("mom-reference-card", class_name)}" href="{_text(href)}">'
        f'<span class="mom-reference-card-media">{card_image(image, "", seed, chosen_kind, image_tone)}{site_html}</span>'
        + status_html
        + f'<span class="mom-reference-card-title">{_text(title)}</span>'
        + summary_html + rating + meter + date_html + "</a>"
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
        f'{latest_html}<span class="mom-card-date mom-thread-card-meta">{_text(meta)}</span></a>'
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
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "play": '<polygon points="6 3 20 12 6 21 6 3"/>',
    "external-link": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "languages": '<path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "pause": '<rect x="14" y="4" width="4" height="16" rx="1"/><rect x="6" y="4" width="4" height="16" rx="1"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
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
#
# An ad is an asset the advertiser supplies and controls completely: its pictures, with the words, type, colors and art drawn inside them.
# The site draws only the slot around the picture: the "Advertisement" label and the advertiser's name, the sponsored link, the alt text, the
# unit's size and placement, and the containment that stops a picture from spilling out. The site never styles what is inside a creative.

AD_UNIT_NAMES = ("band", "half-page", "card", "story", "pullquote", "aside")
AD_IN_CONTENT_UNITS = ("story", "pullquote", "aside")  # the units that sit inside the words of an article, not after them
AD_LINK_RELATIONSHIP = "sponsored noopener"
AD_FIXED_SIZE_UNITS = ("half-page",)  # one picture: the 300x600 rail, which is 300 wide at every width it is shown
# A unit that sits in a column or a page-wide slot fills the slot's whole width, so each size is drawn for the slot a range of windows gives it:
# the slot is the window less the page gutters (576 to 727 from 600, 728 to 969 from 800, 970 and wider from 1042), and an article's column is 618.
AD_SIZE_NAMES = {"band": ("wide", "medium", "column", "narrow")}  # the other stretchy units offer a wide and a narrow picture
AD_DEFAULT_SIZE_NAMES = ("wide", "narrow")
AD_BREAKPOINTS = {"band": (("wide", 1042), ("medium", 800), ("column", 600))}  # real pixels
AD_DEFAULT_BREAKPOINTS = (("wide", 600),)  # where the site starts drawing at 75%, so the column is no longer the phone's
AD_CONTAINED_SIZES = ("column",)  # a band in an article's column is drawn for the column, never for the page
AD_IMAGE_FIELDS = ("src", "alt", "width", "height")
AD_ASSET_FOLDER = "/assets/ads/"
AD_ASSET_TYPES = (".webp", ".png", ".jpg", ".jpeg", ".svg")
AD_ASSET_MAXIMUM_BYTES = 150_000
AD_ALT_MINIMUM_CHARACTERS = 20  # alt text carries the creative's words, so a name alone is never enough
AD_REQUIRED_FIELDS = ("id", "advertiser", "href", "images")
AD_ADDRESS_PATTERN = re.compile(r"^(https://|/)")
AD_ASSET_ROOT = Path(__file__).parent


def ad_units(ad) -> tuple[str, ...]:
    """The units an ad offers: the ones it supplies pictures for, in the standard order."""
    return tuple(unit for unit in AD_UNIT_NAMES if unit in (ad.get("images") or {}))


def _ad_sizes(unit: str, images) -> list[dict]:
    """Every picture of one unit: the one picture of a fixed-size unit, or each named size of the others."""
    return [images] if unit in AD_FIXED_SIZE_UNITS else list(images.values())


def _ad_image_sources(image) -> list[str]:
    return [image["src"], *([image["src_dark"]] if image.get("src_dark") else [])]


def _validate_ad_image(name: str, unit: str, image, advertiser: str) -> None:
    if not isinstance(image, dict):
        raise ValueError(f"ad {name}: the {unit} picture is an object with {list(AD_IMAGE_FIELDS)}")
    missing = [field for field in AD_IMAGE_FIELDS if not image.get(field)]
    if missing:
        raise ValueError(f"ad {name}: the {unit} picture needs {missing}; every creative has alt text and its pixel size")
    alt = image["alt"].strip()
    if len(alt) < AD_ALT_MINIMUM_CHARACTERS or alt.lower() == advertiser.lower():
        raise ValueError(f"ad {name}: the {unit} alt text must say what the creative says (at least {AD_ALT_MINIMUM_CHARACTERS} characters, more than the advertiser's name)")
    for field in ("width", "height"):
        if not isinstance(image[field], int) or image[field] <= 0:
            raise ValueError(f"ad {name}: the {unit} picture's {field} is a whole number of pixels")
    for source in _ad_image_sources(image):
        if not source.startswith(AD_ASSET_FOLDER) or not source.lower().endswith(AD_ASSET_TYPES):
            raise ValueError(f"ad {name}: the {unit} picture {source!r} must be a {'/'.join(AD_ASSET_TYPES)} file under {AD_ASSET_FOLDER}")
        asset = AD_ASSET_ROOT / source.lstrip("/")
        if not asset.is_file():
            raise ValueError(f"ad {name}: the {unit} picture {source!r} is not in web{AD_ASSET_FOLDER}")
        if asset.stat().st_size > AD_ASSET_MAXIMUM_BYTES:
            raise ValueError(f"ad {name}: the {unit} picture {source!r} is {asset.stat().st_size} bytes; the limit is {AD_ASSET_MAXIMUM_BYTES}")


def validate_advertisement(ad) -> None:
    """Raise `ValueError` naming what is wrong with an ad before it can reach a page: its advertiser, its sponsored address, and for every unit it offers
    pictures that exist under `web/assets/ads/`, have alt text that says what they say, and say their pixel size."""
    if not isinstance(ad, dict):
        raise ValueError("an ad is an object")
    name = ad.get("id", "(no id)")
    for field in AD_REQUIRED_FIELDS:
        if not ad.get(field):
            raise ValueError(f"ad {name}: {field} is required")
    if not AD_ADDRESS_PATTERN.match(ad["href"]):
        raise ValueError(f"ad {name}: href must be an https address or a path on this site")
    unknown_units = [unit for unit in ad["images"] if unit not in AD_UNIT_NAMES]
    if unknown_units:
        raise ValueError(f"ad {name}: unknown units {unknown_units}; the standard units are {list(AD_UNIT_NAMES)}")
    for unit, images in ad["images"].items():
        if unit not in AD_FIXED_SIZE_UNITS:
            allowed = AD_SIZE_NAMES.get(unit, AD_DEFAULT_SIZE_NAMES)
            unknown_sizes = [size for size in images if size not in allowed]
            if unknown_sizes:
                raise ValueError(f"ad {name}: the {unit} has no sizes {unknown_sizes}; its sizes are {list(allowed)}")
            if "narrow" not in images:
                raise ValueError(f"ad {name}: the {unit} needs a narrow version, the one every width can show")
        sizes = _ad_sizes(unit, images)
        for image in sizes:
            _validate_ad_image(name, unit, image, ad["advertiser"])
        if len({bool(image.get("src_dark")) for image in sizes}) > 1:
            raise ValueError(f"ad {name}: the {unit} gives a Night picture for some of its sizes and not all")


def _ad_attributes(unit: str, ad, placement: str | None) -> str:
    # data-promotion-* is what web/assets/mom.js reports to GA4 (view_promotion, select_promotion), and it keeps Papyrus's shared listener
    # from counting an ad click as a call to action.
    return (f'data-ad="{_text(ad["id"])}" data-ad-unit="{unit}" data-ad-placement="{_text(placement or unit)}" '
            f'data-promotion-id="{_text(ad["id"])}" data-promotion-name="{_text(ad["advertiser"])}"')


def _ad_label(ad) -> str:
    return f'<p class="mom-ad-label"><b>Advertisement</b> · {_text(ad["advertiser"])}</p>'


def _ad_image_tag(image, source: str) -> str:
    return f'<img src="{_text(source)}" alt="{_text(image["alt"])}" width="{int(image["width"])}" height="{int(image["height"])}" loading="lazy">'


def _ad_picture(unit: str, images, contained: bool, source_field: str) -> str:
    """One theme's picture for a unit: the narrow picture, and a larger one for each breakpoint the unit has that the column can hold."""
    if unit in AD_FIXED_SIZE_UNITS:
        return _ad_image_tag(images, images[source_field])
    breakpoints = [(size, width) for size, width in AD_BREAKPOINTS.get(unit, AD_DEFAULT_BREAKPOINTS) if size in images and (not contained or size in AD_CONTAINED_SIZES)]
    sources = "".join(
        f'<source media="(min-width: {width}px)" srcset="{_text(images[size][source_field])}" width="{int(images[size]["width"])}" height="{int(images[size]["height"])}">'
        for size, width in breakpoints
    )
    return f'<picture>{sources}{_ad_image_tag(images["narrow"], images["narrow"][source_field])}</picture>'


def _ad_creative(unit: str, ad, contained: bool) -> str:
    """The advertiser's picture in the site's slot, linked and marked sponsored. With a Night picture it draws both and the stylesheet shows the one the theme calls for."""
    images = ad["images"][unit]
    picture = _ad_picture(unit, images, contained, "src")
    if any(image.get("src_dark") for image in _ad_sizes(unit, images)):
        picture = f'<span class="mom-ad-day">{picture}</span><span class="mom-ad-night">{_ad_picture(unit, images, contained, "src_dark")}</span>'
    return f'<div class="mom-ad-slot"><a rel="{AD_LINK_RELATIONSHIP}" href="{_text(ad["href"])}">{picture}</a></div>'


def advertisement(unit: str, ad, placement: str | None = None, contained: bool = False) -> str:
    """One of the standard units, drawn from an ad: the site's label, then the advertiser's own picture for the unit in a sponsored link.
    `contained` is for an article's column, narrower than the page: a band there offers only its column and narrow pictures."""
    if unit not in AD_UNIT_NAMES:
        raise ValueError(f"unknown ad unit {unit!r}")
    if unit not in ad_units(ad):
        raise ValueError(f"ad {ad['id']} has no picture for the {unit} unit")
    return (f'<aside class="mom-ad mom-ad-{unit}" aria-label="Advertisement" {_ad_attributes(unit, ad, placement)}>'
            f'{_ad_label(ad)}{_ad_creative(unit, ad, contained)}</aside>')
