"""Template and Environment Manager API"""
import enum
import os
from contextvars import ContextVar

from tem._meta import __prefix__, __version__

default_repo = os.path.expanduser("~/.local/share/tem/repo")


class Context(enum.Enum):
    """The runtime context of `tem`."""

    #: Python interpreter
    PYTHON = 0b001
    #: Vanilla command-line interface, without shell extensions
    CLI = 0b010
    #: Command-line interface with a shell extension enabled
    SHELL = 0b100

    def __enter__(self):
        global _context
        token = _context.set(self)
        self._token = token

    def __exit__(self):
        global _context
        _context.reset(self._token)


_context = ContextVar("_context", default=Context.PYTHON)


def context() -> Context:
    """Get the current context `tem` is running in."""
    return _context.get()


def shell():
    sh = os.environ.get("TEM_SHELL", None)
    if sh not in ("fish", "bash", "zsh"):
        return None
    return sh
