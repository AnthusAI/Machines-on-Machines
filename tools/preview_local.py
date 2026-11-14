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
from urllib.parse import quote

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


def static_directory_with_fixture_article_section(scratch_directory: Path, extra_sections: dict | None = None, extra_pages: list | None = None) -> Path:
    """The published site declares no article section until the newsroom has one; the fixture site adds one so articles render. `extra_sections` adds more
    (`{folder in the content directory: {base, label, description}}`, used to put a language's pages under its URL prefix) and `extra_pages` adds
    `{id, path, title, description, source, text}` pages (a language's home)."""
    fixture_static_directory = scratch_directory / "web"
    shutil.copytree(STATIC_DIRECTORY, fixture_static_directory)
    projection_path = fixture_static_directory / "projection.json"
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["urls"]["sections"] = {**FIXTURE_ARTICLE_SECTION, **(extra_sections or {}), **projection["urls"]["sections"]}
    for page in extra_pages or []:
        (fixture_static_directory / page["source"]).write_text(page["text"], encoding="utf-8")
        projection["pages"].append({key: page[key] for key in ("id", "path", "title", "description", "source")})
    projection_path.write_text(json.dumps(projection, indent=2, ensure_ascii=False), encoding="utf-8")
    return fixture_static_directory


def papyrus_executable() -> str:
    beside_interpreter = Path(sys.executable).parent / "papyrus"
    return str(beside_interpreter) if beside_interpreter.exists() else (shutil.which("papyrus") or "papyrus")


TEXT_OUTPUT_SUFFIXES = {".html", ".md", ".xml", ".txt", ".json"}


def put_pages_at_unicode_paths(output_directory: Path, unicode_page_paths: dict[str, str]) -> None:
    """Move each page the engine wrote at a stand-in ASCII address to its real Unicode address, and write that address percent-encoded wherever the site refers to it.

    Papyrus 5.109.0 reduces a slug to ASCII (`papyrus_content.projection.source.split_output_path` slugifies every segment), so a Chinese slug cannot be projected yet. Until
    the engine keeps them, the preview and the tests project such a page under a stand-in slug and this step makes the output what the engine will write: the page's
    directory has the characters as its name, and its `canonical`, `hreflang`, switcher options, links, `llms.txt` and sitemap carry the percent-encoded address, which is
    what an address copied from the browser looks like. `unicode_page_paths` is `{real path: stand-in path}`."""
    for real_path, stand_in_path in unicode_page_paths.items():
        encoded = quote(real_path, safe="/")
        for target in output_directory.rglob("*"):
            if target.is_file() and target.suffix in TEXT_OUTPUT_SUFFIXES:
                text = target.read_text(encoding="utf-8")
                if stand_in_path in text:
                    target.write_text(text.replace(stand_in_path, encoded), encoding="utf-8")
        source = output_directory / stand_in_path.strip("/")
        destination = output_directory / real_path.strip("/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)


def project_fixture_site(output_directory: Path, home_page_data_directory: Path = HOME_PAGE_DATA_DIRECTORY, declares_sections: bool = True,
                         content_directory: Path | None = None, language_groups: list | None = None, language_prefixes: dict | None = None,
                         extra_sections: dict | None = None, extra_pages: list | None = None, unicode_page_paths: dict | None = None) -> subprocess.CompletedProcess:
    """Project the fixture site. `declares_sections=False` projects a publication that declares no newsroom sections: no section is filed, so no block and no section page.
    `content_directory` replaces the fixture content, and `language_groups` (`[{language tag: page path}]`, see web/languages.py) says which pages are translations of one another and `language_prefixes`
    (`{language tag: URL prefix}`) where each non-primary language lives; `extra_sections` and `extra_pages` put a language's pages under its prefix.
    `unicode_page_paths` (`{real path: stand-in path}`, see `put_pages_at_unicode_paths`) is for pages whose slug is not ASCII: the groups may name the real path."""
    stand_ins = unicode_page_paths or {}
    if stand_ins and language_groups:
        language_groups = [{tag: stand_ins.get(path, path) for tag, path in group.items()} for group in language_groups]
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    shutil.copytree(home_page_data_directory, output_directory / "_data", dirs_exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mom-fixture-static-") as scratch_directory:
        fixture_static_directory = static_directory_with_fixture_article_section(Path(scratch_directory), extra_sections, extra_pages)
        if language_groups is not None or language_prefixes is not None:
            (fixture_static_directory / "language-groups.json").write_text(
                json.dumps({"prefixes": language_prefixes or {}, "groups": language_groups or []}, ensure_ascii=False), encoding="utf-8")
        if not declares_sections:
            (fixture_static_directory / "sections.json").write_text(
                json.dumps({"articleCards": 12, "postCards": 12, "videoCards": 6, "findingCards": 3, "sections": []}), encoding="utf-8",
            )
            sync_section_pages.write_files(web=fixture_static_directory)
        result = subprocess.run(
            [
                papyrus_executable(), "ops", "content", "project", "--all",
                "--from-dir", str(content_directory or CONTENT_DIRECTORY),
                "--static-dir", str(fixture_static_directory),
                "--knowledge-dir", str(KNOWLEDGE_DIRECTORY),
                "--out", str(output_directory),
            ],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and stand_ins:
            put_pages_at_unicode_paths(output_directory, stand_ins)
        return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 tools/preview_local.py OUTPUT_DIRECTORY")
    result = project_fixture_site(Path(sys.argv[1]))
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    raise SystemExit(result.returncode)
