"""tem rm subcommand"""
import os

from .. import util
from . import common as cli


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    cli.add_general_options(parser)

    parser.add_argument(
        "files", metavar="FILES", nargs="+", help="files/directories to remove"
    )

    parser.set_defaults(func=cmd)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""

    for repo in args.repo:
        for file in args.files:
            file = repo + "/" + file
            if os.path.exists(file):
                util.remove(file)
