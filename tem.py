#!/usr/bin/env python3

# This is a test script
# Run it when you need to quickly test new features during development -- so you
# don't have to install tem each time you make a change.

# `tem env` puts this script into the PATH while you are inside the project
# directory.

import sys, os
# Prepend PWD to the PATH so that local modules are used over the global ones
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tem import __main__ as main
sys.argv.insert(1, os.path.dirname(os.environ['TEM_EXECUTABLE']) + '/conf/config')
sys.argv.insert(1, '--config')
sys.argv.insert(1, '--reconfigure')
main.main()
