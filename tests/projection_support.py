import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
sys.path.insert(0, str(REPOSITORY_ROOT / "tests"))

from preview_local import project_fixture_site  # noqa: E402
from reference_cases import write_reference_case  # noqa: E402


def project_to_temporary_directory(prefix: str = "mom-site-") -> Path:
    output_directory = Path(tempfile.mkdtemp(prefix=prefix))
    result = project_fixture_site(output_directory)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return output_directory


def page_text(output_directory: Path, route: str) -> str:
    relative = route.strip("/")
    target = output_directory / relative / "index.html" if relative else output_directory / "index.html"
    if not target.exists():
        raise AssertionError(f"{route} was not projected")
    return target.read_text(encoding="utf-8")


def project_reference_case(case: str, declares_sections: bool = True) -> tuple[Path, dict]:
    """Project the site with the snapshot of one case (see reference_cases.py), dated from today. Returns the output directory and what the pages should hold."""
    scratch = Path(tempfile.mkdtemp(prefix=f"mom-case-{case}-"))
    expected = write_reference_case(scratch / "_data", case, datetime.now(timezone.utc).date())
    output_directory = scratch / "out"
    result = project_fixture_site(output_directory, scratch / "_data", declares_sections)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return output_directory, expected
