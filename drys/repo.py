import argparse

from . import common
import sys, os

def setup_parser(subparsers):
    p = subparsers.add_parser('repo', help='repository operations')
    common.add_common_options(p)

    p.add_argument('-l', '--list', action='store_true',
                   help='list repositories')
    p.add_argument('-a', '--add', action='store_true',
                   help='add repositories to the list of default repositories')
    p.add_argument('repositories', nargs='*',
                   help='repository paths, partial paths or names')

    p.set_defaults(func=cmd)

def cmd(parser, args):
    repos = common.form_repo_list(args.repo, cmd='repo')
    repos = common.resolve_and_validate_repos(repos)

    # True marks a repository from args.repositories as found
    matches = [False] * len(args.repositories)
    # indicates if any item in `args.repositories` was matched
    any_matching_repos = not args.repositories

    for repo in repos:
        if args.repositories:
            name = common.fetch_name(repo)
            # Does the repo match any of the ids in args.repositories?
            for i, repo_id in enumerate(args.repositories):
                if repo_id == name or repo_id == os.path.basename(repo):
                    # Yes: print absolute path
                    print(os.path.abspath(repo))
                    # also mark repo as found
                    any_matching_repos = matches[i] = True
        elif os.path.exists(repo):
            print(os.path.abspath(repo))

    for i, match in enumerate(matches):
        if not match:
            print("drys: info: repository '{}' not found"
                  .format(args.repositories[i]), file=sys.stderr)
    if not any_matching_repos:
        exit(1)
