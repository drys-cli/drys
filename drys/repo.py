import argparse

from . import common
from . import ext
import sys, os

def setup_parser(subparsers):
    p = subparsers.add_parser('repo', help='repository operations')
    common.add_common_options(p)

    p.add_argument('-l', '--list', action='store_true',
                   help='list default repositories')


    p.set_defaults(func=cmd)

def cmd(parser, args):
    if args.list:
        for repo in common.repos:
            print(repo)

