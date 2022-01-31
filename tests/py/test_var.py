import pytest
import tem.find
from tem import var
from common import *  # isort: skip


class TestVar:
    def test_variable_constructor(self):
        # Integer, take default value for that type
        v = var.Variable(int)
        assert v.value == 0
        # String with explicit default value
        v = var.Variable(str, default="default")
        assert v.value == "default"
        # Variable with a list of allowed values, no explicit default
        v = var.Variable([1, "2", True])
        assert v.value == 1
        # Variable with a list of allowed values, with explicit default
        v = var.Variable([1, "2", True], True)
        assert v.value
        v = var.Variable()
        assert v.value is None
        # Variable with Any type, with explicit default
        v = var.Variable(default=10)
        assert v.value == 10
        # Variant initialized directly
        v = var.Variant()
        assert not v.value and v.var_type == bool
        # Variant instantiated from Variable.__new__
        v = var.Variable(bool)
        assert isinstance(v, var.Variant)

    def test_errors(self):
        # Variable type is not a type or list of values
        with pytest.raises(TypeError):
            var.Variable("type")
        # Unmatched variable type and default value
        with pytest.raises(ValueError):
            var.Variable(bool, 1)
        v = var.Variable(bool)
        # Calling setter with unmatched var_type (type is a python type)
        with pytest.raises(ValueError):
            v.value = 1
        # Calling setter with unmatched type (type is a list of values)
        v = var.Variable([1, "2", 3.0])
        with pytest.raises(ValueError):
            v.value = 4
        # Both default and from_env specified

    def test_var_decorator(self):
        pass
