"""The consent edge pieces of infra/edge/machines-on-machines.yaml, checked without calling AWS.

The template is loaded with a CloudFormation-aware YAML loader and rendered the way CloudFormation resolves
conditions (Fn::If, Fn::Equals, Fn::And, Fn::Not, Condition, Ref to a parameter, AWS::NoValue).
"""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPOSITORY_ROOT / "infra" / "edge" / "machines-on-machines.yaml"
TEMPLATE_BEFORE_CONSENT_PATH = REPOSITORY_ROOT / "tests" / "fixtures" / "edge" / "machines-on-machines-before-consent.yaml"
CONSENT_PATH = "/_papyrus/consent"
CACHING_DISABLED_POLICY_ID = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
NO_VALUE = object()
CONSENT_RESOURCES = {"ConsentRegionFunction", "ConsentOriginRequestPolicy", "ConsentCachePolicy"}


class CloudFormationLoader(yaml.SafeLoader):
    pass


def _intrinsic(loader, tag_suffix, node):
    name = "Ref" if tag_suffix == "Ref" else "Condition" if tag_suffix == "Condition" else "Fn::" + tag_suffix
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
        if tag_suffix == "GetAtt":
            value = value.split(".", 1)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node, deep=True)
    else:
        value = loader.construct_mapping(node, deep=True)
    return {name: value}


CloudFormationLoader.add_multi_constructor("!", _intrinsic)


def load_template(path):
    return yaml.load(path.read_text(), Loader=CloudFormationLoader)


def parameter_values(template, overrides):
    values = {name: spec.get("Default", "") for name, spec in template["Parameters"].items()}
    values.update(overrides)
    return values


def condition_value(name, template, values):
    return resolve(template["Conditions"][name], template, values)


def resolve(node, template, values):
    if isinstance(node, list):
        items = [resolve(item, template, values) for item in node]
        return [item for item in items if item is not NO_VALUE]
    if not isinstance(node, dict):
        return node
    if len(node) == 1:
        (key, argument), = node.items()
        if key == "Ref":
            if argument == "AWS::NoValue":
                return NO_VALUE
            return values.get(argument, node)
        if key == "Condition":
            return condition_value(argument, template, values)
        if key == "Fn::If":
            name, when_true, when_false = argument
            return resolve(when_true if condition_value(name, template, values) else when_false, template, values)
        if key == "Fn::Equals":
            return resolve(argument[0], template, values) == resolve(argument[1], template, values)
        if key == "Fn::Not":
            return not resolve(argument[0], template, values)
        if key == "Fn::And":
            return all(resolve(item, template, values) for item in argument)
        if key == "Fn::Or":
            return any(resolve(item, template, values) for item in argument)
    resolved = {key: resolve(value, template, values) for key, value in node.items()}
    return {key: value for key, value in resolved.items() if value is not NO_VALUE}


def render(path, **overrides):
    """The resources CloudFormation would create for these parameters, conditions resolved."""
    template = load_template(path)
    values = parameter_values(template, overrides)
    resources = {}
    for name, resource in template["Resources"].items():
        condition = resource.get("Condition")
        if condition and not condition_value(condition, template, values):
            continue
        resources[name] = resolve({key: value for key, value in resource.items() if key != "Condition"}, template, values)
    return resources


def behavior_for(resources, path_pattern):
    behaviors = resources["SiteDistribution"]["Properties"]["DistributionConfig"].get("CacheBehaviors", [])
    return [behavior for behavior in behaviors if behavior["PathPattern"] == path_pattern]


class DefaultTemplateIsUnchangedTest(unittest.TestCase):
    def test_the_parameters_default_to_off_and_origin_request_policy(self):
        parameters = load_template(TEMPLATE_PATH)["Parameters"]
        self.assertEqual(parameters["ConsentRegionLookup"]["Default"], "false")
        self.assertEqual(parameters["ConsentRegionLookup"]["AllowedValues"], ["true", "false"])
        self.assertEqual(parameters["ConsentHeaderPolicy"]["Default"], "origin-request-policy")
        self.assertEqual(parameters["ConsentHeaderPolicy"]["AllowedValues"], ["origin-request-policy", "cache-policy"])

    def test_every_new_resource_is_conditional_on_the_lookup(self):
        template = load_template(TEMPLATE_PATH)
        for name in CONSENT_RESOURCES:
            self.assertIn("Condition", template["Resources"][name], name)
        self.assertEqual(
            {name for name in template["Resources"] if name not in load_template(TEMPLATE_BEFORE_CONSENT_PATH)["Resources"]},
            CONSENT_RESOURCES,
        )

    def test_with_the_defaults_the_rendered_resources_equal_the_template_before_this_change(self):
        self.assertEqual(render(TEMPLATE_PATH), render(TEMPLATE_BEFORE_CONSENT_PATH))

    def test_with_the_defaults_there_is_no_consent_resource_and_no_consent_behavior(self):
        resources = render(TEMPLATE_PATH)
        self.assertFalse(CONSENT_RESOURCES & set(resources))
        self.assertEqual(behavior_for(resources, CONSENT_PATH), [])

    def test_outputs_and_the_other_sections_are_the_same_as_before(self):
        after, before = load_template(TEMPLATE_PATH), load_template(TEMPLATE_BEFORE_CONSENT_PATH)
        self.assertEqual(after["Outputs"], before["Outputs"])
        self.assertEqual(after["Description"], before["Description"])
        for name, parameter in before["Parameters"].items():
            self.assertEqual(after["Parameters"][name], parameter)


class LookupOnTest(unittest.TestCase):
    def setUp(self):
        self.before = render(TEMPLATE_BEFORE_CONSENT_PATH)
        self.on = render(TEMPLATE_PATH, ConsentRegionLookup="true")

    def test_exactly_one_behavior_is_added_for_the_consent_path(self):
        before = self.before["SiteDistribution"]["Properties"]["DistributionConfig"]["CacheBehaviors"]
        after = self.on["SiteDistribution"]["Properties"]["DistributionConfig"]["CacheBehaviors"]
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual(len(behavior_for(self.on, CONSENT_PATH)), 1)
        self.assertEqual([b for b in after if b["PathPattern"] != CONSENT_PATH], before)

    def test_the_new_pattern_is_exact_and_matched_by_no_existing_pattern(self):
        patterns = [b["PathPattern"] for b in self.before["SiteDistribution"]["Properties"]["DistributionConfig"]["CacheBehaviors"]]
        self.assertNotIn("*", CONSENT_PATH)
        for pattern in patterns:
            if pattern.endswith("*"):
                self.assertFalse(CONSENT_PATH.startswith(pattern[:-1]), pattern)
            else:
                self.assertNotEqual(pattern, CONSENT_PATH)

    def test_the_default_behavior_and_every_other_property_are_unchanged(self):
        def without_behaviors(resources):
            copy = json.loads(json.dumps(resources))
            del copy["SiteDistribution"]["Properties"]["DistributionConfig"]["CacheBehaviors"]
            return copy

        self.assertEqual(without_behaviors(self.on), {**without_behaviors(self.before), **{n: self.on[n] for n in self.on if n in CONSENT_RESOURCES}})
        self.assertEqual(
            self.on["SiteDistribution"]["Properties"]["DistributionConfig"]["DefaultCacheBehavior"],
            self.before["SiteDistribution"]["Properties"]["DistributionConfig"]["DefaultCacheBehavior"],
        )

    def test_the_function_is_on_viewer_request_and_is_the_only_association(self):
        behavior = behavior_for(self.on, CONSENT_PATH)[0]
        self.assertEqual(
            behavior["FunctionAssociations"],
            [{"EventType": "viewer-request", "FunctionARN": {"Fn::GetAtt": ["ConsentRegionFunction", "FunctionARN"]}}],
        )
        self.assertNotIn("LambdaFunctionAssociations", behavior)

    def test_the_behavior_allows_only_get_and_head_and_targets_the_site_bucket(self):
        behavior = behavior_for(self.on, CONSENT_PATH)[0]
        self.assertEqual(behavior["AllowedMethods"], ["GET", "HEAD"])
        self.assertEqual(behavior["TargetOriginId"], "site-bucket")
        self.assertEqual(behavior["ViewerProtocolPolicy"], "redirect-to-https")

    def test_the_function_resource_is_published_and_named_after_the_stack(self):
        function = self.on["ConsentRegionFunction"]
        self.assertEqual(function["Type"], "AWS::CloudFront::Function")
        self.assertIs(function["Properties"]["AutoPublish"], True)
        self.assertEqual(function["Properties"]["FunctionConfig"]["Runtime"], "cloudfront-js-2.0")
        self.assertEqual(function["Properties"]["Name"], {"Fn::Sub": "${AWS::StackName}-consent-region"})

    def test_the_other_resources_are_the_same_as_before(self):
        for name, resource in self.before.items():
            if name != "SiteDistribution":
                self.assertEqual(self.on[name], resource, name)


class HeaderPolicyChoiceTest(unittest.TestCase):
    def test_origin_request_policy_forwards_the_country_header_and_caching_is_disabled(self):
        resources = render(TEMPLATE_PATH, ConsentRegionLookup="true")
        self.assertIn("ConsentOriginRequestPolicy", resources)
        self.assertNotIn("ConsentCachePolicy", resources)
        headers = resources["ConsentOriginRequestPolicy"]["Properties"]["OriginRequestPolicyConfig"]["HeadersConfig"]
        self.assertEqual(headers, {"HeaderBehavior": "whitelist", "Headers": ["CloudFront-Viewer-Country"]})
        behavior = behavior_for(resources, CONSENT_PATH)[0]
        self.assertEqual(behavior["CachePolicyId"], CACHING_DISABLED_POLICY_ID)
        self.assertEqual(behavior["OriginRequestPolicyId"], {"Ref": "ConsentOriginRequestPolicy"})

    def test_cache_policy_has_the_header_in_the_cache_key_and_no_origin_request_policy(self):
        resources = render(TEMPLATE_PATH, ConsentRegionLookup="true", ConsentHeaderPolicy="cache-policy")
        self.assertIn("ConsentCachePolicy", resources)
        self.assertNotIn("ConsentOriginRequestPolicy", resources)
        config = resources["ConsentCachePolicy"]["Properties"]["CachePolicyConfig"]
        self.assertEqual(
            config["ParametersInCacheKeyAndForwardedToOrigin"]["HeadersConfig"],
            {"HeaderBehavior": "whitelist", "Headers": ["CloudFront-Viewer-Country"]},
        )
        self.assertEqual(config["MinTTL"], 0)
        self.assertLessEqual(config["MaxTTL"], 1)
        behavior = behavior_for(resources, CONSENT_PATH)[0]
        self.assertEqual(behavior["CachePolicyId"], {"Ref": "ConsentCachePolicy"})
        self.assertNotIn("OriginRequestPolicyId", behavior)

    def test_both_policies_never_exist_together(self):
        for choice in ("origin-request-policy", "cache-policy"):
            resources = render(TEMPLATE_PATH, ConsentRegionLookup="true", ConsentHeaderPolicy=choice)
            self.assertEqual(len({"ConsentOriginRequestPolicy", "ConsentCachePolicy"} & set(resources)), 1)

    def test_the_header_choice_is_ignored_while_the_lookup_is_off(self):
        self.assertEqual(
            render(TEMPLATE_PATH, ConsentHeaderPolicy="cache-policy"),
            render(TEMPLATE_PATH),
        )


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class EmbeddedFunctionTest(unittest.TestCase):
    """Runs the function code embedded in the template, as CloudFront would call it."""

    @staticmethod
    def answer_for(country_header):
        code = render(TEMPLATE_PATH, ConsentRegionLookup="true")["ConsentRegionFunction"]["Properties"]["FunctionCode"]
        headers = {} if country_header is None else {"cloudfront-viewer-country": {"value": country_header}}
        script = code + "\nconsole.log(JSON.stringify(handler({request:{headers:%s}})));" % json.dumps(headers)
        output = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout
        return json.loads(output)

    def test_the_answer_is_private_and_never_stored(self):
        response = self.answer_for("US")
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["cache-control"]["value"], "private, no-store")
        self.assertEqual(json.loads(response["body"]), {"country": "US", "notice": False})

    def test_regulated_countries_get_the_notice(self):
        for country in ("DE", "FR", "GB", "CH", "NO", "IS", "LI"):
            self.assertEqual(json.loads(self.answer_for(country)["body"]), {"country": country, "notice": True})

    def test_it_fails_closed_without_a_usable_country(self):
        for header in (None, "", "T1", "XX", "garbage"):
            self.assertEqual(json.loads(self.answer_for(header)["body"]), {"country": "", "notice": True}, header)


if __name__ == "__main__":
    unittest.main()
