"""Variables defined per directory."""
import functools
import inspect
import os
import typing
from typing import Any, Callable, Iterable, Union, overload

from tem import find, util
from tem.fs import TemDir


class V:
    """A namespace containing all tem variables in the current Environment."""


class Variable:
    """A tem variable.

    Parameters
    ----------
    var_type
        Type of this variable. Can be specified as any ``type`` or a list of
        possible values. Ignore or use ``Any`` to allow any type.
    default
        Default value. Its type must match ``var_type``. If unspecified, then
        the default value for the given ``var_type`` will be used. Cannot be
        used at the same time as ``from_env``.
    from_env
        Environment variable from which to take the default value. The
        environment variable value will be parsed to an object whose type best
        matches ``var_type``. Note that ``var_type`` must be a primitive type
        or a list of values with primitive types.
    to_env
        Changes to this variable will be reflected in a corresponding change of
        the environment variable named ``to_env``.
    Notes
    -----
        - If you try instantiating this class with a ``var_type`` of ``bool``, a
          :class:`Variant` will be created instead.
    """

    @property
    def value(self):
        """Value of the variable."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the variable value."""
        if not self._matches_type(value, self.var_type):
            raise ValueError("'value' must match 'var_type'")
        self._value = value
        if self._to_env:
            os.environ[self._to_env] = str(value)

    def _function_with_init_params(exclude_args: list[str] = []):
        """Modifies a function signature so it has Variable init parameters."""
        # We define this so that we don't have to maintain this signature in 3
        # different places, and also because of a python behavior:
        # Consider what happens when a Variable(bool) is instantiated:
        #   Variable.__new__(cls, bool)
        #     return Variant(bool)
        #       Variant.__init__(bool)
        # Although var_type is a kwarg, Variable was instantiated by specifying
        # it as a positional argument, and it is passed as such to
        # Variant.__init__. But the problem is that the first argument of
        # Variant.__init__ is default instead of var_type.
        # I'm not sure why, but this decorator fixes the behavior.
        def decorator(actual_function):
            @functools.wraps(actual_function)
            def wrapper(
                    self,
                    var_type: Union[type, Any, Iterable[Any]] = Any,
                    default=None,
                    from_env: str = None,
                    to_env: str = None,
            ):
                """This function determines the parameters of __init__."""
                return actual_function(
                    self,
                    var_type=var_type,
                    default=default,
                    from_env=from_env,
                    to_env=to_env,
                )

            sig = inspect.signature(wrapper)
            sig.replace(
                parameters=tuple(
                    param
                    for param in sig.parameters.values()
                    if param.name not in exclude_args
                )
            )
            wrapper.__signature__ = sig

            return wrapper

        return decorator

    @_function_with_init_params()
    def __init__(self, *args, **kwargs):
        # A type of 'Any' is converted to None for uniformity
        var_type = kwargs["var_type"]
        default = kwargs["default"]
        from_env = kwargs["from_env"]
        to_env = kwargs["to_env"]
        if var_type == Any:
            var_type = None
        if (
            var_type and not isinstance(var_type, (type, Iterable))
        ) or isinstance(var_type, (str, bytes)):
            raise TypeError(
                "'var_type' must be a type or an iterable containing allowed"
                "values"
            )
        if default is not None and from_env is not None:
            raise ValueError("You can use only one of: 'default', 'from_env'")
        if default is not None and not self._matches_type(default, var_type):
            raise ValueError("The type of 'default' must match 'var_type'")

        self.var_type = var_type
        self._to_env = to_env
        self.value = default or self._default_value_for_type(var_type)

    @_function_with_init_params()
    def __new__(cls, *args, **kwargs):
        """Always instantiate a bool variable as a Variant."""
        var_type = kwargs.get("var_type")
        if var_type == bool:
            kwargs.pop("var_type")
            return Variant(*args, **kwargs)
        return super().__new__(cls)

    @staticmethod
    def _matches_type(value, var_type):
        if value is None or var_type is None:
            return True
        elif isinstance(var_type, type):
            return isinstance(value, var_type)
        else:
            return value in var_type

    @staticmethod
    def _default_value_for_type(var_type):
        if isinstance(var_type, type):
            return var_type()
        elif isinstance(var_type, Iterable):
            return next((x for x in var_type), None)
        else:
            return None

    @staticmethod
    def _parse_from_env(self):
        raise NotImplementedError


class Variant(Variable):
    """A tem variable with a type of ``bool``."""

    @Variable._function_with_init_params(exclude_args=["var_type"])
    def __init__(self, *args, **kwargs):
        kwargs["var_type"] = bool
        super().__init__(*args, **kwargs)

    @classmethod
    def mutex(cls, variants):
        """Make the decorated variant mutually exclusive with ``variants``."""

        def decorator(variant: Variant):
            if variant in cls._mutually_exclusive:
                cls._mutually_exclusive[variant] = []
            cls._mutually_exclusive[variant] += variants
            return variant

        return decorator

    @Variable.value.setter
    def value(self, value):
        if not value:
            Variable.value.fset(self, value)
            return
        # If we want to set the value to True, we have to check mutual exclusion
        _excluded_by = (
            v for v in self._mutually_exclusive.get(self, []) if v.value
        )
        if next((v for v in _excluded_by if v), None):
            # TODO define custom error class
            raise ValueError(
                f"Variable {self.__name__} is excluded by:"
                f" {', '.join(_excluded_by)}"
            )
        Variable.value.fset(self, value)

    value.__doc__ = ""  # Do not repeat it in sphinx autodoc output

    # A graph that keeps track of variants that are mutually exclusive.
    # Implemented as a dict[Variant, list[Variant]]
    # Maps each variant to a list of variants that exclude it.
    _mutually_exclusive = {}


def var(on_change):
    """
    Decorator that creates a Variable and uses the decorated function as an
    on_change listener.

    Parameters
    ----------
    on_change:
        The on_change listener receives the value that is about to be set for
        the variable, and its return value will be used as an override value.
    """
    var_type = typing.get_type_hints(on_change).get("return")
    variable = Variable(var_type)
    variable._on_change = on_change


def activate_(variant: Variant):
    """Activate a variant (set it to ``True``)."""
    variant.value = True


def deactivate_(variant: Variant):
    """Deactivate a variant (set it to ``False``)."""
    variant.value = False


def when(condition: str):
    """Decorator that allows the decorated object to be created only when the
    condition is met."""

    def decorator(func):
        if condition:
            return func
        else:
            try:
                # If the function is already defined, return it
                return eval(func.__name__)
            except NameError:
                # Otherwise, return a function that throws ...
                def raise_name_error():
                    exception = NameError(
                        f"function '{func.__name__}' is not defined"
                    )
                    exception.__context__ = None
                    raise exception

                return raise_name_error

    return decorator


def load(temdir: TemDir = None, recursive=True, only_env=False):
    """Load tem variables into the current program.

    Parameters
    ----------
    temdir
        Temdir from which to load variables.
    recursive
        Load variables from all directories in the hierarchy, from the top down
        until variables for ``temdir`` are loadedin an
    only_env
        Load variables only if ``temdir`` is in an active environment.
    """
    if temdir is None:
        temdir = TemDir()


def save():
    pass


def _load_for_single_directory(dir: TemDir):
    pass


###############################################################################


def active_variants() -> list[str]:
    return _read_variants()


def activate(variants: list[str]):
    _write_variants(util.unique(active_variants() + variants))


def deactivate(variants: list[str]):
    new = [var for var in active_variants() if var not in variants]
    _write_variants(new)


def set_active_variants(variants: list[str]):
    _write_variants(util.unique(variants))


def _read_variants() -> list[str]:
    """Read the active variants for the current."""
    if not os.path.exists(".tem/.internal/variants"):
        return []
    with open(".tem/.internal/variants", encoding="utf-8") as f:
        return f.read().split("\n")


def _write_variants(variants: list[str]):
    if not os.path.exists(".tem/.internal"):
        os.mkdir(".tem/.internal")
    with open(".tem/.internal/variants", "w", encoding="utf-8") as f:
        f.write("\n".join(variants))
