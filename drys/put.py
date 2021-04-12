import argparse
import os, sys

from . import common
from .common import copy, move
from . import ext

def setup_parser(subparsers):
    p = subparsers.add_parser('put',
                              help='put template(s) into the desired directory')
    p.add_argument('-R', '--repo', action='append', default=[],
                   help='repository to be searched')
    grp = p.add_mutually_exclusive_group()
    grp.add_argument('-o', '--output', metavar='OUT',
                     help='output file or directory')
    grp.add_argument('-d', '--directory', metavar='DIR',
                     help='directory where the file(s) should be placed')
    p.add_argument('templates', nargs='+', help='which templates to put')
    p.set_defaults(func=cmd)

def _error_output_multiple_templates():
    print('error: ' + sys.argv[0] +
          ': option -o/--output is allowed only with a single template',
          file=sys.stderr)
    quit(1)

def _error_exists_but_not_dir(path):
    print('error: ' + sys.argv[0] +
          ': \'' + path + '\' exists and is not a directory',
          file=sys.stderr)
    quit(1)

def cmd(parser, args):
    repos = args.repo if args.repo else common.repos

    dest = '.'          # Current dir by default

    if args.output:
        # --output option works only for single files or directories
        if len(args.templates) != 1:
            _error_output_multiple_templates()

    if args.directory:
        # The path exists and is not a directory
        if os.path.exists(args.directory) and not os.path.isdir(args.directory):
            _error_exists_but_not_dir(args.directory)

    for repo in repos:
        for src in args.templates:
            if args.output:                             # --output was specified
                copy(repo + '/' + src, args.output)
            elif args.directory:                    # --directory was specified
                if not os.path.exists(args.directory):
                    os.mkdir(args.directory)
                copy(repo + '/' + src, args.directory)
            else:
                copy(repo + '/' + src, '.')
