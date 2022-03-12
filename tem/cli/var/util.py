import enum
import textwrap
from typing import Dict, Any

from tem import util
from tem.var import Variable
from tem.cli import common as cli


# This class is used as a way to document the verbosity levels
class Verbosity(enum.Enum):
    """Verbosity levels. Usually the number of `--verbose` flags."""

    LIST = -1  # When --list option is used
    NONE = -1  # Otherwise
    DEFAULT = 0
    DOCUMENTATION = 1
    OLD_VALUE = 1  # When --reset option is used


def print_doc(variable: Variable):
    """Print documentation for ``variable``, indented for readability."""
    if variable.__doc__:
        print(
            textwrap.TextWrapper(
                initial_indent="    ", subsequent_indent="    "
            ).fill(variable.__doc__)
        )


def print_name_value(var_name, variable, *args_, verbosity=0, **kwargs):
    """
    Print name and value for ``variable`` named ``var_name``. Also print
    documentation if args contain --verbose.

    Parameters
    ----------

    args_
        Additional args that are passed to ``print``.
    kwargs
        Additional kwargs that are passed to ``print``.
    """
    if verbosity < 0:
        return

    print(var_name, "=", repr(variable.value), *args_, **kwargs)

    if verbosity > 0:
        print_doc(variable)


def print_default_and_old_value(var_name, variable, default, old_value):
    if old_value != default or cli.args().verbosity > 0:
        additional_args = (
            ["\033[1;33m\t| was:\033[0m", old_value]
            if cli.args().verbosity >= 2
            else []
        )
        print_name_value(var_name, variable, *additional_args, verbosity=0)


def edit_values(value_dict: Dict[str, Any]):
    """Return the `value_dict` after being edited in a text editor."""
    result_dict = dict()
    initial_content = (
        "# Change the variable values to your liking and save this file.\n"
        "# NOTE: This file uses python syntax\n\n"
    ) + "\n".join([f"{k} = {repr(value)}" for k, value in value_dict.items()])
    with cli.edit_tmp_file(suffix=".py", initial_content=initial_content) as (
        _,
        path,
    ):
        mod = util.import_path("__tem_temporary_module", path)
        for attr, value in mod.__dict__.items():
            if not (attr.startswith("__") and attr.endswith("__")):
                result_dict[attr] = value

    return result_dict
