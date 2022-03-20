"""
Template and Environment Manager API
"""
import os

from tem._meta import __prefix__, __version__

from .env import Environment
from .fs import TemDir

default_repo = os.path.expanduser("~/.local/share/tem/repo")
