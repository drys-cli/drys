"""tem put subcommand"""
import os
import sys

from .. import util
from . import common as cli


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    cli.add_general_options(parser)

    out = parser.add_mutually_exclusive_group()
    out.add_argument(
        "-o", "--output", metavar="OUT", help="output file or directory"
    )
    out.add_argument(
        "-d",
        "--directory",
        metavar="DIR",
        help="directory where the file(s) should be placed",
    )
    cli.add_edit_options(parser)
    parser.add_argument(
        "-s", "--symlink", action="store_true", help="create symlinks instead"
    )
    parser.add_argument(
        "templates",
        metavar="TEMPLATES",
        nargs="+",
        help="which templates to put",
    )
    parser.set_defaults(func=cmd)


def _err_output_multiple_templates():
    cli.print_cli_err(
        """option -o/--output is allowed with multiple templates
          only if all of them are directories"""
    )
    sys.exit(1)


def _err_exists_but_not_dir(path):
    cli.print_cli_err("'{}' exists and is not a directory".format(path))
    sys.exit(1)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""

    if args.output:
        # --output option doesn't make sense for multiple files
        # (multiple directories are OK)
        if len(args.templates) != 1:
            for file in args.templates:
                # TODO doesn't work. Where is the repo path in here?
                if os.path.isfile(file):
                    _err_output_multiple_templates()
                    return

    if args.directory:
        # The path exists and is not a directory
        if os.path.exists(args.directory) and not os.path.isdir(
            args.directory
        ):
            _err_exists_but_not_dir(args.directory)

    edit_files = []  # Files that will be edited if --edit[or] was provided
    for template in args.templates:
        exists = False  # Indicates that file exists in at least one repo
        for repo in args.repo:
            src = repo + "/" + template
            if os.path.exists(src):
                exists = True
            else:
                continue

            # Determine destination file based on arguments
            dest_candidates = [
                args.output,  # --output
                args.directory
                + "/"
                + os.path.basename(template)  # --directory
                if args.directory
                else None,
                os.path.basename(template),  # neither
            ]
            dest = next(x for x in dest_candidates if x)
            if args.edit or args.editor:
                edit_files.append(dest)

            # If template is a directory, run pre hooks
            if os.path.isdir(src):
                environment = {"TEM_DESTDIR": util.abspath(dest)}
                # TODO debug, creates dest as a directory
                # cli.run_hooks("put.pre", src, dest, environment)

            try:
                util.copy(src, dest, symlink=args.symlink)
            except Exception as e:
                cli.print_error_from_exception(e)
                sys.exit(1)

            # If template is a directory, run post hooks
            if os.path.isdir(src):
                cli.run_hooks("put.post", src)

        if not exists:
            cli.print_cli_err(
                "template '{}' could not be found in the available "
                "repositories".format(template)
            )
            sys.exit(1)
    if edit_files:
        cli.try_open_in_editor(edit_files, override_editor=args.editor)
