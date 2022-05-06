# pylint: skip-file

"""Utilities for accessing dotdirs."""
import os

# FIXME fix this file


class hooks(Dir):
    """Representation of a .tem/hooks subdirectory."""

    @staticmethod
    def filter(trigger: str):
        """Return a subset of hooks by trigger"""


class path(Dir):
    """Representation of a .tem/path subdirectory."""

    def __init__(self, temdir):

    @staticmethod
    def executables():
        """Return all executables that can be run by tem"""
        return (
            Executable() for file in Dir().scan()
        )
