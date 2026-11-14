import sys
import tempfile
from pathlib import Path

from behave import then, when

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

from build_design_system import GALLERY_ROOT, build  # noqa: E402
from papyrus_content.figures.design_system import DirectorySource, load_design_system  # noqa: E402
from papyrus_content.figures.records import collect, read_settings_file, validate_design_system_document  # noqa: E402


@when("the design system folder is built")
def step_build(context):
    scratch = tempfile.TemporaryDirectory()
    context.add_cleanup(scratch.cleanup)
    context.design_system_folder = Path(scratch.name) / "design-system"
    build(context.design_system_folder)


@then("Papyrus loads it as a design system with the Anton and Archivo fonts embedded")
def step_loads(context):
    design_system = load_design_system(DirectorySource(context.design_system_folder))
    assert design_system.embeds_fonts, "a font file is missing"
    assert design_system.font_families() == {"Anton", "Archivo"}, design_system.font_families()


@then("Papyrus would store it, with every gallery figure as a worked example")
def step_stores(context):
    source = DirectorySource(context.design_system_folder)
    document, _ = collect(source, read_settings_file(context.design_system_folder))
    assert validate_design_system_document(document) == [], validate_design_system_document(document)
    gallery = sorted(f"examples/{path.parent.name}" for path in GALLERY_ROOT.glob("*/figure.svg"))
    assert source.list_examples() == gallery, source.list_examples()


@then('its settings turn on "{setting}" and nothing else')
def step_settings(context, setting):
    settings = read_settings_file(context.design_system_folder)
    assert settings == {setting: True}, settings


@then("the deploy workflow pushes the built folder after the deploy job, with the site's GitHub CI role on the operator lane")
def step_workflow(context):
    workflow = (REPOSITORY_ROOT / ".github" / "workflows" / "deploy.yml").read_text()
    job = workflow[workflow.index("\n  design-system:"):]
    for expected in ("needs: deploy", "role/machines-on-machines-github-ci", "python3 tools/build_design_system.py --out",
                     "papyrus design-system push", "--author-label", "PAPYRUS_GRAPHQL_AUTH: iam", "PAPYRUS_TENANT_ID: machines-on-machines"):
        assert expected in job, f"the design-system job lacks {expected!r}"
    assert "--dry-run" not in job, "the release job must really push"
