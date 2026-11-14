"""Build the folder Papyrus stores as this site's design system (`papyrus design-system push`) from the sources in this repository.

Papyrus reads a design system as one folder (Papyrus docs/figures.md, "The design system as backend data"): `mapping.json` at its root, the tokens
file and the fonts it names (paths relative to that root), the worked examples as `examples/NAME/figure.svg` + `figure.json`, and `settings.json`
(the site settings, such as `publishRequiresRating`). Here those pieces live apart: the mapping, the fonts, the settings and the worked figures
(`gallery/`) in `design/figures/`, and the tokens in `design/system/tokens.json`, which the site's stylesheets are built from too. This copies each
into that one folder, byte for byte, at the path the mapping names it by; nothing is rewritten.

    python3 tools/build_design_system.py --out DIR     write the folder (DIR must be new or empty)

The deploy builds and pushes it after every release (`.github/workflows/deploy.yml`, job `design-system`); see design/figures/README.md.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
FIGURES_ROOT = REPOSITORY_ROOT / "design" / "figures"
GALLERY_ROOT = FIGURES_ROOT / "gallery"
MAPPING_FILE = "mapping.json"
SETTINGS_FILE = "settings.json"
EXAMPLE_FILES = ("figure.svg", "figure.json")


def design_system_files() -> dict[str, Path]:
    """Each file of the design system folder, by its path in the folder, and the repository file it is copied from."""
    mapping = json.loads((FIGURES_ROOT / MAPPING_FILE).read_text(encoding="utf-8"))
    files = {
        MAPPING_FILE: FIGURES_ROOT / MAPPING_FILE,
        mapping["tokens_file"]: REPOSITORY_ROOT / mapping["tokens_file"],  # the mapping names the tokens by their path in this repository
        SETTINGS_FILE: FIGURES_ROOT / SETTINGS_FILE,
    }
    for font in mapping["fonts"].values():
        files[font["file"]] = FIGURES_ROOT / font["file"]  # and the fonts by their path in design/figures
    for svg in sorted(GALLERY_ROOT.glob("*/figure.svg")):
        for leaf in EXAMPLE_FILES:
            files[f"examples/{svg.parent.name}/{leaf}"] = svg.parent / leaf
    return files


def build(out: Path) -> list[str]:
    """Write the design system folder into ``out`` (new or empty). Returns the paths written."""
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} is not empty; build into a new folder.")
    written = []
    for name, source in design_system_files().items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        written.append(name)
    return written


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=Path, help="the folder to write (new or empty)")
    arguments = parser.parse_args(argv)
    for name in build(arguments.out):
        print(f"design-system\tbuild\twrote\t{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
