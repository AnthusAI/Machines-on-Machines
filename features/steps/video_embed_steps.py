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


@then('the card has a player from "{source}"')
def step_player(context, source):
    assert f'<iframe src="{source.replace("&", "&amp;")}"' in context.card, context.card


@then("the card has no picture")
def step_no_picture(context):
    assert "<img" not in context.card, context.card


@then("the card has no player")
def step_no_player(context):
    assert "<iframe" not in context.card, context.card


@then("the player loads lazily")
def step_lazy(context):
    assert 'loading="lazy"' in re.search(r"<iframe[^>]*>", context.card).group(0)


@then("the player does not autoplay")
def step_no_autoplay(context):
    tag = re.search(r"<iframe[^>]*>", context.card).group(0)
    assert "autoplay" not in tag, tag


@then('the player\'s title is "{title}"')
def step_title(context, title):
    assert f'title="{title}"' in re.search(r"<iframe[^>]*>", context.card).group(0)


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
