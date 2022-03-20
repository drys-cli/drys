import os
import shlex

from . import shell


class _Util:
    """
    Utility functions, wrapped inside this class to avoid namespace problems
    when importing this module. Must be instantiated in order to use properties.
    """

    @classmethod
    def eval(self, text: str):
        """Instruct the shell that it should evaluate ``text``."""
        path = os.environ.get("__TEM_SHELL_SOURCE")
        if not path:
            raise EnvironmentError(
                "No '__TEM_SHELL_SOURCE' environment variable"
            )

        with open(path, "a") as file:
            print(text, file=file)


def export(variable, value):
    _Util.eval(f"export {variable}={shlex.quote(value)}")


def command(cmd, *args):
    _Util.eval(" ".join([shlex.quote(token) for token in [cmd] + list(args)]))
