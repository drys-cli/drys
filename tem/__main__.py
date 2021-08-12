#!/usr/bin/env python3

import tem

import argparse, sys, os
from tem import cli, util

from tem.util import print_cli_err

def init_user():
    """Initialize a user config file in a location with the highest priority"""
    try:
        existing_cfg = next(path for path in cli.user_config_paths
                    if os.path.exists(path))
    except StopIteration:
        existing_cfg = None
    if existing_cfg:
        print_cli_err('configuration already exists at ' + existing_cfg)
        exit(1)
    else:
        cfg_dest = cli.get_user_config_path()
        util.copy(tem.__prefix__ + '/share/tem/config',
                    cli.get_user_config_path())
        os.makedirs(os.path.expanduser('~/.local/share/tem/repo'),
                    exist_ok=True)
        exit(0)

def main():
    # NOTE: These three functions have to be defined inside main() because they
    # access local objects
    def cmd_warmup(module_name, parsers):
        # Comments contain example calls when module_name = add
        def func():
            # global add
            exec("global %s" % module_name)
            # from tem import add
            exec("from tem import %s" % module_name)
            _parsers = parsers
            # add.setup_parser(parsers['add'])
            exec("{0}.setup_parser(_parsers['{0}'])".format(module_name))
            return module_name
        return func

    def print_help_exit(parser):
        parser.print_help()
        exit(0)

    def minimum_parser_setup(subcommand, *args, **kwargs):
        parsers[subcommand] = subparsers.add_parser(
            subcommand, *args, add_help=False, **kwargs
        )
        parsers[subcommand].set_defaults(func=cmd_warmup(subcommand, parsers))

    # Create a proper parser and a dummy parser
    # The dummy parser will be used to find out which subcommand was run
    parser, dummy_parser = [
        argparse.ArgumentParser(add_help=False,
                                formatter_class=argparse.RawTextHelpFormatter)
        for i in range(2)
    ]

    # Set up options for the main command -- `tem`
    # The same options are added to the proper and the dummy parser
    for i, p in enumerate([parser, dummy_parser]):
        p.add_argument('-v', '--version', action='version',
                       version='%(prog)s version {}'.format(tem.__version__))
        cli.add_general_options(p, dummy=(i == 1))
        p.add_argument('--init-user', action='store_true',
                       help='generate initial user configuration file')
        p.add_argument('--debug', action='store_true',
                       help=argparse.SUPPRESS)
        # Tem invoked with no args should print help and exit
        p.set_defaults(func=lambda: print_help_exit(parser))

    # The dummy parser gets a positional argument. This positional is the
    # subcommand that tem was run with
    dummy_parser.add_argument('subcommand', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)

    # Set up subcommand parsers
    subparsers = parser.add_subparsers(title='commands', metavar='')

    # Bare minimum setup for subcommand parsers
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    parsers = dict()
    minimum_parser_setup('add',    help='add templates to a repository')
    minimum_parser_setup('rm',     help='remove templates from a repository')
    minimum_parser_setup('put',    help='put templates into a desired directory')
    minimum_parser_setup('ls',     help='list templates')
    minimum_parser_setup('repo',   help='perform actions on tem repositories')
    minimum_parser_setup('config', help='get and set configuration options')
    minimum_parser_setup('env',    help='run or modify local environments')
    minimum_parser_setup('path',   help='run or modify the local path')
    minimum_parser_setup('git',    help='use environments versioned under git')
    minimum_parser_setup('hook',   help='run or modify command hooks')
    minimum_parser_setup('dot')

    # Use the dummy parser to determine the subcommand
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    args = dummy_parser.parse_known_args()[0]

    if args.debug:
        import pudb; pu.db

    if args.init_user:
        init_user()

    # Load configuration that is applicable so far
    cli.load_system_config()
    cli.load_user_config()
    cli.load_config_from_args(args)

    # Subcommand contains the first positional, and all the subsequent arguments
    if not args.subcommand:
        args.func()
    else:
        sys.argv[1:] = cli.expand_alias(-len(args.subcommand), sys.argv[1:])

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

if __name__ == '__main__':
    main()
