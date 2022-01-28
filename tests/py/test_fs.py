import pytest
import shutil as sh
from common import *
from tem.fs import TemDir
from tem.errors import NotATemDirError


OUT_DIR = OUT_DIR / "py/fs"
TEMDIR = OUT_DIR / "temdir"
TEMDIR1 = TEMDIR / "dir1"
TEMDIR2 = TEMDIR1 / "dir2"
NOT_A_TEMDIR = OUT_DIR / "not_a_temdir"


class TestTemDir:
    @classmethod
    def setup_class(cls):
        os.makedirs(TEMDIR2, exist_ok=True)
        os.makedirs(NOT_A_TEMDIR, exist_ok=True)
        TemDir.init(TEMDIR)
        TemDir.init(TEMDIR1)
        TemDir.init(TEMDIR2)

    def test_constructor(self):
        temdir = TemDir(TEMDIR)
        with pytest.raises(NotATemDirError):
            temdir = TemDir(NOT_A_TEMDIR)

    def test_tem_parent(self):
        temdir = TemDir(TEMDIR)
        temdir1 = TemDir(TEMDIR1)
        temdir2 = TemDir(TEMDIR2)
        assert temdir2.parent == temdir1
        assert temdir1.parent == temdir

    @classmethod
    def teardown_class(cls):
        sh.rmtree(OUT_DIR)
