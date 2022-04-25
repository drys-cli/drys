"""
The context is used to obtain global information in a nested call structure,
without passing that information as arguments with each call. For example, when
you set ``tem.context.temdir`` to a certain value, whenever you access
``tem.context.temdir`` from that point onwards, it will have the value you set.

Another convenient way instead of setting :attr:`tem.context.env` is to use
:class:`~tem.env.Environment` as a context manager.

Examples
--------
>>> from tem import context
>>> from tem.env import Environment
>>> context.env = Environment("/path/to/dir1")
>>> print(context.env.basedir)
/path/to/dir1
>>> with Environment("/path/to/dir2"):
>>>     print(context.env.basedir)
/path/to/dir2
>>> print(context.env)
/path/to/dir1

"""
import enum
import sys
import types
from contextvars import ContextVar


class Runtime(enum.Enum):
    """*[Enum]* The runtime context of `tem`."""

    #: Python interpreter
    PYTHON = 0b001
    #: Vanilla command-line interface, without shell extensions
    CLI = 0b010
    #: Command-line interface with a shell extension enabled
    SHELL = 0b100

    def __enter__(self):
        global _runtime
        token = _runtime.set(self)
        self._context_reset_token = token

    def __exit__(self, _1, _2, _3):
        global _runtime
        _runtime.reset(self._context_reset_token)


class __ContextModule(types.ModuleType):

    _runtime = ContextVar("_context", default=Runtime.PYTHON)
    _env = ContextVar("_context_env", default=None)

    @property
    def runtime(self) -> Runtime:
        return _runtime.get()

    @property
    def env(self):
        """Get the environment of the active context."""
        from tem.env import Environment

        return self._env.get() or Environment()


sys.modules[__name__].__class__ = __ContextModule
