import argparse

from . import common
from . import ext
import sys, os

def setup_parser(subparsers):
    p = subparsers.add_parser('ls', help='list templates')
    common.add_common_options(p)
    p.add_argument('-s', '--short', action='store_true', help='only list the contents of the repositories')
    p.add_argument('-R', '--repo', action='append', default=[], help='repository to be searched')
    p.add_argument('templates', nargs='*', help='which templates to list')
    p.set_defaults(func=cmd)

def print_contents(repo):
    print()
    for file in os.listdir(repo):
        print('\t', file, sep='', end='')
        if os.path.isdir(repo + '/' + file):
            print('/', end='')
        print()

def cmd(parser, args):
    if args.repo: # Show only the specified repositories
        ls_args = args.repo
    else:
        ls_args = common.repos

    for repo in ls_args:
        message = 'Repository @ ' + repo
        print(message); print('=' * len(message))
        # TODO Check for excluded files
        if args.short:
            print_contents(repo)
        else:
            ext.call(['ls', '-1'] + ls_args)
