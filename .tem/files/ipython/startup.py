# Startup file for python interpreter started in the local directory

import os
import sys
from tem.fs import TemDir

class __private:
    user_startup = os.environ.get("__PYTHONSTARTUP_DEFAULT")

if __private.user_startup:
    exec(open(__private.user_startup).read())

del __private

# Load temporary startup file
exec(open(os.path.dirname(os.path.abspath(__file__)) + "/startup.tmp.py").read())
