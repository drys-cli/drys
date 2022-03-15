"""
Template and Environment Manager API

The top level module provides some global defaults and ways to retrieve values
from the current context. The current context is
"""
import enum
import os
from contextvars import ContextVar

from tem._meta import __prefix__, __version__

from .fs import TemDir
from .env import Environment

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
        self._context_reset_token = token

    def __exit__(self, _1, _2, _3):
        global _context
        _context.reset(self._context_reset_token)


_context = ContextVar("_context", default=Context.PYTHON)


class __Context:
    _temdir = ContextVar("_context_temdir", default=None)
    _env = ContextVar("_context_env", default=None)

    @classmethod
    def __call__(cls):
        return _context.get()

    @property
    def temdir(self):
        """Get the temdir of the current context."""
        return self._temdir.get() or TemDir()

    @property
    def env(self):
        """Get the environment of the current context."""
        return self._env.get() or Environment()


context = __Context()
