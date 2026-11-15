import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
sys.path.insert(0, str(REPOSITORY_ROOT / "tests"))

from preview_local import CONTENT_DIRECTORY, project_fixture_site  # noqa: E402
from reference_cases import write_reference_case  # noqa: E402


def project_to_temporary_directory(prefix: str = "mom-site-") -> Path:
    output_directory = Path(tempfile.mkdtemp(prefix=prefix))
    result = project_fixture_site(output_directory)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return output_directory


def page_text(output_directory: Path, route: str) -> str:
    relative = unquote(route).strip("/")
    target = output_directory / relative / "index.html" if relative else output_directory / "index.html"
    if not target.exists():
        raise AssertionError(f"{route} was not projected")
    return target.read_text(encoding="utf-8")


LINKING_ARTICLE_PATH = "security/an-article-that-links-a-video-rated-two-stars.md"


def content_linking_excluded_video(content_directory: Path, expected: dict) -> Path:
    """The fixture content plus one article whose text links directly to the first video the case excludes from video indexes."""
    shutil.copytree(CONTENT_DIRECTORY, content_directory)
    address = expected["videos"]["excluded"][0]
    article = (
        "---\ntype: article\ntitle: An article that links a video rated two stars\ndek: A fictional dek for an article with a direct link to a video.\n"
        "date: 2026-11-03\nupdated: 2026-11-03\nauthors: [Sam Rivera]\ntags: [Machines]\n---\n\n"
        f"A fictional article whose editors chose to link [this video]({address}) directly.\n"
    )
    (content_directory / LINKING_ARTICLE_PATH).write_text(article, encoding="utf-8")
    return content_directory


def project_reference_case(case: str, declares_sections: bool = True) -> tuple[Path, dict]:
    """Project the site with the snapshot of one case (see reference_cases.py), dated from today. Returns the output directory and what the pages should hold."""
    scratch = Path(tempfile.mkdtemp(prefix=f"mom-case-{case}-"))
    expected = write_reference_case(scratch / "_data", case, datetime.now(timezone.utc).date())
    output_directory = scratch / "out"
    content_directory = content_linking_excluded_video(scratch / "content", expected) if expected["videos"]["excluded"] else None
    result = project_fixture_site(output_directory, scratch / "_data", declares_sections, content_directory)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return output_directory, expected


def project_language_case(**options) -> Path:
    """Project the site with translations of two articles and a Concept (see language_cases.py)."""
    from language_cases import project_language_case as project

    return project(**options)
