"""tem put subcommand"""
import os
import sys

from tem import util, repo, errors
from tem.cli import common as cli


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


def destinations_from_args(args, template):
    """Return a list of destinations by reading `args`."""
    # TODO currently only works with one destination
    # Determine destination file based on arguments
    if not args.output and not args.directory and not os.isatty(1):
        return [sys.stdout]
    dest_candidates = [
        args.output,  # --output
        args.directory + "/" + os.path.basename(template)  # --directory
        if args.directory
        else None,
        os.path.basename(template),  # neither, use local path
    ]
    dest = next(x for x in dest_candidates if x)
    return [dest]


def pre_hooks(dest):
    environment = {"TEM_DESTDIR": util.abspath(dest)}
    # TODO debug, creates dest as a directory
    # cli.run_hooks("put.pre", src, dest, environment)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""

    if args.output:
        _verify_output_option(args)

    if args.directory:
        _verify_directory_option(args)

    edit_files = []  # Files that will be edited if --edit[or] was provided
    for template in args.templates:
        exists = False  # Indicates that file exists in at least one repo
        for src in repo.find_template(template, repos=args.repo):
            exists = True
            destinations = destinations_from_args(args, template)
            if args.edit or args.editor:
                edit_files.append(destinations)

            for dest in destinations:
                # If template is a directory, run pre hooks
                if os.path.isdir(src):
                    pre_hooks(dest)
                if dest == "-":
                    util.cat(src)
                else:
                    util.copy(src, dest, symlink=args.symlink)
                # If template is a directory, run post hooks
                if os.path.isdir(src):
                    cli.run_hooks("put.post", src)

        if not exists:
            raise errors.TemplateNotFoundError(template)
    if edit_files:
        cli.try_open_in_editor(edit_files, override_editor=args.editor)


# HELPER FUNCTIONS


def _err_output_multiple_templates():
    cli.print_cli_err(
        """option -o/--output is allowed with multiple templates
          only if all of them are directories"""
    )
    sys.exit(1)


def _verify_output_option(args):
    # --output option doesn't make sense for multiple files
    # (multiple directories are OK)
    if len(args.templates) != 1:
        for file in args.templates:
            # TODO doesn't work. Where is the repo path in here?
            if os.path.isfile(file):
                _err_output_multiple_templates()
                sys.exit(1)


def _verify_directory_option(args):
    # The path exists and is not a directory
    if os.path.exists(args.directory) and not os.path.isdir(args.directory):
        raise errors.FileNotDirError(args.directory)
