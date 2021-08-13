"""Utility functions and classes"""
import configparser
import contextlib
import os
import re
import shutil
import sys


class ConfigParser(configparser.ConfigParser):
    """Custom ConfigParser."""

    def __init__(self, files=None, **kwargs):
        super().__init__(**kwargs)
        # Allow reading files on construction
        if files:
            self.read(files)

    def set(self, section, option, value=None):
        if not self.has_section(section):
            self.add_section(section)
        super().set(section, option, value=value)

    def items(
        self, section=configparser.DEFAULTSECT, raw=False, vars=None
    ):  # pylint: disable=line-too-long,redefined-builtin
        if self.has_section(section):
            return super().items(section, raw=raw, vars=vars)
        return []

    def __getitem__(self, option):
        split = option.split(".", 1)
        if len(split) == 1:
            split.insert(0, "general")
        return self.get(*split, fallback="")

    def __setitem__(self, option, value):
        split = option.split(".", 1)
        if len(split) == 1:
            split.insert(0, "general")
        section, option = tuple(split)
        self.set(section, option, value)


def print_err(*args, **kwargs):
    """Like regular print, but print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def abspath(path):
    """Get absolute path with ~ expanded."""
    return os.path.abspath(os.path.expanduser(path))


def basename(path):
    """Get basename. Paths containing ~ are valid."""
    return os.path.basename(os.path.abspath(path))


def dirname(path):
    """Get dirname. Paths containing ~ are valid."""
    return os.path.dirname(os.path.abspath(path))


def shortpath(path):
    """Get path with `$HOME` shortened to `~`."""
    # TODO make more robust
    return path.replace(os.path.expanduser("~"), "~")


def copy(src, dest="."):
    """
    Copy ``src`` to ``dest``. If ``dest`` is a directory, ``src`` will be
    placed under it.
    """
    _dirname = dirname(dest)
    if _dirname and not os.path.exists(_dirname):
        os.makedirs(_dirname, exist_ok=True)
    if os.path.isdir(src):
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


def make_file_executable(path):
    """Equivalent to performing `chmod u+x` on ``path``."""
    os.chmod(path, os.stat(path).st_mode | 0o100)


# TODO move to repo.py
def fetch_name(repo_path):
    """
    Fetch the name of the repo at ``repo_path`` from its configuration. If the
    repo has not configured a name, the name of its directory is used.
    """
    cfg = ConfigParser(repo_path + "/.tem/repo")
    name = cfg["general.name"]
    if name:
        return name
    return basename(repo_path)


def resolve_repo(repo_id, lookup_repos=None):
    """
    Resolve a repo ID (path, partial path or name) to the absolute path of a
    repo.
    """
    if not repo_id:
        return ""
    # Path is absolute or explicitly relative (starts with . or ..)
    if (
        repo_id[0] == "/"
        or repo_id in [".", ".."]
        or re.match(r"\.\.*/", repo_id)
    ):
        return repo_id

    # Otherwise try to find a repo whose name is `repo_id`
    if not lookup_repos:
        from . import cli

        lookup_repos = cli.repo_path

    for repo in lookup_repos:
        if os.path.exists(repo) and fetch_name(repo) == repo_id:
            return abspath(repo)

    # If all else fails, try to find a repo whose basename is equal to `path`
    for repo in lookup_repos:
        if basename(repo) == repo_id:
            return repo

    # The `path` must be relative/absolute then
    return os.path.expanduser(repo_id)


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
