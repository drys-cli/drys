"""Common functions for most CLI subcommands."""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

from .. import config, ext, util, repo
from ..repo import RepoSpec
from ..util import print_err


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


def subcommand(cmd):
    """Decorator for tem subcommand functions"""

    def wrapper(args):
        # Transform RepoSpecs into absolute paths
        global repo
        repo.lookup_path = args.repo.repos()
        args.repo = args.repo.repos()
        for repo in args.repo:
            if not os.path.isdir(repo.abspath()):
                print_cli_err("repository '%s' does not exist" % repo)
                sys.exit(1)
        return cmd(args)

    return wrapper


def add_general_options(parser, dummy=False):
    """
    Add options that are common among various commands. By default, when a
    subcommand is called, all options that are defined for the main command are
    valid but they must be specified before the subcommand. By using this
    function on each subcommand parser, the option can be specified after the
    subcommand name as well.
    """
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
        default=RepoSpec(),
        action="append",
        type=RepoSpec,
        help="use the repository REPO",
    )
    group.add_argument(
        "-R%",
        dest="repo",
        default=RepoSpec(),
        action="append_const",
        const=RepoSpec(RepoSpec.FROM_LOOKUP_PATH),
        help=argparse.SUPPRESS,
    )
    group.add_argument(
        "-R!",
        dest="repo",
        default=RepoSpec(),
        action="append",
        type=RepoSpec.of_type(RepoSpec.EXCLUDE),
        help=argparse.SUPPRESS,
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
        print_error_from_exception(e)
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


def set_active_subcommand(subcmd):
    """
    Set the name of the active subcommand. This is used when reporting errors
    and warnings.
    """
    global _active_subcommand
    _active_subcommand = subcmd


def print_cli_err(*args, sep=" ", **kwargs):
    """
    Print an error with conventional formatting. The first line starts with
    '<subcommand>: error:'.
    """
    kwargs1 = kwargs.copy()
    kwargs1["end"] = ""
    print_err("tem " + _active_subcommand + ": error: ", **kwargs1)
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
