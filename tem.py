#!/usr/bin/env python3
"""
Test script for development purposes Run this when you need to quickly test new
features during development -- so you don't have to re-install tem each time
you make a change to test it.

If you have a shell plugin installed, running `tem env` puts this script into
the PATH while you are inside the project directory. That way, simply running
`tem` will run this script instead of the one installed on your system (or for
your user).
"""

import os
import sys
import shutil as sh
from tem import __main__ as main


executable_dir = os.path.abspath(__file__)
if d := os.environ.get("TEM_EXECUTABLE"):
    executable_dir = d
executable_dir = os.path.dirname(executable_dir)

# Prepend PWD to the PATH so that local modules are used over the global ones
sys.path.insert(0, executable_dir)

# Create a temporary configuration
config_dir = f"{executable_dir}/.tem/tmp"
os.makedirs(config_dir, exist_ok=True)
sh.copy(f"{executable_dir}/conf/config", config_dir)

sys.argv.insert(1, f"{config_dir}/config")
sys.argv.insert(1, "--config")
main.main()
