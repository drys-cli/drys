import pytest
import shutil as sh

import tem.util
from common import *
from tem.fs import TemDir
from tem.errors import NotATemDirError


# OUTDIR is defined in 'common.py'
OUTDIR = OUTDIR / "fs"
TEMDIR = OUTDIR / "temdir"
TEMDIR1 = TEMDIR / "dir1"
TEMDIR2 = TEMDIR1 / "dir2"
NOT_A_TEMDIR = OUTDIR / "not_a_temdir"


class TestTemDir:
    @classmethod
    def setup_class(cls):
        for directory in TEMDIR, TEMDIR1, TEMDIR2, NOT_A_TEMDIR:
            os.makedirs(directory)
        TemDir.init(TEMDIR)
        TemDir.init(TEMDIR1)
        TemDir.init(TEMDIR2)

    def test_constructor(self):
        temdir = TemDir(TEMDIR)
        with pytest.raises(NotATemDirError):
            temdir = TemDir(NOT_A_TEMDIR)
        with tem.util.chdir(TEMDIR):
            assert str(TemDir().absolute()) == os.path.abspath(os.getcwd())

    def test_tem_parent(self):
        temdir = TemDir(TEMDIR)
        temdir1 = TemDir(TEMDIR1)
        temdir2 = TemDir(TEMDIR2)
        assert temdir2.parent == temdir1
        assert temdir1.parent == temdir

    @classmethod
    def teardown_class(cls):
        sh.rmtree(OUTDIR)
