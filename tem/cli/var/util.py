import textwrap

from tem.var import Variable


def print_doc(variable: Variable):
    """Print documentation for ``variable``, indented for readability."""
    if variable.__doc__:
        print(
            textwrap.TextWrapper(
                initial_indent="    ", subsequent_indent="    "
            ).fill(variable.__doc__)
        )


def print_name_value(var_name, variable, *args_, verbosity, **kwargs):
    """
    Print name and value for variable in :data:`var_container` named
    ``var_name``. Also print documentation if args contain --verbose.

    Parameters
    ----------

    args_
        Additional args that are passed to ``print``.
    kwargs
        Additional kwargs that are passed to ``print``.
    """
    print(var_name, "=", repr(variable.value), *args_, **kwargs)

    verbosity = verbosity
    if verbosity > 0:
        print_doc(variable)
