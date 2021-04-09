import argparse

from . import common
from . import ext

def setup_parser(subparsers):
    p = subparsers.add_parser('put',
                              help='put template(s) into the desired directory')
    p.add_argument('-R', '--repo', action='append', default=[],
                   help='repository to be searched')
    p.add_argument('templates', nargs='*', help='which templates to put')
    p.set_defaults(func=cmd)

def cmd(parser, args):
    return
