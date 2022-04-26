"""Representations for expressions used with the `tem var` command."""
import ast
from itertools import dropwhile, cycle
from abc import ABC

from tem.errors import TemVariableValueError
from tem.var import Variable, VariableContainer, Variant
from tem.cli import common as cli


class Expression:
    """
    Represents any expression supported by the `tem var` command. Subclasses
    must raise a `SyntaxError` on any expected error, with an optional error
    message as its argument. All other errors will be considered bugs.
    """

    var_name: str = None
    variable: Variable = None

    @classmethod
    def _ast_parse(cls, expr: str) -> ast.stmt:
        try:
            parsed = ast.parse(expr)
            if len(parsed.body) != 1:
                raise SyntaxError
        except SyntaxError:
            raise SyntaxError from None
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
                raise SyntaxError from None

    @property
    def value(self):
        """Get variable value."""
        return self.variable.value

    def execute(self):
        """Execute the action associated with the expression."""


class SimpleExpression(Expression, ABC):
    """Represents a single variable get, assign or toggle expression."""

    def __new__(cls, expr: str, var_container: VariableContainer):
        if cls != SimpleExpression:
            return super().__new__(cls)
        try:
            if "=" in expr:
                return Assign(expr, var_container)
            elif expr.endswith("!"):
                return Cycle(expr, var_container)
            else:
                return Get(expr, var_container)
        except SyntaxError as e:
            text = expr + (f" ({e})" if str(e) != "None" else "")
            raise SyntaxError(text) from None


class Assign(SimpleExpression):
    """A variable assignment expression of the form `variable=value`."""

    def __init__(self, expr: str, var_container: VariableContainer):
        _left, _right = expr.split("=", maxsplit=1)
        left = self._ast_name(_left).id
        variable = var_container[left]
        self.rhs = self._parse_rhs(_right, variable)
        self.var_name = left
        self.variable = var_container[self.var_name]

    def execute(self):
        try:
            self.variable.value = self.rhs
        except TemVariableValueError as e:
            e.name = self.var_name
            raise e

    @classmethod
    def from_pair(cls, var_name, value, var_container):
        """
        Create an Assign expression for a variable from ``var_container``
        named ``var_name`` to value ``value``.
        """
        expr = Assign("dummy=1", VariableContainer({"dummy": Variable(int)}))
        expr.var_name = var_name
        expr.rhs = value
        expr.variable = var_container[expr.var_name]
        return expr


class Cycle(SimpleExpression):
    """Expression for cycling among a variable's allowed values."""

    def __init__(self, expr: str, var_container: VariableContainer):
        if not expr.endswith("!"):
            raise SyntaxError(expr)
        name = self._ast_name(expr[:-1]).id
        self.var_name = name
        self.variable = var_container[name]
        if not isinstance(self.variable, Variant) and not isinstance(
            self.variable.var_type, list
        ):
            raise SyntaxError(
                "only variables with a finite set of values can be cycled"
            )

    def execute(self):
        if self.variable.var_type == bool:
            self.variable.value = not self.variable.value
        else:
            values = cycle(self.variable.var_type)
            iter_values = dropwhile(
                lambda x: not x == self.variable.value, values
            )
            next(iter_values)
            self.variable.value = next(iter_values)


class Get(SimpleExpression):
    """
    A get expression, simply corresponds to a variable name specified on the
    command line.
    """

    def __init__(self, expr: str, var_container: VariableContainer):
        self.var_name = self._ast_name(expr).id
        self.variable = var_container[self.var_name]


class Query(Expression):
    """A query expression (used with the `--query` flag)"""

    def __init__(self, expr: str, var_container):
        try:
            if ":" not in expr:
                # Colon is used to query the value of a regular variable
                self.var_name = self._ast_name(expr).id
            else:
                # A variant can be queried by specifying its name alone
                _left, _right = expr.split(":", maxsplit=1)
                left = self._ast_name(_left).id
                self.var_name = left
                self.rhs = self._parse_rhs(
                    _right, variable=var_container[left]
                )
            self.variable = var_container[self.var_name]
        except SyntaxError:
            raise SyntaxError(expr) from None

    def execute(self):
        if not hasattr(self, "rhs"):
            # The expression is a name of a variable (must be a variant)
            if not isinstance(self.variable, Variant):
                raise SyntaxError(
                    f"{self.var_name} (only variants can be queried this way)"
                )
            if not self.variable.value:
                cli.exit_code = 1
        elif self.variable.value != self.rhs:
            cli.exit_code = 1
