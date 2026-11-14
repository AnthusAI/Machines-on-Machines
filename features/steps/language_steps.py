"""Steps for features/language-switcher.feature.

The static scenarios read pages projected by tests/language_cases.py (a fixture site with translations). The `@browser` scenarios drive that site in
Chromium through tools/check_language_switcher.cjs and skip themselves when Node or Playwright is missing (set PLAYWRIGHT_MODULE to the package's path).
"""

import html
import json
import os
import re
import shutil
import subprocess

from behave import given, then, when

from image_ratio_steps import served_directory_origin  # noqa: E402
from projection_support import REPOSITORY_ROOT, page_text, project_language_case  # noqa: E402

CHECK_SCRIPT = REPOSITORY_ROOT / "tools" / "check_language_switcher.cjs"
LANGUAGE_SCRIPT = REPOSITORY_ROOT / "web" / "assets" / "mom-language.js"
STYLESHEET_SOURCES = (REPOSITORY_ROOT / "design" / "system" / "components" / "bundle.css", REPOSITORY_ROOT / "web" / "css-src" / "site-theme.src.css")
OPTION = re.compile(r'<a class="mom-language-option[^"]*" href="([^"]*)" lang="([^"]*)" hreflang="([^"]*)" data-language="([^"]*)"( aria-current="true")?>'
                    r'<span class="mom-language-name">([^<]*)</span>(<svg.*?</svg>)?</a>', re.S)
ENGLISH = "/field-notes/steer-a-story/"
SPANISH = "/es/field-notes/dirigir-una-historia/"
CHINESE = "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/"
NOTE_UNDO = "撤销"


PROJECTED = {}  # the language case is projected once for the whole run: Papyrus's multilingual projection of the fixture site takes a while, and no scenario changes it


@given("the language case is projected")
def step_projected(context):
    if "public" not in PROJECTED:
        PROJECTED["public"] = project_language_case()
    context.language_directory = PROJECTED["public"]


@given("the language case is projected with translations published but no language public")
def step_projected_not_public(context):
    from language_cases import NOT_PUBLIC
    if "private" not in PROJECTED:
        PROJECTED["private"] = project_language_case(languages=NOT_PUBLIC)
    context.language_directory = PROJECTED["private"]


@when('I open the language page "{route}"')
def step_open(context, route):
    context.language_route = route
    context.language_page = page_text(context.language_directory, route)


def bar_options(page):
    return OPTION.findall(page.split('<ul class="mom-language-list">', 1)[1].split("</ul>", 1)[0]) if '<ul class="mom-language-list">' in page else []


def menu_options(page):
    return OPTION.findall(page.split('<ul class="mom-menu-language-list">', 1)[1].split("</ul>", 1)[0]) if '<ul class="mom-menu-language-list">' in page else []


def names(options):
    return [option[5] for option in options]


def head_of(page):
    return page.split("</head>", 1)[0]


@then('the switcher lists "{expected}" in that order')
def step_lists(context, expected):
    assert names(bar_options(context.language_page)) == expected.split(", "), names(bar_options(context.language_page))


@then('the switcher\'s control is named "{name}" and shows the Lucide "languages" icon')
def step_control(context, name):
    found = re.search(r'<summary class="mom-language-trigger" aria-label="([^"]*)">(<svg[^>]*data-icon="languages")?', context.language_page)
    assert found and html.unescape(found.group(1)) == name, found and found.group(1)
    assert found.group(2), "no Languages icon"


@then("no language is drawn as a flag or a picture")
def step_no_flags(context):
    switcher = context.language_page.split('data-mom-language-switcher>', 1)[1].split("</details>", 1)[0]
    assert "<img" not in switcher and "<picture" not in switcher
    assert not re.search("[\U0001F1E6-\U0001F1FF]", switcher), "a flag emoji"
    assert not re.search(r"flag", switcher, re.I)


@then('the switcher links "English" to "{english}", "Español" to "{spanish}" and "中文" to "{chinese}"')
def step_links(context, english, spanish, chinese):
    found = {option[5]: option[0] for option in bar_options(context.language_page)}
    assert found == {"English": english, "Español": spanish, "中文": chinese}, found


@then('every switcher option has lang and hreflang equal to its language tag "{tags}"')
def step_tags(context, tags):
    options = bar_options(context.language_page)
    assert [option[1] for option in options] == tags.split(", ") and [option[2] for option in options] == tags.split(", "), options


@then('the control shows "{name}" as the current language')
def step_current_name(context, name):
    assert f'<span class="mom-language-current">{name}</span>' in context.language_page


@then('only the "{name}" option has aria-current and a check mark')
def step_only_current(context, name):
    for options in (bar_options(context.language_page), menu_options(context.language_page)):
        marked = [option[5] for option in options if option[4]]
        checked = [option[5] for option in options if option[6]]
        assert marked == [name] and checked == [name], (marked, checked)


@then('the page\'s html lang is "{tag}"')
def step_html_lang(context, tag):
    assert f'<html lang="{tag}">' in context.language_page.split("\n", 2)[1], context.language_page[:80]


@then('the page has no hreflang for "{tag}"')
def step_no_hreflang(context, tag):
    assert f'hreflang="{tag}"' not in context.language_page


@then("the page has no language switcher, no welcoming banner, no language script and no hreflang")
def step_nothing(context):
    page = context.language_page
    for needle in ("mom-language-switcher", "mom-language-banner", "mom-language.js", "mom-language-data", "hreflang", "mom-menu-languages"):
        assert needle not in page, needle


@then('the page has hreflang links for "{tags}" with absolute addresses of the matching pages')
def step_hreflang(context, tags):
    links = dict(re.findall(r'<link rel="alternate" hreflang="([^"]*)" href="([^"]*)">', head_of(context.language_page)))
    expected = {"en": ENGLISH, "es-419": SPANISH, "zh-Hans": CHINESE}
    for tag in tags.split(", "):
        assert links[tag] == "https://machines-on-machines.anth.us" + expected[tag], (tag, links.get(tag))


@then("the page has an x-default hreflang that is the English page")
def step_x_default(context):
    assert f'<link rel="alternate" hreflang="x-default" href="https://machines-on-machines.anth.us{ENGLISH}">' in head_of(context.language_page)


@then("the page is canonical to itself")
def step_canonical(context):
    assert f'<link rel="canonical" href="https://machines-on-machines.anth.us{context.language_route}">' in head_of(context.language_page)


@then('the menu lists the languages "{expected}" under a heading named in the page\'s language')
def step_menu(context, expected):
    assert names(menu_options(context.language_page)) == expected.split(", ")
    assert re.search(r'<h2 class="mom-menu-languages-title" id="mom-menu-languages-title"><svg[^>]*data-icon="languages".*?</svg><span>Language</span></h2>', context.language_page, re.S)
    assert context.language_page.index('class="mom-menu-languages"') > context.language_page.index('class="mom-menu"')


@then("the welcoming banner is hidden, empty and comes right after the skip link")
def step_banner(context):
    page = context.language_page
    assert re.search(r'<a class="markus-skip-link" href="#main">[^<]*</a>\s*<div class="mom-language-banner" data-mom-language-banner hidden>', page), "not right after the skip link"
    assert page.index("data-mom-language-banner") < page.index('<header class="mom-masthead">')
    assert '<span class="mom-language-banner-message"></span>' in page and 'role="status" aria-live="polite"></p>' in page


@then("the banner's words for every language of the group are in the page as JSON")
def step_json(context):
    data = json.loads(re.search(r'<script type="application/json" id="mom-language-data">(.*?)</script>', context.language_page, re.S).group(1))
    assert data["primary"] == "en" and sorted(data["strings"]) == ["en", "es-419", "zh-Hans"]
    for strings in data["strings"].values():
        for key in ("noticed", "countdown", "switchNow", "stay", "pause", "resume", "announce", "switched", "undo", "readInThisLanguage"):
            assert strings[key], key


@then("the language script is in the head without defer")
def step_script_head(context):
    head = head_of(context.language_page)
    assert '<script src="/assets/mom-language.js"></script>' in head
    assert head.index('id="mom-language-data"') < head.index("mom-language.js"), "the script runs before the data it reads"
    assert head.index("hreflang") < head.index("mom-language.js"), "the script runs before the links it reads"


@then('the language script never reads or writes a cookie and keeps the choice only in localStorage under "{key}"')
def step_no_cookie(context, key):
    script = LANGUAGE_SCRIPT.read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", script, flags=re.S)
    assert "cookie" not in code.lower()
    assert f'"{key}"' in script and re.search(r'write\("localStorage", READING_LANGUAGE_KEY', script)
    assert "try {" in script and "catch (error)" in script, "storage access is not wrapped"


@then("the language script gives the primary language a link and never a countdown")
def step_primary_rule(context):
    script = LANGUAGE_SCRIPT.read_text(encoding="utf-8")
    assert 'if (best === primary) {' in script and 'mode: "read"' in script
    assert script.count('mode: "offer"') == 1 and "target: best" in script
    assert "best === primary" in script.split('mode: "offer"')[0], "the offer is reachable for the primary language"


@then('Traditional Chinese preferences match no page and Simplified ones match "{tag}"')
def step_traditional(context, tag):
    script = LANGUAGE_SCRIPT.read_text(encoding="utf-8")
    result = subprocess.run(
        ["node", "-e", "const source = require('fs').readFileSync(process.argv[1], 'utf8'); "
         "const match = source.match(/function preferenceMeansLanguage[\\s\\S]*?\\n  }\\n/)[0]; eval(match + ';globalThis.m = preferenceMeansLanguage');"
         "console.log(JSON.stringify(['zh-CN','zh-SG','zh-Hans','zh','zh-Hans-CN','zh-TW','zh-HK','zh-Hant','es-MX','es','en-US'].map(p => [p, m(p, 'zh-Hans'), m(p, 'es-419'), m(p, 'en')])))", str(LANGUAGE_SCRIPT)],
        capture_output=True, text=True)
    if shutil.which("node") is None or result.returncode != 0:
        context.scenario.skip("Node is not available")
        return
    found = {row[0]: row[1:] for row in json.loads(result.stdout)}
    for simplified in ("zh-CN", "zh-SG", "zh-Hans", "zh", "zh-Hans-CN"):
        assert found[simplified][0], simplified
    for traditional in ("zh-TW", "zh-HK", "zh-Hant"):
        assert found[traditional] == [False, False, False], traditional
    assert found["es-MX"] == [False, True, False] and found["es"][1] and found["en-US"] == [False, False, True]
    assert tag in script


@then("the switcher and banner rules draw no border, and the focus outline is the only outline")
def step_no_borders(context):
    for path in STYLESHEET_SOURCES:
        for selectors, body in re.findall(r"([^{}]*\.mom-(?:language|menu-language)[^{}]*)\{([^}]*)\}", path.read_text(encoding="utf-8")):
            assert not re.search(r"(?<![\w-])border(-(top|right|bottom|left|width|style|color)[a-z-]*)?\s*:(?!\s*(?:0|none)\s*(?:;|$))", body), (selectors, body)
            assert "box-shadow" not in body, (selectors, body)
            if re.search(r"\boutline\s*:", body):
                assert ":focus-visible" in selectors, selectors


@then("with reduced motion the countdown bar is not drawn and nothing fades")
def step_reduced_motion(context):
    css = STYLESHEET_SOURCES[0].read_text(encoding="utf-8")
    block = css.split("@media (prefers-reduced-motion: reduce) {\n  .mom-language-banner-progress", 1)[1].split("}\n}", 1)[0]
    assert "display: none" in block and "transition: none" in block


# ---------------------------------------------------------------------------------------------- the browser scenarios

def run_check(context, scenario, width):
    if shutil.which("node") is None:
        context.scenario.skip("Node is not installed")
        return None
    result = subprocess.run(["node", str(CHECK_SCRIPT), served_directory_origin(context.language_directory), scenario, str(width)], capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        context.scenario.skip("Playwright is not available: " + (result.stderr.strip().splitlines() or [""])[-1][:120])
        return None
    context.measured = json.loads(result.stdout)
    context.width = width
    return context.measured


@when("I check the language switcher in a browser {width:d} pixels wide")
def step_check_switcher(context, width):
    run_check(context, "switcher", width)


@then('the control is in the bar and named "{name}"')
def step_in_bar(context, name):
    initial = context.measured["initial"]
    assert initial["triggerShown"] and initial["triggerName"] == name, initial
    assert initial["triggerBox"]["bottom"] < 120 and initial["triggerBox"]["right"] <= context.width, initial["triggerBox"]
    assert initial["triggerBox"]["height"] >= 33, "too small a target"


@then("the language list holds the three languages as links, the current one marked")
def step_list(context):
    options = context.measured["afterOpen"]["facts"]["barOptions"]
    assert [(o["text"], o["lang"], o["hreflang"], o["current"], o["mark"]) for o in options] == [
        ("English", "en", "en", "true", True), ("Español", "es-419", "es-419", None, False), ("中文", "zh-Hans", "zh-Hans", None, False)], options
    assert context.measured["listInside"], "the list leaves the screen"
    assert all(o["box"]["height"] >= 36 and o["fontSize"] >= 14 for o in options), options


@then("the language page does not scroll sideways")
def step_no_sideways(context):
    measured = context.measured
    found = [measured["initial"]["overflowX"]] if "initial" in measured else []
    found += [measured["afterOpen"]["facts"]["overflowX"]] if "afterOpen" in measured else []
    found += [measured["page"]["overflowX"]] if "page" in measured else []
    assert found and not any(found), found


@then("the control and the list are reachable by keyboard with a visible focus, and Escape closes the list")
def step_keyboard(context):
    assert context.measured["focusOutline"]["style"] == "solid" and context.measured["focusOutline"]["width"] >= 2, context.measured["focusOutline"]
    assert context.measured["afterOpen"]["open"] is True
    assert context.measured["afterEscape"] == {"open": False, "focusOnTrigger": True}


@then("the bar's control shows the icon alone at 48 pixels and the menu holds the three languages in 72 pixel blocks")
def step_phone(context):
    initial = context.measured["initial"]
    assert not initial["currentNameShown"] and initial["menuButtonShown"], initial
    assert round(initial["triggerBox"]["width"]) == 48 and round(initial["triggerBox"]["height"]) == 48, initial["triggerBox"]
    assert context.measured["menuOpen"]["shown"]
    options = context.measured["menuOptions"]
    assert [o["text"] for o in options] == ["English", "Español", "中文"] and all(round(o["box"]["height"]) >= 72 and o["fontSize"] >= 18 for o in options), options
    assert [o["current"] for o in options] == ["true", None, None]


@then("without JavaScript the control and its links are still there")
def step_no_javascript(context):
    without = context.measured["withoutJavaScript"]
    assert without["triggerShown"] and not without["overflowX"], without
    assert [o["text"] for o in without["barOptions"]] == ["English", "Español", "中文"]


@when("a browser {width:d} pixels wide that prefers Chinese opens the English page")
def step_offer(context, width):
    run_check(context, "offer", width)


@then("the banner is shown in Chinese before the masthead with Switch now, Stay here and Pause")
def step_banner_chinese(context):
    banner = context.measured["atLoad"]
    assert banner["shown"] and banner["mode"] == "offer" and banner["lang"] == "zh-Hans" and banner["beforeMasthead"], banner
    assert [action["text"] for action in banner["actions"]] == ["立即切换", "留在此页", "暂停"], banner["actions"]
    assert context.measured["page"]["path"] == ENGLISH and context.measured["page"]["lang"] == "en"


@then("the countdown reads 15 seconds, counts down and is announced once in a polite live region")
def step_countdown(context):
    first, later = context.measured["atLoad"], context.measured["afterFourSeconds"]
    assert "15" in first["count"] and "11" in later["count"], (first["count"], later["count"])
    assert first["liveRole"] == "status" and first["liveAria"] == "polite"
    assert first["live"] == later["live"] and "15" in first["live"], "the live region must not announce every second"


@then("Pause stops the clock and Resume starts it again")
def step_pause(context):
    assert context.measured["stillOnPageWhilePaused"] == ENGLISH, "the clock ran while paused"
    assert [action["text"] for action in context.measured["pausedBanner"]["actions"]][-1] == "继续", context.measured["pausedBanner"]["actions"]


@then("when the clock runs out the page is replaced by the Chinese page and the choice is remembered")
def step_leaves(context):
    arrived = context.measured["arrived"]
    assert arrived["path"] == CHINESE and arrived["lang"] == "zh-Hans" and arrived["stored"] == "zh-Hans", arrived
    assert context.measured["historyLength"] == 2, "replace must not leave the English page in the history"


@when("a browser 1440 pixels wide that prefers Chinese opens the page with no Chinese page")
def step_nothing(context):
    run_check(context, "nothing", 1440)


@then("there is no banner, the page stays and Chinese is not in the switcher")
def step_no_banner(context):
    found = context.measured["noChinesePage"]
    assert not found["banner"]["shown"] and found["page"]["path"] == "/field-notes/run-a-monitor/" and found["options"] == ["English", "Español"], found
    assert not context.measured["untranslated"]["banner"]["present"] and not context.measured["untranslated"]["hasSwitcher"]


@then("a Traditional Chinese browser is offered nothing on the Chinese page")
def step_traditional_browser(context):
    assert not context.measured["traditionalChinese"]["shown"], context.measured["traditionalChinese"]


@then("a Spanish browser from Mexico is offered the Spanish page")
def step_spanish_region(context):
    banner = context.measured["spanishRegion"]
    assert banner["shown"] and banner["lang"] == "es-419" and [action["text"] for action in banner["actions"]][0] == "Cambiar ahora", banner


@when("an English-preferring browser 1440 pixels wide opens the Spanish page")
def step_primary(context):
    run_check(context, "primary", 1440)


@then('the banner is a quiet "Read in English" link to the English page with no countdown')
def step_read_in_english(context):
    banner = context.measured["atLoad"]
    assert banner["shown"] and banner["mode"] == "read" and banner["lang"] == "en", banner
    assert banner["readHref"] == ENGLISH and banner["count"] == "" and "pause" not in [a["action"] for a in banner["actions"]], banner


@then("two minutes later the page has not moved")
def step_two_minutes(context):
    later = context.measured["afterTwoMinutes"]
    assert later["page"]["path"] == SPANISH and later["page"]["lang"] == "es-419" and later["banner"]["mode"] == "read", later


@then("a Chinese-preferring browser on the Chinese page sees no banner")
def step_chinese_on_chinese(context):
    assert not context.measured["chinesePageChinesePreference"]["shown"]


@when("a browser 1440 pixels wide that prefers Chinese stays on the English page")
def step_stay(context):
    run_check(context, "remember", 1440)


@then("after a reload and on another English page there is no banner and the page stays")
def step_stay_remembered(context):
    for key in ("afterStay", "afterReload", "otherEnglishPage"):
        found = context.measured[key]
        assert not found["banner"]["shown"] and found["page"]["lang"] == "en" and found["page"]["stored"] == "en", (key, found)


@when("an English-preferring browser 375 pixels wide picks 中文 in the switcher")
def step_pick(context):
    run_check(context, "remember", 375)


@then("the Chinese page opens and Chinese is remembered")
def step_picked(context):
    assert context.measured["afterPick"]["path"] == CHINESE and context.measured["afterPick"]["stored"] == "zh-Hans"


@then('opening the English page again opens the Chinese page with a note "{words}" and Undo, without adding to the history')
def step_note(context, words):
    remembered = context.measured["remembered"]
    assert remembered["page"]["path"] == CHINESE and remembered["banner"]["mode"] == "note" and remembered["banner"]["message"] == words, remembered
    assert [action["text"] for action in remembered["banner"]["actions"]][0] == NOTE_UNDO


@then("Undo returns to the English page and remembers English")
def step_undo(context):
    after = context.measured["afterUndo"]
    assert after["path"] == ENGLISH and after["lang"] == "en" and after["stored"] == "en", after
    assert not context.measured["afterUndoBanner"]["shown"]


@then("a remembered language leaves a page that does not exist in it alone")
def step_remembered_no_page(context):
    found = context.measured["rememberedButNoPage"]
    assert found["page"]["path"] == "/field-notes/run-a-monitor/" and not found["banner"]["shown"], found


@when("a browser 1440 pixels wide that prefers Chinese opens the English page with storage blocked")
def step_blocked(context):
    run_check(context, "remember", 1440)


@then("the banner is shown and the page raised no error")
def step_blocked_result(context):
    found = context.measured["storageBlocked"]
    assert found["banner"]["shown"] and found["errors"] == [], found


@when("a browser {width:d} pixels wide that prefers Chinese measures the English page as it loads")
def step_noshift(context, width):
    run_check(context, "noshift", width)


@then("the navigation bar never changes its position while the page loads and no layout shift is reported")
def step_noshift_result(context):
    for key in ("offer", "none"):
        found = context.measured[key]
        assert len(found["tops"]) == 1 and found["shifts"] < 0.001, (key, found)
    assert context.measured["offer"]["banner"] and not context.measured["none"]["banner"]


# ---------------------------------------------------------------------------------------------- links inside a translated page (features/language-links.feature)

ANCHOR = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.S)
MARKER = re.compile(r'<span class="mom-link-language">.*?<span class="mom-visually-hidden"[^>]*>([^<]*)</span></span>', re.S)
PAGE_PATH = re.compile(r"^/(?:[^./?#]+/)*$")
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]*)">')


def without_switcher(page):
    page = re.sub(r'<div class="mom-language-switcher" data-mom-language-switcher>.*?</details></div>', "", page, flags=re.S)
    return re.sub(r'<section class="mom-menu-languages".*?</section>', "", page, flags=re.S)


def anchors(page):
    found = []
    for attributes, inner in ANCHOR.findall(without_switcher(page)):
        href = re.search(r'\bhref="([^"]*)"', attributes)
        if href:
            marker = MARKER.search(inner)
            found.append({"href": html.unescape(href.group(1)), "attributes": attributes, "text": re.sub(r"<[^>]+>", "", MARKER.sub("", inner)).strip(),
                          "marker": marker.group(1).strip() if marker else None, "hreflang": (re.search(r'\bhreflang="([^"]*)"', attributes) or [None, None])[1]})
    return found


def link_named(context, text):
    found = [link for link in anchors(context.language_page) if link["text"] == text]
    assert found, f"no link reads {text!r}"
    return found[0]


@then('the page is canonical to "{address}" and its language is "{tag}"')
def step_canonical(context, address, tag):
    assert CANONICAL.search(context.language_page).group(1) == address, CANONICAL.search(context.language_page).group(1)
    assert f'<html lang="{tag}">' in context.language_page.split("\n", 2)[1]


@then("the hreflang links are")
def step_hreflang_table(context):
    found = dict(re.findall(r'<link rel="alternate" hreflang="([^"]*)" href="([^"]*)">', context.language_page))
    assert found == {row["hreflang"]: row["href"] for row in context.table}, found


@then('the link "{text}" goes to "{target}" and is not marked')
def step_unmarked(context, text, target):
    link = link_named(context, text)
    assert link["href"] == target and link["marker"] is None and link["hreflang"] is None, link


@then('the link "{text}" goes to "{target}" and is marked for "{name}" with lang and hreflang "{tag}"')
def step_marked(context, text, target, name, tag):
    link = link_named(context, text)
    assert link["href"] == target and link["hreflang"] == tag and f' lang="{tag}"' in link["attributes"], link
    assert link["marker"] == name, link


@then("no link text holds parentheses added by the site")
def step_no_parentheses(context):
    assert not re.search(r"\((?:en inglés|in English)\)|（英文）", context.language_page)


@then('every link to the home page goes to "{target}"')
def step_home(context, target):
    homes = [link["href"] for link in anchors(context.language_page) if link["href"] in ("/", "/es/", "/zh/")]
    assert homes and set(homes) == {target}, homes


@then('the section label links to "{target}"')
def step_section_label(context, target):
    assert f'<a class="mom-kicker" href="{target}">' in context.language_page


def page_links_outside_the_words(page):
    """Internal links to pages in the navigation, the menu, the footer and the rest of the furniture: everything outside `<main>`."""
    outside = re.sub(r"<main\b.*?</main>", "", page, flags=re.S)
    return [link for link in anchors(outside) if link["href"].startswith("/") and not link["href"].startswith("//") and PAGE_PATH.match(link["href"].split("#")[0].split("?")[0])
            and not link["href"].startswith("/assets/")]


@then('every navigation, menu and footer link to a page goes to a page under "{prefix}"')
def step_chrome_prefixed(context, prefix):
    links = page_links_outside_the_words(context.language_page)
    assert len(links) >= 8, links
    for link in links:
        assert link["href"].startswith(prefix), link
        assert link["marker"] is None, link


@then("no link in the page leads to a page in another language without saying so")
def step_nothing_silent(context):
    for link in anchors(context.language_page):
        if link["href"].startswith("/") and not link["href"].startswith(("/es/", "/zh/", "/assets/")) and PAGE_PATH.match(link["href"].split("#")[0]):
            assert link["hreflang"] == "en" and link["marker"], link


@then('the list links to "{first}" and "{second}" and to no English page')
def step_list_spanish(context, first, second):
    hrefs = set(main_stories(context.language_page))
    assert {first, second} <= hrefs and all(href.startswith("/es/") for href in hrefs), hrefs


@then('the list links to "{only}" and to no page that is not Chinese')
def step_list_chinese(context, only):
    hrefs = set(main_stories(context.language_page))
    assert hrefs == {only}, hrefs


@then('the list links to no page under "{one}" or "{other}"')
def step_list_english(context, one, other):
    hrefs = main_stories(context.language_page)
    assert hrefs and not any(href.startswith((one, other)) for href in hrefs), hrefs


def main_stories(page):
    main = page.split("<main", 1)[1].split("</main>", 1)[0]
    return [html.unescape(href) for href in re.findall(r'<a [^>]*href="(/(?:es/|zh/)?field-notes/[^"/]+/)"', without_switcher(main))]


@then('the page has no marked link and no link into "{one}" or "{other}" outside the switcher')
def step_primary_unchanged(context, one, other):
    page = without_switcher(context.language_page)
    assert "mom-link-language" not in page
    assert not re.search(rf'<a [^>]*href="({re.escape(one)}|{re.escape(other)})', page)


# ---------------------------------------------------------------------------------------------- slugs and Unicode addresses (features/language-slugs.feature)

CHINESE_PAGE = "/zh/field-notes/如何引导一篇报道/"
CHINESE_PAGE_ENCODED = "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/"


@then('the directory "{relative}" holds the Chinese page')
def step_directory(context, relative):
    page = (context.language_directory / relative / "index.html")
    assert page.is_file() and '<html lang="zh-Hans">' in page.read_text(encoding="utf-8").split("\n", 2)[1]


@then('the server returns that page at "{address}"')
def step_served(context, address):
    from urllib.request import urlopen
    with urlopen(served_directory_origin(context.language_directory) + address) as response:
        assert response.status == 200 and "<html lang=\"zh-Hans\">" in response.read().decode("utf-8")[:300]


@then("the Chinese page's address is written percent-encoded in the hreflang links, the switcher and the menu, and nowhere as raw characters")
def step_encoded_everywhere(context):
    page = context.language_page
    assert page.count(CHINESE_PAGE_ENCODED) == 3, page.count(CHINESE_PAGE_ENCODED)  # the hreflang link, the bar's option and the menu's option
    assert not re.search(r'(?:href|content)="[^"]*如何引导', page), "a raw-character address"


def sitemap(context):  # the site's sitemap style is `single`: every language's addresses are in the one file
    return (context.language_directory / "sitemap.xml").read_text(encoding="utf-8")


@then('the sitemap lists "{address}" once')
def step_sitemap_once(context, address):
    assert sitemap(context).count(f"<loc>{address}</loc>") == 1


@then("no address in the sitemap holds characters outside ASCII")
def step_sitemap_ascii(context):
    assert all(location.isascii() for location in re.findall(r"<loc>([^<]*)</loc>", sitemap(context)))


@then('the page\'s canonical address, once decoded, is "{address}"')
def step_canonical_decoded(context, address):
    from urllib.parse import unquote
    assert unquote(CANONICAL.search(context.language_page).group(1)) == address


@then("the page's canonical address is the percent-encoded form of those characters")
def step_canonical_encoded(context):
    assert CANONICAL.search(context.language_page).group(1) == "https://machines-on-machines.anth.us" + CHINESE_PAGE_ENCODED


# ---------------------------------------------------------------------------------------------- the chrome in the language (features/language-chrome.feature)

def strings_of(tag):
    import languages
    return languages.interface_strings()[tag]


def tag_of_page(page):
    return re.search(r'<html lang="([^"]*)"', page).group(1)


def nav_pills(page):
    items = page.split('<ul class="mom-nav-items">', 1)[1].split("</ul>", 1)[0]
    pills = []
    for attributes, inner in ANCHOR.findall(items):
        if "mom-home-pill" not in attributes:
            pills.append((html.unescape(re.sub(r"<[^>]+>", "", inner)).strip(), re.search(r'href="([^"]*)"', attributes).group(1)))
    return pills


@then('the navigation reads "{labels}" and nothing else')
def step_nav_reads(context, labels):
    assert [text for text, _href in nav_pills(context.language_page)] == labels.split(", "), nav_pills(context.language_page)


@then('the navigation links go to {targets}')
def step_nav_links(context, targets):
    expected = re.findall(r'"([^"]*)"', targets)
    assert [href for _text, href in nav_pills(context.language_page)] == expected, nav_pills(context.language_page)


@then("no navigation label holds parentheses")
def step_nav_no_parentheses(context):
    assert not any(re.search(r"[()（）]", text) for text, _href in nav_pills(context.language_page))


@then('the menu names "{names}" with lines in the language')
def step_menu(context, names):
    tag = tag_of_page(context.language_page)
    strings = strings_of(tag)
    menu = context.language_page.split('<nav class="mom-menu"', 1)[1].split("</nav>", 1)[0]
    found = [html.unescape(name) for name in re.findall(r'<span class="mom-menu-name">([^<]*)</span>', menu)]
    assert found == names.split(", "), found
    lines = [html.unescape(line) for line in re.findall(r'<span class="mom-menu-sub">([^<]*)</span>', menu)]
    assert lines == [strings[key] for key in ("site.tagline", "leadArticles", "leadPosts", "section.wiki.description")], lines


@then('the footer reads "{labels}" with the feed of the language')
def step_footer(context, labels):
    tag = tag_of_page(context.language_page)
    footer = context.language_page.split('<ul class="mom-footer-links">', 1)[1].split("</ul>", 1)[0]
    found = [html.unescape(text) for text in re.findall(r"<li><a [^>]*>([^<]*)</a></li>", footer)]
    assert found == labels.split(", "), found
    feed = next(href for href, text in re.findall(r'<li><a href="([^"]*)"[^>]*>([^<]*)</a></li>', footer) if text == "RSS")
    assert feed == {"en": "/feed.xml", "es-419": "/es/feed.xml", "zh-Hans": "/zh/feed.xml"}[tag], feed


@then("no link in the navigation, the menu or the footer leads to Findings, Videos, Conversations, About, Corrections or llms.txt")
def step_no_primary_only(context):
    page = context.language_page
    outside = re.sub(r"<main\b.*?</main>", "", page, flags=re.S)
    hrefs = [html.unescape(href) for href in re.findall(r'href="([^"]*)"', without_switcher(outside))]
    for destination in ("/findings/", "/videos/", "/conversations/", "/about/", "/corrections/", "/llms.txt"):
        assert not any(href.rstrip("/") == destination.rstrip("/") or href.endswith(destination) for href in hrefs), (destination, hrefs)


@then("the engine's chrome is in the language: {words}")
def step_engine_chrome(context, words):
    page = context.language_page
    for word in re.findall(r'"([^"]*)"', words):
        assert word in page, word
    tag = tag_of_page(context.language_page)
    for english in ("Skip to main content", "Cookies and analytics", "Accept all", "Reject all", "Privacy policy"):
        assert f">{english}<" not in page, english


@then('the byline reads "{text}"')
def step_byline(context, text):
    assert f">{text}<" in context.language_page, re.findall(r">([^<>]*·[^<>]*)<", context.language_page)


@then('the page exists in the language "{tag}" and its navigation is intact')
def step_page_in_language(context, tag):
    assert tag_of_page(context.language_page) == tag
    assert len(nav_pills(context.language_page)) == 3 and '<title>' in context.language_page


@then('the page says "{sentence}"')
def step_page_says(context, sentence):
    main = html.unescape(context.language_page.split("<main", 1)[1].split("</main>", 1)[0])
    assert sentence in main, re.sub(r"<[^>]+>", " ", main)[:400]


@then("the page lists no story")
def step_lists_nothing(context):
    assert not main_stories(context.language_page)


@then('the section label reads "{label}"')
def step_section_label_reads(context, label):
    assert f">{label}<" in context.language_page


@then("every language file is a flat object holding every key of English, none empty, with twelve month names")
def step_strings_complete(context):
    import languages
    english = strings_of("en")
    for tag in ("en", "es-419", "zh-Hans"):
        found = strings_of(tag)
        assert set(found) == set(english) and all(isinstance(value, str) and value for value in found.values()), tag
        assert len(languages.month_names(found)) == 12, tag


@then('serving Spanish without the key "{key}" is refused naming "{named}"')
def step_refused(context, key, named):
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path
    from language_cases import LANGUAGES, write_content
    from preview_local import KNOWLEDGE_DIRECTORY, static_directory_with_fixture_article_section
    with tempfile.TemporaryDirectory() as scratch:
        static = static_directory_with_fixture_article_section(Path(scratch))
        spanish = static / "strings" / "es-419.json"
        words = json.loads(spanish.read_text(encoding="utf-8"))
        del words[key]
        spanish.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run([sys.executable, str(REPOSITORY_ROOT / "tools" / "language_source.py"), str(write_content(Path(scratch))), str(static), str(KNOWLEDGE_DIRECTORY),
                                 str(Path(scratch) / "out"), json.dumps(LANGUAGES)], capture_output=True, text=True)
    assert result.returncode != 0 and named in result.stderr, result.stderr[-400:]


@when("I check the translated chrome in a browser {width:d} pixels wide")
def step_check_chrome(context, width):
    run_check(context, "chrome", width)


@then('the navigation in "{first}" and in "{second}" shows only the language\'s own words with no parentheses and nothing is cut off')
def step_chrome_browser(context, first, second):
    for tag in (first, second):
        found = context.measured[tag]
        strings = strings_of(tag)
        assert not found["overflowX"], found
        if found["navShown"]:
            labels = [strings[key] for key in ("nav./articles/.label", "nav./posts/.label", "nav./wiki/.label")]
            assert [pill["text"] for pill in found["pills"]] == labels, found["pills"]
            assert not any(re.search(r"[()（）]", pill["text"]) for pill in found["pills"])
            assert not found["itemsClipped"] and all(pill["box"]["right"] <= found["switcherLeft"] + 1 for pill in found["pills"]), found
        else:
            assert context.width < 1000, "the navigation is hidden on a wide window"


@then("the menu shows the translated labels")
def step_menu_browser(context):
    for tag, home in (("es-419", "/es/"), ("zh-Hans", "/zh/")):
        found = context.measured[tag]
        strings = strings_of(tag)
        assert found["menu"] == [strings[key] for key in ("home.label", "nav./articles/.label", "nav./posts/.label", "nav./wiki/.label")], found["menu"]
        assert all(href.startswith(home) for href in found["menuHrefs"]), found["menuHrefs"]


@then('the navigation marks "{label}" as the current page')
def step_current(context, label):
    items = context.language_page.split('<ul class="mom-nav-items">', 1)[1].split("</ul>", 1)[0]
    current = [html.unescape(re.sub(r"<[^>]+>", "", inner)).strip() for attributes, inner in ANCHOR.findall(items) if 'aria-current="page"' in attributes]
    assert current == [label], current


@then('the list links to the concept "{address}"')
def step_concept_list(context, address):
    main = context.language_page.split("<main", 1)[1].split("</main>", 1)[0]
    assert address in re.findall(r'href="([^"]*)"', main), re.findall(r'href="([^"]*)"', main)


# ---------------------------------------------------------------------------------------------- no language public (features/language-not-public.feature)

@then('no page of the site is under "{one}" or "{other}"')
def step_no_prefixed_page(context, one, other):
    assert not (context.language_directory / one.strip("/")).exists() and not (context.language_directory / other.strip("/")).exists()


@then("no page of the site has a language switcher, a welcoming banner, a language script or an hreflang link")
def step_no_language_furniture(context):
    for page in context.language_directory.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        for marker in ("data-mom-language-switcher", "data-mom-language-banner", "mom-language.js", "hreflang"):
            assert marker not in text, (page, marker)


@then('the sitemap lists no address under "{one}" or "{other}"')
def step_sitemap_no_prefixed(context, one, other):
    addresses = re.findall(r"<loc>([^<]*)</loc>", (context.language_directory / "sitemap.xml").read_text(encoding="utf-8"))
    assert addresses and not any(one in address or other in address for address in addresses), addresses


@then('the English article "{route}" is where it always was and says its language is "{tag}"')
def step_english_unchanged(context, route, tag):
    page = page_text(context.language_directory, route)
    assert f'<html lang="{tag}">' in page.split("\n", 2)[1]
