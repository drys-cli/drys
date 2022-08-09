"""Variables defined per directory."""
import functools
import glob
import os
import shelve
from contextlib import ExitStack
from textwrap import TextWrapper
from typing import Any, Dict, Iterable, Union, cast

import tem
from tem import util
from tem.env import Environment
from tem.errors import TemVariableNotDefinedError, TemVariableValueError
from tem.fs import AnyPath, TemDir


class __NoInit(type):
    """Prevents __new__ from calling __init__ automatically."""

    def __call__(cls, *args, **kwargs):
        return cls.__new__(cls, *args, **kwargs)


class Variable(metaclass=__NoInit):
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
        - If you try instantiating this class with a ``var_type`` of ``bool``,
          a :class:`Variant` will be created instead.
    """

    # TODO __slots__ = ("var_type", "value", "to_env", "doc")

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
        if self.to_env:
            os.environ[self.to_env] = str(value)

    def __init__(
        self,
        var_type: Union[type, Any, list] = Any,
        default=None,
        from_env: str = None,
        to_env: str = None,
    ):
        # A type of 'Any' is converted to None for uniformity
        if var_type is None:
            var_type = Any
        if var_type != Any and not isinstance(var_type, (type, list)):
            raise TypeError(
                "'var_type' must be a type or a list containing allowed values"
            )
        if isinstance(var_type, list) and default is None:
            raise TemVariableValueError(
                "'default' value is mandatory if 'var_type' is a list of "
                "allowed values"
            )
        if default is not None and not self._matches_type(default, var_type):
            raise TemVariableValueError(
                "The type of 'default' must match 'var_type'", value=default
            )

        self.from_env = from_env
        self.to_env = to_env
        self.var_type = var_type
        if not self.set_from_env():
            self.value = (
                default
                if default is not None
                else self._default_value_for_type(var_type)
            )
        super().__setattr__("doc", VariableDoc(self))

    def __new__(
        cls,
        var_type: Union[type, Any, list] = Any,
        default=None,
        from_env: str = None,
        to_env: str = None,
    ):
        """Always instantiate a bool variable as a Variant."""
        if var_type == bool:
            return Variant(default=default, from_env=from_env, to_env=to_env)
        variable = super().__new__(cls)
        variable.__init__(
            var_type=var_type,
            default=default,
            from_env=from_env,
            to_env=to_env,
        )
        return variable

    def __setattr__(self, key, value):
        if key == "doc":
            # pylint: disable-next=no-member
            self.doc.description = value
        else:
            super().__setattr__(key, value)

    @staticmethod
    def _matches_type(value, var_type: Union[type, Any, list]):
        if var_type == Any:
            return True
        if isinstance(var_type, type):
            return isinstance(value, var_type)
        return value in var_type

    @staticmethod
    def _default_value_for_type(var_type):
        if isinstance(var_type, type):
            return var_type()
        elif isinstance(var_type, Iterable):
            return next((x for x in var_type), None)
        else:
            return None

    def _convert_to_var_type(self, value):
        if self.var_type == Any:
            return value

        # Variable type is a regular type
        if isinstance(self.var_type, type):
            try:
                return self.var_type(value)
            except Exception:
                raise TemVariableValueError(value=value) from None
        exception = None
        # Variable type is an array of possible values.
        # Go through all allowed values and see if `value` can be converted to
        # any of those.
        for allowed_value in cast(Iterable, self.var_type):
            try:
                converted_value = type(allowed_value)(value)
                if converted_value == allowed_value:
                    return converted_value
            except Exception as e:
                exception = e

        raise TemVariableValueError(value=value) from exception

    def set_from_env(self):
        """
        Set the variable value based on the content of the `from_env`
        environment variable, if it exists.
        Returns
        -------
        True, if the value was set from the environment.
        """
        if not self.from_env:
            return False

        class NonExistent:
            """Special sentinel value."""

        raw_value = os.environ.get(self.from_env, NonExistent)
        if raw_value != NonExistent:
            self.value = self._convert_to_var_type(raw_value)
            return True
        return False


class VariableDoc(str):
    """Glorified string used to document a :class:`Variable`."""

    def __init__(self, variable: Variable):
        self._value_docs: Dict[Any, str] = {}
        self._variable = variable
        self.description = ""
        super().__init__()

    def __setitem__(self, value, doc):
        """Document variable ``value`` as ``doc``."""
        if not Variable._matches_type(value, self._variable.var_type):
            raise TemVariableValueError(value=value)
        self._value_docs[value] = doc

    def __getitem__(self, value):
        return self._value_docs[value]

    def __delitem__(self, value):
        del self._value_docs[value]

    def __iter__(self):
        return iter(self._value_docs)

    def __setattr__(self, key, value):
        if key == "description":
            self.__str__.cache_clear()
        super().__setattr__(key, value)

    @functools.lru_cache(maxsize=1)
    def __str__(self):
        doc = self.description

        # If variable has a regular type
        if self._variable.var_type == Any or isinstance(
            self._variable.var_type, type
        ):
            if doc:
                doc += "\n\n"
            type_ = (
                self._variable.var_type.__name__
                if self._variable.var_type
                else "Any"
            )
            doc += f"Type: {type_}"
            # If at least one value is documented
            if self._value_docs:
                doc += "\n"
                doc += "Notable values:\n"
                doc += self._document_values()
        else:
            if doc:
                doc += "\n\n"
            # If all values are documented
            if len(self._value_docs) == len(self._variable.var_type):
                doc += "Values:\n"
                doc += self._document_values()
            else:
                # If some values are documented
                if self._value_docs:
                    doc += "Notable values:\n"
                    doc += self._document_values()
                    doc += "\nOther values:\n"
                    undoc_values = set(self._variable.var_type) - set(
                        self._value_docs
                    )
                    doc += ", ".join([repr(v) for v in undoc_values])
                # If no values are documented
                else:
                    doc += "Values: "
                    doc += ", ".join(
                        [repr(v) for v in self._variable.var_type]
                    )

        return doc

    def __repr__(self):
        return repr(str(self))

    def __bool__(self):
        return bool(str(self))

    def _document_values(self):
        doc = ""
        doc += "\n".join(
            [
                f"  {repr(value)}\n"
                + TextWrapper(
                    initial_indent="    ", subsequent_indent="    "
                ).fill(doc)
                for value, doc in self._value_docs.items()
            ]
        )
        return doc


class Variant(Variable):
    """A tem variable with a type of ``bool``."""

    def __init__(
        self,
        default=None,
        from_env: str = None,
        to_env: str = None,
    ):
        super().__init__(
            var_type=bool, default=default, from_env=from_env, to_env=to_env
        )

    def __new__(cls, *args, **kwargs):
        variant = super(Variable, cls).__new__(cls)
        variant.__init__(*args, **kwargs)
        return variant

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
        # In order to set the value to True, we have to check mutual exclusion
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


def when(condition: str):
    """Decorator that allows the decorated object to be created only when the
    condition is met."""

    def decorator(func):
        if condition:
            return func
        else:
            try:
                # If the function is already defined, return it
                return eval(func.__name__)  # pylint: disable=eval-used
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
    variable_dict: default={}
        A dictionary of variables to be wrapped by this container. The
        dictionary will automatically be filtered to contain only instances of
        :class:`Variable`.
    """

    def __init__(self, variable_dict=None):
        # Get all public variables (of type `Variable`) from `variable_dict`
        variable_dict = variable_dict or {}
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


def load(
    source: Union[TemDir, Environment] = None, defaults=False
) -> VariableContainer:
    """
    Load variables from the given ``source``.

    Parameters
    ----------
    source
        Temdir or environment whose variables to load. Loading from an
        environment will just load from each temdir in the environment.
        Defaults to :data:`tem.context.env`.
    defaults
        Use default variable values instead of stored values.
    Returns
    -------
    variable_container
        Instance of :class:`VariableContainer` that contains the loaded
        variables.
    """
    source = source or tem.context.env

    if isinstance(source, TemDir):
        return VariableContainer(_load(source, defaults=defaults))

    if not isinstance(source, Environment):
        raise TypeError(
            "Argument 'source' must be a 'TemDir' or 'Environment'"
        )

    # Dict of variable names and loaded variable definitions
    definitions: Dict[str, Variable] = {}

    for temdir in reversed(source.envdirs):
        _definitions = _load(temdir, defaults=defaults)
        definitions = {**definitions, **_definitions}

    return VariableContainer(definitions)


def save(variable_container: VariableContainer, target=None):
    """
    Save the variables from ``variable_container`` to the variable store of
    ``temdir``.

    Parameters
    ----------
    variable_container
        Instance of :class:`VariableContainer` containing the variable values
        to save.
    target: TemDir or Environment
        Temdir or environment where to save variables. If unspecified, the
        currently active environment is used.
    Raises
    ------
    TemVariableNotDefinedError
        If a variable is not defined anywhere in the ``target``.
    See Also
    --------
    load: Load variables that were previously saved using :func:`save`.
    """
    target = target or tem.context.env

    if isinstance(target, TemDir):
        temdirs = [target]
    else:
        temdirs = list(reversed(target.envdirs))

    # Maps each variable name with the lowest temdir that defines it
    var_definition_sources = {
        var_name: None for var_name in variable_container
    }
    for temdir in temdirs:
        definitions = _load_variable_definitions(temdir / ".tem/vars.py")
        for variable in definitions:
            var_definition_sources[variable] = temdir

    if None in var_definition_sources.values():
        raise TemVariableNotDefinedError()

    with ExitStack() as stack:
        for temdir in temdirs:
            store = stack.enter_context(
                # pylint: disable-next=protected-access
                shelve.open(str(temdir._internal / "vars"), writeback=True)
            )
            # We store only those variables that are in `variable_container`.
            # Even then, the new value is stored inside `temdir` only if it is
            # the lowest directory that defines the variable. Otherwise, the
            # directory retains the old value for the variable.
            values = store["values"] if "values" in store else {}
            for vname in variable_container:
                if var_definition_sources[vname] == temdir:
                    values[vname] = variable_container[vname].value
            store["values"] = values
            store["tem_version"] = tem.__version__


def _load(temdir: TemDir, defaults=False) -> Dict[str, Variable]:
    """
    Helper function for :func:`load` that loads variables from ``temdir`` and
    returns them.
    """
    if not os.path.isfile(temdir / ".tem/vars.py"):
        return {}
    # pylint: disable-next=protected-access
    saved_vars_path = str(temdir._internal / "vars")
    definitions = _load_variable_definitions(temdir / ".tem/vars.py")
    # Try to load variables from temdir's variable store
    if not defaults and glob.glob(f"{saved_vars_path}*"):
        for var_name, value in _load_from_shelf(saved_vars_path).items():
            if not definitions[var_name].set_from_env():
                definitions[var_name].value = value
    return definitions


def _load_variable_definitions(path) -> Dict[str, Variable]:
    try:
        definitions = util.import_path("__tem_var_definitions", path)
    except FileNotFoundError:
        return {}
    return _filter_variables(definitions.__dict__)


def _load_from_shelf(file: AnyPath) -> Dict[str, Variable]:
    """Load a variable namespace object from variable store ``file``."""
    shelf = shelve.open(file)
    variables = shelf.get("values", {})
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
        if isinstance(val, Variable)
        and not (key.startswith("_") and key.endswith("_"))
    }
