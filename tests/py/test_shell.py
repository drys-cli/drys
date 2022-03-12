import tempfile

from tem.shell import commands
from common import *


class TestShell:
    file = None

    @classmethod
    def setup_class(cls):
        cls.write_file = tempfile.NamedTemporaryFile(mode="a", suffix=".sh")
        cls.path = cls.write_file.name
        cls.read_file = open(cls.path)
        os.environ["__TEM_SHELL_SOURCE"] = cls.path

    def test_export(self):
        commands.export("TEST", "value")
        assert self.read_file.read().strip() == "export TEST=value"

    @classmethod
    def teardown_class(cls):
        cls.read_file.close()
        cls.write_file.close()
