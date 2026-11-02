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


def static_directory_with_fixture_article_section(scratch_directory: Path) -> Path:
    """The published site declares no article section until the newsroom has one; the fixture site adds one so articles render."""
    fixture_static_directory = scratch_directory / "web"
    shutil.copytree(STATIC_DIRECTORY, fixture_static_directory)
    projection_path = fixture_static_directory / "projection.json"
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["urls"]["sections"] = {**FIXTURE_ARTICLE_SECTION, **projection["urls"]["sections"]}
    projection_path.write_text(json.dumps(projection, indent=2, ensure_ascii=False), encoding="utf-8")
    return fixture_static_directory


def papyrus_executable() -> str:
    beside_interpreter = Path(sys.executable).parent / "papyrus"
    return str(beside_interpreter) if beside_interpreter.exists() else (shutil.which("papyrus") or "papyrus")


def project_fixture_site(output_directory: Path) -> subprocess.CompletedProcess:
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    shutil.copytree(HOME_PAGE_DATA_DIRECTORY, output_directory / "_data", dirs_exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mom-fixture-static-") as scratch_directory:
        fixture_static_directory = static_directory_with_fixture_article_section(Path(scratch_directory))
        return subprocess.run(
            [
                papyrus_executable(), "ops", "content", "project", "--all",
                "--from-dir", str(CONTENT_DIRECTORY),
                "--static-dir", str(fixture_static_directory),
                "--knowledge-dir", str(KNOWLEDGE_DIRECTORY),
                "--out", str(output_directory),
            ],
            capture_output=True, text=True,
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 tools/preview_local.py OUTPUT_DIRECTORY")
    result = project_fixture_site(Path(sys.argv[1]))
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    raise SystemExit(result.returncode)
