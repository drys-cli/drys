import argparse, os

from . import cli, util

def setup_parser(subparsers):
    p = subparsers.add_parser('rm', add_help=False,
                              help='remove templates from a repository')
    cli.add_general_options(p)

    p.add_argument('files', metavar='FILES', nargs='+',
                   help='files/directories to remove')

    p.set_defaults(func=cmd)

@cli.subcommand_routine('rm')
def cmd(args):
    repos = cli.resolve_and_validate_repos(args.repo, cmd='rm')

    for repo in repos:
        for file in args.files:
            file = repo + '/' + file
            if os.path.exists(file):
                util.remove(file)
