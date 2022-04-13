"""Manipulate tem variants."""
import os
import sys
from argparse import ArgumentParser
from typing import Iterable, List

from tem import env, var, context
from tem.cli import common as cli
from tem.errors import TemError, TemVariableValueError
from tem.fs import TemDir

from .expr import Expression, Get, Query, SimpleExpression, Assign, Cycle
from .util import (
    edit_values,
    print_default_and_old_value,
    print_name_value,
    print_all_values,
)

#: Variable container to which most operations in this module are applied.
var_container: var.VariableContainer


def setup_parser(p: ArgumentParser):
    p.add_argument(
        "expressions", nargs="*", help="variable names or assignments"
    )
    actions = p.add_argument_group(
        title="action options"
    ).add_mutually_exclusive_group()
    modifiers = p.add_argument_group(title="modifier options")

    actions.add_argument(
        "-q",
        "--query",
        action="store_true",
        help="query if EXPRESSIONS are true",
    )
    actions.add_argument(
        "-a",
        "--active",
        action="store_true",
        help="print all active variants matching EXPRESSIONS",
    )
    actions.add_argument(
        "-z",
        "--reset",
        action="store_true",
        help="restore variables to their default values",
    )
    actions.add_argument(
        "-l", "--list", action="store_true", help="list all defined variables"
    )

    modifiers.add_argument(
        "-d",
        "--defaults",
        action="store_true",
        help="do not load stored values, only defaults",
    )
    modifiers.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity",
        default=0,
        help="print more information",
    )

    cli.add_general_options(p)
    cli.add_edit_options(p)

    p.set_defaults(func=cmd)


def parse_simple_expressions(expressions: Iterable[str]) -> List[Expression]:
    """
    Parse ``expressions`` and return a list of :class:`Expression` objects.
    Warnings will be emitted for each invalid expression.
    """
    result = []
    for expr in expressions:
        try:
            with handle_expression_exceptions():
                result.append(SimpleExpression(expr, var_container))
        except SyntaxError as e:
            cli.print_cli_warn(e)
    return result


class handle_expression_exceptions:
    """
    A reusable try block for raising SyntaxErrors with descriptions from various
    exceptions.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc: Exception, traceback):
        if exc_type is None:
            return
        if issubclass(exc_type, SyntaxError):
            raise SyntaxError(f"invalid expression: {exc}")
        elif issubclass(exc_type, KeyError):
            raise SyntaxError(f"variable {exc} is not defined")
        elif issubclass(exc_type, TemVariableValueError):
            exc: TemVariableValueError
            val = repr(exc.value)
            raise SyntaxError(
                f"value {val} does not match type for variable '{exc.name}'"
            )


def process_simple_expressions():
    # An empty expressions CLI argument means get the values of all variables
    args = cli.args()
    expressions = parse_simple_expressions(args.expressions or var_container)
    any_succeeded = False

    if args.edit or args.editor:
        values = {}
        for expr in expressions:
            value = None
            if isinstance(expr, Assign):
                value = expr.rhs
            elif isinstance(expr, Cycle):
                expr.execute()
                value = expr.variable.value
            elif isinstance(expr, Get):
                value = expr.variable.value
            values[expr.var_name] = value

        values = edit_values(
            {expr.var_name: expr.value for expr in expressions},
            var_container,
        )
        for i, expr in enumerate(expressions):
            var_name = expr.var_name
            expr = Assign.from_pair(var_name, values[var_name], var_container)
            expr.execute()

    # Execute each expression
    for expr in expressions:
        try:
            with handle_expression_exceptions():
                expr.execute()
                any_succeeded = True
        except SyntaxError as e:
            cli.print_cli_warn(e)

    if args.expressions and not any_succeeded:
        # All expressions failed
        cli.print_cli_err("none of the specified expressions are valid")
        cli.exit_code = 1
    else:
        verbosity = args.verbosity
        if not args.expressions and args.verbosity == 0:
            verbosity += 1
        for expr in expressions:
            print_name_value(
                expr.var_name, expr.variable, verbosity=verbosity
            )


def process_query_expressions():
    args = cli.args()
    for expr in args.expressions:
        try:
            with handle_expression_exceptions():
                expr = Query(expr, var_container)
                expr.execute()
                print_name_value(
                    expr.var_name, expr.variable, verbosity=args.verbosity - 1
                )
        except SyntaxError as e:
            cli.print_cli_err(e)
            cli.exit_code = 1


def reset_to_defaults():
    args = cli.args()
    global var_container
    # No positional args => delete the variable store
    if not args.expressions and not (args.edit or args.editor):
        try:
            os.remove(TemDir()._internal / "vars")
        except FileNotFoundError:
            pass
        if args.verbosity:
            for var_name, default in var.load(defaults=True).__dict__.items():
                old_value = var_container[var_name].value
                var_container[var_name].value = default.value
                print_default_and_old_value(
                    var_name, var_container[var_name], default.value, old_value
                )
        return
    expressions = args.expressions or var_container
    # Validate that args.expressions contains only expressions of type `Get`
    for expr in expressions:
        try:
            with handle_expression_exceptions():
                get = SimpleExpression(expr, var_container)
                if not isinstance(get, Get):
                    raise TemError(
                        f"expression {expr} is not valid with `--reset` option"
                    )
        except SyntaxError as e:
            cli.print_cli_err(e)
            return
    # Maps variable names to their default values
    defaults = {
        k: v.value
        for k, v in var.load(defaults=True).__dict__.items()
        if k in expressions
    }
    # Possibly intercept (edit) the default values before committing them
    if args.edit or args.editor:
        defaults = edit_values(defaults, var_container)

    # Commit the changes and print
    for var_name, default in defaults.items():
        old_value = var_container[var_name].value
        var_container[var_name].value = default
        print_default_and_old_value(
            var_name, var_container[var_name], default, old_value
        )
    var.save(var_container)


def edit_defaults():
    args = cli.args()
    if args.expressions:
        cli.print_cli_err(
            "'tem --default --edit/--editor' accepts no arguments"
        )
        sys.exit(1)
    cli.edit_files(
        [
            temdir / ".tem/vars.py"
            for temdir in context.env.envdirs
            if (temdir / ".tem/vars.py").is_file()
        ],
        override_editor=args.editor,
    )
    if args.verbosity:
        print_all_values(var.load(defaults=True), verbosity=args.verbosity)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    with env.Environment():

        global var_container
        var_container = var.load(defaults=(args.defaults and not args.reset))

        # Handle conflicting/ineffectual option combinations
        if args.query and (args.edit or args.editor):
            cli.print_cli_warn(
                "--edit and --editor have no effect with --query"
            )
            args.edit = args.editor = None
        if args.defaults and args.reset:
            cli.print_cli_warn("--default has no effect with --reset")

        # Special case: tem var -de
        if (
            (args.edit or args.editor)
            and args.defaults
            and not args.query
            and not args.reset
        ):
            edit_defaults()
            return

        if args.query:
            process_query_expressions()
        elif args.reset:
            reset_to_defaults()
        else:
            process_simple_expressions()
            var.save(var_container)
