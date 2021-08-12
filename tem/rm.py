import argparse, os

from . import cli, util

def setup_parser(parser):
    cli.add_general_options(parser)

    parser.add_argument('files', metavar='FILES', nargs='+',
                        help='files/directories to remove')

    parser.set_defaults(func=cmd)

def cmd(args):
    repos = cli.resolve_and_validate_repos(args.repo, cmd='rm')

    for repo in repos:
        for file in args.files:
            file = repo + '/' + file
            if os.path.exists(file):
                util.remove(file)
