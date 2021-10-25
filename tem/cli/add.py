"""tem add subcommand"""
import os
import sys

from .. import util
from . import common as cli


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    parser.add_argument(
        "files",
        metavar="FILES",
        nargs="+",
        type=cli.existing_file,
        help="files or directories to add",
    )

    out = parser.add_mutually_exclusive_group()
    out.add_argument(
        "-o",
        "--output",
        metavar="OUT",
        help="output file or directory relative to repo",
    )
    out.add_argument(
        "-d",
        "--directory",
        metavar="DIR",
        help="directory inside repo where FILES should be placed",
    )
    cli.add_edit_options(parser)
    parser.add_argument(
        "-m",
        "--move",
        action="store_true",
        help="move FILES instead of copying",
    )

    # Recursion options
    recursion = parser.add_mutually_exclusive_group()
    recursion.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="copy directories recursively [default]",
    )
    recursion.add_argument(
        "--norecursive",
        dest="recursive",
        action="store_false",
        help="do not copy directories recursively",
    )

    cli.add_general_options(parser)
    parser.set_defaults(func=cmd)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""

    edit_files = []  # Files that will be edited if --edit[or] was provided
    try:
        # Copy or move the files
        for file in args.files:
            basename = os.path.basename(file)
            dests = [
                args.directory + "/" + basename if args.directory else None,
                args.output,
                basename,
            ]
            # Get first that is not None
            dest = next(path for path in dests if path is not None)
            for repo in args.repo:
                repo = repo.abspath()
                # Create the destination path if it doesn't exist
                if not os.path.exists(repo):
                    os.makedirs(repo, mode=0o777)
                    print(
                        "The repo directory '"
                        + repo
                        + "' did not exist. It was created for you."
                    )
                if not args.move:  # copy
                    dest_file = util.copy(file, repo + "/" + dest)
                else:  # move
                    dest_file = util.move(file, repo + "/" + dest)

                if args.edit or args.editor:
                    edit_files.append(dest_file)
    except Exception as exception:
        cli.print_error_from_exception(exception)
        sys.exit(1)
    if edit_files:
        cli.try_open_in_editor(edit_files, override_editor=args.editor)
