"""Steps for features/video-embeds.feature: a stock reference tile drawn as the site's card, with the player when the platform embeds."""

import re

from behave import given, then, when

from projection_support import REPOSITORY_ROOT


@given('a reference tile for the address "{address}" titled "{title}"')
def step_tile(context, address, title):
    context.tile = (
        '<article class="home-page-tile" data-status="accepted"><img class="home-page-image" src="/assets/picture.jpg">'
        '<p class="home-page-eyebrow">youtube.com</p>'
        f'<h3 class="home-page-title"><a href="{address}">{title}</a></h3>'
        '<span data-stars="5"></span><p>Accepted <time datetime="2026-11-06">6 Nov 2026</time></p></article>'
    )


@when("the tile is drawn as a card")
def step_draw(context):
    import hooks
    context.card = hooks.STOCK_TILE.sub(hooks._tile_to_reference_card, context.tile)


def _play_button(card):
    found = re.search(r'<button type="button" class="mom-video-poster"[^>]*>', card)
    assert found, card
    return found.group(0)


@given('a reference tile with no picture for the address "{address}" titled "{title}"')
def step_tile_without_picture(context, address, title):
    step_tile(context, address, title)
    context.tile = context.tile.replace('<img class="home-page-image" src="/assets/picture.jpg">', "")


@then('the card has a Play button that starts the player at "{source}"')
def step_player(context, source):
    assert f'data-player-src="{source.replace("&", "&amp;")}"' in _play_button(context.card), _play_button(context.card)


@then("the Play button's face is the card's picture")
def step_face_picture(context):
    face = re.search(r'<button type="button" class="mom-video-poster".*?</button>', context.card, re.S).group(0)
    assert '<img class="mom-card-image"' in face and 'src="/assets/picture.jpg"' in face, face


@then("the Play button's face is the site's placeholder art")
def step_face_art(context):
    face = re.search(r'<button type="button" class="mom-video-poster".*?</button>', context.card, re.S).group(0)
    assert "mom-art" in face and "<img" not in face, face


@then("the card has no player")
def step_no_player(context):
    assert "<iframe" not in context.card and "mom-video-poster" not in context.card, context.card


@then("the card has no player frame yet")
def step_no_frame(context):
    assert "<iframe" not in context.card, context.card


@then('the Play button is named "{name}"')
def step_button_name(context, name):
    assert f'aria-label="{name}"' in _play_button(context.card), _play_button(context.card)


@then('the Play button carries the player\'s title "{title}"')
def step_button_title(context, title):
    assert f'data-player-title="{title}"' in _play_button(context.card), _play_button(context.card)


@then("the Play button lets the player start itself")
def step_button_allow(context):
    assert re.search(r'data-player-allow="[^"]*\bautoplay\b', _play_button(context.card)), _play_button(context.card)


@then('the card\'s headline links to "{address}"')
def step_headline_link(context, address):
    assert re.search(rf'<a class="mom-reference-card-title" href="{re.escape(address)}">', context.card), context.card


@then("the card is not itself a link")
def step_not_link(context):
    assert context.card.startswith("<div "), context.card[:80]


@then("the card shows the source and the date under the headline")
def step_meta(context):
    assert context.card.index("mom-reference-card-title") < context.card.index("mom-stars") < context.card.index("youtube.com · 6 November 2026"), context.card


@then('the card is a link to "{address}" with a picture')
def step_plain_link(context, address):
    assert context.card.startswith(f'<a class="mom-reference-card" href="{address}">') and "<img" in context.card, context.card


@then('the stylesheet "{path}" gives the player the picture\'s ratio, no border and the full width of its slot')
def step_stylesheet(context, path):
    css = (REPOSITORY_ROOT / "web" / path.lstrip("/")).read_text(encoding="utf-8")
    rule = re.search(r"\.mom-video-frame iframe\s*\{([^}]*)\}", css).group(1)
    assert "aspect-ratio: var(--ratio-media)" in rule and "border: 0" in rule and "width: 100%" in rule, rule


@then('the site\'s frame-src policy allows "{first}" and "{second}"')
def step_frame_policy(context, first, second):
    import json
    from papyrus_content.markus_renderer.video import VideoRendering, csp_text
    providers = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text(encoding="utf-8"))["embeds"]["providers"]
    policy = csp_text(VideoRendering(providers=tuple(providers)))
    assert first in policy and second in policy, policy


@then('the stylesheet "{path}" draws the Play button without border, with a focus outline and a label beside its icon')
def step_play_stylesheet(context, path):
    css = (REPOSITORY_ROOT / "web" / path.lstrip("/")).read_text(encoding="utf-8")
    button = re.search(r"\.mom-video-poster\s*\{([^}]*)\}", css).group(1)
    assert "border: 0" in button and "width: 100%" in button, button
    assert re.search(r"\.mom-video-poster:focus-visible\s*\{[^}]*outline: 3px solid", css), "no focus outline"
    assert re.search(r"\.mom-video-play\s*\{[^}]*display: inline-flex", css), "icon and label are not side by side"
