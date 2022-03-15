"""Work with tem environments."""
import os

from tem import find, context
from tem.context import Context
from tem.fs import TemDir


class ExecPath(list):
    """
    Wrapper for the `PATH` environment variable with handy functionality.

    Parameters
    ----------
    source: optional, List[str], str
        Represents the `PATH` environment variable, as a list of paths or a
        string of colon-separated paths. If unspecified, `os.environ["PATH"]` is
        used.
    """
    #: Special value for parameter index in method :meth:`lookup`.
    SYSTEM = type("_", (), dict())

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
        return ":".join(self)

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
            from tem.shell.commands import export
            export("PATH", value)


class Environment:
    """A tem environment.

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
    def execpath(self) -> ExecPath:
        """Return the list of `PATH` entries injected by this environment."""
        # TODO need to think if I want to take the PATH from environ, or store
        # it somehow
        return self._path

    @execpath.setter
    def execpath(self, path):
        self._path = path
        # TODO

    def __enter__(self):
        from tem import context
        self._context_reset_token = context._env.set(self)

    def __exit__(self, _1, _2, _3):
        from tem import context
        context._env.reset(self._context_reset_token)

