"""Find various tem-related stuff"""
import os
import sys

from tem import env, find, repo, util
from tem.cli import common as cli

from .common import print_err, print_cli_err, print_cli_warn

# TODO DOCUMENT IN MANPAGE


def setup_parser(parser):
    cli.add_general_options(parser)

    # (make it the directory that we are looking from)
    # but specify temdirs using another option
    parser.add_argument(
        "--base",
        "-b",
        action="store_true",
        help="find the base tem directory",
    )
    parser.add_argument(
        "--root",
        "-r",
        action="store_true",
        help="find the root tem directory",
    )
    # TODO implement
    parser.add_argument(
        "--from",
        "-f",
        metavar="DIR",
        help="search from DIR instead of PWD",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print more details",
    )
    cli.add_edit_options(parser)
    parser.add_argument("args", help="names to match against", nargs="*")


@cli.subcommand
def cmd(args):
    # TODO Add tests for this subcommand
    # TODO consider a way to make this work with coreutils 'find' or 'fd'
    # TODO Handle explicit paths differently
    # TODO add coloring to verbose headings
    # use the TEM_ENV environment variable (this variable is not yet used by
    # any commands)

    result_paths = []

    # No options given, print all temdirs in the current hierarchy
    if not args.root and not args.args:
        if args.verbose:
            cli.print_err("Tem directories:")
        result_paths += list(find.parent_temdirs())

    if args.base:  # --base option
        _print_base(args)
    if args.root:  # --root option
        _print_root(args)

    # TODO rework this part
    if args.args:  # templates specified as positional arguments
        for template in args.args:
            result_paths += repo.find_template(template)

    if args.edit or args.editor:
        cli.try_open_in_editor(result_paths, args.editor)


def _print_base(args):
    if args.verbose:
        cli.print_err("Base directory:")

    try:
        print(
            next(
                d
                for d in find.parent_temdirs()
                if util.basename(d) in args.args or not args.args
            )
        )
    except StopIteration:
        cli.exit_code = 1


def _print_root(args):
    if args.verbose:
        cli.print_err("Root tem directory:")
    try:
        print(
            [
                d
                for d in find.parent_temdirs()
                if util.basename(d) in args.args or not args.args
            ][-1]
        )
    except IndexError:
        cli.exit_code = 1
