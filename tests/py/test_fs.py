import pytest
import shutil as sh

import tem.util
from common import *
from tem.fs import TemDir
from tem.errors import NotATemDirError


# OUTDIR is defined in 'common.py'
OUTDIR = OUTDIR / "fs"
NOT_A_TEMDIR = OUTDIR / "not_a_temdir"
TEMDIR = OUTDIR / "temdir"
TEMDIR1 = TEMDIR / "dir1"
TEMDIR2 = TEMDIR1 / "dir2"
NOT_A_TEMDIR2 = TEMDIR2 / "not_a_temdir2"


class TestTemDir:
    @classmethod
    def setup_class(cls):
        for directory in TEMDIR, TEMDIR1, TEMDIR2, NOT_A_TEMDIR, NOT_A_TEMDIR2:
            os.makedirs(directory)
        TemDir.init(TEMDIR)
        assert os.path.isdir(TEMDIR / ".tem")
        TemDir.init(TEMDIR1)
        TemDir.init(TEMDIR2)

    def test_constructor(self):
        TemDir(TEMDIR)
        with pytest.raises(NotATemDirError):
            TemDir(NOT_A_TEMDIR)
        with tem.util.chdir(NOT_A_TEMDIR2):
            assert str(TemDir().absolute()) == str(TEMDIR2.absolute())

    def test_parent(self):
        temdir = TemDir(TEMDIR)
        assert temdir.parent == OUTDIR
        temdir1 = TemDir(TEMDIR1)
        assert temdir1.parent == temdir

    def test_tem_parent(self):
        temdir = TemDir(TEMDIR)
        temdir1 = TemDir(TEMDIR1)
        assert temdir1.tem_parent == temdir
        # We would just be asserting temdir.tem_parent is None, if we could
        # guarantee that the tests/ directory is not in a hierarchy that has a
        # temdir
        assert (
            temdir.tem_parent is None
            or str(temdir.tem_parent) != OUTDIR.absolute()
        )
