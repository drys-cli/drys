"""Registry of environment variables used by tem."""
import functools
import inspect
import os
import sys
from types import ModuleType
from typing import Optional, Callable, Union

__envvars = []


def _envvar(name):
    __envvars.append(name)

    def decorator(func):
        @functools.wraps(func)
        def getter(_: object):
            return os.environ.get(name)

        def setter(_, value: str):
            os.environ[name] = value

        getter.__doc__ += f"\n\t*Environment variable*: `{name}`"
        return property(getter).setter(setter)

    return decorator


class __Vars(ModuleType):
    """
    Registry of environment variables used to control the behavior of tem
    environments.
    """

    @_envvar("__TEM_SHELL_SOURCE")
    def shell_source(self) -> Optional[str]:
        """
        Path to the file where tem should output commands that the parent shell
        will then source.
        """

    @_envvar("__TEM_EXPORTED_ENVIRONMENT")
    def exported_environment(self) -> Optional[str]:
        """
        List of paths exported to `PATH` as part of the tem environment.

        This variable exists to clearly separate those paths in `PATH` that were
        added by tem as part of an :class:`~tem.env.Environment` from those that
        existed beforehand.
        """

    def __iter__(self):
        return iter(self.__all__)

    __all__ = tuple(
        x for x in locals() if not x.startswith("_") and inspect.isfunction(x)
    )


sys.modules[__name__].__class__ = __Vars
