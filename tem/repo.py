import sys, os
import argparse

from . import common, util
from .util import print_err

def setup_parser(subparsers):
    p = subparsers.add_parser('repo', add_help=False,
                              help='repository operations')
    common.add_common_options(p)

    p.add_argument('-l', '--list', action='store_true',
                   help='list repositories')
    p.add_argument('-n', '--name', action='store_true',
                   help='print the repository name')
    p.add_argument('-p', '--path', action='store_true',
                   help='print the repository path')

    add_rem = p.add_mutually_exclusive_group()
    add_rem.add_argument('-a', '--add', action='store_true',
                   help='add repositories to REPO_PATH')
    add_rem.add_argument('-r', '--remove', action='store_true',
                   help='remove repositories from REPO_PATH')

    p.add_argument('repositories', nargs='*',
                   help='repository paths, partial paths or names')

    p.set_defaults(func=cmd)

def print_repo(repo, args):
    # TODO align output, too lazy at the moment
    pr = lambda *args, **kwargs: print(*args, **kwargs, sep=' ', end='')
    if args.name:
        pr(util.fetch_name(repo))
        if args.path:
            pr(' @ ')
    if args.path:
        pr(os.path.abspath(repo))

    if not args.name and not args.path:
        pr('{} @ {}'
              .format(util.fetch_name(repo), os.path.abspath(repo)))
    print() # New line at the end
    if not os.path.exists(repo):
        print_err("tem: warning: repository '{}' does not exist".format(repo))

def list_repos(args):
        repos = common.form_repo_list(args.repo, cmd='repo')
        repos = common.resolve_and_validate_repos(repos)

        # True marks a repository from args.repositories as found
        matches = [False] * len(args.repositories)
        # indicates if any item in `args.repositories` was matched
        any_matching_repos = not args.repositories or args.add or args.remove

        # With --add or --remove, or with no args.repositories print all repos
        if args.add or args.remove or not args.repositories:
            for repo in repos: print_repo(repo, args)
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
                    print_err("tem: info: repository '{}' not found"
                          .format(args.repositories[i]))
        if not any_matching_repos:
            exit(1)

def cmd(args):

    if args.add or args.remove:
        user_cfg_path = common.get_user_config_path()
        if user_cfg_path:
            cfg = util.ConfigParser(user_cfg_path)
            # Read contents of REPO_PATH from the user config file
            paths = [ r for r in cfg['general.repo_path'].split('\n') if r ]
            # TODO notify if repo already exists (add) or doesn't exist (remove)
            if args.add:
                arg_repos = [ util.realpath(r) for r in args.repositories ]
                paths += arg_repos
            elif args.remove:
                arg_repos = [ os.path.realpath(util.resolve_repo(r))
                             for r in args.repositories ]
                # Remove matching paths from REPO_PATH
                paths = [ cfg_path for cfg_path in paths
                         if util.realpath(cfg_path) not in arg_repos ]
            # Remove any duplicates
            paths = list(dict.fromkeys([ r for r in paths ]))
            cfg['general.repo_path'] = '\n'.join(paths)
            # Save modified data to the same file
            with open(user_cfg_path, 'w') as file_object:
                try:
                    cfg.write(file_object)
                    common.repo_path = paths
                    if args.list: list_repos(args)
                except Exception as e:
                    if args.list: list_repos(args)
                    util.print_error_from_exception(e)
                    exit(1)
        else:
            print('tem: error: no user configuration file was found')
            exit(1)

    else:
        list_repos(args)
