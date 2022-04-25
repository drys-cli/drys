"""Work with tem environments."""
import os
import pathlib
import subprocess
import weakref
from functools import cached_property
from itertools import islice
from typing import Iterator, List, Literal, Type, Union, overload

import tem.shell.commands as shell_commands
from tem import context, find
from tem.context import Runtime
from tem.fs import AnyPath, TemDir

__all__ = ["Environment", "ExecPath", "ExecutableLookup"]


class Environment:
    """A tem environment.

    Parameters
    ----------
    basedir
        Base tem directory for the environment.
    recursive
        Determines if all parent temdirs should partake in the environment.
    """

    def __init__(self, basedir: TemDir = None, recursive: bool = True):
        basedir = TemDir(basedir)  # throws if basedir can't be cast
        #: All temdirs that take part in this environment
        if recursive:
            self._envdirs = list(find.parent_temdirs(basedir))
        else:
            self._envdirs: List[TemDir] = [basedir]

        self._path = []

    @property
    def envdirs(self) -> List[TemDir]:
        """
        All :class:`TemDir<tem.fs.TemDir>`\\s participating in this environment.

        The directories are sorted from :attr:`basedir` to :attr:`rootdir`.
        """
        return self._envdirs

    @property
    def rootdir(self) -> TemDir:
        """
        Of all :attr:`envdirs`, this is the topmost one in the filesystem
        hierarchy.

        Example
        -------
        If ``self.envdirs == ["/a", "/a/b", "/a/b/c"]``, then
        ``self.rootdir == "/a"``.
        """
        return self.envdirs[-1]

    @property
    def basedir(self) -> TemDir:
        """
        Of all :attr:`envdirs`, this is the lowest in the filesystem
        hierarchy.

        Example
        -------
        If ``self.envdirs == ["/a", "/a/b", "/a/b/c"]``, then
        ``self.basedir == "/a/b/c"``.
        """
        return self.envdirs[0]

    @cached_property
    def execpath(self) -> "ExecPath":
        """
        Return a convenient wrapper around the value that ``os.environ["PATH"]``
        would have after exporting this environment.
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
        """Export this environment to ``os.environ["PATH"]``."""
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


class ExecPath(list):
    """
    Wrapper for the `PATH` environment variable with handy functionality.

    Parameters
    ----------
    source: str, List[AnyPath], ExecPath
        Represents the `PATH` environment variable, as a list of paths or a
        string of colon-separated paths. If unspecified, ``os.environ["PATH"]``
        is used.
    auto_export
        Automatically export any changes to ``os.environ["PATH"]``.

    Indexing and lookup
    -------------------
    Assume that we have ``ep = ExecPath()``. This will initialize an ExecPath
    object based on the current value of ``os.environ["PATH"]``.
    An executable with a specific file name can be looked up using
    ``ep["executable_name"]``. This will return an :class:`ExecutableLookup`
    object that can be called.

    """

    #: Special index value indicating that `PATH` entries injected by tem should
    #: be ignored when looking up executables.
    NO_TEM = type("NO_TEM", (), dict())

    def __init__(
        self,
        source: Union[str, List[AnyPath], "ExecPath"] = None,
        auto_export=True,
    ):
        if isinstance(source, str):
            super().__init__(self._abspaths(source.split(os.pathsep)))
        elif isinstance(source, list):
            super().__init__(self._abspaths(source))
        elif isinstance(source, ExecPath):
            super().__init__(self._abspaths(source))
        elif source is None:
            super().__init__(
                self._abspaths(os.environ.get("PATH", "").split(os.pathsep))
            )
        else:
            raise TypeError(
                "parameter 'source' must be an instance of str, list or ExecPath"
            )

        self.auto_export = auto_export

    @overload
    def __getitem__(self, item: str) -> "ExecutableLookup":
        ...

    @overload
    def __getitem__(self, item: slice) -> "ExecPath":
        ...

    @overload
    def __getitem__(self, item: int) -> pathlib.Path:
        ...

    def __getitem__(
        self, item: Union[str, int, slice]
    ) -> Union["ExecPath", "ExecutableLookup", pathlib.Path, Type[NO_TEM]]:
        if isinstance(item, slice):
            return ExecPath(
                super().__getitem__(item), auto_export=self.auto_export
            )
        elif isinstance(item, int):
            return super().__getitem__(item)
        elif isinstance(item, str):
            return ExecutableLookup(self, item)
        else:
            raise TypeError("index has invalid type")

    def __setitem__(self, key: Union[int, slice], value: AnyPath):
        super().__setitem__(key, value)
        if self.auto_export:
            os.environ["PATH"] = str(self)

    def __delitem__(self, key: Union[int, slice]):
        super().__delitem__(key)
        if self.auto_export:
            os.environ["PATH"] = str(self)

    def __iter__(self) -> Iterator[str]:
        return super().__iter__()

    def __str__(self):
        """Convert to string representation suitable for os.environ."""
        return ":".join([str(entry) for entry in self])

    def __repr__(self):
        return f"ExecPath({super().__repr__()})"

    def prepend(self, path):
        return ExecPath([os.path.abspath(path)] + list(self))

    def dedupe(self):
        return ExecPath(list(dict.fromkeys(self).keys()))

    def export(self):
        """
        Export to ``os.environ["PATH"]``. If the current context is
        :data:`~tem.context.Runtime.SHELL`, the environment variable will be
        exported to the shell also.
        """
        value = str(self)
        os.environ["PATH"] = value
        if context.runtime == Runtime.SHELL:
            shell_commands.export("PATH", value)

    @staticmethod
    def _abspaths(paths: List[AnyPath]):
        return [os.path.abspath(path) for path in paths]


class ExecutableLookup:
    """
    Lookup for an executable with a specified name.

    You should avoid constructing instances of this class directly. Instead, you
    can obtain an instance as ``ExecPath(...)["<executable_name>"]``.

    Parameters
    ----------
    execpath
        ExecPath to perform lookup in.
    executable_name
        The name of the executable to find.
    """

    def __init__(self, execpath: Union[ExecPath, list], executable_name: str):
        self._execpath = execpath
        self.executable_name = executable_name
        self._index = 0

    def __getitem__(self, index: int) -> "ExecutableLookup":
        """
        Return a modified lookup that finds the ``index``-th executable instead
        of the first one in the :class:`ExecPath`.

        Example
        -------
        Assuming that `/a` and `/c` contain an executable named `script` and
        `/b` doesn't, then:

        >>> el = ExecutableLookup(["/a", "/b", "/c"], "script")
        >>> print(el[0].lookup())
        /a/script
        >>> print(el[1].lookup())
        /c/script
        """
        new_spec = ExecutableLookup(self._execpath, self.executable_name)
        new_spec._index = index
        return new_spec

    def __call__(self, *args, **kwargs):
        """
        Execute the found executable, passing ``args`` as positional arguments
        and ``kwargs`` as CLI options.

        The ``kwargs`` are passed to the command as options in the following
        way:

        - If the kwarg name consists of one character, it will be prepended
          with a single hyphen.

          *Example*: ``s=1`` is passed as ``["-s", "1"]``

        - If the kwarg name consists of multiple characters, it will be
          prepended with two hyphens.

          *Example*: ``long=2`` is passed as ``["--long", "2"]``.

        - A bool kwarg that is ``True`` is specified without an argument.

          *Example*: ``flag=True`` is passed as ``["--flag"]``.

        - A bool kwarg that is ``False`` is not passed to the command at all.

        - Underscores in the argument name will be converted to hyphens.

          *Example*: ``no_print=True`` is passed as ``["--no-print"]``

        Notes
        -----
        Options are always placed before the positional arguments when executing
        the command.

        Example
        -------
        >>> executable_lookup = ExecPath()["git"]
        >>> print(type(executable_lookup))
        ExecutableLookup
        >>> executable_lookup("commit", m="Initial commit", amend=True)
        # Will call subprocess.run(["git", "commit", "-m", "Initial commit", "--amend"])
        """
        arguments = [self.lookup()]
        for k, v in kwargs.items():
            if not isinstance(v, bool) or v:
                if len(k) == 1:
                    arguments.append(f"-{k}")
                else:
                    arguments.append(f"--{k.replace('_', '-')}")

            if not isinstance(v, bool):
                arguments.append(str(v))

        arguments += list(map(str, args))
        return subprocess.run(arguments, check=False)

    def lookup(self) -> str:
        """
        Lookup the executable that would be executed by ``__call__``, and
        return its path.
        """
        try:
            return next(
                islice(
                    (
                        exe_path
                        for path in self._execpath
                        if os.path.exists(
                            exe_path := os.path.join(
                                path, self.executable_name
                            )
                        )
                        and os.access(exe_path, os.X_OK)
                    ),
                    self._index,
                    None,
                )
            )
        except StopIteration:
            raise LookupError(self.executable_name)
