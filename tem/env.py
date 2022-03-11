"""Work with tem environments."""
import contextvars
import os

import tem
from tem import find, fs, util
from tem.errors import NotADirError
from tem.fs import DotDir, TemDir


class Environment:
    """A tem environment.

    An environment consists of a list of envdirs.
    Attributes
    ----------
    """

    # Simple properties
    envdirs = property(lambda self: self._envdirs)
    rootdir = property(lambda self: self.envdirs[-1])
    basedir = property(lambda self: self.envdirs[0])

    def __init__(self, basedir: TemDir = None, recursive=True):
        basedir = TemDir(basedir)  # throws if basedir can't be cast
        #: All temdirs that take part in this environment
        if recursive:
            self._envdirs = list(find.parent_temdirs(basedir))
        else:
            self._envdirs = [basedir]

        self._path = []

    @property
    def execpath(self):
        """Return the list of `PATH` entries injected by this environment."""
        # TODO need to think if I want to take the PATH from environ, or store
        # it somehow
        return self._path

    @execpath.setter
    def execpath(self, path):
        self._path = path
        if _current.get() == self:
            path_prepend_unique(self._path)

    def __enter__(self):
        self._env_restore_token = _current.set(self)

    def __exit__(self, _1, _2, _3):
        _current.reset(self._env_restore_token)


_current = contextvars.ContextVar[Environment](
    "__tem_current_env", default=None
)


def current() -> Environment:
    """Get the currently active application-wide environment."""
    global _current
    return _current.get()


def path_prepend_unique(path):
    """Prepend `path` to the `PATH` envvar such that it only appears once."""
    path = os.path.realpath(path)
    path_list = [p for p in path_as_list() if os.path.realpath(p) != path]
    os.environ["PATH"] = ":".join([path, *path_list])


def path_as_list():
    """Return `PATH` envvar as a list of paths."""
    return os.environ["PATH"].split(":")
