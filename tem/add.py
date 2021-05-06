import argparse
import sys, os
import re

# Local imports
from . import common
from .common import cfg, aliases, copy, move

def setup_parser(subparsers):
    p = subparsers.add_parser('add',
        help='add files or directories to your tem repository'
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

    out = p.add_mutually_exclusive_group()
    out.add_argument('-o', '--output', metavar='OUT',
                     help='output file or directory relative to repo')
    out.add_argument('-d', '--directory', metavar='DIR',
                     help='directory relative to repo where the file(s) should be placed')

    # Recursion options
    recursion = p.add_mutually_exclusive_group()
    recursion.add_argument('-r', '--recursive', action='store_true',
                           help='copy directories recursively [default]')
    recursion.add_argument('--norecursive', dest='recursive', action='store_false',
                           help='do not copy directories recursively')

    p.set_defaults(func=cmd)
    return p

def cmd(parser, args):
    repos = common.form_repo_list(args.repo, cmd='add')
    repos = common.resolve_and_validate_repos(repos)

    try:
        # Copy or move the files
        for file in args.files:
            basename = os.path.basename(file)
            dests = [args.directory + '/' + basename if args.directory else None,
                     args.output, basename]
            # Get first that is not None
            dest = next(path for path in dests if path != None)
            for repo in repos:
                # Create the destination path if it doesn't exist
                if not os.path.exists(repo):
                    os.makedirs(repo, mode=0o777)
                    print("The repo directory '" + repo +
                          "' did not exist. It was created for you.")
                if not args.move:                                       # copy
                    copy(file, repo + '/' + dest)
                else:                                                   # move
                    move(file, repo + '/' + dest)
    except Exception as e:
        common.print_error_from_exception(e)
        exit(1)

