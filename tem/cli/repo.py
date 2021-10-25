"""tem repo subcommand"""
import os
import sys

from .. import config, util, repo as repo_module
from . import common as cli
from . import config as config_cli

from ..repo import (
    Repo,
    resolve as resolve_repo,
)


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    cli.add_general_options(parser)

    parser.add_argument(
        "-l", "--list", action="store_true", help="list REPOSITORIES"
    )
    parser.add_argument(
        "-n", "--name", action="store_true", help="print the repository name"
    )
    parser.add_argument(
        "-p", "--path", action="store_true", help="print the repository path"
    )

    add_rem = parser.add_mutually_exclusive_group()
    add_rem.add_argument(
        "-a",
        "--add",
        action="store_true",
        help="add REPOSITORIES to REPO_PATH",
    )
    add_rem.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="remove REPOSITORIES from REPO_PATH",
    )

    parser.add_argument(
        "repositories",
        metavar="REPOSITORIES",
        type=Repo,
        nargs="*",
        help="repository paths, partial paths or names",
    )

    parser.set_defaults(func=cmd)


# TODO Make a function that just returns the string
def print_repo(repo: Repo, args):
    """
    Print the title line for a repository. Takes CLI arguments ``args`` into
    account.
    """
    # TODO align output, too lazy at the moment
    def pr(*args, **kwargs):
        print(*args, **kwargs, sep=" ", end="")

    if args.name:
        pr(repo.name())
        if args.path:
            pr(" @ ")
    if args.path:
        pr(repo.abspath())

    if not args.name and not args.path:
        pr("{} @ {}".format(repo.name(), repo.abspath()))
    print()  # New line at the end
    if not os.path.exists(repo.abspath()):
        cli.print_cli_warn(
            "repository '{}' does not exist".format(repo.abspath())
        )


# TODO make use RepoSpec
def list_repos(args):
    """Print list of repositories from ``args``."""

    # True marks a repository from args.repositories as found
    matches = [False] * len(args.repositories)
    # indicates if any item in `args.repositories` was matched
    any_matching_repos = not args.repositories or args.add or args.remove

    # With --add or --remove, or with no args.repositories print all repos
    if args.add or args.remove or not args.repositories:
        for repo in repo_module.lookup_path:
            print_repo(repo, args)
    else:
        for repo in repo_module.lookup_path:
            name = repo.name()
            # Does the repo match any of the ids in args.repositories?
            for i, repo_id in enumerate(args.repositories):
                if repo_id == name or repo_id == util.basename(repo.abspath()):
                    # Yes: print absolute path
                    print_repo(repo, args)
                    # also mark repo as found
                    any_matching_repos = matches[i] = True

    if not args.add and not args.remove:
        for i, match in enumerate(matches):
            if not match:
                cli.print_cli_err(
                    "repository '{}' not found".format(args.repositories[i])
                )
    if (
        not any_matching_repos  # no matching repos
        and args.repositories  # some repos specified in positional arguments
        and not args.add  # no --add option
        and not args.remove  # no --remove option
    ):
        sys.exit(1)


def remove_from_path(remove_repos):
    """Remove matching repos from REPO_PATH environment variable."""
    remove_repo_paths = [r.realpath() for r in remove_repos]
    repo_module.lookup_path[:] = (
        repo
        for repo in repo_module.lookup_path
        if repo.realpath() not in remove_repo_paths
    )


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    # print(args.repositories)
    # print()
    # print(*[r.abspath() for r in args.repo], sep='\n')
    # print()
    # print(args.repo.repos())
    if args.add or args.remove:
        user_cfg_path = config.user_default_path()
        if user_cfg_path:
            # TODO notify if repo already exists (add) or doesn't (remove)
            if args.add:
                repo_module.lookup_path += args.repositories
            elif args.remove:
                # Remove matching paths from REPO_PATH
                remove_from_path(args.repositories)
            # Remove any duplicates
            paths = [r.abspath() for r in repo_module.lookup_path]
            paths = list(dict.fromkeys(paths))  # remove dubplicates
            config.cfg["general.repo_path"] = "\n".join(paths)
            config_cli.write_config(user_cfg_path)
        else:
            cli.print_cli_err("no user configuration file was found")
            sys.exit(1)

    if args.list or (not args.add and not args.remove):
        # if args.add or args.remove:
        list_repos(args)
        # TODO else:
        #     list_repos(args, args.repo)
