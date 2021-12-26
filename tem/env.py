"""Work with tem environments."""
import os

import tem
from tem import util
from tem.fs import TemDir, DotDir
from tem.errors import NotADirError


class Environment:
    """A tem environment.

    An environment consists of a list of envdirs.
    Attributes
    ----------
    current: Environment
        The currently active environment, if any.
    """
    current = None

    """An environment for a given directory."""

    def __init__(self, basedir: TemDir, recursive=True):
        basedir = TemDir(basedir)  # throws if basedir can't be cast
        #: All temdirs that take part in this environment
        self.envdirs = [basedir]

        if recursive:
            while True:
                directory = directory.tem_parent
                if not directory:
                    break
                self.envdirs.insert(0, directory)

        self._path = []

    @property
    def path(self, path):
        """Return the list of `PATH` entries injected by this environment."""
        # TODO need to think if I want to take the PATH from environ, or store
        # it somehow
        return self._path

    @path.setter
    def path(self, path):
        self._path = path
        if Environment.current == self:
            path_prepend_unique(self._path)

    def activate(self):
        Environment.current = self
        for envdir in self.envdirs:
            envdir.dot_env.exec()
        raise NotImplementedError

    def deactivate(self):
        # TODO
        Environment.current = None
        raise NotImplementedError

    @property
    def auto_update(self):
        return self._autoupdate


def path_prepend_unique(path):
    """Prepend `path` to the `PATH` envvar such that it only appears once."""
    path = os.path.realpath(path)
    path_list = [p for p in path_as_list() if os.path.realpath(p) != path]
    os.environ["PATH"] = ":".join([path, *path_list])


def path_as_list():
    """Return `PATH` envvar as a list of paths."""
    return os.environ["PATH"].split(":")
