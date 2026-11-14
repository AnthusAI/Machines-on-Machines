import json
import re
import sys
from pathlib import Path

from behave import given, then

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))

from projection_support import REPOSITORY_ROOT  # noqa: E402

WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "app-shell.yml"
SITE = REPOSITORY_ROOT / "infra" / "site.json"


@given("the app-shell caller workflow")
def step_workflow(context):
    context.workflow_text = WORKFLOW.read_text()


@given("the site configuration infra/site.json")
def step_site(context):
    context.site = json.loads(SITE.read_text())


@then("it calls the Papyrus reusable app-shell workflow at the pinned Papyrus version")
def step_pinned(context):
    pin = json.loads(SITE.read_text())["papyrusVersion"]
    assert f"AnthusAI/Papyrus/.github/workflows/app-shell-deploy.yml@v{pin}" in context.workflow_text
    assert f"papyrus-ref: v{pin}" in context.workflow_text


@then("its stack name is the stack name in infra/site.json")
def step_stack(context):
    stack = json.loads(SITE.read_text())["stackName"]
    assert re.search(rf"^\s+stack-name: {re.escape(stack)}$", context.workflow_text, re.M)


@then("it does not start the Amplify build itself")
def step_no_build(context):
    assert "start-amplify-build" not in context.workflow_text


@then("the branch environment carries PAPYRUS_SITE_ID and PAPYRUS_TENANT_ID equal to the site id")
def step_env(context):
    environment = context.site["cms"]["environment"]
    for name in ("PAPYRUS_SITE_ID", "PAPYRUS_TENANT_ID"):
        assert environment.get(name) == context.site["siteId"], name
