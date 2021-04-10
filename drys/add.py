import argparse
import sys, os
import shutil
import re

# Local imports
from . import common
from .common import cfg, aliases

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
    p.add_argument('-R', '--repo',
                   help='the repository the file(s) will be saved to')

    # Recursion options
    recursion = p.add_mutually_exclusive_group()
    recursion.add_argument('--recursive', action='store_true',
                           help='copy directories recursively [default]')
    recursion.add_argument('--norecursive', dest='recursive', action='store_false',
                           help='do not copy directories recursively')

    p.set_defaults(func=cmd)
    return p

def copy(src, dest):
    if os.path.isdir(src):
        shutil.copytree(src, dest + '/' + os.path.basename(src),
                        dirs_exist_ok=True, copy_function=copy)
    else:
        shutil.copy(src, dest) # TODO Support multiple repos

def move(src, dest):
    shutil.move(src, dest) # TODO Support multiple repos

def cmd(parser, args):
    args = parser.parse_args() # Unrecognized arguments will exit with an error

    # Determine the repo
    if not args.repo:
        args.repo = common.repos[0]

    try:
        # Create the destination path if it doesn't exist
        if not os.path.exists(args.repo):
            os.makedirs(args.repo, mode=0o777)
            print('The repo directory \'' + args.repo +
                  '\' does not exist. It was created for you.')

        # Copy or move the files
        if not args.move:               # copy
            for file in args.files:
                copy(file, args.repo)
        else:                           # move
            for file in args.files:
                move(file, args.repo)

    except Exception as e:
        print('error:', re.sub(r'^\[Errno [0-9]*\] ', '', str(e)), file=sys.stderr)

