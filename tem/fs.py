"""The standard tem filesystem."""
import glob
import os
import pathlib
import subprocess
from contextlib import suppress
from functools import cached_property
from typing import Iterable, Literal, Optional, Union

import tem.util.fs
from tem import __prefix__, __version__, errors, util
from tem.errors import FileNotFoundError as FileNotFoundError_
from tem.errors import (
    NotATemDirError,
    NoTemDirInHierarchy,
    TemInitializedError,
)
from tem.shell import shell

__all__ = (
    "AnyPath",
    "TemDir",
    "DotDir",
    "Runnable",
    "Executable",
    "iterate_hierarchy",
)


AnyPath = tem.util.fs.AnyPath
SystemPath = type(pathlib.Path())


class TemDir(SystemPath):
    """
    A directory that supports tem features. Supports all ``pathlib.Path``
    features.

    Always contains a `.tem/` subdirectory.

    Attributes
    ----------
    path: AnyPath
        Path to this temdir.
    isolated : bool
        If True, the environment can be activated only if this directory is the
        current working directory.
    autoenv : bool
        Automatically activate the environment when `cd`-ing to this directory.
        This variable exists only if a tem shell plugin is active.
    """

    path: AnyPath

    # pylint: disable-next=arguments-differ
    def __new__(cls, path: AnyPath = None):
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

    def __getitem__(
        self, dotdir: Literal["path", "env", "hooks", "files", "tmp"]
    ) -> "DotDir":
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
    def parent(self) -> Union[pathlib.Path, "TemDir"]:
        """
        Parent directory.

        If the parent is a valid temdir, the returned path will be an instance
        of :class:`TemDir`.
        """
        parent = pathlib.Path(super().parent)
        try:
            return TemDir(parent)
        except NotATemDirError:
            return parent

    @property
    def tem_parent(self) -> Optional["TemDir"]:
        """Get the first parent directory that is also a temdir."""
        # Traverse the fs tree upwards until a parent temdir is found
        directory = self.parent
        while str(directory) != "/":
            try:
                return TemDir(directory)
            except NotATemDirError:
                directory = directory.parent
        return None

    @staticmethod
    def init(path: AnyPath, force: bool = False):
        """Initialize a temdir at ``path``.

        Parameters
        ----------
        path
            Path to initialize at.
        force
            Re-initialize temdir from scratch.
        Returns
        -------
        temdir: TemDir
            The newly initialized temdir at ``path``.
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


class DotDir(SystemPath):
    """Represents a directory under `.tem/`."""

    # pylint: disable-next=arguments-differ
    def __new__(cls, path: AnyPath):
        return super(DotDir, cls).__new__(cls, str(path))

    def __init__(self, *_):
        super().__init__()
        if not self.exists():
            raise errors.FileNotFoundError(self.absolute())
        if not self.is_dir():
            raise errors.FileNotDirError(self.absolute())
        if os.path.basename(self.parent) != ".tem":
            raise errors.NotADotDirError(self.absolute())

    def exec(self, files: Iterable = tuple("."), ignore_nonexistent=False):
        """
        Execute the given file(s) as programs. Relative paths are relative to
        the dotdir.

        ``files`` can also contain directories. Each file in those directories
        will be executed, recursively. If ``ignore_nonexistent`` is ``True``,
        no exception is raised by nonexistent files.

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
        ``exec(['program1', 'dir/subdir'])`` will run `program3` and
        `program4`.
        """
        files = sorted(files)
        with util.chdir(self):
            for file in files:
                if not os.path.exists(file):
                    if not ignore_nonexistent:
                        raise FileNotFoundError_(file)
                elif os.path.isdir(directory := file):
                    for _file in os.scandir(directory):
                        if os.path.isfile(_file):
                            subprocess.run(_file, check=False)
                        elif os.path.isdir(_file):
                            DotDir(directory).exec(
                                ignore_nonexistent=ignore_nonexistent
                            )
                else:
                    subprocess.run(file, check=False)

    def executables(self):  # pylint: disable=no-self-use
        """Recursively iterate over all executable files in this dotdir."""
        return (
            file
            for file in glob.iglob(str(self / "**/*"), recursive=True)
            if os.path.isfile(file) and os.access(file, os.X_OK)
        )

    def __iter__(self):
        return os.scandir(self)


class Runnable(SystemPath):
    """An abstraction for executables and shell (including python) scripts."""

    # pylint: disable-next=arguments-differ
    def __new__(cls, path: AnyPath):
        return super(Runnable, cls).__new__(cls, str(path))

    def __init__(self, *_):
        super().__init__()

    def brief(self):
        """Extract the brief comment from the runnable."""
        _ = self  # prevents warning
        return NotImplemented


class Executable(Runnable):
    """An executable file."""

    def __init__(self, path: AnyPath):
        if not pathlib.Path(path).exists():
            raise errors.FileNotFoundError(path.absolute())
        if not util.is_executable(path):
            raise PermissionError(f"File '{path}' must be executable")
        super().__init__(path)


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
