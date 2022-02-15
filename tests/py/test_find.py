from common import *  # isort: skip
from tem import find

OUTDIR = OUTDIR / "find"

# These tests can only succeed inside a docker container, since only inside one
# can we control the structure of the entire directory hierarchy starting from /
class TestFind:
    @classmethod
    def setup_class(cls):
        os.mkdir(OUTDIR)

    # TODO implement
