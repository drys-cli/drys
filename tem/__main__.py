#!/usr/bin/env python3

import tem

import argparse, sys, os
from tem import common, util

from tem.util import print_cli_err

def init_user():
    try:
        existing_cfg = next(path for path in common.user_config_paths
                    if os.path.exists(path))
    except StopIteration:
        existing_cfg = None
    if existing_cfg:
        print_cli_err('configuration already exists at ' + existing_cfg)
        exit(1)
    else:
        cfg_dest = common.get_user_config_path()
        util.copy(tem.__prefix__ + '/share/tem/config',
                    common.get_user_config_path())
        os.makedirs(os.path.expanduser('~/.local/share/tem/repo'),
                    exist_ok=True)
        exit(0)

def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s version {}'.format(tem.__version__))
    common.add_common_options(parser, main_parser=True)
    parser.add_argument('--init-user', action='store_true',
                        help='generate initial user configuration file')
    parser.add_argument('--debug', action='store_true',
                        help='start in debugger mode')
    parser.set_defaults(func=lambda args: parser.print_help())

    # Setup subcommand parsers
    sub = parser.add_subparsers(title='commands', metavar='')
    from tem import add, rm, put, ls, repo, config, init, env, hook, git
    add.setup_parser(sub)
    rm.setup_parser(sub)
    put.setup_parser(sub)
    ls.setup_parser(sub)
    repo.setup_parser(sub)
    config.setup_parser(sub)
    init.setup_parser(sub)
    env.setup_parser(sub)
    hook.setup_parser(sub)
    git.setup_parser(sub)

    # ┏━━━━━━┓
    # ┃ NOTE ┃
    # ┗━━━━━━┛
    # Because the --config option is part of both the main parser and all the
    # subparsers, whenever a subcommand is parsed, the contents of args.config
    # are reset. So, args.config contains only those occurrences that are
    # specified AFTER a subcommand.
    # For example after running: tem -c file1 ls -c file2 -c file3
    #   args.config will be [ 'file2', 'file3' ]
    #
    # This is a workaround I intend to remove once I figure out a proper way
    # around it
    config = []
    for i in range(1, len(sys.argv)):
        if sys.argv[i] in ['--config', '-c'] and i < len(sys.argv) - 1:
            config.append(sys.argv[i+1])
        elif sys.argv[i] == '--reconfigure':
            config.append(None)

    # Parse arguments before reading config. This allows us to process arguments
    # that can potentially terminate the program immediately (like '--help')
    args = parser.parse_args();

    if args.debug:
        import pudb; pu.db

    # Load configuration, from default files and from '--config' arguments
    common.load_config(config)

    if args.init_user:
        init_user()

    if args.func:
        args.func(args)

if __name__ == '__main__':
    main()
