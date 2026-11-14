"""The design system folder this repository publishes to Papyrus at each release (tools/build_design_system.py), checked with Papyrus's own loader."""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

from build_design_system import FIGURES_ROOT, GALLERY_ROOT, build  # noqa: E402
from papyrus_content.figures.design_system import DirectorySource, load_design_system  # noqa: E402
from papyrus_content.figures.records import collect, read_settings_file, validate_design_system_document  # noqa: E402

DEPLOY_WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "deploy.yml"


class BuiltDesignSystem(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.folder = Path(self.scratch.name) / "design-system"
        build(self.folder)

    def tearDown(self):
        self.scratch.cleanup()

    def test_papyrus_loads_it_as_a_design_system_that_can_draw(self):
        design_system = load_design_system(DirectorySource(self.folder))
        self.assertEqual(design_system.name, "Machines on Machines")
        self.assertTrue(design_system.embeds_fonts)
        self.assertEqual(design_system.font_families(), {"Anton", "Archivo"})

    def test_papyrus_would_store_it(self):
        document, fonts = collect(DirectorySource(self.folder), read_settings_file(self.folder))
        self.assertEqual(validate_design_system_document(document), [])
        self.assertEqual(sorted(fonts), ["fonts/Anton-Regular.ttf", "fonts/Archivo-Variable.ttf"])

    def test_every_gallery_figure_is_a_worked_example(self):
        gallery = sorted(f"examples/{path.parent.name}" for path in GALLERY_ROOT.glob("*/figure.svg"))
        self.assertEqual(DirectorySource(self.folder).list_examples(), gallery)

    def test_the_files_are_copied_byte_for_byte(self):
        mapping = json.loads((FIGURES_ROOT / "mapping.json").read_text())
        self.assertEqual((self.folder / "mapping.json").read_bytes(), (FIGURES_ROOT / "mapping.json").read_bytes())
        self.assertEqual((self.folder / mapping["tokens_file"]).read_bytes(), (REPOSITORY_ROOT / mapping["tokens_file"]).read_bytes())

    def test_the_settings_turn_on_only_the_rating_requirement(self):
        self.assertEqual(read_settings_file(self.folder), {"publishRequiresRating": True})

    def test_a_folder_that_is_not_empty_is_refused(self):
        with self.assertRaises(SystemExit):
            build(self.folder)


class DeployPushesIt(unittest.TestCase):
    def test_the_release_pushes_the_built_folder_after_the_deploy_with_the_ci_role(self):
        workflow = DEPLOY_WORKFLOW.read_text()
        job = workflow[workflow.index("\n  design-system:"):]
        self.assertIn("needs: deploy", job)
        self.assertIn("role/machines-on-machines-github-ci", job)
        self.assertIn("python3 tools/build_design_system.py --out", job)
        self.assertRegex(job, re.compile(r"papyrus design-system push \S+ --reason .+ --author-label "))
        self.assertIn("PAPYRUS_GRAPHQL_AUTH: iam", job)
        self.assertIn("PAPYRUS_TENANT_ID: machines-on-machines", job)
        self.assertNotIn("--dry-run", job)


if __name__ == "__main__":
    unittest.main()
