import unittest
from pathlib import Path

CSS = (Path(__file__).resolve().parent.parent / "web" / "css-src" / "site-theme.src.css").read_text()


class HomeGridGapTest(unittest.TestCase):
    def test_home_reference_grids_have_a_row_gap_after_the_tile_padding_is_zeroed(self):
        zeroed = CSS.index(".rh-home .home-page-grid > li, .rh-home .home-page-grid > li:has(> .mom-reference-card)")
        gap = CSS.index(".rh-home .home-page-grid:has(> li > .mom-reference-card) { row-gap: var(--space-5); }")
        self.assertGreater(gap, zeroed)


if __name__ == "__main__":
    unittest.main()
