"""Project the fixture site into a local directory so every component renders without a backend.

    python3 tools/preview_local.py /tmp/out

This writes only to the directory you name. It never touches a bucket: the content comes from tests/fixtures/content,
the knowledge snapshot from tests/fixtures/knowledge and the home-page data (references, threads) from
tests/fixtures/_data, which is copied into the output directory first because the projector reads the snapshot from where it writes.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import sync_section_pages  # noqa: E402

FIXTURE_DIRECTORY = REPOSITORY_ROOT / "tests" / "fixtures"
CONTENT_DIRECTORY = FIXTURE_DIRECTORY / "content"
KNOWLEDGE_DIRECTORY = FIXTURE_DIRECTORY / "knowledge"
HOME_PAGE_DATA_DIRECTORY = FIXTURE_DIRECTORY / "_data"
STATIC_DIRECTORY = REPOSITORY_ROOT / "web"
FIXTURE_ARTICLE_SECTION = {
    "field-notes": {
        "base": "field-notes",
        "label": "Field Notes",
        "description": "A section that exists only in the fixture site, so article pages have somewhere to live.",
    }
}


# The fixture section's words in each language Papyrus serves: a language is public only when it has a label (and a description, when the section has one) for every section
# with a listing page, and the fixture adds one, so the strings of the fixture copy of the site carry them.
FIXTURE_SECTION_STRINGS = {
    "en": {"section.field-notes.label": "Field Notes", "section.field-notes.description": FIXTURE_ARTICLE_SECTION["field-notes"]["description"]},
    "es-419": {"section.field-notes.label": "Notas de campo", "section.field-notes.description": "Una sección que existe solo en el sitio de prueba, para que las páginas de artículos tengan dónde vivir."},
    "zh-Hans": {"section.field-notes.label": "现场笔记", "section.field-notes.description": "一个只存在于测试站点中的栏目，让文章页面有处可放。"},
}


def static_directory_with_fixture_article_section(scratch_directory: Path) -> Path:
    """The published site declares no article section until the newsroom has one; the fixture site adds one so articles render (and its words, in every language the
    site's strings are written in)."""
    fixture_static_directory = scratch_directory / "web"
    shutil.copytree(STATIC_DIRECTORY, fixture_static_directory)
    projection_path = fixture_static_directory / "projection.json"
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["urls"]["sections"] = {**FIXTURE_ARTICLE_SECTION, **projection["urls"]["sections"]}
    projection_path.write_text(json.dumps(projection, indent=2, ensure_ascii=False), encoding="utf-8")
    for strings_path in (fixture_static_directory / "strings").glob("*.json"):
        strings = json.loads(strings_path.read_text(encoding="utf-8"))
        strings.update(FIXTURE_SECTION_STRINGS[strings_path.stem])
        strings_path.write_text(json.dumps(strings, indent=2, ensure_ascii=False), encoding="utf-8")
    return fixture_static_directory


def papyrus_executable() -> str:
    beside_interpreter = Path(sys.executable).parent / "papyrus"
    return str(beside_interpreter) if beside_interpreter.exists() else (shutil.which("papyrus") or "papyrus")


def project_fixture_site(output_directory: Path, home_page_data_directory: Path = HOME_PAGE_DATA_DIRECTORY, declares_sections: bool = True,
                         content_directory: Path | None = None, languages: dict | None = None) -> subprocess.CompletedProcess:
    """Project the fixture site. `declares_sections=False` projects a publication that declares no newsroom sections: no section is filed, so no block and no section page.
    `content_directory` replaces the fixture content. `languages` (the shape of the editorial settings' `languages`: `primary`, `enabled`, `prefixes`, `public`) projects
    the site as Papyrus serves several languages, from the Stories' `language` and `languageGroup` front matter (see tools/language_source.py); without it the site is
    projected by the `papyrus` command, in its one language."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    shutil.copytree(home_page_data_directory, output_directory / "_data", dirs_exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mom-fixture-static-") as scratch_directory:
        fixture_static_directory = static_directory_with_fixture_article_section(Path(scratch_directory))
        if not declares_sections:
            (fixture_static_directory / "sections.json").write_text(
                json.dumps({"articleCards": 12, "postCards": 12, "videoCards": 6, "findingCards": 3, "sections": []}), encoding="utf-8",
            )
            sync_section_pages.write_files(web=fixture_static_directory)
        content = str(content_directory or CONTENT_DIRECTORY)
        if languages is not None:
            command = [sys.executable, str(Path(__file__).with_name("language_source.py")), content, str(fixture_static_directory), str(KNOWLEDGE_DIRECTORY),
                       str(output_directory), json.dumps(languages)]
        else:
            command = [papyrus_executable(), "ops", "content", "project", "--all", "--from-dir", content, "--static-dir", str(fixture_static_directory),
                       "--knowledge-dir", str(KNOWLEDGE_DIRECTORY), "--out", str(output_directory)]
        return subprocess.run(command, capture_output=True, text=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 tools/preview_local.py OUTPUT_DIRECTORY")
    result = project_fixture_site(Path(sys.argv[1]))
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    raise SystemExit(result.returncode)
