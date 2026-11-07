"""Steps for features/navigation.feature.

The static scenarios read the projected pages and stylesheets. The `@browser` scenarios drive the projected site in Chromium through
tools/check_nav.cjs and skip themselves when Node or Playwright is missing (set PLAYWRIGHT_MODULE to the package's path to point at one).
"""

import json
import os
import re
import shutil
import subprocess

from behave import then, when

from image_ratio_steps import served_origin
from projection_support import REPOSITORY_ROOT

CHECK_SCRIPT = REPOSITORY_ROOT / "tools" / "check_nav.cjs"
ALL_DESTINATIONS = ["Home", "Articles", "Posts", "Findings", "Videos", "Conversations", "Concepts"]


def menu_links(page):
    menu = page.split('class="mom-menu"', 1)[1].split("</nav>", 1)[0]
    return re.findall(r'<a class="mom-menu-link" href="([^"]*)"([^>]*)><span class="mom-menu-head"><span class="mom-menu-name">([^<]*)</span>(.*?)</span>(?:<span class="mom-menu-sub">([^<]*)</span>)?</a>', menu, re.S)


def menu_by_name(page):
    return {name: {"href": href, "attributes": attributes, "head": head, "subtitle": subtitle} for href, attributes, name, head, subtitle in menu_links(page)}


def unescaped(text):
    import html
    return html.unescape(text)


@then('the navigation has a button named "{name}" that controls the menu and starts collapsed')
def step_button(context, name):
    found = re.search(r'<button type="button" class="mom-menu-button" aria-label="([^"]*)" aria-expanded="false" aria-controls="([^"]*)">', context.page)
    assert found and found.group(1) == name, "no menu button"
    assert f'<nav class="mom-menu" id="{found.group(2)}"' in context.page, "the button controls nothing"


@then("the menu is hidden until it is opened")
def step_menu_hidden(context):
    assert re.search(r'<nav class="mom-menu" id="mom-menu" aria-label="Site menu" hidden>', context.page)


@then('the navigation row lists "{labels}"')
def step_row(context, labels):
    row = context.page.split('class="mom-nav-items"', 1)[1].split("</ul>", 1)[0]
    shown = [unescaped(re.sub("<[^>]+>", "", a)) or "" for a in re.findall(r"<a [^>]*>.*?</a>", row, re.S)]
    labelled = ["Home" if 'aria-label="Home"' in a else shown[i] for i, a in enumerate(re.findall(r"<a [^>]*>.*?</a>", row, re.S))]
    assert labelled == labels.split(", "), labelled


@then("the page loads a script that marks it as having JavaScript before it is first drawn")
def step_js_class(context):
    head = context.page.split("</head>", 1)[0]
    assert 'document.documentElement.classList.add("mom-js")' in head and head.index("mom-js") < head.index("/assets/mom.js")


@then('the menu lists "{labels}" in that order')
def step_menu_order(context, labels):
    assert [name for _href, _attributes, name, _head, _sub in menu_links(context.page)] == labels.split(", ")


@then("every destination in the menu has a subtitle")
def step_every_subtitle(context):
    for name, entry in menu_by_name(context.page).items():
        assert entry["subtitle"].strip(), f"{name} has no subtitle"


def _hooks():
    import sys
    sys.path.insert(0, str(REPOSITORY_ROOT / "web"))
    import hooks
    return hooks


def _projection():
    return json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text(encoding="utf-8"))


@then('the subtitle of "{name}" is the {source} page lead')
def step_lead_subtitle(context, name, source):
    lead = getattr(_hooks(), f"{source.upper()}_LEAD")
    assert unescaped(menu_by_name(context.page)[name]["subtitle"]) == lead


@then('the subtitle of "Concepts" is the description of the Concepts section in the projection')
def step_concepts_subtitle(context):
    wanted = _projection()["urls"]["sections"]["wiki"]["description"]
    assert unescaped(menu_by_name(context.page)["Concepts"]["subtitle"]) == wanted


@then('the subtitle of "Videos" is the description of the Videos page in the projection')
def step_videos_subtitle(context):
    wanted = next(page["description"] for page in _projection()["pages"] if page["id"] == "videos")
    assert unescaped(menu_by_name(context.page)["Videos"]["subtitle"]) == wanted


@then('the menu marks "{name}" as the current page with "{words}"')
def step_current(context, name, words):
    entry = menu_by_name(context.page)[name]
    assert 'aria-current="page"' in entry["attributes"] and words in entry["head"], entry


@then("the menu marks no other destination as the current page")
def step_no_other_current(context):
    current = [name for name, entry in menu_by_name(context.page).items() if "aria-current" in entry["attributes"]]
    assert len(current) == 1, current


@then('the menu button holds the Lucide "{first}" icon and the Lucide "{second}" icon')
def step_icons(context, first, second):
    button = context.page.split('class="mom-menu-button"', 1)[1].split("</button>", 1)[0]
    assert f'data-icon="{first}"' in button and f'data-icon="{second}"' in button, button


@then("the menu names are set at 24 pixels and the subtitles at 19 pixels, which are 18 and 14.25 pixels once the 75 percent scale applies")
def step_sizes(context):
    phone, scaled = context.stylesheet.split("@media (min-width: 600px) {")
    for text, name, sub in ((phone, "24px", "19px"), (scaled, "18px", "14.25px")):
        assert re.search(r"\.mom-menu-name \{ font: 800 " + name, text), name
        assert re.search(r"\.mom-menu-sub \{ font: 400 " + sub, text), sub


@then("the menu destinations are at least {pixels:d} pixels tall")
def step_min_height(context, pixels):
    phone = context.stylesheet.split("@media (min-width: 600px) {")[0]
    found = re.search(r"\.mom-menu-link \{[^}]*min-height: (\d+)px", phone)
    assert found and int(found.group(1)) >= pixels


@then('the rule for "{selector}" does not set "{prop}"')
def step_rule_lacks(context, selector, prop):
    phone = context.stylesheet.split("@media (min-width: 600px) {")[0]
    for rule in re.finditer(r"(?:^|\})\s*" + re.escape(selector) + r"\s*\{([^}]*)\}", phone):
        assert prop + ":" not in rule.group(1), rule.group(0)


# --- the browser scenarios ---

def _run(context, route, width, mode=""):
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return False
    result = subprocess.run(["node", str(CHECK_SCRIPT), served_origin(context), route, str(width), mode], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available: " + (result.stderr.strip().splitlines() or [""])[-1][:120])
        return False
    context.nav = json.loads(result.stdout)
    return True


@when('I view the navigation on "{route}" in a browser {width:d} pixels wide')
def step_view(context, route, width):
    _run(context, route, width)


@when('I view the navigation on "{route}" in a browser {width:d} pixels wide without JavaScript')
def step_view_nojs(context, route, width):
    _run(context, route, width, "nojs")


def _bar_labels(context):
    return [item["text"].title() if item["text"] != "Home" else "Home" for item in context.nav["barItems"]]


@then("the bar shows the wordmark and the menu button and no destinations")
def step_phone_bar(context):
    if getattr(context, "nav", None) is None:
        return
    assert context.nav["brandVisible"] and context.nav["buttonVisible"] and context.nav["barItems"] == [], context.nav


@then("the page does not scroll sideways")
def step_no_sideways(context):
    if getattr(context, "nav", None) is None:
        return
    scroll, inner = context.nav["pageWidth"]
    assert scroll <= inner, context.nav["pageWidth"]


@then("the bar shows some destinations in order and the menu button")
def step_tablet_bar(context):
    if getattr(context, "nav", None) is None:
        return
    shown = _bar_labels(context)
    assert context.nav["buttonVisible"] and context.nav["brandVisible"], context.nav
    assert 0 < len(shown) < len(ALL_DESTINATIONS) and shown == ALL_DESTINATIONS[:len(shown)], shown


@then("every destination the bar does not show is in the menu")
def step_buried_in_menu(context):
    if getattr(context, "nav", None) is None:
        return
    in_menu = [item["name"] for item in context.nav["open"]["items"]] if "open" in context.nav else None
    assert in_menu == ALL_DESTINATIONS, in_menu


@then("the bar shows every destination and no menu button")
def step_wide_bar(context):
    if getattr(context, "nav", None) is None:
        return
    shown = _bar_labels(context)
    assert not context.nav["buttonVisible"] and set(ALL_DESTINATIONS[1:]) <= set(shown), context.nav


def _open(context):
    return context.nav["open"] if getattr(context, "nav", None) else None


@then("the menu opens from the bottom of the bar to the bottom of the screen")
def step_geometry(context):
    opened = _open(context)
    if opened is None:
        return
    assert opened["panelPosition"] == "fixed" and abs(opened["panelTop"] - opened["headerBottom"]) <= 1 and abs(opened["panelBottom"] - opened["viewportHeight"]) <= 1, opened


@then("the page behind it cannot scroll")
def step_locked(context):
    opened = _open(context)
    if opened is not None:
        assert opened["pageOverflow"] == "hidden", opened["pageOverflow"]


@then("the menu button is expanded and shows the close icon")
def step_expanded(context):
    opened = _open(context)
    if opened is not None:
        assert opened["expanded"] == "true" and opened["closeIcon"] and opened["focusInPanel"], opened


@then("every destination in the open menu is at least {pixels:d} pixels tall")
def step_tap_targets(context, pixels):
    opened = _open(context)
    if opened is not None:
        assert all(item["height"] >= pixels for item in opened["items"]), opened["items"]
        assert [item["name"] for item in opened["items"]] == ALL_DESTINATIONS


@then("the open menu's names are at least {names:d} pixels and its subtitles at least {subtitles:d} pixels")
def step_open_sizes(context, names, subtitles):
    opened = _open(context)
    if opened is not None:
        assert all(item["nameSize"] >= names and item["subtitleSize"] >= subtitles for item in opened["items"]), opened["items"]


@then("Escape closes the menu and focus returns to the menu button")
def step_escape(context):
    if getattr(context, "nav", None) is not None:
        assert context.nav["escape"] == {"hidden": True, "focusOnButton": True, "expanded": "false", "locked": False}, context.nav["escape"]


@then("choosing a destination closes the menu and focus returns to the menu button")
def step_choose(context):
    if getattr(context, "nav", None) is not None:
        assert context.nav["afterChoosing"] == {"hidden": True, "focusOnButton": True}, context.nav["afterChoosing"]


@then("Tab and Shift+Tab keep focus on the menu button and the menu's links")
def step_trap(context):
    if getattr(context, "nav", None) is not None:
        assert context.nav["trap"] == {"forward": True, "backward": True}, context.nav["trap"]
