from tem.var import Variable, Variant

# TODO implement this functionality

use_pipenv = Variant(False)
env = Variable(["prod", "dev"], default="dev", from_env="ENV")
test1 = Variable(str, default="n")
anyv = Variable()

use_pipenv.doc = "Whether to run all python modules in a pipenv."
