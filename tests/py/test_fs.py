
import pytest
import shutil as sh
from common import *
from tem.fs import TemDir
from tem.errors import NotATemDirError


OUT_DIR = OUT_DIR / "py/temdir"


class TestTemDir:
    @classmethod
    def setup_class(cls):
        os.makedirs(OUT_DIR, exist_ok=True)

    def test_constructor(self):
        with pytest.raises(NotATemDirError):
            temdir = TemDir(OUT_DIR)

    @classmethod
    def teardown_class(cls):
        return
        sh.rmtree(OUT_DIR)
