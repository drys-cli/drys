import argparse, os

from . import common, util

def setup_parser(subparsers):
    p = subparsers.add_parser('rm', add_help=False,
                              help='remove files from a repository')
    common.add_common_options(p)

    p.add_argument('files', nargs='+', help='which files/directories to remove')

    p.set_defaults(func=cmd)

def cmd(args):
    repos = common.form_repo_list(args.repo, cmd='rm')
    repos = common.resolve_and_validate_repos(repos)

    for repo in repos:
        for file in args.files:
            file = repo + '/' + file
            if os.path.exists(file):
                util.remove(file)
