from tem.var import Variable, Variant

# TODO implement this functionality

use_pipenv = Variant(True)
env = Variable(["prod", "dev"], default="dev")
test1 = Variable(str, default="n")
anyv = Variable()

use_pipenv.doc = "Whether to run all python modules in a pipenv."
