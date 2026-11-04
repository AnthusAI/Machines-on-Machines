"""The figure system: its sources, its exported pictures, its generated guide, and a real render through Papyrus."""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
sys.path.insert(0, str(REPOSITORY_ROOT))

from build_figure_style_guide import GUIDE_PATH, build_guide, contrast_ratio  # noqa: E402
from render_figures import GALLERY_ROOT, LABEL_LIMIT_CHARACTERS, LABELS, MAX_PICTURE_BYTES, MAX_RATIO_DIFFERENCE, image_directive, load_mapping, load_tokens, png_size, role_colors, source_problems  # noqa: E402
from tools.preview_local import papyrus_executable, static_directory_with_fixture_article_section  # noqa: E402

GALLERY_FIGURES = ("parked-car", "search-nobody-sees", "wall-and-climb", "walls-and-gaps", "wiped-board")


def figure_folder(slug: str) -> Path:
    return GALLERY_ROOT / slug


def figure_metadata(slug: str) -> dict:
    return json.loads((figure_folder(slug) / "figure.json").read_text())


def figure_source(slug: str) -> str:
    return (figure_folder(slug) / "figure.svg").read_text()


class FigureSources(unittest.TestCase):
    def test_the_gallery_holds_the_five_worked_figures(self):
        self.assertEqual(sorted(path.parent.name for path in GALLERY_ROOT.glob("*/figure.svg")), list(GALLERY_FIGURES))

    def test_every_figure_source_passes_the_source_checks(self):
        mapping = load_mapping()
        for slug in GALLERY_FIGURES:
            self.assertEqual(source_problems(figure_source(slug), figure_metadata(slug), mapping), [], slug)

    def test_a_raw_color_is_refused(self):
        source = figure_source("wiped-board").replace('fill="{ground}"', 'fill="#ff0000"')
        self.assertTrue(any("raw color" in problem for problem in source_problems(source, figure_metadata("wiped-board"), load_mapping())))

    def test_navy_is_refused_in_a_diagram_but_allowed_in_an_illustration(self):
        mapping = load_mapping()
        source = figure_source("wiped-board").replace('fill="{ground}"', 'fill="{brand}"')
        self.assertTrue(any("brand navy" in problem for problem in source_problems(source, figure_metadata("wiped-board"), mapping)))
        self.assertIn("{brand}", figure_source("parked-car"))

    def test_a_second_focal_mark_is_refused(self):
        source = figure_source("wiped-board").replace('fill="{ground}"', 'fill="{ground}" data-focal="true"')
        self.assertTrue(any("focal" in problem for problem in source_problems(source, figure_metadata("wiped-board"), load_mapping())))

    def test_a_forecast_without_its_stamp_is_refused(self):
        source = figure_source("wall-and-climb").replace(LABELS["forecast"], "THE CLIMB")
        self.assertTrue(any("stamp" in problem for problem in source_problems(source, figure_metadata("wall-and-climb"), load_mapping())))

    def test_a_forecast_shows_no_numbers(self):
        visible_words = " ".join(re.findall(r"<text[^>]*>([^<]*)</text>", figure_source("wall-and-climb")))
        self.assertNotRegex(visible_words, r"\d")

    def test_labels_stay_short(self):
        for slug in GALLERY_FIGURES:
            for label in re.findall(r"<text[^>]*>([^<]*)</text>", figure_source(slug)):
                self.assertLessEqual(len(label), LABEL_LIMIT_CHARACTERS, f"{slug}: {label}")

    def test_no_figure_outlines_a_tile(self):
        for slug in GALLERY_FIGURES:
            self.assertNotRegex(figure_source(slug), r"<rect[^>]*stroke=", slug)


class FigurePictures(unittest.TestCase):
    def test_day_and_night_pictures_match_and_fit_the_papyrus_limits(self):
        for slug in GALLERY_FIGURES:
            light_path = figure_folder(slug) / f"{slug}.png"
            dark_path = figure_folder(slug) / f"{slug}.dark.png"
            light_width, light_height = png_size(light_path)
            dark_width, dark_height = png_size(dark_path)
            self.assertLessEqual(abs(light_width / light_height - dark_width / dark_height) / (light_width / light_height), MAX_RATIO_DIFFERENCE, slug)
            self.assertLess(light_path.stat().st_size, MAX_PICTURE_BYTES, slug)
            self.assertLess(dark_path.stat().st_size, MAX_PICTURE_BYTES, slug)

    def test_pictures_are_exported_at_twice_the_canvas(self):
        for slug in GALLERY_FIGURES:
            width, _ = png_size(figure_folder(slug) / f"{slug}.png")
            canvas_width = int(re.search(r'viewBox="0 0 (\d+) ', figure_source(slug)).group(1))
            self.assertEqual(width, canvas_width * load_mapping()["canvas"]["export_scale"], slug)


class FigureMetadata(unittest.TestCase):
    def test_every_figure_says_what_it_shows_and_why_it_is_there(self):
        for slug in GALLERY_FIGURES:
            self.assertRegex(figure_metadata(slug)["alt"], r"(?i)\bit (shows|sets)\b", slug)

    def test_credits_follow_the_attribution_wording(self):
        for slug in GALLERY_FIGURES:
            credit = figure_metadata(slug)["credit"]
            self.assertIn("rafted by AI", credit, slug)
            self.assertIn("Approved by {approved_by}", credit, slug)
            self.assertNotIn("desk", credit.lower(), slug)

    def test_nothing_is_marked_approved_before_a_person_confirms(self):
        directive = image_directive(figure_metadata("wiped-board") | {"approved_by": None})
        self.assertIn("Approved by <name>", directive)


class FigureTokens(unittest.TestCase):
    def test_every_figure_pair_clears_its_contrast_bar_in_both_themes(self):
        mapping = load_mapping()
        tokens = load_tokens(mapping)
        for theme_id in ("light", "dark"):
            colors = role_colors(mapping, tokens, theme_id)
            for foreground, background in mapping["contrast_pairs"]:
                self.assertGreaterEqual(contrast_ratio(colors[foreground], colors[background]), 4.5, f"{theme_id}: {foreground} on {background}")

    def test_the_mapping_only_names_real_tokens(self):
        mapping = load_mapping()
        color_names = {token["name"] for token in load_tokens(mapping)["color"]["tokens"]}
        self.assertLessEqual(set(mapping["figure_roles"].values()), color_names)

    def test_the_stylesheet_carries_the_figure_sizes(self):
        stylesheet = (REPOSITORY_ROOT / "design" / "system" / "tokens.css").read_text()
        self.assertIn("--figure-phone-text-min: 13px;", stylesheet)
        self.assertIn("--figure-hatch:", stylesheet)

    def test_the_type_floor_matches_the_phone_floor(self):
        mapping = load_mapping()
        canvas = mapping["canvas"]
        styles = {style["name"]: style for group in load_tokens(mapping)["type"]["groups"] for style in group["styles"]}
        for style_name in mapping["type_roles"].values():
            displayed = float(styles[style_name]["fontSize"].removesuffix("px")) * canvas["phone_width"] / canvas["diagram_width"]
            self.assertGreaterEqual(displayed, canvas["phone_text_min"], style_name)


class FigureStyleGuide(unittest.TestCase):
    def test_the_guide_is_current(self):
        self.assertEqual(GUIDE_PATH.read_text(), build_guide())

    def test_the_guide_has_every_row_the_skill_requires(self):
        guide = GUIDE_PATH.read_text()
        self.assertTrue(guide.startswith("<!-- diagram-design-profile"))
        for role in ("paper", "paper-2", "ink", "ink-strong", "muted", "soft", "rule", "rule-solid", "accent", "accent-tint", "link"):
            self.assertIn(f"| `{role}` |", guide)
        for role in ("title", "node-name", "sublabel", "eyebrow", "arrow-label", "callout"):
            self.assertIn(f"| `{role}` |", guide)

    def test_the_rules_name_roles_and_not_this_brand(self):
        rules = (REPOSITORY_ROOT / "design" / "figures" / "rules.md").read_text()
        self.assertNotRegex(rules, r"#[0-9a-fA-F]{6}")
        for brand_word in ("Machines on Machines", "Anton", "Archivo"):
            self.assertNotIn(brand_word, rules)


class FigureThroughPapyrus(unittest.TestCase):
    def test_the_theme_fits_figures_to_the_column_without_the_browser_margin(self):
        theme = (REPOSITORY_ROOT / "web" / "css" / "site-theme.css").read_text()
        self.assertRegex(theme, r"\.mom-article-body \.papyrus-image \{ margin: var\(--space-8\) 0; \}")
        self.assertRegex(theme, r"\.mom-article-body \.papyrus-image img \{[^}]*width: 100%")

    def test_papyrus_publishes_the_pair_with_alt_text_and_credit(self):
        slug = "wiped-board"
        metadata = figure_metadata(slug) | {"approved_by": "Test Editor", "slug": f"field-notes/{slug}"}
        with tempfile.TemporaryDirectory(prefix="mom-figure-") as scratch:
            scratch_path = Path(scratch)
            content_directory = scratch_path / "content"
            shutil.copytree(REPOSITORY_ROOT / "tests" / "fixtures" / "content", content_directory)
            shutil.copy(figure_folder(slug) / f"{slug}.png", content_directory / "field-notes")
            shutil.copy(figure_folder(slug) / f"{slug}.dark.png", content_directory / "field-notes")
            (content_directory / "field-notes" / "figure-test.md").write_text(
                "---\ntitle: A figure test\ndek: Testing a figure.\ndate: 2026-11-04\nauthors: [Editor]\n---\n\nText.\n\n" + image_directive(metadata) + "\n"
            )
            output_directory = scratch_path / "out"
            output_directory.mkdir()
            shutil.copytree(REPOSITORY_ROOT / "tests" / "fixtures" / "_data", output_directory / "_data")
            static_directory = static_directory_with_fixture_article_section(scratch_path)
            projection_path = static_directory / "projection.json"
            projection = json.loads(projection_path.read_text())
            projection["images"] = {}
            projection_path.write_text(json.dumps(projection))
            result = subprocess.run(
                [papyrus_executable(), "ops", "content", "project", "--all", "--from-dir", str(content_directory), "--static-dir", str(static_directory),
                 "--knowledge-dir", str(REPOSITORY_ROOT / "tests" / "fixtures" / "knowledge"), "--out", str(output_directory)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])
            page = next(output_directory.rglob("figure-test/index.html")).read_text()
            self.assertIn("papyrus-image-light", page)
            self.assertIn("papyrus-image-dark", page)
            self.assertIn("A timeline of July 6 to July 11", page)
            self.assertIn("Approved by Test Editor", page)


if __name__ == "__main__":
    unittest.main()
