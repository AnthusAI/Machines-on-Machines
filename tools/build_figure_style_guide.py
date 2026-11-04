"""Build the diagram-design style guide from the figure rules, this publication's mapping and its tokens.

The guide follows the skill's profile format (diagram-design 2.6), so its semantic roles and type roles are tables the
skill and its contrast check can read. The rules stay in design/figures/rules.md and name roles only.

    python3 tools/build_figure_style_guide.py           write design/figures/style-guide.md
    python3 tools/build_figure_style_guide.py --check   exit 1 when the guide differs (CI)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
FIGURES_ROOT = REPOSITORY_ROOT / "design" / "figures"
GUIDE_PATH = FIGURES_ROOT / "style-guide.md"
PROFILE_DATE = "2026-11-04"

OVERRIDES = """## Where this overrides the skill

Where the skill and this guide disagree, this guide wins. The rules below are the full text; this list tells a reader of the skill what changes.

| The skill says | Here |
| --- | --- |
| Self-contained HTML is the deliverable, and export is manual | The deliverable is a Day and a Night PNG, from `tools/render_figures.py` |
| Canvas `doc-inline` 960×600, kept wide with a scroll wrapper | Canvas 680 wide and any height to 1100, never scrolled; illustrations 960×540 |
| Node names 12px, sublabels 9px, eyebrows 7 to 8px | Nothing under 26px on a 680 canvas (13px on a phone) |
| Three families: serif, sans, mono | Anton and Archivo only. The serif title and callout and every mono role are retired |
| Accent is a hue on one or two nodes, with a tinted fill and a colored stroke | One inverted ink tile per figure, no hue, no stroke |
| Node boxes have 1px strokes, `rule` hairlines, radius 6 | No outlines or hairlines. Containers separate by fill, radius 12 or 16 |
| `stroke-thin` 0.8, `stroke-default` 1, `stroke-strong` 1.2 | 4px minimum, 6 for connectors, 8 for series, 12 for a fixed line, 16 for a wall |
| Arrow labels, all caps, on masks | Labels sit beside the line in sentence case. Masks are never needed |
| Legend strip with a hairline | A key row with no line, and only when direct labels can't do it |
| Series palette | Removed. Series differ by label, line style, pattern and end shape |
| Horizontal timeline with labels alternating above and below | Top to bottom, one equal row per time unit |
| 9 nodes, 12 arrows, 2 callouts, 2 accents | 9 named things, 6 connectors, no callouts, 1 focal mark, and 14 labels in total |
| Dotted paper, sketchy and terminal variants, motion | Not used. Figures are static |
| Paper should be warm, keep the serif | Not applied; the brand's cool paper and two families stand |

Keep from the skill: choose a semantic pattern and a form before drawing; the remove test in its taste gate; orthogonal connectors that attach perpendicular to an edge and never pass behind a tile; honest time scales; the accessible title and description.
"""


def color_values(tokens: dict) -> dict[str, dict[str, str]]:
    return {token["name"]: token["value"] for token in tokens["color"]["tokens"]}


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def semantic_roles_table(mapping: dict, colors: dict) -> str:
    rows = ["| Role | Purpose | Default (light) | Default (dark) |", "|---|---|---|---|"]
    for role, entry in mapping["skill_roles"].items():
        value = colors[entry["token"]]
        rows.append(f"| `{role}` | {entry['note']} (token `{entry['token']}`) | `{value['light']}` | `{value['dark']}` |")
    return "\n".join(rows)


def figure_roles_table(mapping: dict, colors: dict) -> str:
    rows = ["| Figure role | Token | Day | Night |", "|---|---|---|---|"]
    for role, token_name in mapping["figure_roles"].items():
        value = colors[token_name]
        rows.append(f"| `{{{role}}}` | `{token_name}` | `{value['light']}` | `{value['dark']}` |")
    return "\n".join(rows)


def contrast_table(mapping: dict, colors: dict) -> str:
    rows = ["| Foreground | Background | Day | Night |", "|---|---|---|---|"]
    for foreground, background in mapping["contrast_pairs"]:
        foreground_value = colors[mapping["figure_roles"][foreground]]
        background_value = colors[mapping["figure_roles"][background]]
        day, night = (contrast_ratio(foreground_value[theme], background_value[theme]) for theme in ("light", "dark"))
        rows.append(f"| `{foreground}` | `{background}` | {day:.2f}:1 | {night:.2f}:1 |")
    return "\n".join(rows)


def typography_table(mapping: dict, tokens: dict) -> str:
    styles = {style["name"]: (style, group["family"]) for group in tokens["type"]["groups"] for style in group["styles"]}
    rows = ["| Role | Family | Size | Weight | Usage |", "|---|---|---|---|---|"]
    for role, entry in mapping["skill_type_roles"].items():
        style, family_key = styles[entry["style"]]
        rows.append(f"| `{role}` | {mapping['fonts'][family_key]['family']} | {style['fontSize']} | {style['fontWeight']} | {entry['usage']} |")
    return "\n".join(rows)


def build_guide() -> str:
    mapping = json.loads((FIGURES_ROOT / "mapping.json").read_text())
    tokens = json.loads((REPOSITORY_ROOT / mapping["tokens_file"]).read_text())
    colors = color_values(tokens)
    profile = mapping["profile"]
    rules = (FIGURES_ROOT / "rules.md").read_text().split("\n", 1)[1].strip()
    return f"""<!-- diagram-design-profile
name: {profile['name']}
slug: {profile['slug']}
source-url: {profile['source_url']}
created: {PROFILE_DATE}
updated: {PROFILE_DATE}
notes: {profile['notes']}
-->
# Style Guide

The complete figure style for {mapping['publication']}. Generated by `tools/build_figure_style_guide.py` from `design/figures/rules.md`, `mapping.json` and `{mapping['tokens_file']}`. Tested with diagram-design 2.6 (plugin build 2.6.141, commit f24d98b).

## Tokens

### Semantic roles

{semantic_roles_table(mapping, colors)}

### Figure roles

Figure sources use these names, written `{{role}}`. The renderer fills in the value for each theme.

{figure_roles_table(mapping, colors)}

### Contrast contract

Text needs 4.5:1 against the fill behind it, or 3:1 when it is 24px or larger on a phone. Lines and marks need 3:1. The renderer measures every text element in both themes. The pairs used in figures measure:

{contrast_table(mapping, colors)}

Tints and the hatch are near the ground in lightness on purpose, so they never carry meaning alone.

### Series palette

None. See "Telling series apart".

## Typography

{typography_table(mapping, tokens)}

Sizes are on a 680px canvas, which a phone shows at 343px.

### Font source

Font source: web

A web-font link is for the skill's own HTML. Published figures are PNGs with the type in the pixels, exported using the fonts in `design/figures/fonts/`, so a reader's device loads no font.

## Stroke, radius, spacing

| Token | Value | Use |
|---|---|---|
| `stroke-thin` | `4` | The thinnest line allowed |
| `stroke-default` | `6` | Connectors, rails, axes, rings |
| `stroke-strong` | `8` | Chart series. A fixed-value line is 12, a wall bar is 16 |
| `radius-sm` | `12` | Tiles and stamps |
| `radius-md` | `16` | Tiles that hold other tiles |
| `radius-lg` | `22` | The figure's ground |
| `grid` | `4` | Geometry sits on this grid |

## Node type → treatment

| Type | Fill | Stroke |
|---|---|---|
| `focal` (one) | `{{focal}}` | None |
| `backend` | `{{inset}}` | None |
| `store` | `{{inset}}` with `#file` | None |
| `external` | `{{inset}}` with `#globe` | None |
| `input` | `{{human-fill}}` with `#person` | None |
| `optional` | Not drawn; say it in words | None |
| `security` | A wall bar | None |
| A machine | `{{machine-fill}}` with `#machine` | None |

{OVERRIDES}
# The rules

{rules}
"""


if __name__ == "__main__":
    guide = build_guide()
    if "--check" in sys.argv[1:]:
        if not GUIDE_PATH.is_file() or GUIDE_PATH.read_text() != guide:
            raise SystemExit("design/figures/style-guide.md is out of date; run python3 tools/build_figure_style_guide.py")
    else:
        GUIDE_PATH.write_text(guide)
