import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import scale_css  # noqa: E402


class ScaleLengthsTest(unittest.TestCase):
    def test_px_are_scaled_including_media_query_breakpoints(self):
        css = "@media (min-width: 900px) and (max-width: 1839px) { a { margin: -96px 0 0 12px; } }"
        self.assertEqual(
            scale_css.scale_lengths(css),
            "@media (min-width: 675px) and (max-width: 1379.25px) { a { margin: -72px 0 0 9px; } }",
        )

    def test_rem_is_scaled_in_breakpoints_and_left_to_the_root_font_size_in_rules(self):
        css = "@media (min-width: 40rem) { a { margin: 1.5rem; } }"
        self.assertEqual(scale_css.scale_lengths(css), "@media (min-width: 30rem) { a { margin: 1.5rem; } }")

    def test_the_site_stylesheet_scales_the_root_font_size_so_every_rem_follows(self):
        dual = scale_css.dual_stylesheet("a { margin: 1rem; }", "s.css", scale_root=True)
        self.assertIn("@media (min-width: 600px) {\nhtml { font-size: 75%; }\na { margin: 1rem; }", dual)

    def test_unitless_numbers_colors_and_other_units_are_untouched(self):
        css = "a { line-height: 1.5; z-index: 20; color: #1a2b3c; width: 50%; height: 100dvh; padding: 2em; opacity: .5; }"
        self.assertEqual(scale_css.scale_lengths(css), css)

    def test_urls_strings_and_comments_are_untouched(self):
        css = 'a { background: url("data:image/svg+xml;utf8,<svg width=\'48px\'/>"); content: "10px"; } /* 20px */'
        self.assertEqual(scale_css.scale_lengths(css), css)

    def test_functions_scale_every_length_inside_them(self):
        self.assertEqual(scale_css.scale_lengths("a { font-size: clamp(32px, 5.6vh, 70px); }"), "a { font-size: clamp(24px, 5.6vh, 52.5px); }")


class DualStylesheetTest(unittest.TestCase):
    SOURCE = '@font-face { font-family: X; src: url(x.woff2); }\n:root { --space: 16px; }\n@media (min-width: 640px) { a { top: 8px; } }\n'

    def test_the_phone_block_is_verbatim_and_the_wide_block_is_scaled(self):
        dual = scale_css.dual_stylesheet(self.SOURCE, "source.css")
        self.assertIn("@media (max-width: 599px) {\n:root { --space: 16px; }\n@media (min-width: 640px) { a { top: 8px; } }\n}", dual)
        self.assertIn("@media (min-width: 600px) {\n:root { --space: 12px; }\n@media (min-width: 480px) { a { top: 6px; } }\n}", dual)

    def test_font_faces_stay_at_the_top_level_once(self):
        dual = scale_css.dual_stylesheet(self.SOURCE, "source.css")
        self.assertEqual(dual.count("@font-face"), 1)
        self.assertLess(dual.index("@font-face"), dual.index("@media (max-width"))

    def test_generating_twice_from_the_same_source_gives_the_same_text(self):
        self.assertEqual(scale_css.dual_stylesheet(self.SOURCE, "s.css"), scale_css.dual_stylesheet(self.SOURCE, "s.css"))

    def test_the_constants_are_the_documented_ones(self):
        self.assertEqual((scale_css.SCALE, scale_css.PHONE_MAX), (0.75, 599))


class MinimumTextSizeTest(unittest.TestCase):
    def dual(self, css):
        return scale_css.dual_stylesheet(css, "s.css")

    def test_the_floors_are_the_policy_numbers(self):
        self.assertEqual((scale_css.READING_FLOOR_PX, scale_css.INTERFACE_FLOOR_PX, scale_css.LABEL_FLOOR_PX), (18, 14, 13))

    def test_interface_text_is_raised_to_14_after_scaling_and_micro_labels_to_13_in_both_versions(self):
        dual = self.dual(".meta { font: 600 13px/20px X; }\n.tag { font-size: 11px; text-transform: uppercase; }")
        phone, scaled = dual.split("@media (min-width: 600px) {")
        self.assertIn(".meta { font: 600 14px/21px X; }", scaled)
        self.assertIn(".meta { font: 600 14px/20px X; }", phone)
        self.assertIn("font-size: 13px; text-transform: uppercase", phone)
        self.assertIn("font-size: 13px; text-transform: uppercase", scaled)

    def test_reading_text_is_18_when_scaled_and_a_raised_line_height_stays_on_the_rhythm(self):
        scaled = self.dual(".mom-article-body { font: 400 18px / 1.65 X; }\n.mom-home-purpose { font: 600 17px / 24px X; }").split("@media (min-width: 600px) {")[1]
        self.assertIn(".mom-article-body { font: 400 18px/1.65 X; }", scaled)
        self.assertIn(".mom-home-purpose { font: 600 18px/30px X; }", scaled)  # 30 = 10 units of 3px

    def test_text_already_above_its_floor_and_non_pixel_sizes_are_left_alone(self):
        css = ".a { font-size: 40px; }\n.b { font: 400 clamp(52px, 7vw, 92px) / 0.92 X; }\n.c { font-size: 1.2em; }"
        scaled = self.dual(css).split("@media (min-width: 600px) {")[1]
        self.assertIn(".a { font-size: 30px; }", scaled)
        self.assertIn("clamp(39px, 7vw, 69px)", scaled)
        self.assertIn(".c { font-size: 1.2em; }", scaled)

    def test_no_generated_font_size_is_below_the_smallest_floor(self):
        root = Path(__file__).resolve().parent.parent
        for name in ("web/css/site-theme.css", "web/assets/mom-components.css"):
            for size in re.findall(r"(?<![\w-])font(?:-size)?:\s*(?:[\w ]*? )?(\d*\.?\d+)px", (root / name).read_text()):
                self.assertGreaterEqual(float(size), scale_css.LABEL_FLOOR_PX, f"{name}: {size}px")
