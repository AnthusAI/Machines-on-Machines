import json
import os
import shutil
import subprocess

from behave import then, when

from image_ratio_steps import served_origin
from projection_support import REPOSITORY_ROOT


@when('I measure paired quotes at {width:d} pixels in "{theme}" mode')
def step_measure_paired_quotes(context, width, theme):
    if not shutil.which("node"):
        context.scenario.skip("Node is not installed")
        return
    result = subprocess.run(
        ["node", str(REPOSITORY_ROOT / "tools/measure_paired_quotes.cjs"), served_origin(context), str(width), theme],
        capture_output=True,
        text=True,
        env=os.environ,
    )
    if result.returncode == 2:
        context.scenario.skip(result.stderr.strip())
        return
    assert result.returncode == 0, result.stderr
    context.paired_quotes = json.loads(result.stdout)


@then("the attributed quotes are {arrangement} in readable type")
def step_paired_quotes_fit(context, arrangement):
    if not hasattr(context, "paired_quotes"):
        return
    measured = context.paired_quotes
    assert measured["arrangement"] == arrangement, measured
    assert not measured["overflow"] and not measured["nestedFigures"], measured
    assert len(measured["quotes"]) == 2, measured
    assert all(18 <= quote["size"] < measured["singleSize"] and quote["sourceSize"] >= 14 for quote in measured["quotes"]), measured
