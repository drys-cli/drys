"""Work with tem environments."""
import os
import subprocess
from functools import cached_property
from typing import List

import tem.shell.commands as shell_commands
from tem import context, find
from tem.context import Context
from tem.fs import TemDir
from tem.shell import shell


class ExecPath(list):
    """
    Wrapper for the `PATH` environment variable with handy functionality.

    Parameters
    ----------
    source: optional, List[str | os.PathLike], str
        Represents the `PATH` environment variable, as a list of paths or a
        string of colon-separated paths. If unspecified, `os.environ["PATH"]` is
        used.
    """

    #: Special value for parameter index in method :meth:`lookup`.
    SYSTEM = type("SYSTEM", (), dict())

    def __init__(self, source=None):
        if source is None:
            source = os.environ["PATH"]

        if isinstance(source, str):
            paths = source.split(":")
        elif isinstance(source, list):
            paths = source
        else:
            raise TypeError("optional 'source' must be of type list or str")

        super().__init__(paths)

    def __str__(self):
        """Convert to string representation suitable for os.environ."""
        return ":".join([str(entry) for entry in self])

    def __repr__(self):
        return f"ExecPath({super().__repr__()})"

    def lookup(self, executable: str, index: int = None):
        """
        Lookup an executable named ``executable`` in this ExecPath.  If
        ``index`` is unspecified, returns the same path as the OS would after
        searching through the `PATH` env variable.

        Parameters
        ----------
        index
            Of all possible matches, return the one at ``index``. A negative
            value works the same as negative indexing of a python list.
        """
        pass

    def prepend(self, path):
        return ExecPath([os.path.abspath(path)] + list(self))

    def dedupe(self):
        return ExecPath(list(dict.fromkeys(self).keys()))

    def export(self):
        """
        Export to `os.environ["PATH"]`. If the current context is
        :data:`~tem.context.Context.SHELL`, the environment variable will be
        exported to the shell also.
        """
        value = str(self)
        os.environ["PATH"] = value
        if context() == Context.SHELL:
            shell_commands.export("PATH", value)


class Environment:
    """A tem environment.

    Attributes
    ----------
    """

    @property
    def envdirs(self) -> List[TemDir]:
        return self._envdirs

    @property
    def rootdir(self) -> TemDir:
        return self.envdirs[-1]

    @property
    def basedir(self) -> TemDir:
        return self.envdirs[0]

    def __init__(self, basedir: TemDir = None, recursive=True):
        basedir = TemDir(basedir)  # throws if basedir can't be cast
        #: All temdirs that take part in this environment
        if recursive:
            self._envdirs = list(find.parent_temdirs(basedir))
        else:
            self._envdirs: List[TemDir] = [basedir]

        self._path = []

    @cached_property
    def execpath(self) -> ExecPath:
        """
        Return the value that `os.environ["PATH"]` would have after exporting
        this environment.
        """
        envdirs_real = [os.path.realpath(path) for path in self.envdirs]
        execpath = [
            path
            for path in ExecPath()
            if os.path.realpath(path) not in envdirs_real
        ]
        return ExecPath(self.envdirs + execpath)

    @cached_property
    def is_exported(self) -> bool:
        """
        Test if the environment is fully exported into the `PATH` environment
        variable. This means that the envdirs must be the first entries of
        `PATH`.
        """
        for i, envdir in enumerate(self.envdirs):
            if i >= len(self.execpath) or os.path.realpath(
                envdir
            ) != os.path.realpath(self.execpath[i]):
                return False
        return True

    def export(self):
        """Export this environment to the system environment variables."""
        self.execpath.export()
        os.environ["_TEM_EXPORTED_ENVIRONMENT"] = str(self.basedir)

    def execute(self):
        """
        Execute the environment scripts, exporting the environment
        beforehand.
        """
        self.export()
        for envdir in reversed(self.envdirs):
            subdir = envdir["env"]
            for entry in os.scandir(subdir):
                if os.path.isfile(entry):
                    subprocess.run(entry)

    def __enter__(self):
        from tem import context

        self._context_reset_token = context._env.set(self)
        if not self.is_exported:
            self.export()

    def __exit__(self, _1, _2, _3):
        from tem import context

        context._env.reset(self._context_reset_token)
