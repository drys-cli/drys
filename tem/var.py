"""Variables defined per directory."""
import functools
import importlib.util
import inspect
import os
import shelve
import sys
import types
import typing
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union

import tem
from tem import env, util
from tem.env import Environment
from tem.errors import TemVariableValueError
from tem.fs import TemDir


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
            raise TemVariableValueError(value=value)
        self._value = value
        if self._to_env:
            os.environ[self._to_env] = str(value)

    def _function_with_init_params(exclude_args: List[str] = []):
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
        if var_type and not isinstance(var_type, (type, list)):
            raise TypeError(
                "'var_type' must be a type or a list containing allowed"
                "values"
            )
        if default is not None and from_env is not None:
            raise ValueError("You can use only one of: 'default', 'from_env'")
        if default is not None and not self._matches_type(default, var_type):
            raise TemVariableValueError(
                "The type of 'default' must match 'var_type'"
            )

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

    # An undirected graph that keeps track of variants that are mutually
    # exclusive. Implemented as a dict[Variant, list[Variant]] that maps each
    # variant to a list of variants that exclude it.
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


class VariableContainer:
    """
    An object that serves as a namespace for tem variables. Variable values are
    accessed as attributes.

    Parameters
    ----------
    variable_dict: default=dict()
        A dictionary of variables to be wrapped by this container. The
        dictionary will automatically be filtered to contain only instances of
        :class:`Variable`.
    """

    def __init__(self, variable_dict=None):
        # Get all public variables (of type `Variable`) from `variable_dict`
        variable_dict = variable_dict or dict()
        __dict__ = _filter_variables(variable_dict)
        object.__setattr__(self, "__dict__", __dict__)

    def __getattribute__(self, attr):
        __dict__ = object.__getattribute__(self, "__dict__")
        if not (__dict__ and attr in __dict__):
            return object.__getattribute__(self, attr)

        attribute = __dict__[attr]
        if isinstance(attribute, Variable):
            return __dict__[attr].value

        return attribute

    def __setattr__(self, attr, value):
        attribute = object.__getattribute__(self, attr)
        if isinstance(attribute, Variable):
            attribute.value = value
        else:
            object.__setattr__(self, attr, value)

    def __getitem__(self, name: str) -> Variable:
        """Return the variable wrapped by this container named ``name``."""
        return self.__dict__[name]

    def __setitem__(self, name, definition: Variable):
        """
        Change the definition of the variable named ``name`` wrapped by this
        container. Note that the new variable will have its default value.
        """
        self.__dict__[name] = definition

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return (variable for variable in self.__dict__)


def load(source=None, defaults=False):
    """
    Load variables for the given ``temdir``.

    Parameters
    ----------
    source: TemDir or Environment, default=None
        Temdir or environment whose variables to load. Loading from an
        environment will just load from each temdir in the environment. Defaults
        to `env.current()`.
    defaults
        Use default variable values instead of stored values.
    Returns
    -------
    variable_container
        Instance of :class:`VariableContainer` that contains the loaded
        variables.
    """
    source = source or env.current() or Environment()

    if isinstance(source, TemDir):
        return VariableContainer(_load(source, defaults=defaults)[0])

    if not isinstance(source, Environment):
        raise TypeError(
            "Argument 'source' must be a 'TemDir' or 'Environment'"
        )

    # Container of variable definitions and loaded values
    container = VariableContainer()
    # Variable definitions, along with default values
    definitions = dict()

    for temdir in reversed(source.envdirs):
        _container, _definitions = _load(temdir, defaults=defaults)
        definitions = {**definitions, **_definitions}
        container = VariableContainer({**container.__dict__, **_container})

    container = VariableContainer({**definitions, **container.__dict__})

    return container


def _load(temdir: TemDir, defaults=False) -> Tuple[Dict, Dict]:
    """
    Helper function for :func:`load` that returns loads variables from
    ``temdir``.
    """
    if not os.path.isfile(temdir / ".tem/vars.py"):
        return dict(), dict()
    saved_vars_path = str(temdir._internal / "vars")
    definitions = __load_variable_definitions(temdir / ".tem/vars.py")
    # Try to load variables from temdir's variable store
    if not defaults and os.path.isfile(saved_vars_path):
        return __load_from_shelf(saved_vars_path), definitions

    return definitions, definitions


def save(variable_container: VariableContainer, temdir: TemDir = None):
    """
    Save the variables from ``variable_container`` to the variable store of
    ``temdir``.

    Parameters
    ----------
    variable_container
        Instance of :class:`VariableContainer` containing the variable values to
        save.
    temdir
        Temdir where to save variables. Determined based on CWD by default.
    See Also
    --------
    load: Load variables that were previously saved using :func:`save`.
    """
    temdir = temdir or TemDir()
    file = str(temdir._internal / "vars")
    store = shelve.open(file)

    store["tem_version"] = tem.__version__
    store["container"] = variable_container.__dict__
    store.close()


def __load_variable_definitions(path) -> Dict[str, Variable]:
    definitions = _import_path("__tem_var_definitions", path)
    return _filter_variables(definitions.__dict__)


def __load_from_shelf(file) -> Dict[str, Variable]:
    """Load a variable namespace object from variable store ``file``."""
    shelf = shelve.open(file)
    variables = shelf.get("container", dict())
    shelf.close()
    return variables


def _filter_variables(dictionary: dict) -> Dict[str, Variable]:
    """
    Filter ``dictionary`` so only public values of type ``Variable`` remain.
    Note: Variables are considered public if they don't start with an
    underscore.
    """
    return {
        key: val
        for key, val in dictionary.items()
        if isinstance(val, Variable) and not key.startswith("_")
    }


def _import_path(
    module_name: str, path: Path, add_to_sys=False
) -> types.ModuleType:
    """Import a python file from ``path``."""
    if not os.path.exists(path):
        raise FileNotFoundError
    if os.path.isdir(path):
        raise NotImplementedError

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if add_to_sys:
        sys.modules[module_name] = module
    return module


################################################################################


def active_variants() -> List[str]:
    return _read_variants()


def activate(variants: List[str]):
    _write_variants(util.unique(active_variants() + variants))


def deactivate(variants: List[str]):
    new = [var for var in active_variants() if var not in variants]
    _write_variants(new)


def set_active_variants(variants: List[str]):
    _write_variants(util.unique(variants))


def _read_variants() -> List[str]:
    """Read the active variants for the current."""
    if not os.path.exists(".tem/.internal/variants"):
        return []
    with open(".tem/.internal/variants", encoding="utf-8") as f:
        return f.read().split("\n")


def _write_variants(variants: List[str]):
    if not os.path.exists(".tem/.internal"):
        os.mkdir(".tem/.internal")
    with open(".tem/.internal/variants", "w", encoding="utf-8") as f:
        f.write("\n".join(variants))
