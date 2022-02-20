# Copied over to a .tem/vars.py file in a test

from tem.var import Variable, Variant

str1 = Variable(["val1", "val2"], default="val1")
str2 = Variable(["val3", "val4"], default="val3")
bool1 = Variant()
bool2 = Variant(default=True)
