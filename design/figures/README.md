# Figures

How Machines on Machines draws diagrams, charts and editorial illustrations. An agent should be able to draw a new figure from this folder alone.

| File | What it is |
| --- | --- |
| [`rules.md`](rules.md) | The rules, in role names. **Read it first.** |
| [`mapping.json`](mapping.json) | This publication's tokens, fonts and canvas sizes for those roles. |
| [`primitives.svg`](primitives.svg) | The glyphs, arrowhead and patterns every figure can use. |
| [`style-guide.md`](style-guide.md) | The `diagram-design` profile, generated from the three above. |
| [`gallery/`](gallery/) | Five worked figures. Copy the closest one. |
| [`fonts/`](fonts/) | Anton and Archivo (SIL Open Font License) for export. |

The pieces stay apart so another Papyrus publication could later keep `rules.md` and supply its own mapping. Tokens live in [`../system/tokens.json`](../system/tokens.json).

## Draw a figure

1. **Read** `rules.md`.
2. **Set up.** Install the renderer once:

   ```bash
   pip install playwright && playwright install chromium
   ```

   Google Chrome also works if it is installed.
3. **Make a folder** at `design/figures/gallery/<slug>/`. Copy `figure.svg` and `figure.json` from the closest gallery figure:

   | Drawing | Copy |
   | --- | --- |
   | Numbered steps | `search-nobody-sees` |
   | Timeline | `wiped-board` |
   | Layers, walls, things in between | `walls-and-gaps` |
   | Chart or forecast | `wall-and-climb` |
   | Illustration | `parked-car` |

4. **Write `figure.json` first.** Fill in `audience`, `shows`, `complements` and `surrounding_text` before you draw. If you can't, don't draw.
5. **Draw `figure.svg`**, with these conventions:
   - Colors are `{role}` names from `mapping.json` `figure_roles`, such as `fill="{inset}"`. Never a raw color.
   - Type is `class="t-label"` and so on, never a font attribute.
   - The first children of the `<svg>` are `<title>`, `<desc>`, then the line `<!--primitives-->`.
   - One `<text>` per line, placed by hand on the canvas. Geometry goes on a 4px grid.
   - Glyphs: `<use href="#machine" x="" y="" width="40" height="40" color="{machine-mark}"/>`.
   - Arrowheads: `marker-end="url(#arrow-head)"`. They take the line's color. Stop the line 8px short of its target.
6. **Render and check:**

   ```bash
   python3 tools/render_figures.py design/figures/gallery/<slug>
   ```

   This checks the source, then opens the figure in a real browser, in both themes, and fails on type below the phone floor, text past the margin or hanging over its fill, overlapping labels, low contrast, thin lines, a second focal mark, a missing stamp, navy outside an illustration, and raw colors. It writes `<slug>.png` and `<slug>.dark.png`. Fix every `PROBLEM`, and read every `note`.
7. **Look at it.** The tool can't judge whether it makes sense. View both PNGs at 343px wide, and once in grayscale. Check that rings don't touch letters.
8. **Hand it to a person.** Show both pictures. When they approve, set `approved_by` in `figure.json` to their name.
9. **Put it in the Story.** Copy both PNGs into the draft's pictures folder and print the line for the draft:

   ```bash
   python3 tools/render_figures.py --print-directive design/figures/gallery/<slug>
   ```

   Then follow "Saving a draft with its pictures" in Papyrus's `docs/story-reporting.md`. Papyrus pairs the `.dark` file automatically and makes the web renditions. Never publish without the person's confirmation.

## Install it as a `diagram-design` profile

Tested against `diagram-design` version 2.6, plugin build 2.6.141, commit `f24d98b05e2d7a5e68c2dedfe46e5b7173f50118`. Ask Ryan before installing the skill. The profile needs only:

```bash
mkdir -p ~/.diagram-design/profiles
```

```bash
cp design/figures/style-guide.md ~/.diagram-design/profiles/machines-on-machines.md
```

```bash
printf 'profile: machines-on-machines\n' > .diagram-design
```

Where they disagree, the profile's section "Where this overrides the skill" wins. Use the skill for choosing a form and its remove test, and export with `tools/render_figures.py`. After changing a rule, a token or the mapping, run:

```bash
python3 tools/build_figure_style_guide.py
```

`--check` fails if the guide is out of date, and CI runs it.

## Adopting this in another publication

Keep `rules.md`, `primitives.svg` and the tools. Write your own `mapping.json` that points to your tokens and fonts, then run the check. Nothing else names this brand.
