#!/usr/bin/env python3
"""Test script for development purposes.

Run this when you need to quickly test new features during development -- so you
don't have to re-install tem each time you make a change to test it.

If you have a shell plugin installed, running `tem env` puts this script into
the `PATH` while you are inside the project directory. That way, simply running
`tem` will run this script instead of the one installed on your system (or what
the user has in their `PATH`).
"""

import os
import sys
import shutil as sh
import tem
from tem import __main__ as main


tem.__version__ = "develop"

tem_projectroot = next(
    x
    for x in (
        os.environ.get("TEM_PROJECTROOT"),
        os.path.dirname(os.path.abspath(__file__)),
    )
    if x
)

os.environ["TEM_PROJECTROOT"] = tem_projectroot

# Prepend PWD to the PATH so that local modules are used over the global ones
sys.path.insert(0, tem_projectroot)

# Create a temporary configuration
config_dir = f"{tem_projectroot}/.tem/tmp"
os.makedirs(config_dir, exist_ok=True)
sh.copy(f"{tem_projectroot}/share/config", config_dir)

sys.argv.insert(1, f"{config_dir}/config")
sys.argv.insert(1, "--config")
main.main()
