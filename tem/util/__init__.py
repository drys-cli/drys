"""Utility functions and classes"""
import contextlib
import importlib
import os
import pathlib
import re
import shutil
import sys
import types

import tem


def print_err(*args, **kwargs):
    """Like regular print, but print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def abspath(path):
    """Get absolute path with `~` expanded."""
    return os.path.abspath(os.path.expanduser(path))


def basename(path):
    """Get basename. Paths containing `~` are valid."""
    return os.path.basename(os.path.abspath(path))


def dirname(path):
    """Get dirname. Paths containing `~` are valid."""
    return os.path.dirname(os.path.abspath(path))


def shortpath(path):
    """Get path with `$HOME` shortened to `~`."""
    return re.sub("^" + re.escape(os.path.expanduser("~")), "~", path)


# TODO try to remember where I wanted to use this?
def explicit_path(path):
    """
    If the path is relative, prepend `./`. If the path is a directory, append a
    `/`. In all other cases `path` is returned unmodified
    """
    if (
        path
        and path != "."
        and path[0] != "/"
        and path[0] != "~"
        and (path[0] != "." or path[1] != "/")
    ):
        path = "./" + path
    if os.path.isdir(path):
        # Append a '/' if it's not there already
        return re.sub(r"([^/])$", r"\1/", path)
    return path


def copy(src, dest=".", symlink=False):
    """
    Copy ``src`` to ``dest``. If ``dest`` is a directory, ``src`` will be
    placed under it. Create a symlink if ``symlink`` is True.
    """
    # TODO add `force` argument

    if dest == sys.stdout:
        return cat(src)

    _dirname = dirname(dest)
    if _dirname and not os.path.exists(_dirname):
        os.makedirs(_dirname, exist_ok=True)

    if symlink:
        try:
            os.symlink(src, dest)
            return dest
        except OSError:
            return ""
    elif os.path.isdir(src):
        return shutil.copytree(
            src, dest, dirs_exist_ok=True, copy_function=shutil.copy
        )

    return shutil.copy(src, dest)


def move(src, dest):
    """
    Same as :func:`.copy`, but move the file instead.
    """
    return shutil.move(src, dest)


def remove(path):
    """Remove ``path``. Directories are treated as files."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def cat(file):
    """Same as coreutils `cat` program."""
    with open(file, "r", encoding="utf-8") as f:
        print(f.read(), sep="\n")


def make_file_executable(path):
    """Equivalent to performing `chmod u+x` on ``path``."""
    os.chmod(path, os.stat(path).st_mode | 0o100)


@contextlib.contextmanager
def chdir(new_dir):
    """
    This context manager allows you cd to `new_dir`, do stuff, then cd back.
    """
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


def unique(iterable):
    """Remove duplicates from `iterable`."""
    return type(iterable)(x for x in dict.fromkeys(iterable))


def import_path(
    module_name: str, path: pathlib.Path, add_to_sys=False
) -> types.ModuleType:
    """Import a python file from ``path``."""
    if not os.path.exists(path):
        raise FileNotFoundError
    if os.path.isdir(path):
        raise NotImplementedError

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if add_to_sys:
        sys.modules[module_name] = module
    return module


def raise_or_warn(exception: Exception):
    """
    Raise ``exception`` or print an ``exception``-derived CLI warning if
    :func:`tem.cli.context.as_warning` is set for the given exception, in the
    current context.
    """
    if tem.context() in (tem.Context.CLI, tem.Context.SHELL):
        from tem.cli.context import as_warnings
        from tem.cli import common as cli

        if as_warnings([exception]):
            cli.print_exception_message(exception)
    else:
        raise exception
