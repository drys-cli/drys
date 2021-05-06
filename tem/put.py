import argparse
import os, sys

from . import common
from .common import copy, move
from . import ext

def setup_parser(subparsers):
    p = subparsers.add_parser('put',
                              help='put template(s) into the desired directory')
    common.add_common_options(p)

    out = p.add_mutually_exclusive_group()
    out.add_argument('-o', '--output', metavar='OUT',
                     help='output file or directory')
    out.add_argument('-d', '--directory', metavar='DIR',
                     help='directory where the file(s) should be placed')
    p.add_argument('templates', nargs='+', help='which templates to put')
    p.set_defaults(func=cmd)

def _error_output_multiple_templates():
    print('error: ' + sys.argv[0] +
          ''': option -o/--output is allowed with multiple templates
          only if all of them are directories''',
          file=sys.stderr)
    quit(1)

def _error_exists_but_not_dir(path):
    print('error: ' + sys.argv[0] +
          ': \'' + path + '\' exists and is not a directory',
          file=sys.stderr)
    quit(1)

def cmd(parser, args):
    repos = common.form_repo_list(args.repo, cmd='put')
    repos = common.resolve_and_validate_repos(repos)

    if args.output:
        # --output option doesn't make sense for multiple files
        # (multiple directories are OK)
        if len(args.templates) != 1:
            for file in args.templates:
                if os.path.isfile(file):
                    _error_output_multiple_templates()
                    return

    if args.directory:
        # The path exists and is not a directory
        if os.path.exists(args.directory) and not os.path.isdir(args.directory):
            _error_exists_but_not_dir(args.directory)

    for src in args.templates:
        exists = False
        for repo in repos:
            src_file = repo + '/' + src
            dest_candidates = [
                args.output,                                    # --output
                args.directory + '/' + os.path.basename(src)    # --directory
                if args.directory else None,
                os.path.basename(src),                          # neither
            ]
            result = copy(src_file, next(x for x in dest_candidates if x), True)
            if not exists and result:
                exists = True
        if not exists:
            print('tem: error: the following template was not found in the'
                  'available repositories:', src, file=sys.stderr)
            exit(1)
