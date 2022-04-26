"""tem hook subcommand"""
import os
import sys

from .. import ext
from . import common as cli


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    cli.add_general_options(parser)

    action_opts = parser.add_mutually_exclusive_group()
    action_opts.add_argument(
        "-x", "--exec", action="store_true", help="execute HOOKS (default)"
    )
    action_opts.add_argument(
        "-n", "--new", action="store_true", help="create new HOOKS"
    )
    action_opts.add_argument(
        "-a", "--add", action="store_true", help="add specified files as hooks"
    )
    action_opts.add_argument(
        "-l", "--list", action="store_true", help="list hooks"
    )
    cli.add_edit_options(parser)
    parser.add_argument(
        "-f",
        "--force",
        help="create .tem/ if it doesn't exist (only when adding hooks)",
    )
    parser.add_argument(
        "hooks",
        metavar="HOOKS",
        nargs="?",
        help="the hooks on which to operate",
    )


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    # TODO this part is unusable
    # Create a cli interface for env and hooks, and potentially other files
    # in the .tem/* subdirectories
    if not (args.new or args.add or args.edit or args.editor or args.list):
        args.exec = True
    if args.new:
        raise NotImplementedError
    elif args.add:
        pass  # TODO
    if args.list:
        ls_args = ["ls", "-1"]
        os.chdir(".tem/hooks/")
        # Without --new and --add, only display files from `args.hooks`.
        # With --new or --add options, all files will be displayed.
        if not args.new and not args.add:
            ls_args += args.hooks
        p = ext.run(ls_args, encoding="utf-8")
        sys.exit(p.returncode)
