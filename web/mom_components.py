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
    "accepted-human": ("Accepted by an editor", "human"),
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


def placeholder_art(seed, kind: str | None = None, tone: str | None = None, composition: str | None = None, class_name: str | None = None) -> str:
    chosen_composition, chosen_tone = choose_placeholder_art(seed, kind)
    final_composition = composition if composition in PLACEHOLDER_SHAPE_COUNTS else chosen_composition
    final_tone = tone if tone in KNOWN_ROLES else chosen_tone
    shapes = "".join(f'<span class="mom-art-shape mom-art-shape-{index}"></span>' for index in range(1, PLACEHOLDER_SHAPE_COUNTS[final_composition] + 1))
    classes = join_class_names("mom-card-image", "mom-art", f"mom-art-{final_composition}", f"mom-art-tone-{final_tone}", class_name)
    return f'<span class="{classes}" aria-hidden="true" data-composition="{final_composition}" data-tone="{final_tone}">{shapes}</span>'


def card_image(src: str | None, alt: str = "", seed=None, kind: str | None = None, tone: str | None = None,
               composition: str | None = None, class_name: str | None = None, image_dark: str | None = None) -> str:
    """The card's image, or `PlaceholderArt` when there is none. An image that fails to load is swapped for the same art by `assets/mom.js`. With a Night version it draws both and the stylesheet shows the one the theme calls for."""
    if src:
        classes = join_class_names("mom-card-image", class_name)
        kind_attribute = f' data-art-kind="{_text(kind)}"' if kind else ""
        def picture(path: str) -> str:
            return f'<img class="{classes}" src="{_text(path)}" alt="{_text(alt)}" loading="lazy" data-art-seed="{_text(seed)}"{kind_attribute}>'
        if image_dark:
            return f'<span class="mom-card-image-day">{picture(src)}</span><span class="mom-card-image-night">{picture(image_dark)}</span>'
        return picture(src)
    return placeholder_art(seed, kind, tone, composition, class_name)


def story_card(headline: str, href: str = "#", blurb: str | None = None, kicker: str | None = None, meta: str | None = None,
               image: str | None = None, image_alt: str = "", image_seed=None, image_tone: str | None = None,
               provenance=None, size: str = "large", class_name: str | None = None, image_dark: str | None = None) -> str:
    chosen_size = "small" if size == "small" else "large"
    seed = image_seed or href or headline
    ratio = "mom-ratio-wide" if chosen_size == "small" else "mom-ratio-photo"
    parts = [
        card_image(image, image_alt, seed, tone=image_tone, class_name=ratio, image_dark=image_dark),
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


def reference_status(status: str | None, actor: str | None) -> tuple[str, str]:
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
                   stars=None, class_name: str | None = None) -> str:
    label, role = reference_status(status, actor)
    seed = image_seed or href or title
    chosen_kind = kind or ("paper" if is_research_paper_location(href) or is_research_paper_location(host) else None)
    site_html = f'<span class="mom-reference-card-site">{_text(site_name)}</span>' if site_name else ""
    meter = confidence_meter(confidence) if confidence is not None and status == "recommended" else ""
    rating = star_rating(stars) if stars and status != "recommended" else ""
    meta = " · ".join(part for part in (host, meta_date) if part)
    return (
        f'<a class="{join_class_names("mom-reference-card", class_name)}" href="{_text(href)}">'
        f'<span class="mom-reference-card-media">{card_image(image, "", seed, chosen_kind, image_tone, class_name="mom-ratio-wide")}{site_html}</span>'
        f'<span class="mom-reference-status mom-reference-status-{role}">{_text(label)}</span>'
        f'<span class="mom-reference-card-title">{_text(title)}</span>'
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
        f'{anchor_html}<span class="mom-thread-card-title">{_text(title)}</span>{card_image(image, "", seed, tone=image_tone, class_name="mom-thread-card-thumb")}'
        f'{latest_html}<span class="mom-meta mom-thread-card-meta">{_text(meta)}</span></a>'
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


def wiki_card(term: str, href: str = "#", relation: str | None = None, definition: str | None = None, class_name: str | None = None) -> str:
    relation_html = f'<span class="mom-wiki-card-relation">{_text(relation)}</span>' if relation else ""
    definition_html = f'<span class="mom-wiki-card-definition">{_text(definition)}</span>' if definition else ""
    return (
        f'<a class="{join_class_names("mom-wiki-card", class_name)}" href="{_text(href)}">'
        f'<span class="mom-wiki-card-head"><span class="mom-wiki-card-term">{_text(term)}</span>{relation_html}</span>{definition_html}</a>'
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

