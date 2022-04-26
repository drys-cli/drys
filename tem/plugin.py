"""Interact with user plugins"""
import glob
import os
import re

from .util import import_path


def load_all():
    """Load plugins from all applicable locations."""
    # TODO load plugins from default system directories
    # TODO handle plugin name conflict with existing tem subcommands
    if os.path.isdir(".tem/plugin"):
        plugins = []
        for plugin_file in glob.glob(".tem/plugin/*.py"):
            plugin_name = re.sub(r"\.py$", "", os.path.basename(plugin_file))
            plugin = import_path(plugin_name, plugin_file)
            plugins.append(plugin)
        return plugins
    return []
