"""tem ls subcommand"""
import os
import subprocess as sp

from tem import ext, util
from tem import repo as repo_module
from tem.cli import common as cli

from ..repo import Repo


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    cli.add_general_options(parser)

    parser.add_argument(
        "-s",
        "--short",
        action="store_true",
        help="don't display headers and decorations",
    )
    parser.add_argument(
        "-p", "--path", action="store_true", help="print full path"
    )
    parser.add_argument(
        "-x", "--command", metavar="CMD", help="ls command to use"
    )
    parser.add_argument(
        "-n",
        "--number",
        metavar="N",
        type=int,
        help="list contents of no more than N repositories",
    )
    cli.add_edit_options(parser)

    recursion = parser.add_mutually_exclusive_group()
    recursion.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="recurse into subdirectories",
    )
    recursion.add_argument(
        "--norecursive",
        dest="recursive",
        action="store_false",
        help="do not recurse into subdirectories [default]",
    )

    parser.add_argument(
        "templates",
        metavar="TEMPLATES",
        nargs="*",
        help="which templates to list",
    )
    # TODO is there a way to show a '--' in the usage synopsis? I tried this
    # but '--' shows up at the end of help (argparse.SUPPRESS doesn't help
    # either) Also I would like this to show up after templates and before
    # ls_arguments
    #  ATTEMPT: p.add_argument('--', action='store_true', dest='__discard')
    parser.add_argument(
        "ls_arguments",
        metavar="LS_ARGUMENTS",
        nargs="*",
        help="additional arguments that will be passed to ls",
    )


def separate_files_and_options(args):
    """
    Take a list of arguments and separate out files and options. An option is
    any string starting with a '-'. File arguments are relative to the current
    working directory and they can be incomplete.
    Returns:
        a tuple (file_list, option_list)
    """
    file_args = []
    opt_args = []

    for arg in args:
        if arg and arg[0] != "-":
            file_args.append(arg)
        else:
            opt_args.append(arg)
    return file_args, opt_args


# TODO Currently matches files that start with the incomplete_path entries
# I might try to make it more sophisticated some day
def fill_in_gaps(incomplete_paths):
    """
    Take all paths from `incomplete_paths` and complete them to match actual
    files. Returns a list that contains the completed paths.
    """

    paths = []
    for arg in incomplete_paths:
        paths += sp.run(
            ["sh", "-c", 'printf "%s\n" ' + arg + "*"],
            stdout=sp.PIPE,
            encoding="utf-8",
            check=False,
        ).stdout.split("\n")[:-1]
    return [p for p in paths if os.path.exists(p)]


def print_repo_header(repo: Repo):
    name = repo.name()
    path = repo.abspath()
    if os.isatty(1):
        print("\033[1;32m" + name + " @ " + "\033[0;4;32m" + path + "\033[0m")
    else:
        print("# " + name + " @ " + path)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""

    ls_args = args.templates + args.ls_arguments

    edit_files = []  # Files that will be edited if --edit[or] was provided
    original_cwd = os.getcwd()
    # TODO Make it so that ls is always displayed per-file, so that other file
    # info can be appended or prepended on each line
    for i, repo in enumerate(args.repo):
        os.chdir(repo.abspath())
        file_args, opt_args = separate_files_and_options(ls_args)
        # Any missing file extensions are filled in here
        # TODO Check for excluded files
        files = fill_in_gaps(file_args)
        if not any(os.scandir()) or (file_args and not files):
            continue  # Nothing to show in this repo
        if args.path:
            files = [os.path.abspath(f) for f in files]
        cmd_args = ["ls"] + opt_args + files
        p = ext.run(
            cmd_args,
            override=args.command,
            encoding="utf-8",
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        if args.edit or args.editor:
            edit_files += [os.path.abspath(f) for f in files]
        # Print what the command spit out
        if p.returncode != 0:
            if p.stdout:
                print(p.stdout)
            if p.stderr:
                cli.print_cli_err(p.stderr)
            return
        if not args.short:
            print_repo_header(repo)
        if p.stdout:
            print(p.stdout[:-1])
        if p.stderr:
            cli.print_cli_err(p.stderr)

        if args.number and i >= args.number - 1:  # --number option
            break

    os.chdir(original_cwd)

    if edit_files:
        cli.edit_files(edit_files)
