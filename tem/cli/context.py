"""Context variables for the tem CLI."""

from typing import Union, Type, ContextManager, List
from contextvars import ContextVar


# Keeps track of which exception types should be treated as warnings in the
# current context
# ContextVar docs say this must be a top module level variable
_as_warnings = ContextVar[List[Type[Exception]]]("__as_warning", default=())


class __AsWarnings:
    def __init__(self, exceptions):
        self.exceptions = tuple(exceptions) if exceptions is not None else None
        self._token = None

    def __enter__(self):
        self._token = _as_warnings.set(self.exceptions)

    def __exit__(self, _1, _2, _3):
        _as_warnings.reset(self._token)

    def __bool__(self):
        exc_types = _as_warnings.get()
        if exc_types is None:
            return True

        for exc_instance in self.exceptions:
            if not isinstance(exc_instance, exc_types) and not (
                type(exc_instance) == type
                and issubclass(exc_instance, exc_types)
            ):
                return False
        return True


def as_warnings(exceptions: List = None) -> Union[ContextManager, bool]:
    """
    Query if ``exceptions`` should be treated as warnings instead of being
    raised. If used as a context manager, then ``exceptions`` is a list of
    exception types that should be treated as warnings in the current context.
    If ``exceptions`` is unspecified, all exceptions will be treated as
    warnings.

    Examples
    --------
    >>> def assign_value(container, index, value):
    >>>     try:
    >>>         container[index] = value
    >>>     except Exception as e:
    >>>         if as_warnings([e]):  # Used here
    >>>             print(e)
    >>>         else:
    >>>             raise e
    >>>
    >>> with as_warnings([IndexError, KeyError]):
    >>>     l = [0, 1]
    >>>     assign_value(l, 2, 2)
    >>>
    """
    return __AsWarnings(exceptions)
