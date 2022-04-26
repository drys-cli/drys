"""Python bindings for shell commands."""

import os
import shlex


class _Util:
    """
    Utility functions, wrapped inside this class to avoid namespace problems
    when importing this module. Must be instantiated in order to use
    properties.
    """

    @classmethod
    def eval(cls, text: str):
        """Instruct the shell that it should evaluate ``text``."""
        path = os.environ.get("__TEM_SHELL_SOURCE")
        if not path:
            raise EnvironmentError(
                "No '__TEM_SHELL_SOURCE' environment variable"
            )

        with open(path, "a", encoding="utf-8") as file:
            print(text, file=file)


def export(variable, value):
    """Export a variable named ``variable`` with value ``value``."""
    _Util.eval(f"export {variable}={shlex.quote(value)}")


def command(cmd, *args):
    """Run shell command ``cmd`` with arguments ``args``."""
    _Util.eval(" ".join([shlex.quote(token) for token in [cmd] + list(args)]))
