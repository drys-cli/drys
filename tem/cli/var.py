"""Manipulate tem variants."""
import ast
import textwrap
from abc import ABC

from tem import var
from tem.cli import common as cli
from tem.errors import TemVariableValueError

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
        help="do not read stored values, only defaults",
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

    p.set_defaults(func=cmd)


def no_action_specified():
    return not args.active and not args.query


def print_doc(variable: Variable):
    """Print documentation for ``variable``, indented for readability."""
    if variable.__doc__:
        print(
            textwrap.TextWrapper(
                initial_indent="    ", subsequent_indent="    "
            ).fill(variable.__doc__)
        )


def print_name_value(var_name, verbosity=None):
    """
    Print name and value for variable in :data:`var_container` named
    ``var_name``. Also print documentation if args contain --verbose.
    """
    variable = var_container[var_name]
    print(var_name, "=", repr(variable.value))

    verbosity = verbosity if verbosity is not None else args.verbosity
    if verbosity > 0:
        print_doc(variable)


class Expression:
    """
    Represents any expression supported by the `tem var` command. Subclasses
    must raise a `SyntaxError` on any error, with an optional error message as
    its argument.
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
                self.rhs = self._parse_rhs(_right, variable=var_container[left])
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


def process_default_expressions():
    any_successful = False
    all_variable_names = args.expressions or var_container
    for expr in all_variable_names:
        try:
            with handle_expression_exceptions():
                SimpleExpression(expr).execute()
                any_successful = all_variable_names
        except SyntaxError as e:
            cli.print_cli_warn(e)

    if not any_successful and all_variable_names:
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


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    globals()["args"] = args

    global var_container
    var_container = var.load()

    if no_action_specified():
        process_default_expressions()
    elif args.query:
        process_query_expressions()
    var.save(var_container)
