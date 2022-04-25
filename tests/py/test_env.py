from common import *
from tem.env import ExecPath


class TestExecPath:
    """Tests for both"""

    @classmethod
    def setup_class(cls):
        cls.TESTDIR = PY_TESTDIR / "execpath"
        cls.paths = [
            cls.TESTDIR / path for path in ("path1", "path2", "path3")
        ]
        cls.ep = ExecPath(cls.paths)

    def test_slicing(self):
        assert list(self.ep[0:1]) == [str(self.paths[0])]
        assert list(self.ep[0:]) == list(map(str, self.paths))
        assert list(self.ep[2:3]) == list(map(str, self.paths[2:3]))

    def test_lookup(self):
        """Test lookup of nth"""
        common_script = self.ep["common_script"]
        assert os.path.abspath(common_script.lookup()) == os.path.abspath(
            self.TESTDIR / "path1" / "common_script"
        )
        assert os.path.abspath(common_script[1].lookup()) == os.path.abspath(
            self.TESTDIR / "path2" / "common_script"
        )
        assert os.path.abspath(common_script[2].lookup()) == os.path.abspath(
            self.TESTDIR / "path3" / "common_script"
        )

    def test_run(self, capfd):
        self.ep["script1"]()
        captured = capfd.readouterr()
        assert captured.out == "script1\n"
        assert captured.err == ""

    def test_run_with_args(self, capfd):
        # Positional args
        self.ep["script2"]("pos1", "pos2", "--test=1")
        captured = capfd.readouterr()
        assert captured.out == "script2\npos1\npos2\n--test=1\n"
        assert captured.err == ""
        # Options as kwargs
        self.ep["script3"]("pos", test="testarg", s=1, boolopt=True)
        captured = capfd.readouterr()
        assert (
            captured.out == "script3\n--test\ntestarg\n-s\n1\n--boolopt\npos\n"
        )
        assert captured.err == ""


class TestEnv:
    def test_environment(self):
        pass
