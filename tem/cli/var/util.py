import enum
import textwrap
from typing import Dict, Any

from tem import util
from tem.var import Variable, VariableContainer
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
    if variable.doc:
        print(textwrap.indent(str(variable.doc), "  "))


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
        if var_name != "use_pipenv":
            return  # TODO
        print_doc(variable)


def print_all_values(var_container, verbosity=0):
    for name, variable in {**var_container}.items():
        print_name_value(name, variable, verbosity=verbosity)


def print_default_and_old_value(var_name, variable, default, old_value):
    if old_value != default or cli.args().verbosity > 0:
        additional_args = (
            ["\033[1;33m\t| was:\033[0m", old_value]
            if cli.args().verbosity >= 2
            else []
        )
        print_name_value(var_name, variable, *additional_args, verbosity=0)


def edit_values(value_dict: Dict[str, Any], var_container: VariableContainer):
    """Return the `value_dict` after being edited in a text editor."""
    result_dict = dict()
    # Contains an assignment text for each variable
    lines = []
    longest_line_length = 0

    # Populate `lines`
    for k, value in value_dict.items():
        var = var_container[k]
        line = f"{k} = {repr(value)}"
        if len(line) > longest_line_length:
            longest_line_length = len(line)
        lines.append(line)

    # Append "possible types" hint at the end of each line
    for i, (k, value) in enumerate(value_dict.items()):
        var = var_container[k]
        if isinstance(var.var_type, list):
            possible_values = "One of: " + ", ".join(
                [repr(val) for val in var.var_type]
            )
        else:
            possible_values = "Type: " + var.var_type.__name__
        lines[i] = (
            lines[i].ljust(longest_line_length) + "  # " + possible_values
        )

    initial_content = (
        "# Change the variable values to your liking and save this file.\n"
        "# NOTE: This file uses python syntax\n\n"
    ) + "\n".join(lines)
    with cli.edit_tmp_file(suffix=".py", initial_content=initial_content) as (
        _,
        path,
    ):
        mod = util.import_path("__tem_temporary_module", path)
        for attr, value in mod.__dict__.items():
            if not (attr.startswith("__") and attr.endswith("__")):
                result_dict[attr] = value

    return result_dict
