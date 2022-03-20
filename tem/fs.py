"""The standard tem filesystem."""
import glob
import os
import pathlib
import subprocess
from contextlib import suppress
from functools import cached_property
from subprocess import run
from typing import List

from tem import util
from tem.errors import (
    FileNotFoundError,
    NotATemDirError,
    NoTemDirInHierarchy,
    TemInitializedError,
)
from tem.shell import shell


class TemDir(type(pathlib.Path())):
    """
    A directory that supports tem features. Supports all ``pathlib.Path``
    features.

    Always contains a `.tem/` subdirectory.

    Attributes
    ----------
    path : os.PathLike
        Path to this temdir.
    isolated : bool
        If True, the environment can be activated only if this directory is the
        current working directory.
    autoenv : bool
        Automatically activate the environment when `cd`-ing to this directory.
        This variable exists only if a tem shell plugin is active.
    """

    def __new__(cls, path=None):
        if not path:
            # Use first parent directory that contains '.tem'
            path = next(
                (
                    p
                    for p in iterate_hierarchy(".")
                    if os.path.isdir(p / ".tem")
                ),
                None,
            )
            if not path:
                raise NoTemDirInHierarchy(os.getcwd())
        path = os.path.abspath(path)
        if not os.path.exists(os.path.join(path, ".tem")):
            raise NotATemDirError(path)
        return super(TemDir, cls).__new__(cls, path)

    def __init__(self, *_):
        super().__init__()
        self.isolated = False
        self.autoenv = False

    def __getitem__(self, dotdir: str) -> "DotDir":
        return DotDir(self / f".tem/{dotdir}")

    @property
    def name(self):
        """The name of this temdir, taken from `.tem/config`.

        This is used to identify this dir in a hierarchy of multiple temdirs.
        """
        raise NotImplementedError

    @cached_property
    def vars(self):
        """Get a module object containing defined variables for this temdir."""
        raise NotImplementedError

    @property
    def parent(self):
        """Parent directory. An instance of ``pathlib.Path``."""
        parent = pathlib.Path(super().parent)
        try:
            return TemDir(parent)
        except NotATemDirError:
            return parent

    @property
    def tem_parent(self):
        """Get the first parent of this temdir that is also a temdir."""
        # Traverse the fs tree upwards until a parent temdir is found
        directory = self.parent
        while str(directory) != "/":
            try:
                return TemDir(directory)
            except NotATemDirError:
                directory = directory.parent
                continue
        return None

    @staticmethod
    def init(path: os.PathLike, force: bool = False):
        """Initialize a temdir at ``path``.

        Parameters
        ----------
        path
            Path to initialize at.
        force:
            Re-initialize temdir from scratch.
        Returns
        -------
        temdir: TemDir
            Return the new temdir at ``path``.
        """
        path = pathlib.Path(path)
        dot_tem = path / ".tem"
        # If temdir already exists, act according to the value of ``force``
        with suppress(NotATemDirError):
            temdir = TemDir(path)
            # At this point, we know that .tem/ exists
            if force:
                os.remove(dot_tem)
            else:
                raise TemInitializedError(path)
            return temdir

        # Create directories
        os.makedirs(dot_tem, exist_ok=True)
        os.makedirs(dot_tem / "path", exist_ok=True)
        os.makedirs(dot_tem / "hooks", exist_ok=True)
        os.makedirs(dot_tem / "env", exist_ok=True)
        if sh := shell():
            os.makedirs(dot_tem / f"{sh}-env", exist_ok=True)
            os.makedirs(dot_tem / f"{sh}-hooks", exist_ok=True)

        from tem import __prefix__, __version__

        share_dir = (
            pathlib.Path(__prefix__ + "/share/tem")
            if __version__ not in ("develop", "0.0.0")
            else pathlib.Path(os.environ.get("TEM_PROJECTROOT")) / "share"
        )

        # Copy system default files to .tem/
        files = [share_dir / file for file in ["config", "ignore"]]
        for i, file in enumerate(files):
            dest = util.copy(file, dot_tem / file.relative_to(share_dir))
            files[i] = dest

        return TemDir(path)

    @property
    def _internal(self):
        """
        Get the `.tem/.internal` directory for this temdir. Will be
        automatically created if necessary.
        """
        path = self / ".tem/.internal"
        os.makedirs(path, exist_ok=True)
        return path

    def __enter__(self):
        import tem

        self._context_reset_token = tem.context._temdir.set(self)

    def __exit__(self, _1, _2, _3):
        from tem import context

        context._temdir.reset(self._context_reset_token)


class DotDir(type(pathlib.Path())):
    def __new__(cls, path: os.PathLike):
        return super(DotDir, cls).__new__(cls, str(path))

    def __init__(self, *_):
        super().__init__()

    def exec(self, files: List = ["."], ignore_nonexistent=False):
        """
        Execute the given file(s) as programs. Relative paths are relative to
        the dotdir.

        ``files`` can also contain directories. Each file in those directories
        will be executed, recursively. If ``ignore_nonexistent`` is ``True``, no
        exception is raised by nonexistent files.

        Examples
        --------
        Assume the following directory structure:
            .
            ├── program1
            └── dir/
                ├── program2
                └── subdir/
                    ├── program3
                    └── program4
        ``exec()`` will run all programs recursively.
        ``exec(['program1'])`` or `exec(['program1'])` will run 'program1'.
        ``exec(['dir'])`` will run programs 2 through 4.
        ``exec(['dir/subdir'])`` will run `program3` and `program4`.
        ``exec(['program1', 'dir/subdir'])`` will run `program3` and `program4`.
        """
        files = sorted(files)
        with util.chdir(self):
            for file in files:
                if not os.path.exists(file):
                    if not ignore_nonexistent:
                        raise FileNotFoundError(file)
                elif os.path.isdir(directory := file):
                    for _file in os.scandir(directory):
                        if os.path.isfile(_file):
                            subprocess.run(_file)
                        elif os.path.isdir(_file):
                            DotDir(directory).exec(
                                ignore_nonexistent=ignore_nonexistent
                            )
                else:
                    run(file)

    def executables(self):
        """Recursively iterate over all executable files in this dotdir."""
        return (
            file
            for file in glob.iglob("**/*", recursive=True)
            if os.path.isfile(file) and os.access(file, os.X_OK)
        )


class Environment:
    class Path(List[str]):
        """A convenient abstraction of the PATH environment variable."""

        _path = os.environ.get("PATH", "")

        @staticmethod
        def apply():
            """Apply changes to the PATH environment variable."""
            raise NotImplementedError  # TODO

    @property
    def path(self) -> Path:
        raise NotImplementedError


class Runnable(type(pathlib.Path())):
    """An abstraction for executables and shell (including python) scripts."""

    def __init__(self, path):
        if not util.is_executable(path):
            raise
        super().__init__(path)

    def brief(self):
        """Extract the brief comment from the runnable."""
        raise NotImplementedError


def iterate_hierarchy(path):
    """
    Iterate directory hierarchy upwards from ``path``.
    Output paths are absolute.
    """
    path = os.path.abspath(path)

    yield pathlib.Path(path)

    while True:
        path = os.path.dirname(path)
        yield pathlib.Path(path)
        if path == "/":
            break
