"""Template and Environment Manager API"""
import os

from tem._meta import __prefix__, __version__

default_repo = os.path.expanduser("~/.local/share/tem/repo")


def shell():
    sh = os.environ.get("TEM_SHELL", None)
    if sh not in ("fish", "bash", "zsh"):
        return None
    return sh
