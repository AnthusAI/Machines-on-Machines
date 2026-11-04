"""Check a figure's source and export its Day and Night pictures.

A figure is a folder holding figure.svg, written with {role} colors and t-<type role> classes, and figure.json, its
acceptance criteria, alt text and credit. See design/figures/README.md. One source draws both themes, so the two
pictures always share one geometry and the fonts are in the pixels, so nothing depends on a web font at display time.

    python3 tools/render_figures.py design/figures/gallery/wiped-board     check and export one figure
    python3 tools/render_figures.py --all                                  check and export every gallery figure
    python3 tools/render_figures.py --check-only <folder>                  check, writing nothing
    python3 tools/render_figures.py --print-directive <folder>             print the ::image{} line for the Story
    python3 tools/render_figures.py --standalone-html <out.html> <folder>  write the Day HTML, for the skill's own checks

Needs `pip install playwright` and a Chromium; run `playwright install chromium` or have Google Chrome installed.
"""

from __future__ import annotations

import base64
import json
import re
import struct
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
FIGURES_ROOT = REPOSITORY_ROOT / "design" / "figures"
GALLERY_ROOT = FIGURES_ROOT / "gallery"
MAX_PICTURE_BYTES = 10 * 1024 * 1024
MAX_RATIO_DIFFERENCE = 0.005
LABEL_TARGET_CHARACTERS = 25
LABEL_LIMIT_CHARACTERS = 30
REQUIRED_METADATA = ("slug", "kind", "audience", "shows", "complements", "surrounding_text", "alt", "caption", "labelled_as", "approved_by", "layout")
KINDS = ("diagram", "chart", "illustration")
LABELS = {"none": None, "forecast": "FORECAST, NOT DATA", "invented": "SCENARIO"}
THEME_IDS = ("light", "dark")
BANNED_ELEMENTS = ("filter", "linearGradient", "radialGradient", "image", "foreignObject", "script", "animate")
SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


def load_mapping() -> dict:
    return json.loads((FIGURES_ROOT / "mapping.json").read_text())


def load_tokens(mapping: dict) -> dict:
    return json.loads((REPOSITORY_ROOT / mapping["tokens_file"]).read_text())


def role_colors(mapping: dict, tokens: dict, theme_id: str) -> dict[str, str]:
    color_by_token = {token["name"]: token["value"][theme_id] for token in tokens["color"]["tokens"]}
    return {role: color_by_token[token_name] for role, token_name in mapping["figure_roles"].items()}


def type_style_rules(mapping: dict, tokens: dict, canvas_width: int) -> str:
    size_scale = canvas_width / mapping["canvas"]["diagram_width"]
    styles = {style["name"]: (style, group["family"]) for group in tokens["type"]["groups"] for style in group["styles"]}
    rules = []
    for type_role, style_name in mapping["type_roles"].items():
        style, family_key = styles[style_name]
        declarations = [
            f"font-family:'{mapping['fonts'][family_key]['family']}',sans-serif",
            f"font-size:{float(style['fontSize'].removesuffix('px')) * size_scale:.2f}px",
            f"font-weight:{style['fontWeight']}",
        ]
        if "letterSpacing" in style:
            declarations.append(f"letter-spacing:{style['letterSpacing']}")
        if type_role in mapping["uppercase_type_roles"]:
            declarations.append("text-transform:uppercase")
        rules.append(f".t-{type_role}{{{';'.join(declarations)}}}")
    return "\n".join(rules)


def font_face_rules(mapping: dict) -> str:
    rules = []
    for font in mapping["fonts"].values():
        encoded_font = base64.b64encode((FIGURES_ROOT / font["file"]).read_bytes()).decode()
        rules.append(f"@font-face{{font-family:'{font['family']}';font-weight:{font['weight']};src:url(data:font/ttf;base64,{encoded_font}) format('truetype');font-display:block}}")
    return "\n".join(rules)


def resolve_roles(source: str, colors: dict[str, str]) -> str:
    return re.sub(r"\{([a-z-]+)\}", lambda match: colors[match.group(1)], source)


def figure_document(figure_source: str, colors: dict[str, str], mapping: dict, tokens: dict, slug: str, use_web_fonts: bool = False) -> str:
    canvas_width = int(re.search(r'viewBox="0 0 (\d+) ', figure_source).group(1))
    primitives = (FIGURES_ROOT / "primitives.svg").read_text()
    svg = figure_source.replace("<!--primitives-->", resolve_roles(primitives, colors))
    svg = resolve_roles(svg, colors)
    fonts = f'<link href="{mapping["web_font_link"]}" rel="stylesheet">' if use_web_fonts else f"<style>{font_face_rules(mapping)}</style>"
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{slug}</title>{fonts}'
        f"<style>html,body{{margin:0;background:transparent}}svg{{display:block}}\n{type_style_rules(mapping, tokens, canvas_width)}</style>"
        f"</head><body>{svg}</body></html>"
    )


def source_problems(figure_source: str, metadata: dict, mapping: dict) -> list[str]:
    problems = []
    for key in REQUIRED_METADATA:
        if key not in metadata or (metadata[key] in ("", None) and key != "approved_by"):
            problems.append(f"figure.json is missing {key}")
    kind = metadata.get("kind")
    if kind not in KINDS:
        problems.append(f"kind must be one of {KINDS}")
    label_kind = metadata.get("labelled_as")
    if label_kind not in LABELS:
        problems.append(f"labelled_as must be one of {tuple(LABELS)}")
    elif LABELS[label_kind] and LABELS[label_kind] not in figure_source:
        problems.append(f'the picture must carry the stamp "{LABELS[label_kind]}"')
    if "<!--primitives-->" not in figure_source:
        problems.append("figure.svg must include the <!--primitives--> line after <desc>")
    if re.search(r"#[0-9a-fA-F]{3,8}\b(?!-)", re.sub(r'(?:href|url\()\s*=?\s*"?#[\w-]+', "", figure_source)):
        problems.append("figure.svg holds a raw color; use {role} names")
    unknown_roles = set(re.findall(r"\{([a-z-]+)\}", figure_source)) - set(mapping["figure_roles"])
    if unknown_roles:
        problems.append(f"unknown color roles: {sorted(unknown_roles)}")
    if "{brand}" in figure_source and kind != "illustration":
        problems.append("brand navy appears only in illustrations")
    if re.search(r"font-size|font-family|font-weight", figure_source):
        problems.append("set type only with t-<role> classes")
    if re.search(r'opacity="', figure_source):
        problems.append("no opacity; every color is a solid role")
    if kind != "illustration" and "rotate(" in figure_source:
        problems.append("nothing tilts in a diagram or chart")
    focal_count = len(re.findall(r'data-focal="true"', figure_source))
    if focal_count > 1:
        problems.append(f"{focal_count} focal marks; one is the limit")
    try:
        root = ElementTree.fromstring(re.sub(r"\{[a-z-]+\}", "x", figure_source).replace("<!--primitives-->", ""))
    except ElementTree.ParseError as error:
        return problems + [f"figure.svg is not valid XML: {error}"]
    if root.get("role") != "img" or not root.get("aria-labelledby"):
        problems.append('the <svg> needs role="img" and aria-labelledby')
    children = list(root)
    if len(children) < 2 or children[0].tag != f"{SVG_NAMESPACE}title" or children[1].tag != f"{SVG_NAMESPACE}desc":
        problems.append("<title> and <desc> must be the first two children of the <svg>")
    view_box = [float(value) for value in root.get("viewBox", "0 0 0 0").split()]
    if view_box[2] != root_canvas_width(kind, mapping):
        problems.append(f"canvas width must be {root_canvas_width(kind, mapping)}")
    if kind != "illustration" and view_box[3] > mapping["canvas"]["max_height"]:
        problems.append(f"canvas is {view_box[3]:.0f} tall; over {mapping['canvas']['max_height']} means split the figure")
    for element in root.iter():
        name = element.tag.replace(SVG_NAMESPACE, "")
        if name in BANNED_ELEMENTS:
            problems.append(f"<{name}> is not allowed")
    return problems


def root_canvas_width(kind: str | None, mapping: dict) -> int:
    return mapping["canvas"]["illustration_width"] if kind == "illustration" else mapping["canvas"]["diagram_width"]


RENDERED_CHECK_SCRIPT = """
(canvas) => {
  const svg = document.querySelector('svg');
  const scale = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
  const rgb = (value) => { const m = value.match(/rgba?\\((\\d+), (\\d+), (\\d+)/); return m ? [+m[1], +m[2], +m[3]] : null; };
  const under = (element, x, y) => {
    for (const candidate of document.elementsFromPoint(x, y)) {
      if (candidate === element || candidate.closest('text') || candidate.tagName === 'svg') continue;
      const color = rgb(getComputedStyle(candidate).fill);
      if (color) return color;
    }
    return null;
  };
  const texts = [...document.querySelectorAll('svg text')].map((element) => {
    const box = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return {
      text: element.textContent.trim(), left: box.left, right: box.right, top: box.top, bottom: box.bottom,
      fontFamily: style.fontFamily.split(',')[0].replaceAll('"', ''), fontSize: parseFloat(style.fontSize), fontWeight: style.fontWeight,
      textRole: element.getAttribute('class') || '', fill: rgb(style.fill), ground: under(element, (box.left + box.right) / 2, (box.top + box.bottom) / 2),
      groundLeft: under(element, box.left + 2, (box.top + box.bottom) / 2), groundRight: under(element, box.right - 2, (box.top + box.bottom) / 2),
    };
  });
  const lines = [...document.querySelectorAll('svg line, svg path[stroke], svg polyline, svg circle[stroke]')].filter((e) => !e.closest('defs, symbol, marker, pattern')).map((element) => ({
    tag: element.tagName, width: parseFloat(element.getAttribute('stroke-width') || '0'),
  }));
  return { texts, lines, scale, fontsLoaded: [...document.fonts].map((font) => font.family + ':' + font.status) };
}
"""


def relative_luminance(color: list[int]) -> float:
    def channel(value: int) -> float:
        fraction = value / 255
        return fraction / 12.92 if fraction <= 0.04045 else ((fraction + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(color[0]) + 0.7152 * channel(color[1]) + 0.0722 * channel(color[2])


def contrast_ratio(first: list[int], second: list[int]) -> float:
    lighter, darker = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def rendered_problems(measurements: dict, canvas_width: int, canvas_height: float, mapping: dict, theme_id: str, kind: str) -> tuple[list[str], list[str]]:
    problems, warnings = [], []
    canvas = mapping["canvas"]
    phone_scale = canvas["phone_width"] / canvas_width
    margin = canvas["margin"]
    texts = measurements["texts"]
    for text in texts:
        if text["fontFamily"] not in {font["family"] for font in mapping["fonts"].values()}:
            problems.append(f'{theme_id}: "{text["text"]}" is not in a brand font ({text["fontFamily"]})')
        phone_size = text["fontSize"] * phone_scale
        if phone_size < canvas["phone_text_min"] - 0.05:
            problems.append(f'{theme_id}: "{text["text"]}" is {phone_size:.1f}px on a phone; the floor is {canvas["phone_text_min"]}px')
        if not text["textRole"].startswith("t-"):
            problems.append(f'{theme_id}: "{text["text"]}" has no t-<role> class')
        characters = len(text["text"])
        if characters > LABEL_LIMIT_CHARACTERS:
            problems.append(f'"{text["text"]}" is {characters} characters; the limit is {LABEL_LIMIT_CHARACTERS}. Break it onto a second line or cut it')
        elif characters > LABEL_TARGET_CHARACTERS:
            warnings.append(f'"{text["text"]}" is {characters} characters; aim for {LABEL_TARGET_CHARACTERS}')
        if text["left"] < margin - 0.5 or text["right"] > canvas_width - margin + 0.5 or text["top"] < 0 or text["bottom"] > canvas_height:
            problems.append(f'{theme_id}: "{text["text"]}" crosses the {margin}px margin')
        if text["ground"] != text["groundLeft"] or text["ground"] != text["groundRight"]:
            problems.append(f'{theme_id}: "{text["text"]}" hangs over the edge of the shape behind it')
        minimum_ratio = 3.0 if phone_size >= 24 else 4.5
        for ground in (text["ground"], text["groundLeft"], text["groundRight"]):
            if ground is None or text["fill"] is None:
                problems.append(f'{theme_id}: "{text["text"]}" has no solid fill behind it')
                break
            ratio = contrast_ratio(text["fill"], ground)
            if ratio < minimum_ratio:
                problems.append(f'{theme_id}: "{text["text"]}" has contrast {ratio:.2f}:1; it needs {minimum_ratio}:1')
                break
    for index, first in enumerate(texts):
        for second in texts[index + 1:]:
            overlap_width = min(first["right"], second["right"]) - max(first["left"], second["left"])
            overlap_height = min(first["bottom"], second["bottom"]) - max(first["top"], second["top"])
            if overlap_width > 1 and overlap_height > (first["bottom"] - first["top"]) * 0.45:
                problems.append(f'{theme_id}: "{first["text"]}" overlaps "{second["text"]}"')
    minimum_line = canvas["phone_line_min"] / phone_scale
    for line in measurements["lines"]:
        if line["width"] and line["width"] < minimum_line - 0.05:
            problems.append(f'{theme_id}: a {line["tag"]} is {line["width"]}px; the thinnest allowed here is {minimum_line:.1f}px')
    return problems, warnings


def open_browser(playwright):
    try:
        return playwright.chromium.launch()
    except Exception:
        return playwright.chromium.launch(channel="chrome")


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    return struct.unpack(">II", header[16:24])


def picture_problems(light_path: Path, dark_path: Path) -> list[str]:
    problems = []
    light_width, light_height = png_size(light_path)
    dark_width, dark_height = png_size(dark_path)
    light_ratio, dark_ratio = light_width / light_height, dark_width / dark_height
    if abs(light_ratio - dark_ratio) / light_ratio > MAX_RATIO_DIFFERENCE:
        problems.append(f"Day and Night ratios differ: {light_ratio:.4f} and {dark_ratio:.4f}")
    for path in (light_path, dark_path):
        if path.stat().st_size >= MAX_PICTURE_BYTES:
            problems.append(f"{path.name} is 10 MB or more")
    return problems


def image_directive(metadata: dict) -> str:
    credit = f'  credit="{metadata["credit"]}"\n' if metadata.get("credit") else ""
    return (
        f'::image{{\n  src="{metadata["slug"]}.png"\n  layout="{metadata["layout"]}"\n'
        f'  alt="{metadata["alt"]}"\n  caption="{metadata["caption"]}"\n{credit}}}'
    )


def check_and_export_figure(browser, figure_folder: Path, mapping: dict, tokens: dict, write_pictures: bool = True) -> bool:
    figure_source = (figure_folder / "figure.svg").read_text()
    metadata = json.loads((figure_folder / "figure.json").read_text())
    slug = metadata.get("slug", figure_folder.name)
    problems = source_problems(figure_source, metadata, mapping)
    warnings: list[str] = []
    if problems:
        return report_figure(slug, problems, warnings)
    view_box = [float(value) for value in re.search(r'viewBox="([^"]+)"', figure_source).group(1).split()]
    canvas_width, canvas_height = int(view_box[2]), view_box[3]
    scale = mapping["canvas"]["export_scale"]
    for theme_id in THEME_IDS:
        colors = role_colors(mapping, tokens, theme_id)
        page = browser.new_page(viewport={"width": canvas_width, "height": int(canvas_height)}, device_scale_factor=scale, java_script_enabled=True)
        page.set_content(figure_document(figure_source, colors, mapping, tokens, slug), wait_until="load")
        page.evaluate("document.fonts.ready")
        theme_problems, theme_warnings = rendered_problems(page.evaluate(RENDERED_CHECK_SCRIPT, mapping["canvas"]), canvas_width, canvas_height, mapping, theme_id, metadata["kind"])
        problems += theme_problems
        warnings += [warning for warning in theme_warnings if warning not in warnings]
        if write_pictures:
            suffix = ".dark.png" if theme_id == "dark" else ".png"
            page.locator("svg").first.screenshot(path=str(figure_folder / f"{slug}{suffix}"), omit_background=True)
        page.close()
    if write_pictures:
        problems += picture_problems(figure_folder / f"{slug}.png", figure_folder / f"{slug}.dark.png")
    return report_figure(slug, problems, warnings)


def report_figure(slug: str, problems: list[str], warnings: list[str]) -> bool:
    for warning in warnings:
        print(f"{slug}: note: {warning}")
    for problem in problems:
        print(f"{slug}: PROBLEM: {problem}")
    print(f"{slug}: {'FAILED' if problems else 'ok'}")
    return not problems


def main(arguments: list[str]) -> int:
    from playwright.sync_api import sync_playwright

    mapping, tokens = load_mapping(), load_tokens(load_mapping())
    if "--print-directive" in arguments:
        folder = Path(arguments[arguments.index("--print-directive") + 1])
        print(image_directive(json.loads((folder / "figure.json").read_text())))
        return 0
    if "--standalone-html" in arguments:
        position = arguments.index("--standalone-html")
        output_path, folder = Path(arguments[position + 1]), Path(arguments[position + 2])
        metadata = json.loads((folder / "figure.json").read_text())
        colors = role_colors(mapping, tokens, "light")
        output_path.write_text(figure_document((folder / "figure.svg").read_text(), colors, mapping, tokens, metadata["slug"], use_web_fonts=True))
        return 0
    write_pictures = "--check-only" not in arguments
    folders = [Path(argument) for argument in arguments if not argument.startswith("--")]
    if "--all" in arguments:
        folders = sorted(path.parent for path in GALLERY_ROOT.glob("*/figure.svg"))
    if not folders:
        print(__doc__)
        return 2
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        results = [check_and_export_figure(browser, folder, mapping, tokens, write_pictures) for folder in folders]
        browser.close()
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
