import argparse, os

from . import common

def setup_parser(subparsers):
    p = subparsers.add_parser('rm', help='remove files from a repository')
    common.add_common_options(p)

    p.add_argument('files', nargs='+', help='which files/directories to remove')

    p.set_defaults(func=cmd)

def cmd(parser, args):
    repos = common.form_repo_list(args.repo, cmd='rm')
    repos = common.resolve_and_validate_repos(repos)

    for repo in repos:
        for file in args.files:
            common.remove(repo + '/' + file)
