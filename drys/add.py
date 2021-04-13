import argparse
import sys, os
import re

# Local imports
from . import common
from .common import cfg, aliases, copy, move

def setup_parser(subparsers):
    p = subparsers.add_parser('add',
        help='add files or directories to your drys repository'
    )
    common.add_common_options(p)

    p.add_argument('files', nargs='+', type=common.existing_file,
                   help='files or directories to add')
    p.add_argument('-H', '--hook', nargs='?',
                   help='script that will run when the directory is imported')
    p.add_argument('-t', '--template', metavar='T',
                   help='add the files to an existing template')
    p.add_argument('-m', '--move', action='store_true',
                   help='move the file(s) instead of copying')

    # Recursion options
    recursion = p.add_mutually_exclusive_group()
    recursion.add_argument('-r', '--recursive', action='store_true',
                           help='copy directories recursively [default]')
    recursion.add_argument('--norecursive', dest='recursive', action='store_false',
                           help='do not copy directories recursively')

    p.set_defaults(func=cmd)
    return p

def cmd(parser, args):
    args = parser.parse_args() # Unrecognized arguments will exit with an error

    # Determine the repo
    if not args.repo:
        args.repo = common.repos[0]

    try:
        for repo in args.repo:
            # Create the destination path if it doesn't exist
            if not os.path.exists(repo):
                os.mkdir(repo, mode=0o777)
                print("The repo directory '" + repo +
                      "' did not exist. It was created for you.")

            # Copy or move the files
            if not args.move:               # copy
                for file in args.files:
                    copy(file, repo + '/' + os.path.basename(file))
            else:                           # move
                for file in args.files:
                    move(file, repo)
    except Exception as e:
        common.print_error_from_exception(e)

