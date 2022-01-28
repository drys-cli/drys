"""Find various tem-related stuff."""
import os

from tem import env


def _default_cwd(func):
    """
    Decorator that populates ``func``'s ``path`` argument with ``os.getcwd()``
    if the caller left it empty.
    """

    def wrapper(path=None):
        if path is None:
            path = os.getcwd()
        return func(path=path)

    return wrapper


def parents_with_subdir(path: os.PathLike, subdir: str):
    """
    Return parent directories of ``path`` that contain a subdirectory tree as in
    ``subdir``, as absolute paths, from leaf to root.
    """

    path = os.path.realpath(path)
    result_paths = []

    while True:
        if os.path.isdir(path + "/" + subdir):
            result_paths.append(path)
        path = os.path.dirname(path)
        if path == "/":
            break

    return result_paths


def parents_with_dotdir(path: os.PathLike, dotdir: str):
    """
    Return parent directories of ``path`` that contain dotdir ``dotdir``.
    """
    return parents_with_subdir(f".tem/{dotdir}")


@_default_cwd
def parent_temdirs(path: os.PathLike = None):
    """
    Return temdirs that are parents of the directory at ``path``, from leaf to
    root, as absolute paths.
    """

    return parents_with_subdir(path, ".tem")


@_default_cwd
def basedir(path: os.PathLike = None):
    """Return the base temdir in the hierarchy that ``path`` belongs to."""
    return parent_temdirs(path)[0]


@_default_cwd
def rootdir(path: os.PathLike = None):
    """Return the root temdir in the hierarchy that ``path`` belongs to."""
    return parent_temdirs(path)[0]


def base_envdir():
    """Return the base envdir in the hierarchy that ``path`` belongs to."""
    return env.current()


def root_envdir():
    """Return the root envdir in the hierarchy that ``path`` belongs to."""
    return env.current().rootdir
