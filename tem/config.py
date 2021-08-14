"""Configuration utilities"""
import configparser
import os

from . import __prefix__, repo


class Parser(configparser.ConfigParser):  # pylint: disable=too-many-ancestors
    """Custom ConfigParser"""

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


cfg = Parser()

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME")
TEM_CONFIG = os.environ.get("TEM_CONFIG")


SYSTEM_PATHS = [__prefix__ + "/share/tem/config"]

"""
All possible user configuration files sorted in the order they should be read.
"""
USER_PATHS = [
    os.path.expanduser("~/.config/tem/config"),
    os.path.expanduser("~/.temconfig"),
    XDG_CONFIG_HOME + "/tem/config" if XDG_CONFIG_HOME else "",
    TEM_CONFIG if TEM_CONFIG else "",
]


def user_default_path():
    """
    Of all the possible paths for the user configuration, return the one with
    the highest priority.

    .. seealso:: :data:`USER_PATHS`
    """
    lst = [USER_PATHS[i] for i in [3, 2, 0, 1]]
    return next(path for path in lst if path)


def repo_path_from_config(config):
    """Get `REPO_PATH` from the loaded configuration."""
    if not config:
        return []
    return [
        os.path.expanduser(repo)
        for repo in cfg["general.repo_path"].split("\n")
        if repo
    ]


def load(paths):
    """
    Load configuration from `paths`, in the specified order.
    :returns: list of files that could not be read
    """
    if not paths:
        return {}

    global cfg
    successful = cfg.read(paths)
    repo.repo_path += repo_path_from_config(cfg)
    repo.repo_path = list(dict.fromkeys(repo.repo_path))  # Remove duplicates

    return set(paths) - set(successful)
