"""
Registry of environment variables used to control the behavior of tem
environments.
"""
import os
from typing import Optional


class EnvVar:
    """An environment variable.

    Attributes
    ----------
    name
        The name of the environment variable.
    """

    def __init__(self, name: str):
        self.name = name

    @property
    def value(self):
        """
        Value of the environment variable. Assigning to this property will
        update the corresponding entry in ``os.environ``.
        """
        return os.environ.get(self.name)

    @value.setter
    def value(self, value: Optional[str]):
        if value is None:
            del os.environ[self.name]
        else:
            os.environ[self.name] = value

    def __str__(self):
        return self.value or ""


shell_source = EnvVar("__TEM_SHELL_SOURCE")
"""
Path to the file where tem should output commands that the parent shell
will then source.

*Environment variable:* :envvar:`__TEM_SHELL_SOURCE`
"""

exported_environment = EnvVar("__TEM_EXPORTED_ENVIRONMENT")
"""
List of paths exported to `PATH` as part of the tem environment.

This variable exists to clearly separate those paths in `PATH` that were
added by tem as part of an :class:`~tem.env.Environment` from those that
existed beforehand.

*Environment variable:* :envvar:`__TEM_EXPORTED_ENVIRONMENT`
"""

# __all__ = tuple(
#    x for x in globals() if isinstance(x, EnvVar) or x == EnvVar
# )
