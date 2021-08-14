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


def cmd(args):
    """Execute this subcommand."""
    repos = cli.resolve_and_validate_repos(args.repo)

    for repo in repos:
        for file in args.files:
            file = repo + "/" + file
            if os.path.exists(file):
                util.remove(file)
