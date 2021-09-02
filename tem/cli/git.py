"""tem git subcommand"""
import subprocess as sp
import sys
import re

from . import common as cli
from .. import config


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    cli.add_general_options(parser)

    grp = parser.add_mutually_exclusive_group()
    grp.add_argument(
        "-C",
        "--checkout",
        action="store_true",
        help="load work environment from git (default)",
    )
    grp.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list files that would be added by --checkout",
    )

    parser.add_argument(
        "-b", "--branch", help="git branch that contains tem files"
    )

    parser.set_defaults(func=cmd)


def _run_that_must_succeed(*args, **kwargs):
    """
    Helper function that does the same as `subprocess.run`, but exits if the
    subprocess returns an error code.
    """
    p = sp.run(*args, check=False, **kwargs)
    if p.returncode != 0:
        sys.exit(1)
    return p


def get_current_branch():
    """Call git to get the checked out branch."""
    p = _run_that_must_succeed(
        ["git", "branch", "--show-current"], stdout=sp.PIPE, encoding="utf-8"
    )
    return p.stdout[:-1]  # Remove newline at end


def get_tem_branch():
    """
    Get the tem branch from the current git repository.
    Git is called to obtain a list of branches.
    """

    # Obtain branches from git and filter them
    p = _run_that_must_succeed(
        ["git", "branch"], stdout=sp.PIPE, encoding="utf-8"
    )
    branches = p.stdout[:-1].split("\n")
    branches = [
        b[2:] for b in branches if re.match("^  tem($|[^a-zA-Z].*)", b)
    ]

    # Handle special cases
    if p.returncode != 0:
        sys.exit(p.returncode)
    elif not branches:  # No available branches
        cli.print_cli_err("current branch is the only branch")
        sys.exit(1)
    elif len(branches) == 1:  # Single available branch
        return branches[0]
    # Prompt the user for a choice
    print("The following branches are available:")
    for i, b in enumerate(branches):
        print("{})".format(i + 1), b)
    choice = input("Enter a choice (default: 1): ")

    if not choice:  # Default choice
        return branches[0]
    # Verify and convert the choice
    try:
        choice = int(choice)
    except ValueError:
        cli.print_cli_err("invalid choice")
        sys.exit(1)
    if choice < 1 or choice > len(branches):
        cli.print_cli_err("invalid choice")
        sys.exit(1)

    return branches[choice - 1]


def ls_branch(branch):
    """Get a list of versioned files in the checked out git branch."""
    p = _run_that_must_succeed(
        ["git", "ls-tree", "-r", "--name-only", branch],
        stdout=sp.PIPE,
        encoding="utf-8",
    )
    ls = p.stdout[:-1]  # Remove newline at end
    return ls.split("\n")


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    if not args.list:
        args.checkout = True
    # Obtain current branch
    cur_branch = get_current_branch()
    # First we try to take `tem_branch` from arguments or from config
    tem_branch = (
        args.branch if args.branch else config.cfg["git.default_branch"]
    )
    # Then we check that it is a valid branch (must not be the active branch)
    p = _run_that_must_succeed(
        ["git", "branch"], encoding="utf-8", stdout=sp.PIPE
    )
    valid_branches = [
        b[2:] for b in p.stdout[:-1].split("\n") if b[0:1] != "* "
    ]

    # Note: tem_branch == '' is treated as tem_branch == None
    if tem_branch and tem_branch not in valid_branches:
        print("tem: error: branch '{}' not valid".format(tem_branch))
    # As a fallback, we try to find branches whose names start with 'tem'.
    # Actually, the regex pattern is slightly more complicated than that.
    if not tem_branch:
        tem_branch = get_tem_branch()

    # Obtain lists of versioned files in current and tem branch
    ls_cur = ls_branch(cur_branch)
    ls_tem = ls_branch(tem_branch)

    # Files that are in tem branch but are not in current branch get placed
    # into the working tree
    extra_files = list(set(ls_tem) - set(ls_cur))
    if args.list:
        print(*sorted(extra_files), sep="\n")
    else:
        p = _run_that_must_succeed(
            ["git", "restore", "-s", tem_branch] + extra_files
        )
