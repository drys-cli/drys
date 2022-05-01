import os
from pathlib import Path
from typing import Union

__all__ = ("AnyPath", "create_file")

from tem import errors

AnyPath = Union[str, Path, os.PathLike]


def create_file(path: AnyPath, permissions=0o644, force=False) -> type(open):
    """
    Create a file at ``path`` and open it in write mode if it doesn't exist.

    This automatically creates the necessary directory structure.

    Parameters
    ----------
    path
        The path of the new file.
    permissions
        Permissions of the file in UNIX format.
    force
        Do not fail if the file exists.

    Raises
    ------
    tem.errors.FileExistsError
        If the file exists.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and not force:
        raise errors.FileExistsError(path)
    handle = open(path, "w", encoding="utf-8")
    os.chmod(path, permissions)

    return handle
