import os, sys
import argparse

from . import cli, util, ext
from .util import print_cli_err

def setup_parser(subparsers):
    p = subparsers.add_parser('put', add_help=False,
                              help='put template(s) into the desired directory')
    cli.add_cli_options(p)

    out = p.add_mutually_exclusive_group()
    out.add_argument('-o', '--output', metavar='OUT',
                     help='output file or directory')
    out.add_argument('-d', '--directory', metavar='DIR',
                     help='directory where the file(s) should be placed')
    cli.add_edit_options(p)
    p.add_argument('templates', metavar='TEMPLATES', nargs='+',
                   help='which templates to put')
    p.set_defaults(func=cmd)

def error_output_multiple_templates():
    print_cli_err('''option -o/--output is allowed with multiple templates
          only if all of them are directories''')
    quit(1)

def _error_exists_but_not_dir(path):
    print_cli_err("'{}' exists and is not a directory".format(path))
    quit(1)

@cli.subcommand_routine('put')
def cmd(args):
    repos = cli.resolve_and_validate_repos(args.repo, cmd='put')

    if args.output:
        # --output option doesn't make sense for multiple files
        # (multiple directories are OK)
        if len(args.templates) != 1:
            for file in args.templates:
                # TODO doesn't work. Where is the repo path in here?
                if os.path.isfile(file):
                    error_output_multiple_templates()
                    return

    if args.directory:
        # The path exists and is not a directory
        if os.path.exists(args.directory) and not os.path.isdir(args.directory):
            _error_exists_but_not_dir(args.directory)

    edit_files = []     # Files that will be edited if --edit[or] was provided
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
            if args.edit or args.editor:
                edit_files.append(dest)

            # If template is a directory, run pre hooks
            if os.path.isdir(src):
                environment = { 'TEM_DESTDIR': util.abspath(dest) }
                cli.run_hooks('put.pre', src, dest, environment)

            try:
                util.copy(src, dest)
            except Exception as e:
                util.print_error_from_exception(e)
                exit(1)

            # If template is a directory, run post hooks
            if os.path.isdir(src):
                cli.run_hooks('put.post', src)

        if not exists:
            print_cli_err("template '{}' could not be found in the available "
                          "repositories".format(template))
            exit(1)
    if edit_files:
        cli.try_open_in_editor(edit_files, override_editor=args.editor)
