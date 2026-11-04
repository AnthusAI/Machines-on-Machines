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
               composition: str | None = None, class_name: str | None = None) -> str:
    """The card's image, or `PlaceholderArt` when there is none. An image that fails to load is swapped for the same art by `assets/mom.js`."""
    if src:
        classes = join_class_names("mom-card-image", class_name)
        kind_attribute = f' data-art-kind="{_text(kind)}"' if kind else ""
        return f'<img class="{classes}" src="{_text(src)}" alt="{_text(alt)}" loading="lazy" data-art-seed="{_text(seed)}"{kind_attribute}>'
    return placeholder_art(seed, kind, tone, composition, class_name)


def story_card(headline: str, href: str = "#", blurb: str | None = None, kicker: str | None = None, meta: str | None = None,
               image: str | None = None, image_alt: str = "", image_seed=None, image_tone: str | None = None,
               provenance=None, size: str = "large", class_name: str | None = None) -> str:
    chosen_size = "small" if size == "small" else "large"
    seed = image_seed or href or headline
    ratio = "mom-ratio-wide" if chosen_size == "small" else "mom-ratio-photo"
    parts = [
        card_image(image, image_alt, seed, tone=image_tone, class_name=ratio),
        f'<span class="mom-kicker">{_text(kicker)}</span>' if kicker else "",
        provenance_chips(provenance),
        f'<span class="mom-story-card-headline">{_text(headline)}</span>',
        f'<span class="mom-blurb">{_text(blurb)}</span>' if blurb else "",
        f'<span class="mom-meta">{_text(meta)}</span>' if meta else "",
    ]
    classes = join_class_names("mom-story-card", f"mom-story-card-{chosen_size}", class_name)
    return f'<a class="{classes}" href="{_text(href)}">{"".join(parts)}</a>'


def confidence_meter(confidence) -> str:
    confidence_fraction = clamp_between_zero_and_one(confidence)
    filled_segment_count = js_round(confidence_fraction * METER_SEGMENT_COUNT)
    percent_label = f"{js_round(confidence_fraction * 100)}% confidence"
    segments = "".join(
        '<span class="mom-meter-segment mom-meter-segment-filled"></span>' if index < filled_segment_count else '<span class="mom-meter-segment"></span>'
        for index in range(METER_SEGMENT_COUNT)
    )
    return (
        f'<span class="mom-meter"><span class="mom-meter-track" role="img" aria-label="{percent_label}">{segments}</span>'
        f'<span class="mom-meter-label">{percent_label}</span></span>'
    )


def reference_status(status: str | None, actor: str | None) -> tuple[str, str]:
    if status == "recommended":
        return REFERENCE_STATUS_LABELS["recommended"]
    return REFERENCE_STATUS_LABELS.get(f"accepted-{actor}", REFERENCE_STATUS_LABELS["accepted-automatic"])


def reference_card(title: str, href: str = "#", status: str | None = None, actor: str | None = None, summary: str | None = None,
                   image: str | None = None, image_seed=None, image_tone: str | None = None, site_name: str | None = None,
                   host: str | None = None, meta_date: str | None = None, confidence=None, kind: str | None = None,
                   class_name: str | None = None) -> str:
    label, role = reference_status(status, actor)
    seed = image_seed or href or title
    chosen_kind = kind or ("paper" if is_research_paper_location(href) or is_research_paper_location(host) else None)
    site_html = f'<span class="mom-reference-card-site">{_text(site_name)}</span>' if site_name else ""
    meter = confidence_meter(confidence) if confidence is not None and status == "recommended" else ""
    meta = " · ".join(part for part in (host, meta_date) if part)
    return (
        f'<a class="{join_class_names("mom-reference-card", class_name)}" href="{_text(href)}">'
        f'<span class="mom-reference-card-media">{card_image(image, "", seed, chosen_kind, image_tone, class_name="mom-ratio-wide")}{site_html}</span>'
        f'<span class="mom-reference-status mom-reference-status-{role}">{_text(label)}</span>'
        f'<span class="mom-reference-card-title">{_text(title)}</span>'
        + (f'<span class="mom-reference-card-summary">{_text(summary)}</span>' if summary else "")
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
    anchor_html = f'<span class="mom-meta">{_text(anchor)}</span>' if anchor else ""
    return (
        f'<a class="{join_class_names("mom-thread-card", class_name)}" href="{_text(href)}">'
        f'<span class="mom-thread-card-head">{card_image(image, "", seed, tone=image_tone, class_name="mom-thread-card-thumb")}'
        f'<span class="mom-thread-card-heading">{anchor_html}<span class="mom-thread-card-title">{_text(title)}</span></span></span>'
        f'{latest_html}<span class="mom-meta">{_text(meta)}</span></a>'
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


def pull_quote(text: str, caption: str | None = "Pull quote chosen by the editor", class_name: str | None = None) -> str:
    caption_html = f'<figcaption class="mom-pull-quote-caption">{_text(caption)}</figcaption>' if caption else ""
    return (
        f'<figure class="{join_class_names("mom-pull-quote", class_name)}">'
        f'<blockquote class="mom-pull-quote-text">{_text(text)}</blockquote>{caption_html}</figure>'
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


def article_actions(page_path: str, title: str = "") -> str:
    """View as Markdown, and a popup that shares the web page or its Markdown. The script fills in the full addresses."""
    markdown_path = page_path.rstrip("/") + "/index.md"
    return (
        '<div class="mom-article-actions">'
        f'<a class="mom-icon-button" href="{_text(markdown_path)}" aria-label="View as Markdown" title="View as Markdown">{MARKDOWN_MARK}</a>'
        f'<div class="mom-share" data-mom-share data-title="{_text(title)}">'
        f'<button type="button" class="mom-icon-button" aria-label="Share" title="Share" aria-expanded="false">{SHARE_ICON}</button>'
        '<div class="mom-share-panel" hidden>'
        f'<button type="button" data-share-path="{_text(page_path)}">Share the web page</button>'
        f'<button type="button" data-share-path="{_text(markdown_path)}">Share the Markdown</button>'
        '<p class="mom-share-status" role="status"></p>'
        "</div></div></div>"
    )

