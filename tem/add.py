import argparse
import sys, os
import re

# Local imports
from . import common, util
from .common import cfg, aliases

def setup_parser(subparsers):
    p = subparsers.add_parser('add', add_help=False,
                              help='add files or directories to your tem repository')
    p.add_argument('files', nargs='+', type=common.existing_file,
                   help='files or directories to add')
    p.add_argument('-H', '--hook', nargs='?',
                   help='script that will run when the directory is imported')
    p.add_argument('-m', '--move', action='store_true',
                   help='move the file(s) instead of copying')

    out = p.add_mutually_exclusive_group()
    out.add_argument('-o', '--output', metavar='OUT',
                     help='output file or directory relative to repo')
    out.add_argument('-d', '--directory', metavar='DIR',
                     help='directory relative to repo where the file(s) should be placed')
    common.add_edit_options(p)

    # Recursion options
    recursion = p.add_mutually_exclusive_group()
    recursion.add_argument('-r', '--recursive', action='store_true',
                           help='copy directories recursively [default]')
    recursion.add_argument('--norecursive', dest='recursive', action='store_false',
                           help='do not copy directories recursively')

    common.add_common_options(p)
    p.set_defaults(func=cmd)

def cmd(args):
    repos = common.form_repo_list(args.repo, cmd='add')
    repos = common.resolve_and_validate_repos(repos)

    edit_files = []     # Files that will be edited if --edit[or] was provided
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
                    dest_file = util.copy(file, repo + '/' + dest)
                else:                                                   # move
                    dest_file = util.move(file, repo + '/' + dest)

                if args.edit or args.editor:
                    edit_files.append(dest_file)
    except Exception as e:
        util.print_error_from_exception(e)
        exit(1)
    if edit_files:
        common.try_open_in_editor(edit_files, override_editor=args.editor)

