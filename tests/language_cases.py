"""A fixture site that has translations, for the language switcher's tests.

The ordinary fixture site is English only. This case copies its content and adds Spanish and Chinese pages for one article ("How to steer a story": all three
languages) and a Spanish page for another ("How to run a monitor": English and Spanish, no Chinese), and says which pages are translations of one another in
`web/language-groups.json` (see web/languages.py). Every other page has no translation, so it has no switcher and no banner.
"""

import json
import shutil
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPOSITORY_ROOT / "tests" / "fixtures" / "content"

STEER = {"en": "/field-notes/steer-a-story/", "es": "/field-notes/steer-a-story-es/", "zh-Hans": "/field-notes/steer-a-story-zh/"}
MONITOR = {"en": "/field-notes/run-a-monitor/", "es": "/field-notes/run-a-monitor-es/"}
UNTRANSLATED = "/field-notes/read-the-wire/"
GROUPS = [STEER, MONITOR]

TRANSLATED_PAGES = {
    "steer-a-story-es": ("Cómo dirigir una historia", "Añade una fuente, señala una afirmación o pide otro enfoque, y mira cómo cambia el borrador."),
    "steer-a-story-zh": ("如何引导一篇报道", "添加来源、标记一项说法，或要求换个角度，然后看草稿如何变化。"),
    "run-a-monitor-es": ("Cómo ejecutar un monitor", "Un monitor vigila una fuente y avisa a la redacción cuando cambia."),
}


def write_content(directory: Path) -> Path:
    content = directory / "content"
    shutil.copytree(CONTENT, content)
    for slug, (title, dek) in TRANSLATED_PAGES.items():
        (content / "field-notes" / f"{slug}.md").write_text(
            f"---\ntitle: {json.dumps(title, ensure_ascii=False)}\ndek: {json.dumps(dek, ensure_ascii=False)}\ndate: 2026-10-27\ntags: [Steering]\n"
            "drafting: {by: agent, at: 2026-10-26}\napproval: {status: approved, by: Ada Reader, at: 2026-10-27}\n---\n\nA fictional fixture translation.\n",
            encoding="utf-8",
        )
    return content


def project_language_case() -> Path:
    from preview_local import project_fixture_site

    scratch = Path(tempfile.mkdtemp(prefix="mom-language-case-"))
    output_directory = scratch / "out"
    result = project_fixture_site(output_directory, content_directory=write_content(scratch), language_groups=GROUPS)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return output_directory
