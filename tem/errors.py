"""Tem error definitions."""

# pylint: disable=missing-class-docstring,missing-function-docstring

import inspect
import os

from tem.util import abspath, print_err


class TemError(Exception):
    """Base class for all tem errors."""

    _brief = "an unknown error has occured"

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._additional_text = ""
        if not args:
            self._brief = __class__._brief
        elif isinstance(args[0], str):
            self._brief = args[0]

    def cli(self):
        """The error text to print if the CLI is active."""
        return self._brief

    def append(self, text):
        """Append additional text to the error."""
        self._additional_text += f"{text}"
        return self

    def print(self):
        """Print the error to the CLI."""
        # pylint: disable-next=import-outside-toplevel
        from tem.cli.common import print_cli_err

        print_cli_err(self.cli())
        print_err(self._additional_text)

    def __str__(self):
        return self._brief


class PathError(TemError):
    """An error that has a path as an argument."""

    def __init__(self, path):
        super().__init__(self, path)
        self.path = path


class RepoDoesNotExistError(PathError):
    def cli(self):
        return f"repository '{self.path}' does not exist"


class FileNotFoundError(PathError):  # pylint: disable=redefined-builtin
    def cli(self):
        return f"file '{abspath(self.path)}' was not found"


class ProgramNotFoundError(PathError):
    def cli(self):
        return f"program '{self.path}' was not found"


class DirNotFoundError(PathError):
    def cli(self):
        return f"directory '{abspath(self.path)}' was not found"


class FileNotDirError(PathError):
    def cli(self):
        return f"'{abspath(self.path)}' exists and is not a directory"


# pylint: disable-next=redefined-builtin
class FileExistsError(PathError):
    def cli(self):
        return f"file '{abspath(self.path)}' already exists"


class NotADirError(PathError):
    def cli(self):
        return f"'{abspath(self.path)}' is not a directory"


class NotATemDirError(PathError):
    def cli(self):
        return (
            f"'{abspath(self.path)}' is not a temdir\n"
            f"Try running `tem init` first."
        )


class NoTemDirInHierarchy(PathError):
    def cli(self):
        return f"no temdir in filesystem hierarchy of '{abspath(self.path)}'"


class TemInitializedError(PathError):
    """Note: the argument is the path to the temdir."""

    def cli(self):
        text = "'.tem' already exists"
        if not os.path.isdir(self.path):
            text += " and is not a directory"
        return text


class TemLookupError(TemError):
    """Base class for errors related to lookup."""

    def __init__(self, *args):  # pylint: disable=super-init-not-called
        # pylint: disable-next=non-parent-init-called
        Exception.__init__(self, *args)


class RepoNotFoundError(TemLookupError):
    def __init__(self, repo_name):
        super().__init__(self)
        self.repo_name = repo_name

    def cli(self):
        return f"repository '{self.repo_name}' not found"


class TemplateNotFoundError(TemError):
    def __init__(self, template_name):
        super().__init__(self, template_name)
        self.template_name = template_name

    def cli(self):
        return (
            f"template '{self.template_name}' could not be found in the "
            "available repositories"
        )


class NotARunnable(TemError):
    # pylint: disable-next=useless-super-delegation
    def __init__(self, path):
        super().__init__(path)


# tem.var


class TemVariableValueError(TemError, ValueError):
    def __init__(self, *args, name=None, value=None):
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value
        super().__init__(*args)

    def cli(self):
        return "variable value must match variable type"


class TemVariableNotDefinedError(TemError):
    def __init__(self, name=None):
        if name is not None:
            self.name = name
        super().__init__()

    def cli(self):
        return (
            f"variable '{self.name}' is not defined"
            if self.name
            else "variable is not defined"
        )


#: Tuple of all tem error classes
all_errors = tuple(
    obj
    for obj in globals().values()
    if inspect.isclass(obj) and issubclass(obj, TemError)
)
