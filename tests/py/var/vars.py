# Copied over to a .tem/vars.py file in a test

from tem.var import Variable, Variant

build_type = Variable(["release", "debug"], default="release")
production = Variant()
