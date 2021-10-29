"""Work with tem environments."""
import os


def list_path():
    """Return the `PATH` envvar as a list of paths."""
    return os.environ["PATH"].split(":")


def path_prepend_unique(path):
    """Prepend `path` to the `PATH` envvar such that it only appears once."""
    path = os.path.realpath(path)
    path_list = [p for p in list_path() if os.path.realpath(p) != path]
    os.environ["PATH"] = ":".join([path, *path_list])
