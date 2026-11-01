import re
import sys

from behave import given, then, when

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "tests"))

from projection_support import page_text  # noqa: E402


@given("the Machines on Machines site is projected from the fixtures")
def step_projected(context):
    assert (context.output_directory / "index.html").exists()


@when('I open the page "{route}"')
def step_open(context, route):
    context.route = route
    context.page = page_text(context.output_directory, route)


@then('the page contains "{text}"')
def step_contains(context, text):
    assert text in context.page, f"{context.route} does not contain {text!r}"


@then('the page does not contain "{text}"')
def step_lacks(context, text):
    assert text not in context.page, f"{context.route} contains {text!r}"


@then('"{first}" comes before "{second}"')
def step_order(context, first, second):
    one, two = context.page.find(first), context.page.find(second)
    assert one != -1 and two != -1 and one < two, f"{first!r} at {one}, {second!r} at {two}"


@then("the page shows {count:d} reference cards under \"{heading_id}\"")
def step_reference_count(context, count, heading_id):
    block = context.page.split(f'id="{heading_id}"')[1].split("</section>")[0]
    assert block.count('class="mom-reference-card"') == count, block.count('class="mom-reference-card"')


@then("the page shows {count:d} thread cards under \"{heading_id}\"")
def step_thread_count(context, count, heading_id):
    block = context.page.split(f'id="{heading_id}"')[1].split("</section>")[0]
    assert block.count('class="mom-thread-card"') == count


@then('the reference card for "{address}" is drawn with the "{composition}" placeholder art')
def step_reference_art(context, address, composition):
    card = re.search(rf'<a class="mom-reference-card" href="{re.escape(address)}">.*?</a>', context.page, re.S)
    assert card, f"no card for {address}"
    assert f"mom-art-{composition}" in card.group(0), card.group(0)[:300]


@then("every card on the page has an image or placeholder art")
def step_every_card(context):
    cards = re.findall(r'<a class="mom-(?:story|reference|thread)-card[^"]*".*?</a>', context.page, re.S)
    assert cards
    bad = [card[:100] for card in cards if "<img" not in card and "mom-art " not in card]
    assert not bad, bad


@then("the same address always draws the same art")
def step_same_art(context):
    import mom_components as mom
    assert mom.placeholder_art("https://example.test/x") == mom.placeholder_art("https://example.test/x")


@then('the seed "{seed}" chooses the "{composition}" composition in the "{tone}" tone')
def step_seed(context, seed, composition, tone):
    import mom_components as mom
    assert mom.choose_placeholder_art(seed) == (composition, tone), mom.choose_placeholder_art(seed)


@then('the stylesheet "{path}" defines Day colors and Night colors')
def step_themes(context, path):
    text = (context.output_directory / path).read_text()
    assert ":root {" in text and "prefers-color-scheme: dark" in text and ':root[data-theme="dark"]' in text


@then('the stylesheet "{path}" gives "{token}" a different value by night than by day')
def step_token_differs(context, path, token):
    text = (context.output_directory / path).read_text()
    values = re.findall(rf"--{re.escape(token)}:\s*([^;]+);", text)
    assert len(set(values)) > 1, values


@then("no projected page contains the word \"{word}\"")
def step_no_word(context, word):
    offenders = [p.name for p in context.output_directory.rglob("*.html") if re.search(rf"\b{word}\b", p.read_text(), re.I)]
    assert not offenders, offenders


@then('the stylesheet "{path}" sets "{token}" above {minimum:g}em')
def step_token_above(context, path, token, minimum):
    text = (context.output_directory / path).read_text()
    value = float(re.search(rf"--{re.escape(token)}:\s*([\d.]+)em;", text).group(1))
    assert value > minimum, value


@then('in the stylesheet "{path}" the wordmark seal is drawn behind the words')
def step_seal_behind(context, path):
    text = (context.output_directory / path).read_text()
    assert re.search(r"\.mom-wordmark-on \{[^}]*z-index: 0", text)
    assert re.search(r"\.mom-wordmark > span:not\(\.mom-wordmark-on\) \{[^}]*z-index: 1", text)
