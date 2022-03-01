"""Manipulate tem variants."""
import ast
import os
import textwrap
from abc import ABC
from typing import List, Iterable

from tem import util, var
from tem.cli import common as cli
from tem.errors import TemVariableValueError, TemError
from tem.fs import TemDir

from tem.var import Variant, Variable


#: Variable container to which most operations in this module are applied.
var_container: var.VariableContainer
args = None


def setup_parser(p):
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


def print_doc(variable: Variable):
    """Print documentation for ``variable``, indented for readability."""
    if variable.__doc__:
        print(
            textwrap.TextWrapper(
                initial_indent="    ", subsequent_indent="    "
            ).fill(variable.__doc__)
        )


def print_name_value(var_name, *args_, verbosity=None, **kwargs):
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
    variable = var_container[var_name]
    print(var_name, "=", repr(variable.value), *args_, **kwargs)

    verbosity = verbosity if verbosity is not None else args.verbosity
    if verbosity > 0:
        print_doc(variable)


class Expression:
    """
    Represents any expression supported by the `tem var` command. Subclasses
    must raise a `SyntaxError` on any expected error, with an optional error
    message as its argument. All other errors will be considered bugs.
    """

    @classmethod
    def _ast_parse(cls, expr: str) -> ast.stmt:
        try:
            parsed = ast.parse(expr)
            if len(parsed.body) != 1:
                raise SyntaxError
        except SyntaxError:
            raise SyntaxError
        return parsed.body[0]

    @classmethod
    def _ast_name(cls, expr: str) -> ast.Name:
        expr = cls._ast_parse(expr)
        if not isinstance(expr, ast.Expr) or not isinstance(
            expr.value, ast.Name
        ):
            raise SyntaxError
        return expr.value

    @classmethod
    def _ast_constant(cls, expr: str) -> ast.Constant:
        expr = cls._ast_parse(expr)
        if not isinstance(expr, ast.Expr) or not isinstance(
            expr.value, ast.Constant
        ):
            raise SyntaxError
        return expr.value

    @classmethod
    def _parse_rhs(cls, expr: str, variable: Variable):
        """
        Parse a right-hand side from ``expr``, allowing for special syntax
        like: string without quote, true and false instead of True and False.
        """
        if variable.var_type == str:
            return expr
        elif isinstance(variable.var_type, list) and all(
            isinstance(t, str) for t in variable.var_type
        ):
            # Variable type is a list of string values
            return expr
        try:
            return cls._ast_constant(expr).value
        except SyntaxError:
            if variable.var_type in (bool, None) and expr in (
                "true",
                "false",
            ):
                return expr == "true"
            elif variable.var_type is None:
                return expr
            else:
                raise SyntaxError

    def execute(self):
        raise NotImplementedError


class SimpleExpression(Expression, ABC):
    """Represents a single variable get, assign or toggle expression."""

    def __new__(cls, expr: str):
        if cls != SimpleExpression:
            return super().__new__(cls)
        try:
            if "=" in expr:
                return Assign(expr)
            elif expr.endswith("!"):
                return Toggle(expr)
            else:
                return Get(expr)
        except SyntaxError as e:
            text = expr + (f" ({e})" if str(e) != "None" else "")
            raise SyntaxError(text)


class Assign(SimpleExpression):
    def __init__(self, expr: str):
        _left, _right = expr.split("=", maxsplit=1)
        left = self._ast_name(_left).id
        variable = var_container[left]
        self.rhs = self._parse_rhs(_right, variable)
        self.var_name = left

    def execute(self):
        try:
            var_container[self.var_name].value = self.rhs
        except TemVariableValueError as e:
            e.name = self.var_name
            raise e
        print_name_value(self.var_name)


class Toggle(SimpleExpression):
    def __init__(self, expr: str):
        if not expr.endswith("!"):
            raise SyntaxError(expr)
        name = self._ast_name(expr[:-1]).id
        self.var_name = name
        self.variant = var_container[name]
        if not isinstance(self.variant, Variant):
            raise SyntaxError("only variants can be toggled")

    def execute(self):
        self.variant.value = not self.variant.value
        print_name_value(self.var_name)


class Get(SimpleExpression):
    def __init__(self, expr: str):
        self.var_name = self._ast_name(expr).id

    def execute(self):
        print_name_value(self.var_name)


class Query(Expression):
    def __init__(self, expr: str):
        try:
            if ":" not in expr:
                self.var_name = self._ast_name(expr).id
            else:
                _left, _right = expr.split(":", maxsplit=1)
                left = self._ast_name(_left).id
                self.var_name = left
                self.rhs = self._parse_rhs(
                    _right, variable=var_container[left]
                )
        except SyntaxError:
            raise SyntaxError(expr)

    def execute(self):
        variable = var_container[self.var_name]
        if not hasattr(self, "rhs"):
            # The expression is a name of a variable (must be a variant)
            if not isinstance(variable, Variant):
                raise SyntaxError(
                    f"{self.var_name} (only variants can be queried this way)"
                )
            if not variable.value:
                cli.exit_code = 1
        elif variable.value != self.rhs:
            cli.exit_code = 1

        if args.verbosity > 0:
            print_name_value(self.var_name, verbosity=args.verbosity - 1)


def parse_simple_expressions(expressions: Iterable[str]) -> List[Expression]:
    """
    Parse ``expressions`` and return a list of :class:`Expression` objects.
    Warnings will be emitted for each invalid expression.
    """
    result = []
    for expr in expressions:
        try:
            with handle_expression_exceptions():
                result.append(SimpleExpression(expr))
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
            val = repr(exc.value)
            raise SyntaxError(
                f"value {val} does not match type for variable '{exc.name}'"
            )


def process_simple_expressions():
    # An empty expressions CLI argument means get the values of all variables
    all_expressions = args.expressions or var_container
    expressions = parse_simple_expressions(all_expressions)
    any_succeeded = False
    for expr in expressions:
        try:
            with handle_expression_exceptions():
                expr.execute()
                any_succeeded = True
        except SyntaxError as e:
            cli.print_cli_warn(e)

    if all_expressions and not any_succeeded:
        # All expressions failed
        cli.print_cli_err("none of the specified expressions are valid")
        cli.exit_code = 1


def process_query_expressions():
    any_failed = False
    for expr in args.expressions:
        try:
            with handle_expression_exceptions():
                Query(expr).execute()
        except SyntaxError as e:
            cli.print_cli_err(e)
            any_failed = True

    if any_failed:
        cli.exit_code = 1


def reset_to_defaults():
    if not args.expressions:
        try:
            os.remove(TemDir()._internal / "vars")
        except FileNotFoundError:
            pass
        return
    # Validate that args.expressions contains only expressions of type `Get`
    for expr in args.expressions:
        try:
            with handle_expression_exceptions():
                get = SimpleExpression(expr)
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
        if k in args.expressions
    }
    # Possibly intercept (edit) the default values before committing them
    if args.edit or args.editor:
        initial_content = "\n".join(
            [f"{k} = {repr(value)}" for k, value in defaults.items()]
        )
        initial_content = (
            "# Change the variable values to your liking and save this file.\n"
            "# This file uses python syntax\n\n"
        ) + initial_content
        with cli.edit_tmp_file(
            suffix=".py", initial_content=initial_content
        ) as (_, path):
            mod = util.import_path("__tem_temporary_module", path)
            for attr, value in mod.__dict__.items():
                if not (attr.startswith("__") and attr.endswith("__")):
                    defaults[attr] = value

    # Commit the changes
    for var_name, default in defaults.items():
        old_value = var_container[var_name].value
        var_container[var_name].value = default
        if old_value != default or args.verbosity > 0:
            additional_args = (
                ["\033[1;33m\t| was:\033[0m", old_value]
                if args.verbosity >= 2
                else []
            )
            print_name_value(var_name, *additional_args, verbosity=0)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    globals()["args"] = args

    global var_container
    if args.defaults:
        pass
        # TODO process_
    else:
        var_container = var.load(defaults=args.defaults)

    if args.query:
        process_query_expressions()
    elif args.reset:
        reset_to_defaults()
    else:
        process_simple_expressions()

    var.save(var_container)
