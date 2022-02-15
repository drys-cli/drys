import os
import pathlib
import shutil

from contextlib import suppress

OUTDIR = os.environ.get("OUTDIR")
if not OUTDIR:
    raise EnvironmentError(
        "Environment for tests must contain an 'OUTDIR' variable"
    )
# Python test output goes to py/ subdirectory of generic test output directory
OUTDIR = pathlib.Path(OUTDIR) / "py"
#: Directory containing python test modules
TESTDIR = pathlib.Path(__file__).parent


def recreate_dir(path):
    with suppress(FileNotFoundError):
        shutil.rmtree(path)
    os.makedirs(path)


def setup_module():
    recreate_dir(OUTDIR)
