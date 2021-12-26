#!/usr/bin/env python3
"""
Main tem script

This module contains the main entry point -- :func:`main`
In that function, the following is done:
  - the highest command-level parser is set up
  - options relating to the `tem` command are parsed
  - the subcommands' parsers are set up and invoked

Additionally, this module should contain functions that implement the
functionality of the highest-level command, subcommands should implement their
own functionality.

Unfortunately, due to some limitations of :mod:`argparse`, the parsing is a bit
convoluted. If you want to understand what is going on, look at the comments
carefully. This module is not supposed to change very often, so it shouldn't be
necessary to understand the fine details.
"""

import argparse
import glob
import os
import re
import sys
from importlib import import_module

import tem
from tem import config, plugin, util
from tem.cli import common as cli


def init_user():
    """Initialize a user config file in a location with the highest priority"""
    try:
        existing_cfg = next(
            path for path in config.USER_PATHS if os.path.exists(path)
        )
    except StopIteration:
        existing_cfg = None
    os.makedirs(tem.default_repo, exist_ok=True)
    if existing_cfg:
        cli.print_cli_err("configuration already exists at " + existing_cfg)
        sys.exit(1)
    else:
        util.copy(
            tem.__prefix__ + "/share/tem/config", config.user_default_path()
        )
        sys.exit(0)


def print_help_exit(parser):
    parser.print_help()
    sys.exit(0)


def cmd_lazy_load(subcommand, parsers):
    """
    Loads a subcommand module only after we know which subcommand was
    invoked. This gives a small performance improvement.
    """

    def func():
        module = import_module("tem.cli.%s" % subcommand)
        module.setup_parser(parsers[subcommand])
        parsers[subcommand].set_defaults(func=module.cmd)

    return func


def minimum_parser_setup(subparsers, parsers, subcommand, *args, **kwargs):
    # This is the local variable ``parsers`` in the main function
    parsers[subcommand] = subparsers.add_parser(
        subcommand, *args, add_help=False, **kwargs
    )
    parsers[subcommand].set_defaults(func=cmd_lazy_load(subcommand, parsers))


def main():
    """Main program entry point"""
    # The dummy parser will be used to find out which subcommand was run
    parser, dummy_parser = [
        argparse.ArgumentParser(
            add_help=False, formatter_class=argparse.RawTextHelpFormatter
        )
        for i in range(2)
    ]

    # Set up options for the main command -- `tem`
    # The same options are added to the proper and the dummy parser
    for i, p in enumerate([parser, dummy_parser]):
        p.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s version {}".format(tem.__version__),
        )
        cli.add_general_options(p, dummy=(i == 1))
        p.add_argument(
            "--init-user",
            action="store_true",
            help="generate initial user configuration file",
        )
        # Tem invoked with no args should print help and exit
        p.set_defaults(func=lambda: print_help_exit(parser))

    # The dummy parser gets a positional argument. This positional is the
    # subcommand that tem was run with
    dummy_parser.add_argument(
        "subcommand", nargs=argparse.REMAINDER, help=argparse.SUPPRESS
    )

    # Set up subcommand parsers
    subparsers = parser.add_subparsers(title="commands", metavar="")

    # Bare minimum setup for subcommand parsers
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    parsers = dict()
    # fmt: off
    # pylint: disable=line-too-long
    minimum_parser_setup(subparsers, parsers, "add",
                         help="add templates to a repository")
    minimum_parser_setup(subparsers, parsers, "rm",
                         help="remove templates from a repository")
    minimum_parser_setup(subparsers, parsers, "put",
                         help="put templates into a desired directory")
    minimum_parser_setup(subparsers, parsers, "ls", help="list templates")
    minimum_parser_setup(subparsers, parsers, "repo",
                         help="perform actions on tem repositories")
    minimum_parser_setup(subparsers, parsers, "config",
                         help="get and set configuration options")
    minimum_parser_setup(subparsers, parsers, "init",
                         help="generate a .tem/ directory")
    minimum_parser_setup(subparsers, parsers, "env",
                         help="run or modify local environments")
    minimum_parser_setup(subparsers, parsers, "path",
                         help="run or modify the local path")
    minimum_parser_setup(subparsers, parsers, "git",
                         help="use environments versioned under git")
    minimum_parser_setup(subparsers, parsers, "hook",
                         help="run or modify command hooks")
    minimum_parser_setup(subparsers, parsers, "find",
                         help="find anything tem-related")
    minimum_parser_setup(subparsers, parsers, "var",
                         help="manipulate tem variants")
    minimum_parser_setup(subparsers, parsers, "dot")
    # pylint: enable=line-too-long
    # fmt: on
    for plug in plugin.load_all():
        description = plug.__doc__.split("\n", maxsplit=1)[0]
        p = subparsers.add_parser(
            plug.__name__,
            add_help=True,
            help=plug.__doc__ + " \033[33;1m[plugin]\033[0m",
        )

        def cli_setup_function(plug, parser):
            def func():
                plug.setup_parser(parser)
                parser.set_defaults(func=plug.cmd)

            return func

        p.set_defaults(func=cli_setup_function(plug, p))

    # Use the dummy parser to determine the subcommand
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    args = dummy_parser.parse_known_args()[0]

    if args.init_user:  # --init-user option
        init_user()

    # Load configuration that is applicable so far
    cli.load_system_config()
    cli.load_user_config()
    cli.load_config_from_args(args)

    # Subcommand contains the first positional, and all subsequent arguments
    if not args.subcommand:
        args.func()
    else:
        index = -len(args.subcommand)
        sys.argv[1:] = cli.expand_alias(-len(args.subcommand), sys.argv[1:])
        cli.set_active_subcommand(sys.argv[index])

    # Parse known arguments without delving into the details of subcommands
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    args = parser.parse_known_args()[0]

    # Execute the warm-up function for the given subcommand
    # This will fully set up the argument parser for that subcommand
    args.func()

    # Final parsing
    # ━━━━━━━━━━━━━
    args = parser.parse_args()

    # Append --config arguments that came after the subcommand argument
    cli.load_config_from_args(args)

    args.func(args)


if __name__ == "__main__":
    main()
