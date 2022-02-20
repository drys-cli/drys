"""Find various tem-related stuff."""
import functools
import os
from typing import Iterator

from tem import fs
from tem.errors import NotATemDirError
from tem.fs import TemDir


def _default_cwd(func):
    """
    Decorator that populates ``func``'s ``path`` argument with ``os.getcwd()``
    if the caller left it empty.
    """

    @functools.wraps(func)
    def wrapper(path=None):
        return func(path=path or os.getcwd())

    return wrapper


def parents_with_subdir(path, subdir: str):
    """
    Iterate over the directory hierarchy from ``path`` upwards, including only
    directories  that contain a subdirectory tree as in ``subdir``. Output paths
    are absolute.
    """
    return (p for p in fs.iterate_hierarchy(path) if os.path.isdir(p / subdir))


def parents_with_dotdir(path, dotdir: str):
    """
    Iterate over parent directories of ``path`` that contain ``dotdir``.
    """
    return parents_with_subdir(path, f".tem/{dotdir}")


@_default_cwd
def parent_temdirs(path=None) -> Iterator[TemDir]:
    """
    Return temdirs that are parents of the directory at ``path``, from leaf to
    root, as absolute paths. ``path`` is included in the output.
    """

    for directory in fs.iterate_hierarchy(path):
        try:
            yield TemDir(directory)
        except NotATemDirError:
            continue


@_default_cwd
def basedir(path: os.PathLike = None):
    """Return the base temdir in the hierarchy that ``path`` belongs to."""
    return next(parent_temdirs(path))


@_default_cwd
def rootdir(path=None):
    """Return the root temdir in the hierarchy that ``path`` belongs to."""
    return next(parent_temdirs(path))
