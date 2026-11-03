import json
import sys
from pathlib import Path

from behave import given, then

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))

from projection_support import REPOSITORY_ROOT  # noqa: E402


@given("the publication's projection settings")
def step_projection_settings(context):
    context.projection = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())


@then('new Stories default to the type "{story_type}"')
def step_default_type(context, story_type):
    assert context.projection["storyTypes"]["default"] == story_type


@then('the newsroom offers the types "{first}" and "{second}"')
def step_offered_types(context, first, second):
    assert set(context.projection["storyTypes"]["types"]) == {first, second}


@then('the type "{story_type}" is published under "{prefix}"')
def step_type_address(context, story_type, prefix):
    assert context.projection["urls"]["types"][story_type]["base"] == prefix.strip("/")


@then('the type "{story_type}" has no address of its own')
def step_type_without_address(context, story_type):
    assert story_type not in context.projection["urls"]["types"]
