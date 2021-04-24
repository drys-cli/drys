#!/usr/bin/env python3

# This is a test script
# Run it when you need to quickly test new features during development -- so you
# don't have to install drys each time you make a change.

import sys, os
# Prepend PWD to the PATH so that local modules are used over the global ones
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from drys import __main__ as main
main.main()
