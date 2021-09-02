"""tem path subcommand"""
from . import dot, common as cli


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    dot.setup_common_parser(parser)
    parser.set_defaults(func=cmd)


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    dot.cmd_common(args, subdir="path")
