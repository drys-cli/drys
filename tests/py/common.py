import os
import pathlib
import shutil

OUTDIR = os.environ.get("OUTDIR")
if not OUTDIR:
    raise EnvironmentError(
        "Environment for tests must contain an 'OUTDIR' " "variable"
    )
# Use outdir for python tests
OUTDIR = pathlib.Path(OUTDIR) / "py"


def setup_module():
    try:
        shutil.rmtree(OUTDIR)
    except FileNotFoundError:
        pass
    os.makedirs(OUTDIR)
