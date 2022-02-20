import pytest

from tem import var
from tem import errors
from tem.fs import TemDir
from common import *

TEMDIR = OUTDIR / "var/temdir"


class TestVar:
    @classmethod
    def setup_class(cls):
        recreate_dir(TEMDIR)
        cls.temdir = TemDir.init(TEMDIR)

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
        with pytest.raises(errors.TemVariableValueError):
            var.Variable(bool, 1)
        v = var.Variable(bool)
        # Calling setter with unmatched var_type (type is a python type)
        with pytest.raises(errors.TemVariableValueError):
            v.value = 1
        # Calling setter with unmatched type (type is a list of values)
        v = var.Variable([1, "2", 3.0])
        with pytest.raises(errors.TemVariableValueError):
            v.value = 4
        # Both default and from_env specified

    def test_variable_container_utility_functions(self):
        """TODO"""

    def test_variable_container(self):
        v = var.VariableContainer()
        assert len(v) == 0

        v1 = var.VariableContainer(dict(a=var.Variant(), b=var.Variant()))
        assert type(v1["a"]) == var.Variant and type(v1["b"]) == var.Variant

        v2 = var.VariableContainer(dict(a=var.Variant(), b=1))
        assert len(v2) == 1  # b is not a Variant so it's filtered out
        assert type(v2["a"]) == var.Variant

        v3 = var.VariableContainer(dict(a=var.Variant()))
        assert type(v3.a) == bool and type(v3["a"]) == var.Variant
        assert not v3.a  # default variant value is False

        v3.a = True
        assert v3.a is v3["a"].value
        assert v3.a

    def test_load_save(self):
        shutil.copy(TESTDIR / "var/vars.py", self.temdir / ".tem")

        v = var.load(self.temdir)
        assert not v.bool1
        assert v.str1 == "val1"

        v.bool1 = True
        v.str1 = "val2"
        assert v.bool1 and v.str1 == "val2"

        var.save(v, self.temdir)
        v1 = var.load(self.temdir)
        assert v1.bool1 and v1.str1 == "val2"

        v2 = var.load(self.temdir, defaults=True)
        assert not v2.bool1
        assert v2.str1 == "val1"

        with pytest.raises(TypeError):
            var.load(self.temdir.parent / "nonexistent_temdir")

    def test_load_from_env(self):
        """TODO"""
