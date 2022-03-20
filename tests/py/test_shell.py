import tempfile

import pytest

from tem.shell import commands
from common import *


class TestShell:
    file = None

    @pytest.fixture(autouse=True)
    def clear_source_file(self):
        self.write_file = tempfile.NamedTemporaryFile(mode="a", suffix=".sh")
        self.path = self.write_file.name
        self.read_file = open(self.path)
        os.environ["__TEM_SHELL_SOURCE"] = self.path
        yield

    def test_export(self):
        commands.export("TEST", "value")
        assert self.read() == "export TEST=value"

    def test_command(self):
        commands.command("spaced command", "--option", "arg$")
        assert self.read() == "'spaced command' --option 'arg$'"

    def read(self):
        """Read the source file."""
        return self.read_file.read().strip()
