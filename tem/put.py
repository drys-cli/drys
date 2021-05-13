import os, sys
import argparse

from . import common, util, ext
from .util import print_err

def setup_parser(subparsers):
    p = subparsers.add_parser('put', add_help=False,
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
    print_err('error: ' + sys.argv[0] +
          ''': option -o/--output is allowed with multiple templates
          only if all of them are directories''')
    quit(1)

def _error_exists_but_not_dir(path):
    print_err("error: tem: '{}' exists and is not a directory".format(path))
    quit(1)

def cmd(args):
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

    for template in args.templates:
        exists = False      # Indicates that file exists in at least one repo
        for repo in repos:
            src = repo + '/' + template
            if os.path.exists(src):
                exists = True
            else: continue

            # Determine destination file based on arguments
            dest_candidates = [
                args.output,                                        # --output
                args.directory + '/' + os.path.basename(template)   # --directory
                if args.directory else None,
                os.path.basename(template),                         # neither
            ]
            dest = next(x for x in dest_candidates if x)

            # If template is a directory, run pre hooks
            if os.path.isdir(src):
                environment = { 'TEM_DESTDIR': os.path.realpath(dest) }
                common.run_hooks('put.pre', src, environment)
            try:
                dest = util.copy(src, dest)
            except Exception as e:
                util.print_error_from_exception(e)
                exit(1)

            # If template is a directory, run pre hooks
            if os.path.isdir(src):
                common.run_hooks('put.post', src)

        if not exists:
            print_err('tem: error: the following template was not found in the'
                  'available repositories:', template)
            exit(1)
