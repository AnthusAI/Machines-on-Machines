import sys
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

from preview_local import project_fixture_site  # noqa: E402


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
