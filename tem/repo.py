"""tem repo subcommand"""
import os
import sys

from . import cli, util


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
        nargs="*",
        help="repository paths, partial paths or names",
    )

    parser.set_defaults(func=cmd)


# TODO Make a function that just returns the string
def print_repo(repo, args):
    """
    Print the title line for a repository. Takes CLI arguments ``args`` into
    account.
    """
    # TODO align output, too lazy at the moment
    pr = lambda *args, **kwargs: print(*args, **kwargs, sep=" ", end="")
    if args.name:
        pr(util.fetch_name(repo))
        if args.path:
            pr(" @ ")
    if args.path:
        pr(util.abspath(repo))

    if not args.name and not args.path:
        pr("{} @ {}".format(util.fetch_name(repo), util.abspath(repo)))
    print()  # New line at the end
    if not os.path.exists(repo):
        cli.print_cli_warn("repository '{}' does not exist".format(repo))


def list_repos(args):
    """Print list of repositories from ``args``."""
    repos = cli.resolve_and_validate_repos(args.repo)

    # True marks a repository from args.repositories as found
    matches = [False] * len(args.repositories)
    # indicates if any item in `args.repositories` was matched
    any_matching_repos = not args.repositories or args.add or args.remove

    # With --add or --remove, or with no args.repositories print all repos
    if args.add or args.remove or not args.repositories:
        for repo in repos:
            print_repo(repo, args)
    else:
        for repo in repos:
            name = util.fetch_name(repo)
            # Does the repo match any of the ids in args.repositories?
            for i, repo_id in enumerate(args.repositories):
                if repo_id == name or repo_id == util.basename(repo):
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
    if not any_matching_repos:
        sys.exit(1)


def find_template(template, repos, all_repos=False):
    """
    Return the absolute path of a template, looked up in ``repos``. If
    ``all_repos`` is ``True`` then a list of matching templates in each
    repository is returned. Otherwise, only the match in the first repository
    is returned (a list with one element). If there are not matches an empty
    list is returned.
    .. note:: A template can be a directory tree.
    """
    result_paths = []

    for repo in repos:
        template_abspath = util.abspath(repo + "/" + template)
        if not os.path.exists(template_abspath):
            continue
        if not all_repos:
            return [template_abspath]
        result_paths.append(template_abspath)

    return result_paths


def cmd(args):
    """Execute this subcommand."""

    if args.add or args.remove:
        user_cfg_path = cli.get_user_config_path()
        if user_cfg_path:
            cfg = util.ConfigParser(user_cfg_path)
            # Read contents of REPO_PATH from the user config file
            paths = [r for r in cfg["general.repo_path"].split("\n") if r]
            # TODO notify if repo already exists (add) or doesn't (remove)
            if args.add:
                arg_repos = [util.abspath(r) for r in args.repositories]
                paths += arg_repos
            elif args.remove:
                arg_repos = [
                    util.abspath(util.resolve_repo(r))
                    for r in args.repositories
                ]
                # Remove matching paths from REPO_PATH
                paths = [
                    cfg_path
                    for cfg_path in paths
                    if util.abspath(cfg_path) not in arg_repos
                ]
            # Remove any duplicates
            paths = list(dict.fromkeys(paths))
            cfg["general.repo_path"] = "\n".join(paths)
            # Save modified data to the same file
            with open(user_cfg_path, "w") as file_object:
                try:
                    cfg.write(file_object)
                    cli.repo_path = paths
                    if args.list:
                        list_repos(args)
                except Exception as e:
                    if args.list:
                        list_repos(args)
                    cli.print_error_from_exception(e)
                    sys.exit(1)
        else:
            print("tem: error: no user configuration file was found")
            sys.exit(1)

    else:
        list_repos(args)
