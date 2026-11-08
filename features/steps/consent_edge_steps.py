import json
import shutil
import subprocess
import sys
from pathlib import Path

from behave import given, then, when

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))

import test_consent_edge as edge  # noqa: E402


@given("the edge template")
def step_template(context):
    assert edge.TEMPLATE_PATH.exists()


@when("it is rendered with the lookup switch at its default")
def step_render_default(context):
    context.resources = edge.render(edge.TEMPLATE_PATH)


@when("it is rendered with the lookup switched on")
def step_render_on(context):
    context.resources = edge.render(edge.TEMPLATE_PATH, ConsentRegionLookup="true")


@when('it is rendered with the lookup switched on and the header policy "{choice}"')
def step_render_choice(context, choice):
    context.resources = edge.render(edge.TEMPLATE_PATH, ConsentRegionLookup="true", ConsentHeaderPolicy=choice)


def _behaviors(resources):
    return resources["SiteDistribution"]["Properties"]["DistributionConfig"]["CacheBehaviors"]


@then("it creates the same resources as the template before the consent change")
def step_same(context):
    assert context.resources == edge.render(edge.TEMPLATE_BEFORE_CONSENT_PATH)


@then("it has no behavior for the consent path")
def step_no_behavior(context):
    assert edge.behavior_for(context.resources, edge.CONSENT_PATH) == []


@then('it has exactly one more behavior than before, for the path "{path}" only')
def step_one_more(context, path):
    before = _behaviors(edge.render(edge.TEMPLATE_BEFORE_CONSENT_PATH))
    after = _behaviors(context.resources)
    assert len(after) == len(before) + 1
    assert [b for b in after if b["PathPattern"] != path] == before
    assert len(edge.behavior_for(context.resources, path)) == 1


@then("the new behavior answers from a function on the viewer request and allows only GET and HEAD")
def step_function(context):
    behavior = edge.behavior_for(context.resources, edge.CONSENT_PATH)[0]
    assert [a["EventType"] for a in behavior["FunctionAssociations"]] == ["viewer-request"]
    assert behavior["AllowedMethods"] == ["GET", "HEAD"]


@then("the page behavior and every other path behavior are exactly as they were")
def step_others(context):
    before = edge.render(edge.TEMPLATE_BEFORE_CONSENT_PATH)["SiteDistribution"]["Properties"]["DistributionConfig"]
    after = context.resources["SiteDistribution"]["Properties"]["DistributionConfig"]
    assert after["DefaultCacheBehavior"] == before["DefaultCacheBehavior"]
    assert [b for b in after["CacheBehaviors"] if b["PathPattern"] != edge.CONSENT_PATH] == before["CacheBehaviors"]


@then('the consent path has an origin request policy that forwards "{header}"')
def step_origin_request_policy(context, header):
    config = context.resources["ConsentOriginRequestPolicy"]["Properties"]["OriginRequestPolicyConfig"]
    assert config["HeadersConfig"]["Headers"] == [header]
    assert edge.behavior_for(context.resources, edge.CONSENT_PATH)[0]["OriginRequestPolicyId"] == {"Ref": "ConsentOriginRequestPolicy"}


@then('the consent path has a cache policy that includes "{header}"')
def step_cache_policy(context, header):
    config = context.resources["ConsentCachePolicy"]["Properties"]["CachePolicyConfig"]
    assert config["ParametersInCacheKeyAndForwardedToOrigin"]["HeadersConfig"]["Headers"] == [header]
    assert edge.behavior_for(context.resources, edge.CONSENT_PATH)[0]["CachePolicyId"] == {"Ref": "ConsentCachePolicy"}


def _answer(context, header_value):
    if not shutil.which("node"):
        context.scenario.skip("node is not installed")
        return None
    code = context.resources["ConsentRegionFunction"]["Properties"]["FunctionCode"]
    headers = {} if header_value is None else {"cloudfront-viewer-country": {"value": header_value}}
    script = code + "\nconsole.log(JSON.stringify(handler({request:{headers:%s}})));" % json.dumps(headers)
    return json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)


@then('the consent function answers with "{cache_control}"')
def step_cache_control(context, cache_control):
    response = _answer(context, "US")
    if response is not None:
        assert response["headers"]["cache-control"]["value"] == cache_control


@then("an unknown country gets the notice")
def step_unknown(context):
    response = _answer(context, None)
    if response is not None:
        assert json.loads(response["body"]) == {"country": "", "notice": True}
