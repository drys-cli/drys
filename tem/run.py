"""Run scripts defined on a temdir level."""
import functools
from typing import Callable

from tem import TemDir


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
