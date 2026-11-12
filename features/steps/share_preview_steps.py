import struct

from behave import then

DEFAULT_PICTURE_PATH = "assets/share/mom-share-default.png"


@then("the page names the default link preview picture in its Open Graph and Twitter tags")
def step_names_default_picture(context):
    for tag in ('property="og:image"', 'name="twitter:image"'):
        pattern = f'<meta {tag} content="'
        start = context.page.find(pattern)
        assert start >= 0, f"{context.route} has no {tag} tag"
        address = context.page[start + len(pattern):].split('"', 1)[0]
        assert address.startswith("https://") and address.endswith("/" + DEFAULT_PICTURE_PATH), address


@then("the page asks for a large Twitter card")
def step_large_card(context):
    assert '<meta name="twitter:card" content="summary_large_image">' in context.page


@then("the default link preview picture is published as a 1200 by 630 picture")
def step_picture_published(context):
    header = (context.output_directory / DEFAULT_PICTURE_PATH).read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", header[16:24]) == (1200, 630)
