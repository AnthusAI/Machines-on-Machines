import shutil
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tests"))
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

from projection_support import project_to_temporary_directory  # noqa: E402


def before_all(context):
    context.repository_root = REPOSITORY_ROOT
    context.output_directory = project_to_temporary_directory("mom-features-")
    context.reference_cases = {}


def after_all(context):
    shutil.rmtree(context.output_directory, ignore_errors=True)
    for output_directory, _expected in context.reference_cases.values():
        shutil.rmtree(output_directory.parent, ignore_errors=True)
