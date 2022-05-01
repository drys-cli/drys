"""Run scripts defined on a temdir level."""
import functools
import subprocess
from typing import Callable

from tem import TemDir
from tem.fs import Executable


def run(script_name: str, *args, temdir: TemDir = None):
    """Run script with path ``script_name`` relative to `.tem/path`."""
    temdir = temdir or TemDir()
    executable = Executable(temdir["path"] / script_name)
    subprocess.run([str(executable.absolute()), *args], check=False)


def script(mount_point: str):
    """
    Decorator that makes its function callable as a script. This will not
    create a script file, but will behave as if it were.

    Parameters
    ----------
    mount_point
        Entry under `.tem/path` the script should be available at.
    """
    _ = mount_point  # TODO

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # TODO
            return func(*args, **kwargs)

        return wrapper

    return decorator
