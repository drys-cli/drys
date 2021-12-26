"""The standard tem filesystem."""

import os
import glob
import pathlib
from subprocess import run
import tem
from tem import __prefix__, util
from tem.errors import NotADirError, NotATemDirError, FileNotFoundError, TemInitializedError


class TemDir(type(pathlib.Path())):
    """A directory that supports tem features.

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

    def __init__(self, path: os.PathLike):
        if not os.path.exists(os.path.join(path, ".tem")):
            raise NotATemDirError(path)

        super().__init__()
        self.isolated = False
        self.autoenv = False

    @property
    def name(self):
        """The name of this temdir, taken from `.tem/config`.

        This is used to identify this dir in a hierarchy of multiple temdirs.
        """
        raise NotImplementedError

    @property
    def dot_path(self):
        return DotDir(os.path.join(self, ".tem/path"))

    @property
    def dot_env(self):
        return DotDir(os.path.join(self, ".tem/env"))

    @property
    def dot_hooks(self):
        return DotDir(os.path.join(self, ".tem/hooks"))

    @property
    def tem_parent(self):
        """Get the first parent of this temdir that is also a temdir."""
        # Traverse the fs tree upwards until a parent temdir is found
        directory = self
        while str(directory) != "/":
            try:
                directory = TemDir(directory.parent)
            except NotATemDirError:
                continue
        return None

    @staticmethod
    def init(path: os.PathLike, force: bool=False):
        """Initialize a temdir at ``path``.
        Parameters
        ----------
        force: bool
            Re-initialize temdir from scratch.
        Returns
        -------
        temdir: TemDir
            Return the new temdir at ``path``.
        """
        path = pathlib.Path(path)
        dot_tem = path / ".tem"
        # If temdir already exists, act according to the value of ``force``
        try:
            temdir = TemDir(path)
            # At this point, we know that .tem/ exists
            if force:
                os.remove(dot_tem)
            else:
                raise TemInitializedError(path)
            return temdir
        except NotATemDirError:
            pass

        # Create directories
        os.makedirs(dot_tem, exist_ok=True)
        os.makedirs(dot_tem / "path", exist_ok=True)
        os.makedirs(dot_tem / "hooks", exist_ok=True)
        os.makedirs(dot_tem / "env", exist_ok=True)
        shell = tem.shell()
        if shell:
            os.makedirs(dot_tem / f"{shell}-env", exist_ok=True)
            os.makedirs(dot_tem / f"{shell}-hooks", exist_ok=True)

        share_dir = pathlib.Path(__prefix__ + "/share/tem")

        # Copy system default files to .tem/
        files = [share_dir / file for file in ["config", "ignore"]]
        for i, file in enumerate(files):
            dest = util.copy(file, ".tem" / file.relative_to(share_dir))
            files[i] = dest

        return TemDir(path)


class DotDir:

    def __init__(self, path: os.PathLike):
        self.path = path

    def exec(self, files: list[os.PathLike] = ["."], ignore_nonexistent=False):
        """Execute the given file(s) as programs.

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

        for file in files:
            if not os.path.exists(file):
                if not ignore_nonexistent:
                    raise FileNotFoundError(file)
            elif os.path.isdir(file):
                DotDir.exec([file], ignore_nonexistent=ignore_nonexistent)
            else:
                run(file)

    def executables(self):
        """Recursively iterate over all executable files in this dotdir."""
        return (file for file in glob.iglob("**/*", recursive=True)
                if os.path.isfile(file) and os.access(file, os.X_OK))


class Environment:
    class Path(list[str]):
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
    """An abstraction for executables and shell (incl. python) scripts."""

    def __init__(self, path):
        super().__init__(path)

    def brief(self):
        """Extract the brief comment from the runnable."""
