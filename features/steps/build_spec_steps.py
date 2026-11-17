"""Steps for features/build-spec.feature: the Amplify build spec is the one Papyrus generates, not a hand-written copy."""

import json
import subprocess

from behave import then, when

from projection_support import REPOSITORY_ROOT


@when('Papyrus prints the production build spec for "{site_file}"')
def step_print_build_spec(context, site_file):
    printed = subprocess.run(
        ["npx", "papyrus-infra", "print-buildspec", "--site", site_file, "--app", "cms-production"],
        cwd=REPOSITORY_ROOT, capture_output=True, text=True, check=True,
    )
    context.generated_build_spec = printed.stdout


@then('"{path}" is exactly that build spec')
def step_build_spec_is_generated(context, path):
    assert (REPOSITORY_ROOT / path).read_text() == context.generated_build_spec, (
        f"{path} differs from the generated spec; regenerate it with "
        "`npx papyrus-infra print-buildspec --site infra/site.json --app cms-production > amplify.yml`"
    )


@then('"{path}" runs these commands in order')
def step_commands_in_order(context, path):
    lines = [line.strip()[2:] for line in (REPOSITORY_ROOT / path).read_text().splitlines() if line.strip().startswith("- ")]
    position = -1
    for row in context.table:
        wanted = row["command"].strip()
        following = [index for index, line in enumerate(lines) if index > position and wanted in line]
        assert following, f"no command containing {wanted!r} after position {position} in {path}"
        position = following[0]


@then('"{path}" sets "{first}" and "{second}" to "{value}"')
def step_site_environment(context, path, first, second, value):
    environment = json.loads((REPOSITORY_ROOT / path).read_text())["cms"]["environment"]
    assert environment.get(first) == value and environment.get(second) == value, f"{first}/{second} are not both {value!r}: {environment}"


@then('the schedule step names the site\'s brand "{brand}"')
def step_schedule_names_brand(context, brand):
    site = json.loads((REPOSITORY_ROOT / "infra" / "site.json").read_text())
    assert site["brand"] == brand
    assert f"papyrus agents schedules --site {brand}" in (REPOSITORY_ROOT / "amplify.yml").read_text()
