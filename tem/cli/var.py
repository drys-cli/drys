"""Manipulate tem variants."""
import os
import sys

from tem import util, var
from tem.cli import common as cli

from .common import print_cli_err


def setup_parser(p):
    cli.add_general_options(p)

    p.add_argument("variants", nargs="*", help="set the active variant")
    mutex = p.add_mutually_exclusive_group()
    mutex.add_argument(
        "-q",
        "--query",
        action="store_true",
        help="query if VARIANTs are active",
    )
    mutex.add_argument(
        "-a",
        "--activate",
        action="store_true",
        help="activate VARIANTs [default]",
    )
    mutex.add_argument(
        "-d", "--deactivate", action="store_true", help="disable VARIANTs"
    )
    mutex.add_argument(
        "-x",
        "--exclusive",
        action="store_true",
        help="activate VARIANTs, deactivate all others",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print all active variants",
    )

    p.set_defaults(func=cmd)


def query(args):
    """Query if specified variants are active."""
    exit_with_fail = False
    for arg_variant in args.variants:
        if arg_variant not in var.active_variants():
            if not args.verbose:
                sys.exit(1)
            else:
                exit_with_fail = True
    if exit_with_fail:
        sys.exit(1)


def no_action(args):
    return not (
        args.activate or args.deactivate or args.exclusive or args.query
    )


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    # TODO make it so users can only choose from an existing pool of variants
    # and so that new variants can be registered using a special option
    if not os.path.exists(".tem"):
        print_cli_err("this is not a temdir")
        util.print_err("Try running `tem init` first.")
        return

    if no_action(args):
        if args.variants:  # variants not empty
            args.activate = True
        else:
            args.verbose = True

    if args.activate:  # --activate option
        var.activate(args.variants)
    if args.exclusive:  # --exclusive option
        var.set_active_variants(args.variants)
    elif args.deactivate:  # --deactivate option
        var.deactivate(args.variants)
    elif args.query:  # --query option
        query(args)

    # This will run either when the --verbose option is given, or when
    # this command is run simply as `tem var`
    if args.verbose:
        variants = var.active_variants()
        print(*(variants if variants else ["default"]), sep="\n")
