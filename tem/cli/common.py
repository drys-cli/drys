"""Common functions for most CLI subcommands."""
import argparse
import os
import re
import shutil
import subprocess
import sys
import glob

from .. import config, ext, repo, util
from ..util import print_err
from . import common as cli


def load_system_config():
    """
    Load configuration from ``system_config_paths``. If any of the files
    cannot be read, print an error and exit.
    """
    failed = config.load(config.SYSTEM_PATHS)
    if failed:
        print_cli_err(
            "the following system configuration files could not be read:",
            *failed,
            sep="\n\t",
        )
        sys.exit(1)


def load_user_config():
    """
    Load configuration from :data:`config.USER_PATHS`. If some of the files
    can't be read, print a warning.
    """
    failed = config.load(config.USER_PATHS)
    if len(failed) == len(config.USER_PATHS):
        print_cli_warn("no user configuration files could not be read:")
        print_cli_warn("The following files were tried:", *failed, sep="\n\t")


def load_config_from_args(args):
    """
    Load configuration files specified as command arguments in ``args``.
    If any of the files can't be read, print an error and exit."""
    failed = config.load(args.config)
    if failed:
        print_cli_err(
            "the following configuration files could not be read:",
            *failed,
            sep="\n\t",
        )
        sys.exit(1)


def add_general_options(parser, dummy=False):
    """
    Add options that are common among various commands. By default, when a
    subcommand is called, all options that are defined for the main command are
    valid but they must be specified before the subcommand name. By using this
    function with each subcommand, the option can be specified after the
    subcommand name.
    """
    # TODO remove this after a tryout period
    group = parser.add_argument_group("general options")
    group.add_argument(
        "-h",
        "--help",
        action=("store_true" if dummy else "help"),
        help="show this help message and exit",
    )
    group.add_argument(
        "-R",
        "--repo",
        action="append",
        default=[],
        help="use the repository REPO",
    )
    group.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        action="append",
        default=[],
        help="use configuration from FILE",
    )


def add_edit_options(parser):
    """Add `--edit` and `--editor` options to ``parser``."""
    parser.add_argument(
        "-e",
        "--edit",
        action="store_true",
        help="open target files for editing",
    )
    parser.add_argument(
        "-E", "--editor", help="same as -e but override editor with EDITOR"
    )


def existing_file(path):
    """Type check for ArgumentParser"""
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(path + " does not exist")
    return path


def resolve_and_validate_repos(repo_args):
    """
    Form a list of repo IDs that shall be used in the currently running
    subcommand. Repos from `repo_args` are arguments to the `--repo` options
    passed to the subcommand. Every applicable repository is considered,
    including those from any applicable configuration files. A repo id can be a
    repo name, a path or a special character (see manpages).
    """
    repo_ids = []

    # Parse arguments into a suitable list of entries
    if repo_args:  # repos specified with -R/--repo option
        include_def_repos = False
        read_from_stdin = False
        for r in repo_args:
            if r == "/":  # '/' is a special indicator
                include_def_repos = True
            elif "\n" in r:  # multiline text, each line is a repo id
                repo_ids += [line for line in r.split("\n") if line != ""]
            elif r == "-":  # Repos will be taken from stdin as well
                read_from_stdin = True
            else:  # Regular repo id, just add it
                repo_ids.append(r)
        if include_def_repos:  # Include default repos
            repo_ids += repo.repo_path
        if read_from_stdin:
            try:
                while True:  # Read repos until empty line or EOF
                    line = input()
                    if line == "":
                        break
                    repo_ids.append(line)
            except EOFError:
                pass
    else:  # No repos were specified by -R/--repo
        repo_ids = repo.repo_path

    # Resolve the entries to valid file-like objects
    resolved_repos = []  # this will be returned
    any_repo_valid = False  # indicates if any repo_ids are valid
    for r in repo_ids:
        if os.path.exists(r := util.resolve_repo(r)):
            any_repo_valid = True
            resolved_repos.append(r)
        else:
            print_cli_warn("repository '{}' not valid".format(r))
    if not any_repo_valid:
        print_cli_err("no valid repositories")
        sys.exit(1)

    return resolved_repos


def get_editor(override=None, default="vim"):
    """
    Get the editor that should be used to open files when `--edit` or
    `--editor` are used. Uses the fallback mechanism that is documented in
    tem(1).
    """
    editors = [
        override,
        config.cfg["general.editor"],
        os.environ.get("EDITOR") if os.environ.get("EDITOR") else None,
        os.environ.get("VISUAL") if os.environ.get("VISUAL") else None,
        default,
    ]
    return next(ed for ed in editors if ed)


def try_open_in_editor(files, override_editor=None):
    """
    Open `files` in editor. If `override_editor` is specified then that is
    used. Otherwise, the editor is looked up in the configuration. The editor
    can be any string that the shell can parse into a list of arguments (e.g.
    'vim -o' is valid). If the editor cannot be found, print an error and exit.
    """
    call_args = ext.parse_args(get_editor(override_editor)) + files

    if not shutil.which(call_args[0]):
        print(
            "tem config: error: invalid editor: '" + call_args[0] + "'",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        p = subprocess.run(call_args, check=False)
        return p
    except Exception as e:
        cli.print_error_from_exception(e)
        sys.exit(1)


def run_hooks(trigger, src_dir, dest_dir=".", environment=None):
    """For reference look at tem-hooks(1) manpage."""

    src_dir = util.abspath(src_dir)

    # Setup environment variables that the hooks can use
    if environment is not None:
        if "TEM_TEMPLATEDIR" not in environment:
            environment["TEM_TEMPLATEDIR"] = src_dir
        environment["PATH"] = src_dir + "/.tem/path:" + os.environ["PATH"]
        for var, value in environment.items():
            os.environ[var] = value

    os.makedirs(dest_dir, exist_ok=True)

    with util.chdir(dest_dir):
        # Execute matching hooks
        for file in glob.glob(src_dir + "/.tem/hooks/*.{}".format(trigger)):
            subprocess.run(
                [file] + sys.argv, cwd=os.path.dirname(file), check=False
            )


def expand_alias(index, args):
    """
    Expand alias in ``args`` and return the modified argument list.
    :param index: the index of the argument that is to be expanded as an alias
        If the argument isn't aliased to anything, the list is returned
        unmodified.
    :param args: list of command arguments
    """
    alias = args[index]
    aliased = config.cfg["alias.%s" % alias]

    if not aliased:  # No alias found in config
        return args

    expanded_alias = ext.shell_arglist(aliased)  # Expand alias into arg list
    if index == -1:
        args[-1:] = expanded_alias
    else:
        args[index : index + 1] = expanded_alias

    return args


# Used only in print_cli_err and print_cli_warn
_active_subcommand = ""


def set_active_subcommand(subcommand):
    """
    Set the name of the active subcommand. This is used when reporting errors
    and warnings.
    """
    global _active_subcommand
    _active_subcommand = subcommand


def print_cli_err(*args, sep=" ", **kwargs):
    """
    Print an error with conventional formatting. The first line starts with
    '<subcommand>: error:'.
    """
    print_err("tem " + _active_subcommand + ": error: ", end="", **kwargs)
    print_err(*args, sep=sep, **kwargs)


def print_cli_warn(*args, sep=" ", **kwargs):
    """
    Print a warning with conventional formatting. The first line starts with
    '<subcommand>: warning:'.
    """
    print_err("tem " + _active_subcommand + ": warning: ", end="", **kwargs)
    print_err(*args, sep=sep, **kwargs)


def print_cli_info(*args, sep=" ", **kwargs):
    """
    Print an info message with conventional formatting. The first line starts
    with '<subcommand>: info:'.
    """
    print_err("tem " + _active_subcommand + ": info: ", end="", **kwargs)
    print_err(*args, sep=sep, **kwargs)


def print_error_from_exception(exception):
    """
    Take the python exception ``e``, strip it of unnecessary text and print it
    as a CLI error.
    """
    print_cli_err(re.sub(r"^\[Errno [0-9]*\] ", "", str(exception)))


def copy(*args, ignore_nonexistent=False, **kwargs):
    """
    CLI front end to :func:`util.copy`.
    If an error occurs and ``ignore_nonexistent`` is ``True``, print an error
    and exit.
    """
    try:
        util.copy(*args, **kwargs)
    except Exception as exception:
        # TODO use more specific error
        if not ignore_nonexistent:
            print_error_from_exception(exception)
            sys.exit(1)


def move(*args, ignore_nonexistent=False, **kwargs):
    """
    CLI front end to :func:`util.move`.
    If an error occurs and ``ignore_nonexistent`` is ``True``, print an error
    and exit.
    """
    try:
        util.move(*args, **kwargs)
    except Exception as exception:
        # TODO use more specific error
        if not ignore_nonexistent:
            print_error_from_exception(exception)
            sys.exit(1)


def remove(path):
    """CLI front end to :func:`util.remove`"""
    try:
        util.remove(path)
    except Exception as exception:
        # TODO use more specific error
        print_error_from_exception(exception)
        sys.exit(1)
